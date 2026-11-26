#!/usr/bin/env bash
# guardia.sh — impide publicar datos personales o documentos firmados.
#
# Uso:
#   guardia.sh pre-push           hook de git: revisa los commits que se van a subir (refs por stdin)
#   guardia.sh historia           revisa todo lo alcanzable desde HEAD (CI)
#   guardia.sh commits <args...>  revisa los commits de `git rev-list <args...>` (p. ej. origin/main..HEAD)
#
# Qué revisa en cada commit:
#   - correos de autor y committer: solo noreply de GitHub;
#   - ficheros: nada de PDF, documentos de ofimática ni firmas;
#   - líneas añadidas y mensajes: ni DNI ni NIE, ni términos de la lista local.
#
# Lista local de términos prohibidos (NO se versiona: contiene justo lo que no se publica):
#   ${GUARDIA_DENYLIST:-$HOME/.config/mycelium/guardia-denylist}
#   Un término por línea, sin distinguir mayúsculas ni tildes. Líneas con # son comentarios.
#   Opcional: un tabulador y un patrón de ruta (glob de bash) donde el término sí se permite,
#   p. ej. "calle Mayor<TAB>estatutos.md".
# En CI (CI=true) no hay lista local y esa comprobación se omite; en local, sin lista, falla.
set -euo pipefail

DENYLIST="${GUARDIA_DENYLIST:-$HOME/.config/mycelium/guardia-denylist}"
EXT_PROHIBIDAS='\.(pdf|p7s|xsig|docx?|odt|xlsx?|ods)$'
DNI_NIE='\b[0-9]{8}[A-HJ-NP-TV-Z]\b|\b[XYZ][0-9]{7}[A-HJ-NP-TV-Z]\b'
CORREO_OK='(@users\.noreply\.github\.com|^noreply@github\.com)$'

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fallos=0
falla() { printf 'guardia: %s\n' "$*" >&2; fallos=$((fallos + 1)); }
# Quita tildes y diacríticos para que "Garcia" coincida con "García".
# Sin iconv: la de glibc sale con código 1 ante un carácter que no tiene en ASCII (p. ej. «−»,
# U+2212), aunque lo convierta, y con `set -e` la guardia se cortaba sin decir nada.
plano() {
  python3 -c 'import sys, unicodedata as u
sys.stdout.write("".join(c for c in u.normalize("NFKD", sys.stdin.read()) if not u.combining(c)))'
}

revisar() {
  git rev-list "$@" > "$tmp/commits"
  [ -s "$tmp/commits" ] || return 0
  local log=(git log --no-walk --stdin --no-color)

  # Identidad de los commits
  while read -r c ae ce; do
    [[ $ae =~ $CORREO_OK ]] || falla "commit $c: correo de autor no permitido ($ae)"
    [[ $ce =~ $CORREO_OK ]] || falla "commit $c: correo de committer no permitido ($ce)"
  done < <("${log[@]}" --format='%h %ae %ce' < "$tmp/commits")

  # Ficheros prohibidos
  while read -r f; do
    falla "fichero no permitido: $f"
  done < <("${log[@]}" --format= --name-only --diff-filter=AMRC < "$tmp/commits" | sort -u | grep -iE "$EXT_PROHIBIDAS" || true)

  # Líneas añadidas (ruta<TAB>línea) y mensajes de commit
  "${log[@]}" -p --format= --diff-filter=AMRC --no-ext-diff < "$tmp/commits" \
    | awk '/^\+\+\+ b\//{p=substr($0,7);next} /^\+\+\+ /{next} /^\+/{print p "\t" substr($0,2)}' > "$tmp/lineas"
  "${log[@]}" --format='%B' < "$tmp/commits" | sed 's/^/(mensaje de commit)\t/' >> "$tmp/lineas"

  while IFS=$'\t' read -r ruta linea; do
    falla "posible DNI/NIE en $ruta: $linea"
  done < <(grep -P "\t.*($DNI_NIE)" "$tmp/lineas" || true)

  if [ ! -f "$DENYLIST" ]; then
    if [ "${CI:-}" = "true" ]; then
      echo "guardia: CI sin lista local de términos; se omite esa comprobación"
    else
      falla "no existe $DENYLIST (lista local de términos prohibidos); créala antes de publicar"
    fi
    return 0
  fi

  plano < "$tmp/lineas" > "$tmp/lineas-planas"
  local termino permitido ruta linea
  while IFS=$'\t' read -r termino permitido || [ -n "$termino" ]; do
    [[ -z ${termino// } || $termino == \#* ]] && continue
    termino=$(plano <<< "$termino"); permitido=$(plano <<< "${permitido:-}")
    while IFS=$'\t' read -r ruta linea; do
      # shellcheck disable=SC2053  # el patrón permitido es un glob a propósito
      [[ -n ${permitido:-} && $ruta == $permitido ]] && continue
      falla "término prohibido «$termino» en $ruta: $linea"
    done < <(grep -iF -- "$termino" "$tmp/lineas-planas" || true)
  done < "$DENYLIST"
}

modo="${1:-}"
case "$modo" in
  pre-push)
    cero=$(git hash-object --stdin < /dev/null | tr '0-9a-f' '0')
    while read -r _ local_sha _ remote_sha; do
      [ "$local_sha" = "$cero" ] && continue   # borrado de rama
      if [ "$remote_sha" = "$cero" ]; then
        revisar "$local_sha" --not --remotes
      else
        revisar "$remote_sha..$local_sha"
      fi
    done
    ;;
  historia) revisar HEAD ;;
  commits) shift; revisar "$@" ;;
  *) sed -n '2,8p' "$0" >&2; exit 2 ;;
esac

if [ "$fallos" -gt 0 ]; then
  printf '\nguardia: %d problema(s). No se publica nada.\n' "$fallos" >&2
  exit 1
fi
echo "guardia: sin problemas"
