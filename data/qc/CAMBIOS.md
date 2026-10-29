# data/qc/CAMBIOS.md — registro de cambios de contrato

Regla del doc maestro: cada cambio de contrato se anota aquí con fecha y motivo.

---

## 2026-10-26 · cuatro cambios aprobados por el dueño

### 1. Se elimina el personaje TICO
**Motivo:** decisión explícita del dueño — «olvidate ya de tico … ya no hay personaje».
**Efecto:** se anulan §2.2 (SVG base), §2.3 (tabla de poses) y la regla «1 accesorio temático por
video» de `Tico renovado.md`. La identidad visual pasa a ser **animación acorde al tema** de cada
video, gobernada por la paleta y las reglas de movimiento (§2.1 tokens y §6), que se conservan.
§2.4 (lenguaje de anatomía Z1/Z2/Z3 y gore cero) **sí se conserva**: sigue siendo la gramática del
nivel de zoom, ahora sin muñeco. El nombre del canal queda en «Cosas raras que tu cuerpo hace,
explico con ciencia»; el repo se llama `fabrica-cuerpo-raro`.

### 2. Cámara continua sin cortes (reemplaza §6.5)
**Motivo:** requisito del dueño — los elementos de cada tema se presentan **dentro de una escena
completa** mediante movimientos de cámara, «sin que haya una transición que corte».
**Efecto:** queda derogada la línea de §6.5 «los match cuts reemplazan la necesidad de moves
complejos: el corte ES la cámara». Nuevo contrato obligatorio, en `docs/reglas-de-camara.md`:
una sola escena-mundo por video, la cámara nunca se detiene en seco (continuidad C¹), los cambios
Z1→Z2→Z3 se hacen **travelling de zoom**, no fundidos ni cortes, y el desenfoque de movimiento o
el retroceso de zoom absorben los saltos largos. §6.1-6.4, 6.6-6.10 siguen vigentes.

### 3. Subtítulos: se conserva el look ya entregado (reemplaza §4.6)
**Motivo:** el dueño eligió explícitamente el subtítulo con **caja de palabra clave**, tal como
salió en `prototipo_codigo.mp4` y en los 10 videos de la serie.
**Efecto:** `subs.ass` de §4.6 deja de ser la fuente del karaoke. El karaoke se genera en
HTML/CSS dentro de `comp.html` desde `timestamps.json`, replicando `pipeline/draw.py:370-412`:
palabra aún no hablada en gris `#7A8699`, palabra hablada en blanco `#ECF0F5` (Inter SemiBold), y
las palabras clave con caja redondeada fondo `#172A42`, contorno `#4A90D9` y **cuatro manijas
circularas en las esquinas**. Fuente: Inter (OFL, en `assets/fonts/`), no Nunito.

### 4. Corrección de dato: el tag del cerebro
**Motivo:** verificación externa del 26-oct-2026 contra la biblioteca de Ollama.
**Efecto:** `qwen3.5-small:9b` **no existe**. Los tags válidos son `qwen3.5:0.8b|2b|4b|9b|27b|35b|122b`.
Se corrige a `qwen3.5:9b` en `notebook_cerebro.ipynb` y en la config del cerebro; el doc maestro
debe actualizarse en §8-bis.1 y §8-bis.7.

---

## 2026-10-26 · tres cambios más, impuestos por el pipeline determinista

