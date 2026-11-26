#!/usr/bin/env python3
"""Digest de triaje del backlog de `transparencia`: una pasada de `gh` y una tabla de señales.

Lee TODAS las issues abiertas de `asociacionmycelium/transparencia` con sus
comentarios (una sola llamada a la API) y emite lo que hace falta para *ordenar*,
no para *entender*: prioridad, quién referencia a quién, a qué otros repos cruza,
qué decisiones (D-NN), asuntos de la Junta (P-NNN) y docs cita, cuántas casillas
quedan y la cola del último comentario. El cuerpo completo se lee después, y solo
el de la lista corta.

Adaptado del script de triaje de otro proyecto. Lo propio de este proyecto:

  1. Prioridad `prioridad-1..4`. Se ordena por prioridad y
     número, y se avisa de las issues sin prioridad o con más de una.
  2. Las issues remiten al registro de decisiones (`docs/01`: «D26»), a los
     asuntos de la Junta (`documentos/junta/pendientes.md`: «P-012») y a los docs
     de diseño (`docs/07-landing.md`, «doc 02»). Se cuentan esas menciones: dicen
     qué hay que leer para entenderla.
  3. Lo que más bloquea aquí no es código sino algo de fuera: un acuerdo de la
     Junta, la inscripción en el Registro, la cuenta bancaria. Esas issues se
     reconocen por la frase fija del último comentario («Espera a la Junta: …») y
     van, dentro de su prioridad, en un grupo aparte de una línea cada una
     (`--completo` saca la ficha entera).

Uso:
    python3 .claude/skills/revisar-backlog/scripts/triaje.py [--json ruta.json] [--completo]

Con --json cachea la respuesta cruda de `gh` en esa ruta y la reutiliza si ya
existe, para no repetir la llamada mientras se itera sobre el mismo backlog.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = "asociacionmycelium/transparencia"
CAMPOS = "number,title,body,labels,comments,createdAt,updatedAt,url,author"

# Referencia a otra issue de ESTE repo: «#123» pero no «#12345678» de un hash,
# ni el «repo#123» de otro repo (lo veta el (?<![\w/#])), ni un color «#E2AE45».
REF = re.compile(r"(?<![\w/#])#(\d{1,4})\b")
# Referencia cross-repo: `documentos#3`, `asociacionmycelium/documentos#3`.
REF_EXTERNA = re.compile(r"(?<![\w/])((?:[A-Za-z][\w.-]*/)?[A-Za-z][\w.-]*)#(\d{1,4})\b")
# «D26», «(D15)», «D1–D24» (cuenta los extremos). No casa «D+3» ni «2D».
DECISION = re.compile(r"(?<![\w-])D(\d{1,3})\b")
# Asuntos para la Junta: «P-012».
JUNTA = re.compile(r"(?<![\w-])P-(\d{3})\b")
# Docs de diseño: «docs/07-landing.md», «docs/07», «doc 02».
DOC = re.compile(r"\bdocs?[/ ]0?(\d)\b")
BLOQUE_CODIGO = re.compile(r"^```.*?^```", re.M | re.S)
CASILLA_HECHA = re.compile(r"^\s*[-*]\s*\[[xX]\]", re.M)
CASILLA_PENDIENTE = re.compile(r"^\s*[-*]\s*\[ \]", re.M)
PRIORIDAD = re.compile(r"^prioridad-(\d)$")
# Frase fija del último comentario cuando la issue no tiene trabajo hasta que pase
# algo de fuera (la escribe `cerrar-sesion`): «Espera a la Junta: P-012»,
# «Espera a la inscripción: …», «Espera a la cuenta bancaria: …», «Sigue abierta
# hasta el 15/12: …».
ESPERA = re.compile(
    r"espera a (?:la |el )?(?:junta|asamblea|inscripci[óo]n|registro|cuenta bancaria)"
    r"|sigue abierta hasta el \d{1,2}/\d{1,2}\b",
    re.I,
)
PIE = re.compile(r"🤖 Generated with \[Claude Code\]\([^)]*\)")


def cargar(cache: str | None) -> list[dict]:
    if cache:
        try:
            with open(cache, encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            pass
    salida = subprocess.run(
        ["gh", "issue", "list", "-R", REPO, "--limit", "200", "--state", "open", "--json", CAMPOS],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    datos = json.loads(salida)
    if cache:
        with open(cache, "w", encoding="utf-8") as fh:
            fh.write(salida)
    return datos


def dias(iso: str) -> int:
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - t).days


def cola(texto: str, chars: int) -> str:
    """Últimos `chars` del texto, en una línea. La conclusión suele estar al final."""
    plano = " ".join((texto or "").split())
    return ("…" + plano[-chars:]) if len(plano) > chars else plano


def casillas(texto: str) -> tuple[int, int]:
    return len(CASILLA_HECHA.findall(texto)), len(CASILLA_PENDIENTE.findall(texto))


def prosa(texto: str) -> str:
    """El texto sin bloques de código: donde están las referencias de verdad."""
    return BLOQUE_CODIGO.sub("", texto or "")


def prioridades(issue: dict) -> list[int]:
    return sorted(
        int(m.group(1)) for l in issue["labels"] if (m := PRIORIDAD.match(l["name"]))
    )


def espera(issue: dict) -> str | None:
    """La frase si el ÚLTIMO comentario dice que la issue espera algo de fuera.

    Solo cuenta el último: un «Espera a la Junta» antiguo seguido de «la Junta lo
    aprobó, sigue» ya no vale. Sin bloques de código y sin el pie «Generated with».
    """
    if not issue["comments"]:
        return None
    texto = PIE.sub("", prosa(issue["comments"][-1]["body"])).replace("**", "")
    plano = " ".join(texto.split())
    m = ESPERA.search(plano)
    if not m:
        return None
    frase = plano[m.start():].strip()
    if len(frase) > 300:
        frase = frase[:120].rstrip() + " … " + frase[-180:].lstrip()
    return frase


def nivel(issue: dict) -> str:
    prio = prioridades(issue)
    return f"prioridad-{prio[0]}" if prio else "sin prioridad"


def ficha(i: dict, abiertas: set[int], entrantes: dict[int, set[int]], chars: int) -> list[str]:
    n = i["number"]
    cuerpo = i["body"] or ""
    coms = i["comments"]
    texto_coms = "\n".join(c["body"] or "" for c in coms)
    todo = prosa(cuerpo + "\n" + texto_coms)
    hechas, pend = casillas(cuerpo)
    hechas_c, pend_c = casillas(texto_coms)
    etiquetas = ",".join(l["name"] for l in i["labels"]) or "-"

    out = [f"## #{n} — {i['title']}"]
    out.append(
        f"- etiquetas: {etiquetas} | creada hace {dias(i['createdAt'])}d, "
        f"tocada hace {dias(i['updatedAt'])}d | cuerpo {len(cuerpo)} chars"
    )
    if hechas or pend:
        out.append(f"- casillas (cuerpo): {hechas} hechas / {pend} pendientes")
    if hechas_c or pend_c:
        out.append(f"- casillas (comentarios): {hechas_c} hechas / {pend_c} pendientes")
    ref = sorted(entrantes[n])
    if ref:
        out.append(f"- ref<- {len(ref)}: {', '.join('#' + str(r) for r in ref)}")
    salientes = sorted({int(m) for m in REF.findall(prosa(cuerpo)) if int(m) in abiertas} - {n})
    if salientes:
        out.append(f"- menciona a: {', '.join('#' + str(s) for s in salientes)}")
    externas = sorted({f"{r}#{num}" for r, num in REF_EXTERNA.findall(todo)})
    if externas:
        out.append(f"- cruza a: {', '.join(externas)}")
    decisiones = sorted({int(d) for d in DECISION.findall(todo)})
    if decisiones:
        out.append(f"- decisiones: {', '.join('D' + str(d) for d in decisiones)}")
    junta = sorted(set(JUNTA.findall(todo)))
    if junta:
        out.append(f"- junta: {', '.join('P-' + p for p in junta)}")
    docs = sorted({int(d) for d in DOC.findall(todo)})
    if docs:
        out.append(f"- docs: {', '.join(f'0{d}' for d in docs)}")
    if coms:
        ultimo = coms[-1]
        fecha = ultimo.get("createdAt", "")[:10]
        out.append(f"- {len(coms)} comentarios; el último ({fecha}) acaba así:")
        out.append(f"  > {cola(ultimo['body'], chars)}")
    else:
        out.append("- sin comentarios")
    out.append("")
    return out


def informe(issues: list[dict], chars: int = 400, completo: bool = False) -> str:
    """El triaje entero como texto. Dentro de cada prioridad, primero lo que tiene
    trabajo (ficha completa) y después lo que espera algo de fuera (una línea y su
    frase; con `completo`, también la ficha)."""
    abiertas = {i["number"] for i in issues}
    # Sin prioridad va al final (9) para que se vea que falta.
    issues = sorted(issues, key=lambda i: ((prioridades(i) or [9])[0], i["number"]))

    # Quién menciona a quién. Solo contamos referencias *desde otra issue abierta*
    # hacia esta: es la señal de taponamiento que buscamos.
    entrantes: dict[int, set[int]] = {n: set() for n in abiertas}
    for i in issues:
        texto = prosa((i["body"] or "") + "\n" + "\n".join(c["body"] or "" for c in i["comments"]))
        for m in REF.findall(texto):
            destino = int(m)
            if destino in abiertas and destino != i["number"]:
                entrantes[destino].add(i["number"])

    esperan_de = {i["number"]: espera(i) for i in issues}
    niveles: dict[str, list[dict]] = {}
    for i in issues:
        niveles.setdefault(nivel(i), []).append(i)

    def cuenta(lista: list[dict]) -> str:
        e = sum(1 for i in lista if esperan_de[i["number"]])
        return f"{len(lista)} ({len(lista) - e} con trabajo, {e} esperan algo de fuera)"

    out: list[str] = []
    sin_prio = [i["number"] for i in issues if not prioridades(i)]
    varias = [i["number"] for i in issues if len(prioridades(i)) > 1]
    out.append(f"# Triaje {REPO}: {len(issues)} issues abiertas, por prioridad y número")
    if not issues:
        out.append("\nNo hay issues abiertas. Mira `docs/06-hoja-de-ruta.md`.")
        return "\n".join(out) + "\n"
    if sin_prio:
        out.append(f"⚠ Sin `prioridad-N`: {', '.join('#' + str(n) for n in sin_prio)}")
    if varias:
        out.append(f"⚠ Con más de una prioridad: {', '.join('#' + str(n) for n in varias)}")
    out.append("")
    for nom, lista in niveles.items():
        out.append(f"- {nom}: {cuenta(lista)}")
    out.append("")
    out.append("Esto mide, no ordena del todo. `ref<-` = issues abiertas que la mencionan;")
    out.append("`cruza a` = otro repo (casi siempre `documentos`); `decisiones`, `junta` y")
    out.append("`docs` = qué leer para entenderla (docs/01, junta/pendientes.md, docs/0N).")
    out.append("«Esperan algo de fuera» sale de la frase del último comentario; su")
    out.append("prioridad no cambia.\n")

    for nom, lista in niveles.items():
        out.append(f"# — {nom}: {cuenta(lista)} —\n")
        for i in lista:
            if not esperan_de[i["number"]]:
                out.extend(ficha(i, abiertas, entrantes, chars))
        en_espera = [i for i in lista if esperan_de[i["number"]]]
        if not en_espera:
            continue
        out.append(f"### Esperan algo de fuera ({len(en_espera)})\n")
        for i in en_espera:
            if completo:
                out.extend(ficha(i, abiertas, entrantes, chars))
                continue
            k = len(entrantes[i["number"]])
            out.append(f"- #{i['number']} — {i['title']}" + (f" · ref<- {k}" if k else ""))
            out.append(f"  > {esperan_de[i['number']]}")
        out.append("")

    out.append("---")
    out.append("Lee el cuerpo completo solo de las que vayan a entrar en la lista corta")
    out.append("(`gh issue view <n> --comments` sale vacío en este entorno; usa --json):")
    out.append(f"  gh issue view <n> -R {REPO} --json body,comments --jq '.body, \"---\", (.comments[] | .body)'")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="cache", default=None)
    ap.add_argument("--cola", type=int, default=400, help="chars del último comentario")
    ap.add_argument(
        "--completo", action="store_true",
        help="ficha entera también de las que esperan algo de fuera",
    )
    args = ap.parse_args()
    sys.stdout.write(informe(cargar(args.cache), args.cola, args.completo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
