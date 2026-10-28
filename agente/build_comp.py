"""Genera comp.html (HyperFrames) desde script.json + timestamps.json.

Es codigo determinista, no creativo: el diseno del video vive en script.json (mundo, zonas, piezas
y una estacion de camara por beat). Las reglas de movimiento se aplican de forma estructural: solo
#cam y #drift se animan a escala global, asi que un corte de camara es imposible por construccion
(docs/reglas-de-camara.md).

Uso: python agente/build_comp.py --script data/escenas/S001/script.json \
       --stamps data/escenas/S001/timestamps.json --out data/escenas/S001/comp.html
"""
import argparse
import json
import math
import re
from pathlib import Path

# Tokens de marca (Tico renovado.md §2.1) + subtitulo replicado de pipeline/draw.py (CAMBIOS.md #3)
PAPEL, TINTA = "#FFF8F1", "#161616"
ROJO, AZUL, VERDE, AMAR, GRIS = "#E23A45", "#2F6BFF", "#39B57A", "#F4B942", "#8A8A8A"
BOX_BG, ACCENT, TXT_DIM, KW_TEXT = "#172A42", "#4A90D9", "#7A8699", "#ECF0F5"
SW = 12
LB, RB = "{", "}"          # llaves literales: los attr:{} de GSAP escapan mal en f-strings
VW, VH = 1080, 1920
SUB_TOP, SUB_SIZE, SUB_MAXW = 182, 45, 900   # el karaoke vive arriba, como en la serie entregada
CHIP_TOP = 1246                              # la franja amarilla "esto no es consejo medico"
PALABRAS_POR_LINEA = 6
TAIL_S, FADE_S = 0.9, 0.4


