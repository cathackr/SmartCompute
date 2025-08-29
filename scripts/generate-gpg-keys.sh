#!/bin/bash
# SmartCompute GPG Key Generation Script
# Generates GPG signing keys for release authentication

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
REAL_NAME="${GPG_REAL_NAME:-SmartCompute Release Signing}"
EMAIL="${GPG_EMAIL:-releases@smartcompute.com}"
KEY_TYPE="${GPG_KEY_TYPE:-RSA}"
KEY_LENGTH="${GPG_KEY_LENGTH:-4096}"
EXPIRE_DATE="${GPG_EXPIRE_DATE:-2y}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        INFO)
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        DEBUG)
            echo -e "${BLUE}[DEBUG]${NC} $message"
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if GPG is installed
    if ! command -v gpg &> /dev/null; then
        log ERROR "GPG is not installed. Please install GPG first."
        log INFO "Ubuntu/Debian: sudo apt-get install gnupg"
        log INFO "CentOS/RHEL: sudo yum install gnupg2"
        log INFO "macOS: brew install gnupg"
        exit 1
    fi
    
    # Check GPG version
    GPG_VERSION=$(gpg --version | head -1 | awk '{print $3}')
    log INFO "GPG version: $GPG_VERSION"
    
    log INFO "Prerequisites check completed"
}

# Generate GPG key configuration
generate_key_config() {
    log INFO "Generating GPG key configuration..."
    
    cat > /tmp/gpg-key-config << EOF
Key-Type: $KEY_TYPE
Key-Length: $KEY_LENGTH
Subkey-Type: $KEY_TYPE
Subkey-Length: $KEY_LENGTH
Name-Real: $REAL_NAME
Name-Email: $EMAIL
Expire-Date: $EXPIRE_DATE
Preferences: SHA512 SHA384 SHA256 SHA224 AES256 AES192 AES CAST5 ZLIB BZIP2 ZIP Uncompressed
Keyserver: hkps://keys.openpgp.org
%pubring SmartCompute-public.gpg
%secring SmartCompute-secret.gpg
%commit
%echo SmartCompute GPG key generated successfully
EOF

    log INFO "Key configuration created"
}

# Generate GPG key
generate_gpg_key() {
    log INFO "Generating GPG key..."
    log WARN "This may take several minutes depending on system entropy..."
    
    # Generate key using batch mode
    if gpg --batch --generate-key /tmp/gpg-key-config; then
        log INFO "GPG key generated successfully"
    else
        log ERROR "Failed to generate GPG key"
        exit 1
    fi
    
    # Clean up config file
    rm -f /tmp/gpg-key-config
}

# Export keys
export_keys() {
    log INFO "Exporting GPG keys..."
    
    # Create keys directory
    mkdir -p "$PROJECT_ROOT/security/gpg"
    
    # Get key ID
    KEY_ID=$(gpg --list-secret-keys --keyid-format LONG "$EMAIL" | grep sec | awk '{print $2}' | cut -d'/' -f2)
    
    if [ -z "$KEY_ID" ]; then
        log ERROR "Could not find generated key ID"
        exit 1
    fi
    
    log INFO "Key ID: $KEY_ID"
    
    # Export public key
    gpg --armor --export "$KEY_ID" > "$PROJECT_ROOT/security/gpg/smartcompute-public.asc"
    log INFO "Public key exported to: security/gpg/smartcompute-public.asc"
    
    # Export private key (for GitHub secrets)
    gpg --armor --export-secret-keys "$KEY_ID" > "$PROJECT_ROOT/security/gpg/smartcompute-private.asc"
    log INFO "Private key exported to: security/gpg/smartcompute-private.asc"
    
    # Create base64 encoded version for GitHub secrets
    base64 -i "$PROJECT_ROOT/security/gpg/smartcompute-private.asc" > "$PROJECT_ROOT/security/gpg/smartcompute-private-base64.txt"
    log INFO "Base64 private key created: security/gpg/smartcompute-private-base64.txt"
    
    # Export key fingerprint
    gpg --fingerprint --keyid-format LONG "$KEY_ID" > "$PROJECT_ROOT/security/gpg/key-fingerprint.txt"
    log INFO "Key fingerprint exported to: security/gpg/key-fingerprint.txt"
    
    # Create key information file
    cat > "$PROJECT_ROOT/security/gpg/key-info.txt" << EOF
SmartCompute Release Signing Key Information
==========================================

Key ID: $KEY_ID
Email: $EMAIL
Real Name: $REAL_NAME
Created: $(date)

Key Files:
- Public key: security/gpg/smartcompute-public.asc
- Private key: security/gpg/smartcompute-private.asc
- Base64 private key: security/gpg/smartcompute-private-base64.txt
- Fingerprint: security/gpg/key-fingerprint.txt

GitHub Secrets Setup:
1. Add GPG_PRIVATE_KEY secret with content from smartcompute-private-base64.txt
2. Add GPG_PASSPHRASE secret with the passphrase used during key generation

Usage:
- Import public key: gpg --import security/gpg/smartcompute-public.asc
- Verify signatures: gpg --verify checksums.txt.asc checksums.txt

Security Notes:
- Keep the private key file secure and never commit to repository
- The private key should only be used in secure CI/CD environments
- Consider using hardware security keys for additional security
EOF
    
    log INFO "Key information saved to: security/gpg/key-info.txt"
}