### 5. `comp.html` lo escribe el código, no el modelo
**Motivo:** el contrato de HyperFrames (root/timed-clips/una-timeline-pausada, las 12 leyes de
determinismo y el lint `font_family_without_font_face` / `caption_exit_missing_hard_kill`) es
demasiado rígido para que un 9B lo escriba a mano sin romperlo. La regla de oro del §0 ya lo dice:
las REGLAS son el 90 % del trabajo.
**Efecto:** el ANIMADOR (§5.5) entrega el **shot-list** en `script.json → mundo.zonas[].piezas[]`
(qué primitiva, dónde, en qué beat aparece, con qué acento). `agente/build_comp.py` materializa el
SVG y la línea de tiempo. Cambia también §4.3: `beats[].cam` pasa a **opcional** (ver #7).

### 6. Color del subtítulo adaptado a la paleta de papel
**Motivo:** el look del §4.6/CAMBIOS #3 se replicó en HTML, pero sobre crema `#FFF8F1` el texto
blanco `#ECF0F5` de la palabra hablada es invisible.
**Efecto:** la caja de keyword conserva fondo `#172A42` + contorno `#4A90D9` + cuatro manijas
circulares; la palabra aún no hablada queda `#7A8699` y la hablada pasa a **tinta `#161616`**. La
keyword hablada mantiene `#ECF0F5` porque vive dentro de la caja oscura.

### 7. El encuadre se deriva del contenido; `cam` es un override del guionista
**Motivo:** con `cam` declarado a mano por un 9B, la mitad de los beats quedaba con márgenes de
papel vacíos o con el objeto chico en un rincón (falla L1/C5 del QC). `build_comp.py` calcula la
estación desde la caja unión de las primitivas que entran en ese beat (las anotaciones —bandera,
anillo— pueden ensanchar el plano pero no mandarlo) y agranda el mundo para que ningún encuadre se
asome fuera del papel.
**Efecto:** en `script.json`, `beats[].cam` es opcional; si existe, manda (es el modo "paneo pedido
por el guionista", como el DEMO de S001). `agente/validate.py` valida `piezas[]` (id único, tipo del
registro, `p=[x,y]`, `aparece` = índice de beat) y ya no exige `cam`.

### Nota de herramienta (no cambia contrato)
El CI verifica el render con `npx -y hyperframes render --resolution portrait --strict`: **0 errores
de lint**. `master_info.json` informa `picovoz` (la muestra real de la voz, para el TC del QC) y
`rates_por_beat` con la RECETA de §5.4.

---

## Verificado el 2026-10-26 (no cambia el contrato, sostiene las hipótesis del §7)

- `heygen-com/hyperframes`: existe, Apache-2.0, 73 120★. Render = headless Chrome con seek por
  fotograma + FFmpeg ⇒ determinista. Requisitos Node 22+ y FFmpeg.
- GSAP: 100 % gratis desde abr-2025 (Webflow) incluidos plugins; licencia *Standard* propietaria,
  no OSI — la nota de honestidad del §7 se mantiene.
- `greensock/gsap-skills` MIT 17 223★ · `emilkowalski/skills` MIT 50 160★.

---

## 2026-10-26 · cuatro correcciones nacidas de mirar la hoja de contacto (no del QC)

Lección del prototipo, otra vez útil: el QC dio verde en umbrales viejos y el video igual tenía
planos vacíos y banderitas sin texto. **El QC mide; la hoja de contacto juzga.**

### 8. Umbrales del QC recalibrados contra el master real
**Motivo:** `MIN_COVERAGE` y `MIN_W_OR_H` estaban pensados para mancha maciza. El estilo del canal es
**línea sobre papel** (trazo ~12 px + rellenos chicos): la cobertura media medida de un master real
de S001 es **3,6 %**, y un beat legítimo de silueta alta da 46 % de ancho pero 50 % de alto. Con los
umbrales viejos el QC reprobaba encuadres buenos.
**Efecto:** `MIN_COVERAGE = 0,015`, `MIN_W_OR_H = (0,55; 0,45)` (basta con **uno** de los dos ejes),
`MAX_CASI_VACIOS = 45` cuadros a 15 fps ≈ 3 s repartidos de papel suelto. La exigencia de L1 (78 %
de ancho) **se cumplía acá y ahora se cumple al generar**, en `build_comp.py`. No se bajó el estándar:
se movió de lado.

### 9. La caja y la palabra de una bandera entran juntas
**Motivo:** el acento de keyword animaba el rectángulo en `t0+0,55` y el texto en `t0+0,70`. En los
~0,15 s del medio se veía **una cajita vacía**, que en pantalla se lee como error de render.
**Efecto:** los dos tweens arrancan en `t0+0,5`; el rectángulo con `back.out(1.7)` y el texto con
`power2.out` de la misma duración. Regla general que queda: *ninguna anotación puede existir sin su
contenido*.

### 10. `SANGRAN` y tope de zoom `MAX_S = 1,35`
**Motivo:** los anillos de pulso son decoración que a propósito se sale del cuadro; pero entraban en
la caja unión y **achicaban** el plano para "mostrarlos completos", dejando el diagrama chico y
flotando en papel. Y sin tope de zoom, una pieza chica (un parpado) llegaba a `scale` absurdos.
**Efecto:** en `build_comp.py`, `SANGRAN = {"anillo"}` se descuenta del encuadre;
`ANOTACIONES = {"bandera", "anillo"}` **ensancha** la estación héredada si no cabría, pero no la
maneja. Topes `MIN_S = 0,30` / `MAX_S = 1,35`.

### 11. La hoja de contacto muestrea todo el video
**Motivo:** se generaba con `select=mod(n,30)` + `tile=2x3`, así que sus 6 recuadros salían todos de
los **primeros 5 segundos**: el QA visual juzgaba el video entero con el arranque.
**Efecto:** `fps=1/(duración/6),tile=2x3` → un cuadro cada ~9 s, del primero al último. Y el muestreo
de `qc.py` pasó a **streaming por Popen a 15 fps**: del cuadro queda la métrica, no el píxel (la
versión anterior pedía 1650 RGBA y se comía la RAM del runner).

### Datos, no contrato
`script.json` de S001: la zona `circuito` se re-dibujó **vertical** (cerebro arriba, músculo abajo,
señal y factores en columna) porque un circuito horizontal de 2000 unidades dentro de un cuadro
9:16 queda chico en ancho y enorme en vacío; y se borró el `cam` hardcodeado del beat DEMO, que
sobró cuando cambió el layout y hoy violaría CAMBIOS #7. El validator sigue en verde y las 10/10
cámaras son derivadas.

---

## 2026-10-26 · cuatro correcciones de la segunda corrida (la que ya tenía los umbrales nuevos)

La segunda corrida bajó de 6 fallas a 2. Las dos que quedaban **no eran umbrales mal puestos: eran
bugs del QC y del encuadre.** Se arregló la causa, no el número.

### 12. El QC ya no adivina dónde está el karaoke: se lo dice el comp
> El `comp_meta.json` y las bandas siguen vigentes. El umbral **`MIN_DENTRO = 8 %` de esta entrada
> fue derogado por #17** (densidad) y el gate por beat lo refinó **#20**.
**Motivo:** `qc.py` excluía de la medición la banda 60-86 % del alto "porque ahí viven los
subtítulos", pero el karaoke de este canal vive **arriba** (`SUB_TOP = 182`, como `SUB_Y` del
prototipo). Con la banda equivocada pasaban dos cosas a la vez: el **texto del subtítulo se contaba
como si fuera dibujo** (un beat casi vacío marcaba 1,4 % de cobertura) y el diagrama que sí caía en
la franja 60-86 % quedaba **ciego**. Es exactamente la falla que ya había diagnosticado el
prototipo: un QA de píxeles con la geometría mal puesta da verde sobre una escena vacía.
**Efecto:** `build_comp.py` escribe **`comp_meta.json`** con dos cosas que sólo él puede saber:
`bandas` (franjas del HUD, en fracción del alto) y `focos` (la caja de **pantalla** que cada
estación promete, en px). `qc.py` recibe `--meta` y, además de tapar las bandas, exige
`MIN_DENTRO = 8 %` de píxel distinto del papel **dentro de la caja declarada**: prueba "la cámara
está mirando acá", que la cobertura global no puede probar nunca (el dibujo de al lado también
cuenta). Sin `--meta` el QC mide todo el cuadro y lo deja escrito como advertencia.

### 13. Una etiqueta no achica el plano (cierra el CAMBIOS #7)
**Motivo:** en S001 la bandera "ese punto" obligaba a bajar la escala del beat 2 de 1.179 a **0.852**
(−28 % de zoom) para que cupiera un rótulo de diez caracteres. El cuerpo quedó chico y rodeado de
papel: el QC lo aprobaba porque la caja unión seguía "extendiéndose".
**Efecto:** `estacion_de` limita el clamp de las anotaciones a **0.94×** del encuadre primario y
`Comp._acerca_anotaciones` **mueve la etiqueta hacia el centro de la estación** (hasta 6 pasos de
0.7, antes del corrimiento del mundo, para comparar en las mismas unidades) hasta que quepa. El beat
2 de S001 pasó de 0.852 a **1.108**. Regla: *lo que se mueve es la anotación, no el plano*.

