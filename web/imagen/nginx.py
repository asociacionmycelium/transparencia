#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Escribe la configuración de nginx de la imagen a partir de web/cabeceras (#15, #12, #25).

web/cabeceras es la única fuente de las cabeceras, en formato `_headers`: una ruta sin sangrar
(`/*` o `/algo/*`) y debajo, con sangría, sus cabeceras. Este script la traduce a nginx:

- `/*` va al nivel de `server`, con `always` para que un 404 también lleve la CSP.
- `/algo/*` pasa a `location /algo/`. En nginx, un `add_header` dentro de una location anula
  todos los heredados, así que allí se repiten los de `/*` y después se ponen los suyos.
- La marca `{NONCE}` se cambia por `$request_id`: 128 bits aleatorios en cada petición. El nonce
  es para el script de detección de bots que inyecta Cloudflare; la página no lleva JavaScript.

Los logs no guardan la IP de quien visita (#25): ni `X-Forwarded-For`, ni `CF-Connecting-IP`, ni
`User-Agent`, ni `Referer`, ni la query. Tampoco hay `real_ip`, así que `$remote_addr` es el del
túnel y no el de la persona.

Se para con un error si el fichero no trae lo imprescindible, para no construir una imagen con
las cabeceras a medias. Solo biblioteca estándar.
"""

import argparse
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = "/srv/pagina"
MARCA_NONCE = "{NONCE}"


class Error(Exception):
    pass


def leer(texto):
    """Devuelve [(ruta, [(cabecera, valor), …]), …] en el orden del fichero."""
    bloques, actual = [], None
    for n, linea in enumerate(texto.splitlines(), 1):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        if not linea[0].isspace():
            actual = (linea.strip(), [])
            bloques.append(actual)
            continue
        if actual is None:
            raise Error(f"línea {n}: cabecera sin ruta delante")
        nombre, dos_puntos, valor = linea.strip().partition(":")
        if not dos_puntos or not re.fullmatch(r"[A-Za-z0-9-]+", nombre.strip()):
            raise Error(f"línea {n}: no es «Cabecera: valor»: {linea.strip()!r}")
        actual[1].append((nombre.strip(), valor.strip()))
    return bloques


def location(ruta):
    """`/*` → None (nivel server); `/algo/*` → `/algo/`. Cualquier otra cosa es un error."""
    if ruta == "/*":
        return None
    m = re.fullmatch(r"(/[a-z0-9-]+(?:/[a-z0-9-]+)*/)\*", ruta)
    if not m:
        raise Error(f"ruta que no sé traducir a nginx: {ruta!r}")
    return m.group(1)


def valor_nginx(nombre, valor):
    if "$" in valor or '"' in valor or "\\" in valor:
        raise Error(f"{nombre}: el valor no puede llevar $, comillas dobles ni \\")
    if MARCA_NONCE in valor:
        if nombre.lower() != "content-security-policy":
            raise Error(f"{nombre}: {MARCA_NONCE} solo vale en la CSP")
        valor = valor.replace(MARCA_NONCE, "$request_id")
    return f'"{valor}"'


def add_headers(cabeceras, sangria):
    return "".join(
        f"{sangria}add_header {nombre} {valor_nginx(nombre, valor)} always;\n"
        for nombre, valor in cabeceras
    )


def comprobar(bloques):
    rutas = [r for r, _ in bloques]
    if len(set(rutas)) != len(rutas):
        raise Error("hay una ruta repetida")
    generales = dict((n.lower(), v) for r, cab in bloques if r == "/*" for n, v in cab)
    if not generales:
        raise Error("falta el bloque /* con las cabeceras de toda la página")
    csp = generales.get("content-security-policy", "")
    directivas = {d.strip().split(" ")[0]: d.strip() for d in csp.split(";") if d.strip()}
    if f"'nonce-{MARCA_NONCE}'" not in directivas.get("script-src", ""):
        raise Error(f"la CSP de /* no lleva script-src con 'nonce-{MARCA_NONCE}'")
    if "unsafe" in csp:
        raise Error("la CSP no puede llevar 'unsafe-…'")
    for falta in ("strict-transport-security", "referrer-policy", "x-content-type-options"):
        if falta not in generales:
            raise Error(f"falta {falta} en /*")


def generar(bloques):
    comprobar(bloques)
    generales = next(cab for r, cab in bloques if r == "/*")
    locations = ""
    for ruta, cabeceras in bloques:
        loc = location(ruta)
        if loc is None:
            continue
        propias = {n.lower() for n, _ in cabeceras}
        heredadas = [(n, v) for n, v in generales if n.lower() not in propias]
        locations += (
            f"\n        # {ruta}: nginx no hereda add_header si la location pone uno propio, así\n"
            f"        # que se repiten aquí las de /*.\n"
            f"        location {loc} {{\n"
            f"{add_headers(heredadas + cabeceras, ' ' * 12)}"
            f"        }}\n"
        )
    return f"""\
# GENERADO por web/imagen/nginx.py desde web/cabeceras. No se edita a mano.
worker_processes auto;
pid /tmp/nginx.pid;
error_log /dev/stderr warn;

events {{
    worker_connections 1024;
}}

http {{
    # Raíz de solo lectura: todo lo que nginx escribe va a /tmp.
    client_body_temp_path /tmp/client_temp;
    proxy_temp_path /tmp/proxy_temp;
    fastcgi_temp_path /tmp/fastcgi_temp;
    uwsgi_temp_path /tmp/uwsgi_temp;
    scgi_temp_path /tmp/scgi_temp;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    charset utf-8;
    charset_types text/css text/plain image/svg+xml;

    # Sin la IP de quien visita (#25): ni $remote_addr, ni X-Forwarded-For, ni CF-Connecting-IP,
    # ni User-Agent, ni Referer, ni la query. Hora, método, ruta, estado, bytes y tiempo.
    log_format sinip '$time_iso8601 "$request_method $uri $server_protocol" '
                     '$status $body_bytes_sent $request_time';
    access_log /dev/stdout sinip;
    # Un 404 no va al error_log, que sí apuntaría el cliente y el Referer.
    log_not_found off;

    sendfile on;
    keepalive_timeout 65;
    server_tokens off;
    gzip on;
    gzip_types text/css image/svg+xml text/plain;

    server {{
        listen 8080;
        root {RAIZ};
        index index.html;
        # Detrás del túnel, una redirección absoluta saldría con http:// y el puerto 8080.
        absolute_redirect off;

        # /*
{add_headers(generales, ' ' * 8)}
        location / {{
            try_files $uri $uri/ =404;
        }}
{locations}    }}
}}
"""


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--cabeceras", type=pathlib.Path, default=AQUI.parent / "cabeceras")
    p.add_argument("--salida", type=pathlib.Path, help="por defecto, a la salida estándar")
    a = p.parse_args()
    try:
        conf = generar(leer(a.cabeceras.read_text(encoding="utf-8")))
    except (Error, OSError) as e:
        sys.exit(f"nginx.py: {e}")
    if a.salida:
        a.salida.write_text(conf, encoding="utf-8")
    else:
        sys.stdout.write(conf)


if __name__ == "__main__":
    main()
