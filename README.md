# Fábrica TICO renovado

"Cosas raras que tu cuerpo hace, explico con ciencia". Reels de ~55 s, 1080×1920, 30 fps,
con el arte **100 % generado por código** (SVG + GSAP), voz TTS y QC automático.
Costo de infraestructura: **0 $**.

**Si es tu primera vez acá, leé [`DIA-1.md`](DIA-1.md).** Este README es el mapa técnico.

---

## Las dos mitades (no se tocan entre sí)

```
  idea ──> [ EL CEREBRO ]  ──git push──>  [ repo ]  ──cron──>  [ EL BRAZO ]  ──artifact──>  MP4
           Colab / Kaggle                                       GitHub Actions
           qwen3.5:9b + Ollama                                 Python + HyperFrames
           escribe guiones y fuentes                            voz, SFX, render, QC
```

| | El cerebro | El brazo |
|---|---|---|
| Dónde corre | `notebook_cerebro.ipynb` en Colab (T4) o Kaggle | `.github/workflows/render.yml` en GitHub Actions |
| Qué produce | `script.json`, `factsets/*.json`, shot-list de piezas | `audio_final.wav`, `comp.html`, `master_final.mp4`, QC, copy de publicación |
| Intervención | el dueño revisa los `data/qc/{slug}.md` el domingo | ninguno: es determinista |
| Fallo | reintenta 3 veces y deja `BLOQUEADO` con motivo | `exit != 0`, el run queda rojo |

El **brazo no piensa**: si un guion no está, falla. El **cerebro no renderiza**: no tiene FFmpeg ni
Chrome. La única escritura compartida es `git push` de archivos de texto.

---

## El brazo, paso a paso

`python agente/run_pipeline.py --slug S001-parpado-temblor`

1. **`validate.py`** — muralla 2: contrato de `script.json`, piezas, frases vetadas, muro médico,
   claims sin URL. Un guion inválido no se renderiza.
2. **`voice.py`** — edge-tts (`es-ES-AlvaroNeural`) con la RECETA de rates por beat
   (HOOK +18 %, MECANISMO −2 %, DEMO/UTILIDAD +6 %, CTA +4 %) y gaps de 0,22 s / 0,30 s antes del CTA.
   Escribe `t_real` por beat y `timestamps.json`. Si edge-tts cae, Kokoro offline.
3. **`synth_sfx.py`** — whoosh/pop/tick/ding/chime **sintetizados con numpy**: sin CC0, sin descargas,
   sin logins.
4. **`mezclar_audio`** — SFX en las llegadas reales (`adelay`) → `amix normalize=0` → `loudnorm` en
   dos pasadas a −14 LUFS / TP −2 dB.
5. **`build_comp.py`** — materializa `comp.html`: toma el shot-list (`piezas[]`) y lo traduce a
   primitivas SVG dentro de la ley de cámara `#scene > #cam > #drift > svg#world`. **Solo `#cam` y
   `#drift` se animan: los cortes son imposibles por construcción.** El encuadre de cada beat se
   *deriva* de la caja de las piezas que entran; `cam` a mano es un override opcional.
6. **`hyperframes render`** — Chrome headless con seek por fotograma + FFmpeg ⇒ determinista.
   `--strict --resolution portrait`. Se verifica además con `npx -y hyperframes lint`.
7. **`qc.py`** — QC-AV: técnica (duración, fps, resolución, pix_fmt, LUFS, dBTP), continuidad de
   cámara (manifiesto `cam_manifest.jsonl`, `|Δ²scale| ≤ 0,008`), y **contenido real en el píxel**:
   cobertura y bbox por beat contra el papel crema, **dentro de la caja que ese beat prometió**
   (`comp_meta.json`). Medir luminancia no detecta una escena vacía; esta comparación sí.

