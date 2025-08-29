#!/bin/bash
# SmartCompute Release Verification Script
# Verifies release artifacts including checksums and GPG signatures

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
RELEASE_TAG="${1:-}"
GITHUB_REPO="${GITHUB_REPO:-gatux/smartcompute}"
TEMP_DIR="/tmp/smartcompute-verify-$$"
VERIFICATION_LOG="$TEMP_DIR/verification.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message" >&2
            echo "[$timestamp] [ERROR] $message" >> "$VERIFICATION_LOG"
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            echo "[$timestamp] [WARN] $message" >> "$VERIFICATION_LOG"
            ;;
        INFO)
            echo -e "${GREEN}[INFO]${NC} $message"
            echo "[$timestamp] [INFO] $message" >> "$VERIFICATION_LOG"
            ;;
        DEBUG)
            echo -e "${BLUE}[DEBUG]${NC} $message"
            echo "[$timestamp] [DEBUG] $message" >> "$VERIFICATION_LOG"
            ;;
    esac
}

# Error handler
error_exit() {
    log ERROR "$1"
    cleanup
    exit 1
}

# Cleanup function
cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Show usage
show_usage() {
    cat << EOF
SmartCompute Release Verification Script

Usage: $0 [RELEASE_TAG]

Arguments:
  RELEASE_TAG    Git tag of the release to verify (e.g., v1.0.0)
                 If not provided, will use the latest release

Examples:
  $0                    # Verify latest release
  $0 v1.0.0            # Verify specific release

Environment Variables:
  GITHUB_REPO          Repository in format owner/repo (default: gatux/smartcompute)
  GPG_PUBLIC_KEY_URL   URL to public GPG key for verification

The script will:
  1. Download release artifacts
  2. Verify file checksums (SHA256, SHA512, MD5)
  3. Verify GPG signatures
  4. Test installer integrity
  5. Generate verification report
EOF
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    # Check required tools
    local missing_tools=()
    
    for tool in curl gpg sha256sum sha512sum md5sum wget; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log ERROR "Missing required tools: ${missing_tools[*]}"
        log INFO "Please install missing tools and try again"
        exit 1
    fi
    
    log INFO "All prerequisites satisfied"
}

# Get latest release tag
get_latest_release() {
    log INFO "Getting latest release information..."
    
    local api_url="https://api.github.com/repos/$GITHUB_REPO/releases/latest"
    local latest_tag
    
    latest_tag=$(curl -s "$api_url" | grep '"tag_name":' | sed -E 's/.*"tag_name": "([^"]*)",/\1/')
    
    if [[ -z "$latest_tag" ]]; then
        error_exit "Could not determine latest release tag"
    fi
    
    echo "$latest_tag"
}

