# Página publicable: lo que hay de verdad hoy

Es la página que se publicará en el dominio cuando la Junta lo decida (P-012). Hasta entonces es un borrador y lleva `noindex`.

La maqueta de [`demo/`](../demo/README.md) es la guía de diseño y no se toca (D26, D28). Esta página sale de ella, pero solo enseña lo que existe. Lo que aún no tiene datos lo dice en la página, y en el código deja un hueco oculto (`<div class="hueco" hidden>`) con la issue que lo rellenará.

## Generarla y verla

```
python3 web/genera.py
python3 -m http.server 8765 --directory web/publico
```

y abrir `http://127.0.0.1:8765/`. El generador lee el repositorio `documentos` del directorio de al lado (o el de `MYCELIUM_DOCUMENTOS`), usa solo la biblioteca estándar y se puede repetir: con las mismas fuentes, la página sale igual.

## Qué hay aquí

| Fichero | Qué es |
|---|---|
| `genera.py` | Lee las fuentes y escribe lo que hay entre `<!--G:…-->` en `publico/index.html` |
| `publico/` | Lo que se sirve o despliega, tal cual. Nada más |
| `publico/index.html` | La página. Sin JavaScript (D26) |
| `publico/estilo.css` | Todo el aspecto. Solo lo que usa la página; el resto está en `demo/estilo.css` |
| `publico/favicon.svg` | El icono de la pestaña: una seta como las de la cabecera, tierra sobre albero. Escrito a mano |
| `publico/tarjeta.png` | La imagen de la tarjeta al compartir (Open Graph), de 1200×630. La dibuja `genera.py` con el color de la superficie, las setas y el arranque de la red de `publico/estilo.css` y la propia página. No se edita a mano |
| `publico/fuentes/` | Atkinson Hyperlegible Next y Mono (SIL OFL 1.1, subconjunto latino de Fontsource), servidas desde aquí: la página no pide nada a terceros |

## De dónde sale cada sección

| Sección | Fuente | Hoy |
|---|---|---|
| Superficie (titular y tres tramos) | `documentos/manifiesto.md` | Real |
| Estado del registro | `ESTADO` en `genera.py`, lo único escrito a mano | Constituida; inscripción en trámite |
| A la vista de todos | `manifiesto.md` y `git log` de `documentos` | Real: últimos cambios con fecha, qué cambió y firma; sin autor |
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
- Lo que sale de `documentos` se dice desde fuera: «este repositorio» en `pendientes.md` sale en la página como «el repositorio documentos» (`desde_fuera` en `genera.py`, #6).
- La tarjeta al compartir apunta a `URL` de `genera.py` (hoy `https://asociacionmycelium.org/`): si la página se publica en otro dominio (#15), se cambia ahí y se regenera. La imagen solo se reescribe si cambian sus píxeles, y el generador se para si `estilo.css` no da los colores o si pesa 300 KB o más.

## Contraste
Medido con WCAG 2 (mínimo AA, 4,5:1) el 26/11/2026 (#6). Sobre `--tierra`: texto y enlaces 12,98:1, tenue 6,74:1, lila 6,27:1, albero 7,82:1; tinta sobre albero, 8,53:1.

En pantalla ancha el texto no llega a la franja de la red. En pantalla estrecha (≤52rem) la red pasa por detrás del texto: por eso allí es más tenue y `--tenue` sube al 75 % de hifa. Con dos troncos cruzados detrás, el peor caso, el tenue da 4,56:1 y el albero 4,52:1. Si cambian los colores o la opacidad de la red, hay que volver a medirlo.
