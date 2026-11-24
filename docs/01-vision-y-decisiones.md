# 01 — Visión y registro de decisiones

## Visión
Una plataforma open source y autoalojable que cualquier asociación pueda conectar a su sistema para publicar, de forma verificable y diaria:
- sus **cuentas** (movimientos, justificantes anonimizados, presupuesto frente a ejecución, cuentas anuales);
- la **trazabilidad** del dinero (fondos finalistas, origen agregado de ingresos);
- sus **decisiones de gobierno** (acuerdos, votos, conflictos de interés, actas);
- las **propuestas ciudadanas** de proyectos y su votación;
- su **actividad e impacto** por proyecto.

## Módulos
| Módulo | Qué hace |
|---|---|
| Agente publicador | Adaptadores (Odoo, ERPNext, CSV/Excel, ficheros bancarios), anonimización, firma, envío diario |
| Ledger público | Log append-only verificable, anclaje de hashes, correcciones visibles |
| Cuentas | Movimientos, justificantes anonimizados, presupuesto vs ejecución, cuentas anuales |
| Trazabilidad | Fondos finalistas, origen de ingresos agregado, donantes solo con consentimiento |
| Propuestas | Propuesta abierta, voto igual para todos, respuesta razonada obligatoria |
| Gobierno | Acuerdos, votos nominales, conflictos de interés, actas; reglas configurables por entidad |
| Proyectos | Ficha por proyecto: estado, coste, horas voluntarias, impacto agregado, repositorio |
| Datos abiertos | API, CSV/JSON, export IATI |
| Identidad | Registro tradicional + verificación para votar (ver doc 03) |
| Privacidad | Niveles público / socios / Junta; minimización por defecto |

## Registro de decisiones (23/11/2026)
| # | Decisión | Motivo |
|---|---|---|
| D1 | Open source y reutilizable por cualquier asociación, integrable con su sistema | Misión de la asociación |
| D2 | Propuestas y votación ciudadana **dentro** de la plataforma, junto con las decisiones de Junta | Un único punto de transparencia |
| D3 | La plataforma **no** es el libro contable oficial; solo publica lo que sale del sistema contable | Reducir superficie de ataque |
| D4 | La plataforma pública **no tiene credenciales** del ERP: un agente privado empuja lotes firmados (push, no pull) | Si comprometen la parte pública, no hay nada privado que robar ni camino hacia la contabilidad |
| D5 | Publicación **diaria** de asientos contabilizados, con desfase configurable (p. ej. D+3); correcciones como asientos nuevos, nunca ediciones | Máxima transparencia sin fricción |
| D6 | Una **instancia por entidad** (no multi-tenant). Primero autoalojable; después, servicio gestionado por Mycelium "en preparación", priorizado según demanda | Simplicidad, aislamiento, portabilidad |
| D7 | Se publica **todo**, incluido lo trivial o burocrático. Numeración correlativa de acuerdos y asientos para que cualquier hueco sea detectable | No ser opacos |
| D8 | Votación ciudadana abierta desde los **14 años**; requisito: identificación única | Edad de consentimiento RGPD en España (art. 7 LOPDGDD) sin gestionar consentimiento parental |
| D9 | Lanzamiento inicial en **España** | Empezar donde se conoce el marco |
| D10 | Identidad: registro tradicional para participar; verificación aparte, propia, para votar. Orden: DNIe por chip NFC → certificado digital → enlace "pide ayuda a alguien que pague con el móvil" → KYC comercial foto + selfie | Ver doc 03 |
| D11 | Mayores de 70 (DNI permanente sin NFC) fuera del público inicial; el proyecto solo vive en internet por costes | Se buscará otra vía cuando haya medios |
| D12 | Datos de identificación guardados de forma **no reversible pero verificable** (hash con clave) | Seudónimo verificable internamente, anónimo en lo público |
| D13 | Retribuciones de miembros de la Junta: publicar **con nombre** (consentimiento al aceptar cargo o contrato); empleados ajenos a la Junta, en agregado. **Revalidar** cuando se implemente | Disipar sospechas donde más importa |
| D14 | ERP open source a elegir más adelante (candidato preferente: Odoo Community + OCA l10n-spain) | No bloquea el diseño gracias a los adaptadores |
| D15 | Domicilio social solo donde lo exija la ley: dentro de los Estatutos (art. 7.1.b LO 1/2002, publicados por obligación del art. 46.3 de los Estatutos) y en el aviso legal si procede. Nunca en cabecera, pie, contacto ni difusión | No es una sede propia ni representa a la asociación; está ahí porque la ley exige fijar uno |
| D16 | Manifiesto y Estatutos se publican en un **repositorio público propio de documentos institucionales**, separado del repositorio de la plataforma. La landing enlazará ahí | El historial de cambios es transparencia en sí mismo; la plataforma tiene identidad y licencia propias |
| D17 | En ese repositorio **nunca** entran los PDF firmados ni el acta fundacional (nombres, DNI y domicilios en el cuadro de firmas y en los certificados de firma). Solo versiones públicas en texto sin datos personales | Protección de datos de las personas promotoras |

