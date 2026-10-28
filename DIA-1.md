# DÍA-1 — de cero al primer video, sin instalar nada en la PC

Todo lo que produce la fábrica ya está escrito en esta carpeta (`fabrica-cuerpo-raro/`).
Este documento te dice **qué tocás vos**, en orden, y **qué archivo va a qué lado**.

El sistema tiene dos mitades y nunca se tocan entre sí:

| Mitad | Dónde corre | Qué hace |
|---|---|---|
| **El cerebro** (creativo) | Colab o Kaggle, con `notebook_cerebro.ipynb` | escribe los guiones, los factsets y los shot-lists. Los sube al repo con `git push`. |
| **El brazo** (determinista) | GitHub Actions, con `.github/workflows/render.yml` | voz + subtítulos + SFX + render + ensamble + QC. Devuelve el MP4. |

---

## 1. Qué archivo es cada cosa (para no perderte)

```
fabrica-cuerpo-raro/
├── README.md                     mapa técnico: las dos mitades y los contratos
├── DIA-1.md                      este papel
├── Tico renovado.md              la biblia: los 10 roles, los contratos, las reglas
├── Manual-del-dueno.md           tu rutina diaria
├── LEEME PRIMERO.txt             índice
├── notebook_cerebro.ipynb        ──> SE SUBE A COLAB (es el cerebro)
├── .gitignore                    qué NO va al repo (los MP4/WAV que produce el brazo)
├── .github/workflows/render.yml  ──> va al repo: el cron que renderiza solo
├── agente/
│   ├── run_pipeline.py           el orquestador del brazo (guion entra, MP4 sale)
│   ├── voice.py                  edge-tts con la RECETA de rates por beat
│   ├── build_comp.py             materializa comp.html desde el shot-list (código, no IA)
│   ├── synth_sfx.py              SFX sintetizados (sin CC0, sin descargas, sin login)
│   ├── validate.py               muralla 2: contratos, frases vetadas, muro médico, URLs
│   ├── qc.py                     QC-AV del master: técnica + contenido real + cámara continua
│   ├── _diag_encuadre.py         cuenta a mano (fuera del CI): qué pieza cae dentro del cuadro
│   │                             en cada beat. Es la que encontró los bugs que el QC daba por buenos.
│   ├── make_notebook.py          regenera notebook_cerebro.ipynb (fuente editable del .ipynb)
│   └── requirements-ci.txt       lo que instala el runner
├── docs/reglas-de-camara.md      la ley de la toma continua y cómo la verifica el QC
├── assets/fonts/                 Inter (OFL) — la única fuente del canal
└── data/
    ├── ideas.json                el backlog de temas
    ├── cola.txt                  línea 1 = lunes … línea 6 = sábado, línea 7 = repuesto
    ├── factsets/S001-…json       la hoja de verdad del video de prueba
    ├── escenas/S001-parpado-temblor/script.json   el guion + shot-list (lo único que sube el cerebro)
    ├── escenas/S001-parpado-temblor/*.mp4|.wav    lo que escupe el brazo (local: una corrida de prueba)
    ├── escenas/S001-parpado-temblor/comp_meta.json las bandas del HUD y el foco de cada beat: se lo
    │                                               dice el comp al QC (CAMBIOS #12). No lo edites a mano
    ├── published/S001-…json      el copy por plataforma (copy-paste al publicar)
    └── qc/CAMBIOS.md             registro de cada cambio de contrato (20 entradas numeradas hoy)
```

**A GitHub va toda la carpeta. A Colab solo se sube `notebook_cerebro.ipynb`** (y ese notebook baja
el resto del repo él solo, con tu token).

---

## 2. Setup único — te quedan ~10 minutos

**Ya está hecho por el brazo** (no lo repitas):

- ✅ Repo creado y público: <https://github.com/EriicksonNTF/Colab-fabrica-video>, rama `main`.
- ✅ Los 31 archivos subidos (1,9 MB). Sin `.mp4` ni `.wav`: el `.gitignore` los frena, y lo que
  llegó de la escena es `script.json`, que es lo único que necesita el brazo.
- ✅ El workflow `tico-render` está **activo y verificado parseado** (GitHub ya lo muestra por nombre,
  no por ruta). Ojo: la primera versión del YAML tenía un error de sintaxis y GitHub **no** avisaba —
  está arreglado y documentado en CAMBIOS #21.
