# SETUP — preparar un equipo para gbo-video

Instala solo los niveles que vayas a usar en cada equipo.

| Nivel | Para qué | Pasos |
|---|---|---|
| 1. Skill | Guionizar con plan de producción, consultar reglas | A + D |
| 2. Edición | Transcribir, cortar, captions, audio, render | A + B + D |
| 3. Motion | Captions animados, títulos, lower thirds, thumbnail con Remotion | A + B + C + D |

> Requisito del nivel 2: **Mac con Apple Silicon** (M1 o superior). La transcripción local usa
> mlx-whisper, que no funciona en Intel ni Windows. En otros equipos se puede reemplazar el
> motor de transcripción manteniendo el mismo formato de salida (ver el docstring de
> `vendor/video-use/helpers/transcribe_local.py`).

## A. Skill

```bash
git clone https://github.com/guillebecerrao/gbo-video-method ~/Developer/gbo-video-method
mkdir -p ~/.claude/skills
ln -sfn ~/Developer/gbo-video-method ~/.claude/skills/gbo-video
```
Verificación: abre Claude Code y pregunta "¿qué dice gbo-video sobre los zooms?".

## B. Edición

### B1. Herramientas base (macOS)
```bash
brew install ffmpeg-full uv
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -hide_banner -filters | grep -E "drawtext|subtitles"
```
El `ffmpeg` normal de Homebrew no trae drawtext ni libass. `ffmpeg-full` es keg-only: los
scripts lo agregan al PATH solos (usa `GBO_FFMPEG_DIR` si está en otra ruta).

### B2. video-use + transcripción local
[video-use](https://github.com/browser-use/video-use) es una skill de terceros que hace el corte
y el render base. gbo-video la usa como dependencia y le agrega un adaptador de transcripción
local, sin servicios pagados.
```bash
git clone https://github.com/browser-use/video-use ~/Developer/video-use
ln -sfn ~/Developer/video-use ~/.claude/skills/video-use
cd ~/Developer/video-use && uv sync

cp ~/Developer/gbo-video-method/vendor/video-use/helpers/transcribe_local.py helpers/
uv pip install mlx-whisper parakeet-mlx scipy
```
Prueba rápida (la primera vez descarga whisper-large-v3-turbo, ~1.5 GB):
```bash
uv run python helpers/transcribe_local.py <un_video.mov> --clip 0 30 -o /tmp/test.json
```
Si clonas video-use en otra ruta, define `VIDEO_USE_DIR`.

### B3. Tipografía de los captions quemados
`scripts/gbo_render.py` quema captions con libass usando una fuente del sistema
(`GBO_CAPTION_FONT`, por defecto `Inter`). Instálala en el equipo; si no, libass usa otra
fuente sin avisar.

## C. Motion (Remotion)

Requiere Node 20+. La plantilla está en `remotion/` de esta skill; la primera vez que llegues a
la fase 7, el agente la copia a tu carpeta de trabajo y la adapta a tu marca
(`references/remotion.md`). Para hacerlo a mano:
```bash
P=${GBO_VIDEO_PROFILE:-~/.config/gbo-video}
cp -R ~/Developer/gbo-video-method/remotion "$P/remotion" && rm -rf "$P/remotion/node_modules"
cd "$P/remotion" && npm install
echo node_modules >> "$P/.gitignore"   # si el perfil es un repo git
npm run dev   # preview en el navegador
```
Remotion exige licencia comercial a partir de cierto tamaño de empresa: revisa sus condiciones.

## D. Perfil local

```bash
mkdir -p ~/.config/gbo-video
cp ~/Developer/gbo-video-method/templates/perfil.md ~/.config/gbo-video/perfil.md
```
Complétalo (o pide al agente que lo haga contigo en el primer uso). Usa `GBO_VIDEO_PROFILE` si
quieres el perfil en otra ruta, por ejemplo dentro de un repo privado tuyo.

## Actualizar
```bash
cd ~/Developer/gbo-video-method && git pull
```
Tu perfil y tu copia de Remotion viven fuera de la skill, así que actualizar no los pisa. Si
`transcribe_local.py` cambia, vuelve a copiarlo a `~/Developer/video-use/helpers/`.

## Verificación final
En una carpeta de prueba, pide a Claude Code: *"verifica que este equipo está listo para editar
con gbo-video"*. Debe confirmar ffmpeg con libass, video-use enlazado, `transcribe_local.py`
funcionando con un clip de 30 s, la fuente de captions instalada y el perfil cargado.
