# 02 — Arquitectura

## Principio: separación privado / público
```
[ERP / Excel / banco] ──► [Agente publicador (privado)] ──push lotes firmados──► [Plataforma pública]
      red de la entidad          sin puertos de entrada                       sin credenciales del ERP
```

### Agente publicador (privado)
- Corre junto al sistema contable, en la red de la entidad. Solo conexiones salientes.
- **Adaptadores** de origen: Odoo, ERPNext, CSV/Excel, ficheros bancarios (CAMT.053, Norma 43), API de Wise.
- Extrae solo asientos **contabilizados** (nunca borradores).
- Filtra y anonimiza (personas físicas, datos de beneficiarios), firma el lote y lo envía.
- Proceso nocturno diario; desfase configurable por entidad.

### Plataforma pública
- Recibe lotes, verifica firma, los añade a un **log append-only** y los muestra.
- Si se compromete, no contiene datos privados ni acceso de vuelta al ERP.
- Habla un **modelo de datos propio y documentado**: es el contrato abierto entre agente y plataforma.

## Verificabilidad
- Log append-only firmado; las correcciones son asientos nuevos que referencian al original.
- Hash de cada lote diario anclado públicamente (OpenTimestamps / Bitcoin). Reutiliza la línea técnica del proyecto de crédito mutuo (log firmado + anclaje).
- Numeración correlativa: cualquier hueco es detectable.

## Datos abiertos
- API pública, exportación CSV/JSON.
- Export en estándar **IATI** (organisation file + activity file) para cooperación internacional; cada vez más financiadores lo exigen. Refuerza una futura vía AECID. Referencia: https://iatistandard.org/en/guidance/standard-overview

## Sistema contable (decidido el 25/11/2026, D25)
**Odoo Community 19.0 + módulos OCA.** Con los adaptadores, la elección no condiciona la plataforma.

Comprobado el 25/11/2026 en el código de cada rama de [odoo/odoo](https://github.com/odoo/odoo) y de los repositorios de [OCA](https://github.com/OCA):
- **Plan contable** de entidades sin fines lucrativos en el núcleo de Odoo (`l10n_es`, plantilla `es_assec`), en 18.0, 19.0 y 20.0.
- **Cuentas anuales** de pymes sin fines lucrativos (balance y cuenta de resultados): `l10n_es_mis_report` con `mis_builder`, en 19.0.
- **Extractos bancarios**: Norma 43 (`l10n_es_account_statement_import_n43`) y CAMT.053 (`account_statement_import_camt`); conciliación con `account_reconcile_oca`. Los tres en 19.0.
- **Informes y ejercicios**: `account_financial_report` y `account_fiscal_year`. AEAT: `l10n_es_aeat`, modelos 303 y 347.
- **Socios y cuotas**: Odoo quitó `membership` del núcleo en 19.0 y lo mantiene OCA (`vertical-association`). Sin portar a 19.0 todavía: `membership_extension`, la cuota de alta y las bajas.
- **Veri\*Factu**: `l10n_es_edi_verifactu` está en el núcleo Community. Si aplica a la asociación: **NO VERIFICADO**.

Por qué 19.0:
- **20.0**: OCA l10n-spain tiene 2 módulos en esa rama. No se puede usar todavía.
- **18.0**: OCA está más completo (66 módulos de l10n-spain frente a 37 en 19.0, con 13 migraciones abiertas). Pero se empieza sin datos que migrar, y en Community cada versión mayor es una migración con OpenUpgrade. Además, 19.0 trae la API JSON-2, que sustituye a XML-RPC (obsoleta desde 19.0, retirada anunciada para Odoo 22).

Descartados:
- **ERPNext**: sin plan contable español oficial (solo un módulo de pago de terceros). Su punto fuerte era el servidor MCP que trae de serie.
- **IA nativa de Odoo**: es de Enterprise. En el código Community de 20.0 no hay módulo `ai` ni `mcp`.

### Acceso de IA (MCP)
- [`erpipe-org/mcp-odoo`](https://github.com/erpipe-org/mcp-odoo) (MIT), autoalojado. No instala nada en Odoo: entra con un usuario de Odoo y respeta sus permisos. Usa JSON-2 con 19.0. Bloquea las escrituras por defecto (variable de entorno, token de aprobación y confirmación humana) y admite campos permitidos y denegados por modelo.
- Descartado [`ivnvxd/mcp-server-odoo`](https://github.com/ivnvxd/mcp-server-odoo): en producción exige el módulo `mcp_server` de la tienda de Odoo, con licencia propietaria OPL-1 y sin código público. Sin él solo queda un modo que su autor marca como de desarrollo.
- Reglas:
  - Un usuario de Odoo solo para el MCP, con los permisos mínimos.
  - Empieza en solo lectura. Cuando escriba, solo **borradores**, y los contabiliza una persona: así nada que haga la IA llega a la plataforma sin validar (D5 solo publica asientos contabilizados).
  - Mientras el modelo sea externo, el MCP deniega los campos personales de los socios (DNI, domicilio, IBAN). Con datos privados reales, modelo local.
- Riesgo: el autor vende una versión alojada (ERPipe). Si el proyecto libre se queda atrás, el MCP se cambia sin tocar Odoo.

### Alojamiento y copias
- Autoalojado en red privada, sin exposición a internet. El agente publicador solo hace conexiones salientes (D4).
- Copias del volcado de Odoo (base de datos y ficheros adjuntos), cifradas con age, en local y fuera del sitio donde se aloja. Previsto: Google Workspace for Nonprofits si la asociación es elegible tras la inscripción (lo valida Goodstack). Restauración ensayada.
- Puesta en marcha: con la cuenta bancaria. Hasta entonces sigue la hoja de cálculo.

## Despliegue
- Una instancia por entidad, autoalojable.
- Servicio gestionado por Mycelium en el futuro = Mycelium opera N instancias aisladas. Implica ser encargado del tratamiento (art. 28 RGPD) de cada entidad.

## Pendiente
Stack, hosting, formato exacto de lotes y API: se decide cuando estén cerrados el alcance de la v1 y el diseño RGPD del log (doc 05).
