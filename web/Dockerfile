# web/Dockerfile
# Use Debian (bookworm) nginx and drop optional modules that pulled in libxml2/xslt
FROM nginx:1.27.5-bookworm

RUN set -eux; \
  apt-get update; \
  # remove optional modules that introduce libxml2/xslt
  apt-get -y --no-install-recommends purge nginx-module-xslt nginx-module-njs || true; \
  # clean up any deps pulled by those modules
  apt-get -y --no-install-recommends autoremove; \
  # small tools
  apt-get -y --no-install-recommends install ca-certificates curl; \
  # upgrade packages with past CVEs (zlib, nginx)
  apt-get -y --no-install-recommends install --only-upgrade zlib1g nginx; \
  rm -rf /var/lib/apt/lists/*

# If you’re serving a plain static site from the repo, this copies everything in web/
# into the nginx html root. If your build outputs to a subfolder, set PUBLIC_DIR at build time.
#   e.g. docker build --build-arg PUBLIC_DIR=dist -t local/web:pr-check web
ARG PUBLIC_DIR=.
COPY ${PUBLIC_DIR}/ /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -fsS http://localhost/ || exit 1
