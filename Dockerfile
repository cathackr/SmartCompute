# SmartCompute Secure Docker Container
# Multi-stage build with non-root user and health check

# Build stage - Install dependencies
FROM python:3.11-slim AS build

# Environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Production stage - Minimal runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for health check
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY . /app

# Create non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

# Change ownership of app directory
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose application port
EXPOSE 5000

# Health check to monitor application status
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://127.0.0.1:5000/health || exit 1

# Start application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.api.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]