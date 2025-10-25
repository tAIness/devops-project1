# web/Dockerfile
FROM nginx:1.27.5-alpine3.21

# Install curl for healthchecks, remove default site, and upgrade known vulnerable libs
RUN set -eux; \
    apk update; \
    apk add --no-cache curl; \
    rm -f /usr/share/nginx/html/index.html /etc/nginx/conf.d/default.conf; \
    apk upgrade --no-cache libxml2 libxslt

# Copy nginx config (this replaces the main config file)
COPY nginx.conf /etc/nginx/nginx.conf

# Static site content
COPY static/index.html /usr/share/nginx/html/index.html
COPY static/css/       /usr/share/nginx/html/css/
COPY assets/           /usr/share/nginx/html/assets/
COPY images/           /usr/share/nginx/html/images/
COPY game/             /usr/share/nginx/html/game/
COPY leaderboard/      /usr/share/nginx/html/leaderboard/

# (Optional) lock down perms so nginx can read everything
RUN chmod -R a+rX /usr/share/nginx/html

# Healthcheck hits nginx directly
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/ || exit 1
