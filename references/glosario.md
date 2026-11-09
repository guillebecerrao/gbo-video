# Glosario técnico — corrección de transcripción

Quien habla en español mezcla términos técnicos en inglés, y la transcripción (Whisper
large-v3-turbo con el idioma forzado; estos términos van también como `--prompt`) suele
escribirlos mal. Esta tabla corrige el TEXTO; los timestamps originales nunca se tocan.

Este archivo trae una base común. Los términos propios de cada creador (su marca, sus
proyectos, nombres de personas, muletillas regionales) van en `<perfil>/glosario.md`, que
**se suma** a esta tabla. Cada error nuevo detectado en una revisión se agrega al glosario del
perfil, con aprobación del creador.

| Término correcto | Errores típicos de transcripción | Notas |
|---|---|---|
| prompt | promt, pront, prom | |
| Claude Code | cloud code, clot code, clocode | |
| Claude | cloud, clot, clod | Solo si el contexto es IA |
| agent / agente | eiyent, éyent | Respetar si dijo "agente" en español |
| skill | esquil, eskil | |
| spec | espec, spek | |
| deploy | diploy, deploi | |
| framework | freimwork, framwork | |
| workflow | worflow, guorflou | |
| product manager | prodac manayer | |
| feedback | fidbak, fíbac | |
| Descript | descrip, the script | |
| Remotion | remoción, remochon | |
| IA | idea | Solo si el contexto es inteligencia artificial |

## Reglas de corrección
1. Corregir solo cuando el contexto lo confirma; ante ambigüedad, marcar `[?]` y preguntar.
2. Nombres propios y marcas con su capitalización oficial.
3. No traducir: si dijo el término en inglés, queda en inglés.
4. Registrar cada corrección hecha en `edit/correcciones.md` (original → corregido, timestamp).
5. Whisper alucina en tomas sin voz ("¡Suscríbete al canal!", "Gracias por ver el video"):
   descartar el transcript de tomas de B-roll sin habla.
