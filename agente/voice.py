"""Voz por beat con la RECETA de direccion (5.4) + WordBoundary global.

Cada beat se sintetiza como clip aparte con su propio rate; las pausas entre beats se insertan
aqui (no en el texto) para que timestamps.json sea exacto. Salida: voz.mp3, timestamps.json,
master_info.json.

En CI: pip install edge-tts. Si edge-tts no esta o el servicio cae, falla loud y escala —
los backups (Kokoro/Piper) se invocan con --fallback, no en silencio.
"""
import asyncio
import json
import subprocess
import sys
import threading
from pathlib import Path

SR = 48000
# RECETA aprobada 26-oct-2026: energia por beat, no clonando nada.
RATE_BY_TIPO = {"HOOK": "+18%", "NOMBRE": "-2%", "MECANISMO": "-2%", "DEMO": "+6%",
                "UTILIDAD": "+6%", "CTA": "+4%"}
# Un solo rate por tipo sonaba plano entre beats del mismo tipo (3 NOMBRE seguidos, 2 UTILIDAD):
# un cuarto de tono arriba en el gancho y abajo en la utilidad alcanza para que se lea "hablado".
PITCH_BY_TIPO = {"HOOK": "+8Hz", "NOMBRE": "+2Hz", "MECANISMO": "+0Hz", "DEMO": "+3Hz",
                 "UTILIDAD": "-2Hz", "CTA": "+5Hz"}
RATE_DEFAULT = "+8%"
GAP_S = 0.22
GAP_BEFORE_CTA_S = 0.30
SILENCE_PEAK = 0.97


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} fallo: {p.stderr[-1200:]}")
    return p.stdout


def decode_wav(src, dst):
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ar", str(SR), "-ac", "1", str(dst)])
    return dst


def peak_of_wav(path):
    """Pico normalizado 0-1 del wav mono pcm16; referencia de mix para master_info.json."""
    import wave
    import numpy as np
    with wave.open(str(path), "rb") as w:
        raw = w.readframes(w.getnframes())
    if not raw:
        return 0.0
    return round(float(np.abs(np.frombuffer(raw, dtype="<i2") / 32768.0).max()), 3)


def wav_samples(path):
    with open(path, "rb") as f:
        data = f.read()
    i = data.find(b"data")
    if i < 0 or i + 4 > len(data):
        return 0
    return int.from_bytes(data[i + 4:i + 8], "little") // 2


async def synth_clip(text, voice, rate, pitch, mp3, words_out):
    import edge_tts

    # edge-tts 7.x cambio el DEFAULT a SentenceBoundary: sin este argumento no llega ni una palabra
    # y el karaoke cae a "proporcional" (reparto por caracteres). Es la regresion de subtitulos del
    # 28-oct: el audio se oye bien, pero la caja azul se adelanta o se atrasa medio segundo.
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    audio, words = bytearray(), []
    async for chunk in com.stream():
        tipo = str(chunk.get("type", ""))
        if tipo == "audio":
            audio.extend(chunk["data"])
        elif tipo.lower().startswith("word") and "offset" in chunk and chunk.get("text"):
            # WordBoundary: offset/duration llegan en unidades de 100 ns.
            words.append({"word": chunk.get("text", ""),
                          "start": round(chunk["offset"] / 1e7, 3),
                          "dur": round(chunk["duration"] / 1e7, 3)})
    if not audio:
        raise RuntimeError("edge-tts devolvio 0 bytes de audio")
    Path(mp3).write_bytes(bytes(audio))
    Path(words_out).write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    return words


