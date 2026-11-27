#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Regenera web/publico desde documentos y, si cambia, lo sube a main en un commit que firma GitHub (#12).

Lo lanza el workflow regenera; ver web/README.md, «Regeneración».

Uso: python3 web/regenera.py [--sin-publicar]
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.parent
PUBLICO = "web/publico"
DOCUMENTOS = Path(os.environ.get("MYCELIUM_DOCUMENTOS", AQUI.parent.parent / "documentos")).resolve()
RAMA = "main"
AUTOR = ("github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com")
CUERPO = "Sale de web/regenera.py (#12): ver web/README.md, «Regeneración»."
MUTACION = ("mutation($input: CreateCommitOnBranchInput!) "
            "{ createCommitOnBranch(input: $input) { commit { oid url } } }")


def para(mensaje):
    raise SystemExit(f"regenera.py: {mensaje}")


def git(*args, env=None, check=True):
    """Lanza git en la raíz del repositorio y devuelve su salida."""
    r = subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True, env=env)
    if check and r.returncode != 0:
        para(f"git {args[0]} ha fallado: {r.stderr.strip()}")
    return r


def salida_github(linea):
    """Escribe una línea en $GITHUB_OUTPUT, si existe."""
    fichero = os.environ.get("GITHUB_OUTPUT")
    if fichero:
        with open(fichero, "a", encoding="utf-8") as f:
            f.write(linea + "\n")


def cambios():
    """Rutas de web/publico añadidas o modificadas, y rutas borradas, respecto a HEAD."""
    r = subprocess.run(
        ["git", "-C", str(RAIZ), "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", PUBLICO],
        capture_output=True, check=True)
    entradas = r.stdout.decode("utf-8").split("\0")
    cambiadas, borradas = set(), set()
    i = 0
    while i < len(entradas):
        entrada = entradas[i]
        i += 1
        if not entrada:
            continue
        xy, ruta = entrada[:2], entrada[3:]
        if xy[0] in "RC":
            i += 1   # la ruta de origen va en la entrada siguiente
        if "D" in xy:
            borradas.add(ruta)
        else:
            cambiadas.add(ruta)
    return sorted(cambiadas), sorted(borradas)


def firmas(html):
    """hash → clase (firmada | sin-firma) de la tabla de cambios de la página."""
    m = re.search(r"<!--G:cambios-->(.*?)<!--/G:cambios-->", html, re.S)
    if not m:
        return {}
    resultado = {}
    for fila in m.group(1).split("<tr>"):
        for h, clase in re.findall(r'commit/([0-9a-f]{40})".*?class="(firmada|sin-firma)"', fila, re.S):
            resultado[h] = clase
    return resultado


def comprobar_firmas():
    """Se para si un cambio que salía Verificada en HEAD ya no lo sale."""
    antes = git("show", f"HEAD:{PUBLICO}/index.html", check=False)
    pagina = RAIZ / PUBLICO / "index.html"
    if antes.returncode != 0 or not pagina.exists():
        return
    viejas = firmas(antes.stdout)
    nuevas = firmas(pagina.read_text(encoding="utf-8"))
    for h, clase in viejas.items():
        if clase == "firmada" and nuevas.get(h) == "sin-firma":
            para(f"el cambio {h[:7]} de documentos salía Verificada y ahora no: "
                 "falta su clave en web/firmantes; no se sube nada")


def commit_de_prueba(titular):
    """Crea, sin mover ninguna rama, el commit que se subiría, y devuelve su hash."""
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        git("read-tree", "HEAD", env=env)
        git("add", "-A", "--", PUBLICO, env=env)
        arbol = git("write-tree", env=env).stdout.strip()
    env = dict(os.environ,
               GIT_AUTHOR_NAME=AUTOR[0], GIT_AUTHOR_EMAIL=AUTOR[1],
               GIT_COMMITTER_NAME=AUTOR[0], GIT_COMMITTER_EMAIL=AUTOR[1])
    return git("commit-tree", "--no-gpg-sign", "-p", "HEAD", "-m", titular, "-m", CUERPO, arbol,
               env=env).stdout.strip()


