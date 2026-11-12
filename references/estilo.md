# Reglas de estilo — gbo-video

> Valores por defecto calibrados en producción real (reels verticales y un long form de
> conversación a dos cámaras). Son un punto de partida, no verdades: cada creador los ajusta
> en su perfil local (`estilo.md` del perfil sobrescribe reglas puntuales de este archivo).

## Norte estético
Bien hecho y sutil. El espectador debe sentir ritmo, no "efectos". Si alguien
nota un recurso como recurso, sobró.

## Ritmo y cortes
- Cortar en límites de palabra; nunca a mitad de sílaba.
- Silencios internos: dejar respiración natural de ~0.15–0.30 s; eliminar gaps > 0.6 s.
- Muletillas ("eh", "este", "o sea" de relleno, falsos comienzos): eliminar, salvo
  que la pausa sea expresiva (preguntar si hay duda).
- **Titubeos y vocales sostenidas se cortan, nunca se aceleran**: acelerar un "eeeh" se nota
  y suena artificial. Se detectan por pitch estable + espectro similar entre ventanas.
- Fundidos de audio cortos en cada corte (video-use usa 30 ms por defecto).
- Jump cuts permitidos en vertical; en long form, cubrir con zoom o B-roll cuando molesten.
- Verificar cada punto de corte con la waveform (`timeline_view`) o `silencedetect`: los
  timestamps de Whisper derivan 0.2–0.5 s. Ningún corte debe dejar pausa > 0.4 s ni click.
- Si un corte salta tanto en texto como en imagen (cambio de idea + jump cut), cubrirlo con
  punch-in o B-roll, o elegir otro punto de entrada.
- **Cortes por energía, no por Whisper**: Whisper puede tragarse pausas dentro de una palabra
  (ej. "siento" = 2,8 s). Detectar silencios por RMS (umbral ≈ −40 dB en lavalier) y acotar
  cada corte por las palabras vecinas de la fuente; fusionar segmentos adyacentes para no
  repetir sílabas.
- **Aire entre segmentos**: mismo hablante ≈ 0,1 s; cambio de interlocutor dentro del tema
  ≈ 0,2–0,4 s; cambio de capítulo = cola más larga + separador visual/sonoro.
- **Aire mínimo medido por energía** (no por timestamps de Whisper): ≥ 0,15 s de cola tras la
  última sílaba y ≥ 0,15 s antes de la primera; 0,4–0,5 s de respiración total en un cambio de
  toma o de locación. Con ~0,08 s el creador percibe "voz pisada". Medirlo con
  `scripts/cut_energy.py check edit/edl.json` (e `islands` para ver dónde empieza y termina de verdad una frase).
- **Verificar los cortes sobre la base sin música** (o transcribiendo tramos aislados): sobre el
  mix final Whisper alucina palabras en los silencios entre segmentos ("no", "eso"). En tomas
  con viento adelanta palabras 0,1–0,4 s: alinear por energía (desplazamiento ≥ 0) y fijar los
  tiempos a mano en frases cortas.
- **No cortar al hablante a mitad de idea justo antes de que entre el otro** (parece
  interrupción): extender hasta el cierre de la frase, salvo que lo que sigue sea relleno.

## Punch-in / zoom
- Punch-in de 1.00 → 1.12 (máximo 1.15) para énfasis de una frase clave. En vertical, 1.08 no se nota.
- Anclar el zoom arriba (`y ≈ 8%` del recorte), no al centro, para no cortar la frente.
- Frecuencia máxima: uno cada 6–8 s. Nunca dos consecutivos en la misma escala.
- Tipo: corte seco a la escala nueva (preferido) o ease-in-out ≤ 300 ms. Nunca zoom lineal lento continuo.
- Zoom out (volver a 1.00) al cerrar una idea o al iniciar sección nueva.
- Nunca recortar frente, barbilla ni manos que estén gesticulando la idea.

## Subtítulos (captions)
- Chunks de 2–4 palabras, sincronizados por palabra.
- Caja de texto alta/baja (sentence case), no MAYÚSCULAS por defecto.
- Énfasis: máximo 1 palabra resaltada por chunk y solo en palabras con carga (cifra, verbo clave, concepto).
- Posición vertical: tercio inferior, dentro de la zona segura (ver `plataformas.md`).
- Sin emojis automáticos. Sin animaciones "bounce" exageradas: fade/slide ≤ 120 ms.
- Ortografía: aplicar `glosario.md` antes de quemar. Términos en inglés en su forma correcta (ej. "prompt", no "promt").
- Siempre con burbuja/rectángulo de fondo (legibilidad sobre cualquier fondo), con esquinas
  redondeadas (en Remotion: `Captions`; quemados: `caption_style.rounded` en `gbo_render.py`).
- Chunks que respeten las frases: no cruzar un punto final ("tarde. Así que ahí") ni dejar
  chunks de una palabra suelta; si `chunk()` lo hace, re-segmentar con `scripts/rechunk.py` (una frase
  por línea) antes de Remotion.
- Dos variantes en la plantilla: `paper` (burbuja clara) y `dark` (estilo reel: caja oscura,
  énfasis en bloque de acento, palabras aún no dichas atenuadas). El perfil dice cuál es la por defecto.
