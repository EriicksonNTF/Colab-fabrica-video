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

## 2. Setup único — ~25 minutos, una vez en la vida

1. **Creá el repo.** github.com → New repository → nombre `fabrica-cuerpo-raro` → **Public** →
   crealo sin README.
2. **Subí esta carpeta.** En la página del repo: *Add file → Upload files* → arrastrá el **contenido**
   de `fabrica-cuerpo-raro/`. Tres detalles que importan:
   - la carpeta `.github` es oculta: activá "ver archivos ocultos" en el explorador o subila aparte
     (dentro de `.github` sólo va `workflows/render.yml`);
   - **no arrastres los `.mp4` ni los `.wav`** que hay dentro de `data/escenas/S001-parpado-temblor/`:
     son de la corrida local de prueba y GitHub Actions los vuelve a crear. Lo que tiene que llegar
     de esa carpeta es **`script.json`**;
   - el uploader web tiene techo de ~100 archivos y 25 MB por archivo. Si te pasa el límite, subi
     primero `agente/`, `.github/`, `data/` y `assets/` en dos tandas.
   `README.md` y `DIA-1.md` también van (son el mapa del repo).
3. **El token (único trámite "técnico").** GitHub → Settings → Developer settings →
   *Personal access tokens* → Fine-grained → **solo este repo** → permisos *Contents: Read and write*
   → copialo.
4. **Colab.** colab.research.google.com → *Subir* → elegí `notebook_cerebro.ipynb` (desde tu PC).
   Abrí la llave 🔑 de la barra lateral → *Snippet secrets* → nombre `GH_TOKEN` → pegá el token →
   marcá "Don't require login for runtime access".
5. **Decile al notebook dónde está tu repo.** En la celda 1, cambiá
   `REPO_URL = "https://github.com/TU-USUARIO/fabrica-cuerpo-raro.git"` por la URL real.
6. Guardá el notebook en tu Drive (*Archivo → Guardar una copia en Drive*). Ya está: nunca más
   volvés a hacer esto.

---

## 3. Estrenar la fábrica con el video de prueba (sin cerebro, ~15 min)

El repo ya trae un guion completo y verificado: `S001-parpado-temblor`.

1. github.com → tu repo → **Actions** → *tico-render* → **Run workflow** → rama `main` →
   en *slug* escribí `S001-parpado-temblor` → *Run workflow*.
2. Esperá **12-18 minutos**. El render corre en la máquina de GitHub, no en la tuya.
3. Cuando termine (✔ verde): panel derecho **Artifacts** → `master-S001-parpado-temblor` →
   descargás un `.zip` con `master_final.mp4`, `hoja_contacto.jpg` y `pipeline_report.json`.
4. Mirá el MP4 (60 s) y la hoja de contacto. Si el run quedó en rojo: abrí el log, bajá a la última
   línea con `::error::`, y mirá `data/qc/` en la web de GitHub.

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

Medido sobre el master real de esta carpeta (`data/escenas/S001-parpado-temblor/master_final.mp4`),
corrida del 27-oct-2026 00:31, calidad `delivery`:

- ✅ **El brazo corrió de punta a punta y el QC-AV dio `PASA` con 0 fallas.** 53,97 s · 1080×1920 ·
  30 fps · yuv420p · 23,6 MB (techo del artifact: 50 MB) · −14,86 LUFS / pico −1,93 dBTP.
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
- ⚠️ En esta PC, edge-tts devolvió el audio pero **sin marcas `WordBoundary`**, así que el karaoke usó
  el modo `proporcional`: cada palabra recibe su parte **de la duración real de ese beat de audio**
  (los tiempos no son de guion, son de la voz que se oyó), pero el corte entre palabra y palabra está
  **estimado por cantidad de caracteres**, no medido. Se ve sincronizado; en GitHub Actions
  normalmente se consiguen las `WordBoundary` y ahí es exacto.
- ⚠️ Las `hora_sugerida` que escribe `run_pipeline.py` (12:40 / 13:10 / 11:30) vienen del §4.9 de la
  biblia y están en hora peninsular española. El plan de lanzamiento de Ticomental acordó **YouTube
  19:00 y el resto 20:00 CDMX**. Antes de publicar, chequeá esas horas contra tu plan; es una
  decisión tuya, no un bug del brazo.
- ⚠️ Falta la corrida real en Colab: el `qwen3.5:9b` y el `ollama pull` no se pudieron probar acá
  (no hay GPU ni Ollama en esta máquina). El tag del modelo fue verificado contra la biblioteca de
  Ollama el 26-oct-2026; el resto del notebook se ejecuta por primera vez el domingo.
- ⏳ Próximo paso tuyo: el punto 2 de esta guía.