def n(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return f"{v:.3f}".rstrip("0").rstrip(".") or "0"
    return str(v)


def q(s):
    return json.dumps(str(s), ensure_ascii=False)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Comp:
    def __init__(self, script, stamps):
        self.sc, self.st = script, stamps
        self.svg, self.tweens = [], []
        self.mundo = script["mundo"]
        self.beats = script["beats"]
        self.arrivals = [float(b.get("t_real", b["t"])) for b in self.beats]
        self.durs = []
        for i, t in enumerate(self.arrivals):
            fin = self.arrivals[i + 1] if i + 1 < len(self.arrivals) else t + 4.5
            self.durs.append(max(0.6, fin - t))
        self.T = round(self.arrivals[-1] + self.durs[-1] + TAIL_S, 2)
        if stamps.get("words"):
            ultimo = stamps["words"][-1]
            self.T = round(ultimo["start"] + ultimo.get("dur", 0.3) + TAIL_S, 2)
        self.armar_encuadres()

    def armar_encuadres(self):
        """Estacion por beat + mundo auto-crecido: ningun encuadre puede asomarse fuera del papel."""
        self.piezas = [(z, pz) for z in self.mundo["zonas"] for pz in z.get("piezas", [])]
        self.stations, self.derivadas = [], 0
        for i, b in enumerate(self.beats):
            prim, extras, sangro = [], [], False
            for (_z, pz) in self.piezas:
                if int(pz.get("aparece", 0)) != i:
                    continue
                if pz["tipo"] in SANGRAN:      # el pulso decorativo puede sangrar fuera del cuadro
                    sangro = True
                    continue
                (extras if pz["tipo"] in ANOTACIONES else prim).append(caja(pz))
            if not prim and not extras:
                if sangro and self.stations:
                    # beat de solo adorno (un pulso, un destello): la camara NO se mueve, el adorno
                    # late sobre la escena que ya esta encuadrada. Moverse para encuadrar un anillo
                    # deja un cuadro de papel con una manchita.
                    self.stations.append(dict(self.stations[-1]))
                    self.derivadas += 0 if b.get("cam") else 1
                    continue
                centro = next((zz["c"] for zz in self.mundo["zonas"] if zz["id"] == b["zona"]),
                              [self.mundo["ancho"] / 2, self.mundo["alto"] / 2])
                prim = [(centro[0] - 620, centro[1] - 420, centro[0] + 620, centro[1] + 420)]
            st = estacion_de(prim, extras, b.get("cam"), self.stations[-1] if self.stations else None)
            self.derivadas += 0 if b.get("cam") else 1
            self.stations.append(st)
        self._acerca_anotaciones()   # ANTES del corrimiento: compara en las mismas unidades del shot-list
        marcos = [(st["x"] - VW / 2 / st["scale"], st["y"] - VH / 2 / st["scale"],
                   st["x"] + VW / 2 / st["scale"], st["y"] + VH / 2 / st["scale"]) for st in self.stations]
        x0, y0, x1, y1 = unir(marcos + [(0, 0, self.mundo["ancho"], self.mundo["alto"])])
        self.dx, self.dy = round(-min(0, x0), 1), round(-min(0, y0), 1)
        self.W, self.H = round(x1 + self.dx), round(y1 + self.dy)
        for st in self.stations:
            st["x"] = round(st["x"] + self.dx, 1)
            st["y"] = round(st["y"] + self.dy, 1)

    def _acerca_anotaciones(self):
        """Una bandera que no cabe SE ACERCA a la estacion; no achica el plano de su beat.

        El prototipo y la primera corrida de S001 perdian hasta un 28 % de zoom porque una etiqueta
        de 10 caracteres colgaba del borde. La etiqueta vive en el mundo, asi que su tamano depende
        de la escala: la unica salida honesta es moverla, no alejar la camara.
        """
        for i, st in enumerate(self.stations):
            s = st["scale"]
            fx0, fy0 = st["x"] - (VW / 2 - MARGEN_F) / s, st["y"] - (VH / 2 - MARGEN_F) / s
            fx1, fy1 = st["x"] + (VW / 2 - MARGEN_F) / s, st["y"] + (VH / 2 - MARGEN_F) / s
            for (_z, pz) in self.piezas:
                if int(pz.get("aparece", 0)) != i or pz["tipo"] not in ANOTACIONES:
                    continue
                for _ in range(6):
                    b = caja(pz)
                    if b[0] >= fx0 and b[2] <= fx1 and b[1] >= fy0 and b[3] <= fy1:
                        break
                    dx, dy = pz.get("hacia", [0, -190])
                    vx = pz["p"][0] + dx - st["x"]        # vector centro de estacion -> etiqueta
                    vy = pz["p"][1] + dy - st["y"]
                    pz["hacia"] = [round(dx - 0.3 * vx, 1), round(dy - 0.3 * vy, 1)]

    def focos_declarados(self):
        """Caja de pantalla (px) del contenido PRIMARIO de cada beat: lo que el pixel debe mostrar.

        El QC no puede conformarse con "hay algo dibujado": compara esta caja contra el bbox de
        pixeles distintos del papel. Es lo que agarra una camara mirando al lado equivocado, que con
        cobertura alta pasa (porque el dibujo de al lado también cuenta).
        """
        focos = []
        for i, st in enumerate(self.stations):
            cajas = [caja(pz) for (_z, pz) in self.piezas
                     if int(pz.get("aparece", 0)) == i and pz["tipo"] not in ANOTACIONES
                     and pz["tipo"] not in SANGRAN]
            if not cajas:
                focos.append(None)
                continue
            x0, y0, x1, y1 = unir(cajas)
            s = st["scale"]
            foco = [round(VW / 2 + s * (x0 + self.dx - st["x"])),
                    round(VH / 2 + s * (y0 + self.dy - st["y"])),
                    round(VW / 2 + s * (x1 + self.dx - st["x"])),
                    round(VH / 2 + s * (y1 + self.dy - st["y"]))]
            focos.append([max(0, min(VW, foco[0])), max(0, min(VH, foco[1])),
                          max(0, min(VW, foco[2])), max(0, min(VH, foco[3]))])
        return focos

    def js(self, linea):
        self.tweens.append(linea)

    def g(self, pid, x, y, inner):
        """<g> estatico con la posicion + <g> hijo animable (GSAP no pisa un transform propio)."""
        self.svg.append(f'<g transform="translate({n(x)} {n(y)})"><g id="{pid}" opacity="0">'
                        f'<g id="{pid}-br">{inner}</g></g></g>')

    def loop(self, sel, t0, t1, frm, to, period=1.6, ease="sine.inOut"):
        span = max(0.0, t1 - t0)
        period = max(0.5, min(period, max(0.5, span)))
        rep = max(0, int(span / period) - 1)
        a = ",".join(f"{k}:{n(v)}" for k, v in frm.items())
        b = ",".join(f"{k}:{n(v)}" for k, v in to.items())
        self.js(f'tl.fromTo({q(sel)}, {{{a}}}, {{{b},duration:{n(period)},ease:{q(ease)},'
                f'yoyo:true,repeat:{rep}}}, {n(t0)});')

    def entra(self, pid, t0, dy=30, d=0.55, ease="power3.out", escala=0.92):
        self.js(f'tl.fromTo({q("#" + pid)}, {{opacity:0,y:{n(dy)},scale:{n(escala)}}},'
                f' {{opacity:1,y:0,scale:1,duration:{n(d)},ease:{q(ease)}}}, {n(t0)});')

    def trazo(self, eid, t0, d=0.65):
        self.js(f'tl.to({q("#" + eid)}, {{strokeDashoffset:0,duration:{n(d)},ease:"power2.inOut"}}, {n(t0)});')

    def txt(self, x, y, s, size=54, peso=700, fill=TINTA, ancla="middle", eid=None):
        ident = f' id="{eid}"' if eid else ""
        return (f'<text{ident} x="{n(x)}" y="{n(y)}" font-family="Inter" font-weight="{peso}"'
                f' font-size="{size}" fill="{fill}" text-anchor="{ancla}"'
                f' dominant-baseline="middle">{esc(s)}</text>')


# ------------------------------------------------------------------ primitivas de anatomia (§2.4)
def p_ojo(c, pid, sp, t0, t1):
    k, col = float(sp.get("escala", 1)), sp.get("color", ROJO)
    rx, ry = 300 * k, 190 * k
    partes = [
        f'<ellipse rx="{n(rx)}" ry="{n(ry)}" fill="#FFFFFF" stroke="{TINTA}" stroke-width="{SW}"/>',
        f'<circle r="{n(88 * k)}" fill="{AZUL}" opacity="0.16"/>',
        f'<circle r="{n(88 * k)}" fill="none" stroke="{TINTA}" stroke-width="{n(SW * 0.7)}"/>',
        f'<circle r="{n(34 * k)}" fill="{TINTA}"/>',
        f'<ellipse rx="{n(rx * 1.16)}" ry="{n(ry * 1.22)}" fill="none" stroke="{col}"'
        f' stroke-width="{n(SW * 1.4)}" stroke-linecap="round" stroke-dasharray="{n(40 * k)} {n(26 * k)}"/>',
        f'<path id="{pid}-lid" d="M {n(-rx * 1.02)} 0 Q 0 {n(-ry * 1.15)} {n(rx * 1.02)} 0" fill="none"'
        f' stroke="{TINTA}" stroke-width="{SW}" stroke-linecap="round"/>',
    ]
    for i in range(int(sp.get("pulso", 0))):
        partes.append(f'<circle id="{pid}-p{i}" r="{n(rx * (1.35 + 0.28 * i))}" fill="none" stroke="{col}"'
                      f' stroke-width="{n(SW * 0.6)}" opacity="0"/>')
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0)
    c.loop(f"#{pid}-br", t0 + 0.5, t1, {"scale": 1.0}, {"scale": 1.035}, period=2.6)
    for i in range(int(sp.get("pulso", 0))):
        c.js(f'tl.fromTo({q("#" + pid + "-p" + str(i))}, {{opacity:0.75,scale:0.86}},'
             f' {{opacity:0,scale:1.14,duration:1.1,ease:"power1.out",repeat:9}},'
             f' {n(t0 + 0.6 + 0.34 * i)});')
    if sp.get("tembleque"):
        c.js(f'tl.to({q("#" + pid + "-lid")}, {{y:{n(9 * k)},duration:0.09,ease:"sine.inOut",'
             f'yoyo:true,repeat:13}}, {n(t0 + 0.5)});')


