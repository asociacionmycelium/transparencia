# 05 — Privacidad y marco legal

## RGPD frente al log inmutable (conflicto principal pendiente)
- El derecho de supresión (art. 17 RGPD) choca con un registro que no se puede borrar.
- Solución de diseño propuesta:
  - En el log **nunca** entran datos personales: solo seudónimos y hashes.
  - Lo que haya que poder borrar se cifra con una clave por persona que se destruye cuando toca (*crypto-shredding*).
- Pendiente: base jurídica de cada tratamiento, registro de actividades de tratamiento y, casi con seguridad, **EIPD** (verificación de identidad; biometría si se usa KYC).

## Niveles de visibilidad
Público / socios / Junta. Minimización por defecto. Anonimización automática de personas físicas en justificantes; protección reforzada de beneficiarios vulnerables. Donantes con nombre solo con consentimiento expreso y revocable.

## Retribuciones y reembolsos (D13, revalidar)
- **Reembolso**: devolución de un gasto adelantado por la asociación, con justificante. Publicable sin problema.
- **Retribución**: pago por un trabajo. En Mycelium el cargo es gratuito; solo cabe pagar servicios distintos del cargo (2/3 de la Asamblea).
- Propuesta acordada en principio: retribuciones de miembros de la Junta **con nombre** (consentimiento al aceptar cargo o contrato); empleados ajenos a la Junta, en agregado. Opción configurable por entidad.

## Menores (14–17)
- Desde 14 años pueden consentir el tratamiento de sus datos (art. 7 LOPDGDD); por eso el mínimo de 14 evita gestionar consentimiento parental.
- Atención especial en moderación y en lo que se publica de ellos.

## Responsabilidad como plataforma
- Al alojar propuestas y comentarios de terceros, la entidad es prestadora de servicios de la sociedad de la información (LSSI): condiciones de uso, criterios de moderación y procedimiento de retirada.

## Servicio gestionado (futuro)
- Gestionar instancias de otras entidades convierte a Mycelium en encargado del tratamiento: contrato art. 28 RGPD con cada una.