## Decisiones de 24/11/2026
| # | Decisión | Motivo |
|---|---|---|
| D18 | Textos del repositorio institucional ([`documentos`](https://github.com/asociacionmycelium/documentos)) con licencia **CC BY-SA 4.0**; el software de la plataforma con **AGPL-3.0-or-later** | Art. 6.1 de los Estatutos: software y documentación con licencias libres con copyleft |
| D19 | Alojamiento en **GitHub**, organización `asociacionmycelium`, sin espejo en Codeberg | Codeberg no admite espejos pull de otras forjas (FAQ) y, desde julio de 2026, su § 2(1)7 de condiciones de uso prohíbe proyectos de código mayoritariamente generado con IA, que es como se desarrollará la plataforma. Git es portable: migrar después es posible |
| D20 | Dos repositorios públicos: `documentos` y `transparencia` (nombre provisional hasta elegir el del producto). La landing tendrá repositorio propio | Aplica D16; renombrar en GitHub mantiene redirecciones |
| D21 | Datos de socios fuera de los repositorios hasta la inscripción: solo cargos, sin nombres. Commits con correo noreply de GitHub | Decisión de 23/11/2026 de no publicar datos de los socios |
| D22 | Nada se publica sin dos controles: `scripts/guardia.sh` (hook `pre-push` y CI; bloquea PDF y ofimática, DNI/NIE, correos que no sean noreply y los términos de una lista local **no versionada**, sin distinguir tildes) y el subagente `revisor-publicacion` (revisión semántica: variantes de nombres, nombre unido a cargo, de quién es un domicilio) | Un regex no ve las deducciones: el revisor bloqueó dos veces textos que permitían identificar a una persona y una cita mal hecha de los Estatutos. La lista de términos no puede estar en el repositorio porque contiene justo lo que no se publica |
| D23 | Endurecimiento de GitHub: commits firmados con SSH; en `main`, ruleset sin borrado ni force-push, historial lineal y firma obligatoria; acciones fijadas por SHA completo con Dependabot; 2FA obligatoria; los miembros no crean, borran ni cambian la visibilidad de repositorios; escaneo de secretos, protección de push y aviso privado de vulnerabilidades | Un proyecto de verificabilidad debe poder demostrar quién cambió qué. Descartado: exigir PR para cada cambio, que con un solo desarrollador solo añade fricción |
| D24 | Los asuntos para la Junta Directiva se registran en [`documentos/junta/`](https://github.com/asociacionmycelium/documentos/tree/main/junta) (pendientes con id, tipo, origen y artículo; orden del día por reunión). El acta oficial no va al repositorio: la levanta la Secretaría-Tesorería y va al libro de actas. Qué se publica de cada reunión lo decide la Junta (P-006) | Que no se olvide nada de lo que hay que ratificar y que la agenda del órgano de gobierno sea pública. Descartado: GitHub Issues, que no viven en git, atan a GitHub y exigirían una cuenta de GitHub a quien tenga que consultarlos |

## Propuestas de Claude pendientes de confirmar
- Voto **no vinculable** a la persona incluso para la propia entidad (credenciales anónimas con nullifier por votación), manteniendo un seudónimo estable para proponer y comentar. Ver doc 04.
- Resultados de votación **desglosados por nivel de verificación**.
