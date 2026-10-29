"""Arma `notebook_cerebro.ipynb` (Colab/Kaggle) desde las celdas de este archivo.

Unica fuente editable del notebook: se edita aqui y se regenera
(`python agente/make_notebook.py`). El .ipynb generado es el que se sube a Colab.
"""
import json
import pathlib

MD = "markdown"
CODE = "code"

CELDA_PORTADA = """# Cerebro de la fábrica — sesión dominguera (Colab T4 / Kaggle T4×2)

Cuatro celdas + una extra. **~35 min de máquina y 10 min de tu revisión.** Esta notebook solo escribe
`data/` y hace `git push`: el MP4 lo genera GitHub Actions con el brazo determinista (§8-bis y §9 del
doc maestro). Tu PC no interviene en ninguna de las dos partes.

| Celda | Qué hace | Tiempo |
|---|---|---|
| 1 | baja el repo, levanta Ollama, descarga el cerebro | ~5 min |
| 2 | lote creativo: INVESTIGADOR → GUIONISTA → ANIMADOR por idea | 15-20 min |
| 3 | auto-validación (contratos + URL + frases vetadas + variedad §6.9) con 2 reintentos | 2-3 min |
| 4 | `git push` de `data/` y de `data/cola.txt` | ~1 min |
| 5 | extra: A/B de voces edge-tts con la RECETA (Manual del dueño §11) | 2 min |

**Setup único (Manual §2), antes de la primera corrida:**
1. `REPO_URL` de la celda 1 **ya viene puesto** a `EriicksonNTF/Colab-fabrica-video`. No hace falta
   tocarla salvo que cambies de repo.
2. Colab → la llave 🔑 de la barra lateral → *Snippet secrets* → agregá `GH_TOKEN` con un
   **fine-grained personal token** de GitHub que solo tenga *Contents: Read and write* en ese repo.
   El token viaja cifrado, no se imprime y nunca se commitea (§10.2: es parte de tu login GitHub).
3. Menú *Entorno de ejecución → Cambiar tipo de entorno → GPU T4*.

Si Colab responde "no hay GPU disponible hoy": abrí el mismo notebook en Kaggle (T4×2), que ya está
aprobado como excepción, y corrés las mismas celdas.
"""

