"""Orquestador del brazo determinista (GitHub Actions): guion entra, MP4 sale.

Corre en CI (ubuntu-latest). Nada creativo: lee data/escenas/{slug}/script.json y produce
voz + SFX + comp.html + master_final.mp4 + QC + paquete de publicacion. Si un paso crítico
falla, ESCALA (exit != 0 y reporte en data/qc/) en vez de parchear.

Uso: python agente/run_pipeline.py --slug S001-parpado-temblor
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import synth_sfx
import voice as voz_mod

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
# SONIDO: mapa determinista tipo de beat -> sonido sintetizado (sin CC0, sin descarga, sin login)
SFX_MAP = {"HOOK": ("whoosh", 0.30), "NOMBRE": ("pop", 0.22), "MECANISMO": ("tick", 0.16),
           "DEMO": ("tick", 0.14), "UTILIDAD": ("ding", 0.24), "CTA": ("chime", 0.26)}
HASHTAGS = ["#ciencia", "#cuerpo", "#sabiasque"]


def sh(cmd, check=True):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} fallo: {(p.stderr or p.stdout)[-900:]}")
    return p


def json_de(texto):
    """Primer objeto JSON valido que arranque en llave: los logs de ffmpeg traen cola suelta."""
    dec = json.JSONDecoder()
    for k, ch in enumerate(texto):
        if ch == "{":
            try:
                return dec.raw_decode(texto[k:])[0]
            except json.JSONDecodeError:
                continue
    return {}


def validar(scene, slug, reporte):
    """Muralla 1: contrato estructural (fatal) + factset (aviso: la URL la captura el humano)."""
    base = [sys.executable, ROOT / "agente" / "validate.py", "--script", scene / "script.json"]
    r = sh(base, check=False)
    v = json_de(r.stdout or "{}")
    if not v.get("ok", False):
        raise RuntimeError(f"script.json rechaza el contrato: {v.get('fallos')}")
    fs = ROOT / "data" / "factsets" / f"{slug}.json"
    if fs.exists():
        r2 = sh(base + ["--factset", fs], check=False)
        reporte["factset"] = json_de(r2.stdout or "{}").get("fallos", [])
    else:
        reporte["factset"] = [f"no hay factset en {fs.relative_to(ROOT)}"]


def hacer_voz(scene, slug, voice_id, reporte):
    """edge-tts con la RECETA; si cae, Kokoro offline; si cae eso, ESCALA."""
    try:
        info = voz_mod.build(scene / "script.json", scene, voice_id=voice_id)
    except Exception as exc:  # noqa: BLE001 - la red de edge-tts es el punto fragil real
        print(f"[voz] edge-tts fallo ({exc}); intento Kokoro offline", file=sys.stderr)
        info = voz_mod.kokoro_fallback(json.loads((scene / "script.json").read_text(encoding="utf-8")),
                                       scene, "ex")
        info["fallback"] = "kokoro"
    sc = json.loads((scene / "script.json").read_text(encoding="utf-8"))
    for b, t in zip(sc["beats"], info["t_reales"]):
        b["t_real"] = t
    (scene / "script_render.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    reporte["voz"] = {k: info[k] for k in ("duracion_s", "palabras", "sync_mode")}
    return scene / "script_render.json"


def mezclar_audio(scene, reporte):
    """Voz + SFX en las llegadas reales -> audio_final.wav medido y normalizado a -14 LUFS."""
    sc = json.loads((scene / "script_render.json").read_text(encoding="utf-8"))
    sfx_dir = scene / "sfx"
    sfx_dir.mkdir(exist_ok=True)
    entradas, filtros, mezcla = [scene / "voz.wav"], ["[0:a]anull[base]"], ["[base]"]
    for i, b in enumerate(sc["beats"]):
        if b["tipo"] not in SFX_MAP:
            continue
        nombre, ganancia = SFX_MAP[b["tipo"]]
        w = sfx_dir / f"{nombre}.wav"
        if not w.exists():
            synth_sfx.build(nombre, w, fs=SR)
        ms = max(0, int(round((float(b.get("t_real", b["t"])) + 0.05) * 1000)))
        k = len(entradas)
        entradas.append(w)
        filtros.append(f"[{k}:a]volume={ganancia:.2f},adelay={ms}|ms[s{k}]")
        mezcla.append(f"[s{k}]")
    pre = scene / "pre_master.wav"
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for e in entradas:
        cmd += ["-i", e]
    fc = ";".join(filtros) + f";{''.join(mezcla)}amix=inputs={len(mezcla)}:duration=first:" \
                             f"dropout_transition=0:normalize=0[mix]"
    sh(cmd + ["-filter_complex", fc, "-map", "[mix]", "-ar", SR, "-c:a", "pcm_s16le", pre])
    # La voz tiene ~17 dB de cresta (pico -2 dB contra -20 LUFS). Para llegar a -14 LUFS con picos
    # bajo -1,5 hay que recortar 5 dB de cresta, y una pasada lineal de loudnorm solo deja +0,2 dB
    # antes de tocar el techo de TP: el 28-oct el master salio -15,86 LUFS y el QC lo rechazo. La
    # cadena es: loudnorm dinamico dos veces (ya baja 4 dB de cresta) -> ganancia medida -> limitador
    # -> una correccion medida mas, porque el limitador se come ~40 % de cada dB que se sube.
    # Medido en S001: -14,5 LUFS con TP -1,96 dB ya codificado en AAC.
    LIMITADOR = "alimiter=level=false:limit=0.70"   # -3,1 dBFS de muestra: el TP real sobresale ~0,8
    LN = "loudnorm=I=-14:TP=-2.0:LRA=11"
    paso1 = scene / "loudnorm_1.wav"

    def medir(w):
        return json_de(sh(["ffmpeg", "-i", w, "-af", LN + ":print_format=json", "-f", "null", "-"],
                          check=False).stderr)

    def aplicar(src, dst, db):
        sh(["ffmpeg", "-y", "-v", "error", "-i", src, "-af",
            f"volume={db:.2f}dB,{LIMITADOR}", "-ar", SR, "-c:a", "pcm_s16le", dst])

    sh(["ffmpeg", "-y", "-v", "error", "-i", pre, "-af", f"{LN},{LN}", "-ar", SR,
        "-c:a", "pcm_s16le", paso1])
    m1 = medir(paso1)
    try:
        ganancia = round(-14.0 - float(m1["input_i"]), 2)
    except (KeyError, TypeError, ValueError):
        ganancia = 0.0
    audio, tmp = scene / "audio_final.wav", scene / "loudnorm_2.wav"
    aplicar(paso1, audio, ganancia)
    # El limitador se come ~60 % de cada dB que se sube despues: una sola correccion dejaba -14,87
    # (dentro del gate pero a 0,13 dB del borde). Se itera hasta -14,15 con tope de 3 vueltas.
    correcciones = 0
    for _ in range(3):
        m2 = medir(audio)
        try:
            delta = round(-14.15 - float(m2["input_i"]), 2)
        except (KeyError, TypeError, ValueError):
            break
        if delta <= 0.10:
            break
        aplicar(audio, tmp, min(delta, 1.5))
        tmp.replace(audio)
        correcciones += 1
    paso1.unlink(missing_ok=True)
    tmp.unlink(missing_ok=True)
    final = medir(audio)
    reporte["audio"] = {"loudness_paso1": m1.get("input_i"), "ganancia_db": ganancia,
                        "correcciones": correcciones, "tp_final_wav": final.get("input_tp")}
    if (scene / "master_info.json").exists():
        mi = json_de((scene / "master_info.json").read_text(encoding="utf-8"))
        reporte["audio"]["pico_voz"] = mi.get("picovoz")
        reporte["audio"]["rates_por_beat"] = mi.get("rates_por_beat")
    return audio


def componer(scene, slug, work):
    """comp.html generado por codigo (CAMBIOS #5) + staging HyperFrames con las fuentes."""
    r = sh([sys.executable, ROOT / "agente" / "build_comp.py", "--script",
            scene / "script_render.json", "--stamps", scene / "timestamps.json",
            "--out", scene / "comp.html"])
    info = json_de(r.stdout)
    (work / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "assets" / "fonts").glob("*.ttf"):
        shutil.copy(f, work / "assets" / "fonts" / f.name)
    shutil.copy(scene / "comp.html", work / "index.html")
    return info


def renderizar(work, scene, slug, calidad, workers):
    """HyperFrames render: retratos 1080x1920, 30 fps, sin audio (la voz va en el ensamble)."""
    video = scene / "video_silencioso.mp4"
    npx = "npx.cmd" if os.name == "nt" else "npx"   # en Windows el shim .cmd no lo resuelve CreateProcess
    cmd = [npx, "-y", "hyperframes", "render", str(work), "-o", video, "-f", 30,
           "--resolution", "portrait", "--quality", calidad, "--strict"]
    if workers:
        cmd += ["-w", str(workers)]
    p = sh(cmd, check=False)
    (scene / "render.log").write_text((p.stdout or "") + "\n" + (p.stderr or ""), encoding="utf-8")
    if p.returncode != 0 or not video.exists():
        raise RuntimeError(f"hyperframes render fallo: {(p.stderr or p.stdout)[-700:]}")
    return video


def ensamblar(video, audio, scene, slug):
    master = scene / "master_final.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", SR, "-movflags", "+faststart",
        "-shortest", master])
    dur = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                    "csv=p=0", master]).stdout.strip() or 0)
    paso = max(1.0, dur / 6)   # hoja de contacto de TODA la linea de tiempo, no de los 5 primeros s
    sh(["ffmpeg", "-y", "-v", "error", "-i", master, "-vf",
        f"fps=1/{paso:.3f},scale=360:-1,tile=2x3", "-frames:v", "1", "-an",
        scene / "hoja_contacto.jpg"])
    return master


