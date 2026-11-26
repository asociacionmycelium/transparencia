#!/usr/bin/env python3
"""Rellena demo/index.html con lo que sale de los datos de ejemplo.

Todo lo que hay entre <!--G:nombre--> y <!--/G:nombre--> lo escribe este
guion: asientos, lotes con su huella SHA-256, fichas, el diagrama de flujos y
la red de filamentos. La red se siembra con la huella del último lote, así que
los mismos datos dan siempre el mismo dibujo y un dato distinto da otro.

En la plataforma real este trabajo lo hará el servidor al recibir cada lote.
La página no lleva JavaScript.

Uso: python3 demo/genera.py   (solo biblioteca estándar; se puede repetir)
"""
import hashlib
import json
import math
import random
import re
from html import escape
from pathlib import Path

AQUI = Path(__file__).parent

# ---------- Datos de ejemplo (inventados) ----------

ASIENTOS = [
    dict(n="2027-0016", fecha="2027-03-14", importe=-0.90, proyecto="Funcionamiento",
         concepto="Corrección del asiento 2027-0012: eran 38,72 €, no 37,82 €",
         justificante="El mismo del asiento 2027-0012", corrige="2027-0012"),
    dict(n="2027-0015", fecha="2027-03-14", importe=50.00, proyecto="Sin asignar todavía",
         concepto="Donación de una persona que no ha pedido aparecer con su nombre",
         justificante="Apunte del banco"),
    dict(n="2027-0014", fecha="2027-03-12", importe=-6.40, proyecto="Taller de copias de seguridad",
         concepto="Reembolso a la Vocalía: autobús para preparar el taller",
         justificante="Billete de autobús"),
    dict(n="2027-0013", fecha="2027-03-05", importe=30.00, proyecto="Funcionamiento",
         concepto="Cuota de un socio", justificante="Apunte del banco"),
    dict(n="2027-0012", fecha="2027-03-05", importe=-37.82, proyecto="Funcionamiento",
         concepto="Alojamiento web, marzo", justificante="Factura del proveedor",
         corregido_por="2027-0016"),
    dict(n="2027-0011", fecha="2027-03-01", importe=-12.00, proyecto="Funcionamiento",
         concepto="Comisión de mantenimiento de la cuenta", justificante="Apunte del banco"),
    dict(n="2027-0010", fecha="2027-02-27", importe=1000.00, proyecto="Web del banco de alimentos",
         concepto="Aportación del banco de alimentos para su web. Solo puede gastarse en eso",
         justificante="Apunte del banco"),
    dict(n="2027-0009", fecha="2027-02-27", importe=-14.51, proyecto="Funcionamiento",
         concepto="Renovación anual del dominio", justificante="Factura del proveedor"),
]

# De dónde viene cada euro y a dónde va (suma 4.180,00 por ambos lados).
ORIGENES = ["Cuotas de socios", "Donaciones", "Aportación de una entidad atendida"]
DESTINOS = ["Funcionamiento", "Taller de copias de seguridad", "Web del banco de alimentos", "Sin gastar"]
FLUJOS = [  # (origen, destino, euros)
    (0, 0, 1210.00), (0, 3, 110.00),
    (1, 1, 486.40), (1, 2, 240.00), (1, 3, 1133.60),
    (2, 2, 1000.00),
]

ANCLAJES = ["Pendiente: tarda unas horas", "Bitcoin, bloque 941.388", "Bitcoin, bloque 940.372",
            "Bitcoin, bloque 939.801", "Bitcoin, bloque 939.502"]

MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()


def euros(v, signo=False):
    s = f"{abs(v):,.2f}".replace(",", "x").replace(".", ",").replace("x", ".")
    if signo:
        s = ("+" if v > 0 else "−") + s
    return s + " €"


def fecha_corta(iso):
    a, m, d = iso.split("-")
    return f"{int(d)}/{int(m)}/{a}"


