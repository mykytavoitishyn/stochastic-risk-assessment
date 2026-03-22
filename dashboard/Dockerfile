# ── Stage 1: build ────────────────────────────────────────────────────────────
# This stage compiles TypeScript and bundles everything into static files.
# The name "builder" lets us reference it in Stage 2.
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files first — same caching trick as Python.
# npm install only re-runs if package.json or package-lock.json changed.
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build.
# "npm run build" runs tsc + vite build → outputs to /app/dist/
COPY . .
RUN npm run build

# ── Stage 2: serve ────────────────────────────────────────────────────────────
# Throw away Node entirely. Copy only the built /dist folder into nginx.
# Final image is ~25MB instead of ~500MB.
FROM nginx:alpine

# Copy built static files to nginx's default serve directory.
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config: forward /api/* requests to the backend container.
# Without this, the browser would try to call /api from the frontend's origin
# and get blocked by CORS or a 404.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
