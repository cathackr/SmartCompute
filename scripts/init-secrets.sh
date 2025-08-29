#!/bin/bash
# Initialize secrets in HashiCorp Vault for SmartCompute production

set -e

VAULT_ADDR=${VAULT_ADDR:-http://localhost:8200}
VAULT_TOKEN=${VAULT_ROOT_TOKEN:-dev-only-token}

echo "Initializing SmartCompute secrets in Vault..."

# Wait for Vault to be ready
echo "Waiting for Vault to be ready..."
for i in {1..30}; do
    if vault status > /dev/null 2>&1; then
        echo "Vault is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Timeout waiting for Vault"
        exit 1
    fi
    sleep 2
done

# Enable KV v2 secrets engine if not already enabled
echo "Enabling KV v2 secrets engine..."
vault secrets enable -version=2 kv || echo "KV secrets engine already enabled"

# Set database passwords
echo "Setting database credentials..."
vault kv put secret/database \
    DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -hex 16)}" \
    PAYMENT_DB_PASSWORD="${PAYMENT_DB_PASSWORD:-$(openssl rand -hex 16)}" \
    MONITORING_DB_PASSWORD="${MONITORING_DB_PASSWORD:-$(openssl rand -hex 16)}"

# Set service credentials
echo "Setting service credentials..."
vault kv put secret/services \
    REDIS_PASSWORD="${REDIS_PASSWORD:-$(openssl rand -hex 16)}" \
    JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32)}" \
    PAYMENT_WEBHOOK_SECRET="${PAYMENT_WEBHOOK_SECRET:-$(openssl rand -hex 24)}" \
    GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-$(openssl rand -hex 12)}"

# Set API keys and external service credentials
echo "Setting API credentials..."
vault kv put secret/api \
    STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-sk_test_placeholder}" \
    STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET:-whsec_placeholder}" \
    SENDGRID_API_KEY="${SENDGRID_API_KEY:-SG.placeholder}" \
    SENTRY_DSN="${SENTRY_DSN:-https://placeholder@sentry.io/project}"

# Set encryption keys
echo "Setting encryption keys..."
vault kv put secret/encryption \
    ENCRYPTION_KEY="${ENCRYPTION_KEY:-$(openssl rand -hex 32)}" \
    SIGNING_KEY="${SIGNING_KEY:-$(openssl rand -hex 32)}"

# Create policies for different services
echo "Creating Vault policies..."

# Policy for API service
vault policy write smartcompute-api - <<EOF
path "secret/data/database" {
  capabilities = ["read"]
}
path "secret/data/services" {
  capabilities = ["read"]
}
path "secret/data/api" {
  capabilities = ["read"]
}
EOF

# Policy for payment service
vault policy write smartcompute-payment - <<EOF
path "secret/data/database" {
  capabilities = ["read"]
}
path "secret/data/services" {
  capabilities = ["read"]
}
path "secret/data/encryption" {
  capabilities = ["read"]
}
EOF

# Policy for monitoring service
vault policy write smartcompute-monitoring - <<EOF
path "secret/data/database" {
  capabilities = ["read"]
}
path "secret/data/services" {
  capabilities = ["read"]
}
EOF

# Create tokens for services
echo "Creating service tokens..."
API_TOKEN=$(vault write -field=token auth/token/create policies=smartcompute-api ttl=168h)
PAYMENT_TOKEN=$(vault write -field=token auth/token/create policies=smartcompute-payment ttl=168h)
MONITORING_TOKEN=$(vault write -field=token auth/token/create policies=smartcompute-monitoring ttl=168h)

echo "Service tokens created:"
echo "API_TOKEN: $API_TOKEN"
echo "PAYMENT_TOKEN: $PAYMENT_TOKEN" 
echo "MONITORING_TOKEN: $MONITORING_TOKEN"

# Save tokens to secure file
cat > /tmp/service-tokens.env <<EOF
# SmartCompute Service Tokens - Store securely
export SMARTCOMPUTE_API_VAULT_TOKEN=$API_TOKEN
export SMARTCOMPUTE_PAYMENT_VAULT_TOKEN=$PAYMENT_TOKEN
export SMARTCOMPUTE_MONITORING_VAULT_TOKEN=$MONITORING_TOKEN
EOF

echo "Tokens saved to /tmp/service-tokens.env"
echo "Move this file to a secure location and source it in your deployment"

echo "SmartCompute secrets initialization completed successfully!"