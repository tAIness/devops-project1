# app/Dockerfile
FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    GUNICORN_WORKERS=2

WORKDIR /app

# context is app/, so drop the "app/"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# context is app/, so this brings in your app code
COPY . .
EXPOSE 8000

CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS} -b 0.0.0.0:${PORT} app:app"]
