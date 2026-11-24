# 03 — Identidad y verificación para votar

## Requisitos (Junta)
- Identificación **única** por persona.
- **Seudónima y verificable** internamente; **anónima** en la parte pública.
- Valorar fricción, deuda técnica y sistema de cada país o bloque (UE).
- Desde 14 años. Arranque en España. Público objetivo con capacitación tecnológica baja: el usuario **nunca** debe tomar decisiones técnicas (la palabra "NFC" no aparece en la interfaz).

## Arquitectura de identidad
1. **Verificación**: comprueba una vez que la persona es real y única. Adaptadores por método/país.
2. **Registro de la entidad**: guarda solo un identificador seudónimo de unicidad.
3. **Plataforma pública**: solo recibe pruebas criptográficas.

Registro tradicional (email + passkey) para participar (proponer, comentar). La verificación es un paso aparte, necesario para votar.

## Por qué no basta con validar el número de DNI
- La letra del DNI es un control módulo 23: se generan números válidos trivialmente.
- No prueba posesión (cualquiera conoce el DNI de un familiar).
- Las entidades privadas no tienen acceso a los servicios estatales de verificación de datos de identidad.
- El espacio de números es tan pequeño que un hash simple se revierte por fuerza bruta en minutos.

## Método principal: chip del DNIe / pasaporte (sin depender del Estado)
- El chip tiene **dos zonas**:
  1. Datos de identidad (nombre, fecha de nacimiento, foto, número) firmados por el Estado emisor. Se leen con el **CAN** (6 dígitos impresos en el anverso) o la MRZ. **No requiere PIN.**
  2. Certificados de autenticación y firma: requieren PIN y caducan. **No se usan.**
- Por eso no importa que el ciudadano haya olvidado el PIN ni que sus certificados estén caducados. Nadie tiene que ir a comisaría.
- **Autenticación pasiva** (ICAO 9303): se valida la firma del chip contra los certificados raíz públicos de cada país:
  - Lista maestra del BSI alemán: ~526 certificados de 109 países; uso comercial permitido si no se usa en publicidad ni aparenta cooperación con el BSI. https://www.bsi.bund.de/EN/Themen/Oeffentliche-Verwaltung/Elektronische-Identitaeten/Public-Key-Infrastrukturen/CSCA/csca.html
  - Lista maestra OACI: solo uso organizativo no comercial y **sin redistribución** → no incluirla en el repositorio; cada instancia la descarga. https://www.icao.int/icao-pkd/icao-master-list
- Librerías open source: **JMRTD** (Java, Android); equivalentes en iOS (iPhone puede leer documentos ICAO).
- Cobertura: NFC desde DNIe 3.0 (2015) y 4.0; DNI de la UE con chip obligatorio; pasaportes electrónicos de más de 170 países.
- DNI caducados: la firma sigue siendo verificable → aceptarlos por defecto, configurable por entidad.
- Flujo de usuario: introducir o escanear el CAN → acercar el DNI a la parte trasera del móvil unos segundos.
- Fricción real: sensibilidad al movimiento durante la lectura (cuidar UX: posición de la antena por modelo, reintentos), móviles sin NFC, DNI anteriores a 2015 (sobre todo mayores de 70, fuera de alcance por D11).
- Limitación: prueba que se tiene un documento auténtico, no que se sea el titular. Riesgo acotado: cada documento solo se registra una vez (quien presta el DNI pierde su voto). Opción futura: comparar selfie con la foto del chip **en el dispositivo** (analizar art. 9 RGPD antes).

## Orden de verificación (decidido)
La app detecta capacidades y guía en lenguaje cotidiano:
1. **Móvil puede leer el DNI** → "Acerca tu DNI a la parte de atrás del móvil".
2. **No puede** → ofrecer en este orden:
   - **Certificado digital** ("el que se usa para la Renta"), desde ordenador: validar cadena hasta FNMT u otra CA cualificada + revocación (OCSP/CRL). Lleva el DNI en el campo de número de serie. Cl@ve **no** es opción: solo pueden integrarla administraciones públicas.
   - **"Pide ayuda a alguien que pague con el móvil en las tiendas"**: flujo cruzado. El usuario inicia la verificación en su cuenta → QR / enlace (WhatsApp) de un solo uso → el móvil del ayudante lee el DNI → la prueba queda ligada a la sesión del titular. El móvil del ayudante no guarda nada (app open source).
   - **KYC comercial foto + selfie** (último recurso): p. ej. Didit — 500 KYC completos gratis al mes, NFC 0,15 $ (precios de noviembre de 2026, https://didit.me/pricing/; ya han cambiado una vez). Sumsub ~1,35 $/verificación. Inconvenientes: el tercero ve datos y biometría (art. 9 RGPD, EIPD, transferencias), dependencia comercial. Estas cuentas quedan con **nivel de verificación menor**.
3. **Futuro**: verificación asistida por entidades colaboradoras (voluntario verificado lee el DNI en persona); videollamada con voluntario de Mycelium para casos puntuales; EUDI Wallet.

## Ancla de unicidad
- España: derivar el identificador del **número de DNI o NIE** (permanente de por vida y presente en chip, certificado y KYC). Así una persona no puede registrarse dos veces por métodos distintos.
- Pasaportes extranjeros (futuro): nacionalidad + nombre + apellidos + fecha de nacimiento (coinciden entre documentos del mismo país; el número de pasaporte cambia al renovar). Riesgo residual: doble nacionalidad.

## Almacenamiento (D12)
- Junta: guardar de forma no descifrable pero verificable, añadiendo campos (nombre, país…) para dificultar la fuerza bruta.
- Implementación recomendada: **HMAC con clave secreta** guardada aparte (KMS/HSM). Añadir campos frena el ataque masivo pero no el dirigido (quien conozca los datos de alguien podría comprobar si está registrado); la clave lo impide. Solo la entidad puede verificar.
- Tras verificar, descartar el resto de datos del documento.

## Implantación por niveles
1. Nivel simple: el móvil envía los datos firmados del chip a un servicio de verificación de la entidad, que valida, calcula el HMAC y descarta. La entidad ve los datos un instante.
2. Nivel ZK (futuro): prueba generada en el móvil (ZKPassport, OpenPassport/Self). Nadie ve los datos. ZKPassport fue adquirido por Aztec Labs manteniendo el código abierto.

## Panorama UE
- EUDI Wallet: cada Estado debe ofrecer una antes del 24/12/2026; España seguía en piloto en octubre de 2026 y EDRi denuncia una interpretación restrictiva de los seudónimos. Diseñar compatible (OpenID4VP) sin depender de ella.

## Prueba de concepto propuesta
App Android que lea el DNIe de un miembro de la Junta con JMRTD, valide la firma contra la lista maestra del BSI y genere el HMAC. Valida el enfoque en una tarde.
