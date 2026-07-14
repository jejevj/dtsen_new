# ── Stage 1: Build Vue app ────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .

# VITE_API_BASE_URL akan di-inject via build-arg atau env
# Default /api/v1 agar nginx bisa proxy ke backend
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ── Stage 2: Serve dengan Nginx ───────────────────────────────────────────────
FROM nginx:1.27-alpine

# Hapus config default nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy hasil build Vue
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