def p_silueta(c, pid, sp, t0, t1):
    k, a = float(sp.get("escala", 1)), n(SW * 1.1)
    partes = [
        f'<circle cx="0" cy="{n(-420 * k)}" r="{n(140 * k)}" fill="#FFFFFF" stroke="{TINTA}" stroke-width="{a}"/>',
        f'<path d="M {n(-95 * k)} {n(-300 * k)} Q {n(-150 * k)} {n(-120 * k)} {n(-120 * k)} 60'
        f' Q 0 {n(120 * k)} {n(120 * k)} 60 Q {n(150 * k)} {n(-120 * k)} {n(95 * k)} {n(-300 * k)} Z"'
        f' fill="#FFFFFF" stroke="{TINTA}" stroke-width="{a}" stroke-linejoin="round"/>',
        f'<path d="M {n(-130 * k)} {n(-160 * k)} L {n(-260 * k)} 40" stroke="{TINTA}" stroke-width="{a}"'
        f' stroke-linecap="round" fill="none"/>',
        f'<path d="M {n(130 * k)} {n(-160 * k)} L {n(260 * k)} 40" stroke="{TINTA}" stroke-width="{a}"'
        f' stroke-linecap="round" fill="none"/>',
        f'<path d="M {n(-60 * k)} 100 L {n(-80 * k)} 430" stroke="{TINTA}" stroke-width="{a}" stroke-linecap="round"/>',
        f'<path d="M {n(60 * k)} 100 L {n(80 * k)} 430" stroke="{TINTA}" stroke-width="{a}" stroke-linecap="round"/>',
    ]
    if sp.get("marca_ojo", True):
        partes.append(f'<circle id="{pid}-ojo" cx="{n(-46 * k)}" cy="{n(-440 * k)}" r="{n(30 * k)}" fill="{ROJO}"/>')
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=44, d=0.7)
    if sp.get("marca_ojo", True):
        c.loop(f"#{pid}-ojo", t0 + 0.8, t1, {"scale": 1.0, "opacity": 0.55},
               {"scale": 1.45, "opacity": 1.0}, period=1.15)


def p_circuito(c, pid, sp, t0, t1):
    cerebro, musculo = sp.get("cerebro", [-520, -120]), sp.get("musculo", [520, -120])
    ns = int(sp.get("senales", 3))
    partes = [
        f'<path d="M {n(cerebro[0] - 130)} {n(cerebro[1])} q 40 -120 130 -90 q 90 -30 120 60'
        f' q 60 60 -20 120 q -60 80 -140 40 q -110 20 -90 -130 Z" fill="#FFFFFF" stroke="{TINTA}"'
        f' stroke-width="{SW}" stroke-linejoin="round"/>',
        c.txt(cerebro[0], cerebro[1] - 200, "sistema nervioso", 44, 600, GRIS),
        f'<ellipse cx="{n(musculo[0])}" cy="{n(musculo[1])}" rx="150" ry="96" fill="{ROJO}"'
        f' opacity="0.2" stroke="{ROJO}" stroke-width="{SW}"/>',
        c.txt(musculo[0], musculo[1] - 170, "orbicular", 44, 600, GRIS),
    ]
    for i in range(ns):
        dy = -70 + i * 70
        x0, y0 = cerebro[0] + 150, cerebro[1] + dy
        x1, y1 = musculo[0] - 170, musculo[1] + dy * 0.4
        partes.append(
            f'<path id="{pid}-f{i}" d="M {n(x0)} {n(y0)} Q {n((x0 + x1) / 2)} {n(y0 - 130)} {n(x1)} {n(y1)}"'
            f' fill="none" stroke="{AZUL}" stroke-width="{n(SW * 0.8)}" stroke-linecap="round" data-draw="1"'
            f' opacity="0.85"/>')
        partes.append(f'<circle id="{pid}-s{i}" cx="{n(x0)}" cy="{n(y0)}" r="17" fill="{AZUL}" opacity="0"/>')
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=18, escala=1.0)
    for i in range(ns):
        dy = -70 + i * 70
        x0, y0 = cerebro[0] + 150, cerebro[1] + dy
        x1, y1 = musculo[0] - 170, musculo[1] + dy * 0.4
        c.trazo(f"{pid}-f{i}", t0 + 0.25 + i * 0.12, 0.8)
        sel = q("#" + pid + f"-s{i}")
        rep = max(1, int((t1 - t0 - 1.4) / 1.9))
        c.js(f'tl.to({sel}, {{opacity:1,duration:0.25}}, {n(t0 + 1.0 + i * 0.06)});')
        c.js(f'tl.fromTo({sel}, {LB}attr:{LB}cx:{n(x0)},cy:{n(y0)}{RB}{RB}, {LB}attr:{LB}cx:{n(x1)},'
             f'cy:{n(y1)}{RB}, duration:1.1, ease:"power1.inOut", repeat:{rep}{RB}, {n(t0 + 1.1 + i * 0.3)});')
    if sp.get("desorden"):
        c.js(f'tl.to({q("#" + pid)}, {{rotation:1.6,duration:0.24,ease:"none",yoyo:true,repeat:15}},'
             f' {n(t0 + 0.6)});')


def p_bateria(c, pid, sp, t0, t1):
    w, nivel = 360.0, float(sp.get("nivel", 12))
    partes = [
        f'<rect x="{n(-w / 2)}" y="-70" width="{n(w)}" height="140" rx="18" fill="#FFFFFF"'
        f' stroke="{TINTA}" stroke-width="{SW}"/>',
        f'<rect x="{n(w / 2)}" y="-24" width="26" height="48" rx="10" fill="{TINTA}"/>',
        f'<rect id="{pid}-fill" x="{n(-w / 2 + 16)}" y="-54" width="0" height="108" rx="10" fill="{AMAR}"/>',
        c.txt(0, 132, sp.get("etiqueta", "energia del sistema"), 44, 600, GRIS),
    ]
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=20, escala=1.0)
    c.js(f'tl.to({q("#" + pid + "-fill")}, {LB}attr:{LB}width:{n(max(0.0, w * nivel / 100 - 32))}{RB},'
         f' duration:1.1, ease:"back.out(1.4)"{RB}, {n(t0 + 0.45)});')


def p_tazas(c, pid, sp, t0, t1):
    total = int(sp.get("n", 3))
    partes = []
    for i in range(total):
        x = -140 + i * 150
        partes.append(
            f'<g id="{pid}-t{i}" opacity="0">'
            f'<path d="M {n(x - 52)} -30 L {n(x + 52)} -30 L {n(x + 40)} 84 Q {n(x)} 100 {n(x - 40)} 84 Z"'
            f' fill="#FFFFFF" stroke="{TINTA}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M {n(x + 52)} 0 q 46 6 8 60" fill="none" stroke="{TINTA}"'
            f' stroke-width="{n(SW * 0.8)}"/>'
            f'<path id="{pid}-h{i}" d="M {n(x - 18)} -60 q 22 -30 0 -58" fill="none" stroke="{GRIS}"'
            f' stroke-width="{n(SW * 0.7)}" stroke-linecap="round" data-draw="1"/></g>')
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=14, escala=1.0)
    for i in range(total):
        c.js(f'tl.fromTo({q("#" + pid + "-t" + str(i))}, {{opacity:0,y:40}}, {{opacity:1,y:0,'
             f'duration:0.45,ease:"back.out(1.5)"}}, {n(t0 + 0.4 + i * 0.22)});')
        c.trazo(f"{pid}-h{i}", t0 + 0.8 + i * 0.22, 0.9)
        c.loop(f"#{pid}-h{i}", t0 + 1.7 + i * 0.22, t1, {"y": 0, "opacity": 0.9},
               {"y": -26, "opacity": 0.15}, period=1.8)


