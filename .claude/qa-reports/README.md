# Informes de validación de QA

Un fichero por versión validada, `vX.Y.Z.md`, escrito por la skill `/validar-qa`
(`.claude/skills/validar-qa/`). Van en git a propósito: son el registro de por qué una versión
llegó a prod, o por qué no llegó.

**La autoridad es el fichero, no el flag de GitHub.** `release-prod` solo promociona una versión
si existe su informe aquí, en `main`, y su línea de veredicto es exactamente
`**Veredicto: APTO**`. El flag `prerelease` de la release es solo la señal: lo cambia cualquiera y
no queda en ningún diff. Una versión que nunca se validó no tiene informe, y la puerta la rechaza.

Son tres veredictos, `APTO`, `NO APTO` y `NO CONCLUYENTE`, y los dos últimos bloquean igual. Por eso
la línea se compara entera y nunca con un `grep APTO`, que también casa con `NO APTO`.

No se edita un informe viejo para cambiar su veredicto. Si algo se corrigió, se valida otra vez y
se escribe el informe de la versión nueva.

Este repositorio es público: un informe no lleva la dirección de QA, nombres de nodo, el
repositorio de despliegue ni datos de socios.