- Tipografía y color: roles de `marca.md` (perfil local). Burbuja en el color de superficie
  (~95% de opacidad), texto en el color de texto, sans en peso 700, énfasis en el color de
  acento. El chunk del CTA va en el color de acción, que no se usa en nada más. Nunca amarillo
  salvo que la marca lo defina.

## Gráficos (Remotion)
- Split screen: video sube a la mitad superior (cara completa), panel papel abajo con
  tarjetas/chips que aparecen en la palabra dicha (± 0.1 s). Subtítulos sobre la costura.
- Títulos en la tipografía serif de la marca (la voz); kickers en sans 600, mayúsculas espaciadas.
- Lower third con el monograma de la marca (tipografía mono) + nombre + cargo.
- Un split screen o tarjeta por idea clave; 2–3 por minuto como máximo.
- Tarjetas y textos **no tapan caras**; revisar en QA, porque al mover tiempos una tarjeta puede
  terminar sobre una cara.
- Gráficos y cortes no van atados 1:1: una tarjeta puede entrar antes de un corte y salir
  después. Anclar sus tiempos a la fuente (`[rango, tiempo_fuente]` en el EDL) para que
  sobrevivan a los re-cortes.
- **Cierre con URL**: si el CTA lleva a una URL, la `EndCard` (URL tecleada + clic) entra cuando
  se dice el CTA, con la voz encima; evita volver a cortar entre tomas al final.

## Efectos de sonido (SFX)
- Solo en: transición de sección, aparición de un gráfico/título, revelación de un dato.
- Nunca en cada corte ni en cada palabra resaltada.
- Nivel: claramente por debajo de la voz (punto de partida: −18 a −24 dB relativo a la voz; ajustar a oído).
- Paleta: whoosh suave, click/pop discreto, riser corto. Una misma familia de sonidos en todo el video.
- Máximo orientativo: 3–5 SFX por minuto en vertical; menos en long form.

## Música
- Opcional. Si va: instrumental, sin voz, ducking bajo la voz.
- Solo con licencia clara (librería del creador, registrar pista e ID en `edit/estrategia.md`),
  o sintetizada ad hoc (`edit/make_audio.py`) como respaldo.
- **El final de la música no cae bajo el CTA.** Tomar el tema desde la sección que calza con el
  tono del hook (suele ser la enérgica) y cerrar con un fade propio que termine después del CTA.
  Las ediciones automáticas "a duración exacta" de las librerías suelen terminar en un fade justo
  bajo el CTA: usarlas solo si se verificó su final.
- Los masters de librería vienen cerca de −9 LUFS: bajarlos (≈ −14 dB) antes del ducking.
- Niveles aprobados en el piloto: música −9 dB con ducking sidechain bajo la voz; SFX −8 dB
  (mezcla vía `edit/mix_audio.py`). Ajustar a oído.

## Voz
- Limpieza por defecto: `highpass=f=90, afftdn=nr=30:nf=-50:tn=1, agate (rango 0.08),
  EQ +2 dB @ 3 kHz, compresor 2.5:1`. En el piloto subió el SNR de ~25 a ~36 dB.
- Loudness final −14 LUFS / −1 dBTP (loudnorm de dos pasadas).

## Color e imagen
- **Primero la conversión por metadatos, después el look.** Decidir por el archivo, nunca por el
  equipo: `ffprobe -show_entries stream=color_transfer,color_primaries,pix_fmt`.
  - `arib-std-b67` (HLG) o `smpte2084` (PQ) → convertir a SDR bt709 (zscale + tonemap). Sin esto
    el material HDR se ve lavado o "nostálgico".
  - Perfil log → LUT de conversión del fabricante, no tonemap.
  - `bt709` / SDR → no convertir.
  En `gbo_render.py`: `color_chain` (conversión) y luego `grade` (look). Mostrar un antes/después
  al creador antes de renderizar.
- Un único look por serie o por locación. Correcciones mínimas: balance de blancos, exposición, contraste leve.
- Piel natural por sobre todo; no "teal & orange" agresivo.

## Transiciones
- Por defecto: corte seco.
- Entre secciones: zoom out + corte, o un fundido muy corto. Nada de wipes, giros ni glitch.

## Lista de prohibidos
- Zooms en cada frase · SFX en cada corte · captions que tapan la cara
- Emojis automáticos · glitch / shake / RGB split · stickers de stock
- Templates por defecto de cualquier herramienta sin adaptar a la marca

## Long form (conversación / entrevista)
- **Cold open**: intercalar cuñas del host y del invitado. Del invitado, preferir cuñas que
  *explican* (análisis, enseñanza) sobre frases polémicas sin contexto, para no presentarlo
  como "pesado". Incluir la tesis o razón de ser de la marca o del proyecto en los highlights.
  Una frase de tensión (ej. "falla de coordinación") funciona como cierre del cold open.
- **Gráficos**: indicador de capítulo persistente + seccionador entre capítulos; bandas
  laterales/chips solo en momentos fuertes.

## Hook (vertical)
- La primera frase con contenido aparece en ≤ 1 s; sin saludo ("hola, hoy les voy a contar…").
- Si el mejor hook está en medio de la grabación, se puede mover al inicio (consultar).
