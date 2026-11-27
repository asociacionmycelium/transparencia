# SPDX-License-Identifier: AGPL-3.0-or-later
# Imagen de la página publicable (#15, D32). Contexto de construcción: web/
#
#   docker buildx build -f web/imagen/Dockerfile web/
#
# Contrato con el clúster (si cambia, cambia también allí): escucha en el 8080, corre como uid 101,
# con la raíz de solo lectura escribe solo en /tmp, y GET / devuelve 200. Las cabeceras van aquí
# dentro, generadas desde web/cabeceras. Ver web/README.md, «Imagen».

# La configuración de nginx se genera en la arquitectura de quien construye: así la etapa final no
# tiene ningún RUN y la variante arm64 no necesita emulación.
FROM --platform=$BUILDPLATFORM python:3.15-alpine3.24@sha256:0f9552bb28711333da16915ec146f5e6bb44a7fdac9ced15dc17c2e0206346dd AS conf
WORKDIR /w
COPY cabeceras imagen/nginx.py ./
RUN python3 -I nginx.py --cabeceras cabeceras --salida nginx.conf

FROM nginxinc/nginx-unprivileged:1.30.6-alpine3.24@sha256:f5116ed4606f3eb015dd4a8e28cb9b351476dc0ad4bc6e9f93b19cec130cdf03
COPY --from=conf /w/nginx.conf /etc/nginx/nginx.conf
# Una raíz propia y vacía: en /usr/share/nginx/html quedarían las páginas de ejemplo de la imagen.
COPY publico/ /srv/pagina/
USER 101:101
EXPOSE 8080
# Sin los scripts de /docker-entrypoint.d: intentan reescribir /etc/nginx, que es de solo lectura,
# y esta configuración no usa plantillas ni variables de entorno.
ENTRYPOINT ["nginx", "-g", "daemon off;"]
