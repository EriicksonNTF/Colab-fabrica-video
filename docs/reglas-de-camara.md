# Reglas de cámara — una toma continua, sin cortes

Deroga §6.5 de `Tico renovado.md`. Es ley para la animación de todo video de este canal; el QC-AV
rechaza el render si algo de aquí falla. Formato: 1080×1920, 30 fps, 45-59 s.

## Principio

Cada video es **un solo mundo dibujado por código** y una **cámara** que lo recorre. Los distintos
elementos del tema no son escenas que se suceden: son zonas del mismo plano que la cámara visita.
No existe en la timeline un instante en el que el cuadro cambie de tema por opacidad.

Implementación: un `#world` de tamaño lógico grande (típico 3200×9000 px CSS) montado dentro de
`#cam`, y la animación **sólo mueve `#cam`** (`x`, `y`, `scale`, `rotate`). Las escenas nunca se
apagan entre sí; lo que entra y sale del cuadro lo decide la cámara.

```
#stage (1080×1920, overflow hidden)
└── #cam            ← la cámara: translate + scale + rotate, única cosa animada globalmente
    └── #world      ← el mundo: zonas Z1/Z2/Z3 repartidas en un plano grande
        ├── .zona-z1, .zona-z2, .zona-z3, .etiqueta, .tco-*
```

## Reglas duras

**C1 — llegar antes que la palabra.** La cámara arriva a la zona en `arrival = t_beat − travel`,
con `travel = clamp(0,35 · Δt_beat, 0,55, 1,30) s`. Cuando la narración nombra algo, eso ya está
centrado y legible. Nunca al revés.

**C2 — continuidad C¹.** La trayectoria se interpola con splines (GSAP `motionPath` o catmull-rom
propio) sobre `(x, y, scale, rotate)` en los tiempos de llegada. Prohibido `set()` de posición y
prohibido `ease: "none"` en un tramo de cámara: una discontinuidad de velocidad se lee como corte.