def _run_async(coro):
    """asyncio.run() revienta dentro de un kernel de Colab/IPython, que ya tiene un loop corriendo
    ('asyncio.run() cannot be called from a running event loop'). Si hay loop, el coroutine se
    ejecuta en un thread propio con su loop nuevo; en CI no hay loop y va directo por asyncio.run."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    caja = {}

    def _worker():
        try:
            caja["r"] = asyncio.run(coro)
        except BaseException as exc:  # noqa: BLE001 - se re-lanza en el thread principal
            caja["e"] = exc

    hilo = threading.Thread(target=_worker)
    hilo.start()
    hilo.join()
    if "e" in caja:
        raise caja["e"]
    return caja.get("r")


def build(script_path, out_dir, voice_id=None, rate_override=None, fallback=False):
    script = json.loads(Path(script_path).read_text(encoding="utf-8"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    vid = voice_id or script["voz"]["voice_id"]
    beats = script["beats"]
    if fallback:
        return kokoro_fallback(script, out, vid)

    import edge_tts  # noqa: F401  (falla aqui si falta el paquete: mejor temprano)

    clips = []
    for i, b in enumerate(beats):
        rate = rate_override or RATE_BY_TIPO.get(b["tipo"], script["voz"].get("rate_global", RATE_DEFAULT))
        pitch = PITCH_BY_TIPO.get(b["tipo"], "+0Hz")
        mp3, wj = out / f"beat{i:02d}.mp3", out / f"beat{i:02d}.words.json"
        try:
            _run_async(synth_clip(b["linea"], vid, rate, pitch, mp3, wj))
        except Exception as exc:  # noqa: BLE001 - edge puede caer sin aviso
            raise RuntimeError(f"voz beat {i} ({b['tipo']}) fallo: {exc}") from exc
        wav = decode_wav(mp3, out / f"beat{i:02d}.wav")
        clips.append({"beat": b, "n_words": len(json.loads(wj.read_text(encoding="utf-8"))),
                      "samples": wav_samples(wav), "words_file": wj, "wav": wav, "rate": rate})

    concat, t, global_words, gaps = [], 0.0, [], []
    for c in clips:
        gap = GAP_BEFORE_CTA_S if c["beat"]["tipo"] == "CTA" else GAP_S
        if c is not clips[0]:
            sil = out / f"sil{int(round(gap * 1000))}.wav"
            if not sil.exists():
                run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                     f"anullsrc=r={SR}:cl=mono", "-t", f"{gap:.3f}", str(sil)])
            concat.append(f"file '{sil.resolve().as_posix()}'")
            t += gap
        gaps.append(round(t, 3))
        concat.append(f"file '{c['wav'].resolve().as_posix()}'")
        for w in json.loads(c["words_file"].read_text(encoding="utf-8")):
            global_words.append({"word": w["word"], "start": round(w["start"] + t, 3),
                                 "dur": w["dur"], "beat": c["beat"]["tipo"]})
        t += c["samples"] / SR
    listfile = out / "concat.txt"
    listfile.write_text("\n".join(concat), encoding="utf-8")
    voz_wav = out / "voz.wav"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:a", "pcm_s16le", str(voz_wav)])
    voz_mp3 = out / "voz.mp3"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(voz_wav), "-c:a", "libmp3lame", "-q:a", "2",
         str(voz_mp3)])

    for i, c in enumerate(clips):
        c["beat"]["t_real"] = gaps[i]

    sync_mode = "WordBoundary" if global_words else "proporcional"
    if sync_mode == "proporcional":
        # Sin WordBoundary: reparto por caracteres sobre la duracion real de cada clip.
        global_words = []
        for i, c in enumerate(clips):
            toks = c["beat"]["linea"].split()
            dur, peso = c["samples"] / SR, max(1, sum(len(w) for w in toks))
            acc = gaps[i]
            for w in toks:
                d = dur * len(w) / peso
                global_words.append({"word": w, "start": round(acc, 3), "dur": round(d, 3),
                                     "beat": c["beat"]["tipo"]})
                acc += d
    (out / "timestamps.json").write_text(
        json.dumps({"audio": "voz.mp3", "sync_mode": sync_mode, "words": global_words},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "master_info.json").write_text(json.dumps({
        "slug": script["slug"], "sync_mode": sync_mode, "voice": vid,
        "rate_global": script["voz"].get("rate_global", RATE_DEFAULT),
        "rates_por_beat": {f'{i:02d}-{c["beat"]["tipo"]}': c["rate"] for i, c in enumerate(clips)},
        "duracion_s": round(t, 3), "palabras": len(global_words),
        "picovoz": peak_of_wav(voz_wav)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"voz": str(voz_mp3), "duracion_s": round(t, 2), "palabras": len(global_words),
            "sync_mode": sync_mode, "t_reales": [g for g in gaps]}


def kokoro_fallback(script, out, vid):
    """Emergencia offline del stack (Kokoro em_*). Sin WordBoundary: sync proporcional."""
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline

    pipe = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")
    voice_key = "em_santa" if "santa" in (vid or "") else "em_alex"
    parts, words, t = [], [], 0.0
    sr = 24000
    for b in script["beats"]:
        chunks = [np.asarray(c.audio, dtype=np.float32)
                  for c in pipe(b["linea"], voice=voice_key, speed=1.08) if c.audio is not None]
        audio = np.concatenate(chunks) if chunks else np.zeros(1, np.float32)
        parts.append(audio)
        toks = b["linea"].split()
        acc = t
        for w in toks:
            d = len(audio) / sr * len(w) / max(1, sum(len(x) for x in toks))
            words.append({"word": w, "start": round(acc, 3), "dur": round(d, 3), "beat": b["tipo"]})
            acc += d
        b["t_real"] = round(t, 3)
        t += len(audio) / sr
        parts.append(np.zeros(int(GAP_S * sr), np.float32))
        t += GAP_S
    voice = np.concatenate(parts)
    voice *= SILENCE_PEAK / max(1e-9, float(np.max(np.abs(voice))))
    wav = out / "voz.wav"
    sf.write(wav, voice, sr, subtype="PCM_16")
    mp3 = out / "voz.mp3"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-c:a", "libmp3lame", "-q:a", "2", str(mp3)])
    (out / "timestamps.json").write_text(json.dumps(
        {"audio": "voz.mp3", "sync_mode": "proporcional", "words": words},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return {"voz": str(mp3), "duracion_s": round(t, 2), "palabras": len(words),
            "sync_mode": "proporcional", "t_reales": [b["t_real"] for b in script["beats"]]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default=None)
    ap.add_argument("--rate", default=None)
    ap.add_argument("--fallback", action="store_true", help="Kokoro offline (emergencia)")
    a = ap.parse_args()
    try:
        info = build(a.script, a.out, a.voice, a.rate, a.fallback)
    except ImportError:
        print("FALTA edge-tts (pip install edge-tts) — o usar --fallback", file=sys.stderr)
        raise SystemExit(3)
    print(json.dumps(info, ensure_ascii=False))
