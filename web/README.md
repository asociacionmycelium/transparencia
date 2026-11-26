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
| Red de filamentos | Sin lotes: unos pocos filamentos sembrados con el nombre | Con lotes, la huella del último (#2) |

## Reglas
- Nada inventado: si no hay dato, la sección lo dice.
- Ningún dato de socios: ni nombres, ni autores de commits, ni correos personales. El domicilio, solo dentro de los Estatutos enlazados (D15).
- Si una fuente cambia de forma (falta una sección del manifiesto, cambian las columnas de `pendientes.md`), el generador se para en vez de publicar algo a medias.
