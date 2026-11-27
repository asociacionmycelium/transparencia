# 06 — Hoja de ruta y pendientes

## Orden acordado
0. ~~**Repositorio público de documentos institucionales**~~ (D16–D21): hecho el 24/11/2026 en [`documentos`](https://github.com/asociacionmycelium/documentos). Si el Registro pide cambios en los Estatutos, actualizarlos en un commit propio con el motivo. Tras la inscripción, publicar la composición de la Junta (art. 46.3 de los Estatutos, dentro del mes siguiente a la aprobación de las cuentas).
1. **Landing de la asociación** (siguiente paso; ver `07-landing.md`). Base de diseño hecha el 26/11/2026 en [`demo/`](../demo/README.md) (D26): falta pulirla, enseñarla a la Junta (P-012) y decidir cómo se produce la definitiva. Primer trabajo: decidir qué enseña ya con lo que hay de verdad hoy y hacer esa versión ([#1](https://github.com/asociacionmycelium/transparencia/issues/1)). Motivo: aún no hay cuenta bancaria ni inscripción, así que no hay cuentas que publicar.
2. **Alcance de la v1 de la plataforma.** Propuesta de Claude: solo cuentas públicas — agente publicando desde Excel/CSV, log verificable con anclaje y web sencilla. Útil desde el día uno y sin necesidad de identidad. Votación y gobierno en una segunda fase. Arrancar cuando haya cuenta bancaria.
3. **Diseño RGPD del log** (doc 05).
4. **Mecánica de propuestas y votación** (doc 04).
5. **Entrada de decisiones de Junta y Asamblea** y configurabilidad por entidad.
6. **Detalle contable**: categorías, proyectos, fondos finalistas, qué se tapa en facturas.
7. **Responsabilidad como plataforma**: condiciones de uso, moderación (LSSI), menores.
8. **Proyecto open source**: AGPLv3, gobernanza de contribuciones y hoja de ruta (podría decidirse con la propia plataforma), nombre (comprobar OEPM y EUIPO).
9. **Arquitectura técnica**: stack, hosting, formato de lotes, API.

El trabajo concreto de cada paso está en las [issues](https://github.com/asociacionmycelium/transparencia/issues) del repositorio, con su prioridad (D27).

## Pendientes operativos (24/11/2026)
- ~~**Dominio verificado en GitHub**~~: hecho el 24/11/2026 (`asociacionmycelium.org`).
- **Segunda persona owner** de la organización en GitHub (P-002 en [`junta/pendientes.md`](https://github.com/asociacionmycelium/documentos/blob/main/junta/pendientes.md)).
- **Fecha de la próxima Junta**: renombrar `junta/AAAA-MM-DD-orden-del-dia.md` y convocar por medios electrónicos con 48 horas de antelación (art. 21.1 de los Estatutos).
- **Cotejar en fuente primaria las citas legales de `docs/00` a `docs/05`**, escritas el 23/11/2026 antes de la regla de no citar de memoria, con el subagente `verificador-legal`. Ya verificadas el 24/11: los arts. 5.2, 7.1.b, 10, 21 y 32 de la ley de asociaciones y el art. 3 de la ley de transparencia (`docs/00`).
- Activar en la organización *Require actions to be pinned to a full-length commit SHA* si no se ha hecho (las acciones ya están fijadas, D23).
- **Maqueta `demo/`** (D26): es la guía y no se toca (D28). Lo que quedaba por pulir pasa a la página publicable.
- **Página publicable `web/`** (D28): primera versión con lo que hay hoy, hecha el 26/11/2026 (#1), con la tipografía servida desde la propia página. Lo que falta para enseñarla a la Junta está en la épica [#7](https://github.com/asociacionmycelium/transparencia/issues/7) (D29). ~~La red de filamentos (#9)~~ se hizo el 26/11/2026 con el flujo automático (D30, PR #16). ~~El pulido (#6)~~ se hizo el 26/11/2026 con el flujo (PR #18), con la prueba en Firefox hecha por una persona; de él salió la información general del pie (#19), que espera a la Junta (P-012). Faltan la cabecera (#10) y las cabeceras y la regeneración (#12); el CI y la tarjeta al compartir (#11 y #13) ya están en el flujo. También están en la épica (hoy [#20](https://github.com/asociacionmycelium/transparencia/issues/20)) los tests del generador (#17) y la infraestructura de QA y prod (#15). El 27/11/2026 se decidió cómo se despliega (D32) y que se publica de forma provisional en el dominio para que la Junta la vea (D33, P-012). Antes de servir prod en el dominio hacen falta la página de privacidad ([#26](https://github.com/asociacionmycelium/transparencia/issues/26)) y ~~logs de nginx sin IP de visitantes ([#25](https://github.com/asociacionmycelium/transparencia/issues/25))~~, hechos el 27/11/2026 (D35). El mismo día quedó montada la cadena de publicación (D34): la imagen se construye en cada push, `release-qa` llevó la `v0.1.0` a QA, que corre en la red local, y están listas la skill `validar-qa` y `release-prod`. Prod está preparado y sin aplicar. El orden es: #26 → la épica con versión en el título (propuesta: `v0.2.0`) → `validar-qa` APTO → `release-prod` → aplicar prod y publicarlo en el dominio. La dependencia de una sola persona (P-002) queda por escribir en `docs/02` (#15). Las secciones con datos reales, en la épica [#8](https://github.com/asociacionmycelium/transparencia/issues/8) (#2 a #5); cada asiento, acuerdo y propuesta tendrá su dirección propia cuando lleguen sus datos.
- ~~**Firma de los commits del flujo** (D30, D23)~~: hecha el 26/11/2026 con una clave propia del flujo (D31).

## Prueba de concepto independiente
Lectura del DNIe con JMRTD + autenticación pasiva contra la lista del BSI + HMAC (doc 03). Puede hacerse en cualquier momento.

## Elección del ERP
Decidido el 25/11/2026 (D25, doc 02): Odoo Community 19.0 + OCA, con MCP autoalojado. La puesta en marcha espera a la cuenta bancaria.
