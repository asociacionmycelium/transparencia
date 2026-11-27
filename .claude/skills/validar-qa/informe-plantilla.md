# Validación QA — <vX.Y.Z>

**Veredicto: <APTO | NO APTO | NO CONCLUYENTE>**

<!--
La línea de arriba es lo que lee release-prod.yml, y la compara ENTERA. Tres valores, no dos.
Formato exacto, sin adornos: **Veredicto: APTO**
Este repositorio es público: ni la dirección de QA, ni nodos, ni el repositorio de despliegue,
ni la cuenta de nadie, ni datos de socios.
-->

| | |
|---|---|
| Validado el | <AAAA-MM-DD> |
| Imagen | `ghcr.io/asociacionmycelium/transparencia-web:<vX.Y.Z>` · digest `<sha256:…>` · commit `<7>` |
| ArgoCD | `<sync>/<health>` |
| Épica | <#N · reflejo del AAAA-MM-DD · lista / bloquean … / contraste …> |
| Versión anterior validada | <vX.Y.Z (veredicto, fecha) o «ninguna»> |
| Modo | <completa \| rapida> |

## Casos

| Frente | Casos | ✔ | ✖ | No ejercidos |
|--------|------:|--:|--:|-------------:|
| Fase 0 (F0a–F0f) | 6 | | | |
| Servidor (S1–S3) | 3 | | | |
| Contenido (C1–C4) | 4 | | | |
| Logs (L1–L2) | 2 | | | |
| Navegador (N1–N5) | 5 | | | |
| Persona (H1) | 1 | | | |

<!-- La salida de qa.py, tal cual, en un bloque de código. Después, N1–N5 con lo que devolvió la
     evaluación en cada anchura, y H1 con la respuesta de la persona. -->

## Bloqueantes (P0)

<!-- Uno por subsección: Qué falla · Evidencia · Issue. Si no hay, «Ninguno». -->

## Hallazgos (P1) y observaciones (P2)

## Qué no se validó

<!-- Y por qué. Un frente sin ejercer y una versión que no está lista no se leen igual. -->
