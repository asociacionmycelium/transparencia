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
            estilo = f"--i:{ia:.1f}%;--f:{fb:.1f}%" + ("" if p is None else f";--p:{p:.2f}")
            partes.append(f'<path class="g{gen}" pathLength="1" style="{estilo}" d="{trazo(pts, a, b)}"/>')
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
    red_vacia, n0 = red(hashlib.sha256("Asociación Mycelium".encode()).hexdigest(), BROTES, densa=False)
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
