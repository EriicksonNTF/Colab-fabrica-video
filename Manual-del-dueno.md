# MANUAL DEL DUEÑO — Modo Nube paso a paso (26-oct-2026)

Guía práctica en lenguaje humano. El documento técnico completo es `Tico renovado.md` (la biblia); este manual te dice QUÉ HACER TÚ cada día. Lo compilado acá fue verificado hoy (27 modelos y tools con licencia y tiempos) — nada inventado.

---

## 1. El sistema en una frase

**Domingo vos creás (Colab, ~45 min) → lunes a sábado GitHub renderiza solo → cada día vos publicas (~10-15 min).** Tu PC no ejecuta nada: solo abre el navegador.

| Tarea | Quién |
|---|---|
| Generar temas, guiones, composiciones | El notebook en Colab (vos corrés 4 celdas) |
| Voz, subtítulos, SFX, render del MP4 | GitHub Action (automático, diario, 8-12 min) |
| Aprobar los 7 guiones del lote | Vos — 10 min, el domingo |
| Descargar el MP4 + mirarlo | Vos — ~2 min/día |
| Publicar a mano en las 4 apps | Vos — ~10 min/día |

Publicar es tu parte por diseño (regla §10.2: sin bots de subida, logins solo de apps oficiales — un bot que toque tus cuentas es riesgo de ban y quedó prohibido por vos).

---

## 2. Setup único (una sola vez en la vida, ~20 min)

1. **Repo en GitHub** (público recomendado): carpeta `data/`, `agente/`, `assets/fonts/` (Nunito OFL), `.github/workflows/render.yml`.
2. **Notebook en Google Drive:** `notebook_cerebro.ipynb` guardado desde Colab. Vive en tu Drive, no en tu PC.
3. **Token de GitHub (único trámite "técnico"):** GitHub → Settings → Developer settings → Personal access token (solo permisos de ese repo) → lo pegás en el candadito de Secrets de Colab. Va encriptado, no queda en el código. El token es parte de tu login GitHub permitido: nada nuevo.
4. Nunca más volvés a hacer esto.

---

## 3. Tu sesión de lote (ancla semanal, por defecto el Domingo)

1. colab.research.google.com → abrís tu notebook → **Entorno de ejecución → Cambiar tipo → T4 GPU**.
2. **"Ejecutar todo"** y dejás trabajar:
   - **Celda 1 (~5 min):** baja tu repo, instala Ollama, descarga el cerebro Qwen 9B (~5 GB). Solo esperás.
   - **Celda 2 (~15-20 min):** genera el lote de 7 slugs: factset (claims+fuentes), guion con 2 ganchos candidatos, composición visual. Te va mostrando tarjetas.
   - **Celda 3 (~2-3 min):** auto-valida TODO: contratos JSON, URLs (código, no el modelo), frases vetadas, muro médico, anti-auto-plagio. Rehace hasta 2 rondas; si sigue mal → rojo + reporte en `data/qc/`.
3. **Tu revisión (~10 min):** mirás las 7 tarjetas (factset + gancho elegido). ¿Alguna huele mal? pedís rehacerla. ¿Todo OK?
4. **Celda 4 (~1 min):** `git push` → los 7 slugs + la cola (`data/cola.txt`) al repo. Cerrás y ya.
5. Cuota de Colab consumida: ~40 min/semana (bajo el límite; por eso casi nunca te niega la GPU).

## 4. La fábrica trabaja mientras dormís

- Cada día a **07:40 ARG / 12:40 ES**, el cron toma el siguiente slug y corre: edge-tts → subtítulos → SFX → render HyperFrames → ensamble FFmpeg → QC técnico → guarda el MP4 como **artifact** + reporte. Vos: cero acciones.
- Activá las **notificaciones por mail de GitHub** una vez, para enterarte si un run falla.

## 5. Recibir el video y publicarlo (~10-15 min/día)

1. github.com → tu repo → **Actions** → el run de arriba (✔ verde) → panel derecho **Artifacts** → bajás `master-SXXX-…` (.zip con `master_final.mp4` + hoja de contacto + QC). *Descargalo el mismo día: los artifacts caducan a los 90 días.*
2. Mirás el MP4 (~1 min): ¿suena bien? ¿chip "Esto no es consejo médico"? ¿los beats?
3. El texto por plataforma (título, descripción, hashtags) vive en `data/published/{slug}.json` (se ve desde la web de GitHub). Copy-paste en TikTok / YT Shorts / IG Reels / FB Reels.
4. Querés re-renderizar algo YA: Actions → `tico-render` → **Run workflow** → escribís el slug → Enter. 10 min.

## 6. Atajo legal para publicar: los programadores nativos (batch 1 vez por semana)

Dentro de tus propias reglas (las 4 apps oficiales, sin bots):

- **Meta Business Suite** → programa IG Reels + FB Reels juntos.
- **YouTube Studio** → programa Shorts.
- **TikTok web (desktop)** → programa hasta 10 días adelante.

**Efecto:** el domingo trasladás los 6 MP4 + textos a los programadores nativos (~30-40 min una vez) → **tu semana diaria queda en 0 pasos de publicación**. Los MP4 descargados y los json tienen que estar a mano en ese momento.

---

## 7. ¿Por qué el domingo y el modo "mismo día"?

| Razón del lote dominguero | Concreto |
|---|---|
| Carga del modelo 1 sola vez | 5 min repartidos entre 7 guiones vs 5 min diarios por 1 |
| Cuota de Colab en zona segura | 1 sesión/sem vs 7 sesiones ("no hay GPU hoy" casi imposible) |
| Colchón | Si falla algo un martes, no pierde el día: hay repuestos |
| Tu semana queda cerrada | 45 min 1 vez; resto solo publicar |

