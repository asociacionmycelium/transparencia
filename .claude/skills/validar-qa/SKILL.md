---
name: validar-qa
description: Valida a fondo el entorno de QA de la página de transparencia antes de que una versión pase a prod. Comprueba contra qué se valida (versión, digest, ArgoCD, la épica del flujo automático), el servidor y sus cabeceras, que el contenido servido es el del commit, que los logs no guardan datos de quien visita, y la página en el navegador y en Firefox. Da un veredicto APTO / NO APTO / NO CONCLUYENTE con evidencia y escribe el informe que lee release-prod. Úsala antes de promocionar cualquier versión a prod, y siempre que se pregunte "valida QA", "¿está lista para prod?", "damos el visto bueno", "podemos publicar esto".
---

# Validar QA antes de publicar

La página es pública y dice cosas de la asociación: una cabecera que falta, un recurso de fuera
o un log que guarda IP no se ven en la página, pero se publican igual. Lo que hay antes de QA no
mira lo desplegado: el CI de `imagen` prueba la imagen en un runner, no la que corre en el clúster
con sus manifiestos, su Service y su ArgoCD.

Esto es la puerta. `release-prod` solo promociona una versión si existe
`.claude/qa-reports/vX.Y.Z.md` y su línea de veredicto es exactamente `**Veredicto: APTO**`.
**El silencio no promueve**: una versión sin informe no pasa.

## Antes de empezar

- **Desde dónde.** QA solo está en la red local (D32), y su dirección **no se escribe** en este
  repositorio. Se valida desde un equipo con acceso al clúster (`kubectl` sobre el namespace
  `transparencia-qa` y las Applications de `argocd`), `gh` autenticado y el navegador de
  Playwright. Si falta alguno, el frente que lo necesita queda sin ejercer: NO CONCLUYENTE.
- **Por dónde.** Por un port-forward al Service de QA, que no necesita saber la dirección:
  ```bash
  kubectl -n transparencia-qa port-forward svc/transparencia-web 18090:80   # en segundo plano
  ```
  Todo lo de abajo usa `http://127.0.0.1:18090`. Al acabar se cierra.
- **La épica.** El flujo automático (D30) dice si una versión se puede validar en la épica cuyo título empieza por
  esa versión (`v0.1.0 — …`), con la etiqueta `flow:release-lista` o `flow:release-bloqueada` y
  un comentario «flow · release» (decisiones 134-137 del flujo). Sin esa épica, el caso F0f sale
  ✖ y la validación no puede dar APTO.

## Invocación

| Forma | Qué hace |
|---|---|
| `/validar-qa vX.Y.Z` | Completa: la Fase 0 y todos los frentes contra esa versión. Es la única que puede dar APTO |
| `/validar-qa` | Igual, con la versión que QA corre ahora (la de F0a) |
| `/validar-qa rapida` | Solo la Fase 0 y los casos «Auto». **Siempre NO CONCLUYENTE**: sirve para diagnosticar |

## 1. Fase 0 y casos automáticos

```bash
python3 -B .claude/skills/validar-qa/scripts/qa.py vX.Y.Z --url http://127.0.0.1:18090
```

Los casos están en [`casos.md`](casos.md). El script ejerce los F0, S, C y L y escribe una línea
por caso.

- **Si corta en la Fase 0** (F0a-F0e), no se sigue: no se sabe contra qué se valida. NO
  CONCLUYENTE, con lo que dijo.
- **Si F0f sale ✖**, la épica no deja validar. En la completa, **no se sigue**: NO CONCLUYENTE, con
  las hijas de `bloquean` o lo que falte. En `rapida` se anota y se sigue.
- **Si un caso sale ✖ fuera de la Fase 0, es un P0 y la validación se para ahí.** No se siguen los
  frentes que falten: se escribe el NO APTO con lo ejercido, y lo demás «no ejercido (cerrada por
  P0)». Seguir solo cuesta tiempo, porque la versión siguiente lo vuelve a ejercer entero. Lo único
  que se completa es lo que da contexto al propio P0.

