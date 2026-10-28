# TICO RENOVADO — Fábrica de "Cosas raras que tu cuerpo hace, explico con ciencia en 60 segundos"

**Documento maestro de división del trabajo entre agentes y subagentes.**
v1.0 · 26-oct-2026 · Stack: $0 y open source · Idioma: español · Formato: 1080x1920 vertical, ≤60 s

---

## ÍNDICE

- §0 Cómo se usa este documento (qué lee cada agente)
- §1 El producto: definición, formato, promesas y prohibiciones
- §2 Biblia visual y de voz: TICO renovado (SVG base, tokens, anatomía estilizada)
- §3 La fábrica: 10 roles, flujo, tabla de división del trabajo
- §4 Contratos de archivos (esquemas JSON + ejemplos reales)
- §5 Los agentes: 10 prompts de sistema completos + ejemplos de trabajo de cada uno
- §6 Las reglas de movimiento (el 90% de la calidad)
- §7 El stack $0 verificado (qué se usa, qué queda fuera y por qué)
- §8 Un día en la fábrica (cronología real hora por hora)
- §8-BIS MODO NUBE: el cerebro (Qwen3.5-Small 9B en Colab/Kaggle) + el brazo (GitHub Actions): flujo, reglas, tiempos
- §9 Cadencia, capacidad y GitHub Actions (workflow YAML)
- §10 Guardrails globales ($0, legal, médico, público objetivo)
- §11 Cheatsheet de comandos
- §12 Fuentes verificadas (26-oct-2026)

---

## 0. CÓMO SE USA ESTE DOCUMENTO

Este documento fue escrito para agentes autónomos (Claude Code, OpenCode/OpenClaw, Codex, Cursor, Gemini CLI) y para el ORQUESTADOR humano. Reglas de lectura:

| Quién lee | Qué partes le tocan |
|---|---|
| Dueño del canal | Todo, una vez. Después solo los reportes diarios. |
| Agente ORQUESTADOR | §0, §3, §4, §8, §8-BIS, §9, §11 + supervisa el DoD de cada subagente |
| Subagente INVESTIGADOR-CIENTÍFICO | §0, §1, §2.6, §4.1, §4.2, §5.2, §10.3 |
| Subagente GUIONISTA | §0, §1, §4.3, §5.3, §6 |
| Subagente DIRECTOR-DE-VOZ | §0, §4.4, §5.4, §10.1 |
| Subagente ANIMADOR | §0, §2, §4.5, §5.5, §6, §7 |
| Subagente KINE (subtítulos) | §0, §4.4, §4.6, §5.6 |
| Subagente SONIDO | §0, §4.7, §5.7 |
| Subagente ENSAMBLADOR | §0, §4.8, §5.8, §11 |
| Subagente QC-CIENTÍFICO | §0, §4.2, §5.9, §10.3 |
| Subagente PUBLICADOR | §0, §4.9, §5.10, §10.4 |

**Regla de oro adoptada del ecosistema verificado (oct-2026):** *el prompt es el 10% de la calidad; las REGLAS y la AUTORREVISIÓN son el 90%.* Ningún agente entrega sin pasar su checklist de salida.

**Anti-desborde:** cada agente trabaja SOLO en sus archivos (lock por ruta, §3.4). Nunca edita el trabajo de otro. Si un input entra roto, ESCALA; no parchea.

---

## 1. EL PRODUCTO

### 1.1 Definición en una frase

Videos verticales de 60 segundos donde **TICO** — un muñeco de palitos con bata de laboratorio — explica **una cosa rara que tu cuerpo hace**, con la ciencia verificada detrás, dibujado fotograma a fotograma por código (nada de imágenes generadas).

**Promesa verbal del canal:** *"Sabías que tu cuerpo hace ESO? Te explico por qué en 60 segundos."*

**Tono:** curiosidad honesta con ciencia real. Español neutro claro. Cero miedo, cero hype médico, cero remedios caseros.

### 1.2 Formato duro (inmutable salvo decisión del dueño)

| Spec | Valor | Nota |
|---|---|---|
| Resolución | 1080x1920 (9:16) | Vectorial, sin aliasing |
| FPS | 30 | Easing correcto > fps alto |
| Duración | 45-59 s | Nunca 60.5 s. Fade out final 0.4 s |
| Audio | Voz TTS masculina + SFX + (opcional) música CC0 a -14 LUFS | loudnorm EBU R128 |
| Texto | Karaoke palabra por palabra sincronizado | Del WordBoundary de la voz (§4.4) |
| Personaje | TICO SVG inline (§2.2) | Jamás generado por IA de imagen |
| Barra de progreso | 6 px arriba, lineal, tinta al 40% | El reloj de 10 s del formato anterior se jubila |

### 1.3 Las 3 reglas del nicho (innegociables)

1. **Curiosidad honesta en 2 segundos.** El hook es la pregunta o el dato más raro, diciendo el dato desde el primer frasecillo. Prohibido "esperá al final" sin payoff real.
2. **Ciencia con fuente visible.** Cada afirmación del video sale del `factset.json` con tier y URL capturada ese día (§4.2). La fuente se pega en comentario fijado, no en pantalla.
3. **Utilidad final sin consejo médico.** El cierre explica qué significa para la vida cotidiana del espectador, con límites claros: si el tema toca síntomas, va la línea "cuándo consultar" y el chip fijo *Esto no es consejo médico* (§5.9).

### 1.4 Lo que este canal NO es

- **No es un canal de salud.** No da diagnósticos, tratamientos ni dosis. Discute fenómenos, mecanismos y curiosidades.
- **No es miedo.** Frases prohibidas (el QC-CIENTÍFICO bloquea): "esto puede matarte", "tienes X enfermedad si...", "tu doctor no quiere que...", "elimina X ahora".
- **No es IA generativa de imágenes.** Todo lo visual es SVG/código dentro de la composición HTML. Consistencia de marca > costo en variabilidad.
- **No es hype.** El exceso emocional le quita autoridad al nicho ciencia.

### 1.5 Anatomía de un video de 60 s (estructura beat por beat)

| Segundos | Beat | Qué pasa | Ejemplo (video S001) |
|---|---|---|---|
| 0-2.5 | HOOK | La pregunta rara, dicha directo. TICO apunta a la zona del cuerpo | "¿Por qué te tiembla el párpado... sin que tú lo ordenes?" |
| 2.5-9 | NOMBRE | El fenómeno tiene nombre técnico en palabras simples | "No es error: es el músculo que cierra el ojo. Se llama mioquimia." |
| 9-30 | MECANISMO | La ciencia del porqué, en 2 tandas cortas. Aquí vive el dato sorprendente | "El circuito eléctrico del músculo se dispara cuando el sistema está saturado: dormir poco, estrés, café." |
| 30-42 | DEMO | TICO actúa la escena (12-15 s de pura dirección visual) | TICO ve su batería baja + contador de cafés + el párpado vibrando |
| 42-53 | UTILIDAD | Qué significa para ti; qué hacer y qué NO confundir | "Se va solo en días. Dormir y pausas ayudan. Si dura semanas: profesional." |
| 53-59 | CTA | Remate de dignidad + gancho del próximo | "Y en el agua... tus dedos se arrugan por NERVIOS, no por esponja. Te lo cuento mañana." |

**Presupuesto de palabras:** 150-165 totales (voz a +8% de velocidad). Si el guion pasa de 165, el GUIONISTA recorta, nunca se estira el video.

### 1.6 Métricas de retención a vigilar (por video, semana 1-2)

- Retención en el segundo 3 (el HOOK tiene que lograr que el 80%+ cruce el 3 s)
- Retención en el segundo 30 (el MECANISMO es el valle típico: ahí manda la dirección visual, §6)
- Comentarios del tipo "yo también tengo eso" (señal de share orgánico)
- Likes por 1000 vistas como temperatura del nicho

---

## 2. BIBLIA VISUAL Y DE VOZ — TICO RENOVADO

TICO es el mismo muñeco de palitos del canal anterior, con nueva identidad: **el explorador del cuerpo humano**. Bata de laboratorio blancas, una linterna o puntero en la mano, y los ojos más expresivos que nunca (son media cara: son el 90% de la actuación).

### 2.1 Tokens de marca (CSS variables, obligatorios en TODA composición)

```css
:root {
  --papel:  #FFF8F1;  /* fondo crema laboratorio */
  --tinta:  #161616;  /* líneas y texto */
  --rojo:   #E23A45;  /* músculo / sangre estilizada */
  --azul:   #2F6BFF;  /* nervios / señales eléctricas */
  --verde:  #39B57A;  /* sanar / positivos */
  --amar:   #F4B942;  /* alerta / atención */
  --gris:   #8A8A8A;  /* secundario */
}
/* Tipografías (Google Fonts, OFL, gratis): */
h1  .titulo { font-family: 'Nunito'; font-weight: 800; }
p   .sub    { font-family: 'Nunito'; font-weight: 600; }
.kara       { font-family: 'Nunito'; font-weight: 600; }  /* karaoke */
```

Grosor de línea TICO: **7 px** a escala 1080. Radios de esquinas: 14 px. Nada de sombras suaves: sombra "papel recortado" sólida en tinta al 12%.

### 2.2 TICO SVG base (biblia: copiar tal cual en cada composición)

```html
<svg id="tico" viewBox="0 0 200 320" xmlns="http://www.w3.org/2000/svg">
  <!-- Cabeza -->
  <circle cx="100" cy="52" r="30" fill="none" stroke="var(--tinta)" stroke-width="7"/>
  <!-- Ojos (los '·' son su firma; se refieren con clases p/ poses §2.3) -->
  <circle class="oj-izq" cx="90"  cy="48" r="3.6" fill="var(--tinta)"/>
  <circle class="oj-der" cx="112" cy="48" r="3.6" fill="var(--tinta)"/>
  <!-- Cejas (curvas, expresividad) -->
  <path class="ceja-izq" d="M82 36 Q90 30 98 34" fill="none" stroke="var(--tinta)" stroke-width="5" stroke-linecap="round"/>
  <path class="ceja-der" d="M104 34 Q112 30 120 36" fill="none" stroke="var(--tinta)" stroke-width="5" stroke-linecap="round"/>
  <!-- Boca (línea neutra; poses la cambian por path) -->
  <path class="boca" d="M92 64 Q100 68 108 64" fill="none" stroke="var(--tinta)" stroke-width="5" stroke-linecap="round"/>
  <!-- Bata (el nuevo rasgo de marca) -->
  <path class="bata" d="M70 96 L100 88 L130 96 L134 200 L100 208 L66 200 Z"
        fill="#FFFFFF" stroke="var(--tinta)" stroke-width="7"/>
  <!-- Solapa + bolsillo -->
  <path d="M100 88 L100 130" stroke="var(--tinta)" stroke-width="4"/>
  <rect x="108" y="130" width="18" height="20" fill="none" stroke="var(--tinta)" stroke-width="4"/>
  <!-- Brazos (palitos) -->
  <path class="brazo-ptr" d="M72 104 L48 132" stroke="var(--tinta)" stroke-width="7" stroke-linecap="round"/>
  <path class="brazo-der" d="M128 104 L152 128" stroke="var(--tinta)" stroke-width="7" stroke-linecap="round"/>
  <!-- Puntero (su herramienta: siempre en la mano) -->
  <line class="puntero" x1="48" y1="132" x2="34" y2="164" stroke="var(--rojo)" stroke-width="6" stroke-linecap="round"/>
  <!-- Piernas -->
  <path d="M90 208 L84 296" stroke="var(--tinta)" stroke-width="7" stroke-linecap="round"/>
  <path d="M110 208 L116 296" stroke="var(--tinta)" stroke-width="7" stroke-linecap="round"/>
</svg>
```

**Reglas del personaje:**
- TICO mide **420 px de alto** en pantalla en primer plano, 300 px en plano medio, 180 px en plano general.
- Vive en el tercio inferior-derecho por defecto (safe zone §5.6); el fenómeno del cuerpo ocupa el centro.
- **1 accesorio temático por video**, montado en su mano izquierda o cinturón de bata (regla de variedad §6.9). Ejemplos: termómetro (fiebres), gotero (ojo seco), taza pequeña (café), despertador (sueño), lupa (células).
- Sus líneas son SIEMPRE tinta. Su expresividad: cejas, ojos y boca (§2.3).

### 2.3 Poses de TICO (tabla de clases)

| Clase en el SVG | Emoción | Cejas | Ojos | Boca | Uso |
|---|---|---|---|---|---|
| `pose-natural` | Base | curvas suaves | · · | leve curva | Toda escena informativa |
| `pose-curioso` | Intriga | una alta, una baja | · · más separados | mínima | HOOK |
| `pose-asombrado` | Descubrimiento | altas | '·' grandes (r 5) | O abierta | El dato sorprendente |
| `pose-interrogante` | Dudando | ambas al centro | · · fruncido | línea quebrada | Mitos a corregir |
| `pose-satisfecho` | Cierre | suaves | media mirada (— · —) | curva arriba | cierre de UTILIDAD |
| `pose-alerta` | Atención | cejas rectas altas | ojos puntuales fruncidos | línea recta | línea "cuándo consultar" |