def p_monitor(c, pid, sp, t0, t1):
    partes = [
        f'<rect x="-230" y="-160" width="460" height="300" rx="16" fill="#FFFFFF" stroke="{TINTA}"'
        f' stroke-width="{SW}"/>',
        f'<rect x="-70" y="140" width="140" height="60" rx="10" fill="none" stroke="{TINTA}"'
        f' stroke-width="{SW}"/>',
        c.txt(0, -20, sp.get("reloj", "00:47"), 96, 700, AZUL, eid=f"{pid}-hz"),
        c.txt(0, -104, "pantalla hasta tarde", 40, 600, GRIS),
    ]
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=26)
    c.loop(f"#{pid}-hz", t0 + 0.7, t1, {"opacity": 1.0}, {"opacity": 0.4}, period=1.4)


def p_linea_tiempo(c, pid, sp, t0, t1):
    w, dias = float(sp.get("w", 900)), int(sp.get("dias", 7))
    partes = [f'<line x1="{n(-w / 2)}" y1="0" x2="{n(w / 2)}" y2="0" stroke="{TINTA}"'
              f' stroke-width="{SW}" stroke-linecap="round"/>']
    for d in range(dias + 1):
        x = -w / 2 + w * d / dias
        partes.append(f'<line x1="{n(x)}" y1="-16" x2="{n(x)}" y2="16" stroke="{TINTA}"'
                      f' stroke-width="{n(SW * 0.6)}"/>')
        partes.append(c.txt(x, 58, str(d), 36, 600, GRIS))
    partes.append(f'<circle id="{pid}-pt" cx="{n(-w / 2)}" cy="0" r="22" fill="{VERDE}"/>')
    partes.append(c.txt(0, -96, sp.get("etiqueta", "dias hasta calmarse"), 44, 700, TINTA))
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=16, escala=1.0)
    c.js(f'tl.to({q("#" + pid + "-pt")}, {LB}attr:{LB}cx:{n(w / 2)}{RB}, '
         f'duration:{n(min(3.4, max(1.2, t1 - t0 - 1)))}, ease:"power1.inOut", '
         f'repeat:{max(0, int((t1 - t0 - 4) / 4.6))}{RB}, {n(t0 + 0.6)});')


def p_ficha(c, pid, sp, t0, t1):
    w, h, badge = float(sp.get("w", 430)), float(sp.get("h", 240)), sp.get("badge")
    col = VERDE if badge == "check" else (ROJO if badge == "cruz" else TINTA)
    partes = [
        f'<rect x="{n(-w / 2 + 10)}" y="{n(-h / 2 + 14)}" width="{n(w)}" height="{n(h)}" rx="16"'
        f' fill="{TINTA}" opacity="0.1"/>',
        f'<rect x="{n(-w / 2)}" y="{n(-h / 2)}" width="{n(w)}" height="{n(h)}" rx="16" fill="#FFFFFF"'
        f' stroke="{TINTA}" stroke-width="{SW}"/>',
        c.txt(0, -h * 0.16, sp.get("titulo", ""), 52, 700, TINTA),
        c.txt(0, h * 0.18, sp.get("nota", ""), 38, 500, GRIS),
    ]
    if badge:
        bx, by = w / 2 - 8, -h / 2 + 8
        mark = (f'<path d="M {n(bx - 26)} {n(by)} l 18 20 l 30 -34" fill="none" stroke="#FFFFFF"'
                f' stroke-width="11" stroke-linecap="round"/>') if badge == "check" else (
            f'<path d="M {n(bx - 22)} {n(by - 22)} L {n(bx + 22)} {n(by + 22)} M {n(bx + 22)}'
            f' {n(by - 22)} L {n(bx - 22)} {n(by + 22)}" fill="none" stroke="#FFFFFF"'
            f' stroke-width="12" stroke-linecap="round"/>')
        partes.append(f'<circle id="{pid}-bg" cx="{n(bx)}" cy="{n(by)}" r="44" fill="{col}" opacity="0"/>'
                      + mark)
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=34, d=0.5)
    if badge:
        c.js(f'tl.to({q("#" + pid + "-bg")}, {{opacity:1,duration:0.3,ease:"power2.out"}},'
             f' {n(t0 + 0.55)});')


def p_bandera(c, pid, sp, t0, t1):
    """Banderita de papel con hilo finito: la unica etiqueta permitida del canal (§2.4)."""
    dx, dy = sp.get("hacia", [0, -190])
    txt = str(sp.get("texto", "")).upper()
    fw = 34 + 34 * len(txt)
    partes = [
        f'<path id="{pid}-hi" d="M 0 0 Q {n(dx * 0.4)} {n(dy * 0.55)} {n(dx)} {n(dy)}" fill="none"'
        f' stroke="{TINTA}" stroke-width="{n(SW * 0.45)}" data-draw="1"/>',
        f'<rect id="{pid}-fl" x="{n(dx - fw / 2)}" y="{n(dy - 44)}" width="{n(fw)}" height="88" rx="12"'
        f' fill="#FFFFFF" stroke="{TINTA}" stroke-width="{n(SW * 0.8)}" opacity="0"/>',
        f'<text id="{pid}-tx" x="{n(dx)}" y="{n(dy)}" font-family="Inter" font-weight="800"'
        f' font-size="44" fill="{TINTA}" text-anchor="middle" dominant-baseline="middle" opacity="0">'
        f'{esc(txt)}</text>',
        f'<circle cx="0" cy="0" r="11" fill="{ROJO}"/>',
    ]
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=10, escala=1.0)
    c.trazo(f"{pid}-hi", t0 + 0.18, 0.5)
    c.js(f'tl.fromTo({q("#" + pid + "-fl")}, {{opacity:0,scale:0.82}}, {{opacity:1,scale:1,'
         f'duration:0.34,ease:"back.out(1.7)"}}, {n(t0 + 0.5)});')
    # la caja y su palabra entran JUNTAS: una banderita sin texto se lee como un error de render
    c.js(f'tl.fromTo({q("#" + pid + "-tx")}, {{opacity:0}}, {{opacity:1,duration:0.34,'
         f'ease:"power2.out"}}, {n(t0 + 0.5)});')