**C3 — respiración perpetua.** `#cam` siempre tiene un micro-deriva (dos senoides desfasadas,
0,6-1,2 px y 0,15-0,3°, 2-3 Hz, con fase distinta por eje). Ningún fotograma del video es
idéntico al anterior aunque la cámara esté "parada".
**Desvío medido, declarado:** en un cuadro de 1080×1920 con línea de 12 px sobre papel, una deriva de
0,6-1,2 px no se ve y el `Δluma` que produce está por debajo del ruido del códec: el QC la contaba
como congelada igual. `build_comp._deriva()` usa **18-22 px de amplitud con periodos de 5,0 + 3,1 s
(x) y 5,0 + 3,7 s (y)**, que es lo que el píxel registra como respiración. La forma de la regla (dos
senoides, fases distintas por eje, sin `random`) se mantiene; lo que cambió es la escala, y está
justificada por una medición y no por gusto (CAMBIOS #18).

**C4 — el zoom entre niveles es travelling.** Z1→Z2→Z3 es `scale` animada con `power2.inOut`
0,6-1,0 s, no un corte ni un fundido. Si el salto de distancia es grande, la cámara **se aleja
primero** (bajar `scale` 0,85×) y luego entra: así dos zonas comparten el cuadro durante el viaje
y nunca aparece un plano vacío.
**Cómo se cumple en el código:** `viaje_de(c, i)` es la única dueña de la duración del viaje, y la
usan a la vez el tween de `#cam`, el replay de `cam_manifest.jsonl` y el `t0` de entrada de las
piezas (`arrival − viaje − 0,15 + retraso`). La escena se dibuja **mientras** la cámara se acerca;
una pieza no puede aparecer antes o después de su cámara porque las dos salen del mismo número
(CAMBIOS #16).

**C5 — sin transición que corte.** Prohibidos en la timeline global: `opacity` de una zona a 0
mientras otra sube, `visibility`, cualquier bloque de `#stage`, los bloques de transición del
catálogo (`flash-through-white` y compañía) y los `beat-freeze-cut`. El único fundido permitido es
el de salida final de 0,4 s sobre negro (§1.2) y sólo si el video no es bucle.

**C6 — nada aparece teletransportado.** Todo elemento del mundo entra con easing (§6.1) y desde
una posición relativa coherente, aunque ya estuviera "dentro" de la zona: un dato que llega con el
beat se infla desde 0,94 con `power4.out`, no aparece con `set()`.

## Composición y legibilidad (lo que mide el QC)

- **L1** En cada llegada, el encuadre debe estar **llenado por el contenido**: ≥ **78 % del ancho** o
  ≥ **62 % del alto** del cuadro (en vertical, una silueta alta vale tanto como un diagrama ancho).
  Se cumple **al generar** el encuadre: `build_comp.py` deriva la estación de `cam` desde la caja de las
  piezas del beat con esos dos factores (`ANCHO_FOCO` / `ALTO_FOCO`) y un tope de zoom
  `MAX_S = 1,35` (por encima, una pieza chica llena el cuadro y deja de leerse como objeto: se ve
  como una mancha sin contexto). El piso es `MIN_S = 0,30`.
  En el píxel, el QC no puede exigir el mismo número: el estilo es **línea sobre papel**, no mancha
  maciza. Medido sobre el master del 28-oct en la ventana real del QC, los beats bien encuadrados dan
  cobertura 3,6-7,7 % y densidad de foco 7,2-19,7 %. Por eso allá el criterio es "hay contenido real
  y se extiende" (cobertura ≥ **2,5 %** **y** bbox ≥ 55 % ancho o ≥ 45 % alto), más
  **`densidadFoco ≥ 5 %`**: píxel distinto del papel por unidad de área dentro de la caja de pantalla
  que ese beat prometió. Se reporta además `pinturaEnFoco` (qué fracción de todo el dibujo cae dentro
  de esa caja) pero **no corta**: en un mundo continuo siempre hay zonas vecinas fuera, y usarla como
  umbral aprobaba beats mal encuadrados y cortaba buenos (CAMBIOS #17).
- **L2** Ninguna etiqueta entra más de **0,6 s** después de su llegada.
- **L3** Luminancia media del fotograma **≥ 34/255** en las paradas de diagrama.
- **L4** Texto efectivo ≥ **17 px** a 1080×1920 (los tamaños del doc maestro ya cumplen; no bajar).
- **L5** Máximo 3 focos simultáneos dentro del cuadro visible (§6.4), y safe zone: nada de texto
  en los 340 px inferiores ni en los 260 px superiores.
- **L6** Movimiento perpetuo en todo fotograma: deriva de cámara (C3) y un elemento vivo de la
  zona (pulso, partículas, oscilación) — nunca un cuadro muerto.

## Verificación automática

`build_comp.py` emite **dos** archivos que el QC lee, para que el veredicto no dependa de adivinar
la geometría del comp:

- `cam_manifest.jsonl`: un registro por fotograma de cámara (`t`, `x`, `y`, `scale`) reconstruido
  **replayando los tweens de `#cam` que él mismo generó**, con las mismas curvas
  (`power2.out = 1-(1-u)³`, `power2.inOut` cúbica). No es una declaración del guionista: es lo que el
  navegador va a ejecutar.
- `comp_meta.json`: `bandas` (qué franjas del alto son HUD —karaoke, chip— y por lo tanto no son
  dibujo) y `focos` (la caja de pantalla que cada beat promete).

`qc.py` decodifica el MP4 en streaming a **15 fps** (un master de 55 s son 810 cuadros medidos, no
1650 guardados en RAM) y comprueba:

| check | criterio implementado |
|---|---|
| sin cortes | ningún `\|Δluma\|` entre fotogramas consecutivos > **26** |
| sin congelados | no más de 3 fotogramas con `Δluma < 0,05` (C3), **excluida la cola de `FADE_SALIDA = 0,6` s**: el fundido a negro que permite C5 congela el cuadro a propósito y contarlo pondría a las dos reglas a pelearse entre sí |
| C¹ | `\|Δ²scale\|` del manifiesto ≤ **0,008** (medido en S001: 0,0038) |
| contenido real (L1/L3) | en la ventana de cada llegada (0,45-1,45 s después del beat, para no puntuar el último fotograma del viaje): bbox ≥ **55 % ancho o 45 % alto** y, si el comp declaró foco para ese beat, `densidadFoco` ≥ **5 %** dentro de esa caja (la cobertura global se imprime pero no corta, porque un diagrama de una sola línea vertical lo llena el alto y pinta poco píxel); sin caja declarada se vuelve al criterio de cobertura ≥ **2,5 %**. En todo el video, ≤ **45** fotogramas casi vacíos (cov < 1,2 %): medido **0** |
| chip médico | desde 0,5 s después de que entra el chip, el píxel fuera de su caja en la franja `[CHIP_TOP, +92]` debe estar por debajo de **1,5 %** (`MAX_FUGA_CHIP`): si el dibujo se mete debajo del aviso, el aviso deja de leerse |
| técnica | 45-59,9 s · 30 fps · 1080×1920 · yuv420p · ≤ 50 MB · −14 ±1 LUFS · pico ≤ −1,5 dBTP |
| bucle | si `loop: true`, SSIM fotograma 0 vs último ≥ 0,98 — **todavía no implementado** |

Los subtítulos no usan `subs.ass` (CAMBIOS #3): el karaoke vive en `comp.html`, en la franja de
arriba. Si el QC no recibe `--meta`, mide el cuadro completo **incluido el karaoke** y lo deja
escrito como advertencia: así fue como un beat casi vacío dio 1,4 % de "contenido" (CAMBIOS #12).