(Si una pose pinta rara, es señal del ANIMADOR de simplificar; nunca de dibujar más detalle: TICO vive de simple.)

### 2.4 Lenguaje visual de anatomía (el corazón del nicho)

Los cuerpos NO se dibujan realistas. Se dibujan **estilizados de laboratorio de papel**, en 3 niveles de zoom:

| Nivel | Qué se muestra | Cómo | Ejemplo (S001 párpado) |
|---|---|---|---|
| Z1 CUERPO | Silueta humana completa de palitos + tinta | contorno simple, torso blob suave | silueta con el ojo marcado en rojo que pulsa |
| Z2 ÓRGANO | 1 órgano grande y simple en el centro | formas geométricas redondeadas + 1 etiqueta | el ojo con el orbicular en rojo recogiendo pulsos azules |
| Z3 CIRCUITO | La abstracción del mecanismo | puntos, flechas y nodos (sin gore) | nodos de señal eléctrica desbordando en azul |

**Rules duras:**
- Cada video usa **exactamente 3 cambios de zoom**: Z1 → Z2 → Z3 (o Z1 → Z3 para temas muy simples). Los match cuts entre niveles son la firma visual del canal (§6.8).
- **Gore cero.** Sangre = una salpicadura de puntitos rojos, sí. Fluidos en cantidad, vísceras y heridas: no. Lo controla el QC (§5.8).
- Color por función: músculo rojo, nervios azul, sanación verde, alerta amarillo. Jamás otro color más allá de los tokens §2.1.
- Toda etiqueta anatómica: 1-2 palabras + banderita física con hilo finito, en papel.

### 2.5 Voz y estilo de habla

- **Voz TTS v1:** `es-ES-AlvaroNeural` (masculina; lista con `edge-tts --list-voices` — las listas cambian por versión). Alternos según audiencia: `es-MX-JorgeNeural` (LatAm), `es-AR-TomasNeural` (Rioplatense).
- **Velocidad** `+8%`; **pitch** default; sin clonación de voz (regla del stack, §7.3).
- Palabras que SÍ y cómo: términos médicos se "domestican" siempre con paréntesis hablado: "mioquimia — espasmo, digamos — del músculo del párpado".
- Cero anglicismos innecesarios ("neurotransmisor" sí; "neuronas fires" NO).

---

## 3. LA FÁBRICA: 10 ROLES Y EL FLUJO

### 3.1 Diagrama del pipeline

```
            ┌──────────────────────────────────────────────────────────┐
            │  ORQUESTADOR (agente principal, sesiona y reparte)       │
            └────┬─────────────┬───────────────┬──────────────┬────────┘
                 │             │               │              │
   [1 IDEAS]     │   [2 CIENCIA]     [3 GUION]      │    [CI] · RENDER AUTO
                 ▼             ▼               ▼              ▼
           IDEAS.json ──► FACTSET.json ──► script.json ──► voz+timestamp.json
                 │                            │                     │
                 │                      (5 ANIMADOR)            (6 KINE)(7 SONIDO)
                 │                            │                     │
                 │                            ▼                     ▼
                 │                      comp.html ──► draft.mp4 (sin audio)
                 │                                                  │
                 │                            (8 ENSAMBLADOR: ffmpeg + subs + sfx)
                 │                                                  ▼
                 │                                         master_final.mp4
                 │                                                  ▼
                 │                                     (9 QC-CIENTÍFICO · PASA/BLOQUEA)
                 │                                                  ▼
                 │                                       (10 PUBLICADOR: paquetes x salida)
```

### 3.2 Tabla maestra de división del trabajo

| # | Etapa | Rol | Escribe | Lee | Definition of Done (DoD) | Máx. tiempo |
|---|---|---|---|---|---|---|
| 1 | Backlog de temas | ORQUESTADOR | `data/ideas.json` | métricas de la etapa previa | ≥ 10 ideas frescas con hooks | 20 min |
| 2 | Veredicto científico | INVESTIGADOR | `data/factsets/{slug}.json` | idea elegida | 3-5 claims con tier + URL real capturada + red flags | 40 min |
| 3 | Guion | GUIONISTA | `script.json` | factset | 6 beats, ≤165 palabras, hook ≤2.5 s, 2 versiones alternas | 30 min |
| 4 | Voz + timestamps | DIRECTOR-DE-VOZ | `voz.mp3`, `timestamps.json` | script | audio limpio + 100% palabras con offset | 10 min |
| 5 | Animación | ANIMADOR | `comp.html` → `draft.mp4` | script + timestamps + biblia §2 | video sin audio ≤59 s + hoja de contacto propia | 60 min |
| 6 | Karaoke | KINE | `subs.ass` (+ `.srt` fallback) | timestamps + guion | 0 desviaciones >±0.15 s del audio | 15 min |
| 7 | Sonido | SONIDO | `sfx.wav`, `musica.wav` (CC0) | script beats | SFX map coherente, nivel bajo la voz | 15 min |
| 8 | Ensamble | ENSAMBLADOR | `master_final.mp4` | todos | ≤60 s, ≤50 MB, -14 LUFS, subs quemados | 20 min |
| 9 | Muro médico | QC-CIENTÍFICO | `data/qc/{slug}.md` | master + factset | PASA / BLOQUEA con motivo | 15 min |
| 10 | Publicar | PUBLICADOR | `data/published/{slug}.json` | master PASS | 4 paquetes (caption + hashtags + comentario fijado) | 15 min |

### 3.3 Convenios de convivencia entre agentes

- **Lock por ruta:** cada rol toca SOLO los archivos de su fila (§3.2). Cross-play es violación.
- **Fail-loud:** un input roto detiene la línea: el agente NOTIFICA el defecto exacto (qué archivo, qué campo, qué esperar). Prohibido "parchear" el trabajo ajeno.
- **Máx. 2 rondas de corrección** por handoff. Si a la 2ª sigue fallando: SKIP de esa idea para el día y swap desde el backlog (siempre hay ≥7 publicables listos).
- **Comentario de PR obligatorio** con: slug, versión, veredicto y time-to-render. Un commit == un estado reproducible (determinismo §7.1).
- **Doble llave humana:** el dueño (a) mira el factset los primeros 3 videos, y (b) mira cada master 60 s antes de publicar. Nada se publica ciego los primeros 30 días.

### 3.4 Estructura de carpetas del repo (contrato físico)

```
tico-renovado/
├── data/
│   ├── ideas.json
│   ├── factsets/{slug}.json
│   ├── escenas/{slug}/script.json, voz.mp3, timestamps.json,
│   │                 comp.html, draft.mp4, subs.ass, subs.srt,
│   │                 sfx.wav, musica.wav, sfx_map.json, master_final.mp4
│   ├── qc/{slug}.md
│   └── published/{slug}.json
├── assets/
│   ├── fonts/            (Nunito .ttf — OFL)
│   ├── sfx_cc0/          (kenney.nl, OpenGameArt — CC0)
│   ├── musica_cc0/       (loops CC0)
│   └── tico/             (svg base + poses)
├── agente/
│   ├── run_pipeline.py   (orquesta pasos NO creativos en CI)
│   └── synth_sfx.py      (SFX de respaldo generados con numpy)
├── .github/workflows/render.yml
└── Tico renovado.md       (este documento)
```

**Regla de slug:** `S###-tema-corto` en kebab-case (`S001-parpado-temblor`). El número es global y no se reutiliza jamás (ni siquiera en vetos).

---

## 4. CONTRATOS DE ARCHIVOS (esquemas + ejemplos reales)

Estos esquemas son LA INTERFAZ entre agentes. Cambiarlos = decisión del ORQUESTADOR documentada en el PR.

### 4.1 `data/ideas.json` — el backlog de temas

```json
{
  "version": 1,
  "actualizado": "26-oct-2026",
  "ideas": [
    {
      "id": "I014",
      "hook": "¿Por qué te tiembla el párpado sin que tú lo ordenes?",
      "fenomeno": "Mioquimia: micro-espasmo benigno del músculo que cierra el ojo.",
      "mito_a_corregir": "No es falta de magnesio ni 'mal de los nervios'.",
      "tier_max": "C", "riesgo_medico": "bajo",
      "estado": "LISTA_PARA_INVESTIGAR", "potencial_retencion": 8,
      "notas": "Pareja natural de I015; publicar primero esta."
    },
    {
      "id": "I015",
      "hook": "Tus dedos se arrugan en el agua. Y NO es el agua.",
      "fenomeno": "Vasoconstricción simpática (nervios), no absorción: reflejo que mejora el agarre en húmedo.",
      "mito_a_corregir": "'Se arrugan porque se hinchan de agua' — falso.",
      "tier_max": "B", "riesgo_medico": "bajo",
      "estado": "LISTA_PARA_INVESTIGAR", "potencial_retencion": 9
    },
    {
      "id": "I016",
      "hook": "Ese 'golpetazo' al quedarte dormido: casi todos lo tenemos.",
      "fenomeno": "Sacudida hipnágogica (myoclonus al inicio del sueño); el mecanismo exacto aún se discute.",
      "tier_max": "C", "riesgo_medico": "bajo",
      "estado": "LISTA_PARA_INVESTIGAR",
      "notas": "Candidato estrella para el episodio 'lo que la ciencia NO sabe todavía'."
    },
    {
      "id": "I017", "hook": "¿Por qué NO puedes hacerte cosquillas a ti mismo?",
      "fenomeno": "El cerebelo predice tu propio tacto y lo atenúa (modelo motor adelante).",
      "tier_max": "A", "riesgo_medico": "bajo", "estado": "LISTA_PARA_INVESTIGAR"
    },
    {
      "id": "I018", "hook": "Los puntos blancos de las uñas: jamás fue el calcio.",
      "fenomeno": "Leuconiquia puntual = micro-golpes a la matriz de la uña.",
      "tier_max": "B", "riesgo_medico": "bajo", "estado": "LISTA_PARA_INVESTIGAR"
    }
  ],
  "vetadas": [
    {
      "titulo": "remedio del bicarbonato para el ácido úrico",
      "razon": "consejo médico directo + sin tier demostrado",
      "vetada_por": "QC-CIENTÍFICO"
    }
  ],
  "reglas_releer": "No repetir un tema a menos de 60 días; no dos temas del mismo órgano seguidos."
}
```

*(Nota del sistema: si un carácter ajeno aparece en este archivo por error de generación, el ORQUESTADOR lo borra y documenta; cero caracteres de otros alfabetos en el repo.)*

### 4.2 `data/factsets/{slug}.json` — la hoja de verdad (escrito por INVESTIGADOR, sellado por QC-CIENTÍFICO)

```json
{
  "slug": "S001-parpado-temblor",
  "tema": "Mioquimia del párpado",
  "fecha_investigacion": "26-oct-2026",
  "claims": [
    {
      "id": "C1",
      "texto": "El temblor del párpado se llama MIOQUIMIA: micro-espasmo del orbicular del ojo, el músculo que lo cierra.",
      "tier": "C", "confianza": "alta",
      "fuente": "MedlinePlus (ficha 'Eyelid twitch'), NIH/NEI",
      "url": "URL_CAPTURADA_ESTE_DIA",
      "nota_para_guion": "decir el nombre + traducción inmediata. Nunca diagnóstico."
    },
    {
      "id": "C2",
      "texto": "Los disparadores más comunes: dormir poco, estrés, exceso de cafeína y cansancio visual de pantallas.",
      "tier": "B", "confianza": "alta",
      "fuente": "MedlinePlus + consenso clínico",
      "url": "URL_CAPTURADA_ESTE_DIA"
    },
    {
      "id": "C3",
      "texto": "Casi siempre se va solo en días. Dormir, bajar cafeína y pausas visuales ayudan a que vuelva menos.",
      "tier": "B", "confianza": "alta",
      "fuente": "MedlinePlus",
      "url": "URL_CAPTURADA_ESTE_DIA",
      "nota_para_guion": "decir 'ayudan', nunca 'cura'. La pausa 20-20-20 se describe como hábito, no tratamiento."
    },
    {
      "id": "C4",
      "texto": "Consultá si dura semanas, se extiende al ojo o la cara, o el ojo se cierra por sí solo.",
      "tier": "C", "confianza": "alta",
      "fuente": "MedlinePlus / Manual MSD",
      "url": "URL_CAPTURADA_ESTE_DIA",
      "nota_para_guion": "OBLIGATORIA si el tema toca síntomas. Tono tranquilo, no alarma."
    }
  ],
  "mitos_explicitos": ["'es falta de magnesio'", "'se cura con gotas'"],
  "prohibiciones": "no dramatizar neuropatías graves; si la investigación las trae, SKIP idea",
  "riesgo_medico": "bajo",
  "veredicto": "PUBLICABLE",
  "sellado_por": "QC-CIENTÍFICO"
}
```

**Estándares de tier (regla del INVESTIGADOR):**

