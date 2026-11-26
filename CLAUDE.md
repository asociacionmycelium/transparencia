# CLAUDE.md — contexto para retomar este proyecto

## Qué es esto
Plataforma de transparencia **open source** impulsada por la Asociación Mycelium (asociación sin ánimo de lucro, Alcalá de Guadaíra, Sevilla). Publica cuentas, decisiones de los órganos de gobierno y propuestas/votaciones ciudadanas de forma verificable. Debe servir a **cualquier asociación** que quiera usarla e integrarla con su sistema, no solo a Mycelium.

Lee `README.md` y después `docs/` en orden. `docs/01-vision-y-decisiones.md` contiene el registro de decisiones: no las reabras sin que la Junta lo pida.

## Estado a 26/11/2026
- Solo diseño. No hay código de la plataforma. En `demo/` hay una maqueta que es la base de diseño de la landing y la plataforma (D26): una sola página, sin JavaScript; `demo/genera.py` rellena `index.html` con los datos de ejemplo. Lee `demo/README.md` antes de tocarla.
- La asociación está constituida (9/11/2026) y con NIF provisional, pero la **inscripción en el Registro Nacional sigue en trámite** y **no hay cuenta bancaria**.
- Repositorios en GitHub, organización `asociacionmycelium`: este (`transparencia`, nombre provisional) y `documentos` (manifiesto, estatutos y registro de la Junta en `junta/`). Organización endurecida (D23); publicación con guardia y revisor (D22).
- Sistema contable decidido (D25, doc 02): Odoo Community 19.0 + OCA, con MCP autoalojado. Se pone en marcha cuando haya cuenta bancaria; la Junta debe conocerlo (P-011).
- Pendientes operativos en `docs/06-hoja-de-ruta.md`: segunda owner, fecha de la próxima Junta, cotejar las citas legales de `docs/00`–`05`. Dominio `asociacionmycelium.org` verificado en GitHub.
- Backlog de desarrollo en las issues del repositorio, con `prioridad-1..4` (D27). Para elegir qué hacer, la skill `revisar-backlog`; `cerrar-sesion` las mantiene.
- Siguiente tarea: issue #1, decidir qué enseña ya la página con lo que hay de verdad hoy y hacer esa versión desde la maqueta. Después, pulir la maqueta (lista en `docs/06`), enseñarla a la Junta (P-012) y decidir si la **landing** definitiva sale de ella o de Claude Design (`docs/07-landing.md`). No publicarla en el dominio hasta que la Junta lo pida.

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
