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

## Sistema contable (decisión aplazada)
- Preferencia provisional: **Odoo Community + módulos OCA l10n-spain**. Odoo incluye paquete de localización "Spain - Non-profit entities (2008)" con el PGC de entidades sin fines lucrativos (https://www.odoo.com/documentation/latest/applications/finance/fiscal_localizations/spain.html). OCA tiene plantillas de cuentas anuales para ESFL, pero en versiones antiguas: comprobar si están portadas.
- ERPNext: localización española aparentemente menos madura — **no verificado a fondo**.
- Con los adaptadores, la elección no condiciona la plataforma.

## Despliegue
- Una instancia por entidad, autoalojable.
- Servicio gestionado por Mycelium en el futuro = Mycelium opera N instancias aisladas. Implica ser encargado del tratamiento (art. 28 RGPD) de cada entidad.

## Pendiente
Stack, hosting, formato exacto de lotes y API: se decide cuando estén cerrados el alcance de la v1 y el diseño RGPD del log (doc 05).
