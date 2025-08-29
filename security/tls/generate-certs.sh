#!/bin/bash
# Generate TLS certificates for SmartCompute microservices
# Self-signed CA for development, Let's Encrypt or commercial CA for production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Configuration
CA_NAME="SmartCompute-CA"
COUNTRY="US"
STATE="California"
CITY="San Francisco"
ORG="SmartCompute"
ORG_UNIT="Security"
VALIDITY_DAYS=365

# Service names for certificate generation
SERVICES=(
    "smartcompute-api"
    "smartcompute-core"
    "smartcompute-payment"
    "smartcompute-dashboard"
    "smartcompute-postgres"
    "smartcompute-redis" 
    "smartcompute-vault"
    "smartcompute-nginx"
    "localhost"
)

echo "🔐 Generating TLS certificates for SmartCompute..."

# Create directories
mkdir -p "$CERTS_DIR"/{ca,server,client}
cd "$CERTS_DIR"

# Function to generate certificate configuration
generate_cert_config() {
    local name=$1
    local type=$2  # ca, server, or client
    local san_entries=$3

    cat > "${name}.conf" <<EOF
[req]
default_bits = 4096
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C = $COUNTRY
ST = $STATE
L = $CITY
O = $ORG
OU = $ORG_UNIT
CN = $name

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth, clientAuth
EOF

    if [ "$type" = "ca" ]; then
        cat >> "${name}.conf" <<EOF
basicConstraints = CA:true
keyUsage = cRLSign, keyCertSign
EOF
    elif [ "$type" = "server" ]; then
        cat >> "${name}.conf" <<EOF
basicConstraints = CA:false
subjectAltName = @alt_names

[alt_names]
$san_entries
EOF
    elif [ "$type" = "client" ]; then
        cat >> "${name}.conf" <<EOF
basicConstraints = CA:false
extendedKeyUsage = clientAuth
EOF
    fi
}

# Generate CA certificate
if [ ! -f "ca/ca-key.pem" ] || [ ! -f "ca/ca-cert.pem" ]; then
    echo "📋 Generating Certificate Authority..."
    
    generate_cert_config "$CA_NAME" "ca" ""
    
    # Generate CA private key
    openssl genrsa -out "ca/ca-key.pem" 4096
    
    # Generate CA certificate
    openssl req -new -x509 -key "ca/ca-key.pem" -out "ca/ca-cert.pem" \
        -days $VALIDITY_DAYS -config "${CA_NAME}.conf"
    
    echo "✅ CA certificate generated"
    rm "${CA_NAME}.conf"
else
    echo "✅ CA certificate already exists"
fi

# Generate server certificates for each service
for service in "${SERVICES[@]}"; do
    if [ ! -f "server/${service}-key.pem" ] || [ ! -f "server/${service}-cert.pem" ]; then
        echo "🔑 Generating server certificate for $service..."
        
        # Create SAN entries for each service
        san_entries="DNS.1 = ${service}"
        san_entries="${san_entries}\nDNS.2 = ${service}.local"
        san_entries="${san_entries}\nDNS.3 = ${service}.smartcompute.local"
        
        if [ "$service" = "localhost" ]; then
            san_entries="${san_entries}\nDNS.4 = localhost"
            san_entries="${san_entries}\nIP.1 = 127.0.0.1"
            san_entries="${san_entries}\nIP.2 = ::1"
        elif [[ "$service" == *"nginx"* ]]; then
            san_entries="${san_entries}\nDNS.4 = api.smartcompute.local"
            san_entries="${san_entries}\nDNS.5 = dashboard.smartcompute.local"
            san_entries="${san_entries}\nIP.1 = 127.0.0.1"
        fi
        
        generate_cert_config "$service" "server" "$san_entries"
        
        # Generate private key
        openssl genrsa -out "server/${service}-key.pem" 4096
        
        # Generate certificate signing request
        openssl req -new -key "server/${service}-key.pem" -out "server/${service}.csr" \
            -config "${service}.conf"
        
        # Sign certificate with CA
        openssl x509 -req -in "server/${service}.csr" -CA "ca/ca-cert.pem" \
            -CAkey "ca/ca-key.pem" -CAcreateserial -out "server/${service}-cert.pem" \
            -days $VALIDITY_DAYS -extensions v3_req -extfile "${service}.conf"
        
        # Cleanup
        rm "server/${service}.csr" "${service}.conf"
        
        echo "✅ Server certificate for $service generated"
    else
        echo "✅ Server certificate for $service already exists"
    fi
done

# Generate client certificates for service-to-service authentication
CLIENT_SERVICES=(
    "api-client"
    "core-client"  
    "payment-client"
    "monitoring-client"
)

