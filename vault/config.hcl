# HashiCorp Vault Configuration for SmartCompute Production

# Storage backend
storage "file" {
  path = "/vault/data"
}

# Network listener
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1  # Only for development/internal networks
}

# API address
api_addr = "http://0.0.0.0:8200"

# Cluster configuration
cluster_addr = "http://0.0.0.0:8201"

# UI configuration
ui = true

# Disable mlock for containers
disable_mlock = true

# Default lease TTL
default_lease_ttl = "168h"  # 1 week
max_lease_ttl = "720h"      # 30 days

# Logging
log_level = "INFO"
log_format = "json"