## 2. Navegador

Los casos N1-N5 de [`casos.md`](casos.md), con Playwright, contra el mismo port-forward, a 390×844
y a 1440×900. Las capturas se guardan en `.playwright-mcp/` (ignorado por git) y **no se suben**.

## 3. Persona

H1 lo hace una persona en Firefox de escritorio. La sesión se lo pide, con lo que tiene que mirar y
por dónde (el port-forward en su equipo), y anota la respuesta tal cual. Sin respuesta, NO
CONCLUYENTE: no se da por mirado.

## 4. Consolidar y decidir

1. **Cuenta los casos ejercidos**, no las etiquetas, y que no haya ids repetidos (la salida tiene que
   venir vacía):
   ```bash
   grep -cE '^\| [FSCLNH][0-9]+[a-z]? ' .claude/skills/validar-qa/casos.md
   grep -oE '^\| [FSCLNH][0-9]+[a-z]? ' .claude/skills/validar-qa/casos.md | sort | uniq -d
   ```
2. **Escribe el informe** en `.claude/qa-reports/vX.Y.Z.md` con [`informe-plantilla.md`](informe-plantilla.md).
   El repositorio es público: el informe **no lleva** la dirección de QA, nombres de nodo, el
   repositorio de despliegue, la cuenta de nadie ni datos de socios. Lo que `qa.py` imprime
   en stdout ya viene sin eso, y se copia tal cual. Lo de stderr (el detalle de un error) **no** se
   copia: puede llevar la dirección del clúster o rutas locales.
3. **Publícalo** como cualquier otro cambio: `scripts/guardia.sh`, el subagente
   `revisor-publicacion` sobre el rango, commit firmado en `main` y push. Es la autoridad: lo que
   lee `release-prod`.
4. **Si es APTO**, baja el flag de prerelease: `gh release edit vX.Y.Z -R asociacionmycelium/transparencia --prerelease=false`.
   Es la señal, no la autoridad: el flag lo cambia cualquiera y no deja rastro en git.
5. **Si es NO APTO**, cada P0 va a la épica de **esa** versión (la de F0f), nunca a la siguiente:
   en una sección `### Del NO APTO de vX.Y.Z` con su casilla `- [ ] #N · <título>`, y un comentario
   en la épica con el veredicto y el enlace al informe (decisión 141 del flujo). Si el P0 no tiene
   issue, se propone el texto y **la persona decide** si se abre: el repositorio es público y una
   issue se publica.
6. **Cierra el port-forward** y di el veredicto en el terminal, en tres líneas: veredicto, cuántos
   P0, P1 y P2, y la frase que lo justifica.

## El veredicto

- **APTO**: ningún P0, y la Fase 0 y todos los frentes (Auto, Navegador y Persona) ejercidos.
- **NO APTO**: al menos un P0.
- **NO CONCLUYENTE**: ningún P0, pero algo sin ejercer, la Fase 0 cortada o la épica que no deja
  validar. Incluye siempre `rapida`.

No hay cuarta opción. **Un frente que no se pudo ejercer no cuenta como aprobado.**

## Qué no hacer

- **No validar contra prod.** QA es `transparencia-qa`; el script no sabe de otro namespace.
- **No escribir en QA** más que la petición de prueba de L1. No se reinician pods ni se toca ArgoCD:
  si algo hay que arreglar en el clúster, es un hallazgo.
- **No escribir la dirección de QA, nodos o el repositorio de despliegue** en el informe, en una
  issue ni en un comentario.
- **No editar un informe viejo** para cambiar su veredicto. Se valida otra vez y se escribe el
  informe de la versión nueva.
- **No leer el veredicto con `grep APTO`**: casa también con `NO APTO`.
- **No subir capturas** al repositorio.