# Download release artifacts
download_artifacts() {
    local tag="$1"
    log INFO "Downloading release artifacts for $tag..."
    
    local base_url="https://github.com/$GITHUB_REPO/releases/download/$tag"
    local artifacts=(
        "checksums.txt"
        "checksums.txt.asc"
        "install.sh"
        "installers-linux-x86_64.tar.gz"
        "installers-linux-aarch64.tar.gz"
        "installers-windows-x86_64.tar.gz"
        "installers-macos-x86_64.tar.gz"
        "installers-macos-arm64.tar.gz"
    )
    
    cd "$TEMP_DIR"
    
    local downloaded_files=()
    local failed_files=()
    
    for artifact in "${artifacts[@]}"; do
        log INFO "Downloading $artifact..."
        
        if wget -q --timeout=30 "$base_url/$artifact"; then
            downloaded_files+=("$artifact")
            log INFO "Successfully downloaded: $artifact"
        else
            failed_files+=("$artifact")
            log WARN "Failed to download: $artifact"
        fi
    done
    
    if [[ ${#downloaded_files[@]} -eq 0 ]]; then
        error_exit "No artifacts could be downloaded"
    fi
    
    log INFO "Downloaded ${#downloaded_files[@]} artifacts, ${#failed_files[@]} failed"
    
    # List downloaded files
    log INFO "Available files for verification:"
    ls -la
}

# Import GPG public key
import_gpg_key() {
    log INFO "Importing SmartCompute public GPG key..."
    
    local public_key_sources=(
        "https://github.com/$GITHUB_REPO/releases/download/gpg-keys/smartcompute-public.asc"
        "https://raw.githubusercontent.com/$GITHUB_REPO/main/security/gpg/smartcompute-public.asc"
        "$PROJECT_ROOT/security/gpg/smartcompute-public.asc"
    )
    
    local imported=false
    
    for source in "${public_key_sources[@]}"; do
        log INFO "Trying to import key from: $source"
        
        if [[ "$source" =~ ^https?:// ]]; then
            # Download from URL
            if wget -q -O public-key.asc "$source"; then
                if gpg --import public-key.asc 2>/dev/null; then
                    imported=true
                    log INFO "Successfully imported GPG key from $source"
                    break
                fi
            fi
        elif [[ -f "$source" ]]; then
            # Local file
            if gpg --import "$source" 2>/dev/null; then
                imported=true
                log INFO "Successfully imported GPG key from local file"
                break
            fi
        fi
    done
    
    if [[ "$imported" != "true" ]]; then
        log WARN "Could not import GPG public key - signature verification will be skipped"
        return 1
    fi
    
    # List imported keys
    log INFO "GPG keys available for verification:"
    gpg --list-keys "SmartCompute" 2>/dev/null || true
}

# Verify GPG signature
verify_signature() {
    log INFO "Verifying GPG signature..."
    
    if [[ ! -f "checksums.txt" ]] || [[ ! -f "checksums.txt.asc" ]]; then
        log WARN "Missing signature files - skipping GPG verification"
        return 1
    fi
    
    if gpg --verify checksums.txt.asc checksums.txt 2>&1; then
        log INFO "✅ GPG signature verification PASSED"
        return 0
    else
        log ERROR "❌ GPG signature verification FAILED"
        return 1
    fi
}

# Verify checksums
verify_checksums() {
    log INFO "Verifying file checksums..."
    
    if [[ ! -f "checksums.txt" ]]; then
        log WARN "checksums.txt not found - skipping checksum verification"
        return 1
    fi
    
    local verification_results=()
    local total_checks=0
    local passed_checks=0
    
    # Extract and verify each checksum
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]] && continue
        
        # Parse checksum line (format: hash filename)
        local hash_value=$(echo "$line" | awk '{print $1}')
        local filename=$(echo "$line" | awk '{print $2}' | sed 's/^\.\///')
        
        # Skip if file doesn't exist
        [[ ! -f "$filename" ]] && continue
        
        total_checks=$((total_checks + 1))
        
        # Determine hash type by length
        local hash_type=""
        case ${#hash_value} in
            32) hash_type="md5" ;;
            64) hash_type="sha256" ;;
            128) hash_type="sha512" ;;
            *) 
                log WARN "Unknown hash type for $filename"
                continue
                ;;
        esac
        
        # Calculate actual hash
        local actual_hash=""
        case $hash_type in
            md5) actual_hash=$(md5sum "$filename" | awk '{print $1}') ;;
            sha256) actual_hash=$(sha256sum "$filename" | awk '{print $1}') ;;
            sha512) actual_hash=$(sha512sum "$filename" | awk '{print $1}') ;;
        esac
        
        # Compare hashes
        if [[ "$hash_value" == "$actual_hash" ]]; then
            verification_results+=("✅ $filename ($hash_type) - PASSED")
            passed_checks=$((passed_checks + 1))
        else
            verification_results+=("❌ $filename ($hash_type) - FAILED")
            log ERROR "Checksum mismatch for $filename:"
            log ERROR "  Expected: $hash_value"
            log ERROR "  Actual:   $actual_hash"
        fi
        
    done < checksums.txt
    
    # Display results
    log INFO "Checksum verification results:"
    for result in "${verification_results[@]}"; do
        echo "  $result"
    done
    
    log INFO "Checksum verification: $passed_checks/$total_checks checks passed"
    
    if [[ $passed_checks -eq $total_checks ]] && [[ $total_checks -gt 0 ]]; then
        log INFO "✅ All checksum verifications PASSED"
        return 0
    else
        log ERROR "❌ Some checksum verifications FAILED"
        return 1
    fi
}

