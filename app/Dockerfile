# app/Dockerfile
FROM python:3.12-slim

# Sensible Python defaults + tunables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    GUNICORN_WORKERS=2

WORKDIR /app

# Minimal OS deps + tini for proper signal handling + curl for healthchecks
RUN apt-get update \
 && apt-get install -y --no-install-recommends tini ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --upgrade --no-cache-dir pip \
 && pip install --no-cache-dir -r requirements.txt

# App source
COPY . .

# Non-root user (fixes previous chown error)
RUN useradd -r -m -U -s /usr/sbin/nologin appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck hits your Flask /health endpoint
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -fsS "http://localhost:${PORT}/health" || exit 1

ENTRYPOINT ["tini", "--"]
# If your WSGI object isn't app:app, change the target below
CMD ["sh", "-c", "exec gunicorn -w ${GUNICORN_WORKERS:-2} -b 0.0.0.0:${PORT:-8000} app:app"]
