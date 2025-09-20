#!/bin/bash
# SmartCompute Payment Server Launcher

echo "🚀 Starting SmartCompute Payment Server..."
echo "============================================"

# Activate virtual environment
source /home/gatux/smartcompute/venv/bin/activate

# Set environment variables for production
export FLASK_ENV=production
export MP_ACCESS_TOKEN="TEST-7123456789012345-123456-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6-123456789"
export MP_CLIENT_ID="7123456789012345"
export MP_CLIENT_SECRET="ABCdefGHIjklMNOpqrSTUvwxYZ123456"
export BITSO_API_KEY="bitso_api_key_12345"
export BITSO_API_SECRET="bitso_api_secret_67890"
export BITSO_CLIENT_ID="bitso_client_12345"

echo "✅ Environment configured"
echo "📊 Payment Gateway will be available at: http://localhost:5000/payment"
echo "🔗 API Endpoints:"
echo "   - MercadoPago: http://localhost:5000/api/create-mp-payment"
echo "   - Bitso: http://localhost:5000/api/create-bitso-payment"
echo ""
echo "🔐 Features enabled:"
echo "   ✅ Real MercadoPago API integration"
echo "   ✅ Real Bitso API integration"
echo "   ✅ Secure payment processing"
echo "   ✅ Webhook handling"
echo "   ✅ Navigation back/forward"
echo "   ✅ Multi-step checkout"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"

# Start the payment server
cd /home/gatux/smartcompute
python3 payments/payment_server.py