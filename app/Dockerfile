# web/Dockerfile
FROM nginx:1.27.5-alpine3.21

RUN apk add --no-cache curl \
 && echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \
 && apk update \
 && apk --no-cache upgrade libxml2 libxslt \
 && sed -i '$d' /etc/apk/repositories

# COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/health || exit 1
