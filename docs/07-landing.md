# 07 — Encargo: landing de la Asociación Mycelium

> **Estado:** solo definido. No crear hasta que la Junta lo pida.

> **26/11/2026:** hay una maqueta en [`demo/`](../demo/README.md) que sirve de base de diseño (D26). Une la landing y la plataforma en una sola página. Queda por decidir si la landing definitiva sale de esa maqueta o se hace con Claude Design tomándola como referencia.
>
> **26/11/2026, después:** el borrador de la página que se publicará está en [`web/`](../web/README.md) (D28), con lo que existe de verdad hoy. No se publica en el dominio hasta que la Junta lo decida (P-012). El inventario está más abajo.

## Objetivo
Una página que **genere impacto y sea emotiva**, que transmita los valores de la asociación tal como están en el manifiesto y deje claro que la asociación está **en proceso de registro**.

## Herramienta
- Se hará con **Claude Design** (tipo de artefacto Design en claude.ai), no a mano.
- Claude Code no puede crear artefactos Design: si esta tarea se retoma desde Claude Code, la parte de diseño se hace en claude.ai; Claude Code puede encargarse después de exportarla, integrarla y publicarla en el dominio.
- Dominio previsto: `asociacionmycelium.org` (y `.es`), registrados en Hostalia.

## Fuente de contenido
- **"Manifiesto de la Asociación Mycelium"**: el texto vigente es [`documentos/manifiesto.md`](https://github.com/asociacionmycelium/documentos/blob/main/manifiesto.md), publicado el 24/11/2026 (P-004). `web/genera.py` lo lee de ahí; no se copia a mano. El documento editable de claude.ai (octubre de 2026, chat "Declaración de intenciones asociación") fue su origen y ya no es la fuente.
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
- En la landing, únicamente en la información general si resulta obligatoria (art. 10 LSSI; hoy parece que no, ver «Información general y LSSI») y dentro del texto de los Estatutos enlazados (art. 7), que deben publicarse por el art. 46.3 de los propios Estatutos.
- Nunca en cabecera, pie, página de contacto ni material de difusión.

## Documentos a enlazar
- [`manifiesto.md`](https://github.com/asociacionmycelium/documentos/blob/main/manifiesto.md) y [`estatutos.md`](https://github.com/asociacionmycelium/documentos/blob/main/estatutos.md) en el repositorio público [`documentos`](https://github.com/asociacionmycelium/documentos); su historial de cambios es visible.

## A decidir antes de publicar
- **Información general del pie** (lo que se suele llamar «aviso legal»): ver la sección siguiente. Propuesta para la Junta: ponerla de forma voluntaria con denominación, NIF y correo, **sin domicilio**.
- **Política de privacidad:** solo hace falta pensarla si la página llega a tratar datos personales (formulario de contacto, analítica). Hoy no tiene ni lo uno ni lo otro, y no pide nada a terceros: las fuentes tipográficas se sirven desde la propia página. Qué exige el RGPD en ese caso está **NO VERIFICADO**.

## Información general y LSSI (cotejado el 26/11/2026)
Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico, versión consolidada actualizada el 18/12/2025 en el BOE: <https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758>. Comprobada con el subagente `verificador-legal` (API de datos abiertos del BOE).

- **Art. 10.1** (versión en vigor desde el 11/05/2014): obliga al *«prestador de servicios de la sociedad de la información»* a dar acceso por medios electrónicos, *«de forma permanente, fácil, directa y gratuita»*, a: *«a) Su nombre o denominación social; su residencia o domicilio o, en su defecto, la dirección de uno de sus establecimientos permanentes en España; su dirección de correo electrónico y cualquier otro dato que permita establecer con él una comunicación directa y efectiva. b) Los datos de su inscripción […] de aquel otro registro público en el que lo estuvieran para la adquisición de personalidad jurídica o a los solos efectos de publicidad»*, y *«e) El número de identificación fiscal que le corresponda»*. El art. 10.2 la da por cumplida si está en la web. La ley lo titula «Información general»; «aviso legal» es solo como se llama en la práctica.
- **Anexo a)**: es servicio de la sociedad de la información *«todo servicio prestado normalmente a título oneroso»*; los no remunerados solo *«en la medida en que constituyan una actividad económica para el prestador de servicios»*, y la lista de ejemplos, en la que está *«5.º El suministro de información por vía telemática»*, empieza con *«Son servicios de la sociedad de la información, entre otros y siempre que representen una actividad económica, los siguientes»*.
- **Lectura**: una web informativa de la asociación, sin venta, publicidad, cobros ni cuotas, no parece actividad económica y quedaría fuera del art. 10. Esta interpretación está **NO VERIFICADA**: la ley no define «actividad económica» y no se ha cotejado ninguna consulta ni sentencia sobre webs de asociaciones. Si la página llega a gestionar cuotas o donaciones, hay que revisarla.
- **Consecuencia para el domicilio** (D15): si la información general no es obligatoria, no hay que poner el domicilio fuera de los Estatutos. Si un día lo es, el art. 10.1.a admite *«residencia o domicilio»*, y habrá que decidir con la Junta.
- **Inscripción**: mientras esté en trámite, no hay datos de inscripción que dar (art. 10.1.b, «en su caso»).

## Inventario a 26/11/2026 (issue #1)
Qué enseña hoy la página de [`web/`](../web/README.md). Decidido con la Presidencia el 26/11/2026: sin selector de entidad; sin datos de ejemplo visibles (están en `demo/`); los asuntos abiertos de la Junta, en lista breve.

| Sección | Qué hay de verdad | Fuente | Hueco | Lo ve o decide la Junta (P-012) |
|---|---|---|---|---|
| Superficie | Titular y tres tramos del manifiesto | `documentos/manifiesto.md` | — | Dar cuenta |
| Estado del registro | Constituida el 9/11/2026; inscripción en trámite | `ESTADO` en `web/genera.py`, lo único escrito a mano | — | — |
| A la vista de todos | Texto del manifiesto y últimos cambios de `documentos`: fecha, qué cambió, firma verificada. Sin autor | `manifiesto.md`, `git log` | — | Dar cuenta |
| Cuentas | Nada: no hay cuenta bancaria. La sección lo dice | ERP (D25) | #2 | — |
| Decisiones: acuerdos | Nada: la Junta no ha publicado acuerdos | Por decidir | #4 | Qué se publica de cada reunión (P-006) |
| Decisiones: asuntos abiertos | Id, primera frase y estado de cada asunto | `documentos/junta/pendientes.md` (si pasa al ERP, se decide en #4) | — | Que salgan en la página |
| Propuestas | Nada: falta identidad y voto. La sección lo dice | Docs 03 y 04 | #5 | — |
| Datos | Nada que descargar | Lotes del ERP | #3 | — |
| Una invitación | Texto del manifiesto y el correo `administracion@asociacionmycelium.org` | `manifiesto.md` | — | Validar el correo («Posible», arriba) |
| Pie | Enlaces, licencias e «Información general (por escribir)» | D18 | — | Información general voluntaria sin domicilio |
| Red de filamentos | Pocos filamentos, sembrados con el nombre | — | #2 (con lotes, la huella del último) | — |