# Test installer integrity
test_installers() {
    log INFO "Testing installer integrity..."
    
    local installer_files=($(find . -name "installers-*.tar.gz" -type f))
    local test_results=()
    
    if [[ ${#installer_files[@]} -eq 0 ]]; then
        log WARN "No installer archives found for testing"
        return 1
    fi
    
    for installer in "${installer_files[@]}"; do
        local platform=$(basename "$installer" .tar.gz | sed 's/installers-//')
        
        log INFO "Testing installer: $platform"
        
        # Create test directory
        local test_dir="test-$platform"
        mkdir -p "$test_dir"
        
        # Extract installer
        if tar -xzf "$installer" -C "$test_dir"; then
            log INFO "Successfully extracted $platform installer"
            
            # Check for required files
            local required_files=()
            case $platform in
                linux-*|macos-*)
                    required_files=("install.sh")
                    ;;
                windows-*)
                    required_files=("install.bat" "install.ps1")
                    ;;
            esac
            
            local missing_files=()
            for file in "${required_files[@]}"; do
                if [[ ! -f "$test_dir/$file" ]]; then
                    missing_files+=("$file")
                fi
            done
            
            if [[ ${#missing_files[@]} -eq 0 ]]; then
                test_results+=("✅ $platform - All required files present")
                
                # Test script syntax (for shell scripts)
                if [[ -f "$test_dir/install.sh" ]]; then
                    if bash -n "$test_dir/install.sh"; then
                        test_results+=("✅ $platform - Script syntax valid")
                    else
                        test_results+=("❌ $platform - Script syntax error")
                    fi
                fi
            else
                test_results+=("❌ $platform - Missing files: ${missing_files[*]}")
            fi
        else
            test_results+=("❌ $platform - Failed to extract installer")
        fi
    done
    
    # Display test results
    log INFO "Installer integrity test results:"
    for result in "${test_results[@]}"; do
        echo "  $result"
    done
}

# Generate verification report
generate_report() {
    local tag="$1"
    local signature_status="$2"
    local checksum_status="$3"
    local installer_status="$4"
    
    log INFO "Generating verification report..."
    
    local report_file="$TEMP_DIR/verification-report.md"
    
    cat > "$report_file" << EOF
# SmartCompute Release Verification Report

## Release Information
- **Tag:** $tag
- **Repository:** $GITHUB_REPO
- **Verification Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
- **Verifier:** $(whoami)@$(hostname)

## Verification Results

### GPG Signature Verification
Status: **$signature_status**

### Checksum Verification  
Status: **$checksum_status**

### Installer Integrity
Status: **$installer_status**

## Downloaded Artifacts
\`\`\`
$(ls -la "$TEMP_DIR")
\`\`\`

## Verification Log
\`\`\`
$(tail -50 "$VERIFICATION_LOG")
\`\`\`

---
*Report generated by SmartCompute Release Verification Script*
EOF
    
    log INFO "Verification report saved to: $report_file"
    
    # Display report summary
    echo ""
    echo "📊 Verification Summary"
    echo "======================"
    echo "Release: $tag"
    echo "GPG Signature: $signature_status"
    echo "Checksums: $checksum_status"  
    echo "Installers: $installer_status"
    echo ""
    echo "Full report: $report_file"
    echo ""
}

# Main execution
main() {
    # Handle help flag
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        show_usage
        exit 0
    fi
    
    log INFO "Starting SmartCompute release verification..."
    
    check_prerequisites
    
    # Determine release tag
    local tag="$RELEASE_TAG"
    if [[ -z "$tag" ]]; then
        tag=$(get_latest_release)
        log INFO "Using latest release: $tag"
    else
        log INFO "Verifying specified release: $tag"
    fi
    
    # Download artifacts
    download_artifacts "$tag"
    
    # Import GPG key
    local gpg_imported=false
    if import_gpg_key; then
        gpg_imported=true
    fi
    
    # Verify signature
    local signature_status="SKIPPED"
    if [[ "$gpg_imported" == "true" ]]; then
        if verify_signature; then
            signature_status="PASSED"
        else
            signature_status="FAILED"
        fi
    fi
    
    # Verify checksums
    local checksum_status="SKIPPED"
    if verify_checksums; then
        checksum_status="PASSED"
    else
        checksum_status="FAILED"
    fi
    
    # Test installers
    local installer_status="SKIPPED"
    if test_installers; then
        installer_status="PASSED"
    else
        installer_status="FAILED"
    fi
    
    # Generate report
    generate_report "$tag" "$signature_status" "$checksum_status" "$installer_status"
    
    # Determine overall result
    local failed_checks=0
    [[ "$signature_status" == "FAILED" ]] && ((failed_checks++))
    [[ "$checksum_status" == "FAILED" ]] && ((failed_checks++))
    [[ "$installer_status" == "FAILED" ]] && ((failed_checks++))
    
    if [[ $failed_checks -eq 0 ]]; then
        log INFO "🎉 Release verification completed successfully!"
        log INFO "All available checks passed for release $tag"
        exit 0
    else
        log ERROR "❌ Release verification found $failed_checks failed check(s)"
        log ERROR "Please review the verification report for details"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"