- ✅ Dos corridas de prueba en la nube, desde un checkout limpio del repo público, las dos con
  **QC `PASA` y 0 fallas**:
  [`40619491592`](https://github.com/EriicksonNTF/Colab-fabrica-video/actions/runs/40619491592) en
  `draft` (3 min 54 s, 22,87 MB) y
  [`40621193653`](https://github.com/EriicksonNTF/Colab-fabrica-video/actions/runs/40621193653) en
  `delivery` — que es la calidad del cron diario — (**3 min 11 s**, 26,09 MB, −14,87 LUFS /
  −1,88 dBTP, 10/10 cámaras derivadas). O sea: no depende de esta PC ni de los archivos que hay acá.

**Lo que sólo vos podés hacer** (es el token, y es a propósito):

1. **Creá el token.** github.com → tu avatar → *Settings* → *Developer settings* →
   *Personal access tokens* → **Fine-grained** → *Generate new token* → en *Repository access* elegí
   **only Colab-fabrica-video** → en *Permissions* dejá **Contents: Read and write** y nada más →
   copiá el token (`github_pat_...`).
2. **Colab.** abrí <https://colab.research.google.com> → *Subir* → elegí
   [notebook_cerebro.ipynb](file:///C:/Users/Erickson/Desktop/Muestras/fabrica-cuerpo-raro/notebook_cerebro.ipynb)
   desde tu PC → abrí la llave 🔑 de la barra lateral → *Snippet secrets* → nombre `GH_TOKEN` → pegá el
   token → marcá "Don't require login for runtime access".
3. **Guardá el notebook en tu Drive** (*Archivo → Guardar una copia en Drive*). El `.ipynb` que está
   en la PC es una copia de trabajo: la versión viva es la del Drive.

Ya está: nunca más volvés a hacer esto. El paso 1 no lo puedo correr yo porque el token sale de tu
sesión de GitHub y tiene que quedar cifrado en tu Colab, no en un archivo.

---

## 3. Renderizar un slug cuando se te ocurra (15 min, de los cuales vos mirás 1)

La primera vez ya está corrida: el run 40619491592 del 27-oct dejó el `master_final.mp4` de
`S001-parpado-temblor` en los artifacts de ese run. Este es el procedimiento para cualquier slug,
incluido el del día siguiente.

1. github.com → tu repo → **Actions** → *tico-render* → **Run workflow** → rama `main` →
   en *slug* escribí `S001-parpado-temblor` → *Run workflow*.
2. Esperá. **Medido en el runner: 3 min 11 s en `delivery`** (y 3 min 54 s en `draft`), no los 12-18
   min que suponía la biblia §9. El render corre en la máquina de GitHub, no en la tuya.
3. Cuando termine (✔ verde): panel derecho **Artifacts** → `master-S001-parpado-temblor` →
   descargás un `.zip` con `master_final.mp4`, `hoja_contacto.jpg` y `pipeline_report.json`.
4. Mirá el MP4 (60 s) y la hoja de contacto. Si el run quedó en rojo: abrí el log, bajá a la última
   línea con `::error::`, y mirá `data/qc/{slug}-qcav.md` **dentro del zip del artifact** (el brazo no
   sube el QC de vuelta al repo: corre con `contents: read`, así que en la web de GitHub vas a ver el
   de la última corrida local, no el de hoy).

**Activá las notificaciones por mail de GitHub** (Settings → Notifications → *Watch all activity*
del repo) para enterarte si un día el cron falla sin que vos mires.

---

## 4. Tu primer lote creativo (el domingo, ~45 min)

1. Colab → tu notebook → *Entorno de ejecución → Cambiar tipo de ejecución → GPU T4* → **Ejecutar todo**.
2. Celda 1 (~5 min): baja el repo, instala Ollama, descarga `qwen3.5:9b` (~5 GB). Solo esperás.
3. Celda 2 (~15-20 min): genera el lote. Vas viendo una tarjeta por idea: `[ok] I015 -> S015-dedos-arrugados`.
4. Celda 3 (~2-3 min): auto-valida todo con **código** (contratos, URLs reales, frases vetadas,
   variedad §6.9) y reintenta hasta 2 veces. Lo que no pasa queda `BLOQUEADO` con el motivo en
   `data/qc/{slug}.md`.
5. **Tu revisión (~10 min):** leé los `data/qc/{slug}.md` y los ganchos. ¿Alguna huele mal?
   volvé a correr la celda 2 con esa idea. ¿Todo OK?
6. Celda 4: `git push` de los slugs + `data/cola.txt`. Cerrá la notebook.
7. De acá en más, **el cron hace solo**: lunes a sábado a las 10:40 UTC (07:40 ARG) renderiza la
   línea que le toca según `cola.txt`.

Cuota de Colab de una sesión dominguera: ~40 min. Por eso casi nunca te niega la GPU.

---

## 5. Publicar (10-15 min por día, a mano, por diseño)

1. Actions → el run del día → **Artifacts** → bajás el zip (hacelo el mismo día: los artifacts
   caducan a los 90 días).
2. Mirá el MP4 60 segundos. ¿Chip "Esto no es consejo médico" cuando corresponde? ¿Se entiende el
   subtítulo? ¿El audio no clippea?
3. El texto por red ya está escrito en `data/published/{slug}.json` (se ve desde la web de GitHub):
   copy-paste en TikTok / YT Shorts / IG Reels / FB Reels.
4. **Atajo semanal:** los 6 MP4 del domingo los pasás a los programadores nativos (Business Suite
   programa IG+FB, YouTube Studio programa Shorts, TikTok web programa hasta 10 días adelante).
   Tu semana queda en cero pasos de publicación.

**Lo que nunca vas a hacer:** instalar algo en la PC, correr código local, pagar, usar claves de API
distintas del token de GitHub en Colab, o dejar que un bot toque tus cuentas (§10.2 y §10.5).

---

## 6. Estado honesto de lo que se entregó hoy

Medido sobre masters reales, no sobre estimaciones. Compará el de esta carpeta
(`data/escenas/S001-parpado-temblor/master_final.mp4`, corrida local `delivery` 27-oct 00:31) contra
el que escupió la nube en el run `40621193653`:

- ✅ **El brazo corre solo en la nube y del mismo producto.** Dos corridas `PASA` desde un checkout
  limpio (ver §2). Local: 23,6 MB, −14,86 LUFS, pico −1,93 dBTP. CI `delivery`: 26,09 MB,
  −14,87 LUFS, pico −1,88 dBTP. Mismo master: **53,972 s · 1080×1920 · 30 fps · yuv420p**.
- ✅ **El QC-AV dio `PASA` con 0 fallas en las tres corridas** (local, CI draft, CI delivery).
- ✅ **Cámara continua verificada en el píxel, no declarada**: 810 fotogramas medidos en streaming,
  **0** casi vacíos, **0** congelados, `|Δ²scale|` máximo **0,00383** (piso 0,008) y **10 de 10**
  estaciones derivadas del shot-list. Los 10 beats tienen contenido real dentro de la caja que cada
  uno promete (densidad medida 4,5 %–20,4 %).
- ✅ `hyperframes lint`: **0 errores** y 3 avisos. Los avisos son de estilo del archivo (331 líneas y
  dos `<div>` anidados que piden sub-composiciones); **no** se pueden evitar acá porque el contrato
  de cámara exige exactamente esa estructura `#scene > #cam > #drift > #world`.
- ✅ Los 6 archivos del repo + el notebook + la guía están escritos y validados entre sí; todo
  `agente/*.py` compila y las 5 celdas de código del notebook también.
- ⚠️ El `factset` de S001 tiene **2 claims (C3 y C4) sin URL capturada**: el pipeline los avisa como
  advertencia y no bloquea el render, pero **antes de publicar** esos dos hay que confirmarles la
  ficha o bajarlas del guion (la celda 3 del notebook lo hace con `--urls`).
- ⚠️ edge-tts devuelve el audio pero **sin marcas `WordBoundary`**, así que el karaoke usa el modo
  `proporcional`: cada palabra recibe su parte **de la duración real de ese beat de audio** (los
  tiempos no son de guion, son de la voz que se oyó), pero el corte entre palabra y palabra está
  **estimado por cantidad de caracteres**, no medido. **Esto pasa igual en GitHub Actions**: la
  corrida del 27-oct (run 40619491592) reportó `sync_mode: proporcional` desde el runner. Antes había
  escrito acá que en la nube "normalmente se consiguen"; era una hipótesis y **quedó refutada**, así
  que quedó borrada. Se ve sincronizado; si algún día se rompe, la causa es esta, no el comp.
- ⚠️ Las `hora_sugerida` que escribe `run_pipeline.py` (12:40 / 13:10 / 11:30) vienen del §4.9 de la
  biblia y están en hora peninsular española. El plan de lanzamiento de Ticomental acordó **YouTube
  19:00 y el resto 20:00 CDMX**. Antes de publicar, chequeá esas horas contra tu plan; es una
  decisión tuya, no un bug del brazo.
- ⚠️ Falta la corrida real en Colab: el `qwen3.5:9b` y el `ollama pull` no se pudieron probar acá
  (no hay GPU ni Ollama en esta máquina). El tag del modelo fue verificado contra la biblioteca de
  Ollama el 26-oct-2026; el resto del notebook se ejecuta por primera vez el domingo.
- ⏳ Próximo paso tuyo: el punto 2 de esta guía.
