# web/Dockerfile
FROM nginx:1.27.5-bookworm

# If you only serve static files, you don't need xslt or njs.
# Removing them also drops the libxml2 path entirely.
RUN apt-get update \
 && apt-get -y --no-install-recommends purge nginx-module-xslt nginx-module-njs || true \
 && apt-get -y --no-install-recommends autoremove \
 && apt-get -y --no-install-recommends install ca-certificates curl \
 # Upgrade vulnerable libs to patched Debian bookworm versions
 && apt-get -y --no-install-recommends --only-upgrade \
      libxml2 \
      libxslt1.1 \
      zlib1g \
      nginx \
 && rm -rf /var/lib/apt/lists/*

# Copy your site content and nginx.conf as before
# COPY nginx.conf /etc/nginx/nginx.conf
# COPY dist/ /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -fsS http://localhost/ || exit 1