def p_texto(c, pid, sp, t0, t1):
    c.g(pid, sp["p"][0], sp["p"][1],
        c.txt(0, 0, sp["texto"], sp.get("size", 64), sp.get("peso", 800), sp.get("fill", TINTA)))
    c.entra(pid, t0, dy=22, d=0.5, escala=1.0)


def p_anillo(c, pid, sp, t0, t1):
    r, col, total = float(sp.get("r", 260)), sp.get("color", AZUL), int(sp.get("n", 3))
    partes = [f'<circle id="{pid}-a{i}" r="{n(r * (1 + 0.42 * i))}" fill="none" stroke="{col}"'
              f' stroke-width="{n(SW * 0.7)}" opacity="0"/>' for i in range(total)]
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    for i in range(total):
        c.js(f'tl.fromTo({q("#" + pid + "-a" + str(i))}, {{opacity:0.7,scale:0.9}},'
             f' {{opacity:0,scale:1.25,duration:1.2,ease:"power1.out",repeat:7}},'
             f' {n(t0 + 0.5 + i * 0.25)});')


def p_mano(c, pid, sp, t0, t1):
    partes = [
        f'<path id="{pid}-m" d="M -260 150 Q -250 -60 -170 -110 L -150 -250 Q -120 -270 -104 -240'
        f' L -96 -120 L -66 -280 Q -34 -296 -16 -262 L -6 -120 L 30 -268 Q 62 -280 76 -248 L 82 -120'
        f' L 128 -220 Q 158 -226 166 -190 L 170 -70 Q 250 -30 236 120 Q 200 210 -40 210 Q -230 210'
        f' -260 150 Z" fill="#FFFFFF" stroke="{TINTA}" stroke-width="{SW}" stroke-linejoin="round"'
        f' data-draw="1"/>']
    for i in range(5 if sp.get("arrugas", True) else 0):
        y = -150 + i * 46
        partes.append(f'<path id="{pid}-ar{i}" d="M {n(-140 + i * 8)} {n(y)} q 40 -18 90 0 q 44 16 88 -2"'
                      f' fill="none" stroke="{GRIS}" stroke-width="{n(SW * 0.6)}" stroke-linecap="round"'
                      f' data-draw="1"/>')
    for i in range(2 if sp.get("onda", True) else 0):
        partes.append(f'<path id="{pid}-on{i}" d="M -420 {n(230 + i * 54)} q 120 -46 240 0 q 120 46 240 0'
                      f' q 120 -46 240 0" fill="none" stroke="{AZUL}" stroke-width="{SW}"'
                      f' stroke-linecap="round" opacity="{n(0.75 - i * 0.3)}"/>')
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=30, d=0.75, escala=0.96)
    c.trazo(f"{pid}-m", t0 + 0.2, 1.0)
    for i in range(5 if sp.get("arrugas", True) else 0):
        c.trazo(f"{pid}-ar{i}", t0 + 1.0 + i * 0.16, 0.55)
    for i in range(2 if sp.get("onda", True) else 0):
        c.loop(f"#{pid}-on{i}", t0 + 0.4, t1, {"x": -18}, {"x": 18}, period=2.2 + i * 0.6)


REGISTRO = {"ojo": p_ojo, "silueta": p_silueta, "circuito": p_circuito, "bateria": p_bateria,
            "tazas": p_tazas, "monitor": p_monitor, "linea_tiempo": p_linea_tiempo, "ficha": p_ficha,
            "bandera": p_bandera, "texto": p_texto, "anillo": p_anillo, "mano": p_mano}



# ------------------------------------------------------------------ caja de cada pieza y encuadre asistido
def caja(pz):
    """Caja (x0,y0,x1,y1) en unidades del mundo que ocupa una pieza. Sirve para derivar la camara."""
    x, y = float(pz["p"][0]), float(pz["p"][1])
    k = float(pz.get("escala", 1.0))
    tipo = pz["tipo"]
    if tipo == "ojo":
        w, h = 720 * k, 480 * k
    elif tipo == "silueta":
        w, h = 540 * k, 1010 * k
    elif tipo == "circuito":
        ce, mu = pz.get("cerebro", [-520, -120]), pz.get("musculo", [520, -120])
        return (x + min(ce[0] - 150, mu[0] - 170), y + min(ce[1], mu[1]) - 320,
                x + max(ce[0] + 150, mu[0] + 170), y + max(ce[1], mu[1]) + 190)
    elif tipo == "bateria":
        w, h = 390, 230
    elif tipo == "tazas":
        nn = int(pz.get("n", 3))
        return (x - 192, y - 120, x - 192 + 150 * (nn - 1) + 216, y + 104)
    elif tipo == "monitor":
        w, h = 460, 370
    elif tipo == "linea_tiempo":
        w, h = float(pz.get("w", 900)) + 60, 210
    elif tipo == "ficha":
        w, h = float(pz.get("w", 430)), float(pz.get("h", 240))
    elif tipo == "bandera":
        dx, dy = pz.get("hacia", [0, -190])
        fw = 34 + 34 * len(str(pz.get("texto", "")))
        return (min(x - 14, x + dx - fw / 2), min(y - 14, y + dy - 50),
                max(x + 14, x + dx + fw / 2), max(y + 14, y + dy + 50))
    elif tipo == "texto":
        w = len(str(pz.get("texto", ""))) * float(pz.get("size", 64)) * 0.52
        return (x - w / 2, y - 44, x + w / 2, y + 44)
    elif tipo == "anillo":
        r = float(pz.get("r", 260)) * 1.42
        w = h = 2 * r
    elif tipo == "mano":
        return (x - 420 if pz.get("onda", True) else x - 262, y - 300,
                x + 540 if pz.get("onda", True) else x + 238, y + 290)
    else:
        w, h = 400, 400
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def unir(cajas):
    return (min(c[0] for c in cajas), min(c[1] for c in cajas),
            max(c[2] for c in cajas), max(c[3] for c in cajas))


# Regla L1 aplicada por codigo: el foco ocupa ~78% del ancho y hasta 62% del alto del cuadro.
ANCHO_FOCO, ALTO_FOCO, MAX_S, MIN_S = 0.78, 0.62, 1.35, 0.30
MARGEN_F = 34                       # px de aire entre una etiqueta y el borde del cuadro
ANOTACIONES = {"bandera", "anillo"}   # etiquetan: no mandan el encuadre, solo deben caber
SANGRAN = {"anillo"}                  # pulsos decorativos: pueden salirse del cuadro, no achican el plano


