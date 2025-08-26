# web/Dockerfile
FROM nginx:alpine

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