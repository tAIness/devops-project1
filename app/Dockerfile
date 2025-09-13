FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=UTC
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      tini ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade --no-cache-dir pip \
 && pip install --no-cache-dir -r requirements.txt

# create user+group first
RUN useradd -m -U -u 10001 -s /usr/sbin/nologin appuser

# copy code with correct ownership in one go
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["gunicorn","-w","2","-b","0.0.0.0:8000","app:app"]