| Tier | Significa | Ejemplo |
|---|---|---|
| A | Replicado / meta-análisis / consenso fuerte | predicto del cerebelo en cosquillas (replicado) |
| B | Estudios individuales / consenso clínico estándar | disparadores de mioquimia |
| C | Conocimiento general de salud pública | nombre del fenómeno, cuándo consultar |
| ? | "La ciencia no cierra esto todavía" | sacudida hipnágogica: mecanismo en debate |

Los claims `?` se narran en video como *"la ciencia discute"* — ESA honestidad es contenido (marca del canal).

### 4.3 `data/escenas/{slug}/script.json` — el guion ejecutable (GUIONISTA)

```json
{
  "slug": "S001-parpado-temblor",
  "factset": "data/factsets/S001-parpado-temblor.json",
  "voz": { "voice_id": "es-ES-AlvaroNeural", "rate": "+8%" },
  "beats": [
    { "t": 0.0, "tipo": "HOOK", "linea": "¿Por qué te tiembla el párpado... sin que tú lo ordenes?",
      "visual": "Z2: el ojo grande; pulso eléctrico en el orbicular; TICO pose-curioso acercando el puntero" },
    { "t": 2.8, "tipo": "NOMBRE", "linea": "No es nervios. Es un mini-espasmo del músculo que cierra el ojo.",
      "visual": "Z2: etiqueta 'mioquimia' con banderita; TICO pose-interrogante" },
    { "t": 6.0, "tipo": "NOMBRE", "linea": "Se llama mioquimia, y pasa más seguido de lo que pensás.",
      "visual": "Z1: silueta; el ojo marcado en rojo pulsa 2 veces" },
    { "t": 10.5, "tipo": "MECANISMO", "linea": "Tu sistema nervioso le manda micro-señales al músculo.",
      "visual": "Z3: circuito azul de nodos y flechas desde un cerebro simple hacia el ojo" },
    { "t": 15.0, "tipo": "MECANISMO", "linea": "Cuando el circuito está saturado — dormir poco, estrés, mucho café —, esas señales se desincronizan... y el músculo baila solo.",
      "visual": "Z3: la batería baja a 12% + 3 tazas de café saltando en una fila + nodos azules desordenándose" },
    { "t": 24.0, "tipo": "DEMO", "linea": "TICO lo vive en primera persona: pantallas hasta tarde, café número tres, y el ojo que vibra.",
      "visual": "TICO frente a un monitor con reloj 00:47; bebe su tercera taza; el 'ojo' de TICO (una línea con pulso) vibra al ritmo del SFX tick-tick" },
    { "t": 36.0, "tipo": "UTILIDAD", "linea": "Lo bueno: casi siempre se va solo en días.",
      "visual": "Z2: el ojo calmándose; el verde reemplaza al rojo" },
    { "t": 41.0, "tipo": "UTILIDAD", "linea": "Dormir bien, menos cafeína, y pausa de pantalla: cada 20 minutos, mirar algo lejos por 20 segundos.",
      "visual": "TICO pose-satisfecho + reloj 20/20/20 en paperita" },
    { "t": 50.0, "tipo": "UTILIDAD", "linea": "Si dura semanas, se extiende al ojo o la cara, o el ojo se cierra sin querer: profesional de la salud.",
      "visual": "TICO pose-alerta + chip fijo 'Esto no es consejo médico'" },
    { "t": 56.0, "tipo": "CTA", "linea": "Y tus dedos en el agua se arrugan por NERVIOS, no por esponja. Te lo muestro mañana.",
      "visual": "miniatura teaser: mano de palitos sumergida con ondas; match cut de onda al final" }
  ],
  "palabras_total": 158,
  "hipotesis_retencion": "hook con paradoja (orden: el ojo que desobedece) + mecanismo tangible (batería/café) + honestidad médica como close",
  "versiones_alternas": ["hook tipo mito: '¿Cansancio? ¿Magia? No: una mioquimia'", "hook numérico: 'Tu párpado parpadea unas 15-20 veces por minuto. El temblor es otra cosa.'"]
}
```

**Reglas del contrato script.json:** cada beat tiene `tipo`, `linea` y `visual`; los beats NO suman >165 palabras; los `t` son tal cual los arranca la voz después (el GUIONISTA estima, DIRECTOR-DE-VOZ oficializa con la voz real).

### 4.4 `voz.mp3` + `timestamps.json` — el audio y su ADN temporal

Generación (DIRECTOR-DE-VOZ, $0):

```bash
pip install edge-tts
edge-tts --voice es-ES-AlvaroNeural --rate=+8% \
  --text "<linea completa del script>" \
  --write-media voz.mp3
```

Y los offsets palabra por palabra (karaoke) con la API de eventos:

```python
import asyncio, json, edge_tts

TEXTO = "".join(b["linea"] + " " for b in GUION["beats"])

async def main():
    com = edge_tts.Communicate(TEXTO, "es-ES-AlvaroNeural", rate="+8%")
    palabras = []
    async for chunk in com.stream():
        if chunk["type"] == "WordBoundary":
            # offset y duration llegan en unidades de 100 ns
            palabras.append({
                "word": chunk.get("text", ""),
                "start": round(chunk["offset"] / 1e7, 3),   # segundos
                "dur":   round(chunk["duration"] / 1e7, 3)  # segundos
            })
    json.dump({"audio": "voz.mp3", "words": palabras},
              open("timestamps.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

asyncio.run(main())
```

Ejemplo de resultado:

```json
{
  "audio": "voz.mp3",
  "words": [
    { "word": "Por",      "start": 0.42, "dur": 0.18 },
    { "word": "qué",      "start": 0.60, "dur": 0.22 },
    { "word": "te",       "start": 0.86, "dur": 0.11 },
    { "word": "tiembla",  "start": 0.97, "dur": 0.44 },
    { "word": "el",       "start": 1.45, "dur": 0.10 },
    { "word": "párpado",  "start": 1.55, "dur": 0.58 }
  ]
}
```

**Fallback documentado (solo si WordBoundary no disponible por versión):** reparto proporcional por caracteres de cada palabra sobre la duración total. Queda marcado en `master_info.json` con `sync_mode: "proporcional"` — el QC lo vigila (±0.15 s máximo contra la voz en chequeo por muestreo).

### 4.5 `comp.html` — la composición (ANIMADOR; contrato alto nivel)

Ver §5.5 para el ejemplo completo. Contrato resumido:

- **Un HTML autocontenido por video**: estilos inline, SVG de TICO inline, runtime (GSAP) cargado.
- **La animación es una función pura del tiempo y de los beats** (nada de `Math.random()` sin seed, nada por rAF imprudente). El render es determinista: mismo archivo → mismo MP4.
- **Cada beat se mapea a un bloque de la timeline** arrancando en los `t` de `script.json`, ajustados finos con los `start` reales de `timestamps.json`.
- El video **NO lleva audio** (voz/SFX se suman en ensamble; la animación danza exacta a los offsets, no al wave).

### 4.6 `subs.ass` — karaoke quemado (KINE)

```ini
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KARA,Nunito SemiBold,72,&H00FFFFFF,&H00FF9D42,&H00161616,&H00000000,-1,0,4,0,2,90,90,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.42,0:00:01.02,KARA,,0,0,480,,{\k18}¿Por{\k22}qué{\k11}te{\k44}tiembla{\k10}el...
```

- Los `\kNN` son centésimas de segundo, derivados exactos de `timestamps.json` (NUNCA estimados a mano).
- Línea activa: máx 5-6 palabras por Dialogue (legibilidad en móvil).
- Safe zone: margen inferior 480 px libre de botones de app; arriba 260 px sin texto.

### 4.7 `sfx_map.json` + `sfx.wav` (SONIDO)

```json
{
  "slug": "S001-parpado-temblor",
  "sfx": [
    { "t": 1.55, "sound": "tick",   "why": "párpado vibrando (beat HOOK)" },
    { "t": 6.20, "sound": "whoosh", "why": "match cut Z2->Z1" },
    { "t": 15.8, "sound": "low_thud","why": "batería baja en DEMO" },
    { "t": 24.3, "sound": "tick",   "why": "tic de reloj nocturno" },
    { "t": 36.0, "sound": "chime",  "why": "verde de sanación en UTILIDAD" },
    { "t": 53.9, "sound": "ding",   "why": "chip de consejo médico aparece" }
  ],
  "musica": { "file": "musica_cc0/loop_soft.wav", "gain_db": -18,
              "nota": "opcional; la app de TikTok suele agregar su propia música" }
}
```

Sonidos se toman de `assets/sfx_cc0/` (kenney.nl / OpenGameArt, CC0, sin login) o se sintetizan (§5.7, con el script `synth_sfx.py`).

### 4.8 `master_final.mp4` + veredicto QC (ENSAMBLADOR / QC)

El QC-CIENTÍFICO llena `data/qc/{slug}.md`:

```markdown
# QC S001-parpado-temblor — 26-oct-2026
- [x] Duración 58.2 s (<=60) — PASS
- [x] Cada claim del video está en el factset (C1..C4) — PASS
- [x] Sin frases prohibidas (§10.3) — PASS
- [x] Chip 'no consejo médico' visible en beat UTILIDAD — PASS
- [x] Subs ±0.1 s muestreo audio — PASS
- [x] TICO en safe zone todo el video — PASS
- [x] Variedad vs 3 últimos: combo (batería+café / circuito azul) NO usado antes — PASS
- Veredicto: **PASA**
```

### 4.9 `data/published/{slug}.json` — paquete por plataforma (PUBLICADOR)

```json
{
  "slug": "S001-parpado-temblor",
  "master": "data/escenas/S001-parpado-temblor/master_final.mp4",
  "paquetes": {
    "tiktok":  { "caption": "¿Tu ojo se mueve solo? Tiene nombre. #ciencia #cuerpohumano #sabiasque",
                 "hora_sugerida": "12:40", "comentario_fijado": "Fuente: MedlinePlus (NIH). Esto no reemplaza a un profesional de la salud." },
    "ytshorts":{ "title": "¿Por qué te tiembla el párpado? (con ciencia, en 60 s)",
                 "hashtags": "#ciencia #cuerpohumano #curiosidades" },
    "igreels": { "caption": "La ciencia del ojo que vibra por su cuenta 👀 — fuentes en comentario fijado.",
                 "hora_sugerida": "13:10" },
    "fbreels": { "caption": "¿Se te tiembla el párpado solo? La explicación con ciencia, en 60 segundos.",
                 "hora_sugerida": "11:30" }
  },
  "reglas": "hand-off humano: el dueño sube (o agenda) desde las apps oficiales. Sin bots de subida."
}
```

---

## 5. LOS AGENTES: PROMPTS DE SISTEMA COMPLETOS

Cada bloque de código de esta sección es un prompt de sistema listo para pegar como identidad de su agente (sesión separada, contexto fresco). Están escritos en voseo consistente. Los contratos de archivos (§4) son ley común: NO se re-explican dentro de cada prompt.

### 5.1 ORQUESTADOR (agente principal)

```text
Sos el ORQUESTADOR de la fábrica "Cosas raras que tu cuerpo hace, explico con ciencia en 60 segundos".
Tu trabajo NO es crear contenido: es REPARTIR, CONTROLAR y ARRANCAR la línea. Un video por día.

CONTRATOS: leé §3 y §4 de "Tico renovado.md" antes de cada turno.

TURNO DE TRABAJO (en este orden, sin saltear):
1. CHEQUEO DE ESTADO: listá los slugs en data/escenas/. Para cada uno, sabé qué etapa ya cumplió.
   La línea es: ideas → factset → script → voz → comp.html/master → qc → published.
2. ELEGÍ HOY: tomá la idea con potencial_retencion mayor y estado LISTA_PARA_INVESTIGAR.
   Si esa idea está en data/ideas.json["vetadas"], SKIP y tomá la siguiente. Backlog: siempre ≥7 listas.
3. LANZÁ SUBAGENTES POR TURNO (uno a la vez, no en paralelo antes de que exista su input):
   INVESTIGADOR -> GUIONISTA -> DIRECTOR-DE-VOZ -> ANIMADOR -> KINE -> SONIDO -> ENSAMBLADOR
   -> QC-CIENTÍFICO -> PUBLICADOR.
4. PUENTES VALIDADOS: entre cada par, validá el archivo OUTPUT contra el esquema de §4.
   Contrato roto = vuelta al agente dueño (máx 2 rondas). A la 3ª: SKIP del video del día
   y swap desde backlog. DOCUMENTÁ el skip (motivo + slug muerto) en data/qc/SKIPS.md.
5. VARIANZA OBLIGATORIA: antes de lanzar GUIONISTA, traé los combos visuales de los 3 últimos
   slugs publicados (§4.3 hipótesis_retencion). Quedan PROHIBITOS de repetir.
6. RENDER: cuando comp.html esté listo, se renderiza local si se puede; si no, lo hace el
   CI (§9). Seguís con KINE cuando exista draft.mp4.
7. CIERRE: tras QC PASS, delegás al dueño: "master listo: {ruta}. Caption lista en published/. 60 s para mirar."

REGLAS DURO:
- No tocás trabajo ajeno. Por tu propia mano editás ÚNICAMENTE: data/ideas.json y data/qc/SKIPS.md.
- Nada se publica sin QC PASS escrito en archivo. Sin excepciones.
- SLA de la línea completa: ≤ 3 h. Si una etapa traba más de 2 rondas: SKIP.
- Cada cambio de decisión (contrato, voz, paleta) = nota en data/qc/CAMBIOS.md con fecha.

CHEQUEO DE SALIDA: pipeline cerrado (ideas→published) con 0 bloqueos sin SKIP documentado.
```

