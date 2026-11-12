---
name: gbo-video
description: Flujo de edición de video agéntico con buen gusto, de guion a render final (verticales para Reels/TikTok/Shorts y long form de YouTube). Úsala siempre que se edite, corte, transcriba, subtitule, reencuadre, anime, renderice o revise un video, cuando se arme un brief o guion de grabación, y cuando se escriba o revise el guion de un video para agregarle un plan de producción (tomas, ángulos, B-roll, pickups), aunque el guion venga de otro sistema.
---

# gbo-video — flujo de edición de video

Esta skill define el **método**: fases, checkpoints, criterio estético y herramientas. Lo
personal de cada creador (marca, glosario propio, equipo, carpetas, integraciones, aprendizajes)
vive en su **perfil local**, fuera de la skill.

## Antes de empezar: perfil y primer uso

**1. Cargar el perfil local.** Ruta: variable de entorno `GBO_VIDEO_PROFILE` o, si no existe,
`~/.config/gbo-video/`. Leer `perfil.md` y usar el resto de sus archivos así:

| Archivo del perfil | Relación con la skill |
|---|---|
| `marca.md` | Reemplaza los valores de ejemplo de `references/marca.md` |
| `glosario.md` | Se **suma** a `references/glosario.md` |
| `estilo.md` | Sobrescribe o amplía reglas puntuales de `references/estilo.md` |
| `aprendizajes.md` | Registro de cada video (fase 9) |

Si no hay perfil: ofrecer crearlo desde `templates/perfil.md` (y, si el creador quiere,
`references/marca.md` y `templates/aprendizajes.md`), preguntando en UNA tanda lo mínimo
(nombre, idioma, equipo, raíz de proyectos). Sin perfil se puede trabajar igual con los
valores por defecto; decirlo en una línea.

**2. Verificar dependencias antes de la fase 3** (una vez por sesión, en silencio si todo está):
- ffmpeg con libass y drawtext (`ffmpeg -filters | grep -E "subtitles|drawtext"`; en macOS,
  Homebrew `ffmpeg-full`, que es keg-only).
- video-use clonado (`VIDEO_USE_DIR` o `~/Developer/video-use`) con
  `helpers/transcribe_local.py` presente (copia en `vendor/video-use/helpers/` de esta skill).
- mlx-whisper instalado en el entorno de video-use (Apple Silicon).
- Para la fase 7: Node 20+ y la copia de trabajo de `remotion/` (ver `references/remotion.md`).

Si falta algo: decir qué falta, proponer los pasos exactos de `SETUP.md` y **pedir permiso
antes de instalar**. Nunca instalar en silencio.

## Referencias (leer según la fase)
- `references/estilo.md` — reglas estéticas: ritmo, cortes, zooms, captions, SFX, música, voz, color
- `references/glosario.md` — corrección de términos técnicos en la transcripción
- `references/plataformas.md` — especificaciones de salida, loudness, zonas seguras, reencuadre
- `references/marca.md` — qué tokens de marca necesita el video y cómo sincronizarlos
- `references/remotion.md` — plantilla `remotion/`, motion graphics, thumbnail y portada
- `references/plan-produccion.md` — modo plan de producción (apoyo a la guionización)
- `references/frameback.md` — revisión opcional con Frameback

Plantillas: `templates/brief.md`, `templates/guion.md`, `templates/publicacion.md`,
`templates/perfil.md`, `templates/aprendizajes.md`.

## Principios

1. **Historia antes que formato.** Brief y guion preceden a la edición. Si no hay guion, se hace "guion reverso" desde la transcripción (fase 5).
2. **Bien hecho y sutil.** Cada zoom, sonido o animación necesita una razón narrativa. Ante la duda, no se pone.
3. **El audio manda.** Los cortes caen en límites de palabra o silencio.
4. **El agente no ve la calidad visual.** Foco, exposición, encuadre y B-roll silencioso los valida el creador.
5. **Iteración barata.** Checkpoints (⏸) antes de cualquier render final; previews en baja resolución.
6. **Los originales no se tocan.** Todo output va a `edit/`.

## Guion externo y guion congelado

