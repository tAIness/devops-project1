FROM nginx:1.27.5-alpine3.21

RUN set -eux; \
    apk add --no-cache curl; \
    apk del --no-cache nginx-module-xslt nginx-module-njs || true; \
    (apk add --no-cache --upgrade 'libxml2>=2.13.4-r6' || apk upgrade --no-cache libxml2); \
    rm -rf /var/cache/apk/*

# COPY nginx.conf /etc/nginx/nginx.conf
COPY . /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/ || exit 1
