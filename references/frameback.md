# Revisión con Frameback (opcional)

[Frameback](https://github.com/guillebecerrao/frameback) es una interfaz local de revisión (`npx frameback`): el creador abre el video entregado, marca segundos,
rangos, regiones del cuadro o entidades del timeline (cortes, transiciones, B-roll, captions, palabras) y deja
comentarios que llegan **uno a uno** a esta sesión mientras sigue revisando. **Es una capa encima de esta skill, no un
requisito:** si no está disponible, los checkpoints ⏸ funcionan exactamente igual que siempre (feedback por chat).

- **Detección** (una vez por sesión): `command -v frameback`. Si no está, no insistir ni instalar nada sin que
  el creador lo pida; seguir el flujo estándar. (Instalación: `npm install -g frameback`; para desarrollarlo, `npm link` en el clon.)
- **Cuándo:** al entregar un preview (⏸ fase 6) o un final (⏸ fase 8), si el creador pide revisar con Frameback o ya lo
  usa en el proyecto (existe `edit/review/`).
- **Arranque:** `frameback open edit/<archivo>_vN.mp4` en segundo plano (imprime la URL y la carpeta de revisión
  `edit/review/<archivo>_vN/`), y `frameback watch edit/<archivo>_vN.mp4 --json --actor human,system` con la
  herramienta **Monitor** (una notificación por comentario del creador, sin los ecos de lo que escribe el agente). `gbo_render.py` deja junto al render un `<salida>.timeline.json` que Frameback
  usa para mostrar cortes, cambios de speaker, B-roll, punch-ins y captions con tiempos exactos (`--no-timeline` lo
  desactiva). Si no hay sidecar, Frameback lee `edit/edl.json` (tiempos aproximados).
- **Mientras el creador revisa (trabajo encolado):** por cada comentario, mirar el snapshot (`snapshots/<id>.jpg`) y
  clasificar:
  1. *Preparable ya* (cambiar un punto de corte, sacar o reemplazar un B-roll, corregir un caption o el glosario,
     ajustar un punch-in) → `frameback update <dir> <id> --status in_progress`, aplicar el cambio sobre
     **`edit/edl.next.json`** (copia de staging del EDL; nunca tocar el entregable), y `--status prepared --plan "…"`.
  2. *Requiere render o decisión editorial* → `--status acknowledged` con el plan; se resuelve al procesar.
  3. *Ambiguo* → `--status needs_info` + `frameback reply <dir> <id> "pregunta concreta"`. No adivinar.
  Comentario editado (`revision` > `seenRevision`) → re-planificar; comentario borrado → deshacer lo preparado.
  Las decisiones de juicio editorial (re-estructurar el corte, cambiar el hook) siguen la regla de **Modelo por fase**.
- **Al pulsar "Procesar" (`review.submitted`):** `frameback review <dir> --state processing`; promover
  `edl.next.json` → `edl.json`, terminar lo pendiente y renderizar **una sola vez** la versión siguiente según
  **Versionado de entregables** (`_vN+1`, mover la anterior a `edit/_reemplazados/`); marcar cada comentario
  `--status applied --applied-in <archivo>_vN+1` (o `declined` con razón); `frameback review <dir> --state delivered
  --next-video edit/<archivo>_vN+1.mp4` y abrir la nueva versión (`frameback open …`): los comentarios se traspasan
  solos para que el creador verifique. **Detener el watch anterior e iniciar uno nuevo sobre `_vN+1`**: los
  comentarios que el creador reabra ahí vuelven a `pending` y son la siguiente ronda. Mover la versión anterior a
  `edit/_reemplazados/` recién cuando el creador ya abrió la nueva (al moverla, su revisión vieja deja de reproducirse,
  pero los comentarios ya viajaron).
- **Retro (fase 9):** los comentarios de Frameback son la mejor fuente de aprendizajes: `frameback export <dir>`
  genera un resumen en Markdown para proponer reglas en `<perfil>/aprendizajes.md`.
- **Estados de la revisión:** `delivered` y `closed` se aplican solo a la revisión de la versión **reemplazada**
  (`_vN`), nunca a la recién abierta (`_vN+1`), que debe quedar en `reviewing`; si no, Frameback bloquea los
  comentarios nuevos y el clic en planos solo mueve el cabezal. Nada de `--force` en estados sin pedido explícito. Si
  se bloqueó por error, el creador puede pulsar **Reopen review** en el panel de comentarios.

