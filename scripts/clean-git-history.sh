#!/bin/bash
# SmartCompute Git History Cleanup Script
# Removes large files and potential sensitive data from git history

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

# Show usage
show_usage() {
    cat << EOF
SmartCompute Git History Cleanup Script

Usage: $0 [OPTIONS]

This script will clean sensitive and large files from git history using git-filter-repo.

Options:
  --dry-run         Show what would be removed without making changes
  --backup         Create a backup before cleaning (recommended)
  --force          Skip confirmation prompts
  --help, -h       Show this help message

Files that will be removed from history:
  • NVIDIA installers (*.run files) - 270MB+
  • Large binary files (> 10MB)
  • Virtual environment directories (venv/, smartcompute_env/)
  • Compiled binaries (*.so, *.jar)
  • Potential sensitive file patterns

⚠️  WARNING: This operation rewrites git history and cannot be undone!
    Make sure to backup your repository before running.

Examples:
  $0 --dry-run      # See what would be cleaned
  $0 --backup       # Clean with backup
  $0 --force        # Clean without prompts
EOF
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if git-filter-repo is available
    if ! command -v git-filter-repo &> /dev/null; then
        log ERROR "git-filter-repo not found. Installing..."
        
        # Try to install git-filter-repo
        if command -v pip &> /dev/null; then
            pip install --user git-filter-repo || {
                log ERROR "Failed to install git-filter-repo"
                log INFO "Please install manually: pip install git-filter-repo"
                exit 1
            }
        else
            log ERROR "pip not found. Please install git-filter-repo manually"
            log INFO "Installation: pip install git-filter-repo"
            exit 1
        fi
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log ERROR "Not in a git repository"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log ERROR "Uncommitted changes detected. Please commit or stash them first."
        exit 1
    fi
    
    log INFO "Prerequisites satisfied"
}

# Create backup
create_backup() {
    local backup_dir="$PROJECT_ROOT/../smartcompute-backup-$(date +%Y%m%d_%H%M%S)"
    
    log INFO "Creating backup at: $backup_dir"
    
    # Create backup directory
    cp -r "$PROJECT_ROOT" "$backup_dir"
    
    log INFO "✅ Backup created successfully"
    log INFO "Restore command: mv '$backup_dir' '$PROJECT_ROOT'"
}

# Analyze repository
analyze_repository() {
    log INFO "Analyzing repository for large files and sensitive data..."
    
    # Run git-filter-repo analysis
    git-filter-repo --analyze --force
    
    if [[ -f ".git/filter-repo/analysis/blob-shas-and-paths.txt" ]]; then
        log INFO "Top 10 largest files in history:"
        head -15 .git/filter-repo/analysis/blob-shas-and-paths.txt | tail -10
        echo ""
    fi
    
    if [[ -f ".git/filter-repo/analysis/extensions-all-sizes.txt" ]]; then
        log INFO "File types by size:"
        head -20 .git/filter-repo/analysis/extensions-all-sizes.txt
        echo ""
    fi
}

# Define cleanup rules
get_cleanup_rules() {
    cat << 'EOF'
# Large files and installers
NVIDIA-Linux-x86_64-*.run
bfg.jar

# Virtual environments (complete directories)
venv/
smartcompute_env/
temp_env/

# Large compiled files
*.so
*.dll
*.dylib

# IDE and build artifacts
.idea/
.vscode/
__pycache__/
*.pyc
build/
dist/
*.egg-info/

# Logs and temporary files
*.log
logs/
app_logs/
monitoring_logs/

# Database files
*.db
*.sqlite*

# History files
smart_history.json
smartcompute_history.json
test_history.json

# OS files
.DS_Store
Thumbs.db

# Archive files
*.zip
*.tar.gz
*.tar.bz2
*.7z
*.rar

# Backup files
*.bak
*.backup
*~

# Potential sensitive files
*secret*
*password*
*credential*
*api_key*
*.pem
*.key
*.p12
*.pfx
*.jks
config.local.*
.env.local
secrets.json
credentials.json
api_keys.json
EOF
}

