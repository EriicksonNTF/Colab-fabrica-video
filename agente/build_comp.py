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
import unicodedata
from pathlib import Path

# Tokens de marca (Tico renovado.md §2.1) + subtitulo replicado de pipeline/draw.py (CAMBIOS.md #3)
PAPEL, TINTA = "#FFF8F1", "#161616"
ROJO, AZUL, VERDE, AMAR, GRIS = "#E23A45", "#2F6BFF", "#39B57A", "#F4B942", "#8A8A8A"
BOX_BG, ACCENT, TXT_DIM, KW_TEXT = "#172A42", "#4A90D9", "#7A8699", "#ECF0F5"
SW = 12
LB, RB = "{", "}"          # llaves literales: los attr:{} de GSAP escapan mal en f-strings
VW, VH = 1080, 1920
SUB_TOP, SUB_SIZE, SUB_MAXW = 182, 45, 900   # el karaoke vive arriba, como en la serie entregada
ALTO_HUD = SUB_TOP + 2 * 60 + 24             # 2 lineas reservadas: el dibujo no entra aca
CHIP_TOP = 1246                              # la franja amarilla "esto no es consejo medico"
PALABRAS_POR_LINEA = 6
CARACTERES_POR_GRUPO = 30                    # una sola linea por grupo: se corta por ancho, no por conteo
MAX_TEXTO_W = 640                            # ancho maximo de una pieza de texto en el mundo
GAP_V, ASPECTO_MAX = 100, 1.10               # apilado vertical de los grupos horizontales
SEP_BLOQUE = 240                             # aire entre el contenido de un beat y el del siguiente
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