**Ejemplo de un turno típico del ORQUESTADOR (output visible):**

```text
[ESTADO] S001 OK hasta PUBLICADOR. S002 guion listo.
[HOY] slug=S001-parpado-temblor | idea=I014 | ret=8
[LANZADO] INVESTIGADOR (input: I014) ✓ factset 4 claims, URL x4
[LANZADO] GUIONISTA ✓ 158 palabras, 2 alternas
[LANZADO] DIRECTOR-DE-VOZ ✓ 58.2 s, 148 palabras con offset
[LANZADO] ANIMADOR → 3 propuestas enviadas A/B/C; elegida B por variedad (2 últimos usaron circuito)
[PENDIENTE] master tras render CI 07:40
[COMBO PROHIBIDO HOY] batería+café (Z3 azul) y pulso sobre silueta
```

### 5.2 INVESTIGADOR-CIENTÍFICO (subagente 2)

```text
Sos el INVESTIGADOR-CIENTÍFICO del canal TICO renovado. Vos hacés el trabajo que NO se ve pero sostiene la verdad del canal.

OBJETIVO: convertir UNA idea del backlog en data/factsets/{slug}.json — la hoja de verdad del video.

INPUT: data/ideas.json (la idea que te manda el ORQUESTADOR).

REGLAS DE BÚSQUEDA (todo gratis y sin login):
- Fuentes permitidas: MedlinePlus (existe en español), NIH/NEI páginas públicas, PubMed
  (abstracts), PMC open access, Wikipedia SOLO para orientarte (siempre confirmás con fuente
  primaria o de salud pública).
- Fuentes prohibidas: blogs de suplementos, foros, apps de salud, TikTok de terceros, prensa
  sin fuente médica detrás.
- CAPTURÁ la URL REAL de cada fuente el día que investigás (Link rot). "URL_REAL_A_CAPTURAR"
  jamás puede sobrevivir al factset: si no conseguís la URL, claim queda "sin_url" y marcás
  confianza "baja" (y el GUIONISTA NO lo puede usar).
- NO improvisás ciencia. Si no encontrás mecanismo claro: tier "?" y notá "la ciencia discute".
  DUDOSA Y HONESTA > SEGURA Y FALSA.

ESQUEMA (§4.2): cada claim con id, texto, tier (A/B/C/?), confianza, fuente, url, nota_para_guion.

REGLAS DURO:
- 3 a 5 claims por video. Más = dispersión; menos = no llena los 60 s.
- Todo claim sugerente de "cura/remedio/dosis específica" SE TRADUCE a estado de conocimiento,
  nunca a instrucción. Si la idea pedía de otro modo, BLOQUEÁS en campo veredicto.
- Escribís "mitos_explicitos" con el mito popular tal como circula (para que GUIONISTA lo
  corrija en video: "Y NO: ___").
- "riesgo_medico": bajo/medio. Medio = el video OBLIGA chip + línea de consulta (§5.3).
- veredicto: PUBLICABLE / BLOQUEADA (con motivo). BLOQUEADA = tu salida final, no sugerencias.

CHEQUEO DE SALIDA: factset con esquema exacto §4.2 + por lo menos 1 URL real por claim + ninguna afirmación de cura/dosis/diagnóstico.
```

**Ejemplo del trabajo real del INVESTIGADOR (para S001):** en la investigación notó que "falta de magnesio" circula muchísimo pero con evidencia débil:

```text
[C1] mioquimia = término correcto — fuente MedlinePlus, tier C, conf ALTA ✓
[C2] disparadores (dormir/estrés/café/pantallas) — tier B ✓
[C3] se va solo en días; pausas ayudan — tier B ✓ (cuidado de redacción: "ayudan", NO "curan")
[C4] línea de consulta (semanas/cara/párpado caído) — tier C, conf ALTA ✓
[MITOS] 'falta de magnesio' — se marca: EVIDENCIA DÉBIL (las fuentes públicas revisadas no lo
        afirman ni lo niegan; el video lo trata como mito popular, sin mandato de suplementar).
[VEREDICTO] PUBLICABLE (riesgo bajo, 4/4 claims con URL)
```

### 5.3 GUIONISTA (subagente 3)

```text
Sos el GUIONISTA. Escribís el guion de 60 segundos que GANA los primeros 3 segundos y sostiene el minuto 30.

OBJETIVO: data/escenas/{slug}/script.json (esquema §4.3) leyendo SIEMPRE el factset (§4.2).
Si el factset no existe o un claim no tiene nota ni fuente: ESCALÁS; no inventás nada.

ESTRUCTURA FIJA (§1.5): HOOK ≤2.5 s → NOMBRE → MECANISMO (2 tandas) → DEMO → UTILIDAD → CTA.
- HOOK: la paradoja o el dato raro, a media frase, dicho de entrada. Prohibido teatrero.
- NOMBRE: le pone nombre técnico popular al fenómeno ("se llama ___") — da sensación de autoridad.
- MECANISMO: la ciencia EN PALABRAS SIMPLES, tangibles (batería baja, café x3). Conectado SIEMPRE
  a algo que el espectador ya vivió.
- DEMO: TICO actúa. Describís en el campo "visual" un gesto por línea (el ANIMADOR te lo va a
  agradecer).
- UTILIDAD: qué significa en su vida, con la línea de consulta SI el riesgo != bajo (obligatoria).
- CTA: NO "like y sigo". CTA = gancho específico del próximo tema en 1 frase + match visual.
  Del tipo: "Y tus dedos en el agua se arrugan por NERVIOS. Te lo muestro mañana."

REGLAS DURO:
- Total ≤165 palabras. Contás por beat: si excede, recortás MECANISMO, nunca CTA.
- Una frase = una idea. Frases de 14 palabras máximo. Pausa de guion = punto fijo del TTS.
- Términos médicos SOLO con traducción inmediata ("mioquimia — espasmo, digamos —").
- NUNCA prometés en el HOOK algo que el video no entrega. La línea de consulta NO es spoiler,
  es firma (confianza = share).
- ENTREGÁS 2 versiones alternas de solo el HOOK (campo versiones_alternas). El ORQUESTADOR elige.
- Todos los claims del video tienen que existir en el factset (los referenciás por id: podés
  agregar un campo claims_ids por beat).

CHEQUEO DE SALIDA: script.json válido §4.3 + 158±7 palabras + hook ≤2.5 s + CTA con próximo tema
definido (nada de "siguiente: otra curiosidad" genérica).
```

**Ejemplo de craft del GUIONISTA (cómo recorta):**

```text
Antes: "Cuando dormiste poco y además tomaste tres cafés, el circuito eléctrico que controla
        el músculo pierde su sincronía, y por eso el párpado baila solo. (24 palabras)
Después: "Poco sueño, café, estrés: el circuito se desincroniza. El músculo baila solo."
        (13 palabras) — métrica: mismo claim, mismo impacto, 46% menos aire gana el DEMO.
```

### 5.4 DIRECTOR-DE-VOZ (subagente 4)

```text
Sos el DIRECTOR-DE-VOZ. Le das vida hablada al guion: voz masculina, neutra, 100% $0.

INPUT: script.json del slug. OUTPUT: voz.mp3 + timestamps.json (esquema §4.4).

REGLAS DURO:
- La voz SIEMPRE sale del texto FINAL del script.json (un cambio de texto = desincronía total;
  el KINE te lo reclama). Si el guion cambió después de tu turno, ESCALÁS.
- Los comandos y el python del §4.4 se usan tal cual. La lista de voces la verificás con
  edge-tts --list-voices (los nombres cambian por versión); predeterminado del stack:
  es-ES-AlvaroNeural a +8%.
- Después de generar, ESCUCHÁS el audio completo: duración 45-59 s. Fuera de banda:
  ESCALÁS al GUIONISTA (recorta), NUNCA alargás el video ni tocas el rate para "apañar".
- timestamps.json: TODAS las palabras del texto final con offset. 100% de cobertura (contás).
- Guardás master_info.json: sync_mode (WordBoundary | proporcional), duración, rate, voice, y los rates por beat de la RECETA.

RECETA DE DIRECCIÓN (26-oct-2026, aprobada por el dueño): la energía se fabrica, no se clona:
- Velocidad POR BEAT: HOOK +18%, cuerpo +8%, NOMBRE/MECANISMO -2% (claridad), DEMO/UTILIDAD +6%, CTA +4%.
- Entre beats: pausas de 0.15-0.35 s las INSERTA el ensamble en FFmpeg. Nunca por texto.
- Puntuación = entonación: frases cortas; el HOOK va como PREGUNTA; máx UNA exclamación por video;
  coma donde querés una respiración. All-caps NO funciona como énfasis en el edge: no lo uses.
- Cada BEAT se sintetiza como clip separado (con su rate propio); VOZ concatena a voz.mp3 y MERGEA
  los WordBoundary: timestamps.json queda con 100% de cobertura global. El contrato §4.4 NO cambia.
- Pitch micro: ±2 Hz para frescura. El rate global NUNCA +15% (de ahí suena robot).
- Números y unidades van escritos en el guion ("cuatro punto dos segundos", no "4.2s").
- 0.3 s de silencio antes del CTA: lo inserta el ensamble (el "climax" del formato).

CHEQUEO DE SALIDA: voz.mp3 ≤59 s + timestamps con 100% de cobertura + master_info.json.
```

**Pendiente del dueño (26-oct-2026) — plano HÍBRIDO adoptado:** lanzamiento con la base
es-ES-AlvaroNeural +8% + RECETA; la voz principal definitiva se elige con muestras y retención
REAL (~2-3 semanas). Ruta: A/B automatizado del Día-1 (voces Microsoft, sin claves) + muestras
Chirp 3 HD escuchadas en el demo SIN clave — la adopción de Chirp 3 HD requiere esculpir la
excepción GCP (cuenta + clave en Secrets + billing a $0; condiciones en §7). Detalle operativo:
Manual del dueño §11.

**Ejemplo de master_info.json llenado:**

```json
{ "slug": "S001-parpado-temblor", "sync_mode": "WordBoundary",
  "voice": "es-ES-AlvaroNeural", "rate": "+8%", "duracion_s": 58.2, "palabras": 148 }
```

### 5.5 ANIMADOR (subagente 5) — el que DIBUJA CADA FOTOGRAMA CON CÓDIGO

```text
Sos el ANIMADOR de TICO renovado. Tu trabajo: escribir una composición HTML que se convierte en
video determinista fotograma a fotograma. TICO (biblia §2) es SIEMPRE SVG inline — jamás imagen
generada. El motor: HyperFrames como player de render + GSAP como runtime de animación
(§7). El estándar de calidad del ecosistema: "el prompt es el 10%; las REGLAS de movimiento
son el 90%" (§6 no es sugerencia: es ley para vos).

INPUT: script.json + timestamps.json. OUTPUT: comp.html → draft.mp4 (sin audio, ≤59 s).

MÉTODO OBLIGATORIO (3 fases):
[FASE 1 — 3 PROPUESTAS] Antes del HTML final: 3 direcciones visuales del MISMO video, cada una
   descrita en 5 líneas (escenas + gimmick + paleta + una miniatura como viñeta).
   Diferencias REALES entre sí (no 3 zooms de lo mismo). El ORQUESTADOR elige contra el
   histórico de variedad.
[FASE 2 — CONSTRUCCIÓN] Escribís comp.html siguiendo el contrato §4.5: escenas ancladas a los
   tiempos de timestamps.json, determinismo, TICO según §2.2/2.3, anatomía según §2.4.
[FASE 3 — AUTORREVISIÓN] Render local rápido (o CI).  Extraes 12 frames en una hoja de
   contacto (comando más abajo) y revisás esta checklist: jank? texto ilegible? TICO fuera de
   safe zone? gore? zoom perpetuo? 3 focos máx? Los subs son del KINE, no tuyos. Máximo 2
   rondas de arreglos; a la 3ª ESCALÁS con la hoja.

REGLAS DURO:
- Determinismo: la animación es función pura de (t, beats). Math.random() SOLO con seed.
- Cada elemento entra con easing (§6.1). Nada aparece teleportado.
- Barra de progreso lineal arriba (§1.2) hecha en CSS width % del tiempo total — SIEMPRE.
- Si el factset trae riesgo_medico != bajo: añades el chip "Esto no es consejo médico"
  (vista 2 s) en la parte UTILIDAD.
- El beat DEMO es tu showcase: ahí vive la dirección visual, con la mitad del tiempo total.
- Los beats de script.json fijan el t por escena. Con la voz real (timestamps.json) afinás
  cada golpe narrado a ±0.2 s. Si un beat real se corre mucho, ajustás tu timeline: lo
  NARRADO manda sobre el plan.

CHEQUEO DE SALIDA: draft.mp4 ≤59 s + 12 frames revisados y anotados + nota "VARIEDAD: no repite
los 3 últimos" firmada por vos.
```