def publicar(scene, slug, master, reporte):
    """Paquete por plataforma (esqueleto §4.9): el dueño edita y sube/agenda a mano."""
    sc = json.loads((scene / "script.json").read_text(encoding="utf-8"))
    hook = next(b["linea"] for b in sc["beats"] if b["tipo"] == "HOOK")
    etiquetas = " ".join(HASHTAGS)
    fix = "Fuentes en el comentario fijado. Esto no reemplaza a un profesional de la salud."
    pk = {"tiktok": {"caption": f"{hook} {etiquetas}", "hora_sugerida": "12:40",
                     "comentario_fijado": fix},
          "ytshorts": {"title": hook[:100], "hashtags": etiquetas},
          "igreels": {"caption": f"{hook} — {fix}", "hora_sugerida": "13:10"},
          "fbreels": {"caption": hook, "hora_sugerida": "11:30"}}
    out = ROOT / "data" / "published" / f"{slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"slug": slug, "master": str(master.relative_to(ROOT)),
                               "paquetes": pk,
                               "reglas": "hand-off humano: el dueño sube o agenda desde las apps "
                                         "oficiales. Sin bots de subida."},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--voice", default=None, help="voice_id edge-tts (default: la del script)")
    ap.add_argument("--quality", default="delivery", choices=["draft", "looks", "delivery"])
    ap.add_argument("--workers", default=None, help="workers de hyperframes (auto en CI)")
    ap.add_argument("--reuse-voz", action="store_true", help="no regenerar la voz (iterar rapido)")
    a = ap.parse_args()

    scene = ROOT / "data" / "escenas" / a.slug
    if not (scene / "script.json").exists():
        raise SystemExit(f"no existe {scene / 'script.json'}: el slug no esta en la cola")
    work = ROOT / "work" / a.slug
    work.mkdir(parents=True, exist_ok=True)
    reporte = {"slug": a.slug}

    validar(scene, a.slug, reporte)
    if a.reuse_voz and (scene / "timestamps.json").exists():
        # script_render.json es el que lleva `t_real` de la voz que ya suena en voz.wav: si se
        # reescribiera desde script.json se perderian las llegadas y el comp quedaria desfasado.
        fuente = scene / "script_render.json"
        if not fuente.exists():
            fuente = scene / "script.json"
        sc = json.loads(fuente.read_text(encoding="utf-8"))
        (scene / "script_render.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2),
                                                  encoding="utf-8")
        if not (scene / "voz.wav").exists():
            raise SystemExit("--reuse-voz pidio reutilizar la voz pero no existe voz.wav")
        render_stamps = json.loads((scene / "timestamps.json").read_text(encoding="utf-8"))
        reporte["voz"] = {"reutilizada": True, "sync_mode": render_stamps.get("sync_mode")}
    else:
        hacer_voz(scene, a.slug, a.voice, reporte)
    audio = mezclar_audio(scene, reporte)
    reporte["comp"] = componer(scene, a.slug, work)
    video = renderizar(work, scene, a.slug, a.quality, a.workers)
    master = ensamblar(video, audio, scene, a.slug)
    qc = sh([sys.executable, ROOT / "agente" / "qc.py", "--master", master, "--manifest",
             scene / "cam_manifest.jsonl", "--script", scene / "script_render.json",
             "--meta", scene / "comp_meta.json", "--out", ROOT / "data" / "qc"], check=False)
    reporte["qc"] = json_de(qc.stdout or "{}")
    reporte["publicado"] = str(publicar(scene, a.slug, master, reporte).relative_to(ROOT))
    (scene / "pipeline_report.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
    print(json.dumps(reporte, ensure_ascii=False, indent=2))
    if reporte["qc"].get("veredicto") != "PASA":
        print("QC-AV: FIX -> escalar al dueño (ver data/qc/*.md)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
