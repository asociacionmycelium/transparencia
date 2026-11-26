# Maqueta de diseño: landing y plataforma en una sola página

Guía visual para construir la landing de la asociación y la plataforma de transparencia. No es funcional y no es la web de la asociación. Los datos de ejemplo son inventados.

## Verla

```
python3 -m http.server 8765 --directory demo
```

y abrir `http://127.0.0.1:8765/`. Arriba hay dos controles: **Ver con datos de ejemplo** y **Entidad**.

## La idea

La página es un corte de suelo. Arriba, la superficie: el manifiesto. Abajo, lo que normalmente no se ve: cuentas, decisiones, propuestas y datos. No hay un "entrar en la aplicación": se baja.

- La red de filamentos se dibuja a partir de la huella (SHA-256) del último lote de asientos. Mismos datos, mismo dibujo.
- Sin datos, la página lo dice y la red son unos pocos filamentos. Con datos, crece.
- La superficie (color, nombre, texto) es de cada entidad. Lo de bajo tierra es común.

## Cómo está hecha

Tres ficheros, sin dependencias ni compilación, y **sin JavaScript en la página**:

| Fichero | Qué es |
|---|---|
| `index.html` | La página. Lo que hay entre `<!--G:…-->` lo escribe `genera.py` |
| `estilo.css` | Todo el aspecto y todo el comportamiento |
| `genera.py` | Datos de ejemplo → huellas, tablas, fichas, flujos y red. `python3 demo/genera.py` |

| Para | Se usa | En vez de |
|---|---|---|
| Mostrar u ocultar los datos de ejemplo; cambiar de entidad | Casillas y `:has()` | Estado en JavaScript |
| Que la red crezca al bajar | `animation-timeline` con `view-timeline` | `IntersectionObserver` o un `canvas` animado |
| Marcar en el menú la sección que se está leyendo | `timeline-scope` y `animation-range` | Un "scroll spy" |
| Ficha de cada asiento | `<dialog closedby="any">` con `command` y `commandfor` | Un modal con su gestión de foco |
| Aclaraciones | `popover` con `position-area` | Una librería de tooltips |
| Acuerdos que se abren de uno en uno | `<details name>` | Un acordeón |

Comprobado con `CSS.supports` en Firefox 161 y visto en Chromium. En un navegador sin animaciones ligadas al scroll la red aparece ya dibujada; con "reducir movimiento", también.

## Tipografía y color

- Atkinson Hyperlegible Next (Braille Institute, licencia libre), diseñada para leerse con baja visión. Aquí se carga de Google Fonts; en producción se sirve desde el propio dominio.
- Albero `#E2AE45`, tinta `#1F1A14`, tierra `#2B1F26`, hifa `#EFE8DA`, lila `#A999E0`. Lila es lo que entra; albero, lo que sale.

## Lo que falta decidir

- Si la landing se hace a partir de esta maqueta o con Claude Design (`docs/07-landing.md`).
- Que cada asiento, acuerdo y propuesta tenga dirección propia para poder enlazarlo.
- El aviso legal.