def fecha_larga(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def corta(h):
    return f"{h[:4]}…{h[-4:]}"


# ---------- Lotes y huellas ----------

def lotes():
    por_dia = {}
    for a in ASIENTOS:
        por_dia.setdefault(a["fecha"], []).append(a)
    out = []
    for dia in sorted(por_dia, reverse=True):
        cuerpo = json.dumps(sorted(por_dia[dia], key=lambda a: a["n"]),
                            ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        out.append(dict(dia=dia, asientos=por_dia[dia],
                        huella=hashlib.sha256(cuerpo.encode()).hexdigest()))
    return out


# ---------- Red de filamentos ----------

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


# ---------- Flujos ----------

def flujos():
    total = sum(v for _, _, v in FLUJOS)
    t_or = [sum(v for o, _, v in FLUJOS if o == i) for i in range(len(ORIGENES))]
    t_de = [sum(v for _, d, v in FLUJOS if d == i) for i in range(len(DESTINOS))]
    W, H = 1000, 200
    x_or = [sum(t_or[:i]) / total * W for i in range(len(t_or))]
    x_de = [sum(t_de[:i]) / total * W for i in range(len(t_de))]
    cintas = []
    for o, d, v in sorted(FLUJOS, key=lambda f: (f[0], f[1])):
        a0 = x_or[o]; x_or[o] += v / total * W; a1 = x_or[o]
        b0 = x_de[d]; x_de[d] += v / total * W; b1 = x_de[d]
        fill = "url(#queda)" if d == len(DESTINOS) - 1 else "url(#gasto)"
        cintas.append(
            f'<path fill="{fill}" d="M{a0:.1f} 0C{a0:.1f} {H / 2} {b0:.1f} {H / 2} {b0:.1f} {H}'
            f'L{b1:.1f} {H}C{b1:.1f} {H / 2} {a1:.1f} {H / 2} {a1:.1f} 0Z">'
            f'<title>{escape(ORIGENES[o])} → {escape(DESTINOS[d])}: {euros(v)}</title></path>')

    def fila(clase, nombres, tot, letras):
        cols = " ".join(f"minmax(0,{t:.0f}fr)" for t in tot)
        lis = "".join(
            f'<li data-letra="{l}"{" class=queda" if clase == "destino" and i == len(nombres) - 1 else ""}>'
            f'<b>{escape(n)}</b>{euros(t)}</li>'
            for i, (n, t, l) in enumerate(zip(nombres, tot, letras)))
        return f'<ol class="{clase}" style="grid-template-columns:{cols}">{lis}</ol>'

    l_or, l_de = "ABC", "1234"
    leyenda = "; ".join(f"{l}, {n.lower()} ({euros(t)})" for l, n, t in zip(l_or, ORIGENES, t_or)) + ". " + \
              "; ".join(f"{l}, {n.lower()} ({euros(t)})" for l, n, t in zip(l_de, DESTINOS, t_de)) + "."
    return (
        '<figure class="flujos">'
        + fila("origen", ORIGENES, t_or, l_or)
        + f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="img" '
          'aria-label="Cintas que unen cada ingreso con aquello en lo que se gasta">'
          '<defs><linearGradient id="gasto" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#A999E0"/><stop offset="1" stop-color="#E2AE45"/></linearGradient>'
          '<linearGradient id="queda" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#A999E0"/><stop offset="1" stop-color="#A999E0"/></linearGradient></defs>'
        + "".join(cintas) + "</svg>"
        + fila("destino", DESTINOS, t_de, l_de)
        + f'<figcaption class="leyenda">{leyenda}</figcaption></figure>')


# ---------- Tablas y fichas ----------

def filas_asientos():
    out = []
    for a in ASIENTOS:
        clase = "entra" if a["importe"] > 0 else "sale"
        extra = ""
        if a.get("corregido_por"):
            extra = f' Corregido por el asiento {a["corregido_por"]}.'
        out.append(
            f'<tr><td><button commandfor="asiento-{a["n"]}" command="show-modal">{a["n"]}</button></td>'
            f'<td>{fecha_corta(a["fecha"])}</td>'
            f'<td>{escape(a["concepto"])}<small>{escape(a["proyecto"])}.{extra}</small></td>'
            f'<td class="num {clase}">{euros(a["importe"], True)}</td></tr>')
    return "\n".join(out)


def filas_lotes(ls):
    return "\n".join(
        f'<tr><td>{fecha_corta(l["dia"])}</td><td>{len(l["asientos"])}</td>'
        f'<td><code>{corta(l["huella"])}</code></td><td>{ANCLAJES[i]}</td></tr>'
        for i, l in enumerate(ls))


def dialogos(ls):
    huella = {a["n"]: l["huella"] for l in ls for a in l["asientos"]}
    out = []
    for a in ASIENTOS:
        nota = ""
        if a.get("corrige"):
            nota = f'<div><dt>Corrige</dt><dd>El asiento {a["corrige"]}, que sigue publicado tal como se anotó.</dd></div>'
        if a.get("corregido_por"):
            nota = f'<div><dt>Corregido</dt><dd>Por el asiento {a["corregido_por"]}. Este no se ha tocado.</dd></div>'
        out.append(f'''<dialog id="asiento-{a["n"]}" closedby="any" aria-labelledby="t-{a["n"]}">
  <h2 id="t-{a["n"]}">Asiento {a["n"]}</h2>
  <p class="importe">{euros(a["importe"], True)}</p>
  <dl>
    <div><dt>Fecha</dt><dd>{fecha_larga(a["fecha"])}</dd></div>
    <div><dt>Concepto</dt><dd>{escape(a["concepto"])}</dd></div>
    <div><dt>Proyecto</dt><dd>{escape(a["proyecto"])}</dd></div>
    {nota}
    <div><dt>Justificante, con los datos personales tapados</dt>
      <dd><div class="justificante">{escape(a["justificante"])}<br>Titular: <span class="tapado" role="img" aria-label="dato tapado"></span><br>Importe: {euros(abs(a["importe"]))}</div></dd></div>
    <div><dt>Huella del lote del {fecha_corta(a["fecha"])}</dt><dd><code>{huella[a["n"]]}</code></dd></div>
  </dl>
  <button class="cerrar" commandfor="asiento-{a["n"]}" command="close">Cerrar</button>
</dialog>''')
    return "\n".join(out)


# ---------- Montaje ----------

def main():
    ls = lotes()
    ultima = ls[0]["huella"]
    red_ejemplo, n1 = red(ultima, BROTES, densa=True)
    # Sin lotes todavía: unos pocos filamentos, sembrados con el nombre.
    red_vacia, n0 = red(hashlib.sha256("Asociación Mycelium".encode()).hexdigest(), BROTES[:3], densa=False)
    bloques = {
        "setas": setas(),
        "red-vacia": red_vacia,
        "red-ejemplo": red_ejemplo,
        "hash-corto": corta(ultima),
        "flujos": flujos(),
        "asientos": filas_asientos(),
        "lotes": filas_lotes(ls),
        "dialogos": dialogos(ls),
    }
    f = AQUI / "index.html"
    html = f.read_text(encoding="utf-8")
    for nombre, contenido in bloques.items():
        patron = re.compile(rf"(<!--G:{nombre}-->).*?(<!--/G:{nombre}-->)", re.S)
        if not patron.search(html):
            raise SystemExit(f"Falta el hueco {nombre} en index.html")
        html = patron.sub(lambda m: m.group(1) + contenido + m.group(2), html)
    f.write_text(html, encoding="utf-8")
    print(f"último lote {ultima}\nfilamentos: {n0} sin datos, {n1} con datos\n{len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
