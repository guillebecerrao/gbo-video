# Remotion en el flujo

Remotion compone gráficos y captions animados sobre un corte YA hecho con video-use.
No reemplaza el corte.

## La plantilla `remotion/` de esta skill
La carpeta `remotion/` trae un proyecto Remotion que funciona: captions con énfasis, lower
third, paneles divididos, tarjeta de título, reel vertical, long form 16:9, portada de reel y
thumbnail de YouTube. Viene con la marca del autor como **ejemplo** (`src/theme.ts`).

**Primer uso (fase 7 por primera vez):**
1. Copiar la plantilla a la carpeta de trabajo que indica el perfil (`perfil.md` → Remotion;
   por defecto `~/Developer/gbo-remotion`). No trabajar dentro de la carpeta de la skill: al
   actualizar la skill se pisarían los cambios del creador.
2. `npm install` en la copia.
3. Reemplazar `src/theme.ts` con los valores del `marca.md` del perfil, incluido `monogram`
   (⏸ mostrar el diff al creador).
4. La copia es del creador: los componentes nuevos o ajustados se versionan ahí (idealmente en
   su propio repo git), no en esta skill.

Plugin opcional con conocimiento de Remotion para Claude Code:
```bash
claude plugin marketplace add remotion-dev/claude-code-plugin
claude plugin install remotion@remotion
```

**Licencia:** Remotion es gratis para individuos y empresas pequeñas, pero exige licencia
comercial a partir de cierto tamaño de empresa. Revisar las condiciones vigentes en
remotion.dev antes de usarlo comercialmente.

## Patrón de uso
1. video-use entrega `edit/corte.mp4` + transcript con timestamps por palabra (JSON).
2. Una composición (`GboVertical`, `GboReel`, `GboLongform`) recibe como props: ruta del video,
   palabras con tiempos, lista de énfasis y momentos de gráfico.
3. Componentes reutilizables:
   - `Captions` — chunks de 2–4 palabras, según `estilo.md`
   - paneles divididos con tarjetas/chips sincronizados por palabra
   - tarjeta de título y lower third, con los tokens de `src/theme.ts`
   (el punch-in se hace en ffmpeg, antes de Remotion)
4. Render: `npx remotion render GboReel edit/final_vertical_v1.mp4 --props=edit/props.json`

## Regla de carriles
- Captions simples quemados → ffmpeg / `scripts/gbo_render.py` (más rápido).
- Captions con énfasis animado, títulos, lower thirds, gráficos → Remotion.

## Thumbnail de YouTube y portada de reel
- Componentes: `GboThumb` (still 1280×720, long form) y `GboCover` (portada vertical del reel).
  Render: `npx remotion still GboThumb edit/thumbnail/thumbnail_youtube_v1.png --props=<json> --public-dir=edit`
  (las rutas de imagen en los props son relativas a `edit/`).
- Diseño de la plantilla: fondo oscuro, texto ≤ 5 palabras a la izquierda con acento, retratos a
  la derecha, monograma. La esquina inferior derecha queda libre (la tapa la duración de YouTube).
- El texto del thumbnail complementa el título, no lo repite. Verificar legibilidad a 320 px de ancho.
- **Elección de caras: buscar intriga, no solo "verse bien".**
  - Descartar primero lo que no favorece: mueca, boca a medio decir una palabra, ojos cerrados, labios fruncidos.
  - Entre los que quedan, priorizar la emoción que genera curiosidad: cara pensativa, planteando
    una idea con fuerza mientras gesticula, intriga, escepticismo, sorpresa. La sonrisa amable
    es el último recurso.
  - Buscar en los momentos de mayor tensión del guion (desacuerdos, preguntas difíciles),
    no muestrear parejo todo el video. Manos gesticulando dentro del cuadro suman energía.
  - Proponer al menos una variante con emoción fuerte junto a la segura, explicando qué emoción busca cada una.