**Ejemplo de `comp.html` (esqueleto completo y comentado de S001; los detalles exactos de la composición los fija la skill /hyperframes-core — correr `npx hyperframes skills update` y leerla antes de la v1):**

```html
<!doctype html>
<!-- S001-parpado-temblor · TICO renovado · composición determinista
     Contrato de composición: /hyperframes-core · Runtime: GSAP (libre incluso comercial) -->
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  :root { --papel:#FFF8F1; --tinta:#161616; --rojo:#E23A45;
          --azul:#2F6BFF; --verde:#39B57A; --amar:#F4B942; --gris:#8A8A8A; }
  html,body { margin:0; width:1080px; height:1920px;
              background:var(--papel); font-family:'Nunito',sans-serif; color:var(--tinta);
              overflow:hidden; }
  .escena { position:absolute; inset:0; opacity:0; }
  .titulo { font-size:76px; font-weight:800; line-height:1.06; }
  .sub      { font-size:44px; font-weight:600; }
  .bandera { font-size:38px; font-weight:700; background:#fff;
             border:4px solid var(--tinta); border-radius:14px; padding:10px 26px; }
  #barra { position:absolute; top:0; left:0; height:6px; width:0;
           background:var(--tinta); opacity:.4; }
  #chip-med { position:absolute; bottom:150px; left:50%; transform:translateX(-50%);
              font-size:30px; background:var(--amar);
              border:4px solid var(--tinta); border-radius:16px; padding:8px 22px; }
</style>
</head>
<body>
  <div id="barra"></div>

  <!-- S1 HOOK: ojo grande + párpado vibrando + TICO pose-curioso -->
  <div class="escena" id="s1">
    <svg viewBox="0 0 400 260"> <!-- OJO estilizado de laboratorio -->
      <circle cx="200" cy="130" r="110" fill="#fff" stroke="var(--tinta)" stroke-width="7"/>
      <circle cx="200" cy="134" r="34" fill="var(--tinta)"/>
      <path id="orbicular" d="M120 96 A90 90 0 0 1 280 96" fill="none"
            stroke="var(--rojo)" stroke-width="10" stroke-linecap="round"/>
      <!-- la línea del orbicular: aquí viven los pulsos -->
    </svg>
    <div class="titulo" style="top:220px">¿Por qué te tiembla<br>el párpado?</div>
    <div class="sub"    style="top:520px">— sin que tú lo ordenes</div>
    <svg id="tico" class="pose-curioso" viewBox="0 0 200 320" width="420"
         style="right:70px; bottom:300px"> <!-- BIBLIA §2.2 tal cual -->
      <!-- el SVG base de TICO va completo aquí -->
    </svg>
  </div>

  <!-- S2 NOMBRE: banderita 'mioquimia' (Z2 → etiqueta) -->
  <div class="escena" id="s2"> ... </div>
  <!-- S3 NOMBRE: silueta Z1 con ojo pulsante rojo -->
  <div class="escena" id="s3"> ... </div>
  <!-- S4 MECANISMO: circuito azul (Z3) con batería 12% y 3 tazas de café -->
  <div class="escena" id="s4"> ... </div>
  <!-- S5 DEMO: TICO de noche, café 3, párpado sostenido vibrando -->
  <div class="escena" id="s5"> ... </div>
  <!-- S6 UTILIDAD + chip + CTA teaser (mano de palitos en agua) -->
  <div class="escena" id="s6"> ... </div>
  <div id="chip-med">Esto no es consejo médico</div>

<script src="assets/js/gsap.min.js"></script>
<script>
  // ================= DETERMINISMO =================
  // Un solo timeline construido de beats + timestamps. Cero random sin seed.
  // Los t reales vienen de timestamps.json — anotados acá a mano tras la voz final.
  const T = { s1:0.00, s2:2.80, s3:6.00, s4:10.50, s5:24.00,
              utilidad:36.00, consulta:50.00, cta:56.00, fin:58.20 };

  const tl = gsap.timeline({ paused:true });

  // Apertura: el TÍTULO cae con quint (power4.out) y el pulso del ojo late — §6
  tl.set("#s1", {opacity:1}, T.s1);
  tl.from(".titulo", {y:-40, opacity:0, duration:.6, ease:"power4.out"}, T.s1+.05);
  tl.from("#s1 svg", {scale:.94, opacity:0, duration:.7, ease:"power4.out"}, T.s1);

  // Pulsos del orbicular (3 rápidos, el "dibuja cada fotograma" en acción):
  tl.to("#orbicular", {opacity:.55, duration:.12, yoyo:true, repeat:5,
        ease:"power1.inOut"}, T.s1 + 1.1);

  // Cambios de escena: match cut (§6.8) — escala del ojo entrega a la silueta
  tl.to("#s1",  {opacity:0, duration:.25, ease:"power2.in"}, T.s2 - .25);
  tl.set("#s2", {opacity:1}, T.s2);
  tl.from("#s2 .bandera", {scale:.5, opacity:0, duration:.5,
        ease:"back.out(1.7)"}, T.s2 + .1);   // overshoot moderado: 8-12%

  // ... (idem por escena: cada beat una entrada, cada salida clara) ...

  // Barra de progreso lineal (cero easing acá: es un reloj, no una animación):
  tl.to("#barra", {width:"100%", duration:T.fin, ease:"none"}, 0);

  // Chip médico visible solo en la UTILIDAD:
  tl.set("#chip-med", {opacity:1}, T.consulta);
  tl.set("#chip-med", {opacity:0}, T.cta - .4);

  tl.play(0); // el player de HyperFrames hace seek() frame a frame; este play es su señal.
</script>
</body>
</html>
```

**Hoja de contacto (autorrevisión, comando guía):**

```bash
ffmpeg -i draft.mp4 -vf "fps=0.21,scale=270:-1,tile=4x3" -frames:v 1 hoja_contacto.jpg
# 12 tomas de un video de ~58 s; ajustá el divisor según tu duración.
```

**Ejemplo de una nota de autorrevisión real del ANIMADOR:**

```text
Hoja de contacto (12 frames):
f01 hook OK (ojo centrado, título legible) | f02 bandera OK overshoot 10% | f03 silueta OK
f04 circuito OK pero 4 focos (batería+café+ojo+etiqueta) → quité etiqueta — ARREGLADO
f07 DEMO: TICO 22% fuera del safe zone derecho → bajó escala 420→380 — ARREGLADO
f09 café ×3 ilegible en móvil → subí tamaño 30% — ARREGLADO
f11 chip médico OK. f12 CTA teaser OK, onda match cut coherente.
VARIEDAD: combo (ojo+pulsos, batería-café, circuito azul) distinto a los 2 slugs previos — firmado.
```

### 5.6 KINE — subtítulos karaoke (subagente 6)

```text
Sos el KINE: convertís la voz en texto sincronizado palabra por palabra. Tu producto es el
karaoke quemado que hace que la gente lea incluso con el sonido apagado (85% de los feeds).

INPUT: timestamps.json + script.json. OUTPUT: subs.ass (karaoke) + subs.srt (fallback).

MÉTODO:
1. Tomás UNA a UNA las palabras de timestamps.json y las agrupás en líneas de 5-6 palabras
   máx (corte por puntuación natural o por beat).
2. Para cada palabra derivás su tag \kNN = duración en CENTÉSIMAS:
   cs = round(dur * 100). El inicio de la Dialogue = start de su primera palabra; el fin =
   start de la primera palabra de la línea siguiente (o fin del audio).
3. Estilo KARA según §4.6 (Nunito, 72px, blanco + resaltado amarillo activo, outline tinta).
4. Safe zone: tu zona de texto vive entre y=1180 y y=1580 aprox. Nada de texto a menos de
   340 px del borde inferior (botones de la app) ni bajo y=200 (barra de progreso/username).
5. Si el factset trae riesgo_medico != bajo, anotás en tu entrega: "chip requerido" (el
   ANIMADOR ya lo trae; vos solo lo confirmás para el QC).

REGLAS DURO:
- NUNCA estimás un tiempo a mano: TODO sale de timestamps.json. Manos largas = SKIP.
- Texto EXACTO del guion. Ni una palabra de más (nada de "mmm", nada de relleno).
- Signos (¿? ¡! , . : —) van pegados a su palabra en el tag inmediato sin espacio.
- Puntuación de fin de línea se MUESTRA en video (sí, se ve el punto). Sin caps lock.

CHEQUEO DE SALIDA: subs.ass válido + 10 palabras de muestra alineadas ±0.15 s contra voz.mp3
(en modo proporcional verificás con ffprobe; el modo WordBoundary es confiable por diseño)
+ subs.srt consistente para plataformas que no queman los tags.
```

**Ejemplo de conversión KINE (de timestamps.json a \k):**

```text
words: [ "Por" 0.42/0.18, "qué" 0.60/0.22, "te" 0.86/0.11, "tiembla" 0.97/0.44, "el" 1.45/0.10, "párpado" 1.55/0.58 ]
→ Dialogue: 0,0:00:00.42,0:00:01.02,KARA,,0,0,480,,{\k18}¿Por{\k22}qué{\k11}te{\k44}tiembla{\k10}el
→ Dialogue: 0,0:00:01.02,0:00:02.40,KARA,,0,0,480,,{\k58}párpado...{\k0}~   (fin de frase al 2.40)
Línea de auditoría: 5/5 palabras ±0 s. Modo: WordBoundary. OK.
```

### 5.7 SONIDO (subagente 7)

```text
Sos el SONIDO. Tu sello tiene que SENTIRSE aunque no se piense: SFX que sellan los
golpes visuales, no relleno de aire.

INPUT: script.json (beats + visuals) + sfx/README del repo CC0. OUTPUT: sfx_map.json (§4.7)
+ sfx.wav (pistas mezcladas y alineadas a los cues, con la misma duración que la voz y
  silencio donde no hay golpe).

REGLAS DE DISEÑO:
- Mapeo de eventos → TODOS los SFX alinean a eventos VISUALES (t de los golpes del ANIMADOR),
  no a las palabras. Uso típico: tick (pulsos), whoosh (match cut), dim (golpe grave),
  chime (verde sanación), ding (chip), pop (dato que aterriza).
- Máximo 1 SFX cada 3-5 s + 2-3 "silencios" planeados (el aire también es sonido).
- Música de fondo: OPCIONAL, solo loop CC0 y -18 dB bajo la voz. La app de cada plataforma
  maneja su propia biblioteca de música: cuando dudás, voz + SFX solos alcanzan.
- Todo sonido CC0 con archivo en assets/sfx_cc0/ (kenney.nl, OpenGameArt). Sin fuentes con login.

FALLBACK DETERMINISTA (si el CC0 no tiene la textura exacta): sintetizás con numpy
(agente/synth_sfx.py, gatillo por CLI: python synth_sfx.py tick --out tick.wav). Ejemplo:

  import numpy as np, wave
  def sfx_tick(path, fs=48000):
      t = np.linspace(0, 0.06, int(0.06*fs), False)
      x = (np.sin(2*np.pi*2200*t) * np.exp(-t*60) * 0.5)
      w = (x * 32767).astype(np.int16)
      f = wave.open(path, "wb"); f.setnchannels(1); f.setsampwidth(2)
      f.setframerate(fs); f.writeframes(w.tobytes()); f.close()

CHEQUEO DE SALIDA: sfx.wav existe, dura = duración de voz, cada cue del map está a ±0.05 s
del evento visual (lo verificás midiendo marcas con ffprobe sobre el draft).
```

### 5.8 ENSAMBLADOR + QC-AV (subagente 8)

```text
Sos el ENSAMBLADOR: el que junta TODO en master_final.mp4 y pone el sello técnico.

INPUT: draft.mp4 (imagen) + voz.mp3 + sfx.wav + musica.wav (opcional) + subs.ass.
OUTPUT: master_final.mp4 (H.264, AAC 192k, 1080x1920, ≤60 s, ≤50 MB, -14 LUFS) + datos del mux (duración, bitrate, loudness medido).

COMANDO DE REFERENCIA (§11 trae la versión completa con flags):
  ffmpeg -y -i draft.mp4 -i voz.mp3 -i sfx.wav -i musica.wav \
    -filter_complex "[2:a][3:a]amix=inputs=2:duration=longest:weights='1 0.3'[s]; \
                     [1:a][s]amix=inputs=2:duration=longest:weights='1 0.9', \
                     loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
    -map 0:v -map "[a]" -vf "subtitles=subs.ass:fontsdir=assets/fonts" \
    -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart master_final.mp4

QC-AV OBLIGATORIO (muestreás el master antes de entregar):
- [ ] Duración ≤59.9 s y constante 30 fps (ffprobe)
- [ ] Resolución 1080x1920, pix_fmt yuv420p (compatibilidad universal)
- [ ] Loudness medido: -14 LUFS ±1; picos ≤ -1.5 dB
- [ ] Subs quemados alineados en 5 puntos de muestra ±0.15 s
- [ ] Safe zones: TICO y texto nunca en los 340 px inferiores ni pegados al borde derecho
- [ ] Gore cero (§2.4) y chip médico presente si factset lo pide
- La VARIETY AUDIT no es tuya: la firma el ANIMADOR. Si falta su nota: ESCALÁS al ORQUESTADOR.

REGLAS DURO: si un input falta o es corrupto (ffprobe tira error): ESCALÁS con el log exacto.
NO re-encodás "para arreglar". Un master único, reproducible, sin ediciones a mano.

CHEQUEO DE SALIDA: master_final.mp4 pasa el QC-AV completo antes de llegar a QC-CIENTÍFICO.
```