def _norm_pal(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def reparte_palabras(beats, words):
    """Asigna cada palabra timada a su beat por TEXTO, no por tiempo.

    El hueco de silencio entre beats se come la primera palabra del siguiente: en el master del
    27-oct el grupo de un beat mostraba la cola del anterior ("de una semana. Dormir, bajar la").
    Alinear por texto es inmune al hueco y a un `t_real` que falte.

    El alcance de esa regla no alcanzaba para los signos que NO se pronuncian: la raya del guion
    ("—") consumia una palabra del TTS y a partir de ahi cada beat arrancaba un token corrido. En el
    master del 28-oct se leia "que no obedece La buena casi" y "cafeina y pausas de Y no de magnesio".
    Ahora los tokens sin letras se saltean y, si el TTS no devolvio uno, se interpola su tiempo en
    vez de robarle la palabra al beat siguiente.
    """
    out, k = [], 0
    for b in beats:
        sel = []
        for tok in b["linea"].split():
            nt = _norm_pal(tok)
            if not nt:                       # "—", "·": se ven en pantalla, no se dicen
                continue
            j, tope = k, min(len(words), k + 4)
            while j < tope and _norm_pal(words[j]["word"]) != nt:
                j += 1
            if j < tope:
                sel.append(words[j])
                k = j + 1
                continue
            previo = sel[-1] if sel else (out[-1][-1] if out and out[-1] else None)
            inicio = (previo["start"] + previo.get("dur", 0.0)) if previo else 0.0
            sel.append({"word": tok, "start": round(inicio, 3), "dur": 0.0, "sintetica": True})
        out.append(sel)
    return out


class Comp:
    def __init__(self, script, stamps):
        self.sc, self.st = script, stamps
        self.svg, self.tweens = [], []
        self.mundo = script["mundo"]
        self.beats = script["beats"]
        self.palabras = reparte_palabras(self.beats, stamps.get("words", []))
        self.arrivals = [float(b.get("t_real") or b["t"]) for b in self.beats]
        # Sin `t_real` (corrida local, o voz recalculada) la llegada la manda la primera palabra:
        # los tiempos del guion son una estimacion y dejan los subtitulos fuera de fase.
        for i, pal in enumerate(self.palabras):
            if not self.beats[i].get("t_real") and pal:
                self.arrivals[i] = round(max(0.0, pal[0]["start"] - 0.05), 2)
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
        self._prepara_piezas()
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
        self._baja_bajo_el_hud()     # el subtitulo manda: el contenido primario arranca debajo
        self._deja_sitio_al_chip()   # el aviso medico ocupa la franja baja
        self._acerca_anotaciones()   # ANTES del corrimiento: compara en las mismas unidades del shot-list
        marcos = [(st["x"] - VW / 2 / st["scale"], st["y"] - VH / 2 / st["scale"],
                   st["x"] + VW / 2 / st["scale"], st["y"] + VH / 2 / st["scale"]) for st in self.stations]
        x0, y0, x1, y1 = unir(marcos + [(0, 0, self.mundo["ancho"], self.mundo["alto"])])
        self.dx, self.dy = round(-min(0, x0), 1), round(-min(0, y0), 1)
        self.W, self.H = round(x1 + self.dx), round(y1 + self.dy)
        for st in self.stations:
            st["x"] = round(st["x"] + self.dx, 1)
            st["y"] = round(st["y"] + self.dy, 1)

    # ---------------------------------------------------------------- recomposicion (v2)
    def _prepara_piezas(self):
        """Recompone el mundo antes de derivar camaras.

        Medido en el master del 27-oct: los beats con piezas dispersas en horizontal daban cajas de
        842x220 px (78 % de ancho, 11 % de alto) sobre papel vacio. La escala la fija el ancho, asi
        que un grupo ancho y bajo se ve chico por construccion. Dos arreglos deterministas:
        el texto largo se parte en lineas y los grupos horizontales se apilan en columna.
        """
        for _z, pz in self.piezas:
            if pz["tipo"] == "texto":
                self._parte_texto(pz)
            elif pz["tipo"] == "linea_tiempo":
                pz["w"] = min(float(pz.get("w", 900)), MAX_TEXTO_W)
            elif pz["tipo"] == "ficha" and not str(pz.get("nota", "")).strip():
                # una ficha sin nota es una sola palabra: media tarjeta vacia se lee como error
                pz["h"] = min(float(pz.get("h", 190)), 150)
        self._ancla_banderas()
        self._apila()
        self._separa_bloques()

    def _ancla_banderas(self):
        """Una bandera marcada `ancla: senal` apunta a la salida del cerebro de su circuito.

        La bandera SEÑAL ELECTRICA venia con coordenadas fijas del 27-oct; al normalizar el circuito
        el punto rojo quedo sobre el rotulo "sistema nervioso" y el hilo lo cruzaba (s14). El ancla
        se calcula sobre el nodo azul del medio, que es donde nacen las senales.
        """
        for i in range(len(self.beats)):
            circ = next((pz for (_z, pz) in self.piezas
                         if int(pz.get("aparece", 0)) == i and pz["tipo"] == "circuito"), None)
            if circ is None:
                continue
            ce, _mu = anclas_circuito(circ)
            for (_z, pz) in self.piezas:
                if (int(pz.get("aparece", 0)) == i and pz["tipo"] == "bandera"
                        and pz.get("ancla") == "senal"):
                    pz["p"] = [round(circ["p"][0] + ce[0] + 140, 1),
                               round(circ["p"][1] + ce[1], 1)]

    @staticmethod
    def _parte_texto(pz):
        txt = " ".join(str(pz.get("texto", "")).split())
        size = float(pz.get("size", 64))
        limite = max(6, int(MAX_TEXTO_W / (0.52 * size)))
        if len(txt) <= limite:
            pz["lineas"] = [txt]
            return
        lineas, cur = [], ""
        for w in txt.split():
            cand = (cur + " " + w).strip()
            if len(cand) <= limite or not cur:
                cur = cand
            else:
                lineas.append(cur)
                cur = w
        if cur:
            lineas.append(cur)
        pz["lineas"] = lineas

    def _apila(self):
        """Un grupo ancho y bajo se convierte en columna, y sus etiquetas viajan con el.

        Solo mueve piezas del MISMO beat. La version anterior empujaba el grupo hasta despejar
        cualquier pieza del mundo, incluida la de beats posteriores: la columna de fichas terminaba
        3.000 unidades mas abajo y el mundo crecia hasta 11.687 px (S001, 27-oct).
        """
        for i in range(len(self.beats)):
            mios = [pz for (_z, pz) in self.piezas if int(pz.get("aparece", 0)) == i]
            prim = [pz for pz in mios
                    if pz["tipo"] not in ANOTACIONES and pz["tipo"] not in SANGRAN]
            if len(prim) < 2:
                continue
            cj = [caja(pz) for pz in prim]
            u = unir(cj)
            if (u[2] - u[0]) <= ASPECTO_MAX * max(1.0, u[3] - u[1]):
                continue
            orden = sorted(range(len(prim)), key=lambda k: (cj[k][1], prim[k]["p"][0]))
            alturas = [cj[k][3] - cj[k][1] for k in orden]
            total = sum(alturas) + GAP_V * (len(orden) - 1)
            cx = (u[0] + u[2]) / 2
            y = (u[1] + u[3]) / 2 - total / 2
            for k, hh in zip(orden, alturas):
                pz = prim[k]
                pz["p"] = [round(cx, 1), round(y + hh / 2, 1)]
                y += hh + GAP_V
            # una bandera del mismo beat se corre con el grupo para no quedar apuntando al papel
            corrimiento = cx - (u[0] + u[2]) / 2
            for pz in mios:
                if pz["tipo"] in ANOTACIONES:
                    pz["p"] = [round(pz["p"][0] + corrimiento, 1), pz["p"][1]]

    def _separa_bloques(self):
        """Cada beat ocupa su propia banda vertical: el contenido de uno no pisa el del siguiente.

        Los beats sin contenido primario (un pulso, dos etiquetas) viajan con el bloque anterior,
        porque la camara tampoco se mueve en ellos.
        """
        bloques = []
        for i in range(len(self.beats)):
            ps = [pz for (_z, pz) in self.piezas if int(pz.get("aparece", 0)) == i]
            prim = [pz for pz in ps
                    if pz["tipo"] not in ANOTACIONES and pz["tipo"] not in SANGRAN]
            if prim:
                bloques.append({"ps": ps, "caja": unir([caja(pz) for pz in prim])})
            elif bloques:
                bloques[-1]["ps"].extend(ps)
        fondo = None
        for b in bloques:
            x0, y0, x1, y1 = b["caja"]
            if fondo is not None and y0 < fondo + SEP_BLOQUE:
                d = fondo + SEP_BLOQUE - y0
                for pz in b["ps"]:
                    pz["p"] = [pz["p"][0], round(pz["p"][1] + d, 1)]
                y0, y1 = y0 + d, y1 + d
            b["caja"] = (x0, y0, x1, y1)
            fondo = y1 if fondo is None else max(fondo, y1)

    def _baja_bajo_el_hud(self):
        """La franja del karaoke es del subtitulo: el contenido primario empieza por debajo."""
        for i, st in enumerate(self.stations):
            cajas = [caja(pz) for (_z, pz) in self.piezas
                     if int(pz.get("aparece", 0)) == i
                     and pz["tipo"] not in ANOTACIONES and pz["tipo"] not in SANGRAN]
            if not cajas:
                continue
            s = st["scale"]
            arriba = VH / 2 + s * (unir(cajas)[1] - st["y"])
            if arriba < ALTO_HUD + 24:
                st["y"] = round(st["y"] - (ALTO_HUD + 24 - arriba) / s, 1)

    def _deja_sitio_al_chip(self):
        """Cuando entra el aviso medico, el contenido se encoge y se centra por encima de el.

        En el master del 27-oct el aviso caia sobre la tercera ficha ("pausas") y la partia en dos.
        La camara se ajusta ANTES de colocar etiquetas, para que la bandera se ubique en el cuadro
        que realmente se va a ver.
        """
        primero = next((i for i, b in enumerate(self.beats) if b.get("chip")), None)
        if primero is None:
            return
        arriba, abajo = ALTO_HUD + 24, CHIP_TOP - 40
        bloque = None
        for i in range(len(self.beats)):
            cajas = [caja(pz) for (_z, pz) in self.piezas
                     if int(pz.get("aparece", 0)) == i and pz["tipo"] not in ANOTACIONES
                     and pz["tipo"] not in SANGRAN]
            if cajas:
                bloque = unir(cajas)
            if i < primero or bloque is None:
                continue
            st, alto = self.stations[i], bloque[3] - bloque[1]
            st["scale"] = round(max(MIN_S, min(st["scale"], (abajo - arriba) / max(1.0, alto))), 3)
            centro = (arriba + abajo) / 2
            st["y"] = round((bloque[1] + bloque[3]) / 2 + (VH / 2 - centro) / st["scale"], 1)

    def _acerca_anotaciones(self):
        """Una etiqueta que no cabe SE ACERCA a la estacion; no achica el plano de su beat.

        El prototipo y la primera corrida de S001 perdian hasta un 28 % de zoom porque una etiqueta
        de 10 caracteres colgaba del borde. La etiqueta vive en el mundo, asi que su tamano depende
        de la escala: la unica salida honesta es moverla, no alejar la camara.
        """
        for i, st in enumerate(self.stations):
            s = st["scale"]
            fx0 = st["x"] - (VW / 2 - MARGEN_F) / s
            fy0 = st["y"] - (VH / 2 - ALTO_HUD - 12) / s   # la franja del karaoke no se invade
            fx1, fy1 = st["x"] + (VW / 2 - MARGEN_F) / s, st["y"] + (VH / 2 - MARGEN_F) / s
            for (_z, pz) in self.piezas:
                if int(pz.get("aparece", 0)) != i or pz["tipo"] not in ANOTACIONES:
                    continue
                if pz["tipo"] == "bandera":
                    self._ubica_bandera(pz, fx0, fy0, fx1, fy1)
                    continue
                for _ in range(6):
                    b = caja(pz)
                    if b[0] >= fx0 and b[2] <= fx1 and b[1] >= fy0 and b[3] <= fy1:
                        break
                    dx, dy = pz.get("hacia", [0, -190])
                    vx = pz["p"][0] + dx - st["x"]        # vector centro de estacion -> etiqueta
                    vy = pz["p"][1] + dy - st["y"]
                    pz["hacia"] = [round(dx - 0.3 * vx, 1), round(dy - 0.3 * vy, 1)]

    @staticmethod
    def _rect_bandera(pz):
        dx, dy = pz.get("hacia", [0, -190])
        fw = 34 + 34 * len(str(pz.get("texto", "")))
        return (pz["p"][0] + dx - fw / 2, pz["p"][1] + dy - 50,
                pz["p"][0] + dx + fw / 2, pz["p"][1] + dy + 50)

    def _ubica_bandera(self, pz, fx0, fy0, fx1, fy1):
        """Mueve la banderita lo justo para que entre, sin dejarla encima de su propio ancla.

        El tiron anterior corria la etiqueta hacia el centro de la estacion en los dos ejes: en el
        beat 9 (mano) la bandera NERVIOS bajaba hasta tapar su punto rojo y el hilo desaparecia.
        Si al encajarla queda sobre el ancla, se prueba la orientacion espejada.
        """
        base = list(pz.get("hacia", [0, -190]))
        ax, ay = pz["p"]
        for hx, hy in [(base[0], base[1]), (-base[0], base[1]),
                       (base[0], -base[1]), (-base[0], -base[1])]:
            pz["hacia"] = [hx, hy]
            for _ in range(3):
                x0, y0, x1, y1 = self._rect_bandera(pz)
                sx = (fx0 - x0) if x0 < fx0 else ((fx1 - x1) if x1 > fx1 else 0.0)
                sy = (fy0 - y0) if y0 < fy0 else ((fy1 - y1) if y1 > fy1 else 0.0)
                if abs(sx) < 0.5 and abs(sy) < 0.5:
                    break
                pz["hacia"] = [round(pz["hacia"][0] + sx, 1), round(pz["hacia"][1] + sy, 1)]
            x0, y0, x1, y1 = self._rect_bandera(pz)
            tapa = x0 - 8 <= ax <= x1 + 8 and y0 - 8 <= ay <= y1 + 8
            if (x0 >= fx0 - 0.6 and x1 <= fx1 + 0.6 and y0 >= fy0 - 0.6 and y1 <= fy1 + 0.6
                    and not tapa):
                return
        pz["hacia"] = base

    def salida(self, i):
        """Instante en que el contenido del beat i se retira, camino del siguiente beat dibujado.

        La camara no corta, pero el mundo no tiene por que arrastrar todo: medido en S001, la linea
        de tiempo del beat 6 seguia asomando por la franja del karaoke tres beats despues y el
        monitor del beat 5 se colaba en la esquina del beat 9. Cada bloque se desvanece durante el
        viaje de camara hacia el proximo bloque, no de golpe.
        """
        for j in range(i + 1, len(self.beats)):
            if any(int(p.get("aparece", 0)) == j and p["tipo"] not in ANOTACIONES
                   and p["tipo"] not in SANGRAN for (_z, p) in self.piezas):
                return max(0.0, self.arrivals[j] - viaje_de(self, j) - 0.10)
        return None

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
        # El foco es la promesa que el QC mide: si nace detras del karaoke o debajo del chip, el
        # pixel nunca la va a cumplir aunque la camara este perfecta. Falla el build, no el render.
        chip_t = min((self.arrivals[i] for i, b in enumerate(self.beats) if b.get("chip")),
                     default=None)
        for i, f in enumerate(focos):
            if not f:
                continue
            if f[1] < ALTO_HUD + 12:
                raise RuntimeError(f"beat {i}: el foco arranca en y={f[1]} y el karaoke ocupa "
                                   f"hasta {ALTO_HUD}; subir la estacion (_baja_bajo_el_hud)")
            if chip_t is not None and self.arrivals[i] >= chip_t and f[3] > CHIP_TOP - 18:
                raise RuntimeError(f"beat {i}: el foco baja a y={f[3]} y tapa el chip desde "
                                   f"{CHIP_TOP}; encajarlo con _deja_sitio_al_chip")
        return focos
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
    caida = bool(sp.get("caida"))
    anillo = (f'<ellipse rx="{n(rx * 1.16)}" ry="{n(ry * 1.22)}" fill="none" stroke="{col}"'
              f' stroke-width="{n(SW * 1.4)}" stroke-linecap="round" stroke-dasharray="{n(40 * k)} {n(26 * k)}"/>')
    iris = (f'<circle r="{n(88 * k)}" fill="{AZUL}" opacity="0.16"/>'
            f'<circle r="{n(88 * k)}" fill="none" stroke="{TINTA}" stroke-width="{n(SW * 0.7)}"/>'
            f'<circle r="{n(34 * k)}" fill="{TINTA}"/>')
    if caida:
        # Parpado que baja: la pieza recortada por la esclerotica evita que el bloque asome fuera
        # del ojo mientras desciende; el borde inferior curvado es el unico trazo que se ve.
        tapa = (f'<path id="{pid}-pt" d="M {n(-rx * 1.08)} {n(-ry * 1.45)} L {n(rx * 1.08)} {n(-ry * 1.45)}'
                f' L {n(rx * 1.08)} 0 Q 0 {n(-ry * 0.18)} {n(-rx * 1.08)} 0 Z" fill="#FFFFFF"'
                f' stroke="{TINTA}" stroke-width="{SW}" stroke-linejoin="round"/>')
        partes = [
            f'<clipPath id="{pid}-clip"><ellipse rx="{n(rx)}" ry="{n(ry)}"/></clipPath>',
            f'<ellipse rx="{n(rx)}" ry="{n(ry)}" fill="#FFFFFF"/>',
            f'<g clip-path="url(#{pid}-clip)">{iris}{tapa}</g>',
            f'<ellipse rx="{n(rx)}" ry="{n(ry)}" fill="none" stroke="{TINTA}" stroke-width="{SW}"/>',
            anillo,
        ]
    else:
        partes = [
            f'<ellipse rx="{n(rx)}" ry="{n(ry)}" fill="#FFFFFF" stroke="{TINTA}" stroke-width="{SW}"/>',
            iris,
            anillo,
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
    if caida:
        # El párpado baja con la palabra "cierra", no durante el viaje de cámara: la pieza se
        # dibuja antes de que llegue el beat y el cierre quedaba dos segundos adelantado.
        tb = c.arrivals[min(int(sp.get("aparece", 0)), len(c.arrivals) - 1)]
        c.js(f'tl.fromTo({q("#" + pid + "-pt")}, {{y:{n(-ry * 1.5)}}},'
             f' {{y:0,duration:1.5,ease:"power2.inOut"}}, {n(tb + 1.2)});')
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
    cerebro, musculo = anclas_circuito(sp)
    ns = int(sp.get("senales", 3))
    partes = [
        f'<path d="M {n(cerebro[0] - 130)} {n(cerebro[1])} q 40 -120 130 -90 q 90 -30 120 60'
        f' q 60 60 -20 120 q -60 80 -140 40 q -110 20 -90 -130 Z" fill="#FFFFFF" stroke="{TINTA}"'
        f' stroke-width="{SW}" stroke-linejoin="round"/>',
        c.txt(cerebro[0], cerebro[1] - 205, "sistema nervioso", 40, 600, GRIS),
        f'<ellipse cx="{n(musculo[0])}" cy="{n(musculo[1])}" rx="150" ry="96" fill="{ROJO}"'
        f' fill-opacity="0.2" stroke="{ROJO}" stroke-width="{SW}"/>',
        # el rotulo va DEBAJO del musculo: arriba quedaba debajo de la bandera SEÑAL ELECTRICA,
        # que le pasaba el hilo por encima del texto (medido en s14)
        c.txt(musculo[0], musculo[1] + 170, "orbicular", 40, 600, GRIS),
    ]
    # cables con tangente horizontal en los dos extremos: con el control "hacia arriba" del 27-oct
    # los tres trazos se juntaban en un latigo grueso y el nodo viajaba en linea recta, fuera del cable
    x0b, x1m = cerebro[0] + 140, musculo[0] - 160
    ancho = x1m - x0b
    # El desplazamiento entre cables va PERPENDICULAR a la diagonal cerebro->musculo. Con un offset
    # en (x, y) fijo los tres se acercaban en el medio y se cruzaban en el musculo (medido en s13:
    # una sola cuerda trenzada). La perpendicular los mantiene equidistantes de punta a punta.
    vx, vy = x1m - x0b, musculo[1] - cerebro[1]
    largo = math.hypot(vx, vy) or 1.0
    px, py = -vy / largo, vx / largo
    cables = []
    for i in range(ns):
        off = 34.0 * (i - (ns - 1) / 2.0)
        ox, oy = px * off, py * off
        y0, y1 = cerebro[1] + oy, musculo[1] + oy
        c1x, c2x = x0b + 0.42 * ancho + ox, x0b + 0.58 * ancho + ox
        cables.append((x0b + ox, y0, c1x, c2x, x1m + ox, y1))
        partes.append(
            f'<path id="{pid}-f{i}" d="M {n(cables[-1][0])} {n(y0)} C {n(c1x)} {n(y0)} {n(c2x)} {n(y1)}'
            f' {n(cables[-1][4])} {n(y1)}" fill="none" stroke="{AZUL}" stroke-width="{n(SW * 0.8)}"'
            f' stroke-linecap="round" data-draw="1" opacity="0.85"/>')
        partes.append(f'<circle id="{pid}-s{i}" cx="{n(cables[-1][0])}" cy="{n(y0)}" r="17"'
                      f' fill="{AZUL}" opacity="0"/>')
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    c.entra(pid, t0, dy=18, escala=1.0)
    for i in range(ns):
        x0, y0, c1x, c2x, x1, y1 = cables[i]
        c.trazo(f"{pid}-f{i}", t0 + 0.25 + i * 0.12, 0.8)
        sel = q("#" + pid + f"-s{i}")
        rep = max(1, int((t1 - t0 - 1.4) / 1.9))
        # El nodo sigue la curva muestreando la cubica: con cx/cy lineal el punto viajaba al costado
        # del cable (se veia en s13, el azul flotando sobre el papel).
        pasos = []
        for k in range(1, 13):
            u = k / 12.0
            inv = 1 - u
            bx = (inv ** 3 * x0 + 3 * inv ** 2 * u * c1x + 3 * inv * u ** 2 * c2x + u ** 3 * x1)
            by = (inv ** 3 * y0 + 3 * inv ** 2 * u * y0 + 3 * inv * u ** 2 * y1 + u ** 3 * y1)
            pasos.append(f'{{attr:{{cx:{n(bx)},cy:{n(by)}}},ease:"none"}}')
        c.js(f'tl.to({sel}, {{opacity:1,duration:0.25}}, {n(t0 + 1.0 + i * 0.06)});')
        c.js(f'tl.to({sel}, {{keyframes:[{",".join(pasos)}], duration:1.1, repeat:{rep}}},'
             f' {n(t0 + 1.1 + i * 0.3)});')
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
    tit = str(sp.get("titulo", ""))
    nota = str(sp.get("nota", "")).strip()

    def cabe(txt, size, maxw, minimo):
        ancho = len(txt) * size * 0.56
        return max(minimo, min(size, size * maxw / ancho)) if ancho > maxw else size

    # "menos cafeina" a 52 px mide mas que la tarjeta y la insignia le tapaba la ultima letra.
    st = round(cabe(tit, 52, w - 110, 30))
    sn = round(cabe(nota, 38, w - 60, 24)) if nota else 38
    ty, ny = (0, 0) if not nota else (-h * 0.14, h * 0.19)
    partes = [
        f'<rect x="{n(-w / 2 + 10)}" y="{n(-h / 2 + 14)}" width="{n(w)}" height="{n(h)}" rx="16"'
        f' fill="{TINTA}" opacity="0.1"/>',
        f'<rect x="{n(-w / 2)}" y="{n(-h / 2)}" width="{n(w)}" height="{n(h)}" rx="16" fill="#FFFFFF"'
        f' stroke="{TINTA}" stroke-width="{SW}"/>',
        c.txt(0, ty, tit, st, 700, TINTA),
    ]
    if nota:
        partes.append(c.txt(0, ny, nota, sn, 500, GRIS))
    if badge:
        bx, by, r = w / 2 - 10, -h / 2 + 10, 36
        mark = (f'<path d="M {n(bx - 20)} {n(by)} l 14 17 l 24 -28" fill="none" stroke="#FFFFFF"'
                f' stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>') if badge == "check" else (
            f'<path d="M {n(bx - 17)} {n(by - 17)} L {n(bx + 17)} {n(by + 17)} M {n(bx + 17)}'
            f' {n(by - 17)} L {n(bx - 17)} {n(by + 17)}" fill="none" stroke="#FFFFFF"'
            f' stroke-width="10" stroke-linecap="round"/>')
        partes.append(f'<circle id="{pid}-bg" cx="{n(bx)}" cy="{n(by)}" r="{r}" fill="{col}" opacity="0"/>'
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
    size = sp.get("size", 64)
    lineas = sp.get("lineas") or [sp.get("texto", "")]
    alto = size * 1.2
    y0 = -((len(lineas) - 1) / 2) * alto
    inner = "".join(c.txt(0, y0 + i * alto, ln, size, sp.get("peso", 800), sp.get("fill", TINTA))
                    for i, ln in enumerate(lineas))
    c.g(pid, sp["p"][0], sp["p"][1], inner)
    c.entra(pid, t0, dy=22, d=0.5, escala=1.0)


def p_anillo(c, pid, sp, t0, t1):
    r, col, total = float(sp.get("r", 260)), sp.get("color", AZUL), int(sp.get("n", 3))
    partes = [f'<circle id="{pid}-a{i}" r="{n(r * (1 + 0.42 * i))}" fill="none" stroke="{col}"'
              f' stroke-width="{n(SW * 0.7)}" opacity="0"/>' for i in range(total)]
    c.g(pid, sp["p"][0], sp["p"][1], "".join(partes))
    # sin este set el grupo padre se quedaba en opacity 0 y las ondas latian invisibles (beat 8, S001)
    c.js(f'tl.set({q("#" + pid)}, {{opacity:1}}, {n(t0)});')
    for i in range(total):
        c.js(f'tl.fromTo({q("#" + pid + "-a" + str(i))}, {{opacity:0.7,scale:0.9}},'
             f' {{opacity:0,scale:1.25,duration:1.2,ease:"power1.out",repeat:7}},'
             f' {n(t0 + 0.5 + i * 0.25)});')


def p_mano(c, pid, sp, t0, t1):
    # Palma con cuatro dedos y pulgar. La version del 27-oct era una manopla de cuatro bultos sin
    # pulgar y con el canto derecho inflado: se leia como una garra. Los dedos van con punta
    # redondeada y valle a la altura de los nudillos, y el pulgar sale del canto izquierdo.
    partes = [
        f'<path id="{pid}-m" d="M -205 214'
        f' C -244 208 -258 178 -258 138 C -258 96 -262 56 -256 18'
        f' C -320 -22 -338 -102 -308 -142 C -288 -168 -250 -162 -228 -134'
        f' C -214 -116 -198 -112 -186 -114'
        f' C -192 -196 -194 -292 -174 -318 C -164 -333 -140 -333 -130 -318'
        f' C -118 -300 -124 -196 -128 -114'
        f' C -120 -110 -112 -110 -104 -110'
        f' C -108 -204 -106 -300 -88 -326 C -78 -341 -52 -341 -42 -326'
        f' C -30 -308 -36 -204 -40 -110'
        f' C -32 -106 -24 -106 -16 -106'
        f' C -18 -202 -14 -292 4 -316 C 14 -332 40 -332 50 -316'
        f' C 64 -296 58 -196 54 -106'
        f' C 64 -102 72 -102 80 -102'
        f' C 80 -184 86 -252 106 -274 C 120 -290 146 -286 152 -268'
        f' C 160 -242 154 -158 150 -94'
        f' C 198 -66 232 -8 222 72 C 210 160 128 212 18 216 L -205 214 Z"'
        f' fill="#FFFFFF" stroke="{TINTA}" stroke-width="{SW}" stroke-linejoin="round"'
        f' data-draw="1"/>']
    # Las arrugas viven SOLO en la palma: arrancando en y=-150 cruzaban los valles de los dedos y
    # parecian cicatrices sobre el dorso (visto en la previa del 28-oct).
    for i in range(5 if sp.get("arrugas", True) else 0):
        y = -40 + i * 38
        partes.append(f'<path id="{pid}-ar{i}" d="M {n(-150 + i * 6)} {n(y)} q 40 -18 90 0 q 44 16 88 -2"'
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
def anclas_circuito(pz):
    """Cerebro y musculo en diagonal, con la separacion que pide un cuadro 9:16.

    El guionista declara hacia donde va cada parte; el generador normaliza la separacion. Con el
    par casi horizontal (560 a 35 grados) el diagrama medía 766x652: al encajarlo por ancho quedaba
    en 30 % del alto y sobraba papel arriba y abajo (s14). Con 740 a ~53 grados el bloque mide
    ~755x1.060, entra casi justo en el 78 % de ancho y el 62 % de alto, y el par se lee de arriba
    abajo como un circuito.
    """
    ce = [float(v) for v in pz.get("cerebro", [-370, -300])]
    mu = [float(v) for v in pz.get("musculo", [370, 300])]
    dx, dy = mu[0] - ce[0], mu[1] - ce[1]
    d = math.hypot(dx, dy) or 1.0
    objetivo = 740.0
    if d <= objetivo:
        return ce, mu
    if abs(dy) > 1.25 * abs(dx):
        ang = 0.92                                   # ~53 grados: diagonal que usa el alto del cuadro
        dx, dy = objetivo * math.cos(ang), objetivo * math.sin(ang) * (1 if dy >= 0 else -1)
    else:
        dx, dy = dx * objetivo / d, dy * objetivo / d
    cx, cy = (ce[0] + mu[0]) / 2, (ce[1] + mu[1]) / 2
    return [cx - dx / 2, cy - dy / 2], [cx + dx / 2, cy + dy / 2]


def caja(pz):
    """Caja (x0,y0,x1,y1) en unidades del mundo que ocupa una pieza. Sirve para derivar la camara."""
    x, y = float(pz["p"][0]), float(pz["p"][1])
    k = float(pz.get("escala", 1.0))
    tipo = pz["tipo"]
    if tipo == "ojo":
        w, h = 720 * k, 480 * k
        if pz.get("caida"):                # el parpado arranca por encima de la esclerotica
            h = 560 * k
    elif tipo == "silueta":
        w, h = 540 * k, 1010 * k
    elif tipo == "circuito":
        ce, mu = anclas_circuito(pz)
        # incluye los rotulos: "sistema nervioso" arriba del cerebro y "orbicular" debajo del musculo
        return (x + min(ce[0] - 140, mu[0] - 170), y + min(ce[1] - 240, mu[1] - 200),
                x + max(ce[0] + 140, mu[0] + 170), y + max(ce[1] + 130, mu[1] + 210))
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
        size = float(pz.get("size", 64))
        lineas = pz.get("lineas") or [str(pz.get("texto", ""))]
        w = max(len(l) for l in lineas) * size * 0.52
        h = len(lineas) * size * 1.2
        return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    elif tipo == "anillo":
        r = float(pz.get("r", 260)) * 1.42
        w = h = 2 * r
    elif tipo == "mano":
        # la mano dibuja dentro de +/-260 x (-296..210); las ondas decorativas pueden sangrar el cuadro
        return (x - 265, y - 300, x + 265, y + 214)
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
        # La etiqueta no manda el plano: si no entra, se acerca ella (_acerca_anotaciones). Achicar
        # la camara para que entren dos banderitas convertia el ojo de 700 px en uno de 390.
        st = dict(anterior)
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
    out = []
    for i, b in enumerate(c.beats):
        t0, t1 = c.arrivals[i], (c.arrivals[i + 1] if i + 1 < len(c.arrivals) else c.T)
        ns = list(c.palabras[i]) if c.palabras and i < len(c.palabras) else []
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
        cur, lineas, ancho = [], [], 0
        for m in marks:
            cur.append(m)
            ancho += len(m[0]["word"]) + 1
            if len(cur) >= PALABRAS_POR_LINEA or ancho >= CARACTERES_POR_GRUPO:
                lineas.append(cur)
                cur, ancho = [], 0
        if cur:
            lineas.append(cur)
        for ln in lineas:
            out.append({"i": i, "words": ln, "t0": max(0.0, ln[0][0]["start"] - 0.06),
                        "t1": ln[-1][0]["start"] + ln[-1][0].get("dur", 0.3) + 0.42})
    # Una sola linea activa a la vez (regla de la serie entregada). Sin este recorte, el grupo que
    # entra se dibuja encima del que todavia no salio: en el master del 27-oct se leia
    # "pocCuandol circuitosatura" durante medio segundo en cada cambio de linea.
    for k in range(len(out) - 1):
        out[k + 1]["t0"] = max(out[k + 1]["t0"], out[k]["t0"] + 0.10)
        out[k]["t1"] = min(out[k]["t1"], out[k + 1]["t0"] - 0.02)
    # Estructura verificada en el build: dos lineas vivas a la vez fue el defecto del master del
    # 27-oct y no se ve en una captura, se ve en el video. Si el recorte no alcanza, falla aca.
    for k, g in enumerate(out):
        if g["t1"] <= g["t0"]:
            raise RuntimeError(f"grupo {k} con duracion {g['t1'] - g['t0']:.3f}s")
        for w, _kw in g["words"]:
            if not (g["t0"] - 0.12 <= w["start"] <= g["t1"]):
                raise RuntimeError(f"grupo {k}: la palabra '{w['word']}' empieza en "
                                   f"{w['start']:.2f}s, fuera de {g['t0']:.2f}-{g['t1']:.2f}")
        if k and g["t0"] <= out[k - 1]["t1"] + 0.001:
            raise RuntimeError(f"grupos {k - 1} y {k} se solapan "
                               f"({out[k - 1]['t1']:.2f}s > {g['t0']:.2f}s)")
    return out


SUB_HTML = """
<div id="subs">{GRPOS}</div>
"""

def subtitulos(c):
    """Karaoke de una linea: la caja del resaltado vive DENTRO de la palabra y detras del texto.

    Antes la caja era un div absoluto hermano de los spans y se pintaba encima: la palabra clave
    desaparecia debajo del rectangulo azul (medido en el master del 27-oct). Con un <i> en
    z-index:-1 la caja queda detras por construccion y ademas mide exactamente la palabra.
    """
    gs = grupos(c)
    html = []
    for gi, g in enumerate(gs):
        piezas = []
        for wi, (w, kw) in enumerate(g["words"]):
            caja = f'<i class="bx" id="b{gi}_{wi}"></i>' if kw else ""
            piezas.append(f'<span class="w{" k" if kw else ""}" id="w{gi}_{wi}">{caja}{esc(w["word"])}</span>')
        html.append(f'<div class="grp" id="g{gi}">{"".join(piezas)}</div>')
    for gi, g in enumerate(gs):
        c.js(f'tl.set("#g{gi}", {{opacity:1,visibility:"visible"}}, {n(g["t0"])});')
        for wi, (w, kw) in enumerate(g["words"]):
            t = n(max(0.0, w["start"]))
            c.js(f'tl.to("#w{gi}_{wi}", {{color:{q(KW_TEXT if kw else TINTA)},duration:0.09,ease:"none"}},'
                 f' {t});')
            if kw:
                c.js(f'tl.fromTo("#b{gi}_{wi}", {{opacity:0,scale:0.86}},'
                     f' {{opacity:1,scale:1,duration:0.13,ease:"power2.out"}}, {t});')
        c.js(f'tl.set("#g{gi}", {{opacity:0,visibility:"hidden"}}, {n(g["t1"])});')
    for a, b in zip(gs, gs[1:]):
        if b["t0"] < a["t1"] - 1e-6:
            raise RuntimeError("dos grupos de subtitulo se pisan: " + str((a["t0"], a["t1"], b["t0"])))
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
/* .w crea contexto de apilado (z-index:0) y .bx queda en -1: la caja pinta DETRAS del glifo. */
.w {{ display: inline-block; position: relative; z-index: 0; color: {TXT_DIM}; margin: 0 4px; }}
.bx {{ position: absolute; left: -11px; right: -11px; top: -6px; bottom: -6px; z-index: -1;
       background: {BOX_BG}; border: 3px solid {ACCENT}; border-radius: 10px; opacity: 0; }}
/* El mundo es continuo: lo del beat anterior asoma por el borde y se lee como un error. Estos dos
   velos lo desvanecen en la franja del karaoke y detras de la ficha medica. */
#velo {{ position: absolute; left: 0; top: 0; width: {VW}px; height: {ALTO_HUD + 6}px;
         background: linear-gradient({PAPEL} 0%, {PAPEL} 92%, rgba(255,248,241,0) 100%); }}
#velo2 {{ position: absolute; left: 0; top: {CHIP_TOP - 120}px; width: {VW}px; height: 300px;
          opacity: 0;
          background: linear-gradient(rgba(255,248,241,0) 0%, {PAPEL} 46%, {PAPEL} 100%); }}
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
        tsal = c.salida(i)
        if tsal is not None:
            # +0,4 s: medido en el master del 28-oct, con la salida al ras del dibujo del siguiente
            # bloque el viaje largo al CTA dejaba 0,9 s de papel casi vacio (48,0-49,2).
            c.js(f'tl.to({q("#" + pz["id"])}, {{opacity:0,duration:0.5,ease:"power1.in"}}, {n(tsal + 0.4)});')
    world = (f'<svg id="world" class="world" width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
             f' xmlns="http://www.w3.org/2000/svg">{fondo}{"".join(c.svg)}</svg>')
    camara(c)
    sub_html = subtitulos(c)
    chips = [(i, b["chip"]) for i, b in enumerate(c.beats) if b.get("chip")]
    if chips:
        c.js(f'tl.to("#chip", {{opacity:1,duration:0.3,ease:"power2.out"}},'
             f' {n(c.arrivals[chips[0][0]] + 0.4)});')
        c.js(f'tl.to("#velo2", {{opacity:1,duration:0.5,ease:"power2.out"}},'
             f' {n(c.arrivals[chips[0][0]] + 0.3)});')
    c.js(f'tl.fromTo("#bar", {{scaleX:0}}, {{scaleX:1,duration:{n(c.T - FADE_S)},ease:"none"}}, 0);')
    c.js(f'tl.to("#fade", {{opacity:1,duration:{n(FADE_S)},ease:"power1.in"}}, {n(c.T - FADE_S)});')

    js_body = "\n".join([
        "document.querySelectorAll('[data-draw]').forEach(function(el){"
        "  var L = el.getTotalLength();",
        "  el.style.strokeDasharray = L; el.style.strokeDashoffset = L; });",
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
           f'    <div id="velo"></div>{SUB_HTML.format(GRPOS=sub_html)}\n'
           f'    <div id="bar"></div><div id="velo2"></div>\n'
           f'    <div id="chip">{esc(chips[0][1]) if chips else "Esto no es consejo medico"}</div>\n'
           f'    <div id="fade"></div>\n  </div>\n</div>\n'
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>\n'
           f'<script>\n{js_body}\n</script>\n</body>\n</html>\n')
    Path(ruta_out).write_text(doc, encoding="utf-8")
    # Las franjas del HUD se declaran ACA, en la unica unidad que las conoce (px de pantalla), y el
    # QC las lee. Si el QC las hardcodea, una banda mal ubicada mide los subtitulos como si fueran
    # dibujo: cobertura inflada y escena vacia en verde.
    alto_subs = ALTO_HUD   # se reservan 2 lineas: un grupo puede solapar al anterior
    meta = {"ancho": VW, "alto": VH,
            "bandas": [[0.0, round(alto_subs / VH, 4)],
                       [round(CHIP_TOP / VH, 4), round((CHIP_TOP + 92) / VH, 4)]],
            "chip": [260, CHIP_TOP, 820, CHIP_TOP + 92],
            "chip_t": round(c.arrivals[chips[0][0]], 3) if chips else None,
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
