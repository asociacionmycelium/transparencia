#!/usr/bin/env python3
"""Rellena web/publico/index.html con lo que existe de verdad hoy.

Todo lo que hay entre <!--G:nombre--> y <!--/G:nombre--> lo escribe este
guion a partir de las fuentes reales, nunca a mano:

  manifiesto, a-la-vista, invitacion   documentos/manifiesto.md
  cambios                              git log de documentos (sin autor)
  asuntos                              documentos/junta/pendientes.md
  red, setas                           la red de filamentos (sin lotes todavía)

El único dato escrito aquí es ESTADO (constitución e inscripción), porque no
tiene otra fuente. La maqueta de demo/ es la guía de diseño y no se toca: lo
que aquí falta (cuentas, acuerdos, propuestas, datos) está allí con datos de
ejemplo, y llega a esta página cuando haya datos de verdad (issues #2 a #5).

La página no lleva JavaScript: lo que haya que calcular se calcula aquí.

Uso: python3 web/genera.py   (solo biblioteca estándar; se puede repetir)
     MYCELIUM_DOCUMENTOS=/ruta/a/documentos python3 web/genera.py
"""
import hashlib
import math
import os
import random
import re
import subprocess
import sys
from html import escape
from pathlib import Path

AQUI = Path(__file__).parent
PAGINA = AQUI / "publico" / "index.html"
DOCUMENTOS = Path(os.environ.get("MYCELIUM_DOCUMENTOS", AQUI.parent.parent / "documentos")).resolve()
GITHUB_DOCUMENTOS = "https://github.com/asociacionmycelium/documentos"

# Estado del registro. Es lo único que se escribe a mano: cambia cuando el
# Registro Nacional de Asociaciones resuelva (ver docs/07-landing.md).
ESTADO = dict(constituida="2026-11-09", inscrita=None)

N_CAMBIOS = 8
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()


def para(mensaje):
    raise SystemExit(f"genera.py: {mensaje}")


def fecha_corta(iso):
    a, m, d = iso.split("-")
    return f"{int(d)}/{int(m)}/{a}"


