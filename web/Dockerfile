FROM nginx:1.27.5-alpine3.21

# tools & remove the default site so only your config is used
RUN set -eux; apk add --no-cache curl; rm -f /usr/share/nginx/html/index.html /etc/nginx/conf.d/default.conf

# nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# static site
COPY static/index.html /usr/share/nginx/html/index.html
COPY static/css/       /usr/share/nginx/html/css/
COPY assets/           /usr/share/nginx/html/assets/
COPY images/           /usr/share/nginx/html/images/
COPY game/             /usr/share/nginx/html/game/
COPY leaderboard/      /usr/share/nginx/html/leaderboard/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/ || exit 1
