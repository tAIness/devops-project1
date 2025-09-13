# app/Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Optional: make logs show timestamps in UTC
ENV TZ=UTC

# Workdir inside the image
WORKDIR /app

# System deps (tini for clean PID1; ca-certs for HTTPS)
RUN apt-get update && apt-get install -y --no-install-recommends \
      tini ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade --no-cache-dir pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy app source (remember CI sets build context to ./app)
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser:app /app
USER appuser

# App port (your compose maps 8000:8000)
ENV PORT=8000
EXPOSE 8000

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/usr/bin/tini","--"]

# Start gunicorn; update module:app if yours differs
CMD ["gunicorn","-w","2","-b","0.0.0.0:8000","app:app"]
