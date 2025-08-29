# SmartCompute Payment Gateway - Isolated Service
# Minimal, hardened service for payment processing

FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy payment service requirements
COPY services/payment/requirements-payment.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements-payment.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy payment service code only
COPY services/payment/ ./

# Create non-root user with minimal privileges
RUN addgroup --system payment && adduser --system --ingroup payment --no-create-home --shell /sbin/nologin payment

# Change ownership
RUN chown -R payment:payment /app

# Switch to non-root user
USER payment

# Expose payment service port (internal only)
EXPOSE 9001

# Health check for payment service
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://127.0.0.1:9001/health || exit 1

# Start payment service
CMD ["python", "-m", "uvicorn", "payment_main:app", "--host", "0.0.0.0", "--port", "9001"]