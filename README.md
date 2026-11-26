# Plataforma de transparencia — Asociación Mycelium

> Nombre del producto: **pendiente de decidir**. Mycelium es la asociación ("contenedor de valores"); cada plataforma que lance tendrá identidad propia.

Documentación de diseño acordada en la sesión de trabajo del **23 de noviembre de 2026** entre la Junta Directiva de Mycelium y Claude. No hay código todavía; solo una maqueta de diseño en `demo/`.

## Estado

- **Diseño funcional:** decisiones de fondo tomadas (ver `docs/01-vision-y-decisiones.md`).
- **Implementación:** no iniciada. La asociación aún no tiene cuenta bancaria ni está inscrita en el Registro Nacional, así que no hay cuentas que publicar.
- **Siguiente paso acordado:** la **landing de la asociación** (ver `docs/07-landing.md`), no la plataforma.

## Índice

| Documento | Contenido |
|---|---|
| `CLAUDE.md` | Instrucciones y contexto para Claude Code |
| `docs/00-contexto-asociacion.md` | Qué es Mycelium, estado legal, reglas que afectan al producto |
| `docs/01-vision-y-decisiones.md` | Visión, módulos y registro de decisiones |
| `docs/02-arquitectura.md` | Agente publicador, ledger público, datos abiertos, ERP |
| `docs/03-identidad-y-verificacion.md` | Verificación de identidad para votar (DNIe NFC y alternativas) |
| `docs/04-gobierno-y-votacion.md` | Propuestas, votación, decisiones de Junta y Asamblea |
| `docs/05-privacidad-y-legal.md` | RGPD, retribuciones, LSSI, menores |
| `docs/06-hoja-de-ruta.md` | Pendientes y orden propuesto |
| `docs/07-landing.md` | Encargo de la landing (siguiente paso) |
| `demo/` | Maqueta de diseño de la landing y la plataforma (no funcional, datos inventados) |
| [`documentos`](https://github.com/asociacionmycelium/documentos) | Manifiesto y Estatutos en versión pública (repositorio aparte) |

## Antes de publicar
`scripts/guardia.sh` bloquea el push si encuentra PDF u otros documentos firmados, DNI o NIE, correos que no sean noreply o términos de una lista local que no se versiona (`~/.config/mycelium/guardia-denylist`). Se ejecuta como hook `pre-push` y en CI. Para activarlo en un clon nuevo: `git config core.hooksPath .githooks`. Con Claude Code, el subagente `revisor-publicacion` hace además una revisión semántica.

## Licencia
[GNU Affero General Public License v3.0 o posterior](LICENSE) (AGPL-3.0-or-later).