CELDA_1 = '''# ============================================================================
# CELDA 1 · ENTORNO: repo + Ollama + cerebro. Una vez por sesion (~5 min).
# PARCHE 27-oct: el instalador oficial (curl|sh) corta con exit 1 en Colab.
# Causa medida: ahora baja "ollama-linux-amd64.tar.zst" (1,5 GB) y su fallback
# ".tgz" ya no existe (404). Si el runtime no tiene zstd, el script aborta en
# vez de seguir. Se instala a mano lo mismo que instala el script, sin useradd
# ni unidad de systemd (Colab no arranca con systemd).
# Ademas se quito "-U numpy": subia numpy a 2.5.x y rompia numba 0.61.2.
# El cerebro no usa numpy (build_comp solo importa math/json/re/pathlib).
# PARCHE 28-oct: el repo es PUBLICO, asi que el clon no necesita token; el token
# solo hace falta para el push de la celda 4. userdata.get() devuelve None cuando
# el secret no existe (no lanza excepcion), y eso mataba el assert. Ahora el
# token es opcional para clonar, se pide por getpass si falta (no se imprime ni
# se guarda) y se valida contra la API antes de gastar 25 min de GPU.
# ============================================================================
import getpass, os, pathlib, subprocess, time

REPO_URL = "https://github.com/EriicksonNTF/Colab-fabrica-video.git"   # ya apunta al repo real
RAMA     = "main"
os.environ.setdefault("CEREBRO", "qwen3.5:9b")   # tag verificado 26-oct-2026 (CAMBIOS #4)
CEREBRO = os.environ["CEREBRO"]

%pip install -q -U ollama pydantic jsonschema edge-tts

OLLAMA = "/usr/local/bin/ollama"

def _sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

if not pathlib.Path(OLLAMA).exists():
    print("instalando zstd (lo necesita el tar.zst de ollama)...")
    r = _sh("apt-get -qq update && apt-get -qq install -y zstd")
    if r.returncode != 0:
        print("apt fallo:", (r.stderr or "")[-400:])
    print("bajando ollama (~1,5 GB)...")
    r = _sh("curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst "
            "| zstd -d | tar -xf - -C /usr/local")
    if r.returncode != 0 or not pathlib.Path(OLLAMA).exists():
        raise RuntimeError("no se pudo instalar ollama.\\n" + (r.stderr or "")[-900:])
pathlib.Path(OLLAMA).chmod(0o755)
print(subprocess.run([OLLAMA, "--version"], capture_output=True, text=True).stdout.strip())

os.environ["OLLAMA_HOST"] = "http://127.0.0.1:11434"
if not subprocess.run(["pgrep", "-f", "ollama serve"], capture_output=True).stdout:
    subprocess.Popen("nohup /usr/local/bin/ollama serve >/tmp/ollama.log 2>&1 &", shell=True)
for s in range(90):                       # esperar respuesta real, no un sleep a ojo
    if _sh("curl -fsS http://127.0.0.1:11434/api/version").returncode == 0:
        print("ollama listo a los", s, "s")
        break
    time.sleep(1)
else:
    print("ojo: el server no respondio en 90 s. Ultimas lineas de /tmp/ollama.log:")
    print(_sh("tail -20 /tmp/ollama.log").stdout)

print("bajando el cerebro (~5 GB en Q4, sin claves)...")
subprocess.run([OLLAMA, "pull", CEREBRO], check=True)

def _git(args, err):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(err + " | " + (p.stderr or "").strip()[-500:])
    return p

def _token():
    try:
        from google.colab import userdata                       # Kaggle: Secrets > Add input
        t = (userdata.get("GH_TOKEN") or "").strip()
        if t:
            return t, "Colab Secrets"
        print("Colab Secrets: el secret GH_TOKEN existe pero esta vacio.")
    except Exception as e:
        print("Colab Secrets no lo entrego:", type(e).__name__, str(e)[:200])
    t = (os.environ.get("GH_TOKEN") or "").strip()
    return (t, "variable de entorno") if t else ("", "")

TOK, origen = _token()
if not TOK:
    print("No hay GH_TOKEN. Dos formas de arreglarlo:")
    print("  fija : llave del panel izquierdo -> agregar GH_TOKEN -> activar 'Acceso del notebook'")
    print("         (fine-grained, solo Contents: Read and write sobre Colab-fabrica-video)")
    print("  ahora: pegalo abajo; no se muestra en pantalla ni queda guardado en el notebook")
    TOK = (getpass.getpass("GH_TOKEN: ") or "").strip()

if TOK:
    assert TOK.startswith(("ghp_", "github_pat_")), "eso no parece un token de GitHub"
    import json as _json, urllib.request
    req = urllib.request.Request("https://api.github.com/repos/EriicksonNTF/Colab-fabrica-video",
                                 headers={"Authorization": "Bearer " + TOK,
                                          "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            perms = _json.load(r).get("permissions", {})
    except Exception as e:
        raise RuntimeError("el token no sirvio: " + type(e).__name__ + " " + str(e)[:200])
    assert perms.get("push"), "el token llego pero no tiene escritura (Contents: Read and write)"
    print("token ok para el repo (origen:", origen + ")")
    os.environ["GH_TOKEN"] = TOK

if not pathlib.Path("fabrica").exists():
    _git(["git", "clone", "--depth", "1", "-b", RAMA, REPO_URL, "fabrica"], "no se pudo clonar el repo")
%cd fabrica
if TOK:   # la celda 4 empuja por el remoto: sin esto un clon anonimo no puede hacer push
    _git(["git", "remote", "set-url", "origin",
          REPO_URL.replace("https://", "https://oauth2:" + TOK + "@")], "no se pudo configurar el remoto")
subprocess.run(["git", "config", "user.name", "Ticomental"], check=True)
subprocess.run(["git", "config", "user.email", "ticomental@users.noreply.github.com"], check=True)
print("listo:", subprocess.run([OLLAMA, "list"], capture_output=True, text=True).stdout)
'''

