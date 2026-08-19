# --- Etapa 1: build de producción (Vite) ---
FROM node:20-slim AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# VITE_* se hornea en el bundle en build time (no en runtime): se recibe
# como build-arg desde docker-compose para no hardcodear la URL pública.
ARG VITE_API_URL=/api/v1
ARG VITE_APP_NAME=Tutunaku
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
RUN npm run build

# --- Etapa 2: nginx sirviendo el build estático ---
# Esta MISMA imagen nginx es también el proxy inverso + balanceador de carga
# hacia el backend (ver deploy/nginx/nginx.conf montado en docker-compose):
# un solo borde nginx sirve el SPA, reparte /api y /socket.io entre las
# réplicas del backend, y termina TLS — evita un segundo proxy redundante.
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/healthz || exit 1
