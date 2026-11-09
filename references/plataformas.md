# Especificaciones de salida por plataforma

> Valores de partida habituales en la industria. Las plataformas cambian sus
> recomendaciones: verificar en la documentación oficial antes de fijarlos como regla.

| Salida | Resolución | FPS | Duración objetivo | Notas |
|---|---|---|---|---|
| Reels / TikTok / Shorts | 1080×1920 (9:16) | igual al origen (30 o 60) | 30–60 s (definir en brief) | Zona segura: dejar libre ~15% inferior y ~10% superior; margen derecho libre por botones |
| YouTube long form | 3840×2160 o 1920×1080 (16:9) | igual al origen | según brief | Capítulos en descripción |
| Miniatura / cover | 1080×1920 (vertical) / 1280×720 (YT) | — | — | Fuera de esta skill por ahora |

## Códec y audio (punto de partida)
- Video: H.264, CRF 18–20, `-preset veryfast` para previews, `slow` solo para el final si hay tiempo.
- Audio: AAC 48 kHz. Loudness integrado objetivo ≈ −14 LUFS, true peak ≤ −1 dBTP
  (verificar contra la recomendación vigente de cada plataforma).
- Previews: 540×960 o 960×540, CRF 28, para iterar rápido.

## Reencuadre 16:9 → 9:16
- Recorte centrado solo si la cara está centrada en toda la toma.
- Si el sujeto se mueve: seguimiento de cara (script con detección facial) con suavizado; nunca saltos bruscos de encuadre.
- Validar visualmente 3–5 frames del reencuadre antes de renderizar.
