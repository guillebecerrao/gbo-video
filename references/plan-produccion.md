# Modo plan de producción (apoyo a la guionización)

Se usa ANTES de grabar, cuando se está escribiendo un guion de video, ya sea con esta skill
(`templates/guion.md`) o con un sistema de guionización externo (por ejemplo, la skill de
guiones de [FARO](https://github.com/guillebecerrao/faro)). gbo-video no escribe el texto: lee
el guion y le agrega lo que la edición va a necesitar, para que no falte material el día del corte.

## División de responsabilidades
- **Quien guioniza es dueño de la palabra:** hook, estructura, voz, CTA. gbo-video no reescribe.
  Si una frase complica la edición (muy larga para un caption, un dato que pide gráfico, una
  transición sin puente), lo deja como **sugerencia** marcada `[sugerencia gbo]`.
- **gbo-video es dueño del cómo:** tomas, ángulos, material contextual, encuadre, audio,
  marcadores de edición.

## Input mínimo
1. Guion (borrador o final).
2. **Pieza ancla y derivados previstos.** No hay orden fijo: long form → verticales,
   post escrito → reel, reel suelto, etc. Si no se sabe, preguntar una vez; si sigue abierto,
   planificar para el caso más exigente (ver "Grabar para varios destinos").
3. Equipo disponible: el que declara el perfil local (`perfil.md` → Equipo). Segunda cámara y
   grabación de pantalla solo si el creador lo confirma para esta pieza.

## Output: sección `## Plan de producción` anexada al final del guion
1. **Formato de captura:** orientación, resolución, fps y por qué (según destinos).
2. **Tabla de tomas por beat del guion:**

| Beat | Toma | Tipo | Encuadre / ángulo | Para qué la usa la edición | Prioridad |
|---|---|---|---|---|---|
| Hook | T1 | A-cam talking head | plano medio, ojos tercio superior | apertura | imprescindible |
| Bloque B | T4 | B-roll contextual | detalle manos en teclado, 5–8 s | cubrir jump cut / ilustrar | recomendable |

   Tipos: `A-cam` · `B-cam` (segundo ángulo) · `B-roll contextual` · `pantalla` (screen recording) · `inserto` (objeto, documento, lugar) · `pickup` (frase repetida o alternativa).
3. **Marcadores de edición en el guion:** `[ZOOM]`, `[SFX]`, `[GRÁFICO]` (posible Remotion), `[B-ROLL: T4]`, `[PANTALLA: T6]`, insertos en la línea donde corresponden.
4. **Pickups recomendados:** frases clave que conviene grabar 2 veces (hook, CTA) o con una variante corta para el vertical.
5. **Checklist del día de grabación:** la de `templates/guion.md` + lo específico de esta pieza.
6. **Estimación de tiempo de grabación** (honesta, en minutos).

## Reglas
- **Cada toma extra se justifica** con su uso en la edición. Sin razón, no se pide. Sostenible le gana a heroico: respetar el tiempo que el creador tiene para grabar.
- Prioridades: `imprescindible` (sin esto la pieza no se puede editar bien) · `recomendable` (mejora clara) · `opcional` (si sobra tiempo). Máximo ~3 recomendables en un reel.
- B-roll contextual: describirlo de forma grabable con lo que el creador tiene a mano (su escritorio, su entorno, la pantalla), no stock genérico. El perfil local puede listar lugares y objetos disponibles.
- Una B-cam solo si aporta: cortes entre ángulos en piezas > 60 s, o cubrir cortes en long form. En reels cortos, el punch-in suele bastar.
- Respetar `estilo.md`: el plan no puede exigir más zooms o SFX que los límites del estilo.

## Grabar para varios destinos
- **Long form 16:9 con derivados verticales:** grabar 16:9 en 4K, sujeto centrado o con margen suficiente para un recorte 9:16 sin cortar la cara ni las manos. Señalar en el plan qué beats son candidatos a derivado vertical.
- **Reel nativo 9:16:** grabar vertical; si podría ir a YouTube horizontal, avisar que se pierde calidad y proponer una toma horizontal adicional solo si el brief lo pide.
- **Post escrito → video:** el post ya es el guion base; el plan marca qué frases funcionan dichas y cuáles solo funcionan leídas (proponer reescritura como `[sugerencia gbo]`).
- **Ambos formatos reales a la vez:** 16:9 4K + recorte, nunca dos grabaciones de la misma toma salvo que el creador lo pida.