### 14. Beat de sólo adorno: la cámara no se mueve
**Motivo:** el beat 8 de S001 tiene una única pieza, un `anillo`, y los anillos están en `SANGRAN`
(se descuentan del encuadre). Al quedarel beat sin `prim` ni `extras`, entraba el fallback sintético
(caja ±620/±420 alrededor del centro de la zona) y el resultado era **un anillo amarillo flotando en
un mar de papel**.
**Efecto:** si un beat no aporta más que adornos que sangran, **hereda la estación del beat
anterior**: el pulso late sobre la escena que ya está encuadrada. Es además coherente con C5/C6
(cero cortes, nada se teletransporta).

### 15. La deriva de cámara es un ciclo, no un tween de 55 s
> **DEROGADO por #18**: el ciclo por keyframes con `sine.inOut` frenaba en cada extremo y producía
> *más* fotogramas congelados, no menos. Vale el diagnóstico de acá, no la solución.
**Motivo:** con un único `to("#drift")` de duración total, el movimiento es tan lento que el pixel no
lo registra: el QC midió **4 fotogramas congelados** (`|Δluma| < 0,05`) y la regla C3 ("ningún
fotograma idéntico al anterior") se cortaba sola.
**Efecto:** `#drift` ahora tiene seis keyframes por eje en un **ciclo de 5 s con `repeat`**
(determinista: nada de `random`, nada de `Date.now`). Mismo contrato C3, ahora medible.

### Herramienta nueva (fuera del pipeline)
`agente/_diag_encuadre.py <carpeta-de-escena>` proyecta las piezas de cada beat contra el cuadro e
imprime qué se supone que debe verse. No lo llama el CI: es la cuenta a mano que encontró las fallas
13 y 14 cuando el QC todavía daba verde.



---

## 2026-10-27 · el QC corregido delata el defecto real (y se arregla la causa)

Con las bandas ya correctas (CAMBIOS #12), la corrida marcó **83 fotogramas casi vacíos, 6 congelados
y 3 beats sin foco**. No eran umbrales: era la película mostrando papel en blanco.

### 16. Las piezas se dibujan DURANTE el viaje de cámara, no al llegar
**Motivo:** cada pieza entraba en `arrival + retraso`. La cámara tarda entre 0,55 y 1,30 s en llegar a
la estación, así que ese segundo y pico el cuadro sólo mostraba la zona de origen y **cruzaba papel
vacío** hasta la de destino: cinco segundos de los 55 son eso. La regla C4 estaba escrita en el doc y
ninguna parte del código la cumplía.
**Efecto:** una sola función, `viaje_de(c, i)` en `agente/build_comp.py`, es la dueña de la duración
del viaje, y la usan a la vez el tween de `#cam`, el replay de `cam_manifest.jsonl` y el `t0` de
entrada de las piezas (`arrival - viaje - 0,15 + retraso`). Una pieza no puede aparecer antes ni
después de su cámara porque las dos cosas salen del mismo número.
**Verificación:** `hyperframes snapshot --at 11,16,25.5,32.5,39` (los cinco cuadros caen a mitad de
viaje) → los cinco tienen diagrama. Antes: cuatro de ellos eran papel.

### 17. El umbral de foco mide densidad, no fracción de pintura
**Motivo:** el primer gate (`MIN_DENTRO = 8 %` del píxel dentro de la caja declarada) cortó beats
legítimos que estaban bien encuadrados y medían 3,7-7,8 %. La métrica preguntaba "¿cuánto de todo el
dibujo cae dentro de la caja?", y en un mundo continuo siempre hay zonas vecinas fuera de ella: la
pregunta estaba mal hecha.
**Efecto:** el QC reporta dos números pero **gatea sólo uno**:
- `pinturaEnFoco` = fracción del píxel total dentro de la caja → informativo, no corta.
- `densidadFoco` = píxel distinto del papel por unidad de área de la caja → `MIN_DENSIDAD = 1,5 %`.
Calibrado sobre el master real: bien encuadrado 3,7-21 %; cámara mirando al otro lado <0,8 %. El
margen entre ambos es de ~5×, así que el umbral no decide casos límite.
También se corrió la ventana de medición de cada beat a `arrival +0,45 … +1,45` para no puntuar el
fotograma exacto en que todavía está terminando el viaje.

---

## 2026-10-27 · tres correcciones sobre la respiracion de camara y el gate por beat

Con el papel vacío ya eliminado (CAMBIOS #16), el QC bajó de 83 fotogramas casi vacíos a **cero** y
de 10 beats revisados a 9 en verde. Lo que quedaba eran tres cosas distintas, y ninguna era un número
mal puesto.

### 18. La deriva son dos senoides, no seis keyframes con easing
**Motivo:** la primera versión de C3 usó `keyframes:{x:[0,18,-14,26,-18,0]}` con `ease:"sine.inOut"`.
Un keyframe con easing **frena hasta velocidad cero en cada extremo**, así que la cámara se detenía
seis veces cada cinco segundos. El pixel lo midió: **13 fotogramas** con `|Δluma| < 0,05` (antes 6).
O sea: para curar los cuadros congelados habíamos puesto un motor que se congela a propósito.
**Efecto:** `_deriva()` (build_comp.py) muestrea en Python la suma de dos senoides de periodos que no
coinciden — 5,0 s + 3,1 s en x, 5,0 s + 3,7 s en y, fases distintas por eje, como pide C3 — y entrega
220 keyframes unidos con `easeEach:"none"`. Los dos extremos de cada eje nunca caen en el mismo
instante, así que la velocidad compuesta no se anula lo bastante tiempo como para congelar un cuadro.
Interpolación lineal a 4 Hz sobre un seno de 5 s: error de posición ~0,3 % de la amplitud.
Sigue determinista (seno de Python en el build; el navegador no calcula nada). El `comp.html` creció
de 51,7 a 54,8 KB.

### 19. El fundido de salida no puede ser a la vez obligatorio y "fotograma congelado"
**Motivo:** C5 permite exactamente un fundido a negro de 0,4 s al final. En el negro, `Δluma` es 0 por
diseño, y el conteo de C3 sumaba esos cuadros: **5 de los 13 congelados eran el cierre**. Dos reglas
del mismo doc se contradecían en el código.
**Efecto:** `FADE_SALIDA = 0,6` s: la cola del video queda excluida del conteo de C3, con el porqué
escrito en el umbral. El resto de la película se mide igual.

### 20. Con caja declarada, mandan la densidad y el bbox; la cobertura global es el proxy debil
**Motivo:** el beat 4 de S001 (`MECANISMO`, la circuito cerebro→músculo) marcó `cov = 1,47 %` contra un
piso de 1,5 %. Miro el fotograma: cerebro, trazo nervioso con sus puntos, músculo y dos rótulos, todo
centrado y legible. Es **un dibujo de una sola línea vertical**: llena el alto del cuadro y pinta poco
píxel. La cobertura global no puede distinguir "diagrama airy" de "papel vacío"; para eso existe la
densidad dentro de la caja que la propia estación prometió, y ese beat medía `densidadFoco = 4,7 %`.
**Efecto:** cuando el comp declaró foco para el beat, el gate pasa a ser
`densidadFoco ≥ 1,5 %` **y** bbox extendido; la cobertura global se imprime pero no corta. Sin caja
declarada sigue el criterio viejo. Lo que custodia el papel vacío no se tocó y ahora es más fuerte:
`≤ 45 fotogramas` con `cov < 1,2 %` en toda la película (medido: **0**).
**Honesto:** esto afloja un gate que había fallado. La justificación no es "el número estaba mal", es
que con la caja y el bbox hay una medición más específica y el promedio de píxel del cuadro entero es
la versión débil de la misma pregunta. Si alguien baja `MAX_CASI_VACIOS` o borra `comp_meta.json`,
este afloje vuelve a ser peligroso.

**Resultado medido (corrida `delivery`, 27-oct 00:31):** veredicto **PASA**, 10/10 beats, 0 fotogramas
casi vacíos, 0 congelados, `|Δ²scale|` 0,00383, densidad de foco 4,5-20,4 %, cobertura media de cuadro
3,1 %, −14,86 LUFS / −1,93 dBTP, 23,6 MB. `hyperframes lint`: 0 errores, 3 avisos de estilo.

---

## 2026-10-27 · se subió el repo y aparecieron dos verdades que faltaban

### 21. El workflow estaba muerto y GitHub no avisaba
**Motivo:** al subir el repo, `git ls-tree origin/main` mostraba los 31 archivos y la API devolvía el
workflow en estado `active`, pero el `name` que reportaba GitHub era la **ruta del archivo** en vez de
`tico-render`. Eso pasa cuando el YAML no parsea. `python -c "import yaml; yaml.safe_load(...)"` lo
confirmó: **error de sintaxis en la línea 59**.
`- run: npx ... || echo "Chrome: lo baja el propio render"` — YAML lee el `: ` dentro del texto como
un mapa. GitHub Actions **no falla el checkout ni avisa por mail**: simplemente el workflow no existe
para el cron. El brazo entero habría estado apagado desde el lunes.
**Efecto:** el `run` va entrecomillado. Validado: parsea, `name: tico-render`, 9 pasos.
**Regla que sale de acá:** `active` en la API **no** significa "parseado". Antes de dar por vivo un
workflow, `yaml.safe_load` sobre el archivo y comparar el `name` que devuelve la API contra el `name:`
del YAML. Si coinciden con la ruta, está roto.

### 22. La hipótesis "en GitHub Actions sí hay `WordBoundary`" quedó refutada
**Motivo:** DIA-1 afirmaba que el karaoke en modo `proporcional` era un límite **de esta PC**, y que
en el runner de Actions edge-tts normalmente entrega las marcas de palabra y la sincronía pasa a ser
medida. Nunca se había probado.
**Efecto:** se corrió el brazo en la nube (run 40619491592, checkout limpio, `--quality delivery` por
default del form, voz regenerada ahí) y el `pipeline_report.json` del artifact dice
`"sync_mode": "proporcional"`. No es un problema local: edge-tts no entrega `WordBoundary` en ninguna
de las dos máquinas. Se borró la promesa de la guía y quedó escrita la refutación.
**Lo que sí cambió entre máquinas:** `|Δ²scale|` medido **0,00383** en local contra **0,00541** en CI.
Distintas duraciones de audio por beat mueven los tiempos de viaje de cámara. Los dos están bajo el
piso de 0,008, y el hecho de que la corrida de la nube **no** heredara el número de la PC es
exactamente lo que se quiere: el manifiesto se recalcula, no se copia.

### 23. "~12-18 min de máquina" era una proyección: medido, son ~3 min
**Motivo:** toda la documentación (biblia §9, Manual del dueño, LEEME, el propio notebook) presuponía
12-18 minutos de GitHub Actions por video. Nunca se había cronometrado. Con el workflow ya vivo se
corrieron dos runs manuales desde checkout limpio.
**Medido:** `delivery` **3 min 11 s** (run 40621193653, master de 26,09 MB) y `draft` **3 min 54 s**
(run 40619491592, 22,87 MB). Los dos **PASA con 0 fallas**, 53,972 s · 1080×1920 · 30 fps · yuv420p,
−14,87 LUFS / −1,88 dBTP, 10/10 cámaras derivadas. Se corrigió Manual, LEEME, DIA-1 y el notebook.
**No se tocó `Tico renovado.md`** (la biblia es documento del dueño, no de la fábrica): su §9 sigue
diciendo 12-18 min y **queda derogado por esta medición**.
**Consecuencia práctica:** el techo de 2000 min/mes de Actions free queda lejos — 6 videos por semana
son ~18 min de runner. Y el dueño puede re-renderizar un slug a las 20:30 y publicar igual.

### 24. El instalador de Ollama deja de usarse: se instala el payload directo
**Motivo:** la celda 1 del notebook moría en Colab con
`CalledProcessError: 'curl -fsSL https://ollama.com/install.sh | sh' returned non-zero exit status 1`.
Se leyó el script (455 líneas) en vez de adivinar. El script ahora intenta primero
`ollama-linux-amd64.tar.zst` (HEAD 200, **1,52 GB**) y deja el `.tgz` como fallback, **pero ese
fallback ya no existe: HEAD 404**. Si el runtime no tiene `zstd`, el script llama a `error()`
—que es `exit 1`— en vez de degradar. Colab trae Python 3.13 y no garantiza `zstd`.
**Efecto:** la celda ya no llama al instalador. Instala `zstd` por apt y descomprime el mismo payload
que el script bajaría (`curl … .tar.zst | zstd -d | tar -xf - -C /usr/local`), que deja
`/usr/local/bin/ollama` + `/usr/local/lib/ollama`. Eso es exactamente lo que el instalador hace por
dentro, **sin** `useradd` ni unidad de systemd (Colab no arranca con systemd; el script lo saltea solo,
pero es código que no necesitamos).
**Además, dos arreglos que salieron del mismo error:**
- `%pip install -U numpy` **se quitó**. Subía numpy a 2.5.4 y rompía `numba 0.61.2` (`numpy<2.3`), que
  es el warning que apareció en el mismo output. El cerebro no usa numpy: `build_comp` sólo importa
  `math`, `json`, `re` y `pathlib`. El que sí usa numpy es `qc.py`, y corre en GitHub Actions.
- La espera del server pasó de `time.sleep(8)` a un sondeo real de `/api/version` hasta 90 s, y si no
  responde imprime `tail -20 /tmp/ollama.log`. Un sleep fijo falla en sesiones lentas sin decir por qué.

### 25. El token ya no bloquea el clon: el repo es público y el assert mentía
**Motivo:** segundo error en Colab, ahora en la celda 1:
`AssertionError: falta el secret GH_TOKEN en Colab`. Tres cosas distintas se tapaban entre sí:
1. `google.colab.userdata.get()` **devuelve `None`** cuando el secret no existe; no lanza. El
   `try/except` que había no atrapaba nada y el `assert` sí. El mensaje culpaba al token cuando el
   problema real podía ser que el secret nunca se creó o que no se le dio *Acceso del notebook*.
2. El repo es **público**: `git ls-remote https://github.com/EriicksonNTF/Colab-fabrica-video.git`
   devuelve `refs/heads/main` sin credenciales. O sea, **el clon nunca necesitó el token**; sólo el
   `push` de la celda 4 lo necesita. Exigirlo antes del clon bloqueaba 25 min de trabajo por un
   requisito que no existía en ese punto.
3. El token se escribía en la URL del `clone` con `check=True`; si el clone fallaba, el traceback de
   Python imprimía el comando **con el token adentro**.
**Efecto:** la celda 1 ahora (a) clona en anónimo y sólo tokeniza el remoto si hay token, (b) si no
hay secret lo pide con `getpass` —no se imprime en pantalla, no queda en el `.ipynb`, no va al
historial—, (c) valida el token contra `GET /api/v3/repos/...` y exige `permissions.push` **antes** de
bajar el cerebro, (d) todo `git` pasa por `_git()`, que captura la salida: el token nunca aparece en
un traceback.
**Regla que sale de acá:** un `assert` sobre un valor de API opcional tiene que decir *qué* falta y
*cómo se arregla*. `userdata.get()` sin excepción + `assert` produce un error que acusa al usuario de
algo que puede no haber hecho mal.

### 26. `set(vetadas)` reventaba: las vetadas son objetos, no ids
**Motivo:** la celda 2 moría con `TypeError: unhashable type: 'dict'` en
`VETADAS = set(IDEAS.get("vetadas", []))`. El canon §4.1 define cada vetada como
`{titulo, razon, vetada_por}` — un objeto — y los objetos no son hashables. Peor: el filtro comparaba
`i["id"] not in VETADAS`, y **las vetadas no llevan `id`**. Aunque el `set` hubiera funcionado, no
habría vetado nunca nada: el defecto era silencioso en su efecto y ruidoso en su síntoma.
**Efecto:** se normaliza el texto (minúsculas, espacios colapsados) y se compara contra `id`, `hook`,
`fenomeno` y `mito_a_corregir` de cada idea. Cuando una idea queda fuera se imprime
`salteadas por estar vetadas: I0xx`, porque antes el SKIP del §7-2 era invisible.
**Verificado con `data/ideas.json` real:** 0 salteadas, 4 candidatas (I015 9, I016 9, I017 8, I018 7).
Con una vetada de prueba igual al hook de I017: saltea I017 y quedan 3.

### 27. La primera corrida real del cerebro: 4 slugs caídos, el push rechazado y la voz sin loop
**Motivo:** primera corrida completa de la notebook en Colab (29-oct-2026). Tres fallas distintas:

1. **Celda 2 · `[salto] I015..I018: Expecting value: line 1 column 1 (char 0)`.** Ese mensaje es
   `json.loads("")`: el modelo devolvió `content` vacío. La causa es el *thinking*: `qwen3.5:9b` es
   un modelo que razona, y Ollama manda ese razonamiento por `message.thinking`; con
   `num_predict: 4096` los 4096 tokens se iban en pensar y `content` llegaba vacío. Además `num_ctx`
   quedaba en el default (4096) y los prompts §5.x + el contrato no entran cómodos ahí.
   **Efecto:** `contratar()` ahora pide `think=False` (con fallback `TypeError` para clientes viejos
   que no conocen el parámetro), sube a `num_ctx: 8192` / `num_predict: 6144`, y si igual llega
   vacío reintenta una vez con `/no_think`. El error ya no es `Expecting value`: `_json_txt()` dice
   cuántos caracteres llegaron y muestra el arranque de la respuesta.
2. **Celda 4 · `! [rejected] ... the remote contains work that you do not have locally`.** El clon de
   Colab es `--depth 1` y se hizo antes de los commits de los parches 25-26, así que su `main` estaba
   atrás. **Efecto:** la celda 4 hace `git pull --rebase --autostash origin main` antes del push y
   termina imprimiendo `git log --oneline -2`, para que se vea si quedó arriba o no.
3. **Celda 5 · `asyncio.run() cannot be called from a running event loop` en las 7 voces, y el zip
   salió vacío.** `voice.build()` llamaba `asyncio.run(synth_clip(...))` dentro del bucle de beats, y
   el kernel de Colab ya tiene un event loop corriendo. En CI no se notó porque ahí no hay loop.
   **Efecto:** `voice._run_async()` corre el coroutine en un thread propio con su loop cuando ya hay
   uno activo, y sigue usando `asyncio.run` cuando no lo hay (CI). Probado en los dos caminos, y con
   una excepción dentro del coroutine: se re-lanza en el hilo principal. La celda 5 además hace
   `importlib.reload(V)` (un kernel que ya importó `voice.py` sigue usando el módulo viejo) y falla
   con un mensaje claro si ningún mp3 se generó, en vez de escribir un zip vacío.

**Lo que NO es un error:** el `2566` al final de la celda 2 es el valor de retorno de
`Path.write_text()` (cantidad de caracteres), que el notebook muestra como salida de la celda.

**Ninguna de las celdas produce un MP4.** La notebook solo escribe `data/` y hace push; el video lo
hace GitHub Actions (`tico-render`). Con la celda 2 caída no hubo slug nuevo y por eso no había nada
para ver.

### 28. El ANIMADOR cortaba el JSON: el prompt se comía el contexto
**Motivo:** con `contratar` ya arreglado (entrada 27), la celda 3 avanzó de verdad y murió en
`json.loads` con `Expecting ',' delimiter: line 169 column 8 (char 4796)` durante un reintento de
S016. Ese corte mide 4 796 caracteres, o sea ~1 400 tokens: no es `num_predict` (6 144). Es el
**contexto**: `num_ctx: 8192` y el prompt del ANIMADOR —personalidad §5.5 + contrato §4.3 completo +
todos los beats del guion— se lo comía casi entero; al modelo le quedaba poco margen y Ollama cortaba
la salida con `done_reason=length`. El síntoma no es "falta memoria": es un JSON a medio escribir
cuya primera falta es una coma, que fue exactamente el error.
**Efecto:** `NUM_CTX` pasa a **16 384** por defecto (configurable con la env `NUM_CTX`; en T4 el 9B Q4
+ 16k de KV entra en ~9 GB de 16). `contratar()` ahora **repara antes de rendirse**: `_cerrar()`
genera tres candidatos —quitar la coma final y cerrar lo abierto, recortar a la última estructura
completa, recortar a la última coma— y el que parsee gana; el caso 3 (último miembro a medio escribir)
es el que se veía. Si ninguno parsea, reintenta **una** vez a temperatura 0 pidiendo el JSON cerrado
y con la instrucción explícita de usar menos zonas/piezas antes que cortar. El error final incluye
`done_reason` y la cola del texto, así que la próxima vez se sabe si fue longitud o formato.
**Honesto:** reparar puede devolver un JSON válido pero **incompleto** (por ejemplo, sin la última
zona). Eso no se acepta por fe: los validadores de la celda 3 (`zona inexistente`, `piezas`, §6.9) son
los que deciden, y un slug reparado que perdió piezas queda `BLOQUEADO` con el motivo escrito.

### 29. La celda 3 se llevaba puesto el lote entero al primer slug roto
**Motivo:** el `JSONDecodeError` de S016 cortó la celda 3 en el bucle de reintentos: los slugs que
venían después no se validaron aunque ya estaban generados en memoria.
**Efecto:** cada slug va en su propio `try/except`; si explota, queda `BLOQUEADO (excepcion)` en
`data/qc/{slug}.md` con el mensaje y el bucle sigue. Un slug roto deja de costar el lote completo.

### 30. El ANIMADOR inventaba el mundo: zonas propias, `aparece` en segundos y tipos que no existen
**Motivo:** S016 (el único slug que llegó a escribirse en la corrida del 29-oct) quedó `BLOQUEADO` con
53 fallas del validador. Leídas juntas, son tres desobediencias del contrato, no tres bugs:
- **Zonas**: los beats apuntan a `ojo, silueta, circuito, calma, teaser` (lo que eligió el GUIONISTA en
  su campo `zona`), pero el ANIMADOR creó `zona_hook, zona_nombre, zona_mecanismo...`. El validador
  compara el id literal, así que fallan **todos** los beats.
- **`aparece`**: el prompt dice "beat", el modelo escribió **segundos** (0.2, 2.5, 15.2, 45.0) y el
  validador exige un entero 0..8.
- **Tipos**: usó `tico` y `flash`, que no están en `REGISTRO` (12 primitivas). `tico` viene de la
  personalidad §5.5, escrita para el personaje que ya no existe: el prompt dice "solo el registro"
  pero el texto largo de la biblia lo contradice.
Además: 3 URLs que devuelven 403/404 y un guion fuera de la ventana de 60 s. Eso es del INVESTIGADOR
y del GUIONISTA; el validador los caza y por eso reintenta.
**Efecto en `animador()`:** los tres datos van literales y sin ambigüedad en el prompt — la lista
exacta de ids de zona que el mundo debe tener (ni una más), una tabla de beats con `i`, `tipo`, `zona`
y `visual`, el vocabulario cerrado, y la prohibición explícita de `tico/flash/particula/personaje/flecha`
con la alternativa correcta para cada caso (pulso→`anillo`, etiqueta→`bandera` con `texto`, palabra→
`texto`). `aparece` se declara ENTERO 0..n-1 y se aclara que `t` es solo informativo.
**Efecto en `slug_de()`:** el slug salía de cortar a 34 caracteres a mitad de palabra:
`S016-hipn-gogica-mioclon-a-al-`, con guion colgando. Ahora se normaliza (sin acentos), se cortan
palabras enteras (máx. 5, ~38 chars) y se descartan preposiciones finales:
`S016-sacudida-hipnagogica-mioclonia`. El prefijo `S{id}` sigue garantizando unicidad.
**Efecto en el workflow:** cuando el slug no existe, además del `::error::` ahora hace `ls data/escenas/`
y lista los válidos. El error se produjo por escribir a mano un slug de ejemplo que no existía.
**Honesto:** esto es un arreglo de prompt, verificado en sintaxis y en los datos observados, **no
todavía de punta a punta**. Un 9B puede volver a desobedecer; la red de seguridad es la celda 3, que
deja el slug `BLOQUEADO` con el motivo escrito en vez de renderizar algo mal.

---

## 2026-10-28 · la corrida rechazada: recomposición completa y siete defectos medidos

El dueño rechazó el master de S001 con tres frases: *«la única imagen que quedó gráficamente bien
fue la primera»*, *«la voz tomó una genérica»*, *«los subtítulos no están saliendo tan bien como
salían antes»*. Las tres tenían causa concreta; esto es lo que se cambió.

### 31. El mundo crecía de más y la cámara retrocedía entre beats (raíz de «solo la primera»)
**Motivo:** la cascada `_despeja()` empujaba cada pieza hasta despejar **cualquier** pieza del mundo,
incluidas las de beats posteriores: 14 piezas apiladas dejaban el mundo en 11.687 px y estaciones no
monótonas (la del beat 6 caía *arriba* de la del 4). La cámara tenía que retroceder y el monitor del
beat 5 se metía en el beat 9.
**Efecto:** `_despeja()`/`_mueve()` se reemplazan por `_apila()` (apila solo piezas del MISMO beat) y
`_separa_bloques()` (240 unidades fijas entre bloques, en orden). Estaciones monótonas:
1400→3150→4595→5793→6901→7925→9132→9381→10349. `aceleracion_max` bajó a 0,0034.

### 32. Las piezas del beat anterior seguían vivas en la franja del karaoke
**Motivo:** en el master del 27-oct se leían «0 1 2 3 4 5 6 7» del beat 6 tres beats después, y los
títulos de las fichas asomaban bajo el velo. El velo llegaba al 62 % de 366 px y las piezas nunca
salían.
**Efecto:** `#velo` es sólido hasta el 92 % de 332 px y `Comp.salida(i)` funde cada pieza a 0 durante
el viaje de cámara hacia el siguiente beat dibujado (0,5 s, `power1.in`). Nada heredado sobrevive.

### 33. La bandera SEÑAL ELÉCTRICA tapaba su propio rótulo
**Motivo:** la bandera traía coordenadas fijas del 27-oct; al normalizar el circuito (`anclas_circuito`)
el punto rojo quedó **encima** de «sistema nervioso» y el hilo cruzaba el texto (s14). Además, el par
cerebro-músculo casi horizontal (560 a 35°) medía 766×652: al encajarlo por ancho quedaba en **30 %
del alto** con papel vacío arriba y abajo.
**Efecto:** el par va a 740 unidades y ~53° (bloque 755×1.060, entra en 78 % de ancho y 62 % de alto);
los tres cables son **paralelos** con tangente horizontal (el abanico anterior se cruzaba en el medio
y parecía una cuerda), y «orbicular» pasa debajo del músculo. `bandera.ancla="senal"` ancla la
etiqueta en el nodo azul de salida del cerebro, y `_ubica_bandera` conserva el lado declarado con
tolerancia de 0,6 (antes el flip por 0,04 invertía banderas que estaban bien).

### 34. Fichas: tarjetas chicas con huecos enormes y título desbordado
**Motivo:** cuatro fichas en fila se apilaban con `GAP_V=170` entre tarjetas de 150 de alto: el
bloque medía 1.170 unidades, la cámara bajaba a 0,73 y las tarjetas quedaban en 293×110 px.
«menos caféina» se salía de la tarjeta y el badge de 44 se le montaba encima.
**Efecto:** `GAP_V=100` (bloque de 930 → escala 0,89), título con auto-ajuste (0,56 em/char, tope
`w-110`), título centrado cuando la ficha no tiene nota, badge r=36 y alto máximo 150 para fichas
de una sola palabra.

### 35. El chip médico tapaba la última ficha; el anillo dorado no se veía
**Motivo:** el aviso «Esto no es consejo médico» (franja 1246-1338) se dibujaba sobre la tarjeta
«pausas» del beat 8, y el anillo dorado del beat 8 latía invisible: `Comp.g()` deja el grupo padre en
`opacity=0` y `p_anillo` solo animaba los hijos.
**Efecto:** `_deja_sitio_al_chip()` encaja el bloque heredado entre la franja del karaoke y el chip
(beat 8: escala 0,892, bloque 355-1.131, chip debajo) y `p_anillo` hace `tl.set(grupo, opacity:1)`.
También se corrigió el óvalo del músculo: `opacity=0.2` apagaba relleno **y** contorno; ahora es
`fill-opacity` y el contorno rojo se ve.

### 36. Los subtítulos perdieron las marcas de palabra (regresión real, no percepción)
**Motivo:** `edge-tts` 7.x cambió el valor por defecto de `boundary` a **`SentenceBoundary`**. Nuestro
`synth_clip()` nunca lo pasaba, así que no llegaba **ni una** `WordBoundary`: `timestamps.json` caía
a `sync_mode: proporcional` (reparto por caracteres) y la caja azul se adelantaba o atrasaba hasta
medio segundo. El audio se oía bien, por eso no se había visto.
**Efecto:** `Communicate(..., boundary="WordBoundary")`. Verificado: la misma frase devuelve 7 marcas
con `offset`/`duration`. El build además **falla** si dos líneas de karaoke se solapan o si una palabra
empieza fuera de su grupo (`grupos()`), y si el foco declarado nace bajo el karaoke o bajo el chip.

### 37. Voz «genérica»: era castellano de España y plana entre beats
**Motivo:** `es-ES-AlvaroNeural` para un guion latinoamericano, con un solo rate por tipo (tres NOMBRE
seguidos sonaban idénticos).
**Efecto:** voz de lanzamiento `es-MX-JorgeNeural`; `PITCH_BY_TIPO` suma un cuarto de tono en HOOK y
baja dos hercios en UTILIDAD. El A/B de la celda 5 ahora compara **voces latinoamericanas**
(es-MX, es-AR, es-CO, es-CL, es-US) y no siete castellanas.
**Pendiente honesto:** el clon de la voz del dueño no está implementado. Clonar una voz ajena sigue
prohibido; clonar la propia es posible (OpenVoice v2, MIT) pero es una fase aparte y sin probar.

### 38. El QC no distinguía una escena vacía de una llena
**Motivo:** con `MIN_DENSIDAD=1,5 %` pasaban los beats 3 y 4 del 27-oct, que estaban al 1,5-1,6 %.
**Efecto:** medido sobre S001 recompuesto a 540×960 (mismo filtro del QC), la densidad del foco va de
**7,2 % a 19,7 %** y la cobertura de 3,6 % a 7,7 % en las llegadas. Nuevos umbrales:
`MIN_COVERAGE=2,5 %`, `MIN_DENSIDAD=5 %`, y `MAX_FUGA_CHIP=1,5 %` (dibujo bajo el chip fuera de su
caja, medido en píxel, solo desde que el chip está visible).

### 39. Voz propia: el camino ya existe y estaba roto
**Motivo:** `run_pipeline.py --reuse-voz` reescribia `script_render.json` desde `script.json`, que no
lleva `t_real`: el comp quedaba armado sobre los tiempos nominales mientras el `voz.wav` que suena es
el real. Nadie lo noto porque la bandera nunca se uso en el cron.
**Efecto:** con `--reuse-voz` se parte de `script_render.json` (el que tiene `t_real`) y se exige
`voz.wav`. El workflow suma el input `voz: edge | propia`; con `propia` pasa `--reuse-voz`. Asi se
puede dejar en el repo una voz generada fuera de edge (clon propio, grabacion) con sus
`timestamps.json` y el render la respeta.

### 40. El notebook seguia ofreciendo siete voces castellanas
**Motivo:** el A/B de la celda 5 era todo es-ES; elegir ahi garantizaba el mismo problema del 27-oct.
**Efecto:** `VOCES_AB` pasa a es-MX-Jorge (lanzamiento), es-AR-Tomas, es-CO-Gonzalo, es-CL-Lorenzo,
es-PE-Alex, es-US-Alonso y es-ES-Alvaro como control. Los prompts del GUIONISTA y del ANIMADOR ahora
exigen tildes y enie en todo texto visible: `validate.py` ya rechaza la palabra sin tilde
(`senal -> señal`, `parpado -> párpado`, ...), asi que el guion no llega al render mal escrito.

### 41. La doctrina de camara quedo desactualizada respecto del QC
**Efecto:** `docs/reglas-de-camara.md` documenta los umbrales reales (`MIN_COVERAGE=2,5 %`,
`MIN_DENSIDAD=5 %`, `MAX_FUGA_CHIP=1,5 %`) y el `Manual-del-dueno.md` §11 pasa a voz latina de
lanzamiento, con el estado honesto del clon propio (fase aparte, OpenVoice v2 MIT, sin marcas por
palabra, XTTS-v2 descartada por licencia no comercial).

### 42. Los tres cables del circuito se trenzaban y los nodos volaban fuera del trazo
**Motivo:** el desplazamiento entre cables era (30, -34) fijo, no perpendicular a la diagonal
cerebro->musculo: los tres se acercaban en el medio y se cruzaban al llegar al musculo (s13 del
master del 28-oct). Ademas los nodos viajaban de `(x0,y0)` a `(x1,y1)` en linea recta, con el cable
curvo: el punto azul flotaba al costado.
**Efecto:** offset perpendicular `(-dy, dx)/|v|` para arranque, controles y llegada; el nodo recorre la
cubica con 12 keyframes de `attr cx/cy` (sin plugin de motion path). Quedan tres trazos paralelos y el
punto siempre sobre el cable.

### 43. El karaoke se corria una palabra por beat desde el beat 1
**Motivo:** `reparte_palabras` consumia una palabra del TTS por cada token del guion. La raya del
guion ("—") no se pronuncia, pero gastaba una palabra: desde ahi cada beat arrancaba corrido y se
leia "que no obedece La buena casi" (s32) o "cafeina y pausas de Y no de magnesio" (s37), con
mayusculas en mitad de la linea. El tope de 4 palabras de lookahead no alcanzaba a corregirlo.
**Efecto:** los tokens sin letras se saltean; si el TTS no devolvio una palabra, se interpola su
tiempo entre vecinas (`sintetica: True`) en vez de robarle la palabra al beat siguiente. Verificado:
los 10 beats reparten 11/11/7/8/19/12/12/16/14/17 palabras y ninguna linea mezcla dos beats.

### 44. La mano del CTA era una manopla
**Motivo:** el path del 27-oct tenia cuatro bultos sin pulgar y el canto derecho inflado; con las
arrugas arrancando en y=-150 cruzaban los valles de los dedos.
**Efecto:** palma con cuatro dedos de punta redondeada, pulgar saliendo del canto izquierdo y las
cinco arrugas dentro de la palma (y=-40 a +112).

### 45. El master no llegaba a -14 LUFS con picos bajo -1,5
**Motivo:** la voz tiene ~17 dB de cresta. Una pasada lineal de loudnorm solo podia aplicar +0,2 dB
antes de tocar el techo de TP: el master del 28-oct salio -15,86 LUFS y el QC lo rechazo.
**Efecto:** `mezclar_audio` hace loudnorm dinamico dos veces, mide, aplica la ganancia que falta con
`alimiter` (-3,1 dBFS de muestra) y repite la correccion hasta 3 veces. Medido: **-14,5 LUFS / TP
-2,10 dB / LRA 3,3** en el master final, dentro del gate.

### 46. El beat 8 no tenía escena: 6,8 s con las fichas del beat 7
**Motivo:** el beat "si se prolonga..." solo llevaba un `anillo` decorativo. Los anillos son
anotaciones, así que no abrían bloque ni disparaban la salida del beat anterior: las cuatro fichas
seguían en pantalla hasta el CTA mientras la voz hablaba de acudir a un profesional, y el aro
ámbar quedaba cortado en el borde.
**Efecto:** `p_ojo` acepta `caida`: un párpado recortado por la esclerótica que baja con la palabra
"cierra" (`t_beat + 1,2 s`) y se detiene sobre la pupila, dejando el iris visible. El beat 8 ahora
tiene ojo propio en [1600, 8200] con aros ámbar de atención: la cámara lo encuadra a 1,30 y las
fichas se retiran al llegar. El bloque se separa solo del beat 7 y del CTA.
### 47. El viaje al CTA dejaba un segundo de papel vacío
**Motivo:** la salida de cada bloque arrancaba justo cuando el siguiente empezaba a dibujarse; en el
viaje largo del beat 8 al CTA (43,2 a 49,3) eso dejaba el ojo borrado y la mano todavía por debajo
del cuadro: 0,9 s de papel casi vacío a 48,0-49,2.
**Efecto:** la salida espera 0,4 s más, así el bloque que se va cruza durante el paneo con el que
llega. Medido en previas: a 48,3 el ojo sigue en cuadro mientras la mano se dibuja abajo y a 16,6
o 25,4 el bloque anterior se ve al 20-25 % en el borde, como fundido, nunca encima del karaoke.