CELDA_2 = '''# ============================================================================
# CELDA 2 · LOTE CREATIVO: INVESTIGADOR -> GUIONISTA -> ANIMADOR (prompts §5 del canon)
# Los prompts se leen de "Tico renovado.md" del repo: no hay copia que se desactualice.
# Muralla 1: salida enmoldeada (format = JSON-Schema). Muralla 2: validate.py en la celda 3.
# ============================================================================
import json, os, pathlib, re, subprocess, sys
from typing import Any
import ollama
from pydantic import BaseModel

sys.path.insert(0, "agente")
from build_comp import REGISTRO                 # las unicas primitivas que el render sabe dibujar
BIBLIA = pathlib.Path("Tico renovado.md").read_text(encoding="utf-8")

def seccion(inicio, fin):
    a, b = BIBLIA.index(inicio), BIBLIA.index(fin)
    return BIBLIA[a:b].strip()

P_INVESTIGADOR = seccion("### 5.2", "### 5.3")
P_GUIONISTA    = seccion("### 5.3", "### 5.4")
P_ANIMADOR     = seccion("### 5.5", "### 5.6")
C_SCRIPT       = seccion("### 4.3", "### 4.4")
R_VARIEDAD     = seccion("### 6.9", "### 6.10")
CEREBRO        = os.environ["CEREBRO"]

class Claim(BaseModel):
    id: str
    texto: str
    tier: str
    confianza: str
    fuente: str
    url: str
    frase_key_verificada: str
    nota_para_guion: str = ""

class Factset(BaseModel):
    slug: str
    tema: str
    fecha_investigacion: str
    claims: list[Claim]
    mitos_explicitos: list[str]
    prohibiciones: str
    riesgo_medico: str
    veredicto: str
    sellado_por: str

class Beat(BaseModel):
    t: float
    tipo: str
    linea: str
    zona: str
    keywords: list[str]
    visual: str
    chip: str = ""
    linea_de_consulta: str = ""

class Guion(BaseModel):
    slug: str
    factset: str
    duracion_objetivo_s: float
    voz: dict[str, Any]
    fps: int
    cuadro: list[int]
    beats: list[Beat]
    palabras_total: int
    reglas_aplicadas: list[str]
    variedad: dict[str, Any]
    versiones_alternas: dict[str, Any]

def molde(modelo):
    """JSON-Schema de Pydantic -> grammar de Ollama: sin $defs, todo campo requerido, cerrado."""
    s = modelo.model_json_schema()
    defs = s.pop("$defs", {})

    def resolver(x):
        if isinstance(x, dict):
            if "$ref" in x:
                return resolver(defs[x["$ref"].rsplit("/", 1)[-1]])
            return {k: resolver(v) for k, v in x.items() if k != "title"}
        if isinstance(x, list):
            return [resolver(i) for i in x]
        return x

    s = resolver(s)

    def cerrar(x):
        if isinstance(x, dict):
            if x.get("type") == "object":
                x["required"] = list(x.get("properties", {}))
                x["additionalProperties"] = False
            for v in x.values():
                cerrar(v)
        elif isinstance(x, list):
            for v in x:
                cerrar(v)

    cerrar(s)
    return s

def _json_txt(t):
    """El modelo puede devolver prosa o vacio. Antes eso moria con 'Expecting value: line 1 column 1
    (char 0)', que no dice nada; ahora se corta el primer objeto balanceado y, si no hay, se muestra
    que devolvio y cuanto."""
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        raise RuntimeError("el cerebro no devolvio JSON (" + str(len(t)) + " chars); arranque: "
                           + repr(t[:200]))
    return json.loads(t[i:j + 1])

def _chat(system, usuario, schema, temp):
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": usuario}]
    # num_ctx 8192: los prompts §5.x + el contrato no entran comodos en los 4096 por defecto.
    # think=False: un modelo con "thinking" gasta num_predict entero pensando y entrega content vacio,
    # que es exactamente el 'Expecting value: line 1 column 1' de la primera corrida.
    opc = {"temperature": temp, "num_predict": 6144, "num_ctx": 8192}
    try:
        return ollama.chat(model=CEREBRO, messages=msgs, format=schema, options=opc, think=False)
    except TypeError:                          # cliente ollama viejo: no conoce `think`
        return ollama.chat(model=CEREBRO, messages=msgs, format=schema, options=opc)

def contratar(system, usuario, schema, temp=0.2):
    r = _chat(system, usuario, schema, temp)
    t = (r["message"]["content"] or "").strip()
    if not t:
        print("  [reintento] el cerebro devolvio vacio; se repite con /no_think")
        r = _chat(system + " /no_think", usuario, schema, temp)
        t = (r["message"]["content"] or "").strip()
    if not t:
        raise RuntimeError("respuesta vacia del cerebro: gasto los tokens pensando y no escribio "
                           "la salida. Probá CEREBRO=qwen3.5:4b o subi num_predict.")
    return _json_txt(t)

# --- el ANIMADOR ya no escribe HTML: entrega el shot-list de piezas (data/qc/CAMBIOS.md #5) -------
P_ANIMADOR_LISTO = P_ANIMADOR + """

TRADUCCION OBLIGATORIA DE TU ROL EN ESTE PIPELINE (no es opcional, es el contrato):
- NO escribas HTML, SVG ni GSAP. `agente/build_comp.py` materializa la composicion a partir de tu
  shot-list y aplica las reglas de movimiento y de camara continua.
- Devolve EXACTAMENTE: {"mundo": {"ancho": int, "alto": int, "zonas": [{"id": str, "c": [x, y],
  "piezas": [{"id": str, "tipo": str, "p": [x, y], "aparece": int, "retraso": float, ...}]}]}}
- `tipo` sale de este registro cerrado: TIPOS. Cada pieza se dibuja en `p` (unidades del mundo,
  y crece hacia abajo) y aparece en el beat `aparece` (0 = HOOK). Atributos por tipo: ojo/silueta/
  circuito/bateria/tazas/monitor/linea_tiempo/ficha/bandera/texto/anillo/mano.
- El encuadre NO se declara: se deriva de tus cajas. Solo si el guion pide un paneo explicito
  pone `cam` en ese beat.
- `bandera.texto` CORTO (<= 16 caracteres). La etiqueta vive dentro del mundo, asi que se agranda
  con el zoom del beat: una etiqueta larga se come el diagrama (data/qc/CAMBIOS.md #13).
- Ningun beat puede tener SOLO un `anillo` como pieza nueva: el pulso es decoracion sobre una escena
  que ya existe. Si un beat no agrega nada que encuadrar, la camara se queda donde estaba.
- Mundo alto y angosto (retrato): 3200 de ancho y 8000-10000 de alto, con una zona por locacion.
- RETRATO: las cadenas (circuito cerebro->musculo, fila de fichas, linea de tiempo) van
  VERTICALES, de arriba hacia abajo. Una cadena horizontal de 1300 unidades achica el plano y
  deja dos tercios del cuadro en papel vacio (medido en S001: cov 1.2%).
- Separá zonas ~1600-2000 unidades: viajes mas largos cruzan papel vacio y el QC lo anota.
""" .replace("TIPOS", ", ".join(sorted(REGISTRO)))

def slug_de(idea, fs):
    base = re.sub(r"[^a-z0-9]+", "-", (fs["tema"] + " " + idea["id"]).lower()).strip("-")[:34]
    return f"S{int(idea['id'][1:]):03d}-{base.split('-', 1)[-1]}"

def investigar(idea, errores=""):
    sys_txt = (P_INVESTIGADOR + "\\n\\nSALIDA: el JSON del contrato §4.2. Cada claim con su URL real "
               "capturada hoy y `frase_key_verificada` = 8-12 palabras textuales de esa pagina "
               "(un script, no vos, va a comprobar que esten). Sin URL no hay claim.")
    return contratar(sys_txt, json.dumps(idea, ensure_ascii=False) + errores, molde(Factset), 0.2)

def guionista(fs, idea, errores=""):
    sys_txt = (P_GUIONISTA + "\\n\\nSALIDA: el JSON del contrato §4.3 SIN el campo `mundo` (lo escribe "
               "el ANIMADOR despues). Dos ganchos candidatos: `versiones_alternas.hook_2`. "
               "Zonas: usá los ids de zona que despues va a crear el animador: ojo/silueta/circuito/"
               "calma/teaser o los que pidas, pero coherentes con tu campo `visual`.\\n\\n"
               "AUDITORIA DE VARIEDAD OBLIGATORIA (§6.9):\\n" + R_VARIEDAD)
    return contratar(sys_txt, json.dumps({"idea": idea, "factset": fs}, ensure_ascii=False) + errores,
                     molde(Guion), 0.3)

def animador(fs, sc, errores=""):
    sys_txt = P_ANIMADOR_LISTO + "\\n\\nCONTRATO DE REFERENCIA (para que tus `visual` tengan dibujo):\\n" + C_SCRIPT
    return contratar(sys_txt, json.dumps({"beats": sc["beats"], "slug": sc["slug"]},
                                         ensure_ascii=False) + errores, "json", 0.2)

def generar(idea, errores=None):
    """Un slug completo: factset + guion + shot-list. `errores` es el feedback del reintento."""
    err = ("\\n\\nREINTENTO: tu entrega anterior fue rechazada. Corregi exactamente esto:\\n- "
           + "\\n- ".join(errores or [])) if errores else ""
    fs = investigar(idea, err)
    slug = slug_de(idea, fs)
    fs["slug"] = slug
    sc = guionista(fs, idea, err)
    sc["slug"] = slug
    sc["factset"] = f"data/factsets/{slug}.json"
    sc.setdefault("fps", 30)
    sc["cuadro"] = [1080, 1920]
    mundo = animador(fs, sc, err).get("mundo") or {}
    sc["mundo"] = mundo
    return {"slug": slug, "idea": idea, "factset": fs, "script": sc}

IDEAS = json.loads(pathlib.Path("data/ideas.json").read_text(encoding="utf-8"))

def _norm(s):
    return " ".join(str(s or "").lower().split())

def _vetadas(d):
    """§4.1: cada vetada es {titulo, razon, vetada_por} y NO tiene id, por eso `set(vetadas)`
    revienta con 'unhashable type: dict'. Se comparan textos normalizados; ante la duda se
    saltea, porque el muro medico pesa mas que perder una idea."""
    out = []
    for v in d.get("vetadas", []):
        if isinstance(v, dict):
            out += [t for t in (_norm(v.get("titulo")), _norm(v.get("id"))) if t]
        elif v:
            out.append(_norm(v))
    return out

VETADAS = _vetadas(IDEAS)

def vetada(idea):
    textos = [_norm(idea.get(k)) for k in ("id", "hook", "fenomeno", "mito_a_corregir")]
    return any(t and (t == v or v in t or t in v) for v in VETADAS for t in textos)

candidatas = [i for i in IDEAS["ideas"] if i["estado"] == "LISTA_PARA_INVESTIGAR"]
salteadas_por_vetada = [i["id"] for i in candidatas if vetada(i)]
if salteadas_por_vetada:
    print("salteadas por estar vetadas:", ", ".join(salteadas_por_vetada))
pend = [i for i in candidatas if not vetada(i)]
pend.sort(key=lambda i: -int(i.get("potencial_retencion", 0)))
LOTE = int(os.getenv("LOTE", "7"))
print(f"{len(pend)} candidatas; se procesan {min(LOTE, len(pend))} por potencial de retencion")

LOTE_HECHO = {}
for idea in pend[:LOTE]:
    try:
        r = generar(idea)
        LOTE_HECHO[r["slug"]] = r
        idea["estado"], idea["slug"] = "BORRADOR_VALIDANDO", r["slug"]
        print(f"[ok] {idea['id']} -> {r['slug']}  ({len(r['script']['beats'])} beats, "
              f"{len(r['factset']['claims'])} claims)")
    except Exception as exc:                                   # noqa: BLE001 - el lote sigue
        print(f"[salto] {idea['id']}: {exc}")
pathlib.Path("data/ideas.json").write_text(json.dumps(IDEAS, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
'''

