# Perfil local de gbo-video

> Copiar esta carpeta de plantilla a `~/.config/gbo-video/` (o a la ruta de la variable de
> entorno `GBO_VIDEO_PROFILE`) y completarla. El perfil es **privado**: no va en el repo de la
> skill. Puede versionarse en un repo privado propio.
>
> Archivos del perfil (todos opcionales salvo este):
> - `perfil.md` — este archivo
> - `marca.md` — tokens de marca (plantilla en `references/marca.md` de la skill)
> - `glosario.md` — términos propios que se suman al glosario base
> - `estilo.md` — reglas que sobrescriben o amplían `references/estilo.md`
> - `aprendizajes.md` — registro de cada video y propuestas de reglas (plantilla en `templates/aprendizajes.md`)

## Identidad
- **Nombre con el que el agente se refiere al creador:**
- **Idioma y registro del contenido:** (ej. español neutro, tuteo)
- **Firma o marca:** (nombre de la marca personal o proyecto)

## Equipo
- **Cámara principal:** (ej. teléfono en gimbal)
- **Audio:** (ej. lavalier inalámbrico)
- **Segunda cámara / grabación de pantalla:** (sí / no / a veces)
- **Lugares y objetos disponibles para B-roll:** (escritorio, exterior, etc.)

## Carpetas
- **Raíz de proyectos de video:** (ej. `~/Videos/<marca>/`)
- **Remotion (copia de trabajo de la plantilla):** (por defecto `remotion/` dentro de este perfil; o variable `GBO_REMOTION_DIR`)
- **video-use:** (por defecto `~/Developer/video-use`; o variable `VIDEO_USE_DIR`)

## Marca
- **Fuente de verdad de la marca:** (link o ruta al manual, design system o archivo de tokens)

## Integraciones (opcionales)
- **Sistema de guionización:** (ej. FARO en `<ruta>`; dónde viven los guiones y cómo se invoca
  el modo plan de producción desde ahí)
- **Frameback:** (sí / no)
- **Otras herramientas de edición en uso:** (ej. Descript para multicámara)

## Máquinas (opcional)
Si se trabaja en más de un equipo (por ejemplo, uno para guionizar y otro para procesar),
describir el rol de cada uno y qué tiene instalado. Ejemplo:
- **Principal:** guioniza y aprueba; tiene el sistema de guionización.
- **Cómputo:** transcribe y renderiza; trabaja con `guion_snapshot.md`, sin el sistema de guionización.

## Preferencias de trabajo
- **Modelo por fase:** (usar la recomendación de la skill o indicar otra)
- **Otras reglas personales:**
