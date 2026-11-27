# Página publicable: lo que hay de verdad hoy

Es la página que se publica en el dominio. La Presidencia decidió el 27/11/2026 publicarla para enseñarla a la Junta, que puede pedir cambios o que se retire (P-012). Lleva `noindex` hasta que esté publicada la página de privacidad (#26).

La maqueta de [`demo/`](../demo/README.md) es la guía de diseño y no se toca (D26, D28). Esta página sale de ella, pero solo enseña lo que existe. Lo que aún no tiene datos lo dice en la página, y en el código deja un hueco oculto (`<div class="hueco" hidden>`) con la issue que lo rellenará.

## Generarla y verla

```
python3 web/genera.py
python3 -m http.server 8765 --directory web/publico
```

y abrir `http://127.0.0.1:8765/`. El generador lee el repositorio `documentos` del directorio de al lado (o el de `MYCELIUM_DOCUMENTOS`), usa solo la biblioteca estándar y se puede repetir: con las mismas fuentes, la página sale igual.

## Comprobar que está al día

La página versionada tiene que ser la que sale de las fuentes. Para comprobarlo:

```
python3 -B web/genera.py && git diff --exit-code -- web/publico
```

Si sale una diferencia, es que alguien ha tocado a mano lo que hay entre `<!--G:…-->` o que `documentos` ha cambiado y falta regenerar: se regenera y se sube. Si el generador se para, lo dice el mensaje: una fuente que ha cambiado de forma, una seta sin filamento, un hueco a la vista, algo que la CSP bloquearía o unas cabeceras que no son las de `cabeceras`.

Desde que esté en `main` el workflow `pagina` (`.github/workflows/pagina.yml`, se añade a mano tras el merge de #11), GitHub lo hace en cada push y pull request, una vez al día y a mano; hasta entonces, la comprobación es la de arriba, a mano. Saca `transparencia` y `documentos` uno al lado del otro, regenera con `MYCELIUM_DOCUMENTOS` apuntando a `documentos` y falla si `web/publico` cambia. La ejecución diaria es la que avisa cuando `documentos` avanza y nadie ha regenerado. Regenerar y subir solo lo que cambia en `documentos` lo hace el workflow `regenera`: ver «Regeneración».

Las firmas se comprueban contra `firmantes`, no contra la configuración de git de cada máquina. `genera.py` se la pasa a git solo para esa llamada (`-c gpg.ssh.allowedSignersFile=`), sin tocar la configuración global, y por eso la página sale igual aquí y en GitHub.

### Añadir una clave

`firmantes` tiene una línea por clave, `documentos namespaces="git" <tipo> <clave>`, y comentarios que empiezan por `#`. El principal es siempre `documentos`: ni correos ni nombres, tampoco en los comentarios. Cuando alguien más empiece a firmar los cambios de `documentos`:

1. Coge su clave pública de firma, la línea de su `.pub`, y quítale el comentario del final, que suele ser un correo o el nombre de una máquina. Quedan el tipo y la clave.
2. Añade al final de `firmantes` la línea `documentos namespaces="git" <tipo> <clave>`.
3. Comprueba que es la suya: la huella de `ssh-keygen -lf <su .pub>` tiene que ser la que da `git -C ../documentos log --format=%GK` en sus commits.
4. Regenera la página: sus cambios pasan de «No comprobada» a «Verificada». Sube los dos ficheros juntos.

Hasta entonces, sus cambios salen como «No comprobada». Para dejar de reconocer una clave, se borra su línea y se regenera.

## Qué hay aquí

| Fichero | Qué es |
|---|---|
| `genera.py` | Lee las fuentes y escribe lo que hay entre `<!--G:…-->` en `publico/index.html` |
| `regenera.py` | Regenera la página y, si cambia, la sube a `main` en un commit que firma GitHub. Lo lanza el workflow `regenera` (ver «Regeneración») |
| `cabeceras` | Las cabeceras HTTP de la página, en formato `_headers`. El servidor de la imagen (#15) las toma de aquí. No se despliega |
| `firmantes` | Las claves públicas con las que se firman los cambios de `documentos` (formato `allowed_signers` de ssh-keygen). Un cambio sale como «Verificada» solo si lo firma una de ellas, en cualquier máquina. No se despliega |
| `publico/` | Lo que se sirve o despliega, tal cual. Nada más |
| `publico/index.html` | La página. Sin JavaScript (D26) |
| `publico/estilo.css` | Todo el aspecto. Solo lo que usa la página; el resto está en `demo/estilo.css`. El final, entre `/*G:red*/` y `/*/G:red*/`, lo escribe `genera.py`: el tramo del scroll en el que crece cada trazo de la red |
| `publico/favicon.svg` | El icono de la pestaña: una seta como las de la cabecera, tierra sobre albero. Escrito a mano |
| `publico/tarjeta.png` | La imagen de la tarjeta al compartir (Open Graph), de 1200×630. La dibuja `genera.py` con el color de la superficie, las setas y el arranque de la red de `publico/estilo.css` y la propia página. No se edita a mano |
| `publico/fuentes/` | Atkinson Hyperlegible Next y Mono (SIL OFL 1.1, subconjunto latino de Fontsource), servidas desde aquí: la página no pide nada a terceros |
| `imagen/` | La imagen que sirve `publico/` con nginx (#15): `Dockerfile`, `nginx.py`, que escribe la configuración de nginx desde `cabeceras`, y `comprueba.py`, que mira las cabeceras de lo que se sirve. Ver «Imagen» |

## De dónde sale cada sección

| Sección | Fuente | Hoy |
|---|---|---|
| Superficie (titular y tres tramos) | `documentos/manifiesto.md` | Real |
| Estado del registro | `ESTADO` en `genera.py`, lo único escrito a mano | Constituida; inscripción en trámite |
| A la vista de todos | `manifiesto.md` y `git log` de `documentos` | Real: últimos cambios con fecha, qué cambió y firma, comprobada contra `firmantes`; sin autor |
| Cuentas | ERP (D25) | Vacía; hueco #2 |
| Decisiones: acuerdos | Por decidir (P-006) | Vacía; hueco #4 |
| Decisiones: asuntos abiertos | `documentos/junta/pendientes.md` | Real. Si pasan al ERP, se decide en #4 |
| Propuestas | Identidad y voto (docs 03 y 04) | Vacía; hueco #5 |
| Datos | Lotes del ERP | Vacía; hueco #3 |
| Una invitación | `manifiesto.md` | Real; el correo de contacto lo valida la Junta (P-012) |
| Red de filamentos | Sin lotes: un filamento por seta, sembrado con el nombre, que se afina y se apaga hacia abajo | Con lotes, la huella del último (#2) |
| Tarjeta al compartir | Los `og:*` del `<head>`: el nombre, el titular de `manifiesto.md` y `tarjeta.png` | Preparada; se prueba en Telegram y Mastodon cuando se publique (P-012) |

## Reglas
- Nada inventado: si no hay dato, la sección lo dice.
- Ningún dato de socios: ni nombres, ni autores de commits, ni correos personales. El domicilio, solo dentro de los Estatutos enlazados (D15).
- Si una fuente cambia de forma (falta una sección del manifiesto, cambian las columnas de `pendientes.md`), el generador se para en vez de publicar algo a medias.
- La red de filamentos también para el generador: cada seta tiene su filamento, ninguna rama empieza a crecer antes de que su madre llegue a donde nace y ningún punto se sale de la franja de la red.
- Ningún hueco a la vista: si un `class="hueco"` pierde `hidden`, el generador se para.
- Lo que sale de `documentos` se dice desde fuera: «este repositorio» en `pendientes.md` sale en la página como «el repositorio documentos» (`desde_fuera` en `genera.py`, #6).
- La tarjeta al compartir apunta a `URL` de `genera.py` (hoy `https://asociacionmycelium.org/`): si la página se publica en otro dominio (#15), se cambia ahí y se regenera. La imagen solo se reescribe si cambian sus píxeles, y el generador se para si `estilo.css` no da los colores o si pesa 300 KB o más.
- La página cumple la CSP de `cabeceras`: ni `style=`, ni `<style>`, ni `<script>` (tampoco con nonce), ni manejadores `on…=`, ni recursos de fuera, y en `estilo.css` ni `@import` ni `url()` de fuera. Si no, el generador se para. Por eso las variables de cada trazo de la red van en `estilo.css` y no en el atributo `style`.
- `cabeceras` lleva exactamente las de `CABECERAS` en `genera.py`; si no, el generador se para. Para cambiar una cabecera se cambian las dos, y #15 la recoge del fichero.

## Contraste
Medido con WCAG 2 (mínimo AA, 4,5:1) el 26/11/2026 (#6). Sobre `--tierra`: texto y enlaces 12,98:1, tenue 6,74:1, lila 6,27:1, albero 7,82:1; tinta sobre albero, 8,53:1.

En pantalla ancha el texto no llega a la franja de la red. En pantalla estrecha (≤52rem) la red pasa por detrás del texto: por eso allí es más tenue y `--tenue` sube al 75 % de hifa. Con dos troncos cruzados detrás, el peor caso, el tenue da 4,56:1 y el albero 4,52:1. Si cambian los colores o la opacidad de la red, hay que volver a medirlo.

## Cabeceras

Las pone el servidor de la imagen (#15), que las toma de `cabeceras` y las comprueba con `curl -I` contra ese mismo fichero. Las de `/*` valen para todas las rutas, también para `/fuentes/*`. `{NONCE}` es una marca: `_headers` no tiene nonces por petición, así que el servidor pone en su lugar un valor aleatorio distinto en cada respuesta (en nginx, `$request_id`).

| Cabecera | Valor | Por qué |
|---|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'nonce-{NONCE}' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'` | La página no pide nada fuera del dominio: si algo así se cuela, el navegador no lo carga. `script-src` no es `'none'` por Cloudflare: prod va con Bot Fight Mode, que inyecta en cada respuesta HTML un `<script>` que carga `/cdn-cgi/challenge-platform/…`, y Cloudflare le pone el nonce que lee de esta cabecera (en una `<meta>` no le vale). La página sigue sin JavaScript propio: un `<script>` que se colara en ella no lleva el nonce y no se ejecuta. Sin `'self'` ni `'unsafe-inline'`. `form-action` va aparte porque `default-src` no la cubre, y la página no tiene formularios |
| `Strict-Transport-Security` | `max-age=31536000` | Un año solo por HTTPS. Sin `includeSubDomains`, para no forzar HTTPS en los nombres internos que cuelgan del dominio. Sin `preload` |
| `Referrer-Policy` | `no-referrer` | Al seguir un enlace, el otro sitio no sabe de dónde viene la visita |
| `X-Content-Type-Options` | `nosniff` | El navegador no adivina el tipo de un fichero |
| `Cache-Control`, solo en `/fuentes/*` | `public, max-age=31536000, immutable` | Las fuentes no cambian: se descargan una vez |

Lo que sirve Cloudflare en prod puede llevar ese script de más, con el nonce de la respuesta. El resto del HTML es idéntico a `web/publico/index.html`.

Con `<meta http-equiv>` en la página se perdería casi todo: HSTS no vale en una meta, `X-Content-Type-Options` y la caché de las fuentes tampoco, una CSP en `<meta>` no admite `frame-ancestors` y Cloudflare no lee el nonce de ahí. Por eso van en el servidor.

## Regeneración

El workflow `regenera` (`.github/workflows/regenera.yml`, se añade a mano tras el merge de #12) se ejecuta una vez al día y a mano, desde Actions. Saca `main` y `documentos` y lanza `regenera.py`, que:

1. Regenera la página con `genera.py`. Si no cambia nada, dice `nada que regenerar` y acaba.
2. Se para si un cambio de `documentos` que la página daba por «Verificada» deja de serlo: es que falta su clave en `firmantes`.
3. Prepara el commit sin mover ninguna rama y lo pasa por `scripts/guardia.sh`. Lo que sube el token del workflow no lanza otros workflows, así que después no pasaría ninguna guardia.
4. Lo sube a `main` con la API de GitHub, que lo firma (D23). Si `main` ha cambiado mientras tanto, no sube nada y lo intenta la pasada siguiente.

Por la misma razón, ese commit tampoco construye la imagen: `regenera` la pide después por `workflow_dispatch` al workflow `imagen` de #15. Mientras ese workflow no exista, avisa y no hace nada. Va por un cron diario y no por `repository_dispatch` desde `documentos`, para que `documentos` no guarde ninguna credencial con permiso de escritura aquí: un cambio puede tardar hasta un día en llegar a `main`.

Para ver qué cambiaría sin subir nada: `python3 -B web/regenera.py --sin-publicar`.

La imagen nueva no se despliega sola. Un cambio de `documentos` llega a QA con la siguiente release, al crear la etiqueta `vX.Y.Z` en `main` (`release-qa`), y a prod cuando se lanza a mano `release-prod` para esa versión, con la comprobación de QA en verde. Esa cadena la monta #15: hasta entonces, la página regenerada se queda en `main`.

## Pendiente de P-012

La página ya se publica en el dominio (#15). Quedan, a la espera de la Junta (P-012):

- La meta `robots` del `<head>`: se quita cuando esté cotejada la información legal que debe llevar la página (aviso legal y privacidad).
- El aviso de borrador: `<p class="borrador">` y el «(borrador)» del título.
- La «Información general» del pie (#19).

## Imagen
La página se sirve desde una imagen propia, `ghcr.io/asociacionmycelium/transparencia-web` (D32, #15): nginx sin privilegios con `publico/` dentro y nada más. Ni `genera.py`, ni `firmantes`, ni este README entran en ella.

**Cómo se construye.** `imagen/Dockerfile`, con `web/` como contexto. La primera etapa ejecuta `imagen/nginx.py`, que lee `cabeceras` y escribe `nginx.conf`. La segunda copia esa configuración y `publico/` sobre `nginx-unprivileged`, fijada por digest. Dependabot mantiene al día los digests de las dos imágenes base. La etapa final no tiene `RUN`, así que la variante arm64 sale sin emulación.

**El contrato con el clúster.** Escucha en el 8080 y corre como uid 101. Con la raíz de solo lectura escribe solo en `/tmp` (pid y temporales de nginx). `GET /` devuelve 200, y es lo que miran las sondas. Lleva `linux/amd64` y `linux/arm64`. Si algo de esto cambia, cambian a la vez los manifiestos del despliegue.

**Las cabeceras salen de `cabeceras`.** `nginx.py` traduce el bloque `/*` al nivel del servidor, con `always`, para que un 404 también lleve la CSP. `/fuentes/*` pasa a `location /fuentes/`, donde se repiten las de `/*`: en nginx, un `add_header` dentro de una location anula los heredados. La marca `{NONCE}` pasa a ser `$request_id`, 128 bits aleatorios por petición. Si `cabeceras` no trae la CSP con el nonce, HSTS, `Referrer-Policy` y `nosniff`, o trae una ruta que no sabe traducir, se para y no se construye nada.

**Los logs no guardan quién visita (#25).** El formato `sinip` registra la hora, el método, la ruta sin la query, el estado, los bytes y el tiempo. No registra la IP, ni `X-Forwarded-For`, ni `CF-Connecting-IP`, ni `User-Agent`, ni `Referer`. No hay `real_ip`: la dirección que ve nginx es la del túnel, no la de la persona. Se queda un access log, y no `access_log off`, porque es lo único que deja ver los 404 y la carga: el despliegue no tiene métricas propias. Los 404 no pasan al error log (`log_not_found off`), que sí apuntaría el cliente y el `Referer`. Cuánto duran estos logs en el clúster lo dice esta sección cuando QA esté montado (#25).

**Construir y probar en local**, desde la raíz del repositorio:

```
docker buildx build --load -t transparencia-web:local -f web/imagen/Dockerfile web/
docker run --rm -d --name web --read-only --tmpfs /tmp --user 101:101 -p 8080:8080 transparencia-web:local
python3 web/imagen/comprueba.py http://127.0.0.1:8080
```

`comprueba.py` pide la raíz, una fuente y una ruta que no existe. Compara cada cabecera con `cabeceras`, comprueba que el nonce cambia en cada petición, que no hay cookies y que el servidor no dice su versión. Vale igual contra QA desde la red local. Contra prod no vale tal cual, porque Cloudflare añade su script de detección de bots y sus cookies `__cf_bm` y `cf_clearance` (D33).

**En GitHub** lo hace `.github/workflows/imagen.yml`. En cada pull request construye la imagen, la arranca como en el clúster (solo lectura, uid 101, sin capacidades), pasa `comprueba.py` y comprueba que los logs no guardan ni la IP, ni el `User-Agent`, ni el `Referer`, ni la query. En cada push a `main`, y cuando lo lanza `regenera`, hace lo mismo y además publica la imagen multiarquitectura como `sha-<7 primeros del commit>`. No despliega: a QA se llega con una release `vX.Y.Z` y a prod con `release-prod`, que promocionan el mismo digest sin reconstruir (D32).

### Llevar a QA

Se lanza a mano `release-qa` desde Actions, sobre `main`, con la versión (`vX.Y.Z`). No reconstruye nada:

1. Comprueba que la página de `main` está al día con `documentos`. Si no lo está, se lanza `regenera` y se vuelve a intentar.
2. Busca la imagen `sha-<7>` del commit, que tiene que traer amd64 y arm64, y le pone la etiqueta `vX.Y.Z` en el **mismo digest**.
3. Crea una prerelease `vX.Y.Z` en ese commit.
4. Escribe en el overlay de QA la versión y el digest (`newTag` y `digest`: la imagen queda como `…:vX.Y.Z@sha256:…`, y manda el digest). El despliegue lo recoge solo.

Se puede relanzar con la misma versión si falla a mitad: solo se para si esa versión ya apunta a otra imagen u otro commit.

Los manifiestos están, de forma temporal, en un repositorio GitOps de fuera de la organización (D32). El workflow lo saca de dos **secretos**: `GITOPS_REPO`, el nombre, y `GITOPS_SSH_KEY`, una llave de despliegue con escritura solo en ese repositorio. Los logs de este repositorio son públicos y solo los secretos salen enmascarados, así que ni el nombre ni el remoto se imprimen. El paso 4 solo se hace si la variable `ENABLE_BUMP` vale `true`.

**Rotar la llave:** se genera otra (`ssh-keygen -t ed25519 -C transparencia-gitops`), se da de alta como llave de despliegue con escritura en el repositorio GitOps y se borra allí la vieja, se reescribe el secreto (`gh secret set GITOPS_SSH_KEY < <privada>`) y se borra la privada del disco. Cuando la asociación tenga su propio repositorio GitOps, se cambia `GITOPS_REPO`, se mueven los manifiestos y se rota la llave.
