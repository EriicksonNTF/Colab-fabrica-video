"""Validadores de contrato: muralla 2 del cerebro (§8-bis.2) y chequeo de fuentes (§8-bis.3).

Las fuentes las verifica CODIGO, no el modelo: HTTP 200 y la frase clave presente en la pagina.
Uso: python validate.py --factset ... --script ... [--urls]
"""
import argparse
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

MAX_WORDS = 165
MIN_WORDS = 90
TIPOS = ["HOOK", "NOMBRE", "MECANISMO", "DEMO", "UTILIDAD", "CTA"]
TIERS = {"A", "B", "C", "?", "C-sin-fuente-confirmada"}
FRASES_VETADAS = ["esto puede matarte", "señal de muerte", "tienes ", "elimina ", "cura con ",
                  "tu doctor no te lo va a decir", "el 99% de los médicos", "remedio casero"]
# Terminos que un factset nunca debe insinuar como accion. Se ignoran cuando van
# en contexto de prohibicion ("sin dosis", "nunca recomendar cura").
VETADOS_NOTA = ["cura", "curar", "curacion", "dosis", "tomar", "suplementar",
                "suplemento", "complementar", "complemento", "tratamiento"]
NEGACIONES = {"sin", "no", "nunca", "jamas", "ni", "evitar", "evita", "omitir",
              "omite", "prohibido", "unicamente", "solo"}


def desaccent(s):
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")


def nota_vetada(nota):
    """Devuelve el primer termino medico-usado-accion, o None si solo esta en contexto de prohibicion."""
    texto = desaccent(norm(nota))
    for raiz in VETADOS_NOTA:
        for m in re.finditer(r"\b" + raiz + r"\w*", texto):
            tokens = [re.sub(r"^\W+|\W+$", "", t) for t in texto[:m.start()].split()]
            if any(p in NEGACIONES for p in tokens[-2:]):
                continue
            return m.group()
    return None


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def norm(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).lower()


def check_factset(fs):
    errs = []
    for k in ["slug", "tema", "fecha_investigacion", "claims", "riesgo_medico", "veredicto"]:
        if k not in fs:
            errs.append(f"factset sin campo {k}")
    if not (3 <= len(fs.get("claims", [])) <= 5):
        errs.append(f"{len(fs.get('claims', []))} claims: deben ser 3-5")
    for c in fs.get("claims", []):
        for k in ["id", "texto", "tier", "confianza", "fuente", "url"]:
            if k not in c:
                errs.append(f"claim {c.get('id', '?')} sin {k}")
        if c.get("tier") not in TIERS:
            errs.append(f"claim {c.get('id')} tier invalido {c.get('tier')}")
        if "URL_CAPTURADA" in str(c.get("url", "")) or not str(c.get("url", "")).startswith("http"):
            errs.append(f"claim {c.get('id')}: la URL no esta capturada (no puede sobrevivir al factset)")
        veto = nota_vetada(c.get("nota_para_guion", ""))
        if veto:
            errs.append(f"claim {c.get('id')}: nota_para_guion sugiere '{veto}' (prohibido, §10.3)")
    return errs


def check_piezas(sc):
    """El shot-list que el cerebro dibuja en script.json; build_comp.py lo materializa en SVG."""
    from build_comp import REGISTRO
    errs, ids = [], set()
    nb = len(sc.get("beats", []))
    for z in (sc.get("mundo") or {}).get("zonas", []):
        for pz in z.get("piezas", []):
            pid = pz.get("id", "?")
            if not pid or pid in ids:
                errs.append(f"pieza con id vacio o repetido: {pid}")
            ids.add(pid)
            if pz.get("tipo") not in REGISTRO:
                errs.append(f"pieza {pid}: tipo {pz.get('tipo')} no esta en el registro de primitivas")
                continue
            p = pz.get("p")
            if not (isinstance(p, list) and len(p) == 2 and all(isinstance(v, (int, float)) for v in p)):
                errs.append(f"pieza {pid}: p debe ser [x, y] numerico")
            ap = pz.get("aparece")
            if not isinstance(ap, int) or not 0 <= ap < nb:
                errs.append(f"pieza {pid}: aparece={ap} debe ser un indice de beat valido (0-{nb - 1})")
            if pz["tipo"] == "bandera" and not str(pz.get("texto", "")).strip():
                errs.append(f"pieza {pid}: bandera sin texto")
    if not ids:
        errs.append("el mundo no tiene piezas: no hay nada que animar")
    return errs


