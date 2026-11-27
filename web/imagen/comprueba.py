#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Comprueba que la página servida lleva las cabeceras de web/cabeceras (#15, #12).

    python3 web/imagen/comprueba.py http://127.0.0.1:8080

Lo usa el CI contra la imagen recién construida, y sirve igual contra QA desde la red local. Mira
la raíz, una fuente y una ruta que no existe (un 404 también tiene que llevar la CSP). Compara cada
cabecera con web/cabeceras, con el nonce como 32 caracteres hexadecimales que cambian en cada
petición, y además que no hay cookies y que el servidor no dice su versión.

No vale tal cual contra prod: allí Cloudflare añade sus cookies (__cf_bm, cf_clearance) y su
script. Las comprobaciones de prod están en web/README.md, «Imagen».

Sale con 0 si todo está bien; si no, dice qué falla y sale con 1. Solo biblioteca estándar.
"""

import argparse
import http.client
import pathlib
import re
import sys
import urllib.parse

AQUI = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # no dejar __pycache__ en web/imagen
sys.path.insert(0, str(AQUI))
import nginx  # noqa: E402  (mismo lector de web/cabeceras que el generador)

NONCE = re.compile(r"[0-9a-f]{32}")


def pedir(base, ruta):
    u = urllib.parse.urlsplit(base)
    clase = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    c = clase(u.netloc, timeout=10)
    c.request("GET", ruta, headers={"User-Agent": "comprueba.py"})
    r = c.getresponse()
    r.read()
    c.close()
    return r.status, r.headers


def esperadas(bloques, ruta):
    """Las cabeceras que tocan en `ruta`: las de /* y, encima, las del bloque más largo que case."""
    generales = dict((n.lower(), v) for n, v in next(c for r, c in bloques if r == "/*"))
    cab = dict(generales)
    for r, c in bloques:
        loc = nginx.location(r)
        if loc and ruta.startswith(loc):
            cab.update((n.lower(), v) for n, v in c)
    return cab


def casa(esperado, recibido):
    """Igualdad exacta, salvo {NONCE}, que tiene que ser un nonce de 32 hex. Devuelve el nonce."""
    partes = esperado.split(nginx.MARCA_NONCE)
    patron = "(" + NONCE.pattern + ")"
    m = re.fullmatch(patron.join(map(re.escape, partes)), recibido or "")
    if not m:
        return False, None
    return True, (m.group(1) if len(partes) > 1 else None)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("base", help="p. ej. http://127.0.0.1:8080")
    p.add_argument("--cabeceras", type=pathlib.Path, default=AQUI.parent / "cabeceras")
    p.add_argument("--fuente", default=None, help="ruta de una fuente; por defecto, la primera de publico/fuentes")
    a = p.parse_args()

    bloques = nginx.leer(a.cabeceras.read_text(encoding="utf-8"))
    nginx.comprobar(bloques)
    fuente = a.fuente
    if fuente is None:
        woff = sorted((AQUI.parent / "publico" / "fuentes").glob("*.woff2"))
        fuente = "/fuentes/" + woff[0].name if woff else None

    fallos, nonces = [], []
    casos = [("/", 200), ("/no-existe-" + "x" * 8, 404)] + ([(fuente, 200)] if fuente else [])
    for ruta, estado in casos + [("/", 200)]:
        st, h = pedir(a.base, ruta)
        if st != estado:
            fallos.append(f"{ruta}: estado {st}, esperaba {estado}")
        for nombre, valor in esperadas(bloques, ruta).items():
            bien, nonce = casa(valor, h.get(nombre))
            if not bien:
                fallos.append(f"{ruta}: {nombre} es {h.get(nombre)!r}, esperaba {valor!r}")
            if nonce:
                nonces.append(nonce)
        if h.get_all("Set-Cookie"):
            fallos.append(f"{ruta}: pone cookies: {h.get_all('Set-Cookie')}")
        if re.search(r"\d", h.get("Server", "")):
            fallos.append(f"{ruta}: el servidor dice su versión: {h.get('Server')!r}")
        print(f"{st} {ruta}")
    if len(nonces) != len(set(nonces)):
        fallos.append(f"el nonce se repite entre peticiones: {nonces}")

    for f in fallos:
        print("FALLA", f, file=sys.stderr)
    if fallos:
        sys.exit(1)
    print(f"bien: {len(casos) + 1} peticiones, cabeceras de {a.cabeceras.name}, {len(nonces)} nonces distintos")


if __name__ == "__main__":
    main()
