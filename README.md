# gbo-video-method

**[Español](#español) · [English](#english)**

> El repo se llama `gbo-video-method` porque guarda el **método**; la skill se sigue llamando `gbo-video`
> (`/gbo-video` en Claude Code). Lo personal de cada creador vive aparte, en su perfil local.
> *The repo holds the **method**; the skill is still called `gbo-video`. Each creator's personal settings live in a
> separate local profile.* (Antes / formerly: `guillebecerrao/gbo-video`.)

---

## Español

**Edición de video agéntica con buen gusto, para Claude Code.** Del guion al render final: reels
verticales (Instagram, TikTok, Shorts) y long form para YouTube, editados por un agente que sigue
un flujo editorial real en vez de llenar el timeline de efectos.

Creado por **Guillermo Becerra O. (GBO)** · [@guillebecerrao](https://github.com/guillebecerrao) ·
[YouTube](https://www.youtube.com/@guillebecerrao). Pensado para builders de Latinoamérica.

### Qué es

Una sola [skill de Claude Code](https://code.claude.com/docs/en/skills) que contiene un flujo de
edición completo:

- **10 fases con checkpoints**: brief → guion → grabación → ingesta → transcripción → estrategia
  de corte → corte y pulido → motion → render y QA → publicación → retro. El agente se detiene a
  pedir tu aprobación donde un error cuesta caro, y itera sobre previews livianos.
- **El buen gusto escrito como reglas**: ritmo, cortes por energía del audio, punch-ins,
  subtítulos, efectos de sonido, limpieza de voz, loudness, thumbnails. Sutil por defecto: si
  alguien nota un efecto como efecto, sobraba.
- **Modo plan de producción**: mientras escribes el guion, el agente agrega las tomas, ángulos,
  B-roll y pickups que la edición va a necesitar, para que no falte nada el día del corte.
- **Transcripción local**: Whisper large-v3-turbo en Apple Silicon, timestamps por palabra y un
  glosario para los términos técnicos en inglés dentro del español. Sin APIs pagadas.
- **Plantilla de Remotion**: subtítulos animados, lower thirds, paneles divididos, tarjetas de
  título, reel vertical, long form 16:9, portada de reel y thumbnail de YouTube, con los colores
  y tipografías de tu marca.

### Tu perfil es tuyo

El método vive en este repo. Todo lo personal vive en un **perfil local**
(`~/.config/gbo-video/`): tu marca, tu glosario, tu equipo, tus carpetas, tus ajustes de estilo y
lo aprendido en cada video. Actualizar la skill nunca lo toca.

### Parte de un conjunto

| Pieza | Pregunta que responde | Qué es |
|---|---|---|
| [FARO](https://github.com/guillebecerrao/faro) | Qué decir y dónde | Sistema operativo de marca personal: agentes y skills para estrategia, guiones y publicación multicanal |
| **gbo-video** | Cómo editarlo | Esta skill |
| [Frameback](https://github.com/guillebecerrao/frameback) | Cómo corregirlo | Revisión precisa por cuadro: comentarios anclados a cuadros, regiones y elementos del timeline, que llegan al agente en vivo |
| [Teleprompter](https://teleprompter.guillebecerrao.cl/) | Cómo grabarlo | Teleprompter web para leer el guion en un iPad mientras lo controlas desde el computador |

Cada pieza funciona sola. Juntas: el guion escrito en FARO trae su plan de producción, lo grabas
leyéndolo en el teleprompter, la edición sigue gbo-video y tu revisión en Frameback le llega al
agente comentario a comentario.

**Sobre el teleprompter:** funciona en el navegador, sin instalar nada. Abres una sesión con
código y clave, y dos navegadores quedan sincronizados: el editor en el computador y la proyección
en el iPad (o cualquier tablet). Permite espejado horizontal y vertical, tamaño de letra y
velocidad configurables, una línea guía desplazable, pausa, retroceder unos segundos y recargar.

### Inicio rápido

```bash
git clone https://github.com/guillebecerrao/gbo-video-method ~/Developer/gbo-video-method
mkdir -p ~/.claude/skills && ln -sfn ~/Developer/gbo-video-method ~/.claude/skills/gbo-video
```

Abre Claude Code en una carpeta para tus videos y di *"nuevo video con gbo-video"*. En el primer
uso, el agente crea tu perfil contigo y revisa las dependencias de edición, pidiendo permiso antes
de instalar cualquier cosa. Instalación completa: [`SETUP.md`](SETUP.md).

### Requisitos

- [Claude Code](https://code.claude.com/docs)
- Para editar: macOS con Apple Silicon, ffmpeg con libass (Homebrew `ffmpeg-full`),
  [video-use](https://github.com/browser-use/video-use) (skill de terceros que hace el corte y el
  render base) y Python vía `uv`
- Para motion graphics: Node 20+ y [Remotion](https://www.remotion.dev) (revisa su licencia si lo
  usas comercialmente en una empresa)

La skill está escrita en español; Claude la entiende igual y trabaja con contenido en cualquier idioma.

---

## English

**Agentic video editing with taste, for Claude Code.** From script to final render: vertical
reels (Instagram, TikTok, Shorts) and YouTube long form, edited by an agent that follows a real
editorial workflow instead of throwing effects at the timeline.

Created by **Guillermo Becerra O. (GBO)** · [@guillebecerrao](https://github.com/guillebecerrao) ·
[YouTube](https://www.youtube.com/@guillebecerrao). Built for builders in Latin America.

### What it is

A single [Claude Code skill](https://code.claude.com/docs/en/skills) that encodes a complete
editing workflow:

- **10 phases with checkpoints**: brief → script → recording → ingest → transcription → cut
  strategy → cut and polish → motion → render and QA → publishing → retro. The agent stops for
  your approval where a wrong guess is expensive, and iterates on cheap previews.
- **Taste as rules**: rhythm, cuts by audio energy, punch-ins, captions, sound effects, voice
  cleanup, loudness, thumbnails. Subtle by default: if a viewer notices an effect as an effect,
  it was one too many.
- **Production plan mode**: while you write a script, the agent adds the shots, angles, B-roll and
  pickups the edit will need, so nothing is missing on editing day.
- **Local transcription**: Whisper large-v3-turbo on Apple Silicon, word-level timestamps, and a
  glossary for English tech terms inside Spanish speech. No paid APIs.
- **Remotion template**: animated captions, lower thirds, split panels, title cards, vertical
  reel, 16:9 long form, reel cover and YouTube thumbnail, themed from your brand tokens.

### Your profile stays yours

The method lives in this repo. Everything personal lives in a **local profile**
(`~/.config/gbo-video/`): your brand tokens, your own glossary, your equipment, your folders,
your style overrides and the learnings from each video. Updating the skill never touches it.

### Part of a set

| Piece | Question it answers | What it is |
|---|---|---|
| [FARO](https://github.com/guillebecerrao/faro) | What to say, and where | Personal-brand operating system: agents and skills for strategy, scripting and multi-channel publishing |
| **gbo-video** | How to edit it | This skill |
| [Frameback](https://github.com/guillebecerrao/frameback) | How to correct it | Frame-accurate review: comments anchored to frames, regions and timeline items, streamed live to the agent |
| [Teleprompter](https://teleprompter.guillebecerrao.cl/) | How to record it | Web teleprompter to read your script on an iPad while you control it from your computer |

Each piece works alone. Together, a script written in FARO carries its production plan, you record
it reading from the teleprompter, the edit follows gbo-video, and your review in Frameback lands on
the agent comment by comment.

**About the teleprompter:** it runs in the browser, nothing to install. Open a session with a code
and PIN and two browsers stay in sync: the editor on your computer and the projection on an iPad
(or any tablet). Horizontal and vertical mirroring, adjustable font size and speed, a movable guide
line, pause, jump back a few seconds and refresh.

### Quick start

```bash
git clone https://github.com/guillebecerrao/gbo-video-method ~/Developer/gbo-video-method
mkdir -p ~/.claude/skills && ln -sfn ~/Developer/gbo-video-method ~/.claude/skills/gbo-video
```

Then open Claude Code in a folder for your videos and say *"nuevo video con gbo-video"* (or
*"new video with gbo-video"*). On first use the agent creates your profile with you and checks the
editing dependencies, asking before it installs anything. Full setup: [`SETUP.md`](SETUP.md).

### Requirements

- [Claude Code](https://code.claude.com/docs)
- For editing: macOS on Apple Silicon, ffmpeg with libass (Homebrew `ffmpeg-full`),
  [video-use](https://github.com/browser-use/video-use) (third-party skill used for the base cut
  and render) and Python via `uv`
- For motion graphics: Node 20+ and [Remotion](https://www.remotion.dev) (check its license if
  you use it commercially in a company)

The skill itself is written in Spanish; Claude reads it fine and works with content in any language.

---

## Estructura del repo · Repository layout

```
SKILL.md              el flujo (punto de entrada) · the workflow (entry point)
references/           estilo, glosario, plataformas, marca, Remotion, plan de producción, Frameback
templates/            brief, guion, publicación, perfil local, aprendizajes
scripts/              render con punch-ins y subtítulos, audio sintetizado, ducking y loudness
vendor/               adaptador de transcripción local para video-use
remotion/             plantilla de Remotion (con la marca del autor como ejemplo)
```

## Licencia · License

MIT. Ver · See [`LICENSE`](LICENSE).
