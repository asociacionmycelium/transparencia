---
name: cerrar-sesion
description: Cierre de una sesión de trabajo en el proyecto de transparencia de la Asociación Mycelium. Consolida los dos repositorios públicos (`transparencia` y `documentos`) en `main` y en `origin`, con commits firmados, la guardia y el revisor de publicación en verde y el CI pasando. Deja por escrito las decisiones (docs/01), la hoja de ruta (docs/06), los asuntos para la Junta (documentos/junta/pendientes.md) y el estado en CLAUDE.md; comprueba que todo lo legal escrito hoy está cotejado en fuente primaria; revisa la salud de la organización en GitHub y termina con `/wiki close`. Úsala siempre que se dé por terminada la sesión, aunque no se pida: "cerramos", "lo dejamos por hoy", "cerrar sesión", "terminamos", "ya está por hoy".
---

# Cerrar sesión (Mycelium · transparencia)

**La conversación no es un sitio donde guardar cosas.** Al cerrar el terminal desaparece, y lo que solo se dijo aquí (un pendiente, un porqué, un asunto para la Junta) se pierde. Cada cosa viva acaba escrita donde se volverá a encontrar: un commit, `docs/01`, `docs/06`, `junta/pendientes.md` o la wiki. Pregunta de control: *si mañana no me acuerdo de nada de hoy, ¿esto sigue estando en algún sitio?*

Lo particular de este proyecto:
- **Hay dos repositorios** y los dos son **públicos**: `transparencia` (este) y `documentos` (hermano, `../documentos`). Es fácil cerrar uno y olvidar el otro.
- **Todo lo que se sube se publica.** Hasta la inscripción en el Registro Nacional de Asociaciones no salen datos de socios: ni nombres, ni nombre unido a cargo, ni correos personales, ni domicilios. Un commit subido con datos personales no se arregla con otro commit: queda en el historial.

Habla con la persona en español.

```bash
TRANSP="$(git rev-parse --show-toplevel)"
DOCS="$(dirname "$TRANSP")/documentos"
export SSH_AUTH_SOCK="${SSH_AUTH_SOCK:-$XDG_RUNTIME_DIR/ssh-agent.socket}"   # firma sin TTY
```

## 1. Lo escrito hoy queda por escrito donde toca

Antes de consolidar, porque estos ficheros también son trabajo de la sesión:

- **Decisiones** → `docs/01-vision-y-decisiones.md`. Cada decisión de hoy, con su número correlativo (D22, D23…), su motivo y lo descartado. No se reescriben las anteriores: si una queda superada, se dice en la nueva. Las decisiones ya tomadas no se reabren sin que la Junta lo pida.
- **Hoja de ruta** → `docs/06-hoja-de-ruta.md`. Lo hecho se marca hecho con fecha y enlace; lo nuevo pendiente entra en su sitio del orden.
- **Estado** → la sección "Estado a DD/MM/AAAA" de `CLAUDE.md`, con la fecha de hoy y el siguiente paso.
- **Asuntos para la Junta** → `$DOCS/junta/pendientes.md`. Todo lo que haya que ratificar, acordar o de lo que haya que dar cuenta, con id `P-NNN`, tipo, origen y artículo de los Estatutos que lo ampara. Si hay reunión convocada, al orden del día. Ver `$DOCS/junta/README.md`.
- **Trabajo pendiente de desarrollo y diseño** → issue en `asociacionmycelium/transparencia` con `enhancement`/`bug`/`documentation` y **una** prioridad (lo que lee `revisar-backlog`):
  - `prioridad-1`: expone o bloquea ahora (algo publicado que no debía, un control de publicación que falla).
  - `prioridad-2`: hay que hacerlo y algo lo empuja (la Junta tiene que verlo, el siguiente paso de `docs/06`).
  - `prioridad-3`: mejora de verdad; puede esperar semanas.
  - `prioridad-4`: apuntado para que no se pierda.

  Cuerpo para quien no estuvo hoy: qué se vio, dónde, la propuesta y el criterio de aceptación, con las D-NN, P-NNN y docs que la explican. **Es público**: nada de datos de socios. Lo que tenga que decidir la Junta no es una issue: va a `pendientes.md` y la issue lo enlaza. Las issues terminadas se cierran con un comentario de qué se hizo. Si una issue se queda sin trabajo hasta que pase algo de fuera, su **último** comentario acaba con una frase fija: «Espera a la Junta: P-NNN», «Espera a la inscripción: …», «Espera a la cuenta bancaria: …» o «Sigue abierta hasta el DD/MM: …».
- **Lo privado** (preferencias personales, datos que no se publican) → `CLAUDE.local.md`, que git ignora. Nunca a un fichero versionado.

## 2. Todo lo legal está cotejado

