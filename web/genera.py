#!/usr/bin/env python3
"""Rellena web/publico/index.html con lo que existe de verdad hoy.

Todo lo que hay entre <!--G:nombre--> y <!--/G:nombre--> lo escribe este
guion a partir de las fuentes reales, nunca a mano:

  manifiesto, a-la-vista, invitacion   documentos/manifiesto.md
  cambios                              git log de documentos (sin autor)
  asuntos                              documentos/junta/pendientes.md
  red, setas                           la red de filamentos (sin lotes todavía)
  tarjeta (y publico/tarjeta.png)       publico/estilo.css, las setas y la red

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
import struct
import subprocess
import sys
import zlib
from html import escape
from pathlib import Path

AQUI = Path(__file__).parent
PAGINA = AQUI / "publico" / "index.html"
DOCUMENTOS = Path(os.environ.get("MYCELIUM_DOCUMENTOS", AQUI.parent.parent / "documentos")).resolve()
GITHUB_DOCUMENTOS = "https://github.com/asociacionmycelium/documentos"
NOMBRE = "Asociación Mycelium"
URL = "https://asociacionmycelium.org/"   # dominio previsto (doc 07); si #15 decide otro, se cambia aquí
TARJETA = AQUI / "publico" / "tarjeta.png"
ESTILO = AQUI / "publico" / "estilo.css"

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


def desde_fuera(texto):
    """pendientes.md vive en documentos: «este repositorio» se lee raro en la página (#6)."""
    texto = re.sub(r"\beste repositorio\b", "el repositorio documentos", texto)
    return re.sub(r"\bEste repositorio\b", "El repositorio documentos", texto)


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
        filas.append(f'<tr><td>{escape(a["Id"])}</td><td>{escape(desde_fuera(primera_frase(texto_plano(a["Asunto"]))))}</td>'
                     f'<td>{escape(texto_plano(a["Estado"]))}</td></tr>')
    if not filas:
        para("pendientes.md no tiene asuntos")
    return "\n".join(filas)


# ---------- Red de filamentos (de demo/genera.py) ----------

ANCHO, ALTO = 1000, 6000
# La red ocupa solo la franja derecha (de IZQ a ANCHO): el texto queda limpio.
IZQ = 570
SETAS = [(835, 106, 52), (715, 80, 40), (940, 60, 30), (610, 44, 24)]  # x, alto, radio
BROTES = [x for x, _, _ in SETAS]                # cada seta tiene su filamento (#9)


def trazo(pts, desde=0, hasta=None):
    """Curva suave que pasa por los puntos medios (cuadráticas encadenadas).

    Dibuja el trozo entre los nudos `desde` y `hasta`: el primer y el último punto
    y los puntos medios entre vecinos. Sin argumentos, la curva entera.
    """
    n = len(pts) - 1
    if hasta is None:
        hasta = n
    if n == 1:
        return "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)

    def nudo(j):
        if j == 0 or j == n:
            return pts[j]
        return ((pts[j][0] + pts[j + 1][0]) / 2, (pts[j][1] + pts[j + 1][1]) / 2)

    x0, y0 = nudo(desde)
    cx, cy = pts[desde + 1]
    x1, y1 = nudo(desde + 1)
    d = f"M{x0:.0f} {y0:.0f}Q{cx:.0f} {cy:.0f} {x1:.0f} {y1:.0f}"
    for j in range(desde + 2, hasta + 1):
        x, y = nudo(j)
        d += f"T{x:.0f} {y:.0f}"
    return d


def filamentos(semilla, brotes, densa):
    """Geometría de la red: densa cuando haya lotes (semilla: huella del último, issue #2);
    escasa sin ellos, y entonces se apaga poco a poco hacia el fondo.

    Devuelve (pts, gen, madre, nace) por trazo: `madre` es el índice del trazo del que
    nace (None en los troncos) y `nace`, el índice del punto de la madre donde nace.
    """
    rng = random.Random(int(semilla, 16))
    paso = 30
    if densa:
        vida0, ramifica, max_gen = 400, [0.06, 0.04, 0.025], 3
        vida = [None, (22, 60), (10, 30), (5, 14)]
    else:
        vida0, ramifica, max_gen = 400, [0.07, 0.0, 0.0], 1
        vida = [None, (6, 18)]
    cola = []
    for x in brotes:
        ang = math.pi / 2 + rng.uniform(-0.2, 0.2)
        # Sin lotes, cada tronco baja hasta una profundidad propia y ahí se acaba.
        fondo = ALTO if densa else rng.uniform(0.55, 0.65) * ALTO
        cola.append((x, 0.0, ang, 0, vida0, fondo, None, 0))
    trazos = []
    while cola and len(trazos) < 520:
        x, y, ang, gen, pasos, fondo, madre, nace = cola.pop(0)
        pts = [(x, y)]
        for _ in range(pasos):
            ang += rng.gauss(0, 0.2)
            ang += (math.pi / 2 - ang) * (0.06 if gen == 0 else 0.012)
            # Cerca de los bordes se aparta poco a poco, como junto al texto.
            if x < IZQ + 90:
                ang += (0.12 + 0.18 * (IZQ + 90 - x) / 90) * math.sin(0 - ang)
            if x > ANCHO - 15 - 90:
                ang += (0.12 + 0.18 * (x - (ANCHO - 15 - 90)) / 90) * math.sin(math.pi - ang)

            def cabe(a):
                nx = x + math.cos(a) * paso
                ny = y + math.sin(a) * paso
                return IZQ <= nx <= ANCHO - 15 and ny >= 12

            # Si aun así se saldría, gira lo justo para quedarse dentro.
            if not cabe(ang):
                for n in range(1, 64):
                    d = n * 0.05
                    if cabe(ang + d):
                        ang += d
                        break
                    if cabe(ang - d):
                        ang -= d
                        break
            x += math.cos(ang) * paso
            y += math.sin(ang) * paso
            if y > fondo:
                break
            pts.append((x, y))
            if gen < max_gen:
                p = ramifica[gen] * (1 if densa else 1 - y / fondo)   # cuanto más hondo, menos ramas
                if rng.random() < p:
                    lo, hi = vida[gen + 1]
                    cola.append((x, y, ang + rng.choice([-1, 1]) * rng.uniform(0.5, 1.15),
                                 gen + 1, rng.randint(lo, hi), ALTO, len(trazos), len(pts) - 1))
        if len(pts) > 1:
            trazos.append((pts, gen, madre, nace))
    return trazos


def _llega(trazos, ti, n):
    """Momento (en %) en que la madre del trazo n llega al punto donde nace."""
    _, _, madre, nace = trazos[n]
    i_m, f_m = ti[madre]
    return i_m + (f_m - i_m) * nace / (len(trazos[madre][0]) - 1)


def tiempos(trazos):
    """Tramo del scroll (--i, --f, en %) en el que crece cada trazo, ya redondeado.

    Los troncos, por su profundidad; cada rama empieza cuando su madre llega a donde
    nace y crece a su ritmo, así el crecimiento sigue unido.
    """
    ti = []
    for n, (pts, gen, madre, nace) in enumerate(trazos):
        if madre is None:
            y1 = max(p[1] for p in pts)
            i = round(pts[0][1] / ALTO * 88 + 2, 1)
            f = round(max(y1 / ALTO * 88 + 7, i + 3), 1)
        else:
            i_m, f_m = ti[madre]
            n_m = len(trazos[madre][0]) - 1
            i = math.ceil(_llega(trazos, ti, n) * 10 - 1e-9) / 10
            f = round(i + max((f_m - i_m) * (len(pts) - 1) / n_m, 3), 1)
        ti.append((i, f))
    return ti


def red(semilla, brotes, densa):
    """SVG de la red. Las puntas se dibujan en tramos cada vez más finos y tenues (--p)."""
    trazos = filamentos(semilla, brotes, densa)
    ti = tiempos(trazos)

    for x, _, _ in SETAS:
        if not any(gen == 0 and madre is None and pts[0] == (x, 0.0) for pts, gen, madre, _ in trazos):
            para(f"la seta de x={x} no tiene filamento")
    for n, (pts, gen, madre, nace) in enumerate(trazos):
        if not all(IZQ <= x <= ANCHO - 15 and y >= 0 for x, y in pts):
            para(f"el filamento {n} se sale de la franja de la red")
        if madre is not None and ti[n][0] < _llega(trazos, ti, n) - 1e-9:
            para(f"la rama {n} empieza a crecer antes de que su madre llegue a donde nace")

    partes = [f'<svg viewBox="0 0 {ANCHO} {ALTO}" role="presentation">']
    for gen, p, d, ia, fb in tramos_red(trazos, ti):
        estilo = f"--i:{ia:.1f}%;--f:{fb:.1f}%" + ("" if p is None else f";--p:{p:.2f}")
        partes.append(f'<path class="g{gen}" pathLength="1" style="{estilo}" d="{d}"/>')
    partes.append("</svg>")
    return "\n".join(partes), len(trazos)


def tramos_red(trazos, ti):
    """Un tramo por cada <path> de la red, en orden: (gen, p, d, --i, --f).

    p es None en el tramo sin afinar. Lo usan el SVG de la página y la tarjeta.
    """
    tramos = []
    for (pts, gen, _, _), (i, f) in zip(trazos, ti):
        N = len(pts) - 1
        m = min(3, N // 4)

        def fr(j):
            return 0 if j == 0 else min(j + 0.5, N) / N

        trozos = [(0, N - 2 * m, None)]
        for q in range(1, m + 1):
            trozos.append((N - 2 * (m - q + 1), N - 2 * (m - q), 1 - q / (m + 1)))
        for a, b, p in trozos:
            ia = round(i + (f - i) * fr(a), 1)
            fb = round(i + (f - i) * fr(b), 1)
            tramos.append((gen, p, trazo(pts, a, b), ia, fb))
    return tramos


ALTO_SETAS = 170


def formas_setas():
    """La ruta d de cada seta, en el viewBox de las setas (ANCHO × ALTO_SETAS)."""
    alto = ALTO_SETAS
    formas = []
    for x, h, r in SETAS:
        base, pie, c = alto, r * 0.2, r * 0.82
        cy = base - h
        formas.append(
            f'M{x - pie:.0f} {base}L{x - pie * 0.7:.0f} {cy:.0f}L{x + pie * 0.7:.0f} {cy:.0f}L{x + pie:.0f} {base}Z'
            f'M{x - r} {cy:.0f}Q{x - r} {cy - c:.0f} {x} {cy - c * 1.06:.0f}Q{x + r} {cy - c:.0f} {x + r} {cy:.0f}'
            f'Q{x} {cy + r * 0.2:.0f} {x - r} {cy:.0f}Z')
    return formas


def setas():
    partes = [f'<svg viewBox="0 0 {ANCHO} {ALTO_SETAS}" role="presentation">']
    for d in formas_setas():
        partes.append(f'<path d="{d}"/>')
    partes.append("</svg>")
    return "\n".join(partes)


# ---------- Tarjeta al compartir ----------
#
# La imagen de Open Graph (1200 × 630, PNG: las redes no aceptan SVG). Sale de
# lo mismo que la cabecera: el color de la superficie, las setas y el arranque
# de la red, con los colores y trazos de estilo.css. Sin texto: el título y la
# frase van en og:title y og:description.

T_ANCHO, T_ALTO = 1200, 630
E = 1.2                     # los 1000 de ancho del viewBox ocupan los 1200 px
SUELO = 380                 # primera fila de tierra
SUBFILAS = 4                # muestras verticales por fila al rellenar
MAX_TARJETA = 300 * 1024    # lo que aceptan WhatsApp y compañía
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"
ALT_TARJETA = "Setas oscuras sobre la superficie de la asociación y, bajo tierra, los primeros filamentos de su red."


def estilo_tarjeta():
    """Colores (--superficie, --tierra, --hifa) y, por generación, (grosor, opacidad) de la red."""
    try:
        css = ESTILO.read_text(encoding="utf-8")
    except FileNotFoundError:
        para(f"no encuentro {ESTILO}; la tarjeta lo necesita")
    raiz = re.search(r":root\s*\{(.*?)\}", css, re.S)
    variables = dict((k, v.strip()) for k, v in re.findall(r"--([\w-]+):\s*([^;]+);", raiz.group(1))) if raiz else {}
    colores = {}
    for nombre in ("superficie", "tierra", "hifa"):
        valor, vistos = variables.get(nombre, ""), set()
        while (m := re.fullmatch(r"var\(--([\w-]+)\)", valor)) and m.group(1) not in vistos:
            vistos.add(m.group(1))
            valor = variables.get(m.group(1), "")
        if not valor or valor.startswith("var("):
            para(f"estilo.css no define --{nombre} en :root; la tarjeta la necesita")
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", valor):
            para(f"estilo.css da a --{nombre} el valor «{valor}»; la tarjeta necesita un color #RRGGBB")
        colores[nombre] = tuple(int(valor[k:k + 2], 16) for k in (1, 3, 5))
    generaciones = {}
    for gen, cuerpo in re.findall(r"\.red\s+\.g(\d+)\s*\{([^}]*)\}", css):
        w = re.search(r"--w:\s*(\d+(?:\.\d+)?)px\s*;", cuerpo)
        o = re.search(r"--o:\s*(\d+(?:\.\d+)?)\s*;", cuerpo)
        if w and o:
            generaciones.setdefault(int(gen), (float(w.group(1)), float(o.group(1))))
    return colores, generaciones


def subrutas(d):
    """Puntos de cada subruta de una ruta d (M, L, Q, T y Z) y si está cerrada.

    Cada cuadrática se aplana en 16 tramos; T refleja el control de la anterior,
    como en SVG.
    """
    fichas = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?", d)
    rutas, pts = [], None
    x = y = 0.0
    qx = qy = None          # control de la última cuadrática (para T)
    orden, i = None, 0
    while i < len(fichas):
        if fichas[i].isalpha():
            orden = fichas[i]
            i += 1
            if orden == "Z":
                if pts:
                    rutas.append((pts, True))
                    x, y = pts[0]
                pts, qx, qy = None, None, None
                continue
        n = {"M": 2, "L": 2, "Q": 4, "T": 2}.get(orden)
        v = fichas[i:i + n] if n else []
        if not n or len(v) != n or any(t.isalpha() for t in v):
            para(f"no sé dibujar la ruta «{d[:40]}…» en la tarjeta")
        v = [float(t) for t in v]
        i += n
        if orden == "M":
            if pts and len(pts) > 1:
                rutas.append((pts, False))
            x, y = v
            pts, qx, qy = [(x, y)], None, None
            orden = "L"
            continue
        if pts is None:
            pts = [(x, y)]
        if orden == "L":
            x, y = v
            pts.append((x, y))
            qx = qy = None
            continue
        if orden == "Q":
            cx, cy, nx, ny = v
        else:
            cx, cy = (x, y) if qx is None else (2 * x - qx, 2 * y - qy)
            nx, ny = v
        for k in range(1, 17):
            t = k / 16
            pts.append(((1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * nx,
                        (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * ny))
        x, y, qx, qy = nx, ny, cx, cy
    if pts and len(pts) > 1:
        rutas.append((pts, False))
    return rutas


def cubre_relleno(pts, cob):
    """Cobertura (0..1) de un polígono cerrado: SUBFILAS muestras por fila y,
    en horizontal, la parte exacta de cada píxel que queda dentro."""
    aristas = [(pts[k], pts[(k + 1) % len(pts)]) for k in range(len(pts))]
    aristas = [(a, b) for a, b in aristas if a[1] != b[1]]
    if not aristas:
        return
    j0 = max(0, math.floor(min(p[1] for p in pts)))
    j1 = min(T_ALTO - 1, math.ceil(max(p[1] for p in pts)))
    propia = {}
    for j in range(j0, j1 + 1):
        for s in range(SUBFILAS):
            yy = j + (s + 0.5) / SUBFILAS
            xs = sorted(x0 + (yy - y0) * (x1 - x0) / (y1 - y0)
                        for (x0, y0), (x1, y1) in aristas if min(y0, y1) <= yy < max(y0, y1))
            for xa, xb in zip(xs[0::2], xs[1::2]):
                xa, xb = max(xa, 0.0), min(xb, float(T_ANCHO))
                for i in range(math.floor(xa), min(math.ceil(xb), T_ANCHO)):
                    tramo = min(xb, i + 1) - max(xa, i)
                    if tramo > 0:
                        propia[(i, j)] = propia.get((i, j), 0.0) + tramo / SUBFILAS
    for k, c in propia.items():
        c = min(c, 1.0)
        if c > cob.get(k, 0.0):
            cob[k] = c


def cubre_trazo(pts, grosor, cob):
    """Cobertura de un trazo: cada segmento, una cápsula con el borde suave de 1 px."""
    r = grosor / 2 + 0.5
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        i0, i1 = max(0, math.floor(min(x0, x1) - r)), min(T_ANCHO - 1, math.ceil(max(x0, x1) + r))
        j0, j1 = max(0, math.floor(min(y0, y1) - r)), min(T_ALTO - 1, math.ceil(max(y0, y1) + r))
        if i0 > i1 or j0 > j1:
            continue
        dx, dy = x1 - x0, y1 - y0
        ll = dx * dx + dy * dy
        for j in range(j0, j1 + 1):
            py = j + 0.5
            for i in range(i0, i1 + 1):
                px = i + 0.5
                t = 0.0 if ll == 0 else max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / ll))
                c = max(0.0, min(1.0, r - math.hypot(px - x0 - t * dx, py - y0 - t * dy)))
                if c > cob.get((i, j), 0.0):
                    cob[(i, j)] = c


def mezcla(lienzo, cob, color, opacidad):
    """Pone una forma sobre lo que hay: fondo · (1 − a) + color · a."""
    for (i, j), c in cob.items():
        a = c * opacidad
        if a <= 0:
            continue
        o = (j * T_ANCHO + i) * 3
        for k in range(3):
            lienzo[o + k] = max(0, min(255, round(lienzo[o + k] * (1 - a) + color[k] * a)))


def dibuja_tarjeta(semilla):
    """Los píxeles RGB de la tarjeta: superficie, setas, tierra y el arranque de la red."""
    colores, generaciones = estilo_tarjeta()
    superficie, tierra, hifa = colores["superficie"], colores["tierra"], colores["hifa"]
    lienzo = bytearray(bytes(superficie) * (T_ANCHO * SUELO) + bytes(tierra) * (T_ANCHO * (T_ALTO - SUELO)))

    for d in formas_setas():
        cob = {}
        for pts, _ in subrutas(d):
            cubre_relleno([(E * x, SUELO - E * (ALTO_SETAS - y)) for x, y in pts], cob)
        mezcla(lienzo, cob, tierra, 1.0)

    trazos = filamentos(semilla, BROTES, densa=False)
    for gen, p, d, _, _ in tramos_red(trazos, tiempos(trazos)):
        if gen not in generaciones:
            para(f"estilo.css no da grosor y opacidad a la generación g{gen} de la red; la tarjeta los necesita")
        w, o = generaciones[gen]
        p = 1.0 if p is None else float(f"{p:.2f}")     # el --p que lleva la página
        cob = {}
        for pts, cerrada in subrutas(d):
            pts = [(E * x, SUELO + E * y) for x, y in pts]
            cubre_trazo(pts + pts[:1] if cerrada else pts, E * w * p, cob)
        mezcla(lienzo, cob, hifa, o * p)
    return lienzo


def trozo_png(tipo, datos):
    return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))


