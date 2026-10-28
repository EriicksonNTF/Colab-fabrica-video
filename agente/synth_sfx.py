"""SFX deterministas de respaldo (sin CC0, sin descarga, sin login).

Uso:  python synth_sfx.py tick --out tick.wav --fs 48000
Los 6 timbres del mapa de eventos del canal: tick, whoosh, thud, chime, ding, pop.
Mismo input -> misma forma de onda: no hay ruido aleatorio sin seed.
"""
import argparse
import math
import struct
import wave

FS_DEFAULT = 48000


def _envelope(n, attack, decay, hold=0.0):
    env = []
    a, h, d = int(n * attack), int(n * hold), int(n * decay)
    for i in range(a):
        env.append(i / max(1, a))
    for _ in range(h):
        env.append(1.0)
    for i in range(d):
        u = i / max(1, d)
        env.append((1.0 - u) ** 2.2)
    while len(env) < n:
        env.append(0.0)
    return env[:n]


def _render(dur, fs, samples_fn, peak=0.6):
    n = int(round(dur * fs))
    env = _envelope(n, 0.02, 0.9, 0.04)
    raw = [samples_fn(i / fs) * env[i] for i in range(n)]
    m = max(1e-9, max(abs(v) for v in raw))
    return [v * (peak / m) for v in raw]


def tick(dur=0.06, fs=FS_DEFAULT):
    def s(t):
        return math.sin(2 * math.pi * 2200 * t) * math.exp(-t * 60)
    return _render(dur, fs, s, 0.45)


def ding(dur=0.34, fs=FS_DEFAULT):
    def s(t):
        return (math.sin(2 * math.pi * 1180 * t) + 0.4 * math.sin(2 * math.pi * 2360 * t)) * math.exp(-t * 11)
    return _render(dur, fs, s, 0.42)


def chime(dur=0.7, fs=FS_DEFAULT):
    parcial = [(880, 1.0), (1320, 0.55), (1760, 0.3)]

    def s(t):
        v = sum(a * math.sin(2 * math.pi * f * t) * math.exp(-t * (3.5 + i)) for i, (f, a) in enumerate(parcial))
        return v
    return _render(dur, fs, s, 0.4)


def pop(dur=0.12, fs=FS_DEFAULT):
    def s(t):
        return math.sin(2 * math.pi * (330 - 1400 * t) * t) * math.exp(-t * 26)
    return _render(dur, fs, s, 0.5)


def thud(dur=0.4, fs=FS_DEFAULT):
    def s(t):
        return math.sin(2 * math.pi * (95 - 45 * t) * t) * math.exp(-t * 8)
    return _render(dur, fs, s, 0.6)


def whoosh(dur=0.5, fs=FS_DEFAULT):
    """Barrido filtrado sin ruido: suma de armónicos con crossover progresivo."""
    def s(t):
        acc = 0.0
        for k in range(1, 9):
            f = 140 * k * (1.0 + 1.6 * t / dur)
            acc += math.sin(2 * math.pi * f * t) / (k ** 1.4)
        ramp = math.sin(math.pi * min(1.0, t / dur)) ** 1.5
        return acc * ramp * 0.4
    return _render(dur, fs, s, 0.35)


VOICES = {"tick": tick, "ding": ding, "chime": chime, "pop": pop, "thud": thud, "whoosh": whoosh}


def write_wav(path, samples, fs=FS_DEFAULT):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in samples))


def build(name, path, fs=FS_DEFAULT):
    if name not in VOICES:
        raise SystemExit(f"sfx desconocido: {name}. disponibles: {', '.join(sorted(VOICES))}")
    write_wav(path, VOICES[name](fs=fs), fs)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=sorted(VOICES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--fs", type=int, default=FS_DEFAULT)
    a = ap.parse_args()
    print(build(a.name, a.out, a.fs))
