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
- Siempre con burbuja/rectángulo de fondo (legibilidad sobre cualquier fondo).
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

## Efectos de sonido (SFX)
- Solo en: transición de sección, aparición de un gráfico/título, revelación de un dato.
- Nunca en cada corte ni en cada palabra resaltada.
- Nivel: claramente por debajo de la voz (punto de partida: −18 a −24 dB relativo a la voz; ajustar a oído).
- Paleta: whoosh suave, click/pop discreto, riser corto. Una misma familia de sonidos en todo el video.
- Máximo orientativo: 3–5 SFX por minuto en vertical; menos en long form.

## Música
- Opcional. Si va: instrumental, sin voz, ducking bajo la voz.
- Solo con licencia clara (registrar la fuente en `edit/estrategia.md`), o sintetizada ad hoc
  (`edit/make_audio.py`, sin licencia que registrar) mientras no haya librería propia.
- Niveles aprobados en el piloto: música −9 dB con ducking sidechain bajo la voz; SFX −8 dB
  (mezcla vía `edit/mix_audio.py`). Ajustar a oído.

## Voz
- Limpieza por defecto: `highpass=f=90, afftdn=nr=30:nf=-50:tn=1, agate (rango 0.08),
  EQ +2 dB @ 3 kHz, compresor 2.5:1`. En el piloto subió el SNR de ~25 a ~36 dB.
- Loudness final −14 LUFS / −1 dBTP (loudnorm de dos pasadas).

## Color e imagen
- Un único look por serie. Correcciones mínimas: balance de blancos, exposición, contraste leve.
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
