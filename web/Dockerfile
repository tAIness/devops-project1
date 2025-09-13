# web/Dockerfile
FROM nginx:1.27.5-alpine3.21

# add curl for healthcheck
RUN apk add --no-cache curl

# Upgrade vulnerable libraries to fixed versions
RUN apk --no-cache add --upgrade \
    'libxml2>=2.13.4-r6' \
    'libxslt>=1.1.42-r3'

# Set web root and config locations
ENV WEB_ROOT=/usr/share/nginx/html

# Copy your Nginx config (assumes it's a full server block)
# If your file is already a valid default server config, this is fine.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static site (CSS + index.html)
COPY static/ ${WEB_ROOT}/

# Copy game (served under /game/)
COPY game/ ${WEB_ROOT}/game/

# Copy homepage "hero" images (baked in, not overridden by the volume)
# Move your three images to web/assets/hero/ before building
COPY assets/hero/ ${WEB_ROOT}/assets/hero/

EXPOSE 80

CMD ["nginx","-g","daemon off;"]
