# web/Dockerfile (Alpine)
FROM nginx:1.27.5-alpine3.21

# tools for healthcheck
RUN set -eux; \
    apk add --no-cache curl; \
    # drop optional modules that drag in libxml2/libxslt
    apk del --no-cache nginx-module-xslt nginx-module-njs || true; \
    # ensure libxml2 is upgraded to fixed r6 (try strict, fall back to plain upgrade)
    (apk add --no-cache --upgrade 'libxml2>=2.13.4-r6' || apk upgrade --no-cache libxml2); \
    rm -rf /var/cache/apk/*

# your nginx.conf if you have one
# COPY nginx.conf /etc/nginx/nginx.conf

# if you already have prebuilt assets
COPY dist/ /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/ || exit 1
