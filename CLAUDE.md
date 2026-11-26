# CLAUDE.md — contexto para retomar este proyecto

## Qué es esto
Plataforma de transparencia **open source** impulsada por la Asociación Mycelium (asociación sin ánimo de lucro, Alcalá de Guadaíra, Sevilla). Publica cuentas, decisiones de los órganos de gobierno y propuestas/votaciones ciudadanas de forma verificable. Debe servir a **cualquier asociación** que quiera usarla e integrarla con su sistema, no solo a Mycelium.

Lee `README.md` y después `docs/` en orden. `docs/01-vision-y-decisiones.md` contiene el registro de decisiones: no las reabras sin que la Junta lo pida.

## Estado a 26/11/2026
- En `demo/` está la maqueta que es la **guía** de diseño (D26): una sola página, sin JavaScript, con datos de ejemplo. **No se toca** (D28).
- En `web/` está el borrador de la **página publicable** (D28). `web/genera.py` la escribe desde las fuentes reales del repo `documentos` (manifiesto, cambios firmados sin autor, asuntos de la Junta). `web/publico/` es lo único que se despliega. Las secciones sin datos lo dicen y dejan un hueco oculto con su issue (#2 a #5). Lee `web/README.md` antes de tocarla.
- La asociación está constituida (9/11/2026) y con NIF provisional, pero la **inscripción en el Registro Nacional sigue en trámite** y **no hay cuenta bancaria**.
- Repositorios en GitHub, organización `asociacionmycelium`: este (`transparencia`, nombre provisional) y `documentos` (manifiesto, estatutos y registro de la Junta en `junta/`). Organización endurecida (D23); publicación con guardia y revisor (D22).
- Sistema contable decidido (D25, doc 02): Odoo Community 19.0 + OCA, con MCP autoalojado. Se pone en marcha cuando haya cuenta bancaria; la Junta debe conocerlo (P-011).
- Pendientes operativos en `docs/06-hoja-de-ruta.md`: segunda owner, fecha de la próxima Junta, cotejar las citas legales de `docs/00`–`05`. Dominio `asociacionmycelium.org` verificado en GitHub.
- Backlog de desarrollo en las issues del repositorio, con `prioridad-1..4` (D27), agrupadas en épicas con sub-issues (D29): #7, página lista para la Junta; #8, secciones con datos reales. Para elegir qué hacer, la skill `revisar-backlog`; `cerrar-sesion` las mantiene. Hasta que se haga #14, el triaje no distingue las épicas: no las propongas como tarea.
- Hay un flujo automático de desarrollo (D30) que trabaja las issues con `flow:ready`. Las issues con etiquetas `flow:*` no se tocan a mano. Haz `git pull` antes de tocar `web/`. Lo que el flujo pide como paso (Firefox, textos de la Junta) lo hace una persona. Sus commits de rama aún no van firmados: falta decidir la clave.
- Siguiente tarea: épica #7. #9 está hecha (26/11/2026) y #6 está en el flujo. Queda #10 (propuestas de diseño para la cabecera, con variantes para elegir); después #11 a #13, #15 (QA y prod en el clúster) y #17 (tests del generador). Después, enseñarlo a la Junta (P-012) y decidir si la **landing** definitiva sale de él o de Claude Design (`docs/07-landing.md`). No publicarlo en el dominio hasta que la Junta lo pida.

## Estilo de los textos públicos
Cercano, nada comercial, sin justificarse. Sin el marco moral "hacer el bien"; se habla de quien mira por su interés propio o por el interés común.

## Reglas que el producto debe respetar
- Licencia: **AGPL-3.0-or-later** para el software; CC BY-SA 4.0 para los textos institucionales (art. 6.1 de los Estatutos).
- Transparencia total: se publica todo, también lo trivial; el límite es cumplir los estatutos y el RGPD.
- Seguridad: la plataforma pública **nunca** tiene credenciales del sistema contable (ver `docs/02-arquitectura.md`).
- Nombres de producto: comprobar disponibilidad en OEPM y EUIPO antes de lanzar.
- Documentos institucionales: viven en el repositorio público `documentos`, separado de este. Nunca subir PDF firmados ni el acta fundacional; nunca DNI ni domicilios particulares. El domicilio social solo aparece en los Estatutos (y en el aviso legal si es obligatorio).

## Asuntos para la Junta
Lo que necesite conocimiento o acuerdo de la Junta Directiva se apunta en [`junta/pendientes.md`](https://github.com/asociacionmycelium/documentos/blob/main/junta/pendientes.md) del repositorio `documentos`, con su origen y el artículo de los Estatutos que lo ampara.

## Antes de cada push (obligatorio)
Hasta la inscripción no se publican datos de socios: ni nombres, ni nombres unidos a cargos, ni correos personales, ni domicilios.
1. Invoca el subagente `revisor-publicacion` con el rango que se va a subir (`git log origin/main..HEAD`; en el primer push, todo el árbol). Si devuelve BLOQUEAR, corrige antes de seguir.
2. El hook `pre-push` (`scripts/guardia.sh`) se ejecuta solo. No lo saltes con `--no-verify`.