CELDA_3 = '''# ============================================================================
# CELDA 3 · AUTO-VALIDACION (muralla 2) + 2 rondas de reintento + reporte data/qc/
# Falla todo -> ESCALA. Nunca se parchea a mano (regla §8-bis.2).
# ============================================================================
import json, pathlib, subprocess, sys, time

sys.path.insert(0, "agente")
from validate import FRASES_VETADAS, check_factset, check_piezas, check_script, check_urls

def escribir(slug, r):
    esc = pathlib.Path("data/escenas") / slug
    esc.mkdir(parents=True, exist_ok=True)
    (pathlib.Path("data/factsets")).mkdir(exist_ok=True)
    pathlib.Path(f"data/factsets/{slug}.json").write_text(
        json.dumps(r["factset"], ensure_ascii=False, indent=2), encoding="utf-8")
    (esc / "script.json").write_text(json.dumps(r["script"], ensure_ascii=False, indent=2),
                                     encoding="utf-8")

def revisar(slug, r):
    """Todo lo que el codigo puede decidir, lo decide el codigo (no el modelo)."""
    errs = check_factset(r["factset"]) + check_script(r["script"]) + check_piezas(r["script"])
    errs += check_urls(r["factset"])                       # HTTP 200 + frase clave en la pagina
    for b in r["script"]["beats"]:
        for f in FRASES_VETADAS:
            if f in b["linea"].lower():
                errs.append(f"beat {b['tipo']}: frase vetada '{f}' (§5.9)")
    if not (45.0 <= sum(len(b["linea"].split()) for b in r["script"]["beats"]) * 0.34 <= 62.0):
        errs.append("el guion se sale de la ventana de 60 s")
    if r["factset"].get("riesgo_medico") != "bajo" and not any(b.get("chip")
                                                                for b in r["script"]["beats"]):
        errs.append("falta el chip 'Esto no es consejo medico' (muro medico §10.3)")
    return errs

def variedad(slug, r):
    """§6.9 anti-auto-plagio: los ganchos del lote no pueden arrancar igual."""
    arranques = {}
    for s, x in LOTE_HECHO.items():
        a = " ".join(x["script"]["beats"][0]["linea"].lower().split()[:3])
        arranques.setdefault(a, []).append(s)
    duplicados = {a: ss for a, ss in arranques.items() if len(ss) > 1}
    return [f"ganchos repetidos en el lote ({a}): {ss}" for a, ss in duplicados.items()
            if slug in ss]

MAX_INTENTOS = 3                                             # 1 + 2 rondas, coherente con §8-bis.2
for slug, r in list(LOTE_HECHO.items()):
    errs = variedad(slug, r) + revisar(slug, r)
    intento = 1
    while errs and intento < MAX_INTENTOS:
        print(f"[reintento {intento}] {slug}: {errs[:3]}")
        LOTE_HECHO[slug] = r = generar(r["idea"], errores=errs)
        errs = variedad(slug, r) + revisar(slug, r)
        intento += 1
    escribir(slug, r)
    r["estado"] = "MASTER-READY" if not errs else "BLOQUEADO"
    pathlib.Path("data/qc").mkdir(exist_ok=True)
    pathlib.Path(f"data/qc/{slug}.md").write_text(
        f"# {slug} · validacion del cerebro\\n\\n"
        f"- fecha: {time.strftime('%d-%b-%Y')} · intentos: {intento}\\n"
        f"- estado: **{r['estado']}**\\n\\n"
        + ("sin fallas\\n" if not errs else "".join(f"- FALLA: {e}\\n" for e in errs)),
        encoding="utf-8")
    print(("  [listo] " if not errs else "  [BLOQUEADO] ") + slug + (" " + str(errs[:2]) if errs else ""))

print("\\nAprobacion humana: leé los factsets y los ganchos de data/qc/*.md antes de la celda 4.")
'''