def estacion_de(primarias, extras, declarado, anterior):
    """Encuadre derivado del contenido del beat; la declaracion del guionista manda si existe."""
    if declarado:
        return dict(declarado)
    if not primarias:                      # beat de acento: la camara no se mueve, solo deriva
        if not anterior:
            return {"x": 1600, "y": 1600, "scale": 0.7}
        st = dict(anterior)
        for b in extras:                   # la etiqueta nueva debe caber en la estacion heredada
            hx = max(abs(b[0] - st["x"]), abs(b[2] - st["x"]), 1.0)
            hy = max(abs(b[1] - st["y"]), abs(b[3] - st["y"]), 1.0)
            st["scale"] = min(st["scale"], 0.47 * VW / hx, 0.47 * VH / hy)
        st["scale"] = round(max(st["scale"], MIN_S), 3)
        return st
    x0, y0, x1, y1 = unir(primarias)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = min(ANCHO_FOCO * VW / max(60.0, x1 - x0), ALTO_FOCO * VH / max(60.0, y1 - y0))
    s_foco = s
    for b in primarias + extras:           # nada relevante queda fuera del cuadro
        hx = max(abs(b[0] - cx), abs(b[2] - cx), 1.0)
        hy = max(abs(b[1] - cy), abs(b[3] - cy), 1.0)
        s = min(s, 0.47 * VW / hx, 0.47 * VH / hy)
    # una etiqueta no manda el plano: si aun asi no cabria, _acerca_anotaciones la mueve
    return {"x": round(cx, 1), "y": round(cy, 1),
            "scale": round(min(max(max(s, 0.94 * s_foco), MIN_S), MAX_S), 3)}


# ------------------------------------------------------------------ camara continua (C1-C6)
def est(st, s=None):
    """Estacion de mundo -> valores GSAP de #cam con transform-origin 0 0: pantalla = x + s*mundo."""
    sc = st["scale"] if s is None else s
    return {"scale": sc, "x": VW / 2 - sc * st["x"], "y": VH / 2 - sc * st["y"]}


def viaje_de(c, i):
    """Duracion del tramo de camara que precede al beat i.

    Un sola cuenta para tres cosas que tienen que coincidir: el tween de `#cam`, el replay del
    manifiesto y el momento en que el beat empieza a dibujarse. Si se desincronizan, el QC mide una
    coreografia distinta de la que se renderizo.
    """
    return 1.1 if i <= 0 else min(1.30, max(0.55, 0.35 * c.durs[i]))


def camara(c):
    st0, a0 = c.stations[0], est(c.stations[0])
    pre = est(st0, st0["scale"] * 0.94)
    c.js(f'tl.fromTo("#cam", {{scale:{n(pre["scale"])},x:{n(pre["x"])},y:{n(pre["y"])}}},'
         f' {{scale:{n(a0["scale"])},x:{n(a0["x"])},y:{n(a0["y"])},duration:1.1,ease:"power2.out"}}, 0);')
    for i in range(1, len(c.beats)):
        b = est(c.stations[i])
        viaje = viaje_de(c, i)
        inicio = max(0.05, c.arrivals[i] - viaje + 0.05)
        c.js(f'tl.to("#cam", {{scale:{n(b["scale"])},x:{n(b["x"])},y:{n(b["y"])},'
             f'duration:{n(viaje)},ease:"power2.inOut"}}, {n(inicio)});')
    # C3 respiracion perpetua: ver _deriva(). Un keyframe con easing frena en cada extremo y el QC lo
    # mide como fotograma congelado; aca la velocidad compuesta nunca se anula dos periodos seguidos.
    dx, dy = _deriva(c)
    c.js(f'tl.to("#drift", {{keyframes:{{x:{dx},y:{dy}}},duration:{n(c.T)},easeEach:"none"}}, 0);')


def _deriva(c, dt=0.25):
    """Dos senoides de periodos inconmensurables, muestreadas y unidas en linea recta.

    C3 pide "dos senoides desfasadas". Escritas como keyframes con `sine.inOut`, cada keyframe frena
    la camara una fraccion de segundo: el QC midio 13 fotogramas con |dluma| < 0,05 sobre un master
    real. Con periodos que no coinciden (5,0 s y 3,1 s en x; 5,0 s y 3,7 s en y) los dos extremos de
    cada eje no caen en el mismo instante y la velocidad compuesta no se anula lo bastante tiempo
    como para congelar un cuadro. La interpolacion es lineal entre muestras a 4 Hz: sobre un seno de
    5 s el error de posicion es ~0,3 % de la amplitud, invisible, y el HTML cuesta 220 numeros.
    Determinista: `math.sin` de Python en el build, nada de `random` ni `Date.now` en el navegador.
    """
    w = lambda t, per, f: math.sin(2 * math.pi * t / per + f)
    xs = [18 * w(t, 5.0, 0.0) + 9 * w(t, 3.1, 1.1) for t in _tk(c.T, dt)]
    ys = [-22 * w(t, 5.0, 0.6) + 11 * w(t, 3.7, 2.3) for t in _tk(c.T, dt)]
    return [[round(v - xs[0], 2) for v in xs], [round(v - ys[0], 2) for v in ys]]


def _tk(T, dt):
    n = int(T / dt) + 1
    return [i * dt for i in range(n)]


# ------------------------------------------------------------------ manifiesto de camara (QC C2)
def _p2io(u):
    """power2.inOut de GSAP (cubica). Misma formula que el tween, para muestrear la curva."""
    return 4 * u * u * u if u < 0.5 else 1 - pow(-2 * u + 2, 3) / 2


def _p2out(u):
    return 1 - pow(1 - u, 3)


def manifest_camara(c, fps=30):
    """Reproduce en Python las estaciones que camara() escribe en JS: el QC mide continuidad real."""
    a0 = c.stations[0]["scale"]
    tramos = [(0.0, viaje_de(c, 0), a0 * 0.94, a0, _p2out)]
    for i in range(1, len(c.beats)):
        viaje = viaje_de(c, i)
        tramos.append((max(0.05, c.arrivals[i] - viaje + 0.05), viaje,
                       c.stations[i - 1]["scale"], c.stations[i]["scale"], _p2io))
    curva = []
    for f in range(int(c.T * fps)):
        t = f / fps
        s = tramos[0][2]
        for (t0, dur, s0, s1, ease) in tramos:
            if t < t0:
                break
            s = s1 if t > t0 + dur else s0 + (s1 - s0) * ease((t - t0) / dur)
        curva.append({"t": round(t, 3), "scale": round(s, 5)})
    return curva