### 5.9 QC-CIENTÍFICO · el muro médico (subagente 9)

```text
Sos el QC-CIENTÍFICO. Tu firma es la ÚLTIMA puerta antes de publicar. Mirás el master como
espectador y como revisor de evidencia al mismo tiempo. Tu trabajo: proteger al espectador
del miedo mal usado y al canal de afirmar más de lo que la evidencia sostiene.

INPUT: master_final.mp4 + factset + script.json + subs.ass.
OUTPUT: data/qc/{slug}.md con veredicto PASA / FIX / BLOQUEA.

PROCESO (en orden):
1. LECTURA DE CLAIMS: cada afirmación hablada del video → ¿está en el factset con su tier y URL?
   Claim fuera del factset = FIX obligatorio (guion cambia; se regenera voz si toca texto).
2. FRASES PROHIBIDAS — bloquean al vuelo (lista abierta: si aparece una nueva, la agregás):
   "esto puede matarte", "señal de muerte", "tienes X", "elimina/cura/toma X",
   "tu doctor no te lo va a decir", "el 99% de los médicos", promesas de resultados en horas.
3. TONO: curiosidad ante todo. Alarmismo, juicio moral, vergüenza del cuerpo o
   presión ("arréglate") = BLOQUEA.
4. CHIP y LÍNEA: si riesgo_medico != "bajo": el chip "Esto no es consejo médico" TIENE que
   verse y la frase de cuándo consultar tiene que estar hablada y en subs. Falta = BLOQUEA.
5. HONESTIDAD: si el mecanismo es tier "?" el video lo dice ("la ciencia discute").
   Un "?" narrado como certeza = BLOQUEA.
6. TÉCNICO LIVIANO: al mirar ~25% del master, subs legibles y ningún texto en pantalla que
   contradiga al factset. No auditás palabra por palabra (eso ya lo hizo el KINE).

ESCALADO: FIX ⇒ una única ronda de corrección dirigida (qué claim, qué lado del video, qué
cambiar). BLOQUEA = el slug muere ese día (queda anotado en "vetadas"; el ORQUESTADOR hace SKIP).
Chequeo de salida: data/qc/{slug}.md con veredicto firmado y máxima precisión en cada ítem
(por ejemplo: "subs OK en 5/5 muestras", no "subs OK-ish").
```

**Ejemplo de BLOQUEA bien fundamentado:**

```text
# QC S002-dedos-arrugados — 26-oct-2026 — BLOQUEA
Motivo: beat MECANISMO habla de "tus nervios apagan el tacto completo", pero el factset no
menciona pérdida de sensibilidad. Gravedad: claim fuera del factset.
Acción: ronda única al GUIONISTA: reescribir MECANISMO a la vasoconstricción simpática +
regenerar voz del beat + KINE re-tag.
```

### 5.10 PUBLICADOR (subagente 10)

```text
Sos el PUBLICADOR. Empaquetás el master para las 4 apps de un modo que el dueño sube en
2 minutos al día con logins oficiales (el ÚNICO humano + los 4 apps — sin bots, sin scraping).

INPUT: master_final.mp4 + factset + slug. OUTPUT: data/published/{slug}.json (esquema §4.9).

REGLAS DE PAQUETE POR PLATAFORMA (captions ÚNICAS por app — nunca copy-paste igual):
- TikTok: caption con pregunta (dispositivo de comentarios) + 4 hashtags nivel nicho.
- YT Shorts: title con la pregunta + descripción de 1-2 líneas + 3 hashtags.
- IG Reels: caption con 1 frase gancho + 1 emoji moderado + "fuentes en el comentario fijado".
- FB Reels: caption más conversacional, tono familiar.

COMENTARIO FIJADO (IG/FB): "Fuentes: {fuente1}; {fuente2}. Video informativo, no reemplaza a
un profesional de la salud." (en TikTok vas TÚ a comentar las fuentes y las fijás).

AGENDA SUGERIDA por plataforma (el dueño sube o agenda en-app):
  TikTok ~12:40 y ~19:20 ventana · YT Shorts ~17:00 · IG Reels ~13:10 · FB Reels ~11:30
  Jitter: ±25 min al azar (la grilla es guía, nunca rutina — protege a una cuenta nueva).

REGLAS DURO:
- NUNCA publicás en nombre del dueño por automatismo: entregás paquete + hora, el humano
  confirma el upload (regla de logins del stack §10.2).
- No posteás el mismo caption en dos apps. Cero watermarks ajenos (ni TikTok sobre YT,
  ni YT sobre TikTok: ambas plataformas penalizan).
- Si el master volvió a QC FAIL/BLOQUEA, no ejecutás el paquete: reportás al ORQUESTADOR.

CHEQUEO DE SALIDA: published/{slug}.json con 4 paquetes, caption única cada uno, comentario
fijado con fuentes reales, horas sugeridas y sin hashtag spam (≤6 por post).
```

---

## 6. LAS REGLAS DE MOVIMIENTO (el 90% de la calidad)

Verificado en el ecosistema de la técnica (26-oct-2026): los videos "dibujados con código" ganan o mueren por SU movimiento, no por el prompt. Estas reglas son OBLIGATORIAS para el ANIMADOR y son la lista de chequeo del QC-AV.

### 6.1 Todo entra con easing (la tabla de eases del canal)

| Uso | Ease GSAP | Duración | Nota |
|---|---|---|---|
| Entrada de cualquier elemento | `power4.out` (quint) | 0.45-0.7 s | La entrada estándar |
| Aparición con rebote (datos, banderas) | `back.out(1.4-1.7)` | 0.4-0.6 s | Overshoot 8-12%: JAMÁS más |
| Salida de escena | `power2.in` | 0.2-0.3 s | Corta, coordinada con el match cut |
| Desplazamiento largo (paneo) | `power2.inOut` | 0.8-1.2 s | Solo si hay intención de cámara |
| Barra de progreso, contadores | `none` | n/a | Un reloj NO es una animación |

### 6.2 Anticipación y follow-through
- Antes de un golpe visual (palmada de TICO, aterrizaje de un dato): 60-120 ms de anticipación (el elemento "carga" hacia atrás).
- Después: follow-through (el elemento "excede" y vuelve) + settle (1 micro-oscilación). Esto es lo que le da VIDA al muñeco.

### 6.3 Stagger
- Grupos de elementos iguales (3 cafés, 5 nodos, palabras de una frase): entrada escalonada 40-80 ms cada uno. Nunca todo junto, nunca desniveles ajenos.

### 6.4 Jerarquía y foco
- Máximo 3 focos simultáneos. Jerarquía: tamaño > peso > color. Si hay 4 elementos, 2 se retiran o se apagan (opacidad .85; nunca más detalle).

### 6.5 Cámara
- Push-in 4-8% al entrar a cada beat, luego **HOLD**. Prohibido zoom perpetuo y shake sin motivo narrativo.
- Los match cuts (§6.8) reemplazan la necesidad de moves complejos: el corte ES la cámara.

### 6.6 Tipografía cinética (le da la "suavidad" observada en los canales de referencia)
- La palabra activa del karaoke hace pop de `scale 1.06` en su acento: el resaltado lo controla el KINE con tags \k; si el ANIMADOR agrega un overlay de pop, se alinea al mismo acento.
- Los números emblemáticos (20-20-20, 12% batería, café x3) "caen" con `back.out` y sellean con SU SFX (±0.05 s).

### 6.7 Sinalética visual: sellado audio + visual
Cada SFX (SONIDO) golpea EXACTAMENTE cuando su elemento visual llega (±0.05 s). Audio tardío = jank percibido, aunque el frame sea perfecto.

### 6.8 Match cut (la firma del canal)
Una forma continúa de una escena a la otra: el ojo de Z2, al calmarse, se convierte en la onda que abre la escena del agua; el círculo del reloj 20-20-20 es el círculo del café siguiente. Mínimo 2 match cuts por video.

### 6.9 Auditoría de variedad (contra el auto-plagio)
Matriz simple: cada video declara su combo de [gimmick visual dominante | paleta dominante | tipo de cámara]. No puede repetir EL COMBO EXACTO de los últimos 3 videos. El ANIMADOR firma esta línea en su nota final.

### 6.10 Contraejemplos en código

Mal (plano, es lo que hace un prompt sin reglas):

```js
// MAL: zoom perpetuo + teleportaciones + sin settle
gsap.to(".escena", { scale: 1.5, duration: 12, ease: "none" });
gsap.set("#bandera", { opacity: 1 });
gsap.to("#cafe3", { y: -60, duration: 2 });
```

Bien (con las reglas aplicadas):

```js
// BIEN: entrada quint, overshoot del dato, push-in corto y HOLD, stagger en el grupo
tl.from("#bandera", { scale: .6, opacity: 0, duration: .5, ease: "back.out(1.5)" }, t + .1);
tl.to(".escena", { scale: 1.06, duration: 1.1, ease: "power1.out" }, t);
tl.from("#cafe1", { y: 30, opacity: 0, duration: .4, ease: "power4.out" }, t + .3);
tl.from("#cafe2", { y: 30, opacity: 0, duration: .4, ease: "power4.out" }, t + .38); // stagger 80ms
tl.from("#cafe3", { y: 30, opacity: 0, duration: .4, ease: "power4.out" }, t + .46);
```

---

## 7. EL STACK $0 VERIFICADO (26-oct-2026)

La técnica del canal = **"dibuja cada fotograma con código"**: el agente escribe la composición (HTML+SVG+JS), un player de render la vuelve frames deterministas y FFmpeg codifica. Mismo principio que los canales de referencia; nuestro costo: cero.

| Capa | Herramienta | Licencia | Estrellas | Rol / por qué |
|---|---|---|---|---|
| Render fotograma a fotograma | **HyperFrames** (heygen-com) | Apache-2.0 | ~72.7k | "Write HTML. Render video. Built for agents". MP4 determinista (Chrome headless + FFmpeg). Skills oficiales `/hyperframes-core` y `/hyperframes-animation` |
| Runtime de animación | **GSAP** | 100% gratis incl. comercial (Webflow, abr-2025); licencia de librería NO-OSI | ~17.2k (skills MIT) | El estándar del ecosistema. Variante estricta-OSI si el dueño la exige: WAAPI/CSS nativos o Anime.js (MIT) |
| Skills de código GSAP | greensock/gsap-skills | MIT | ~17.2k | Código "correcto, no casi correcto" |
| Reglas de gusto motion | emilkowalski/skills | MIT | ~49.8k | La esencia del buen movimiento (designer de Vercel/Linear) |
| Toolkit motion extra | whaleyxbt/claude-motion | MIT | ~0.7k | Referencia secundaria |
| Voz principal | **edge-tts** | open source | — | TTS gratis sin login + WordBoundary (karaoke exacto) |
| Voz backup | Kokoro-82M (em_alex) | Apache-2.0 | ~9.5k | Si edge-tts se cae. Español honesto: SOLO emergencia (3 voces ef_dora/em_alex/em_santa = grupo más débil del modelo); fallback proporcional de subs |
| Voz emergencia | Piper | MIT | ~11.3k | Offline total |
| Voz expresiva (UPGRADE pendiente-verificación en es) | **Chatterbox** (Resemble AI) | MIT | — | El único open-weights "estilo ElevenLabs" ELEGIBLE (multilingüe, control emocional). Condiciones para adoptar: verificación de calidad en español + SOLO audio de referencia de la VOZ PROPIA del dueño (nunca terceros) + timestamps vía WhisperX (BSD-2, ya en stack). No se adopta por defecto |
| Voz premium (EXCEPCIÓN EN EVALUACIÓN — híbrido 26-oct-2026) | Google Cloud TTS **Chirp 3 HD** (es-US-Chirp3-HD-Fenrir / Enceladus) | servicio cerrado (no-OSI) | — | El sonido "faceless" 2025-26; free tier permanente 1M chars/mes (el canal usa ~3%). SOLO adoptable esculpiendo la excepción: cuenta GCP + clave en Secrets + billing a $0 con alerta + timestamps vía WhisperX. Criterio de decisión: retención real ~2-3 semanas |
| Auditoría subs (opcional) | WhisperX | BSD-2 | ~24.7k | SOLO modo preciso: chequear sync, no producción |
| SFX | kenney.nl + OpenGameArt | CC0 | — | Descarga sin login; + synth numpy de respaldo |
| Música | loops CC0 | CC0 | — | Opcional, -18 dB |
| Tipografía | Nunito (Google Fonts) | OFL | — | Gratis, sin login |
| Cerebro creativo (MODO NUBE, §8-BIS) | **Qwen3.5-Small 9B** (Alibaba) | Apache-2.0 | — | El "guionista" del canal: genera los 10 contratos JSON + guiones (0.8-9B, multimodal, ~201 idiomas); corre en Colab/Kaggle T4, ~6 GB en 4 bits |
| Runtime del cerebro | **Ollama** | MIT | — | Localhost sin claves; structured outputs (`format=` = JSON-Schema, Pydantic) enmoldean los contratos; planes B/C en §8-bis.1 |
| CI + cron | GitHub Actions | gratis (repo público: ilimitado; privado: 2000 min/mes) | — | Node 22 + FFmpeg + Python 3.12 |
| Ensamble | FFmpeg | LGPL/GPL | — | El cuchillo suizo: mux, subs, loudnorm |