def tarjeta(semilla):
    """El PNG de la tarjeta y sus filas en crudo. RGB de 8 bits, filtro 0 y sin
    fecha ni texto: las mismas fuentes dan los mismos bytes."""
    lienzo = dibuja_tarjeta(semilla)
    fila = T_ANCHO * 3
    crudo = b"".join(b"\x00" + bytes(lienzo[j * fila:(j + 1) * fila]) for j in range(T_ALTO))
    datos = (FIRMA_PNG
             + trozo_png(b"IHDR", struct.pack(">IIBBBBB", T_ANCHO, T_ALTO, 8, 2, 0, 0, 0))
             + trozo_png(b"IDAT", zlib.compress(crudo, 9))
             + trozo_png(b"IEND", b""))
    if len(datos) >= MAX_TARJETA:
        kb = f"{len(datos) / 1024:.0f}"
        para(f"la tarjeta pesa {kb} KB; las redes piden menos de 300")
    return datos, crudo


def crudo_png(ruta):
    """Las filas en crudo de un PNG (sus IDAT descomprimidos); None si no hay o no se lee."""
    try:
        b = ruta.read_bytes()
    except FileNotFoundError:
        return None
    if b[:8] != FIRMA_PNG:
        return None
    i, idat = 8, b""
    while i + 8 <= len(b):
        n, = struct.unpack(">I", b[i:i + 4])
        if b[i + 4:i + 8] == b"IDAT":
            idat += b[i + 8:i + 8 + n]
        i += 12 + n
    try:
        return zlib.decompress(idat)
    except zlib.error:
        return None