- Cada artículo de los **Estatutos** citado hoy en los repos se ha comprobado leyendo `$DOCS/estatutos.md`. Los números se confunden con facilidad.
- Cada **norma** citada hoy (ley, reglamento, consulta DGT, sentencia) se ha cotejado en fuente primaria vigente con el subagente `verificador-legal` (BOE consolidado, Cellar/EUR-Lex). Lo que no se pudo verificar dice expresamente "no verificado".
- Si algo no cumple, se corrige antes del paso 3.

## 3. Publicación segura (antes de cada push)

Para **cada** repositorio con commits sin subir:

```bash
for r in "$TRANSP" "$DOCS"; do
  echo "== $r"
  git -C "$r" log --format='%h %G? %ae %s' origin/main..HEAD   # %G? = G (firma válida), correo noreply
  (cd "$r" && scripts/guardia.sh commits origin/main..HEAD)     # sin problemas
done
```

- Lanza el subagente **`revisor-publicacion`** con el rango de cada repositorio. Si devuelve BLOQUEAR, corrige (con `--amend` si el commit no se ha subido) y vuelve a pedir la revisión. Las DUDAS se le plantean a la persona.
- El hook `pre-push` ejecuta la guardia otra vez. **Nunca** `--no-verify`.
- Si falta `~/.config/mycelium/guardia-denylist` en esta máquina, la guardia falla a propósito: no se sube nada hasta que exista.
- Si algo con datos personales ya llegó a un commit **subido**, no reescribas el historial (el ruleset lo impide y además GitHub conserva copias). Díselo a la persona y decidid juntos.

## 4. Consolidar los dos repositorios

```bash
for r in "$TRANSP" "$DOCS"; do
  echo "== $r"; git -C "$r" status -sb; git -C "$r" push origin main
done
for r in transparencia documentos; do
  gh run list -R asociacionmycelium/$r --limit 1 --json headSha,conclusion,status \
    --jq '.[] | "\(.headSha[0:7]) \(.status) \(.conclusion)"'
done
```

- Los dos terminan **limpios, en `main` y sin `[ahead N]`**. Se trabaja directamente sobre `main`: commits pequeños y firmados, con mensajes en español y la atribución de la sesión.
- El CI `guardia` del último commit está en `success` en los dos. Si está en marcha, espera con `gh run watch <id> --exit-status`.
- Si hay PRs de Dependabot abiertas (`gh pr list -R asociacionmycelium/<repo>`), díselo a la persona: actualizan acciones fijadas por SHA y se pueden mezclar desde la web, porque GitHub firma esos commits.

## 5. Salud de la organización en GitHub

```bash
gh api orgs/asociacionmycelium --jq '{is_verified, two_factor_requirement_enabled,
  members_can_create_repositories, members_can_delete_repositories, members_can_change_repo_visibility}'
for r in transparencia documentos; do
  gh api repos/asociacionmycelium/$r/rules/branches/main --jq "\"$r: \" + ([.[].type]|join(\", \"))"
done
```

Esperado: 2FA obligatoria; los miembros no pueden crear, borrar ni cambiar la visibilidad de repositorios; en `main` las reglas `deletion, non_fast_forward, required_linear_history, required_signatures`. Si algo ha cambiado sin que se haya decidido, avisa. Lo que este token no puede leer (Actions, tokens personales, apps OAuth) solo se comprueba en la web.

## 6. Grafo de código (cuando haya código)

Si la sesión tocó código, reindexa con `index_repository` de codebase-memory sobre `$TRANSP` y mira que `nodes`/`edges` no salgan a cero. Mientras el proyecto sea solo documentación, este paso no aplica.

## 7. Memoria y wiki

- Actualiza la memoria del repositorio si algo de hoy no está ya en el código, los docs o el historial.
- Después, `/wiki close`: decide si algo va más allá de este proyecto (una lección sobre una herramienta, un patrón reutilizable en otros repositorios). Si nada lo hace, no toca la wiki.

## 8. Limpieza

Solo lo que creó esta sesión: ficheros temporales del scratchpad, clones de prueba. Nunca la lista local de términos de la guardia, ni `CLAUDE.local.md`, ni la clave de firma.

## Resumen del cierre

- Los commits de **cada** repositorio en `main` y `origin`, con su firma y el CI.
- Resultado de la guardia y del revisor (limpio, o qué se corrigió).
- Decisiones nuevas (D-NN), cambios en la hoja de ruta y asuntos nuevos para la Junta (P-NNN).
- Lo legal verificado hoy y lo que quedó "no verificado".
- Estado de la organización en GitHub y lo que solo puede hacer la persona en la web.
- Lo que se llevó a la wiki.
- El siguiente paso natural.

## Qué NO hacer

- No des el cierre por hecho con trabajo sin subir en cualquiera de los dos repositorios.
- No subas nada sin la guardia y el revisor, ni con `--no-verify`.
- No escribas nombres de socios en ningún fichero versionado, ni siquiera en un ejemplo o un comentario.
- No cites un artículo ni una norma de memoria.