CELDA_4 = '''# ============================================================================
# CELDA 4 · PUSH: los slugs van al repo y la cola le dice al cron cual renderiza cada dia
# ============================================================================
import json, pathlib, subprocess, time

listos = [s for s, r in LOTE_HECHO.items() if r.get("estado") == "MASTER-READY"]
IDEAS = json.loads(pathlib.Path("data/ideas.json").read_text(encoding="utf-8"))
for i in IDEAS["ideas"]:
    if i.get("slug") in listos:
        i["estado"] = "BORRADOR_APROBADO"
IDEAS["actualizado"] = time.strftime("%d-%b-%Y")
pathlib.Path("data/ideas.json").write_text(json.dumps(IDEAS, ensure_ascii=False, indent=2),
                                           encoding="utf-8")

# cola.txt: linea 1 = lunes ... linea 6 = sabado; linea 7 = repuesto del colchon (§8-bis.4)
cola = listos[:7] or ["S001-parpado-temblor"]
pathlib.Path("data/cola.txt").write_text("\\n".join(cola + [""] * 0) + "\\n", encoding="utf-8")
print(pathlib.Path("data/cola.txt").read_text(encoding="utf-8"))

# El clon de Colab es --depth 1 y puede tener dias: si el repo se movio, el push se rechaza con
# "the remote contains work that you do not have locally". Rebase antes de empujar.
for cmd in (["git", "add", "data/"],
            ["git", "commit", "-m", f"lote dominguero {time.strftime('%d-%b-%Y')} ({len(cola)} slugs)"],
            ["git", "pull", "--rebase", "--autostash", "origin", "main"],
            ["git", "push", "origin", "HEAD:main"]):
    p = subprocess.run(cmd, capture_output=True, text=True)
    print("$", *cmd, "->", (p.stdout or p.stderr).strip()[-300:])
print(subprocess.run(["git", "log", "--oneline", "-2"], capture_output=True, text=True).stdout.strip())
print("Despues de esto: GitHub Actions renderiza el de hoy en ~3 min (medido). Vos cerras la notebook.")
'''