**Modo mismo día (para tendencias o días con ganas):** Colab con 1 slug (~15 min) → Actions → Run workflow con el slug (~10 min) → descargás y publicás. Video de cero a publicado en **~40-60 min**.

**Calendario real:** el lote crea 7, el cron renderiza 6 (lun-sáb); el 7º es el repuesto del colchón (o lo renderizás a mano si querés 7 al aire).

**El video diario promedio:** 60 s, ≤165 palabras, beats HOOK ≤2.5 s → NOMBRE → MECANISMO → DEMO → UTILIDAD → CTA; voz es-ES-Alvaro +8% alternos; chip del nicho; **~3 min de máquina por video medidos en GitHub Actions** (3m11s en `delivery`, 3m54s en `draft`; los "~12-18 min" del plan eran una estimación anterior a la primera corrida), $0.

**¿2 por día?** Posible (2 triggers), pero no recomendado al inicio: las cuentas nuevas lo penalizan. 1 diario constante es lo que crece.

---

## 8. El cerebro (decisión del 26-oct-2026)

**Cerebro: Qwen3.5-Small 9B (Apache-2.0)** vía Ollama (MIT), en la T4 de Colab (~6 GB en 4 bits).
**Por qué:** español natural para edge-tts, cabe con margen (la biblia completa entra en el prompt), el más rápido de los calificados. Alternativas ya documentadas: Ministral 3 14B (plan B), Phi-4 14B MIT (plan B-2), Phi-4-mini 3.8B (plan C). Cambiarlo = 1 línea.
**Trucos de fiabilidad:** salida enmoldeada por JSON-Schema (structured outputs de Ollama) + validador pydantic como muralla 2 + 2 ganchos candidatos + temperaturas 0.2/0.3.
**Fuentes:** las verifica un script (HTTP 200 + frase clave), no el modelo. El detalle técnico completo está en **§8-BIS del doc maestro**.

**Por qué este híbrido y no otra arquitectura (las 3 variantes evaluadas):**
- (A) Todo en Colab, render incluido → 45-90 min/video en la CPU de Colab. Lento y sujeto a la sesión.
- (B) **ELEGIDA:** Colab = creativo + GitHub Actions = render y cron. ~3 min de máquina/video (medido en el runner), cron confiable día de por medio, $0.
- (C) API de modelos premium → DESCARTADA: exige claves/pagos (fuera de las reglas).

---

## 9. Si algo se rompe

- **Colab: "no hay GPU"** → mismo notebook en **Kaggle T4×2** (excepción de logins ya aprobada; Kaggle pide verificación telefónica para internet).
- **Actions en rojo** → log → "Re-run". Persistente: revisa `data/qc/` + escalar (contarme y lo arreglamos).
- **Hugging Face NO elegible** (cuenta extra). Colab/Kaggle: única excepción, solo para el cerebro.

## 10. El Día-1 de construcción (arranque)

Hoy o cuando quieras:
1. Setup del §2 (repo + notebook + token).
2. **Video de prueba SIN cerebro:** el doc maestro ya trae el ejemplo completo `S001-parpado-temblor` (§4/§5) → "Run workflow" en Actions → tu primer video en ~10 min. Estrena la fábrica con su muestra de fábrica.
3. Lote creativo: mismo día (ancla lunes) o dejalo para el domingo. Ambos funcionan — el cron no discrimina desde qué día subís el lote (renderiza lun-sáb).

**Lo que NUNCA harás:** instalar algo en la PC, correr código local, pagar, usar claves de API, bots en redes. Todo lo demás lo automatizamos; el último clic es humano.

---

## 11. El plan de voz (híbrido adoptado el 26-oct-2026)

Elección del dueño: lanzar con la mejor voz Microsoft + la receta del §5.4, y dejar la excepción Chirp 3 HD EN EVALUACIÓN con muestras reales.

- **Voz de lanzamiento:** es-ES-AlvaroNeural +8% con la RECETA (rate por beat), alterno semanal Jorge/Tomas. La voz definitiva se elige con muestras + retención real (~2-3 semanas).
- **Comparar familias HOY sin claves ni cuentas:** en el demo (ttsforfree.com/voice-library/spanish o edge-tts.com) pegá el guion real del slug S001 (está en §4.3 del doc maestro) y escuchá: Microsoft (Alvaro, Alonso, Jorge, Gonzalo, Tomas, Teo, Saul) Y Google (Chirp3-HD-Fenrir, Chirp3-HD-Enceladus). Misma frase, misma velocidad (+12% como en la receta).
- **A/B automatizado (Día-1):** el notebook lleva una celda extra que sintetiza el S001 con las voces Microsoft a sus rates de receta y te baja un zip de MP3.
- **A/B de Chirp automatizado:** SOLO existe cuando esculpás la excepción (cuenta GCP + clave en Secrets de Colab/Actions + billing a $0 + alerta de presupuesto). El free tier es 1M chars/mes permanente: el canal usa ~3%.
- **Criterio de decisión (semana 2-3):** retención 3 s y retención 30 s REALES del canal. Si edge+receta pierde frente a Chirp con el mismo guion → migrás (Chirp principal, edge pasa a backup; Kokoro/Piper quedan de emergencia).
- **Cadena oficial de voz del canal:** principal (Alvaro + receta) → rotación de alternos edge (Jorge/Tomas) → Kokoro em_alex (emergencia offline) → Piper (última raya).

---

*Rutina semanal final: ~1 h 50 min de tu vida = 6 videos al aire + 1 repuesto. Documento técnico: `Tico renovado.md`. Última verificación de fuentes y licencias: 26-oct-2026.*