La skill funciona sola (brief y guion con sus plantillas) o junto a un sistema de guionización
externo que el perfil declare (por ejemplo, [FARO](https://github.com/guillebecerrao/faro)).
- **Al guionizar en un sistema externo:** ese sistema puede invocar esta skill en modo plan de
  producción (`references/plan-produccion.md`) para anexar tomas, ángulos y pickups al guion.
  El guion vive en el sistema externo.
- **Al pasar a edición, el guion se congela:** copiarlo a la carpeta del video como
  `guion_snapshot.md`, con frontmatter `fuente: <ruta de origen>`, `version:` y `snapshot: <fecha>`.
  La edición trabaja sobre el snapshot; la fuente de verdad sigue en el sistema externo. Si el
  guion cambia después de grabar, se toma un snapshot nuevo; nunca se edita a mano.
- Así una máquina dedicada a procesar video no necesita el sistema de guionización instalado.

## Arranque de un proyecto nuevo

Cuando el creador diga "nuevo video", "video nuevo con gbo-video" o describa una idea para grabar:

1. **Ubicación:** crear el proyecto dentro de la carpeta donde está abierto Claude Code o en la
   raíz de proyectos del perfil. Si la carpeta actual ya parece un proyecto (tiene `brief.md`,
   `guion_snapshot.md` o `raw/`), preguntar antes de crear otro dentro.
2. **Slug:** `YYYY-MM-DD_slug-corto` con la fecha de hoy y 2–4 palabras del tema, en minúsculas y sin tildes. Proponerlo y aceptar el que prefiera el creador.
3. **Estructura:** crear `brief.md`, `raw/` y `edit/`. No crear `guion.md` hasta que el brief esté aprobado.
4. **Brief:** copiar `templates/brief.md` y llenarlo con lo que el creador ya dijo. Preguntar en UNA sola tanda solo lo que falte (plataforma, ángulo STORY/VALUE, duración, CTA). Proponer valores por defecto razonables en vez de dejar campos vacíos.
5. **Guion:** con el brief aprobado, redactar `guion.md` desde `templates/guion.md` (o pedir el guion del sistema externo). Sugerir leerlo en voz alta e iterar hasta que suene natural. ⏸ Aprobación antes de grabar.
6. **Retomar:** si el creador vuelve a un proyecto existente, leer `brief.md`, el guion y `edit/` para deducir en qué fase está y decírselo en una línea antes de continuar.

Si llega material ya grabado sin brief: crear la carpeta igual, pedir que deje los archivos en `raw/` (no moverlos sin permiso) y hacer un brief mínimo + guion reverso (fase 5).

## Flujo estándar

| Fase | Qué se hace | Output | Checkpoint |
|---|---|---|---|
| 0. Brief | Objetivo, plataforma, ángulo (STORY/VALUE), duración, CTA | `brief.md` | — |
| 1. Guion | Plantilla `templates/guion.md` + plan de producción | `guion.md` o `guion_snapshot.md` | El creador aprueba |
| 2. Grabación | Checklist de grabación (en la plantilla de guion); guion legible en teleprompter si el creador lo usa | `raw/` | — |
| 3. Ingesta | Inventario de tomas + checklist de ingesta (abajo); proxies si pesa mucho | `edit/inventario.md` | ⏸ Si hay HDR/log o espejo, antes/después al creador |
| 4. Transcripción | Whisper large-v3-turbo local (mlx-whisper, idioma forzado, glosario como `--prompt`), timestamps por palabra; luego pasada de corrección con el glosario (corrige texto, nunca timestamps) | transcript + `edit/correcciones.md` | ⏸ El creador revisa correcciones |
| 5. Estrategia de corte | Comparar guion vs. transcript (o guion reverso); elegir tomas; proponer corte con timestamps | `edit/estrategia.md` | ⏸ El creador aprueba |
| 6. Corte y pulido | video-use + ffmpeg según `references/estilo.md` | preview | ⏸ El creador revisa preview |
| 7. Motion (opcional) | Sincronizar marca (`references/marca.md`), luego Remotion: captions, títulos, lower thirds, paneles | composición | ⏸ |
| 8. Render y QA | Checklist QA (abajo) + `references/plataformas.md` | `edit/final_<plataforma>_v1.mp4` (ver Versionado) | ⏸ |
| 8.5 Publicación | Textos por plataforma desde `templates/publicacion.md`, basados en el corte final; thumbnail/portada según `references/remotion.md` | `publicacion.md` + `edit/thumbnail/` | ⏸ El creador aprueba textos y thumbnail |
| 9. Retro | Qué funcionó, qué corrigió el creador | entrada en `<perfil>/aprendizajes.md` | El creador aprueba cambios de reglas |

## Modelo por fase

Criterio de partida (no basado en benchmarks; ajustar según experiencia):

- **Modelo más capaz (p. ej. Opus) — fases 0, 1, 5 y revisión contra `estilo.md`**: brief, guion, guion reverso, estrategia de corte. Es juicio editorial; un error aquí cuesta el video. También para construir o reparar scripts y adaptadores.
- **Modelo rápido (p. ej. Sonnet) — fases 3, 4, 6, 7, 8 y 8.5**: ingesta, transcripción y glosario, corte con ffmpeg, Remotion con componentes ya definidos, render y textos de publicación.
- **Al aprobar la estrategia (⏸ fase 5):** si la sesión corre en el modelo más capaz, sugerir en una línea cambiar con `/model`. Si el creador prefiere seguir, no volver a sugerirlo en esa sesión.
- **Volver al modelo más capaz** si aparece una decisión editorial nueva (re-estructurar el corte, cambiar el hook) o un script falla de forma no trivial.
- No usar el modelo más pequeño para la pasada de glosario: las correcciones dependen del contexto.

## Estructura de carpeta por video

```
YYYY-MM-DD_slug/
  brief.md
  guion.md | guion_snapshot.md
  publicacion.md  # textos para publicar (fase 8.5)
  raw/            # originales, solo lectura
  edit/           # todo lo generado: transcripts, estrategia, previews, finales
    project.md    # memoria de sesión de video-use
```

## Checklist de ingesta (fase 3)

Lo que el agente no detecta aquí lo descubre el creador en la versión 3. Por cada toma, con `ffprobe` y un frame:
- **Color**: `color_transfer` / `color_primaries` / `pix_fmt`. HLG (`arib-std-b67`) o PQ (`smpte2084`) → conversión
  a SDR; log → LUT; SDR → nada (ver `references/estilo.md` § Color). Decidir por metadatos, nunca por el modelo de cámara.
- **Espejo**: mirar un frame buscando texto invertido (ropa, objetos, pantallas). La cámara frontal y algunas apps
  graban espejado → `hflip: true` en el EDL.
- **Rotación**: `side_data` / `rotate`; confirmar que la orientación final es la del brief.
- **fps** y resolución: si las tomas mezclan 24/25/30 fps, elegir el fps de salida (`fps` en el EDL) y avisar.
  25 fps a 1.2x calza 1:1 con 30 fps.
- **Audio**: canales, lavalier vs. cámara, viento (adelanta la transcripción; ver § Ritmo y cortes).
- Tomas sin voz (B-roll): no transcribir, o descartar su transcript (Whisper alucina frases de cierre).

## Versionado de entregables

Evita que el creador revise el archivo equivocado (caso real: abrir `final_youtube.v1.mp4` creyendo que era el más nuevo, cuando la corrección estaba en `final_youtube.mp4`).
- Todo archivo que el creador revisa lleva versión explícita y creciente desde la primera entrega: `final_youtube_v1.mp4`, `final_youtube_v2.mp4`… Nunca un nombre sin número que se sobrescribe mientras el respaldo recibe el número.
- Al entregar una versión nueva, mover las anteriores a `edit/_reemplazados/`: en la carpeta de entrega queda **un solo** candidato por pieza.
- **Un solo contador por pieza, de los previews al final**: cada render que el creador ve sube el número, y el
  final continúa la serie (`reel_v3` → `final_reels_v4`, nunca reiniciar en `v1`). Nunca re-renderizar sobre un
  número que el creador ya abrió (en Frameback o en el reproductor): eso es una versión nueva.
- Sobrescribir el mismo archivo solo en trabajo intermedio que el creador no revisa (proxies, cachés, renders de verificación).
- El mensaje de entrega dice ruta completa + versión + qué cambió respecto a la anterior.
- Los archivos asociados (SRT, portada, thumbnail, props) llevan la misma versión que la pieza a la que pertenecen.

## Herramientas y carriles

- **video-use + ffmpeg**: corte, limpieza de muletillas, silencios, color, loudness, subtítulos quemados. Transcripción local con `helpers/transcribe_local.py` (sin servicios pagados).
- **ffmpeg con libass/drawtext**: requerido. En macOS, Homebrew `ffmpeg-full` (keg-only); los scripts lo agregan al PATH solos (`GBO_FFMPEG_DIR` para otra ruta).
- **Whisper large-v3-turbo** (mlx-whisper): transcripción local con idioma forzado. Parakeet v3 se probó y derivaba a inglés en español con términos técnicos. Igual falla en términos técnicos → glosario.
- **Scripts** (`scripts/`, copiar a `edit/` de cada proyecto): `gbo_render.py` (corte con punch-in, velocidad y silencio por tramo, conversión de color + grade + espejo, limpieza de voz, B-roll y tarjetas anclados al tiempo de la fuente, captions con caja redondeada, desde un `edl.json`; deja un `.timeline.json` para Frameback), `make_audio.py` (música y SFX sintetizados), `mix_audio.py` (ducking + loudnorm, con música sintetizada o una pista con licencia desde un offset y fade propio).
- **Remotion**: motion graphics, captions animados, tarjetas de título, thumbnail. Se compone sobre el corte ya hecho, no lo reemplaza.
- **Frameback** (opcional): revisión anclada a cuadros, regiones y entidades del timeline, con feedback incremental. Ver `references/frameback.md`. Si no está instalado, los checkpoints funcionan igual por chat.
- **Teleprompter** (opcional): [teleprompter.guillebecerrao.cl](https://teleprompter.guillebecerrao.cl/), web, sin instalación; editor en el computador y proyección en un iPad, sincronizados por sesión con código y clave. Al aprobar el guion (fase 1), ofrecer una versión limpia para pegar: solo el texto hablado, sin marcadores de edición ni tabla de tomas.
- **Otras herramientas** (p. ej. Descript para multicámara + pantalla): si el perfil las declara, usarlas en su carril.

## Grabación sin errores de transcripción

- Si el creador se equivoca, hace una pausa de ~2 s y repite la frase completa. **Regla de corte: ante frases repetidas, usar la última toma completa**, salvo que la anterior tenga claramente más energía (consultar si hay duda).
- Las palabras "corte" u "otra vez" dichas a cámara son marcadores, nunca contenido.

## Checklist QA antes de entregar

- [ ] Hook en los primeros 3 s (vertical)
- [ ] Sin pops de audio en los cortes; loudness según `plataformas.md`
- [ ] Captions sin errores ortográficos ni de glosario; dentro de zonas seguras
- [ ] Ningún efecto sin razón (revisar contra la lista de prohibidos en `estilo.md`)
- [ ] Encuadre: cara nunca cortada por el reencuadre 9:16; ninguna tarjeta o texto sobre una cara
- [ ] Cortes verificados sobre la base sin música, con aire suficiente (≥ 0,15 s)
- [ ] El final de la música no cae bajo el CTA
- [ ] Color convertido según los metadatos (nada lavado ni "nostálgico") y sin material espejado
- [ ] Duración dentro del rango del brief
- [ ] Revisión visual final por el creador

## Cómo evolucionan las reglas

- Cuando el creador corrige algo de estilo, se registra en `<perfil>/aprendizajes.md` → "Propuestas pendientes".
- Solo con aprobación explícita la regla pasa a `<perfil>/estilo.md` o `<perfil>/glosario.md`.
- Los archivos de esta skill no se modifican en el uso diario. Una mejora del método que sirva a
  cualquier creador se propone como cambio al repo de la skill (issue o pull request).