# ------------------------------------------------------------------ subtitulos karaoke (§4.6-CAMBIOS)
def grupos(c):
    """Igual que draw.py: una sola linea activa a la vez, palabras de izquierda a derecha."""
    words = c.st.get("words", [])
    out = []
    for i, b in enumerate(c.beats):
        t0, t1 = c.arrivals[i], (c.arrivals[i + 1] if i + 1 < len(c.arrivals) else c.T)
        ns = [w for w in words if t0 - 0.03 <= w["start"] < t1 - 0.03]
        if not ns:
            toks, dur = b["linea"].split(), max(0.6, (t1 - t0) * 0.86)
            peso, acc = max(1, sum(len(t) for t in toks)), t0 + 0.12
            for t in toks:
                d = dur * len(t) / peso
                ns.append({"word": t, "start": round(acc, 3), "dur": round(d, 3)})
                acc += d
        kws = [re.sub(r"[¿?.,!¡:;\"'()]", "", k).lower().strip() for k in b.get("keywords", [])]
        marks = []
        for w in ns:
            limpio = re.sub(r"[¿?.,!¡:;\"'()]", "", w["word"]).lower()
            marks.append((w, any(k and (k == limpio or k in limpio) for k in kws)))
        cur, lineas = [], []
        for m in marks:
            cur.append(m)
            if len(cur) >= PALABRAS_POR_LINEA:
                lineas.append(cur)
                cur = []
        if cur:
            lineas.append(cur)
        for ln in lineas:
            out.append({"i": i, "words": ln, "t0": max(0.0, ln[0][0]["start"] - 0.06),
                        "t1": ln[-1][0]["start"] + ln[-1][0].get("dur", 0.3) + 0.42})
    return out


SUB_HTML = """
<div id="subs">{GRPOS}</div>
"""

BOX_JS = r"""
document.querySelectorAll('.grp').forEach(function(grp){
  var layer = grp.querySelector('.boxlayer'), k = 0;
  grp.querySelectorAll('.w[data-kw]').forEach(function(w){
    var box = document.createElement('b');
    box.className = 'kw';
    box.id = grp.id + '-kw' + (k++);
    box.style.left = (w.offsetLeft - 11) + 'px';
    box.style.top = (w.offsetTop - 6) + 'px';
    box.style.width = (w.offsetWidth + 22) + 'px';
    box.style.height = (w.offsetHeight + 12) + 'px';
    box.innerHTML = '<i></i><i></i><i></i><i></i>';
    box.style.opacity = '0';
    layer.appendChild(box);
  });
});
"""


def subtitulos(c):
    gs = grupos(c)
    html = []
    for gi, g in enumerate(gs):
        spans = "".join(
            f'<span class="w{" k" if kw else ""}" id="w{gi}_{wi}"'
            f'{" data-kw=1" if kw else ""}>{esc(w["word"])}</span>'
            for wi, (w, kw) in enumerate(g["words"]))
        html.append(f'<div class="grp" id="g{gi}"><div class="boxlayer" id="bl{gi}"></div>{spans}</div>')
    for gi, g in enumerate(gs):
        c.js(f'tl.set("#g{gi}", {{opacity:1,visibility:"visible"}}, {n(g["t0"])});')
        cajas = 0
        for wi, (w, kw) in enumerate(g["words"]):
            c.js(f'tl.to("#w{gi}_{wi}", {{color:{q(KW_TEXT if kw else TINTA)},duration:0.09,ease:"none"}},'
                 f' {n(max(0.0, w["start"]))});')
            if kw:
                c.js(f'tl.fromTo({q("#g" + str(gi) + "-kw" + str(cajas))}, {{opacity:0,scale:0.86}},'
                     f' {{opacity:1,scale:1,duration:0.13,ease:"power2.out"}},'
                     f' {n(max(0.0, w["start"]))});')
                cajas += 1
        c.js(f'tl.set("#g{gi}", {{opacity:0,visibility:"hidden"}}, {n(g["t1"])});')
    return "".join(html)


# ------------------------------------------------------------------ ensamble del documento
CSS = f"""
html, body {{ width: {VW}px; height: {VH}px; margin: 0; padding: 0; }}
#root {{ position: relative; width: {VW}px; height: {VH}px; background: {PAPEL}; overflow: hidden; }}
.clip {{ position: absolute; left: 0; top: 0; width: {VW}px; height: {VH}px; }}
#scene {{ overflow: hidden; }}
#cam {{ position: absolute; left: 0; top: 0; transform-origin: 0 0; }}
#drift {{ position: absolute; left: 0; top: 0; }}
#world {{ display: block; }}
#bar {{ position: absolute; left: 0; top: 0; width: {VW}px; height: 6px; background: rgba(22,22,22,.4);
        transform-origin: 0 50%; }}
#subs {{ position: absolute; left: {(VW - SUB_MAXW) // 2}px; top: {SUB_TOP}px; width: {SUB_MAXW}px;
         overflow: visible; }}
.grp {{ position: absolute; left: 0; top: 0; width: {SUB_MAXW}px; text-align: center;
        font-family: 'Inter'; font-weight: 600; font-size: {SUB_SIZE}px; line-height: 1.34;
        opacity: 0; visibility: hidden; }}
.boxlayer {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; pointer-events: none; }}
.w {{ display: inline-block; color: {TXT_DIM}; margin: 0 4px; }}
.kw {{ position: absolute; display: block; background: {BOX_BG}; border: 3px solid {ACCENT};
       border-radius: 10px; }}
.kw i {{ position: absolute; width: 13px; height: 13px; border-radius: 50%; background: {BOX_BG};
         border: 2px solid {ACCENT}; }}
.kw i:nth-child(1) {{ left: -8px; top: -8px; }}
.kw i:nth-child(2) {{ right: -8px; top: -8px; }}
.kw i:nth-child(3) {{ left: -8px; bottom: -8px; }}
.kw i:nth-child(4) {{ right: -8px; bottom: -8px; }}
#chip {{ position: absolute; left: 50%; top: {CHIP_TOP}px; margin-left: -280px; width: 560px;
         font-family: 'Inter'; font-weight: 700; font-size: 34px; color: {TINTA};
         background: {AMAR}; border: 4px solid {TINTA}; border-radius: 14px; padding: 12px 0;
         text-align: center; opacity: 0; }}
#fade {{ position: absolute; left: 0; top: 0; width: {VW}px; height: {VH}px; background: {PAPEL};
         opacity: 0; }}
"""

FONTS = """
@font-face { font-family: 'Inter'; src: url('assets/fonts/Inter-Regular.ttf'); font-weight: 400; }
@font-face { font-family: 'Inter'; src: url('assets/fonts/Inter-Medium.ttf'); font-weight: 500; }
@font-face { font-family: 'Inter'; src: url('assets/fonts/Inter-SemiBold.ttf'); font-weight: 600; }
@font-face { font-family: 'Inter'; src: url('assets/fonts/Inter-Bold.ttf'); font-weight: 700; }
@font-face { font-family: 'Inter'; src: url('assets/fonts/Inter-Bold.ttf'); font-weight: 800; }
"""