# Create .gitignore for GPG directory
create_gitignore() {
    log INFO "Creating .gitignore for GPG directory..."
    
    cat > "$PROJECT_ROOT/security/gpg/.gitignore" << EOF
# GPG Private Keys - NEVER commit these
*-private.asc
*-private-base64.txt
*-secret.gpg

# Temporary files
*.tmp
*.temp

# Allow public keys and documentation
!*-public.asc
!*.md
!key-info.txt
!key-fingerprint.txt
!.gitignore
EOF
    
    log INFO ".gitignore created for GPG directory"
}

# Verify key generation
verify_key() {
    log INFO "Verifying generated key..."
    
    # Create test file
    echo "SmartCompute GPG signature test" > /tmp/test-sign.txt
    
    # Sign test file
    if gpg --detach-sign --armor --local-user "$EMAIL" /tmp/test-sign.txt; then
        log INFO "Test signing successful"
        
        # Verify signature
        if gpg --verify /tmp/test-sign.txt.asc /tmp/test-sign.txt; then
            log INFO "Test verification successful"
        else
            log WARN "Test verification failed"
        fi
        
        # Clean up test files
        rm -f /tmp/test-sign.txt /tmp/test-sign.txt.asc
    else
        log ERROR "Test signing failed"
    fi
}

# Display setup instructions
display_instructions() {
    log INFO "GPG key generation completed successfully!"
    
    echo ""
    echo "🔐 GPG Key Setup Instructions"
    echo "============================"
    echo ""
    echo "📁 Generated Files:"
    echo "  • Public key: security/gpg/smartcompute-public.asc"
    echo "  • Key info: security/gpg/key-info.txt"
    echo "  • Fingerprint: security/gpg/key-fingerprint.txt"
    echo ""
    echo "🚀 GitHub Secrets Setup:"
    echo "1. Go to your repository Settings → Secrets and variables → Actions"
    echo "2. Add the following secrets:"
    echo ""
    echo "   Secret Name: GPG_PRIVATE_KEY"
    echo "   Value: Contents of security/gpg/smartcompute-private-base64.txt"
    echo ""
    echo "   Secret Name: GPG_PASSPHRASE"
    echo "   Value: The passphrase you entered during key generation"
    echo ""
    echo "📋 Commands to copy secrets:"
    echo "   cat security/gpg/smartcompute-private-base64.txt | pbcopy  # macOS"
    echo "   cat security/gpg/smartcompute-private-base64.txt | xclip -selection clipboard  # Linux"
    echo ""
    echo "🔍 Verify Installation:"
    echo "   gpg --import security/gpg/smartcompute-public.asc"
    echo "   gpg --list-keys 'SmartCompute Release Signing'"
    echo ""
    echo "⚠️  Security Reminders:"
    echo "  • Never commit private key files to the repository"
    echo "  • Store private key securely (encrypted backup)"
    echo "  • Use strong passphrase for additional security"
    echo "  • Consider using hardware security keys in production"
    echo ""
    echo "✅ Your GPG signing setup is complete!"
}

# Main execution
main() {
    log INFO "Starting SmartCompute GPG key generation..."
    
    check_prerequisites
    generate_key_config
    generate_gpg_key
    export_keys
    create_gitignore
    verify_key
    display_instructions
    
    log INFO "GPG key generation process completed successfully!"
}

# Check if running directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi