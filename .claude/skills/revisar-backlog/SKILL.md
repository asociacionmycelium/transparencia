---
name: revisar-backlog
description: Revisa todas las issues abiertas de `asociacionmycelium/transparencia` con sus comentarios, las ordena respetando su `prioridad-1..4` y, dentro de cada nivel, por lo que desbloquea (otras issues, lo que necesita ver la Junta, el orden de `docs/06`) y por lo que expone (datos de socios, citas legales sin cotejar), separa las que esperan algo de fuera (Junta, inscripción, cuenta bancaria) y propone cuál trabajar en esta sesión diciendo si basta con Claude Code o hace falta la Junta, el verificador legal o Claude Design. Úsala siempre que se pregunte por dónde seguir, qué hay pendiente, qué toca hoy, qué issue atacar, "repasa el backlog", "revisa las issues", "qué es lo más urgente", "por dónde empiezo", y también al arrancar una sesión sin tarea asignada, aunque no se nombren las issues.
---

# Revisar el backlog y elegir la issue de la sesión (transparencia)

> Adaptada de una skill de triaje de otro proyecto. Lo que cambia aquí: **el repositorio es público**, así
> que lo que se lee y lo que se propone escribir en una issue se publica; las issues remiten al
> registro de decisiones (`D26`), a los asuntos de la Junta (`P-012`) y a los docs de diseño en
> vez de a informes de hito; lo que más bloquea **no es código sino algo de fuera** (un acuerdo de
> la Junta, la inscripción en el Registro, la cuenta bancaria); y el criterio de daño no es un fallo
> del código sino **publicar lo que no se debe**. Se trabaja directo en `main`, sin worktree.

Qué va dónde, para no mezclar:

| Qué | Dónde |
|---|---|
| Trabajo de desarrollo y diseño (una sesión o varias) | Issues de `transparencia`, con `prioridad-N` |
| Orden acordado y pendientes operativos | `docs/06-hoja-de-ruta.md` |
| Decisiones tomadas | `docs/01-vision-y-decisiones.md` (D-NN) |
| Lo que tiene que conocer o acordar la Junta | `documentos/junta/pendientes.md` (P-NNN, D24). **Nunca** una issue |

Consecuencia práctica: **el contexto que falta no está en la issue, está en `docs/` y en
`junta/pendientes.md`**, y en `git log`, porque en `main` una issue puede quedar resuelta de lado
por otro commit.

## 1. Medir: el triaje

```bash
python3 .claude/skills/revisar-backlog/scripts/triaje.py --json <scratchpad>/triaje.json
```

Una sola llamada a `gh` y una ficha por issue, **ya agrupada por prioridad**: etiquetas, edad,
casillas, `ref<-` (issues abiertas que la mencionan), `cruza a` (otros repos, casi siempre
`documentos`), `decisiones` (D-NN), `junta` (P-NNN), `docs` citados y la cola del último
comentario. Avisa arriba si alguna issue no tiene prioridad o tiene más de una.

El `--json` cachea la respuesta cruda. Reutilízalo en la misma sesión, pero **no** si han pasado
horas o se han tocado issues: bórralo y vuelve a tirar.

Lecturas del triaje que conviene no equivocar:

- **`ref<-` es la señal de taponamiento.** Una issue de `prioridad-3` que tapona a otra de
  `prioridad-2` es un aviso de que alguna etiqueta está mal: dilo.
- **`decisiones`, `junta` y `docs` dicen qué leer, no qué hacer.** Si una issue cita D26, lee D26
  antes de opinar; si cita P-012, mira en `junta/pendientes.md` en qué estado está.
- **«Esperan algo de fuera»** es un grupo aparte dentro de cada prioridad, con una línea por issue.
  Sale de la frase fija del **último** comentario: «Espera a la Junta: …», «Espera a la
  inscripción: …», «Espera a la cuenta bancaria: …» o «Sigue abierta hasta el DD/MM: …». La
  prioridad no cambia. No son candidatas para trabajar, pero sí para comprobar si lo que esperaban
  ya llegó (un acuerdo nuevo en `pendientes.md`, la inscripción en `CLAUDE.md`). Si una del grupo
  tiene trabajo, o al revés, el último comentario no lo dice bien: avísalo. `--completo` saca
  también sus fichas.

Añade después datos baratos que el triaje no trae:

```bash
DOCS="$(dirname "$(git rev-parse --show-toplevel)")/documentos"
git status -sb; git -C "$DOCS" status -sb      # ¿quedó algo sin commitear o sin subir?
git log --oneline -15                          # qué se hizo; una issue puede estar ya resuelta
gh pr list -R asociacionmycelium/transparencia # normalmente solo Dependabot
grep -n '^| D[0-9]' docs/01-vision-y-decisiones.md | tail -3   # últimas decisiones
grep -n '^| P-' "$DOCS/junta/pendientes.md"     # asuntos de la Junta y su estado
sed -n '/^## Pendientes operativos/,/^## /p' docs/06-hoja-de-ruta.md
```

Si un pendiente operativo de `docs/06` es trabajo de sesión y no tiene issue, dilo en el
resumen. No la crees durante la revisión.

## 2. Leer a fondo la lista corta

Escoge 4-6 candidatas (casi siempre: todas las del nivel más alto con trabajo, más lo que las
tapona) y léelas enteras:

```bash
gh issue view <n> -R asociacionmycelium/transparencia --json body,comments --jq '.body, "---", (.comments[] | .body)'
```

`gh issue view --comments` sale vacío en este entorno; usa la forma `--json`.

Y lee lo que citan: la decisión en `docs/01`, el asunto en `junta/pendientes.md`, el doc de
diseño. Lo que buscas:

- **Si el trabajo ya está hecho** en `main` (el `git log` lo dice) o si una decisión posterior lo
  dejó desfasado. Esas van a la línea de descartadas; a veces lo que toca es cerrarlas (se propone,
  no se hace).
- **Si la decisión está tomada** en `docs/01` o solo está la propuesta de la issue. Lo segundo
  significa que la sesión empieza por decidir con la persona, no por hacer.
- **Si choca con una regla dura** de `CLAUDE.md` o con una decisión registrada: datos de socios
  antes de la inscripción, credenciales del ERP en la parte pública (D4), domicilio fuera de los
  Estatutos (D15), JavaScript en la página (D26). Una issue que exige aflojar una no se planifica:
  se escala. **Las decisiones de `docs/01` no se reabren sin que la Junta lo pida.**
- **Si necesita a la Junta** aunque la issue no lo diga: publicar algo en el dominio, contenido
  que la Junta tiene que validar (`docs/07`, «Posible»), cualquier cosa sobre socios.
- **Si depende de otra** aunque el triaje no lo vea (mismo fichero de `demo/`, mismo doc).

### El grafo de código, cuando lo haya

Hoy el repositorio es documentación y la maqueta de `demo/` (tres ficheros). Cuando haya código de
la plataforma y esté indexado en `codebase-memory`, úsalo para acotar el
alcance de una candidata dudosa (`search_graph`, `trace_path`). Hasta entonces, abre los ficheros.

## 3. Ordenar

1. **La etiqueta `prioridad-N` es el primer corte.** La puso la persona (o `cerrar-sesion` con su
   criterio) y se respeta. Si crees que una etiqueta está mal —porque tapona a una de nivel
   superior, porque expone algo, o porque ya está hecha— **dilo y propón el cambio**; no la
   reordenes en silencio.
2. **Dentro de cada nivel, qué desbloquea**: otras issues (`ref<-`), lo que la Junta tiene que ver
   en su próxima reunión (un P-NNN «en orden del día» o «pendiente») y el **orden acordado** de
   `docs/06`.
3. **Después, qué expone mientras no se atiende**: un texto publicado que permite identificar a un
   socio, una cita legal sin cotejar en un doc público, un control de publicación (guardia,
   revisor, firma) que deja pasar algo. Es el análogo de «qué corrompe datos»: lo publicado queda
   en el historial.

El coste, y que la decisión esté o no tomada, **no mueven el ranking**: van en la ficha para que la
elección se haga con los ojos abiertos.

Si dos criterios chocan, di cuál has hecho pesar y por qué, en una frase.

## 4. Presentar

Siempre en este formato, en el terminal (nada de ficheros: envejecen en cuanto se toca una issue).

```markdown
## Ranking

| # | Issue | Prio | Por qué aquí | Coste | Estado real |
|---|-------|------|--------------|-------|-------------|
| 1 | #1 Página de transparencia: qué se enseña ya | 2 | la Junta tiene que verla (P-012) | M | inventario sin decidir |
| 2 | … | … | … | … | … |

## Candidatas

### #1 — <título corto>
**Qué pide** — una o dos frases.
**Qué dicen los comentarios, `docs/` y la Junta** — decisión que la motivó, lo que ya está en
`main`, el P-NNN y su estado, dependencias.
**Desbloqueo / exposición** — a quién destraba, o qué queda expuesto mientras no se atienda.
**Encaje en la sesión** — ver abajo.
```

El ranking lleva **todas** las issues abiertas; la ficha, solo las 3 primeras. Las que esperan
algo de fuera van en **una fila por prioridad** con sus números y lo que esperan. Las de
prioridad 3–4 se pueden resumir en una fila. Las descartadas (hechas, desfasadas, bloqueadas)
van en una línea al final diciendo por qué.

### El «encaje en la sesión» de transparencia

- **¿Quién hace falta además de Claude Code?** La Junta (acuerdo o dar cuenta: se prepara el
  P-NNN, no se decide por ella); el subagente `verificador-legal` (cualquier norma que se cite);
  Claude Design en claude.ai (la landing definitiva, si se elige esa vía en `docs/07`; Claude Code
  no crea artefactos Design).
- **¿Se publica algo?** Todo lo que se sube a estos repositorios es público. Si la issue escribe
  textos o datos, el plan incluye pasar la guardia y el `revisor-publicacion` antes del push.
- **¿Toca `demo/`?** Se regenera con `python3 demo/genera.py` y se mira en el navegador
  (`demo/README.md`); sin JavaScript en la página (D26). Antes de usar algo nuevo de HTML o CSS,
  comprobar su soporte real en Firefox.
- **¿Toca `documentos`?** Es otro repositorio con su propia guardia y su revisor; el cierre los
  consolida los dos.
- **¿Cabe en la sesión?** Si es grande, di cuál sería el primer trozo que cabe hoy y qué se
  podría enseñar al acabar.

## 5. Proponer y pasar a plan

Cierra con una recomendación explícita y su porqué, en dos o tres frases, y **espera**. La
elección es de la persona: puede querer la tercera porque hoy tiene media hora, o ninguna.

Cuando confirme, entra en plan mode con esa issue: ya la has leído entera con lo que cita, así que
no vuelvas a tirar de `gh` ni rehagas el análisis. Lo que falta es mirar los ficheros y escribir el
plan, con cómo se verifica (navegador para `demo/`, guardia y revisor para lo que se publica,
verificador legal para lo legal).

**Sin worktree:** se trabaja directo en `main`, con commits pequeños y firmados (igual que en
`cerrar-sesion`).

## Qué no hacer

- No ignores la prioridad ni la cambies: si una etiqueta parece mal, se dice y se propone.
- No etiquetes, comentes, abras ni cierres issues durante la revisión. Poner el backlog al día es
  trabajo de `cerrar-sesion`; si algo merece un comentario, apúntalo y dilo.
- No conviertas un asunto de la Junta en issue: va a `junta/pendientes.md` (D24).
- No reabras decisiones de `docs/01` porque una issue lo sugiera: se escala a la persona.
- No escribas, ni propongas escribir, nombres de socios, nombres unidos a cargos, correos
  personales ni domicilios en una issue o un comentario: el repositorio es público.
