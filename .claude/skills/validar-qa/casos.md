# Casos de /validar-qa

Un id por fila, sin repetirse. «Auto» es `scripts/qa.py`. «Navegador» lo ejerce la sesión con
Playwright contra el mismo port-forward. «Persona» lo mira una persona y lo confirma en la sesión.
Un caso ✖ es **P0** salvo que la columna diga otra cosa.

## Fase 0 · contra qué se valida (cualquier ✖ corta)

| Id | Quién | Qué se comprueba |
|---|---|---|
| F0a | Auto | El Deployment de QA corre `…:vX.Y.Z@sha256:…`, con la versión pedida y fijada por digest |
| F0b | Auto | La etiqueta `vX.Y.Z` de GHCR apunta a ese mismo digest |
| F0c | Auto | Todos los pods están listos con ese digest, se dice cuántos reinicios y en qué arquitectura |
| F0d | Auto | La Application de QA está `Synced/Healthy` |
| F0e | Auto | La etiqueta git `vX.Y.Z` es un commit cuya imagen `sha-<7>` es ese mismo digest |
| F0f | Auto | La épica de la versión deja validarla (el comentario «flow · release» del flujo automático, D30, y contraste con sus casillas). ✖ da NO CONCLUYENTE, no NO APTO |

## Servidor

| Id | Quién | Qué se comprueba |
|---|---|---|
| S1 | Auto | `web/imagen/comprueba.py` con el `web/cabeceras` **del commit de la etiqueta**: estado de `/`, de una fuente y de un 404, las cabeceras exactas, un nonce distinto en cada respuesta, sin cookies y sin la versión del servidor |
| S2 | Auto | El pod corre como uid 101, sin root, con la raíz de solo lectura, sin escalada de privilegios y sin capacidades |
| S3 | Auto | Una redirección de directorio es relativa (`/fuentes` → `/fuentes/`), no `http://…:8080` |

## Contenido

| Id | Quién | Qué se comprueba |
|---|---|---|
| C1 | Auto | Cada fichero de `web/publico` en el commit de la etiqueta se sirve byte a byte igual |
| C2 | Auto | Ningún recurso de terceros: `link`, `img`, `script`… sin URL absolutas, y en el CSS ni `url()` de fuera ni `@import`. Los enlaces `<a>` no cuentan: son navegación, no peticiones |
| C3 | Auto | Sin `<script>`, `<style>`, `style=` ni manejadores `on…=` (D26 y la CSP de #12) |
| C4 | Auto | Lleva `noindex` mientras no exista la página de privacidad (D33, #26) |

## Logs y privacidad (#25)

| Id | Quién | Qué se comprueba |
|---|---|---|
| L1 | Auto | Una petición con `X-Forwarded-For`, `CF-Connecting-IP`, `User-Agent`, `Referer` y query inventados no deja ninguno de esos valores en `kubectl logs` |
| L2 | Auto | nginx no pone cookies |

## Navegador

En Playwright, contra el port-forward, primero a 390×844 y después a 1440×900. Lo que se evalúa en la página:

```js
async () => { await document.fonts.ready; return {
  desborda: document.documentElement.scrollWidth > innerWidth,
  fuentes: [...document.fonts].map(f => `${f.family}:${f.status}`),
  cookies: document.cookie, scripts: document.scripts.length,
  deFuera: performance.getEntriesByType('resource').map(r => r.name).filter(n => !n.startsWith(location.origin)) }; }
```

| Id | Quién | Qué se comprueba |
|---|---|---|
| N1 | Navegador | La consola no tiene errores ni avisos, en particular violaciones de CSP, en las dos anchuras |
| N2 | Navegador | `deFuera` está vacío, `cookies` vacío y `scripts` es 0 |
| N3 | Navegador | Las dos familias, «Atkinson Hyperlegible Next» y «Atkinson Hyperlegible Mono», salen `loaded` (la cursiva puede salir `unloaded` si la página no la usa) |
| N4 | Navegador | A 390 no hay desbordamiento horizontal (`desborda: false`) |
| N5 | Navegador | Captura de pantalla completa en las dos anchuras, mirada: la cabecera, la red de filamentos y las secciones se ven como en `main`. Las capturas no se suben al repositorio. Una diferencia visual sin explicación es **P1**, no P0 |

## Persona

| Id | Quién | Qué se comprueba |
|---|---|---|
| H1 | Persona | En **Firefox** de escritorio (el soporte que se mira en este proyecto): la página se ve bien y la red de filamentos crece al desplazarse. La sesión le pide a la persona que lo mire, por el port-forward, y anota su respuesta. Sin respuesta, el frente queda sin ejercer: NO CONCLUYENTE |