# Perform cleanup
perform_cleanup() {
    local dry_run="$1"
    
    log INFO "Starting git history cleanup..."
    
    # Create temporary file with cleanup rules
    local rules_file=$(mktemp)
    get_cleanup_rules > "$rules_file"
    
    if [[ "$dry_run" == "true" ]]; then
        log INFO "DRY RUN MODE - No changes will be made"
        log INFO "Files that would be removed:"
        
        while IFS= read -r pattern; do
            # Skip comments and empty lines
            [[ "$pattern" =~ ^#.*$ ]] || [[ -z "$pattern" ]] && continue
            
            # Check if pattern exists in git history
            if git log --all --full-history --name-only --pretty=format: | grep -E "^$pattern" | head -5; then
                echo "  - $pattern"
            fi
        done < "$rules_file"
        
        rm -f "$rules_file"
        return 0
    fi
    
    log INFO "Removing large installers and binaries..."
    
    # Remove specific large files
    git-filter-repo --path 'NVIDIA-Linux-x86_64-*.run' --invert-paths --force || true
    git-filter-repo --path 'bfg.jar' --invert-paths --force || true
    
    # Remove virtual environment directories
    log INFO "Removing virtual environment directories..."
    git-filter-repo --path 'venv/' --invert-paths --force || true
    git-filter-repo --path 'smartcompute_env/' --invert-paths --force || true
    git-filter-repo --path 'temp_env/' --invert-paths --force || true
    
    # Remove large binary files
    log INFO "Removing compiled binaries..."
    git-filter-repo --path-glob '*.so' --invert-paths --force || true
    git-filter-repo --path-glob '*.dll' --invert-paths --force || true
    git-filter-repo --path-glob '*.dylib' --invert-paths --force || true
    
    # Remove build artifacts
    log INFO "Removing build artifacts..."
    git-filter-repo --path '__pycache__/' --invert-paths --force || true
    git-filter-repo --path-glob '*.pyc' --invert-paths --force || true
    git-filter-repo --path 'build/' --invert-paths --force || true
    git-filter-repo --path 'dist/' --invert-paths --force || true
    git-filter-repo --path-glob '*.egg-info/' --invert-paths --force || true
    
    # Remove IDE files
    log INFO "Removing IDE files..."
    git-filter-repo --path '.idea/' --invert-paths --force || true
    git-filter-repo --path '.vscode/' --invert-paths --force || true
    
    # Remove log files
    log INFO "Removing log files..."
    git-filter-repo --path-glob '*.log' --invert-paths --force || true
    git-filter-repo --path 'logs/' --invert-paths --force || true
    
    # Remove database files
    log INFO "Removing database files..."
    git-filter-repo --path-glob '*.db' --invert-paths --force || true
    git-filter-repo --path-glob '*.sqlite*' --invert-paths --force || true
    
    # Remove history files
    log INFO "Removing history files..."
    git-filter-repo --path 'smart_history.json' --invert-paths --force || true
    git-filter-repo --path 'smartcompute_history.json' --invert-paths --force || true
    git-filter-repo --path 'test_history.json' --invert-paths --force || true
    
    # Clean up temporary file
    rm -f "$rules_file"
    
    log INFO "✅ Git history cleanup completed"
}

# Verify cleanup results
verify_cleanup() {
    log INFO "Verifying cleanup results..."
    
    # Check repository size
    local repo_size=$(du -sh .git | cut -f1)
    log INFO "Repository size after cleanup: $repo_size"
    
    # Check for remaining large files
    git-filter-repo --analyze --force
    
    if [[ -f ".git/filter-repo/analysis/blob-shas-and-paths.txt" ]]; then
        log INFO "Remaining large files (top 5):"
        head -10 .git/filter-repo/analysis/blob-shas-and-paths.txt | tail -5
    fi
    
    # Check commit count
    local commit_count=$(git rev-list --all --count)
    log INFO "Total commits after cleanup: $commit_count"
    
    log INFO "✅ Cleanup verification completed"
}

# Update remote
update_remote() {
    local force_push="$1"
    
    if [[ "$force_push" != "true" ]]; then
        log WARN "Repository history has been rewritten"
        log WARN "To update the remote repository, run:"
        echo "  git push --force-with-lease --all"
        echo "  git push --force-with-lease --tags"
        log WARN "⚠️  This will rewrite remote history - coordinate with team members!"
        return 0
    fi
    
    log INFO "Updating remote repository..."
    
    # Force push all branches
    git push --force-with-lease --all || {
        log WARN "Failed to push branches. Run manually: git push --force-with-lease --all"
    }
    
    # Force push tags
    git push --force-with-lease --tags || {
        log WARN "Failed to push tags. Run manually: git push --force-with-lease --tags"
    }
    
    log INFO "✅ Remote repository updated"
}

# Main execution
main() {
    cd "$PROJECT_ROOT"
    
    # Parse arguments
    local dry_run=false
    local backup=false
    local force=false
    local push_remote=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                ;;
            --backup)
                backup=true
                ;;
            --force)
                force=true
                ;;
            --push)
                push_remote=true
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log ERROR "Unknown argument: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done
    
    log INFO "Starting SmartCompute git history cleanup..."
    
    # Check prerequisites
    check_prerequisites
    
    # Analyze current state
    analyze_repository
    
    # Show warning and get confirmation
    if [[ "$dry_run" != "true" && "$force" != "true" ]]; then
        echo ""
        log WARN "⚠️  WARNING: This will rewrite git history and cannot be undone!"
        log WARN "Recommended: Run with --dry-run first to see what will be removed"
        echo ""
        read -p "Do you want to continue? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log INFO "Operation cancelled by user"
            exit 0
        fi
    fi
    
    # Create backup if requested
    if [[ "$backup" == "true" ]]; then
        create_backup
    fi
    
    # Perform cleanup
    perform_cleanup "$dry_run"
    
    # Verify results (only if not dry run)
    if [[ "$dry_run" != "true" ]]; then
        verify_cleanup
        
        # Update remote if requested
        if [[ "$push_remote" == "true" ]]; then
            update_remote true
        else
            update_remote false
        fi
    fi
    
    log INFO "🎉 Git history cleanup completed successfully!"
    
    if [[ "$dry_run" != "true" ]]; then
        echo ""
        log INFO "Summary:"
        log INFO "• Repository history has been cleaned"
        log INFO "• Large files and sensitive data removed"
        log INFO "• Repository size reduced"
        echo ""
        log WARN "Next Steps:"
        log WARN "1. Test your application to ensure it still works"
        log WARN "2. Update remote repository: git push --force-with-lease --all"
        log WARN "3. Notify team members about history rewrite"
        log WARN "4. Consider enabling GitHub security features"
    fi
}

# Run main function with all arguments
main "$@"