# Marca — design tokens para video (plantilla)

La marca de cada creador vive en su **perfil local** (`<perfil>/marca.md`), no aquí. Este archivo
explica qué tokens necesita el video y cómo mantenerlos sincronizados. Si el perfil no tiene
`marca.md`, proponer crearlo copiando la tabla de abajo (⏸ el creador completa o aprueba los valores).

## Fuente de verdad
Lo ideal es que la marca tenga un manual propio (un artifact, un PDF, un archivo CSS de tokens,
un design system). El `marca.md` del perfil es una **copia de trabajo para video** y
`remotion/src/theme.ts` es la copia que usa el render. El perfil indica dónde está la fuente.

## Sincronizar (inicio de la fase 7, o cuando el creador diga que cambió la marca)
1. Leer la fuente de verdad que indica el perfil.
2. Comparar con el `marca.md` del perfil. Si nada cambió, seguir.
3. Si cambió: mostrar el diff (⏸), y con el OK actualizar `marca.md` del perfil y
   `remotion/src/theme.ts`.

## Tokens que usa el video

| Rol | Uso en video | Ejemplo (marca del autor) |
|---|---|---|
| Superficie / papel | Burbuja de subtítulos (~95%), paneles, tarjetas | `#FAFAF7` |
| Texto / tinta | Texto principal. Evitar negro puro | `#101418` |
| Texto secundario | Cargo del lower third, kickers | `#5E676E` |
| Línea | Bordes de tarjetas inactivas | `rgba(16,20,24,0.14)` |
| Acento | Énfasis en subtítulos, íconos, borde activo, títulos | `#1A5C86` |
| Acción | SOLO el CTA. Nada más lo usa | `#E08C4A` |
| Acentos extra (opcional) | Reservados; usar con moderación | `#E8A3B3`, `#7FC04E` |

| Voz tipográfica | Uso en video | Ejemplo |
|---|---|---|
| Sans (el sistema) | Subtítulos (700), nombres (800), kickers (600, espaciado, mayúsculas) | Archivo |
| Serif (la voz) | Tarjetas de título, citas | Newsreader itálica |
| Mono (lo técnico) | Monograma | Spline Sans Mono |

**Monograma:** marca corta que aparece como `/<monograma>` en lower thirds, tarjetas y
thumbnails (`theme.monogram` en Remotion). Ejemplo: `gbo`.

## Reglas de marca que conviene declarar
Escribirlas en el perfil para que el agente las respete. Ejemplos de la marca del autor:
acentos "en gramos" (la superficie manda), un solo CTA en el color de acción, nunca negro ni
blanco puros, no mezclar serif y mono en un mismo bloque, sin gradientes de acento como fondo.
