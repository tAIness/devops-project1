# web/Dockerfile
FROM nginx:1.27.5-alpine3.21

# small tools + ensure no optional modules + upgrade zlib to fixed series
RUN set -eux; \
  apk add --no-cache curl ca-certificates; \
  # these modules (if present) pull libxml2/xslt; remove them quietly if absent
  apk del nginx-mod-http-xslt nginx-mod-http-njs 2>/dev/null || true; \
  # bring zlib to the latest (1.3.x on Alpine 3.21)
  apk add --no-cache --upgrade zlib

# If you’re serving plain static files from the repo, set where they live:
#   docker build --build-arg PUBLIC_DIR=dist -t local/web:pr-check web
ARG PUBLIC_DIR=.
COPY ${PUBLIC_DIR}/ /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -fsS http://localhost/ || exit 1
