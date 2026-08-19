FROM python:3.11-slim AS base

# libffi/openssl-dev: requeridos para compilar argon2-cffi/bcrypt en
# arquitecturas sin wheel prebuilt (ej. linux/arm64 en Apple Silicon).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directorio de subidas de usuario (persistido vía volumen en compose).
RUN mkdir -p uploads \
    && useradd --create-home --uid 1000 tutunaku \
    && chown -R tutunaku:tutunaku /app
USER tutunaku

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

# `socket_app` (no `app`) para que /socket.io/ (dashboard en tiempo real y
# el wearable) sirva junto con la API REST desde el mismo proceso, igual que
# en desarrollo (ver backend/main.py). Un solo worker por contenedor: se
# escala horizontalmente con más réplicas del servicio (ver docker-compose.yml
# y Deliverables/WebApp/DeployManual), no con --workers dentro de un mismo
# contenedor, para no duplicar el scheduler ni las conexiones Socket.IO.
CMD ["uvicorn", "app.main:socket_app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