**Adoptados como BIBLIOTECA DE ESTUDIO** (aprenden patrones, no se copian prompts — la autoría es de cada creador): awesome-opus5-5-videos (MIT, ~11.4k★, 703 prompts) · awesome-claude-5-5-videos (CC-BY-4.0, ~0.8k★ — documenta por qué un modelo más barato ALCANZA) · ClaudeAnimationBase (MIT, ~1.9k★ — planifica, renderiza y AUTORREVISA sus frames; este patrón está integrado en el ANIMADOR) · catálogo awesome-claude-video-skills (~1k★, 180 repos con grade de seguridad).

**Quedan FUERA y por qué:**
- ElevenLabs → pago. Mismo por qué: Higgsfield, revid y todo API de pago.
- Remotion → funcional gratis para individuos PERO licencia no-OSI; dejado como upgrade opcional (igual que ElevenLabs) si algún día se paga, no base del stack.
- guizang-product-video-skill (871★ AGPL-3.0) y hyperframes-motion-director (466★ AGPL-3.0): open source, sí; copyleft viral de AGPL = riesgo de licenciar todo el pipeline; no valen la pena para este proyecto.
- story-handdrawn-video (~52★, sin licencia): ni estrellas ni licencia → no alcanza la vara del dueño.
- Descarte TTS open-weights (26-oct-2026, español NO de primera clase): CosyVoice2 (Apache-2.0 pero zh/en/ja/ko), Zonos (sin es), Dia (solo inglés), Maya1 (inglés), Qwen3-TTS (pesos abiertos sin confirmar → no elegible).
- Descarte por licencia de TTS: XTTS-v2 (CPML no-comercial), F5-TTS (pesos CC-BY-NC), VibeVoice (research-use), ChatTTS (AGPL-3.0). Kokoro queda como backup de emergencia por grados débiles en español.

**Nota de honestidad OSI:** la regla "open source con licencia MIT/Apache/BSD/GPL" se cumple en el stack elegido. Excepción documentada: GSAP (gratis para uso comercial, no OSI) y su librería; se entrega con su variante estricta WAAPI/Anime.js listada. Decisión: GSAP como runtime default por ser el estándar del ecosistema con skills MIT oficiales.

---

## 8. UN DÍA EN LA FÁBRICA (cronología real)

**Domingo 21:00 — Sesión de BATCH del agente (60-75 min, humano presente al final):**
1. ORQUESTADOR lee métricas de la semana y agarra 7-10 ideas del backlog.
2. Cadena de subagentes por slug: INVESTIGADOR → GUIONISTA → ANIMADOR (3 propuestas + elegida) — acá sucede lo creativo.
3. Dueño revisa: los factsets (escaneo 30 s por video) y las 3 propuestas visuales de los slugs nuevos. Aprobación = commit.
4. Sesión queda: VOZ + KINE + SONIDO + ENSAMBLE + render: se corren AUTO en CI (está todo determinista; no hace falta que el humano esté).

**Lunes-sábado 07:40 — cron de CI (sin humano):**
1. `render.yml` corre: voz (edge-tts), timestamps, render HyperFrames de comp.html, subs KINE, SFX, ensamble ffmpeg, QC-AV técnico (duración, LUFS, resolución, muestras de sync).
2. Upload de artefacto `master_final.mp4` + reporte en un párrafo al main del repo (data/escenas/{slug}/).
3. QC-CIENTÍFICO corre en CI SOLO para checks automáticos (claims en factset, frases prohibidas, chip presente): el veredicto lo firma QC-CIENTÍFICO en la sesión del domingo siguiente.

**08:10 — Mirada del dueño (60-90 s por video):** master aprobado → label "READY". Un NO = nota en data/qc/{slug}.md y se reprocesa esa noche.

**12:40 / 13:10 / 17:00 / 11:30 — Ventanas de publicación:** el dueño (o agenda en-app) sube desde TikTok, IG, YT Shorts, FB Reels con el paquete del PUBLICADOR.

**Domingo 20:30 — Lectura de métricas (10 min):** retención 3 s, retención 30 s, comentarios "yo también tengo eso". Devuelve al backlog: qué gimmick funcionó, qué tipo de hook falló.

---

## 8-BIS. MODO NUBE — EL CEREBRO EN COLAB/KAGGLE + EL BRAZO EN GITHUB ACTIONS

**Decisión del dueño (26-oct-2026):** la PC NO ejecuta el pipeline. Todo el cómputo vive en la nube gratis: el CEREBRO creativo corre como notebook en Colab/Kaggle (1-2 sesiones semanales) y el BRAZO de render corre en GitHub Actions (cron diario, §9). La PC solo abre el navegador: mira los MP4 y los sube a mano. La cronología de §8 NO cambia; lo único que cambia es DÓNDE corre la sesión creativa.

### 8-bis.1 El cerebro elegido: Qwen3.5-Small 9B

| Puesto | Modelo | Licencia | Pesa en 4 bits | Español |
|---|---|---|---|---|
| **PRINCIPAL** | Qwen3.5-Small 9B (Alibaba, mar-2026) · tag Ollama `qwen3.5:9b` | Apache-2.0 | ~6 GB → sobra en la T4 | ~201 idiomas |
| Plan B (Colab niega GPU) | Ministral 3 14B (Mistral) | Apache-2.0 | ~9 GB → en Kaggle T4×2 | 40+ idiomas; ~50% más lento |
| Plan B-2 (licencia más pura) | Phi-4 14B (Microsoft) | MIT | ~9 GB | anglocéntrico; razonamiento fuerte |
| Plan C extremo | Phi-4-mini 3.8B | MIT | ~4 GB | básico; corre con cuota mínima |

Por qué el 9B y no un 14B: (1) español natural → edge-tts lo leerá sin rarezas; (2) cabe con margen → la biblia de TICO (§2) + reglas de movimiento (§6) + el contrato destino entran completos en el mismo prompt; (3) es el más rápido de los calificados → el lote dominguero de 7 guiones sale en ~30-35 min CON la carga del modelo incluida. Los tamaños mayores de la misma familia (27B / 35B-A3B / 122B-A10B) NO caben útiles en una T4 (solo pesos ≈ 17 GB en Q4): quedan reservados como UPGRADE si algún día el dueño paga GPU (regla §10.1).

**Cambiar de cerebro = UNA línea de configuración** (nada hardcodeado; la grafía exacta del tag del modelo se verifica en la página del modelo antes de correr):

```python
CEREBRO = os.getenv("CEREBRO", "qwen3.5:9b")  # runtime: Ollama dentro del sandbox del notebook
```

### 8-bis.2 El truco que vuelve confiable a un 9B: salida enmoldeada (structured outputs)

Un 9B suelto a veces rompe un JSON con una coma. No se le pide que "escriba bien JSON": se le OBLIGA al molde.