for client in "${CLIENT_SERVICES[@]}"; do
    if [ ! -f "client/${client}-key.pem" ] || [ ! -f "client/${client}-cert.pem" ]; then
        echo "👥 Generating client certificate for $client..."
        
        generate_cert_config "$client" "client" ""
        
        # Generate private key
        openssl genrsa -out "client/${client}-key.pem" 4096
        
        # Generate certificate signing request
        openssl req -new -key "client/${client}-key.pem" -out "client/${client}.csr" \
            -config "${client}.conf"
        
        # Sign certificate with CA
        openssl x509 -req -in "client/${client}.csr" -CA "ca/ca-cert.pem" \
            -CAkey "ca/ca-key.pem" -CAcreateserial -out "client/${client}-cert.pem" \
            -days $VALIDITY_DAYS -extensions v3_req -extfile "${client}.conf"
        
        # Cleanup
        rm "client/${client}.csr" "${client}.conf"
        
        echo "✅ Client certificate for $client generated"
    else
        echo "✅ Client certificate for $client already exists"
    fi
done

# Generate combined certificate bundles
echo "📦 Creating certificate bundles..."

# Server bundle with full chain
for service in "${SERVICES[@]}"; do
    if [ -f "server/${service}-cert.pem" ]; then
        cat "server/${service}-cert.pem" "ca/ca-cert.pem" > "server/${service}-fullchain.pem"
    fi
done

# Create truststore with CA certificate
cp "ca/ca-cert.pem" "ca-truststore.pem"

# Set appropriate permissions
echo "🔒 Setting secure permissions..."
chmod 600 ca/ca-key.pem
chmod 644 ca/ca-cert.pem
chmod 600 server/*-key.pem
chmod 644 server/*-cert.pem server/*-fullchain.pem
chmod 600 client/*-key.pem  
chmod 644 client/*-cert.pem
chmod 644 ca-truststore.pem

# Generate certificate info summary
echo "📄 Generating certificate summary..."
cat > "certificate-summary.txt" <<EOF
SmartCompute TLS Certificate Summary
Generated: $(date)

Certificate Authority:
  Subject: $(openssl x509 -in ca/ca-cert.pem -noout -subject | sed 's/subject=//')
  Valid: $(openssl x509 -in ca/ca-cert.pem -noout -dates)
  Serial: $(openssl x509 -in ca/ca-cert.pem -noout -serial | sed 's/serial=//')

Server Certificates:
EOF

for service in "${SERVICES[@]}"; do
    if [ -f "server/${service}-cert.pem" ]; then
        echo "  $service:" >> "certificate-summary.txt"
        echo "    Subject: $(openssl x509 -in server/${service}-cert.pem -noout -subject | sed 's/subject=//')" >> "certificate-summary.txt"
        echo "    Valid: $(openssl x509 -in server/${service}-cert.pem -noout -dates)" >> "certificate-summary.txt"
        echo "    SAN: $(openssl x509 -in server/${service}-cert.pem -noout -text | grep -A1 'Subject Alternative Name' | tail -1 | sed 's/^ *//' || echo 'None')" >> "certificate-summary.txt"
        echo "" >> "certificate-summary.txt"
    fi
done

echo "Client Certificates:" >> "certificate-summary.txt"
for client in "${CLIENT_SERVICES[@]}"; do
    if [ -f "client/${client}-cert.pem" ]; then
        echo "  $client:" >> "certificate-summary.txt"
        echo "    Subject: $(openssl x509 -in client/${client}-cert.pem -noout -subject | sed 's/subject=//')" >> "certificate-summary.txt"
        echo "    Valid: $(openssl x509 -in client/${client}-cert.pem -noout -dates)" >> "certificate-summary.txt"
        echo "" >> "certificate-summary.txt"
    fi
done

echo ""
echo "🎉 Certificate generation completed!"
echo ""
echo "Generated files:"
echo "  📁 ca/              - Certificate Authority files"
echo "  📁 server/          - Server certificates for services"
echo "  📁 client/          - Client certificates for mutual auth"
echo "  📄 ca-truststore.pem - CA certificate for trust store"
echo "  📄 certificate-summary.txt - Certificate details"
echo ""
echo "⚠️  Security Notes:"
echo "  • Keep ca/ca-key.pem secure - it can sign new certificates"
echo "  • Distribute ca-truststore.pem to all services for validation"
echo "  • Use server certificates for TLS termination"  
echo "  • Use client certificates for mutual authentication"
echo "  • Certificates are valid for $VALIDITY_DAYS days"
echo ""
echo "🔄 To renew certificates before expiry, delete specific cert files and re-run this script"