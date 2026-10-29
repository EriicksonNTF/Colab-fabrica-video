"""QC-AV del master: tecnica + continuidad de camara + contenido REAL en el pixel.

Leccion del prototipo (data/qc/CAMBIOS.md): medir luminancia y diff entre fotogramas no detecta
una escena vacia. Este QC compara lo que el manifiesto DECLARA contra lo que el pixel MUESTRA.

Uso: python qc.py --master .../master_final.mp4 --manifest .../manifest.jsonl \
              --script .../script.json --out .../data/qc/
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

W, H = 540, 960  # ventana de analisis (barato; la medicion de fraccion es invariante a escala)
BG = np.array([255, 248, 241], np.int16)  # --papel de la paleta del canal
# Umbrales calibrados sobre S001 recompuesto (28-oct-2026), medidos en 540x960 con el mismo filtro
# que usa este archivo: cov 3,6-7,7 % en las llegadas y densidad del foco 7,6-19,7 %. El estilo es
# LINEA sobre papel (trazo + rellenos chicos), no mancha maciza. L1 (78 % de ancho) se exige al
# GENERAR el encuadre en build_comp.py; aca el pixel prueba que haya contenido REAL y donde.
MIN_COVERAGE = 0.025
MIN_W_OR_H = (0.55, 0.45)
# Que parte de la caja prometida por la estacion esta efectivamente pintada. Medido en S001
# recompuesto: el minimo de los diez beats es 7,6 % (el circuito, pura linea) y el maximo 19,7 %
# (el ojo). Con 1,5 % pasaban los beats vacios del 27-oct (1,5-1,6 %): el umbral ahora corta.
# Una camara mirando al lado equivocado no pasa de 0,8 %, porque solo la rozan trazos vecinos.
# Se usa DENSIDAD y no "fraccion de toda la pintura del cuadro" porque en un mundo continuo siempre
# hay zonas vecinas dibujadas: eso bajaria a 40 % un plano perfecto (medido en calma y CTA).
MIN_DENSIDAD = 0.05
# Drawing behind the medical chip is the other silent failure: the band is veiled, so the pixel
# barely shows it, but the viewer sees cards crawling under the amber strip.
MAX_FUGA_CHIP = 0.015
MAX_LUMA_JUMP = 26.0
MIN_FRAME_DIFF = 0.05
MAX_CASI_VACIOS = 45    # 3 s repartidos de papel suelto son viajes largos de camara; mas, escena vacia
# C5 permite un unico fundido de salida a negro (0,4 s). Ahi el cuadro se congela **a proposito**, asi
# que esa cola no cuenta en C3: si contara, la regla de respiracion perpetua seria incompatible con
# la regla de cierre y el QC se contradice a si mismo.
FADE_SALIDA = 0.6


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]}: {p.stderr[-800:]}")
    return p.stdout


def probe(master):
    raw = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
              "stream=width,height,r_frame_rate,pix_fmt,nb_frames:format=duration,size,bit_rate",
              "-of", "json", str(master)])
    j = json.loads(raw)
    st, fmt = j["streams"][0], j["format"]
    num, den = st["r_frame_rate"].split("/")
    return {"w": int(st["width"]), "h": int(st["height"]), "fps": float(num) / float(den),
            "pix_fmt": st["pix_fmt"], "duration": float(fmt["duration"]),
            "size_mb": round(int(fmt["size"]) / 1e6, 2)}


def loudness(master):
    """loudnorm imprime su JSON por el canal de INFO: con -v error el informe desaparece."""
    txt = subprocess.run(["ffmpeg", "-i", str(master), "-af",
                          "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    i = txt.rfind("{")
    return json.loads(txt[i:txt.rfind("}") + 1]) if i >= 0 else {}


TM = 15.0   # muestreo del QC (fps): 1650 cuadros de un master de 55 s no se guardan en RAM


def medir(master, bandas, focos=None, chip=None, chip_t=None):
    """Streaming de fotogramas por FFmpeg: del cuadro solo queda la metrica, no el pixel.

    El prototipo aprendio que medir luminancia no detecta una escena vacia: por eso cada cuadro
    devuelve cobertura de contenido y bbox contra el papel, no solo brillo. `bandas` y `focos` llegan
    del comp (comp_meta.json): son las franjas del HUD (karaoke y chip medico) y la caja de pantalla
    que cada estacion promete. Si el QC las hardcodea y el karaoke esta en otra parte, mide los
    subtitulos como si fueran dibujo: escena vacia en verde.
    """
    proc = subprocess.Popen([str(c) for c in ["ffmpeg", "-v", "error", "-i", str(master), "-vf",
                                              f"fps={TM},scale={W}:{H}", "-pix_fmt", "rgb24",
                                              "-f", "rawvideo", "-"]],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    tapas = [(int(round(a * H)), int(round(b * H))) for a, b in bandas]
    tam, metricas, deltas, prev = W * H * 3, [], [], None
    while True:
        buf = proc.stdout.read(tam)
        if buf is None or len(buf) < tam:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.int16)
        luma = fr.mean(axis=2)
        mask = np.abs(fr - BG).max(axis=2) > 40
        m_t = len(metricas) / TM
        fuga = 0.0
        if chip and chip_t is not None and m_t >= chip_t + 0.5:
            cx0, cy0, cx1, cy1 = [v * (W / 1080.0) for v in chip]
            reg = np.zeros((H, W), bool)
            reg[int(cy0):int(cy1), :] = True
            reg[int(cy0):int(cy1), int(cx0):int(cx1)] = False
            fuga = float((mask & reg).sum()) / max(1.0, float(reg.sum()))
        for a, b in tapas:
            mask[max(0, a):min(H, b), :] = False
        ys, xs = np.nonzero(mask)
        m = {"t": m_t, "luma": float(luma.mean()), "fuga": round(fuga, 4),
             "cov": float(mask.mean()),
             "fw": float((xs.max() - xs.min() + 1) / W) if len(xs) else 0.0,
             "fh": float((ys.max() - ys.min() + 1) / H) if len(ys) else 0.0}
        for k, f in enumerate(focos or []):
            if not f:
                continue
            x0, y0 = int(round(f[0] * W)), int(round(f[1] * H))
            x1, y1 = max(x0 + 1, int(round(f[2] * W))), max(y0 + 1, int(round(f[3] * H)))
            caja = mask[y0:y1, x0:x1]
            adentro = float(caja.sum())
            # "cuanta pintura hay dentro" depende del grosor del trazo y del tamano de la caja: un
            # diagrama de linea bien encuadrado da 4 %. "que fraccion DE TODA la pintura del cuadro
            # esta dentro" no: si la camara mira al lado equivocado, la mayoria queda afuera.
            m[f"f{k}"] = adentro / max(1.0, float(mask.sum()))
            m[f"c{k}"] = adentro / max(1.0, caja.size)
        metricas.append(m)
        if prev is not None:
            deltas.append(float(np.abs(luma - prev).mean()))
        prev = luma
    proc.stdout.close()
    proc.wait()
    return metricas, deltas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--meta", default=None, help="comp_meta.json: de donde esta el karaoke y cada foco")
    ap.add_argument("--out", required=".")
    a = ap.parse_args()

    master = Path(a.master)
    script = json.loads(Path(a.script).read_text(encoding="utf-8"))
    man = [json.loads(l) for l in Path(a.manifest).read_text(encoding="utf-8").splitlines() if l.strip()]
    cm = json.loads(Path(a.meta).read_text(encoding="utf-8")) if a.meta and Path(a.meta).exists() else {}
    if cm:
        bandas = [tuple(b) for b in cm["bandas"]]
        mw, mh = cm["ancho"], cm["alto"]
        focos = [None if not f else [f[0] / mw, f[1] / mh, f[2] / mw, f[3] / mh]
                 for f in cm.get("focos", [])]
        chip, chip_t = cm.get("chip"), cm.get("chip_t")
    else:   # sin meta no se puede decir donde esta el HUD: se mide todo y se avisa
        bandas, focos, chip, chip_t = [(0.0, 0.05)], [], None, None
    meta = probe(master)
    ln = loudness(master)
    metrics, delta = medir(master, bandas, focos, chip, chip_t)
    fps = TM

    fails, notes = [], []
    if not (45.0 <= meta["duration"] <= 59.9):
        fails.append(f"duracion {meta['duration']:.2f}s fuera de 45-59.9")
    if abs(meta["fps"] - 30) > 0.05:
        fails.append(f"fps {meta['fps']} != 30")
    if [meta["w"], meta["h"]] != [1080, 1920]:
        fails.append(f"resolucion {meta['w']}x{meta['h']} != 1080x1920")
    if meta["pix_fmt"] != "yuv420p":
        fails.append(f"pix_fmt {meta['pix_fmt']} != yuv420p")
    if meta["size_mb"] > 50:
        fails.append(f"tamano {meta['size_mb']} MB > 50 MB")
    i_lufs = float(ln.get("input_i", 0) or 0)
    if not (-15.0 <= i_lufs <= -13.0):
        fails.append(f"loudness {i_lufs} LUFS fuera de -14 +/-1")
    if float(ln.get("input_tp", -99) or -99) > -1.5:
        fails.append(f"pico {ln.get('input_tp')} dBTP > -1.5")

    fugas = [(m["t"], m["fuga"]) for m in metrics if m.get("fuga", 0) > MAX_FUGA_CHIP]
    if fugas:
        fails.append(f"{len(fugas)} fotogramas con dibujo debajo del chip fuera de su caja: "
                     f"{fugas[:5]}")
    blacks = [m["t"] for m in metrics if m["cov"] < 0.012]
    if len(blacks) > MAX_CASI_VACIOS:
        fails.append(f"{len(blacks)} fotogramas casi vacios (cov<1.2%), primeros {blacks[:5]}")
    jumps = [((i + 1) / fps, float(d)) for i, d in enumerate(delta) if d > MAX_LUMA_JUMP]
    if jumps:
        fails.append(f"{len(jumps)} saltos de contenido > {MAX_LUMA_JUMP} (posible corte): {jumps[:6]}")
    frozen = [((i + 1) / fps, float(d)) for i, d in enumerate(delta)
              if d < MIN_FRAME_DIFF and (i + 1) / fps <= metrics[-1]["t"] - FADE_SALIDA]
    if len(frozen) > 3:
        fails.append(f"{len(frozen)} fotogramas congelados (regla C3): {frozen[:6]}")

    # C1: en cada llegada declarada, el pixel debe mostrar contenido REAL y donde la estacion dice
    for i, b in enumerate(script["beats"]):
        t_arr = b.get("t_real", b["t"])
        idxs = [j for j in range(len(metrics)) if t_arr + 0.45 <= metrics[j]["t"] <= t_arr + 1.45]
        if not idxs:
            notes.append(f"beat {b['tipo']} @{t_arr}s sin fotogramas en el rango")
            continue
        win = [metrics[j] for j in idxs]
        cov = max(m["cov"] for m in win)
        fw = max(m["fw"] for m in win)
        fh = max(m["fh"] for m in win)
        ok = cov >= MIN_COVERAGE and (fw >= MIN_W_OR_H[0] or fh >= MIN_W_OR_H[1])
        detalle = ""
        clave = f"f{i}"
        if clave in win[0]:
            dentro = max(m[clave] for m in win)
            pintura = max(m[f"c{i}"] for m in win)
            detalle = f" pinturaEnFoco={dentro:.0%} densidadFoco={pintura:.1%}"
            if pintura < MIN_DENSIDAD:
                ok = False
                detalle += f" -> la camara no esta mirando el foco ({pintura:.1%} < {MIN_DENSIDAD:.1%})"
            else:
                # Habiendo caja declarada y densidad medida, la cobertura global es el proxy debil:
                # un diagrama de una sola linea vertical (el circuito de S001, beat 4) llena el alto
                # y pinta poco pixel. Lo que importa es que el foco este mirado y el contenido extendido.
                ok = (fw >= MIN_W_OR_H[0] or fh >= MIN_W_OR_H[1])
                detalle += f" (cov global {cov:.1%}: mandan densidad y bbox)"
        line = (f"{b['tipo']:9s} @{t_arr:5.1f}s zona={b['zona']:9s} cov={cov:5.1%} "
                f"ancho={fw:5.1%} alto={fh:5.1%} -> {'OK' if ok else 'FALLA'}{detalle}")
        (notes if ok else fails).append(line)

    escala = [m.get("scale", 1.0) for m in man]
    if len(escala) > 2:
        d2 = np.abs(np.diff(escala, n=2))
        if float(d2.max()) > 0.008:
            fails.append(f"camara no es C1: |d2 scale| max {float(d2.max()):.4f} > 0.008 (regla C2)")

    verdict = "PASA" if not fails else "FIX"
    res = {"slug": script["slug"], "veredicto": verdict, "video": meta,
           "loudness": ln, "checks": len(notes), "fallos": fails, "frames": len(metrics),
           "coverage_media": round(float(np.mean([m["cov"] for m in metrics])), 4)}
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{script['slug']}-qcav.json").write_text(json.dumps(res, ensure_ascii=False, indent=2),
                                                        encoding="utf-8")
    (outdir / f"{script['slug']}-qcav.md").write_text(
        f"# QC-AV {script['slug']}\n\nveredicto: **{verdict}**\n\n"
        + "".join(f"- [x] {n}\n" for n in notes)
        + "".join(f"- [ ] FALLA: {f}\n" for f in fails)
        + f"\n- video: {meta['duration']:.2f}s {meta['w']}x{meta['h']}@{meta['fps']} "
          f"{meta['pix_fmt']} {meta['size_mb']} MB\n"
          f"- loudness: {i_lufs} LUFS / TP {ln.get('input_tp')} dB / LRA {ln.get('input_lra')} LU\n"
          f"- coverage media de cuadro: {res['coverage_media']:.1%}\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASA" else 1


if __name__ == "__main__":
    sys.exit(main())