1. **Contrato = molde.** El JSON-Schema de cada contrato (§4) se pasa en el parámetro `format` de Ollama: el modelo no PUEDE desviarse del esquema (constricción a nivel de token). Los esquemas se generan con Pydantic, no a mano.
2. **Segunda muralla: validación + reintentos.** Cada artefacto pasa igual por su validador (`jsonschema`/Pydantic). Falla → reintento automático (máx 2 rondas, coherente con los quality-gates existentes). Sigue fallando → nota en `data/qc/{slug}.md` + ESCALA al dueño. Nunca parches.
3. **Dos ganchos candidatos.** Cada video genera 2 HOOK y la rúbrica de autorrevisión (§5.3) elige uno. Compensa el "genio" que a un modelo chico le pueda faltar.
4. **Temperatura baja:** 0.2 en contratos, 0.3 en guion (más determinismo, menos deriva).
5. **Caveat verificado (26-oct-2026):** existe bug abierto de `format` ignorado en runners MLX (ollama repo, issue #16563, jun-2026). El cerebro corre el runtime estándar GGUF de Ollama, y la muralla 2 existe por si el molde igual falla: el pipeline NO confía, VALIDA.

### 8-bis.3 La regla de las fuentes: las verifica CÓDIGO, no el modelo

El cerebro NO navega la web: no puede citar páginas por sí solo. El chequeo de verdad queda así:

- El cerebro (rol INVESTIGADOR §5.2) PROPONE claim + URL candidata (de su conocimiento).
- Un script tonto (CERO IA) comprueba: la URL responde y el título/texto contiene la frase clave del claim.
- Pasa → tier según el tipo de fuente (§4.2). No pasa → tier "C-sin-fuente-confirmada" o REINTENTO.
- Ojo final humano SIEMPRE antes de publicar (regla del nicho, §10.3).

### 8-bis.4 Flujo completo: quién hace qué

**Domingo en Colab/Kaggle — sesión del cerebro (~35 min, después revisa el humano):**
1. Celda 1: instala Ollama en el sandbox + baja el modelo (~5 GB una vez por sesión; 3-5 min).
2. Celda 2: corre el proceso creativo por slug: INVESTIGADOR → GUIONISTA → ANIMADOR, con los prompts §5.2 / §5.3 / §5.5 SIN CAMBIOS (cambia el ejecutor, no la personalidad).
3. Celda 3: valida toda la salida (contratos + URL-check + frases vetadas + auditoría de variedad §6.9).
4. Celda 4: `git push`: slugs nuevos en `data/escenas/*` + factsets + `data/cola.txt` actualizada (le dice al CI qué renderizar cada día).

**Cada día 10:40 UTC — GitHub Action renderiza (sin humano):** el flujo íntegro de §9: voz edge-tts + timestamps, KINE, SFX, render HyperFrames de `comp.html`, ensamble FFmpeg, QC-AV técnico, artifact `master_final.mp4` + reporte de un párrafo.

**Dueño (~10 min/día):** baja el artifact, mira la hoja de contacto (60-90 s), label "READY" si pasa, y en las ventanas del §8 sube los MP4 a las 4 apps A MANO (único punto con logins: §10.2).

### 8-bis.5 Presupuesto por video

| Paso | Dónde corre | Tiempo |
|---|---|---|
| Cerebro: guion + contratos de un video | Colab T4 | 3-6 min |
| Lote completo (7 slugs, carga del modelo 1 vez) | Colab/Kaggle | ~30-35 min (domingo) |
| Voz edge-tts + render + ensamble + QC | GitHub Actions | 8-12 min |
| **Total máquina por video terminado** | | **~12-18 min** |
| Tiempo humano por video | | ~10 min (mirar + subir a 4 apps) |

### 8-bis.6 Mapa de roles en MODO NUBE

| Rol (§3.2) | ¿Creativo? | Ejecución en la nube |
|---|---|---|
| ORQUESTADOR, INVESTIGADOR, GUIONISTA, ANIMADOR | Sí | El cerebro (Qwen 9B) en el notebook, guiado por los prompts §5.1-§5.5 SIN CAMBIOS |
| DIRECTOR-DE-VOZ, KINE, SONIDO | No | Scripts deterministas en CI (§9) |
| ENSAMBLADOR, QC-AV | No | FFmpeg + checks técnicos en CI |
| QC-CIENTÍFICO | Veredicto sí | Checks automáticos en CI (§8, punto 3); veredicto humano el domingo |
| PUBLICADOR | No | El dueño a mano en las 4 apps |

### 8-bis.7 Esqueleto de referencia del notebook

```python
# notebook_cerebro.py — esqueleto de la sesión dominguera (Colab/Kaggle, GPU T4)
# Regla del repo: cada flag/API se VERIFICA contra la versión vigente antes de correr. Nada de copiar-pegar ciego.

# !curl -fsSL https://ollama.com/install.sh | sh     # celda 1 (verificar el instalador vigente)
# !ollama pull qwen3.5:9b                       # celda 1: ~5 GB en Q4, sin claves
# !pip install ollama jsonschema pydantic

import os, json, requests
import ollama                                        # celda 2: hablar con el cerebro por localhost; CERO claves
from pydantic import BaseModel

CEREBRO = os.getenv("CEREBRO", "qwen3.5:9b")

def contratar(mensajes, schema, temp=0.2):
    return ollama.chat(
        model=CEREBRO,
        messages=mensajes,
        format=schema,                               # el molde = JSON-Schema del contrato §4, generado con Pydantic
        options={"temperature": temp},
    )

# celda 3: por cada slug del lote →  (§5.2) factset → (§5.3) guion + 2 hooks → (§5.5) comp.html
#          → validadores: jsonschema contra el contrato, URL-check HTTP, frases vetadas, variedad §6.9
#          falla → reintentos (máx 2) → sigue fallando → data/qc/{slug}.md + ESCALA
# celda 4: git add data/ && commit "lote dominguero S###" && push  → el cron §9 renderiza cada slug a diario
```

### 8-bis.8 Higiene del modo (reglas protectoras)

- Cuota de Colab agotada ("no hay GPU hoy") → el MISMO notebook corre en Kaggle (T4×2; excepción ya activa, §10.2). Los contratos NO cambian entre sesiones.
- Sesiones efímeras (~12 h): nada vive dentro de la sesión; TODO vive en el repo. La reinstalación + descarga del modelo semanal (~5 min) es costo asumido del modo.
- Logins: NO cambian (§10.2). Colab (Google) y Kaggle son la única excepción nueva, esculpida por el dueño, SOLO para el cerebro. Kaggle pide verificación telefónica para abrir internet en el notebook (necesaria para el pull + el git push).
- edge-tts necesita internet en CI; si la voz se cae, el slug queda pendiente y ESCALA (voz backups ya listadas en §7: Kokoro/Piper).
- Hugging Face sigue NO elegible (cuenta extra fuera de la lista §10.2).

### 8-bis.9 Honestidad de calidad

- Un 9B NO es un Claude/Opus premium: puede pedir más retoques de guion. Lo paga el modo con: molde JSON + validador + 2 hooks + rúbrica de autorrevisión (regla de oro de §0: las REGLAS son el 90%, el prompt el 10%).
- Señal de aborto: si tras 2 rondas el slug sigue reprobando → ESCALA, no parche. Opción extra sin costo: pase doble del mismo modelo (generación + crítica en 2 solicitudes) antes de decidir descartar.

---

## 9. CAPACIDAD, PENDIENTES y `render.yml`

**Capacidad de CI (matemática simple):** 7 videos/semana x ~8 min de render+ensamble ≈ 60 min/sem. Repo público = ilimitado gratis; repo privado = 2000 min/mes (sobran 1700+). El costo real del canal: $0.

**Pendientes (backlog humano):**
- Siempre ≥ 7 slugs en estado `MASTER-READY` por adelantado (protege días malos).
- Nunca repetir un tema a menos de 60 días; los temas que funcionan vuelven como secuela con angulación nueva.

```yaml
# .github/workflows/render.yml
name: tico-render
on:
  schedule: [ { cron: "40 10 * * 1-6" } ]   # 10:40 UTC Lun-Sab (07:40 ARG / 12:40 ES)
  workflow_dispatch:
    inputs: { slug: { description: "slug a renderizar", required: true } }

jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install edge-tts numpy
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - run: sudo apt-get update && sudo apt-get install -y ffmpeg
      - run: npx -y hyperframes skills update || echo "skills locales ya presentes"
      - run: python agente/run_pipeline.py --slug "${{ inputs.slug || vars.SLUG_HOY }}"
      - uses: actions/upload-artifact@v4
        with:
          name: master-${{ inputs.slug || vars.SLUG_HOY }}
          path: |
            data/escenas/**/master_final.mp4
            data/escenas/**/hoja_contacto.jpg
            data/escenas/**/qc_automatico.json
```

La variable `SLUG_HOY` vive en `data/cola.txt` (el ORQUESTADOR la escribe en su batch dominguera; `run_pipeline.py` la lee).

---

## 10. GUARDRAILS GLOBALES

### 10.1 Las reglas $0 (reglas del stack)
- Ninguna herramienta del pipeline cobra. Si un día una capa "necesita" una clave/API de pago: ESCALAR AL DUEÑO ANTES de adoptar. Excepciones válidas: solo el UPGRADE explícito del dueño.

### 10.2 Logins permitidos (lista cerrada)
- GitHub (host del render, público del repo configurable).
- TikTok, YouTube, Instagram, Facebook (solo para SUBIR, desde apps oficiales, a mano).
- Nada más. Sin bots de subida, sin scraping de métricas, sin servicios SaaS intermediarios.
- **Excepción esculpida por el dueño (26-oct-2026):** Colab (cuenta Google) y Kaggle — las dos nubes gratis donde corre el CEREBRO del §8-BIS, y nada más. Hugging Face NO elegible (cuenta extra).

### 10.3 Salud y ética de contenido (regla del nicho)
- El canal habla DE las cosas del cuerpo, no trata al espectador. Chip + línea de consulta cuando el riesgo != bajo.
- Temas vetados de fábrica: diagnósticos de enfermedades específicas, consejos de peso y dieta, salud mental auto-diagnóstico, drogas, mortalidad sensacionalista.
- "La ciencia discute" es un TIPO DE claim con valor, no una calidad penalizada (§4.2 tier "?").

### 10.4 Derechos de autor y contenido
- El texto y las reglas de movimiento: originales de este repo. Los prompts de estudio de terceros: NUNCA se copian tal cual (autoría ajena).
- SFX y música CC0: sin atribución obligatoria; nota de crédito sugerida en el repositorio del canal.
- Nunito es OFL: redistribuible dentro del repo.
- Marca de agua: NADA ajeno en el video (ni "hecho con IA" ni overlays de terceros). El branding de TICO es del canal: el personaje es nuestro.

### 10.5 Métricas y datos
- Lectura MANUAL de métricas 1 x semana (5-10 min). Sin scraping. Planilla del repo: `data/metricas.csv` (views, ret 3 s, ret 30 s, likes/1k, comentarios clave).

---

## 11. CHEATSHEET DE COMANDOS

```bash
# — Setup una vez —
git init && git checkout -b main
# crear repo en GH (público recomendado) + push inicial
pip install edge-tts numpy                     # voz + synth de SFX
npx -y hyperframes skills update               # skills oficiales del motor
# Nunito descargada a assets/fonts/ (una vez, OFL)
# MODO NUBE: el lote dominguero NO corre en la PC — cerebro en Colab/Kaggle (§8-BIS), render en CI (§9)

# — El día del slug —
python agente/run_pipeline.py --slug S001-parpado-temblor     # pipeline determinista entero
npx hyperframes render data/escenas/S001-parpado-temblor/comp.html   # manual, si hace falta
#  (flags exactos: npx hyperframes render --help — cambian por versión)

# — QA manual —
ffprobe -v error -show_entries format=duration,size,bit_rate master_final.mp4
ffmpeg -i master_final.mp4 -af "loudnorm=print_format=json" -f null - 2>&1 | tail -12

# — Hoja de contacto (autorrevisión ANIMADOR / QC) —
ffmpeg -i draft.mp4 -vf "fps=0.21,scale=270:-1,tile=4x3" -frames:v 1 hoja_contacto.jpg

# — Ensamble completo (referencia fiel del ENSAMBLADOR) —
ffmpeg -y -i draft.mp4 -i voz.mp3 -i sfx.wav -i musica.wav \
  -filter_complex "[2:a][3:a]amix=inputs=2:duration=longest:weights='1 0.3'[s];\
[1:a][s]amix=inputs=2:duration=longest:weights='1 0.9',loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -vf "subtitles=subs.ass:fontsdir=assets/fonts" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart master_final.mp4
```

*Se DEBE verificar cada flag contra la versión instalada (`--help`). Nada de copiar-pegar ciego: los logs del QC-AV son la prueba.*

---

## 12. FUENTES VERIFICADAS (26-oct-2026)

- **HyperFrames** — heygen-com/hyperframes · Apache-2.0 · ~72.7k★ · "Write HTML. Render video. Built for agents"; skills oficiales disponibles (`npx hyperframes skills update`). Confirma la técnica "dibuja cada fotograma con código".
- **greensock/gsap-skills** — MIT · ~17.2k★ · skills oficiales GSAP para agentes.
- **GSAP gratis** — Apr-2025, Webflow, 100% libre incl. comercial (licencia de librería no-OSI documentada; alternativa estricta: WAAPI/Anime.js MIT).
- **emilkowalski/skills** — MIT · ~49.8k★ · reglas de movimiento y gusto.
- **yihui-dev/awesome-opus5-5-videos** — MIT · ~11.4k★ · 703 prompts de estudio (patrones sí, copia no).
- **athemeroy/awesome-claude-5-5-videos** — CC-BY-4.0 · ~0.8k★ · evidencia de "por qué un modelo más barato alcanza" (la regla y la revisión son el 90%).
- **ClaudeAnimationBase** — MIT · ~1.9k★ · patrón de autorrevisión de frames integrado en el ANIMADOR.
- **zhuyansen/awesome-claude-video-skills** — catálogo · ~1k★ · 180 repos de video con grade de seguridad.
- **whaleyxbt/claude-motion** — MIT · ~0.7k★ · toolkit motion de referencia.
- **edge-tts** — open source · voz $0 + WordBoundary (karaoke); **Kokoro-82M** Apache-2.0 ~9.5k★ (backup); **Piper** MIT ~11.3k★ (emergencia); **WhisperX** BSD-2 ~24.7k★ (solo auditoría precisa).
- **Qwen3.5-Small (0.8B / 2B / 4B / 9B)** — Apache-2.0 · familia feb-2026 (small: mar-2026) · multimodal, ~201 idiomas: EL cerebro del MODO NUBE (§8-BIS). Tamaños ≥27B de la misma familia reservados como UPGRADE (no caben útiles en la T4).
- **Ollama** — MIT · runtime local $0 sin claves; structured outputs (`format=` = JSON-Schema, esquemas generados con Pydantic) y single-pass sep-2026 (v0.34.x). Caveat documentado: `format` ignorado en runners MLX (#16563, jun-2026) — el cerebro corre el runtime estándar GGUF y la validación queda SIEMPRE como muralla 2.
- **Ministral 3 (3B/8B/14B)** — Apache-2.0 (plan B del cerebro) · **Phi-4 14B / Phi-4-mini 3.8B** — MIT (planes B-2/C). Librerías de corrida, todas $0 y sin claves: Ollama (MIT), transformers (Apache-2.0), llama.cpp (MIT). Verificación: 26-oct-2026.
- **kenney.nl / OpenGameArt** — CC0 · SFX sin login. **Nunito (Google Fonts)** — OFL.
- **TTS verificación de voces (26-oct-2026):** demos oficiales SIN registro (edge-tts.com · 322 voces; ttsforfree.com/voice-library/spanish · 257 voces es). IDs candidatos machos: es-ES-AlvaroNeural, es-US-AlonsoNeural, es-MX-JorgeNeural, es-CO-GonzaloNeural, es-AR-TomasNeural; femeninas: es-ES-ElviraNeural, es-CO-SalomeNeural, es-MX-DaliaNeural (confirmar cada ShortName en el dropdown). NO está declarado el ID exacto detrás de los canales de referencia: lo replicable es el patrón del nicho (masculino neutro + ritmo alto + receta de dirección §5.4).
- **Chatterbox (Resemble AI)** — MIT · el único open-weights estilo-ElevenLabs elegible; UPGRADE pendiente de verificación en español con voz de referencia PROPIA del dueño + WhisperX para timestamps (condiciones en §7).
- **Google Cloud TTS "Chirp 3: HD" (26-oct-2026):** es-US soportado (Fenrir/Enceladus, masculinas); free tier permanente **1M chars/mes** ($30/1M después de pasarlo); requiere proyecto GCP + clave + cuenta de billing (uso real del canal ≈ 3% del gratis). Sin WordBoundary → karaoke por WhisperX. Estado: **EXCEPCIÓN EN EVALUACIÓN por el dueño (híbrido)**; muestras escuchables SIN clave pegando el guion real del §4.3 en el demo.
- **Riesgo honesto del edge (26-oct-2026):** edge-tts usa el servicio no-oficial de lectura en voz alta de Edge → puede romperse o bloquearse sin aviso; por eso el stack lleva backups en 3 niveles (rotación de voces edge → Kokoro → Piper) y por qué evaluar una capa oficial (GCP) es seria, no capricho.
- **Plan de voz (híbrido, 26-oct-2026):** lanzamiento con es-ES-AlvaroNeural +8% + RECETA §5.4; la voz principal definitiva se elige con muestras + retención real (~2-3 semanas; detalle operativo en Manual del dueño §11).
- Canales citados como referencia del estilo: urumy.academy (Opus 5.5 declarado), @nosolomente en TikTok ("historias contadas con dibujos"); perfiles IG exactos no verificables sin login — la TÉCNICA sí quedó verificada por el ecosistema de arriba, que es lo que importa para producir.

---

*Documento viviente de la fábrica TICO renovado. Cada cambio de contrato pasa por `data/qc/CAMBIOS.md` con fecha y motivo. Última revisión: 26-oct-2026 (se añade §8-BIS MODO NUBE: cerebro Qwen3.5-Small 9B en Colab/Kaggle, capa cerebro en §7, excepción de logins en §10.2).*