def publicar(titular, cabeza, cambiadas, borradas):
    """Sube el cambio a main con createCommitOnBranch; GitHub firma el commit."""
    token = os.environ.get("GITHUB_TOKEN")
    repositorio = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repositorio:
        para("faltan GITHUB_TOKEN o GITHUB_REPOSITORY para subir")
    entrada = {
        "branch": {"repositoryNameWithOwner": repositorio, "branchName": RAMA},
        "expectedHeadOid": cabeza,
        "message": {"headline": titular, "body": CUERPO},
        "fileChanges": {
            "additions": [
                {"path": ruta, "contents": base64.b64encode((RAIZ / ruta).read_bytes()).decode("ascii")}
                for ruta in cambiadas],
            "deletions": [{"path": ruta} for ruta in borradas],
        },
    }
    peticion = urllib.request.Request(
        os.environ.get("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql"),
        data=json.dumps({"query": MUTACION, "variables": {"input": entrada}}).encode("utf-8"),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "mycelium-regenera",
        },
        method="POST")
    try:
        with urllib.request.urlopen(peticion, timeout=60) as r:
            respuesta = json.load(r)
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", "replace").replace(token, "***")
        para(f"no se ha subido nada: HTTP {e.code} {cuerpo}")
    except (urllib.error.URLError, OSError, ValueError) as e:
        para(f"no se ha subido nada: {str(e).replace(token, '***')}")
    if respuesta.get("errors"):
        mensajes = "; ".join(str(e.get("message", e)) for e in respuesta["errors"])
        para(f"no se ha subido nada: {mensajes.replace(token, '***')}")
    try:
        commit = respuesta["data"]["createCommitOnBranch"]["commit"]
        oid, url = commit["oid"], commit["url"]
    except (KeyError, TypeError):
        para("no se ha subido nada: la respuesta de GitHub no trae el commit")
    print(f"subido: {oid} {url}")
    salida_github("subido=true")


def main():
    opciones = argparse.ArgumentParser(description="Regenera web/publico y lo sube a main (#12).")
    opciones.add_argument("--sin-publicar", action="store_true",
                          help="dice qué cambiaría y no sube nada")
    args = opciones.parse_args()

    if git("status", "--porcelain", "--", PUBLICO).stdout.strip():
        para("web/publico tiene cambios sin subir; regenera.py parte de lo que hay en HEAD")

    try:
        subprocess.run([sys.executable, "-B", str(AQUI / "genera.py")], check=True)
    except subprocess.CalledProcessError as e:
        para(f"genera.py ha fallado (código {e.returncode})")

    cambiadas, borradas = cambios()
    if not cambiadas and not borradas:
        print("nada que regenerar")
        salida_github("subido=false")
        return 0

    comprobar_firmas()

    corto = subprocess.run(["git", "-C", str(DOCUMENTOS), "rev-parse", "--short=7", "HEAD"],
                           capture_output=True, text=True)
    if corto.returncode != 0:
        para(f"no se puede leer el HEAD de {DOCUMENTOS}: {corto.stderr.strip()}")
    titular = f"Regenera la página desde documentos ({corto.stdout.strip()})"
    cabeza = git("rev-parse", "HEAD").stdout.strip()
    commit = commit_de_prueba(titular)

    guardia = ["bash", str(RAIZ / "scripts" / "guardia.sh"), "commits", f"{cabeza}..{commit}"]
    if subprocess.run(guardia, cwd=RAIZ).returncode != 0:
        para("la guardia no deja subir este cambio; no se sube nada")

    for ruta in cambiadas:
        print(f"cambia: {ruta}")
    for ruta in borradas:
        print(f"borra: {ruta}")
    if args.sin_publicar:
        return 0

    publicar(titular, cabeza, cambiadas, borradas)
    return 0


if __name__ == "__main__":
    main()