def fecha_larga(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def en_linea(texto):
    """Markdown en línea mínimo: enlaces, **negrita**, *cursiva* y `código`."""
    out = escape(texto, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{escape(m.group(2))}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


def texto_plano(texto):
    """Lo mismo, pero sin marcas: para frases cortas en una tabla."""
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)
    return re.sub(r"[*`]", "", texto).strip()


# ---------- Manifiesto ----------

def leer(ruta):
    try:
        return ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        para(f"no encuentro {ruta}. ¿Está el repositorio documentos al lado? (MYCELIUM_DOCUMENTOS)")


def manifiesto():
    """Divide manifiesto.md en la frase de cabecera y sus secciones ##.

    Antes de la primera sección, el párrafo en negrita es el h1; los demás
    párrafos de entrada (la nota de que no es un texto jurídico) se quedan en
    el documento enlazado.
    """
    entrada, secciones, actual = [], [], None
    for bloque in re.split(r"\n\s*\n", leer(DOCUMENTOS / "manifiesto.md").strip()):
        bloque = " ".join(l.strip() for l in bloque.splitlines())
        if bloque.startswith("# "):
            continue
        if bloque.startswith("## "):
            actual = (bloque[3:].strip(), [])
            secciones.append(actual)
        elif actual:
            actual[1].append(bloque)
        else:
            entrada.append(bloque)
    titular = next((b[2:-2] for b in entrada if re.fullmatch(r"\*\*[^*]+\*\*", b)), None)
    if not titular:
        para("manifiesto.md no tiene la frase de cabecera en negrita")
    return titular, secciones


def parrafos(lista, sangria="      "):
    return "\n".join(f"{sangria}<p>{en_linea(p)}</p>" for p in lista)


def bloques_manifiesto():
    titular, secciones = manifiesto()
    nombres = [n for n, _ in secciones]
    for fija in ("A la vista de todos", "Una invitación"):
        if fija not in nombres:
            para(f"manifiesto.md no tiene la sección «{fija}»; la página la necesita")
    corte = nombres.index("A la vista de todos")
    sobrantes = [n for n in nombres[corte:] if n not in ("A la vista de todos", "Una invitación")]
    if sobrantes:
        para(f"no sé dónde poner estas secciones del manifiesto: {', '.join(sobrantes)}")

    inscripcion = ("La inscripción en el Registro Nacional de Asociaciones está en trámite."
                   if not ESTADO["inscrita"] else
                   f"Inscrita en el Registro Nacional de Asociaciones el {fecha_larga(ESTADO['inscrita'])}.")
    superficie = [
        f"\n    <h1>{en_linea(titular)}</h1>",
        f'    <p class="estado">Constituida el {fecha_larga(ESTADO["constituida"])}. {inscripcion}</p>',
    ]
    for nombre, ps in secciones[:corte]:
        superficie.append(f'    <section class="tramo">\n      <h2>{en_linea(nombre)}</h2>\n'
                          f'      <div>\n{parrafos(ps, "        ")}\n      </div>\n    </section>')
    dict_secciones = dict(secciones)
    return {
        "manifiesto": "\n\n".join(superficie) + "\n  ",
        "a-la-vista": "\n" + parrafos(dict_secciones["A la vista de todos"]) + "\n      ",
        "invitacion": "\n" + parrafos(dict_secciones["Una invitación"]) + "\n      ",
    }


# ---------- Cambios firmados de documentos ----------

def cambios():
    """Últimos commits de documentos: fecha, qué cambió y si la firma es buena.

    Sin autor a propósito: junto al cargo, identificaría a una persona.
    La firma se comprueba con la configuración de git de esta máquina
    (%G?); si no da «G», la página no la da por buena.
    """
    try:
        salida = subprocess.run(
            ["git", "-C", str(DOCUMENTOS), "log", f"-n{N_CAMBIOS}", "--format=%H%x1f%cs%x1f%G?%x1f%s"],
            check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        para(f"no puedo leer el historial de {DOCUMENTOS}: {e}")
    filas = []
    for linea in salida.splitlines():
        h, dia, firma, asunto = linea.split("\x1f", 3)
        if firma == "G":
            celda = '<span class="firmada">Verificada</span>'
        else:
            print(f"aviso: el cambio {h[:7]} no tiene una firma comprobada aquí ({firma})", file=sys.stderr)
            celda = '<span class="sin-firma">No comprobada</span>'
        filas.append(
            f'<tr><td><a href="{GITHUB_DOCUMENTOS}/commit/{h}"><code>{h[:7]}</code></a></td>'
            f"<td>{fecha_corta(dia)}</td><td>{escape(asunto)}</td><td>{celda}</td></tr>")
    if not filas:
        para("documentos no tiene ningún cambio")
    return "\n".join(filas)


# ---------- Asuntos de la Junta ----------

CABECERA_ASUNTOS = ["Id", "Asunto", "Tipo", "Origen", "Estado"]


def primera_frase(texto):
    # Corta en un punto seguido de mayúscula: «art. 46.3» no corta.
    return re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", texto, maxsplit=1)[0].rstrip(".") + "."


def asuntos():
    """Una fila por asunto de junta/pendientes.md: id, primera frase y estado."""
    filas, cabecera = [], None
    for linea in leer(DOCUMENTOS / "junta" / "pendientes.md").splitlines():
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if cabecera is None:
            cabecera = celdas
            if cabecera != CABECERA_ASUNTOS:
                para(f"la tabla de pendientes.md ha cambiado de columnas: {cabecera}")
            continue
        if set("".join(celdas)) <= set("-: "):
            continue
        if len(celdas) != len(CABECERA_ASUNTOS):
            para(f"fila de pendientes.md con {len(celdas)} columnas: {linea[:60]}…")
        a = dict(zip(CABECERA_ASUNTOS, celdas))
        filas.append(f'<tr><td>{escape(a["Id"])}</td><td>{escape(primera_frase(texto_plano(a["Asunto"])))}</td>'
                     f'<td>{escape(texto_plano(a["Estado"]))}</td></tr>')
    if not filas:
        para("pendientes.md no tiene asuntos")
    return "\n".join(filas)


# ---------- Red de filamentos (de demo/genera.py) ----------

ANCHO, ALTO = 1000, 6000
# La red ocupa solo la franja derecha (de IZQ a ANCHO): el texto queda limpio.
IZQ = 570
BROTES = [835, 715, 940, 610]               # de aquí salen los filamentos y las setas
SETAS = [(835, 106, 52), (715, 80, 40), (940, 60, 30), (610, 44, 24)]  # x, alto, radio


def trazo(pts):
    """Curva suave que pasa por los puntos medios (cuadráticas encadenadas)."""
    if len(pts) < 3:
        return "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    d = f"M{pts[0][0]:.0f} {pts[0][1]:.0f}Q{pts[1][0]:.0f} {pts[1][1]:.0f} " \
        f"{(pts[1][0] + pts[2][0]) / 2:.0f} {(pts[1][1] + pts[2][1]) / 2:.0f}"
    for i in range(2, len(pts) - 1):
        d += f"T{(pts[i][0] + pts[i + 1][0]) / 2:.0f} {(pts[i][1] + pts[i + 1][1]) / 2:.0f}"
    return d + f"T{pts[-1][0]:.0f} {pts[-1][1]:.0f}"


def red(semilla, brotes, densa):
    """Densa cuando haya lotes (semilla: huella del último, issue #2); escasa sin ellos."""
    rng = random.Random(int(semilla, 16))
    paso = 30
    if densa:
        vida0, ramifica, max_gen = 400, [0.06, 0.04, 0.025], 3
        vida = [None, (22, 60), (10, 30), (5, 14)]
    else:
        vida0, ramifica, max_gen = 46, [0.07, 0.0, 0.0], 1
        vida = [None, (6, 18)]
    cola = [(x, 0.0, math.pi / 2 + rng.uniform(-0.2, 0.2), 0, vida0 + rng.randint(-8, 8) * (not densa))
            for x in brotes]
    trazos = []
    while cola and len(trazos) < 520:
        x, y, ang, gen, pasos = cola.pop(0)
        pts = [(x, y)]
        for _ in range(pasos):
            ang += rng.gauss(0, 0.2)
            ang += (math.pi / 2 - ang) * (0.06 if gen == 0 else 0.012)
            if x < IZQ + 90:               # cerca del texto, se aparta poco a poco
                ang -= 0.12 * math.sin(ang)
            x += math.cos(ang) * paso
            y += math.sin(ang) * paso
            if y < 12:
                y, ang = 12, -ang
            if not IZQ < x < ANCHO - 15:   # rebota en los bordes en vez de salirse
                x, ang = min(max(x, IZQ), ANCHO - 15), math.pi - ang
            if y > ALTO:
                break
            pts.append((x, y))
            if gen < max_gen and rng.random() < ramifica[gen]:
                lo, hi = vida[gen + 1]
                cola.append((x, y, ang + rng.choice([-1, 1]) * rng.uniform(0.5, 1.15),
                             gen + 1, rng.randint(lo, hi)))
        if len(pts) > 1:
            trazos.append((pts, gen))

    partes = [f'<svg viewBox="0 0 {ANCHO} {ALTO}" role="presentation">']
    for pts, gen in trazos:
        y0 = pts[0][1]
        y1 = max(p[1] for p in pts)
        # Tramo del scroll en el que crece: de cuando asoma a cuando está entero.
        i = y0 / ALTO * 88 + 2
        f = max(y1 / ALTO * 88 + 7, i + 3)
        partes.append(f'<path class="g{gen}" pathLength="1" style="--i:{i:.1f}%;--f:{f:.1f}%" d="{trazo(pts)}"/>')
    partes.append("</svg>")
    return "\n".join(partes), len(trazos)


def setas():
    alto = 170
    partes = [f'<svg viewBox="0 0 {ANCHO} {alto}" role="presentation">']
    for x, h, r in SETAS:
        base, pie, c = alto, r * 0.2, r * 0.82
        cy = base - h
        partes.append(
            f'<path d="M{x - pie:.0f} {base}L{x - pie * 0.7:.0f} {cy:.0f}L{x + pie * 0.7:.0f} {cy:.0f}L{x + pie:.0f} {base}Z'
            f'M{x - r} {cy:.0f}Q{x - r} {cy - c:.0f} {x} {cy - c * 1.06:.0f}Q{x + r} {cy - c:.0f} {x + r} {cy:.0f}'
            f'Q{x} {cy + r * 0.2:.0f} {x - r} {cy:.0f}Z"/>')
    partes.append("</svg>")
    return "\n".join(partes)


# ---------- Montaje ----------

def main():
    # Sin lotes todavía: unos pocos filamentos, sembrados con el nombre.
    red_vacia, n0 = red(hashlib.sha256("Asociación Mycelium".encode()).hexdigest(), BROTES[:3], densa=False)
    bloques = {
        **bloques_manifiesto(),
        "cambios": cambios(),
        "asuntos": asuntos(),
        "setas": setas(),
        "red": red_vacia,
    }
    html = PAGINA.read_text(encoding="utf-8")
    for nombre, contenido in bloques.items():
        patron = re.compile(rf"(<!--G:{nombre}-->).*?(<!--/G:{nombre}-->)", re.S)
        if not patron.search(html):
            para(f"falta el hueco {nombre} en {PAGINA}")
        html = patron.sub(lambda m: m.group(1) + contenido + m.group(2), html)
    PAGINA.write_text(html, encoding="utf-8")
    print(f"fuentes: {DOCUMENTOS}\nfilamentos: {n0}\n{len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