def escribe_tarjeta(datos, crudo):
    """Escribe la tarjeta solo si cambian sus píxeles: otra versión de zlib no deja un diff sin cambio real."""
    if crudo_png(TARJETA) != crudo:
        TARJETA.write_bytes(datos)


def bloque_tarjeta(titular):
    """Los metadatos Open Graph del <head>."""
    lineas = [
        ("og:type", "website"),
        ("og:site_name", NOMBRE),
        ("og:title", NOMBRE),
        ("og:description", texto_plano(titular)),
        ("og:url", URL),
        ("og:locale", "es_ES"),
        ("og:image", URL + "tarjeta.png"),
        ("og:image:type", "image/png"),
        ("og:image:width", str(T_ANCHO)),
        ("og:image:height", str(T_ALTO)),
        ("og:image:alt", ALT_TARJETA),
    ]
    return "\n" + "\n".join(f'<meta property="{p}" content="{escape(v, quote=True)}">' for p, v in lineas) + "\n"


# ---------- Montaje ----------

def main():
    # Sin lotes todavía: unos pocos filamentos, sembrados con el nombre.
    semilla = hashlib.sha256(NOMBRE.encode()).hexdigest()
    red_vacia, n0 = red(semilla, BROTES, densa=False)
    titular, _ = manifiesto()
    bloques = {
        **bloques_manifiesto(),
        "cambios": cambios(),
        "asuntos": asuntos(),
        "setas": setas(),
        "red": red_vacia,
        "tarjeta": bloque_tarjeta(titular),
    }
    # La imagen se genera antes de escribir nada: si un invariante para, no queda nada a medias.
    png, crudo = tarjeta(semilla)
    html = PAGINA.read_text(encoding="utf-8")
    for nombre, contenido in bloques.items():
        patron = re.compile(rf"(<!--G:{nombre}-->).*?(<!--/G:{nombre}-->)", re.S)
        if not patron.search(html):
            para(f"falta el hueco {nombre} en {PAGINA}")
        html = patron.sub(lambda m: m.group(1) + contenido + m.group(2), html)
    escribe_tarjeta(png, crudo)
    PAGINA.write_text(html, encoding="utf-8")
    print(f"fuentes: {DOCUMENTOS}\nfilamentos: {n0}\n{len(html) / 1024:.0f} KB\ntarjeta: {len(png) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
