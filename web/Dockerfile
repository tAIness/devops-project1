# --- build stage: produces /app/dist ---
FROM node:20-alpine AS build
WORKDIR /app

# Copy lockfile(s) first for better caching
COPY package.json ./
COPY package-lock.json* pnpm-lock.yaml* yarn.lock* ./

# Install deps using the detected package manager
RUN set -eux; \
  if [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  else npm install; fi

# Copy source and build
COPY . .
# If your build script is not "build", set:  --build-arg BUILD_CMD=your:script
ARG BUILD_CMD=build
RUN npm run "$BUILD_CMD"

# --- runtime stage: harden + serve static assets ---
FROM nginx:1.27.5-alpine3.21

# Healthcheck tool and remove modules that drag in libxml2/libxslt; upgrade libxml2 to r6
RUN set -eux; \
    apk add --no-cache curl; \
    apk del --no-cache nginx-module-xslt nginx-module-njs || true; \
    (apk add --no-cache --upgrade 'libxml2>=2.13.4-r6' || apk upgrade --no-cache libxml2); \
    rm -rf /var/cache/apk/*

# Optional custom config
# COPY nginx.conf /etc/nginx/nginx.conf

# Copy the built site
COPY --from=build /app/dist/ /usr/share/nginx/html/

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -fsS http://localhost/ || exit 1