def check_script(sc, fs=None):
    errs = []
    zonas = {z["id"] for z in (sc.get("mundo") or {}).get("zonas", [])}
    for k in ["slug", "beats", "voz", "cuadro", "mundo"]:
        if k not in sc:
            errs.append(f"script sin campo {k}")
    if sc.get("cuadro") != [1080, 1920]:
        errs.append(f"cuadro {sc.get('cuadro')} != [1080, 1920]")
    beats = sc.get("beats", [])
    ts = [b.get("t", -1) for b in beats]
    if ts != sorted(ts):
        errs.append("los t de los beats no son crecientes")
    words = sum(len(re.findall(r"\S+", b.get("linea", ""))) for b in beats)
    if not (MIN_WORDS <= words <= MAX_WORDS):
        errs.append(f"{words} palabras: fuera de {MIN_WORDS}-{MAX_WORDS}")
    tipos = [b.get("tipo") for b in beats]
    for falta in ["HOOK", "UTILIDAD", "CTA"]:
        if falta not in tipos:
            errs.append(f"falta el beat {falta}")
    if beats and len(norm(" ".join(b["linea"] for b in beats)).split()) > MAX_WORDS:
        errs.append("el texto total excede el presupuesto al normalizar")
    for b in beats:
        for k in ["t", "tipo", "linea", "zona", "keywords", "visual"]:
            if k not in b:
                errs.append(f"beat {b.get('tipo')} @{b.get('t')} sin campo {k}")
        if b.get("zona") not in zonas:
            errs.append(f"beat {b.get('tipo')} apunta a zona inexistente {b.get('zona')}")
        if b.get("tipo") not in TIPOS:
            errs.append(f"beat con tipo desconocido {b.get('tipo')}")
        cam = b.get("cam")                     # opcional: la estacion se deriva del contenido (CAMBIOS #7)
        if cam is not None and not all(k in cam for k in ("x", "y", "scale")):
            errs.append(f"beat {b.get('tipo')} cam declarada incompleta")
        for kw in b.get("keywords", []):
            if norm(kw) not in norm(b.get("linea", "")):
                errs.append(f"keyword '{kw}' no aparece en la linea del beat {b.get('tipo')}")
        if any(f in norm(b.get("linea", "")) for f in FRASES_VETADAS):
            errs.append(f"beat {b.get('tipo')} usa una frase vetada (§5.9)")
    errs += check_piezas(sc)
    if fs and fs.get("riesgo_medico") != "bajo":
        if not any(b.get("linea_de_consulta") for b in beats):
            errs.append("riesgo_medico != bajo y ningun beat tiene linea_de_consulta")
        if not any(b.get("chip") for b in beats):
            errs.append("riesgo_medico != bajo y ningun beat tiene chip 'no es consejo medico'")
    return errs


def check_urls(fs, timeout=20):
    """Sin user-agent de bot tonto: NIH devuelve 403 al urllib por defecto."""
    errs = []
    for c in fs.get("claims", []):
        for key in ("url", "url_2"):
            u = c.get(key)
            if not u:
                continue
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = norm(r.read(400_000).decode("utf-8", "ignore"))
                    frase = c.get("frase_key_verificada", "")
                    probe_txt = norm(frase)[:60] if frase else ""
                    if frase and probe_txt and probe_txt not in body:
                        errs.append(f"claim {c['id']} ({key}): la frase clave NO esta en la pagina actual")
            except Exception as exc:  # noqa: BLE001
                errs.append(f"claim {c['id']} ({key}): {u} -> {exc}")
    return errs


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--factset", default=None)
    ap.add_argument("--urls", action="store_true", help="re-verificar URL + frase clave contra la web")
    a = ap.parse_args()
    sc = load(a.script)
    fs = load(a.factset) if a.factset else None
    errs = check_script(sc, fs)
    if fs:
        errs += check_factset(fs)
    if fs and a.urls:
        errs += check_urls(fs)
    print(json.dumps({"ok": not errs, "fallos": errs}, ensure_ascii=False, indent=2))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
