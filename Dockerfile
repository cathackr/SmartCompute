# SmartCompute Docker Container
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels for metadata
LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.url="https://github.com/cathackr/SmartCompute" \
      org.opencontainers.image.source="https://github.com/cathackr/SmartCompute" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.vendor="Gatux Security" \
      org.opencontainers.image.title="SmartCompute" \
      org.opencontainers.image.description="Performance-based anomaly detection system" \
      org.opencontainers.image.authors="gatux@smartcompute.ai"

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-core.txt requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements-core.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    # For system monitoring
    procps \
    # For GPU detection (optional)
    pciutils \
    # For network monitoring
    net-tools \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Create non-root user for security
RUN groupadd -r smartcompute && useradd -r -g smartcompute smartcompute

# Set working directory
WORKDIR /app

# Copy application code
COPY app/ ./app/
COPY main.py ./
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create directories and set permissions
RUN mkdir -p /app/data /app/logs /app/reports && \
    chown -R smartcompute:smartcompute /app

# Switch to non-root user
USER smartcompute

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL="sqlite:///./data/smartcompute.db" \
    LOG_LEVEL="INFO" \
    HOST="0.0.0.0" \
    PORT="8000"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)"

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "main.py", "--api", "--port", "8000"]