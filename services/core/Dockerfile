# SmartCompute Core Engine - Internal Service
# Multi-stage build for internal microservice

FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements-core.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements-core.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy core application code only
COPY services/core/ ./
COPY app/core/ ./app/core/
COPY app/models/ ./app/models/
COPY app/__init__.py ./app/

# Create non-root user
RUN addgroup --system smartcompute && adduser --system --ingroup smartcompute smartcompute

# Change ownership
RUN chown -R smartcompute:smartcompute /app

# Switch to non-root user
USER smartcompute

# Expose internal port
EXPOSE 9000

# Health check for internal service
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://127.0.0.1:9000/health || exit 1

# Start core service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]