CELDA_5 = '''# ============================================================================
# CELDA 5 (extra) · A/B DE VOCES con la RECETA del §5.4 (Manual del dueño §11)
# Sintetiza el guion de un slug con cada voz Microsoft en los rates de receta y baja un zip.
# Cero claves, cero cuentas: edge-tts. Escuchá la misma frase a +8% y decide con retencion real.
# ============================================================================
import importlib, json, pathlib, sys, zipfile

sys.path.insert(0, "agente")
import voice as V
importlib.reload(V)   # sin esto, un kernel que ya importo voice.py sigue usando la version vieja

SLUG_AB = "S001-parpado-temblor"
VOCES_AB = ["es-ES-AlvaroNeural", "es-ES-JorgeNeural", "es-ES-TomasNeural",
            "es-ES-AlonsoNeural", "es-ES-GonzaloNeural", "es-ES-TeoNeural", "es-ES-SaulNeural"]
sc = json.loads(pathlib.Path(f"data/escenas/{SLUG_AB}/script.json").read_text(encoding="utf-8"))
carp = pathlib.Path("ab_voz") / SLUG_AB
carp.mkdir(parents=True, exist_ok=True)
for vid in VOCES_AB:
    try:
        info = V.build(pathlib.Path(f"data/escenas/{SLUG_AB}/script.json"), carp / vid, voice_id=vid)
        print(f"[ok] {vid}: {info['duracion_s']}s, sync {info['sync_mode']}")
    except Exception as exc:                                 # noqa: BLE001 - la muestra sigue
        print(f"[salto] {vid}: {exc}")
mp3s = list(carp.rglob("voz.mp3"))
if not mp3s:
    raise RuntimeError("ninguna voz genero audio: mira los [salto] de arriba (un zip vacio no sirve)")
ziph = pathlib.Path(f"ab-voz-{SLUG_AB}.zip")
with zipfile.ZipFile(ziph, "w", zipfile.ZIP_DEFLATED) as z:
    for f in mp3s:
        z.write(f, f.relative_to(carp))
print("bajá el zip y escuchá: " + str(ziph))
try:
    from google.colab import files
    files.download(ziph)
except Exception:
    pass
'''

FUENTES = {
    "nbformat": 4, "nbformat_minor": 0,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    },
}


def celda(tipo, fuente):
    lineas = fuente.splitlines(keepends=True)
    return {"cell_type": tipo, "metadata": {}, "execution_count": None,
            "outputs": [], "source": lineas}


def main():
    celdas = [celda(MD, CELDA_PORTADA)] + [celda(t, f) for t, f in
                                           [(CODE, CELDA_1), (CODE, CELDA_2), (CODE, CELDA_3),
                                            (CODE, CELDA_4), (CODE, CELDA_5)]]
    out = pathlib.Path(__file__).resolve().parents[1] / "notebook_cerebro.ipynb"
    out.write_text(json.dumps({**FUENTES, "cells": celdas}, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{out} · {len(celdas)} celdas · {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
