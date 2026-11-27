#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Fase 0 y casos automáticos de /validar-qa (transparencia).

    python3 -B .claude/skills/validar-qa/scripts/qa.py vX.Y.Z --url http://127.0.0.1:18090

`--url` es QA tal como se sirve, normalmente por `kubectl port-forward` al Service de QA. QA solo
está en la red local, y su dirección no se escribe en este repositorio público.

Solo lee: kubectl get/logs en transparencia-qa y argocd, gh api en GET, git y peticiones HTTP a
QA y a GHCR. Lo único que «escribe» es una petición de prueba con cabeceras inventadas (L1), que
deja una línea en el log de nginx.

Escribe una línea por caso, `ID ✔|✖|— texto`, y al final un resumen. Sale con 0 si no hay ningún
✖ y con 1 si lo hay. Lo que sale aquí va al informe tal cual: no imprime direcciones de la red
local, nombres de nodo ni nada del repositorio de despliegue.
"""

import argparse
import hashlib
import http.client
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
RAIZ = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ / "web" / "imagen"))
import nginx  # noqa: E402  (el mismo lector de web/cabeceras que la imagen)

REPO = "asociacionmycelium/transparencia"
IMAGEN = "ghcr.io/asociacionmycelium/transparencia-web"
NS = "transparencia-qa"
APP = "transparencia-qa"
DEPLOY = "transparencia-web"

resultados = []  # (id, estado, texto)


def caso(cid, bien, texto):
    estado = "—" if bien is None else ("✔" if bien else "✖")
    resultados.append((cid, estado, texto))
    print(f"{cid} {estado} {texto}", flush=True)
    return bien


def sh(*cmd, entrada=None):
    """Ejecuta en la raíz del repositorio. Si falla, el detalle va a stderr y nunca a la salida que
    se copia al informe: el stderr de kubectl puede llevar la dirección del clúster."""
    r = subprocess.run(cmd, capture_output=True, text=True, input=entrada, cwd=RAIZ)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sub = next((c for c in cmd[1:] if c in ("get", "logs", "api", "fetch", "show", "rev-list", "ls-tree")), "")
        raise RuntimeError(f"`{cmd[0]} {sub}` falló (código {r.returncode}); el detalle está en stderr")
    return r.stdout


def kjson(*args):
    return json.loads(sh("kubectl", *args, "-o", "json"))


# ── GHCR, sin docker: el digest de una etiqueta por la API del registro ─────────────────────────
def digest_ghcr(etiqueta):
    repo = IMAGEN.split("/", 1)[1]
    with urllib.request.urlopen(f"https://ghcr.io/token?scope=repository:{repo}:pull", timeout=15) as r:
        token = json.load(r)["token"]
    req = urllib.request.Request(
        f"https://ghcr.io/v2/{repo}/manifests/{etiqueta}", method="HEAD",
        headers={"Authorization": f"Bearer {token}", "Accept": ", ".join([
            "application/vnd.oci.image.index.v1+json",
            "application/vnd.docker.distribution.manifest.list.v2+json"])})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.headers["Docker-Content-Digest"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def pedir(base, ruta, cabeceras=None):
    u = urllib.parse.urlsplit(base)
    c = (http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection)(u.netloc, timeout=10)
    c.request("GET", ruta, headers={"User-Agent": "validar-qa", **(cabeceras or {})})
    r = c.getresponse()
    cuerpo = r.read()
    c.close()
    return r.status, r.headers, cuerpo


# ── Fase 0 ───────────────────────────────────────────────────────────────────────────────────────
def fase0(version):
    """Devuelve (digest, commit) o None si algo corta la validación."""
    corta = False
    dep = kjson("-n", NS, "get", "deploy", DEPLOY)
    imagen = dep["spec"]["template"]["spec"]["containers"][0]["image"]
    m = re.fullmatch(re.escape(IMAGEN) + r":(v\d+\.\d+\.\d+)@(sha256:[0-9a-f]{64})", imagen)
    if not caso("F0a", bool(m) and m.group(1) == version,
                f"QA corre `{imagen.split('/')[-1][:60]}…`" if m else f"QA no corre una versión fijada por digest: `{imagen}`"):
        return None
    digest = m.group(2)

    ghcr = digest_ghcr(version)
    corta |= not caso("F0b", ghcr == digest, f"`{version}` en GHCR es `{(ghcr or 'no existe')[:19]}…`, QA `{digest[:19]}…`")

    pods = kjson("-n", NS, "get", "pods", "-l", "app=" + DEPLOY)["items"]
    malos = [p for p in pods if not all(
        s.get("ready") and s.get("imageID", "").endswith(digest) for s in p["status"].get("containerStatuses", []))]
    reinicios = sum(s.get("restartCount", 0) for p in pods for s in p["status"].get("containerStatuses", []))
    arqs = set()
    for p in pods:
        nodo = kjson("get", "node", p["spec"]["nodeName"])
        arqs.add(nodo["status"]["nodeInfo"]["architecture"])
    corta |= not caso("F0c", pods and not malos,
                      f"{len(pods)} pod(s) listos con ese digest, {reinicios} reinicios, en {','.join(sorted(arqs))}")

    app = kjson("-n", "argocd", "get", "applications.argoproj.io", APP)
    estado = f"{app['status']['sync']['status']}/{app['status']['health']['status']}"
    corta |= not caso("F0d", estado == "Synced/Healthy", f"ArgoCD `{estado}`")

    sh("git", "fetch", "-q", "--tags", "origin")
    try:
        commit = sh("git", "rev-list", "-n1", version).strip()
    except RuntimeError:
        caso("F0e", False, f"no existe la etiqueta git `{version}`")
        return None
    origen = digest_ghcr("sha-" + commit[:7])
    corta |= not caso("F0e", origen == digest,
                      f"la etiqueta `{version}` es el commit `{commit[:7]}`, y su imagen `sha-{commit[:7]}` "
                      + ("es la misma" if origen == digest else f"es otra (`{(origen or 'no existe')[:19]}…`)"))
    return None if corta else (digest, commit)


def epica(version):
    """El guardarraíl del flujo automático (D30): la épica de la versión deja validarla."""
    def gh(ruta):
        return json.loads(sh("gh", "api", ruta))

    def todas(ruta):
        sep = "&" if "?" in ruta else "?"
        out, pag = [], 1
        while True:
            lote = gh(f"{ruta}{sep}per_page=100&page={pag}")
            out += lote
            if len(lote) < 100:
                return out
            pag += 1

    patron = re.compile(r"^[\s*_\[]*" + re.escape(version) + r"\b")
    vistas = {}
    for etiqueta in ("flow:release-lista", "flow:release-bloqueada"):
        for i in todas(f"repos/{REPO}/issues?state=all&labels={urllib.parse.quote(etiqueta)}"):
            if "pull_request" not in i and patron.match(i["title"]):
                vistas[i["number"]] = i
    if len(vistas) != 1:
        return caso("F0f", False, f"{'ninguna épica' if not vistas else 'varias épicas'} con `{version}` al principio del "
                    "título y etiqueta `flow:release-*`: el flow no ha dicho si se puede validar")
    n, issue = next(iter(vistas.items()))
    reflejos = [c for c in todas(f"repos/{REPO}/issues/{n}/comments") if "<!-- aidev-release:" in (c.get("body") or "")]
    if not reflejos:
        return caso("F0f", False, f"#{n} no tiene comentario «flow · release»")
    ult = reflejos[-1]
    datos = json.loads(re.search(r"<!-- aidev-release: (\{.*?\}) -->", ult["body"]).group(1))
    fecha = ult["created_at"][:10]
    if datos.get("version") != version:
        return caso("F0f", False, f"#{n} · reflejo del {fecha} es de `{datos.get('version')}`, no de `{version}`")
    if datos.get("lista") is not True:
        return caso("F0f", False, f"#{n} · reflejo del {fecha} · bloquean {datos.get('bloquean')}")
    # Contraste: casillas sin marcar cuya issue sigue abierta, fuera de «Fuera del flow».
    conocidas = set(datos.get("abiertas", [])) | set(datos.get("bloquean", []))
    faltan, fuera, nivel_fuera = [], False, 0
    for linea in (issue.get("body") or "").splitlines():
        t = re.match(r"^(#{1,6})\s+(.*)", linea)
        if t:
            nivel = len(t.group(1))
            if fuera and nivel <= nivel_fuera:
                fuera = False
            if re.search(r"fuera del flow", t.group(2), re.I):
                fuera, nivel_fuera = True, nivel
            continue
        c = re.match(r"^\s*[-*]\s+\[ \]\s+#(\d+)", linea)
        if c and not fuera:
            num = int(c.group(1))
            if num not in conocidas and gh(f"repos/{REPO}/issues/{num}")["state"] == "open":
                faltan.append(num)
    return caso("F0f", not faltan, f"#{n} · reflejo del {fecha} · lista" + (f", pero faltan {faltan}" if faltan else ", contraste bien"))


# ── Frentes automáticos ──────────────────────────────────────────────────────────────────────────
def servidor(url, commit):
    with tempfile.TemporaryDirectory() as d:
        cab = pathlib.Path(d) / "cabeceras"
        cab.write_text(sh("git", "show", f"{commit}:web/cabeceras"), encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", str(RAIZ / "web/imagen/comprueba.py"), url, "--cabeceras", str(cab)],
                           capture_output=True, text=True)
        fallos = [l for l in r.stderr.splitlines() if l.startswith("FALLA")]
        caso("S1", r.returncode == 0, (r.stdout.strip().splitlines() or ["sin salida"])[-1] if r.returncode == 0
             else "; ".join(fallos)[:400])
    pod = kjson("-n", NS, "get", "pods", "-l", "app=" + DEPLOY)["items"][0]
    sc_pod = pod["spec"].get("securityContext", {})
    sc = pod["spec"]["containers"][0].get("securityContext", {})
    bien = (sc_pod.get("runAsUser") == 101 and sc_pod.get("runAsNonRoot") is True and sc.get("readOnlyRootFilesystem") is True
            and sc.get("allowPrivilegeEscalation") is False and sc.get("capabilities", {}).get("drop") == ["ALL"])
    caso("S2", bien, "uid 101, sin root, raíz de solo lectura, sin escalada, sin capacidades" if bien else f"securityContext: {sc_pod} {sc}")
    st, h, _ = pedir(url, "/fuentes")
    caso("S3", st == 301 and h.get("Location") == "/fuentes/", f"/fuentes → {st} `{h.get('Location')}` (relativa)")


def contenido(url, commit):
    rutas = sh("git", "ls-tree", "-r", "--name-only", commit, "web/publico").split()
    distintos = []
    for r in rutas:
        esperado = subprocess.run(["git", "show", f"{commit}:{r}"], capture_output=True, cwd=RAIZ).stdout
        st, _, cuerpo = pedir(url, "/" + r[len("web/publico/"):])
        if st != 200 or hashlib.sha256(cuerpo).digest() != hashlib.sha256(esperado).digest():
            distintos.append(f"{r} ({st})")
    caso("C1", not distintos, f"{len(rutas)} ficheros servidos idénticos a `web/publico` de `{commit[:7]}`"
         if not distintos else f"distintos: {distintos}")

    _, _, html = pedir(url, "/")
    _, _, css = pedir(url, "/estilo.css")
    html, css = html.decode("utf-8"), css.decode("utf-8")
    sin_comentarios = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    externos = re.findall(r"<(?:link|img|script|iframe|source|video|audio|embed|object)\b[^>]*\b(?:src|href|srcset)=\"((?:https?:)?//[^\"]+)\"",
                          sin_comentarios, re.I)
    externos += re.findall(r"url\(\s*['\"]?((?:https?:)?//[^)'\"]+)", css) + re.findall(r"@import", css)
    caso("C2", not externos, "ningún recurso de terceros en el HTML ni en el CSS" if not externos else f"de fuera: {externos}")
    prohibido = re.findall(r"<script\b|<style\b|\sstyle\s*=|\son[a-z]+\s*=", sin_comentarios, re.I)
    caso("C3", not prohibido, "sin `<script>`, `<style>`, `style=` ni manejadores `on…=`" if not prohibido else f"encontrado: {set(prohibido)}")
    hay_privacidad = any(re.search(r"privacidad", r) for r in rutas)
    noindex = re.search(r"<meta\s+name=\"robots\"\s+content=\"[^\"]*noindex", html) is not None
    caso("C4", noindex or hay_privacidad, "lleva `noindex` (D33: hasta que esté la página de privacidad, #26)" if noindex
         else ("sin `noindex`, y hay página de privacidad" if hay_privacidad else "sin `noindex` y sin página de privacidad (D33)"))


def logs(url):
    marcas = {"X-Forwarded-For": "203.0.113.7", "CF-Connecting-IP": "198.51.100.9", "Referer": "https://referente.example/"}
    pedir(url, "/?q=consulta-de-prueba", {**marcas, "User-Agent": "agente-de-prueba"})
    texto = ""
    for p in kjson("-n", NS, "get", "pods", "-l", "app=" + DEPLOY)["items"]:
        texto += sh("kubectl", "-n", NS, "logs", p["metadata"]["name"], "--since=10m")
    hallado = [v for v in [*marcas.values(), "agente-de-prueba", "consulta-de-prueba", "referente.example"] if v in texto]
    caso("L1", not hallado and "consulta-de-prueba" not in texto,
         "los logs no guardan IP, User-Agent, Referer ni query (petición con valores inventados)" if not hallado
         else f"aparecen en los logs: {hallado}")
    st, h, _ = pedir(url, "/")
    caso("L2", not h.get_all("Set-Cookie"), "nginx no pone cookies")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("version")
    p.add_argument("--url", required=True, help="QA tal como se sirve (port-forward)")
    p.add_argument("--solo-fase0", action="store_true")
    a = p.parse_args()
    if not re.fullmatch(r"v\d+\.\d+\.\d+", a.version):
        sys.exit("versión no válida (vX.Y.Z)")
    listo = None  # None: la épica no llegó a mirarse
    try:
        f0 = fase0(a.version)
        listo = epica(a.version)
        if f0 is None:
            print("\nCORTA EN LA FASE 0: no se sabe contra qué se valida. NO CONCLUYENTE.")
            sys.exit(1)
        if not a.solo_fase0:
            digest, commit = f0
            servidor(a.url, commit)
            contenido(a.url, commit)
            logs(a.url)
    except RuntimeError as e:
        caso("ERR", False, f"no se pudo ejercer: {e}")
    except Exception as e:  # noqa: BLE001  (nunca un traceback en la salida que va al informe)
        import traceback
        traceback.print_exc(file=sys.stderr)
        caso("ERR", False, f"no se pudo ejercer: {type(e).__name__}; el detalle está en stderr")
    malos = [c for c, e, _ in resultados if e == "✖"]
    print(f"\n{len(resultados)} casos · {len(malos)} ✖ {malos if malos else ''}".rstrip())
    if listo is False:
        print("La épica no deja validar (F0f): como mucho, NO CONCLUYENTE.")
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
