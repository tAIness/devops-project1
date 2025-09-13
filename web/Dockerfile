# web/Dockerfile
FROM nginx:1.27.5-bookworm

# small utilities for healthcheck/debug
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# your nginx config (adjust path if you keep it elsewhere)
# COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# static site
COPY . /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/health || exit 1
