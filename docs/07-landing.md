# 07 — Encargo: landing de la Asociación Mycelium

> **Estado:** solo definido. No crear hasta que la Junta lo pida.

> **26/11/2026:** hay una maqueta en [`demo/`](../demo/README.md) que sirve de base de diseño (D26). Une la landing y la plataforma en una sola página. Queda por decidir si la landing definitiva sale de esa maqueta o se hace con Claude Design tomándola como referencia.

## Objetivo
Una página que **genere impacto y sea emotiva**, que transmita los valores de la asociación tal como están en el manifiesto y deje claro que la asociación está **en proceso de registro**.

## Herramienta
- Se hará con **Claude Design** (tipo de artefacto Design en claude.ai), no a mano.
- Claude Code no puede crear artefactos Design: si esta tarea se retoma desde Claude Code, la parte de diseño se hace en claude.ai; Claude Code puede encargarse después de exportarla, integrarla y publicarla en el dominio.
- Dominio previsto: `asociacionmycelium.org` (y `.es`), registrados en Hostalia.

## Fuente de contenido
- **"Manifiesto de la Asociación Mycelium"**: documento editable en claude.ai, redactado en octubre de 2026 (chat "Declaración de intenciones asociación"). Tomar siempre el texto vigente de ese documento.
- Estructura aproximada tras las revisiones: por qué existimos; **para quién trabajamos** (toda la sociedad cabe: lo que se resuelve para unos suele servir a todos, y también personas o empresas con recursos pueden usar, apoyar o inspirarse en el trabajo); **cómo trabajamos** (cuatro párrafos cortos, sin listas); **a la vista de todos** (transparencia y honestidad sobre los límites del voluntariado).
- Metáfora central: el micelio, red subterránea que conecta y nutre sin buscar reconocimiento; lo que se ve son las setas.

## Reglas de tono
- Cercano y emotivo, **nada comercial** ni de marketing.
- Sin justificarse: no presumir de cumplir la ley o de ser altruistas; eso se da por hecho.
- Sin el marco moral "hacer el bien" / "los buenos": hablar de quienes miran por el interés común frente al interés propio.
- Evitar frases grandilocuentes del tipo "la tecnología decide quién avanza y quién se queda atrás" (rechazadas en el manifiesto).

## Obligatorio
- Indicar de forma visible que la asociación está **en proceso de registro** (constituida el 9/11/2026; inscripción en el Registro Nacional en trámite).
- **No publicar información de los socios** (nombres de la Junta incluidos) hasta que esté inscrita.
- No mostrar cuentas ni datos bancarios: aún no hay cuenta.

## Posible (validar con la Junta)
- Anunciar que la transparencia será seña de identidad: cuentas públicas y una plataforma open source de transparencia en camino (sin nombre todavía).
- Contacto: `administracion@asociacionmycelium.org`.
- Enlace al manifiesto completo.

## Domicilio social (decidido 23/11/2026)
- Solo se muestra donde la ley lo exija. No es representativo de la asociación: está ahí porque la ley exige fijar uno.
- En la landing, únicamente en el aviso legal si resulta obligatorio (art. 10 LSSI) y dentro del texto de los Estatutos enlazados (art. 7), que deben publicarse por el art. 46.3 de los propios Estatutos.
- Nunca en cabecera, pie, página de contacto ni material de difusión.

## Documentos a enlazar
- [`manifiesto.md`](https://github.com/asociacionmycelium/documentos/blob/main/manifiesto.md) y [`estatutos.md`](https://github.com/asociacionmycelium/documentos/blob/main/estatutos.md) en el repositorio público [`documentos`](https://github.com/asociacionmycelium/documentos); su historial de cambios es visible.

## A decidir antes de publicar
- Aviso legal y política de privacidad mínimos (LSSI y RGPD) si hay formulario de contacto o analítica; sin formulario ni cookies de seguimiento, basta con un aviso legal.
