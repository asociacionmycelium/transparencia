# 06 — Hoja de ruta y pendientes

## Orden acordado
0. ~~**Repositorio público de documentos institucionales**~~ (D16–D21): hecho el 24/11/2026 en [`documentos`](https://github.com/asociacionmycelium/documentos). Si el Registro pide cambios en los Estatutos, actualizarlos en un commit propio con el motivo. Tras la inscripción, publicar la composición de la Junta (art. 46.3 de los Estatutos, dentro del mes siguiente a la aprobación de las cuentas).
1. **Landing de la asociación** (siguiente paso; ver `07-landing.md`). Motivo: aún no hay cuenta bancaria ni inscripción, así que no hay cuentas que publicar.
2. **Alcance de la v1 de la plataforma.** Propuesta de Claude: solo cuentas públicas — agente publicando desde Excel/CSV, log verificable con anclaje y web sencilla. Útil desde el día uno y sin necesidad de identidad. Votación y gobierno en una segunda fase. Arrancar cuando haya cuenta bancaria.
3. **Diseño RGPD del log** (doc 05).
4. **Mecánica de propuestas y votación** (doc 04).
5. **Entrada de decisiones de Junta y Asamblea** y configurabilidad por entidad.
6. **Detalle contable**: categorías, proyectos, fondos finalistas, qué se tapa en facturas.
7. **Responsabilidad como plataforma**: condiciones de uso, moderación (LSSI), menores.
8. **Proyecto open source**: AGPLv3, gobernanza de contribuciones y hoja de ruta (podría decidirse con la propia plataforma), nombre (comprobar OEPM y EUIPO).
9. **Arquitectura técnica**: stack, hosting, formato de lotes, API.

## Prueba de concepto independiente
Lectura del DNIe con JMRTD + autenticación pasiva contra la lista del BSI + HMAC (doc 03). Puede hacerse en cualquier momento.

## Elección del ERP
Aplazada hasta abrir la cuenta bancaria; candidato preferente Odoo Community + OCA l10n-spain (doc 02).
