# SmartCompute v3.0.0 Secure Docker Container
# Multi-stage build with non-root user and health check

# Build stage - Install dependencies
FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy project files and install package
COPY pyproject.toml README.md LICENSE LICENSE-COMMERCIAL ./
COPY src/ ./src/

RUN python -m pip install --upgrade pip
RUN pip install .[enterprise]
RUN pip install gunicorn

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
COPY --from=build /usr/local/bin/smartcompute /usr/local/bin/smartcompute
COPY --from=build /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=build /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy application code
COPY src/ ./src/

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
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "smartcompute.api.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]
