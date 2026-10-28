"""Diagnostico de encuadre: proyecta las piezas de cada beat contra el cuadro 1080x1920.

No forma parte del pipeline: es la cuenta que el QC deberia poder comparar contra el pixel.
Uso: python _diag_encuadre.py ../data/escenas/S001-parpado-temblor
"""
import json
import sys
from pathlib import Path

import build_comp as B


def main(carpeta):
    p = Path(carpeta)
    sc = json.loads((p / "script_render.json").read_text(encoding="utf-8"))
    st = json.loads((p / "timestamps.json").read_text(encoding="utf-8"))
    c = B.Comp(sc, st)
    for i, b in enumerate(c.beats):
        t = b.get("t_real", b["t"])
        est = c.stations[i]
        s = est["scale"]
        filas = []
        for (_z, pz) in c.piezas:
            if int(pz.get("aparece", 0)) != i:
                continue
            x0, y0, x1, y1 = B.caja(pz)
            # mundo -> pantalla: pantalla = VH/2 + s*(mundo - centro)
            sx0 = B.VW / 2 + s * (x0 - est["x"])
            sy0 = B.VH / 2 + s * (y0 - est["y"])
            sx1 = B.VW / 2 + s * (x1 - est["x"])
            sy1 = B.VH / 2 + s * (y1 - est["y"])
            dentro = not (sx1 < 0 or sx0 > B.VW or sy1 < 0 or sy0 > B.VH)
            filas.append(f"{pz['tipo']:11s}{pz['id']:11s} pantalla=[{sx0:6.0f},{sy0:6.0f} ->"
                         f" {sx1:6.0f},{sy1:6.0f}] {'visible' if dentro else 'FUERA'}")
        print(f"\nbeat {i} {b['tipo']:9s} t={t:5.1f}s zona={b['zona']:9s} escala={s:.3f}")
        for f in filas:
            print("   ", f)
        if not filas:
            print("    (ninguna pieza declara aparece==este beat)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../data/escenas/S001-parpado-temblor")
