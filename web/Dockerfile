FROM nginx:1.27.5-bookworm

# Remove optional modules that pull in libxml2/libxslt paths, then upgrade remaining libs
RUN set -eux; \
  apt-get update; \
  apt-get -y --no-install-recommends purge nginx-module-xslt nginx-module-njs || true; \
  apt-get -y --no-install-recommends autoremove; \
  apt-get -y --no-install-recommends install ca-certificates curl; \
  apt-get -y --no-install-recommends install --only-upgrade zlib1g nginx; \
  rm -rf /var/lib/apt/lists/*

# Optional: your custom nginx.conf
# COPY nginx.conf /etc/nginx/nginx.conf

# Copy static site from the build stage
# If your framework outputs "build" instead of "dist", pass: --build-arg BUILD_DIR=build
ARG BUILD_DIR=dist
COPY --from=build /app/${BUILD_DIR}/ /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/ || exit 1