def construir(ruta_script, ruta_stamps, ruta_out):
    sc = json.loads(Path(ruta_script).read_text(encoding="utf-8"))
    st = json.loads(Path(ruta_stamps).read_text(encoding="utf-8"))
    c = Comp(sc, st)
    W, H = c.W, c.H
    fondo = (f'<defs><pattern id="papel" width="120" height="120" patternUnits="userSpaceOnUse">'
             f'<circle cx="18" cy="24" r="2.4" fill="{TINTA}" opacity="0.05"/>'
             f'<circle cx="76" cy="86" r="2" fill="{TINTA}" opacity="0.045"/></pattern></defs>'
             f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPEL}"/>'
             f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#papel)"/>'
             f'<rect x="26" y="26" width="{W - 52}" height="{H - 52}" fill="none" stroke="{TINTA}"'
             f' stroke-width="3" opacity="0.16" rx="40"/>')
    for z, pz in c.piezas:
        i = min(int(pz.get("aparece", 0)), len(c.arrivals) - 1)
        # La pieza se dibuja DURANTE el viaje de la camara, no despues de la llegada. Dos consecuencias
        # medidas en S001: el cuadro ya no es crema lisa mientras la camara cruza de una zona a la
        # otra (83 fotogramas casi vacios), y cuando el narrador nombra la cosa, esa cosa ya esta
        # dibujada y centrada (regla C1).
        t0 = max(0.0, c.arrivals[i] - viaje_de(c, i) - 0.15 + float(pz.get("retraso", 0.12)))
        sp = dict(pz)
        sp["p"] = [float(pz["p"][0]) + c.dx, float(pz["p"][1]) + c.dy]
        REGISTRO[pz["tipo"]](c, pz["id"], sp, t0, c.T)
    world = (f'<svg id="world" class="world" width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
             f' xmlns="http://www.w3.org/2000/svg">{fondo}{"".join(c.svg)}</svg>')
    camara(c)
    sub_html = subtitulos(c)
    chips = [(i, b["chip"]) for i, b in enumerate(c.beats) if b.get("chip")]
    if chips:
        c.js(f'tl.to("#chip", {{opacity:1,duration:0.3,ease:"power2.out"}},'
             f' {n(c.arrivals[chips[0][0]] + 0.4)});')
    c.js(f'tl.fromTo("#bar", {{scaleX:0}}, {{scaleX:1,duration:{n(c.T - FADE_S)},ease:"none"}}, 0);')
    c.js(f'tl.to("#fade", {{opacity:1,duration:{n(FADE_S)},ease:"power1.in"}}, {n(c.T - FADE_S)});')

    js_body = "\n".join([
        "document.querySelectorAll('[data-draw]').forEach(function(el){"
        "  var L = el.getTotalLength();",
        "  el.style.strokeDasharray = L; el.style.strokeDashoffset = L; });",
        BOX_JS.strip(),
        "window.__timelines = window.__timelines || {};",
        "const tl = gsap.timeline({ paused: true });",
        *c.tweens,
        'window.__timelines["main"] = tl;',
        "tl.seek(0);",
    ])
    doc = (f'<!doctype html>\n<html lang="es">\n<head><meta charset="utf-8">'
           f'<title>{esc(sc["slug"])}</title>\n<style>{FONTS}{CSS}</style></head>\n<body>\n'
           f'<div id="root" data-composition-id="main" data-start="0" data-duration="{n(c.T)}"'
           f' data-fps="{sc.get("fps", 30)}" data-width="{VW}" data-height="{VH}">\n'
           f'  <div id="scene" class="clip" data-start="0" data-duration="{n(c.T)}" data-track-index="1">\n'
           f'    <div id="cam" style="width:{W}px;height:{H}px"><div id="drift" '
           f'style="width:{W}px;height:{H}px">{world}</div></div>\n  </div>\n'
           f'  <div id="hud" class="clip" data-start="0" data-duration="{n(c.T)}" data-track-index="2">\n'
           f'    <div id="bar"></div>{SUB_HTML.format(GRPOS=sub_html)}\n'
           f'    <div id="chip">{esc(chips[0][1]) if chips else "Esto no es consejo medico"}</div>\n'
           f'    <div id="fade"></div>\n  </div>\n</div>\n'
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>\n'
           f'<script>\n{js_body}\n</script>\n</body>\n</html>\n')
    Path(ruta_out).write_text(doc, encoding="utf-8")
    # Las franjas del HUD se declaran ACA, en la unica unidad que las conoce (px de pantalla), y el
    # QC las lee. Si el QC las hardcodea, una banda mal ubicada mide los subtitulos como si fueran
    # dibujo: cobertura inflada y escena vacia en verde.
    alto_subs = SUB_TOP + 2 * 60 + 24   # se reservan 2 lineas: un grupo puede solapar al anterior
    meta = {"ancho": VW, "alto": VH,
            "bandas": [[0.0, round(alto_subs / VH, 4)],
                       [round(CHIP_TOP / VH, 4), round((CHIP_TOP + 92) / VH, 4)]],
            "focos": c.focos_declarados()}
    Path(ruta_out).with_name("comp_meta.json").write_text(json.dumps(meta, ensure_ascii=False,
                                                                     indent=2), encoding="utf-8")
    curva = manifest_camara(c, int(sc.get("fps", 30)))
    man = Path(ruta_out).with_name("cam_manifest.jsonl")
    man.write_text("".join(json.dumps(k, ensure_ascii=False) + "\n" for k in curva), encoding="utf-8")
    d2 = max(abs(curva[i + 1]["scale"] - 2 * curva[i]["scale"] + curva[i - 1]["scale"])
             for i in range(1, len(curva) - 1))
    return {"out": str(ruta_out), "duracion_s": c.T, "mundo": [c.W, c.H],
            "piezas": len(c.piezas), "palabras_sub": len(st.get("words", [])),
            "camaras_derivadas": f"{c.derivadas}/{len(c.beats)}",
            "manifiesto_camara": str(man), "aceleracion_max": round(d2, 5),
            "estaciones": [{"t": round(c.arrivals[i], 2), "zona": b["zona"],
                            "scale": c.stations[i]["scale"]} for i, b in enumerate(c.beats)],
            "tweens": len(c.tweens)}


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--stamps", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print(json.dumps(construir(a.script, a.stamps, a.out), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