Artefactos por escena: `master_final.mp4`, `hoja_contacto.jpg`, `pipeline_report.json`,
`comp.html`, `comp_meta.json`, `cam_manifest.jsonl`, `data/qc/{slug}-qcav.{json,md}`.
Fuera del pipeline, `agente/_diag_encuadre.py <escena>` imprime qué debería verse en cada beat:
es la cuenta a mano para cuando el QC da verde y el plano igual está malo.

## El cerebro, paso a paso

`notebook_cerebro.ipynb` → *Executar todo*.

1. Celda 1: baja el repo con token de Colab Secrets (`GH_TOKEN`, nunca en código ni en el log),
   instala Ollama, `ollama pull qwen3.5:9b`.
2. Celda 2: los 10 roles de `Tico renovado.md` se recortan **en vivo** del documento (no hay prompts
   duplicados que se desincronicen). Cada salida pasa por un molde Pydantic → JSON Schema de Ollama.
3. Celda 3: auto-validación con el **mismo** `validate.py` del brazo + frases vetadas + variedad §6.9;
   hasta 3 intentos; lo que no pasa deja `data/qc/{slug}.md` con el motivo.
4. Celda 4: `git push` de los slugs y de `data/cola.txt`.
5. Celda 5: A/B de 7 voces edge-tts en un zip, para que el dueño elija a oído.

---

## Contratos

`script.json` (lo único que el cerebro entrega al brazo):

```jsonc
{
  "slug": "S001-parpado-temblor",
  "beats": [ { "tipo": "HOOK|NOMBRE|MECANISMO|DEMO|UTILIDAD|CTA",
               "linea": "…", "zona": "ojo", "t": 0.0, "cam": [x, y, s]  /* opcional */ } ],
  "piezas": [ { "id": "parp1", "tipo": "ojo|parche|senal|circuito|silueta|bandera|anillo|texto|…",
                "p": [x, y], "aparece": 3, "hacia": [dx, dy], "texto": "…" } ],
  "mundo": { "zonas": [ { "id": "ojo", "c": [x, y] } ] }
}
```

`factsets/{slug}.json`: un `claim` por afirmación, con `url` real o `null` + `advertencia`.
**Ninguna URL se inventa**: un claim sin ficha sobrevive como advertencia y el humano la confirma
antes de publicar.

`data/cola.txt`: línea 1 = lunes … línea 6 = sábado, línea 7 = repuesto. El cron del día lee su
línea y renderiza ese slug.

Registro de cambios de contrato: **`data/qc/CAMBIOS.md`** (obligatorio por la biblia: todo cambio de
contrato se anota con fecha y motivo).

---

## Reglas que no se rompen

- **0 $**: GitHub (Actions públicos, 2 000 min/mes), Colab/Kaggle (GPU gratis), HyperFrames Apache-2.0,
  GSAP gratis desde abril 2025 (licencia *Standard*, no OSI — anotado por honestidad), edge-tts,
  Inter (OFL).
- **Sin instalar nada en la PC.** La PC sólo abre el navegador.
- **Logins en lista cerrada**: GitHub, TikTok, YouTube, Instagram, Facebook. Colab (Google) y Kaggle
  son la única excepción abierta, y sólo para el cerebro. Hugging Face no es elegible.
- **Publicación manual**: el MP4 se descarga y se sube/agenda desde las apps oficiales. Sin bots de
  engagement ni automatizaciones ocultas.
- **Sin clonar voces de personas reales.**
- Nada de software propietario ni claves de API de pago.

---

## Límites conocidos (leé esto antes de fiarte del verde)

- Colab/Ollama **no se probaron en esta PC** (no hay GPU): la primera corrida real es la del domingo.
- Si edge-tts no entrega `WordBoundary`, el karaoke cae a modo `proporcional` (estimado por longitud
  de palabra). Se ve bien, pero no es sincronía fonética.
- El QC mide píxeles, no gusto: un plano puede pasar y aun así resultarte feo. Para eso está la
  `hoja_contacto.jpg`.
