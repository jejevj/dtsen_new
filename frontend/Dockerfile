# ── Stage 1: Build Vue app ────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .

# Semua variabel VITE_ harus di-declare sebagai ARG + ENV agar
# nilai dari `docker compose build args` benar-benar ter-bake
# ke dalam bundle oleh Vite saat `npm run build`.
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_APP_NAME=DTSEN
ARG VITE_APP_VERSION=2.0.0
ARG VITE_USE_MOCK=false
ARG VITE_VIEW_ONLY=false

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_VERSION=$VITE_APP_VERSION
ENV VITE_USE_MOCK=$VITE_USE_MOCK
ENV VITE_VIEW_ONLY=$VITE_VIEW_ONLY

RUN npm run build

# ── Stage 2: Serve dengan Nginx ───────────────────────────────────────────
FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/app.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
