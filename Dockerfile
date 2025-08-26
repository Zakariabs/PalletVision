# Multi-stage build for simplified PalletVision
FROM node:18-alpine AS frontend-builder

# Build frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy simplified backend code
COPY backend/app.py ./app.py
COPY backend/models.py ./
COPY backend/database_operations.py ./
COPY backend/ai_inference.py ./

# Copy frontend build from previous stage
COPY --from=frontend-builder /frontend/public ./static/

# Create necessary directories
RUN mkdir -p /app/images /app/static/images /app/model

# Expose ports
EXPOSE 3000 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

CMD ["./docker-entrypoint.sh"]