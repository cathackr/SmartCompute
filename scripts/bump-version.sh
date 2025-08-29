#!/bin/bash
# SmartCompute Version Bump Script
# Automatically increments version numbers following semantic versioning

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
VERSION_FILES=(
    "main.py"
    "pyproject.toml"
    "setup.py"
)

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
SmartCompute Version Bump Script

Usage: $0 <increment_type> [options]

Increment Types:
  major          Increment major version (x.y.z -> (x+1).0.0)
  minor          Increment minor version (x.y.z -> x.(y+1).0)
  patch          Increment patch version (x.y.z -> x.y.(z+1))
  prerelease     Increment prerelease version (x.y.z-alpha.n -> x.y.z-alpha.(n+1))
  
Options:
  --dry-run      Show what would be changed without making changes
  --commit       Automatically commit the version changes
  --tag          Create git tag after bumping version
  --push         Push changes and tags to remote
  --changelog    Update CHANGELOG.md with new version entry
  --help, -h     Show this help message

Examples:
  $0 patch                    # Bump patch version
  $0 minor --commit --tag     # Bump minor, commit, and tag
  $0 major --dry-run          # Show what major bump would do
  $0 prerelease --changelog   # Bump prerelease and update changelog

Environment Variables:
  VERSION_PREFIX    Prefix for version tags (default: 'v')
  PRERELEASE_ID     Prerelease identifier (default: 'alpha')

The script will:
  1. Parse current version from project files
  2. Calculate new version based on increment type
  3. Update version in all relevant files
  4. Optionally update CHANGELOG.md
  5. Optionally commit changes and create git tag
EOF
}

# Parse version string
parse_version() {
    local version="$1"
    
    # Remove 'v' prefix if present
    version="${version#v}"
    
    # Extract components using regex
    if [[ "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)(-([a-zA-Z]+)\.([0-9]+))?$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"
        PATCH="${BASH_REMATCH[3]}"
        PRERELEASE_ID_CURRENT="${BASH_REMATCH[5]}"
        PRERELEASE_NUM="${BASH_REMATCH[6]}"
    else
        log ERROR "Invalid version format: $version"
        log INFO "Expected format: x.y.z or x.y.z-prerelease.n"
        exit 1
    fi
}

# Get current version from project files
get_current_version() {
    local version=""
    
    # Try to find version in various files
    for file in "${VERSION_FILES[@]}"; do
        local filepath="$PROJECT_ROOT/$file"
        
        if [[ -f "$filepath" ]]; then
            case "$file" in
                "main.py")
                    version=$(grep -oP "__version__\s*=\s*['\"](\K[^'\"]*)" "$filepath" 2>/dev/null || echo "")
                    ;;
                "pyproject.toml")
                    version=$(grep -oP 'version\s*=\s*["\'](\K[^"\']*)' "$filepath" 2>/dev/null || echo "")
                    ;;
                "setup.py")
                    version=$(grep -oP "version\s*=\s*['\"](\K[^'\"]*)" "$filepath" 2>/dev/null || echo "")
                    ;;
            esac
            
            if [[ -n "$version" ]]; then
                log INFO "Found version $version in $file"
                break
            fi
        fi
    done
    
    # Try git tags as fallback
    if [[ -z "$version" ]]; then
        version=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "")
        if [[ -n "$version" ]]; then
            log INFO "Found version $version from git tags"
        fi
    fi
    
    # Default version if nothing found
    if [[ -z "$version" ]]; then
        version="0.1.0"
        log WARN "No version found, using default: $version"
    fi
    
    echo "$version"
}

# Calculate new version
calculate_new_version() {
    local increment_type="$1"
    local current_version="$2"
    
    parse_version "$current_version"
    
    local new_version=""
    
    case "$increment_type" in
        major)
            new_version="$((MAJOR + 1)).0.0"
            ;;
        minor)
            new_version="$MAJOR.$((MINOR + 1)).0"
            ;;
        patch)
            new_version="$MAJOR.$MINOR.$((PATCH + 1))"
            ;;
        prerelease)
            local prerelease_id="${PRERELEASE_ID:-alpha}"
            if [[ -n "$PRERELEASE_ID_CURRENT" && "$PRERELEASE_ID_CURRENT" == "$prerelease_id" ]]; then
                # Increment existing prerelease
                new_version="$MAJOR.$MINOR.$PATCH-$prerelease_id.$((PRERELEASE_NUM + 1))"
            else
                # Start new prerelease
                new_version="$MAJOR.$MINOR.$((PATCH + 1))-$prerelease_id.0"
            fi
            ;;
        *)
            log ERROR "Unknown increment type: $increment_type"
            log INFO "Valid types: major, minor, patch, prerelease"
            exit 1
            ;;
    esac
    
    echo "$new_version"
}

# Update version in file
update_version_in_file() {
    local file="$1"
    local old_version="$2"
    local new_version="$3"
    local dry_run="$4"
    
    local filepath="$PROJECT_ROOT/$file"
    
    if [[ ! -f "$filepath" ]]; then
        return 0
    fi
    
    local updated=false
    local temp_file=$(mktemp)
    
    case "$file" in
        "main.py")
            if grep -q "__version__" "$filepath"; then
                sed "s/__version__\s*=\s*['\"][^'\"]*['\"]/__version__ = \"$new_version\"/" "$filepath" > "$temp_file"
                updated=true
            fi
            ;;
        "pyproject.toml")
            if grep -q "version\s*=" "$filepath"; then
                sed "s/version\s*=\s*[\"'][^\"']*[\"']/version = \"$new_version\"/" "$filepath" > "$temp_file"
                updated=true
            fi
            ;;
        "setup.py")
            if grep -q "version\s*=" "$filepath"; then
                sed "s/version\s*=\s*[\"'][^\"']*[\"']/version=\"$new_version\"/" "$filepath" > "$temp_file"
                updated=true
            fi
            ;;
    esac
    
    if [[ "$updated" == "true" ]]; then
        if [[ "$dry_run" != "true" ]]; then
            mv "$temp_file" "$filepath"
            log INFO "Updated version in $file: $old_version → $new_version"
        else
            log INFO "Would update version in $file: $old_version → $new_version"
            rm -f "$temp_file"
        fi
    else
        rm -f "$temp_file"
    fi
}

# Update changelog
update_changelog() {
    local new_version="$1"
    local dry_run="$2"
    
    local changelog_file="$PROJECT_ROOT/CHANGELOG.md"
    
    if [[ ! -f "$changelog_file" ]]; then
        log WARN "CHANGELOG.md not found, skipping changelog update"
        return 0
    fi
    
    if [[ "$dry_run" == "true" ]]; then
        log INFO "Would add version $new_version to CHANGELOG.md"
        return 0
    fi
    
    # Create temporary file with new version entry
    local temp_file=$(mktemp)
    local today=$(date +%Y-%m-%d)
    
    # Read existing changelog and insert new version
    local found_unreleased=false
    
    while IFS= read -r line; do
        echo "$line" >> "$temp_file"
        
        # Insert new version after [Unreleased] section
        if [[ "$line" =~ ^\#\#[[:space:]]\[Unreleased\] ]] && [[ "$found_unreleased" == "false" ]]; then
            echo "" >> "$temp_file"
            echo "## [$new_version] - $today" >> "$temp_file"
            echo "" >> "$temp_file"
            echo "### Added" >> "$temp_file"
            echo "- Version $new_version release" >> "$temp_file"
            echo "" >> "$temp_file"
            found_unreleased=true
        fi
    done < "$changelog_file"
    
    # If no [Unreleased] section found, add new version at the top
    if [[ "$found_unreleased" == "false" ]]; then
        # Create new changelog with version entry
        cat > "$temp_file" << EOF
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [$new_version] - $today

### Added
- Version $new_version release

EOF
        # Append existing content (skip first few lines if they exist)
        if grep -q "# Changelog" "$changelog_file"; then
            tail -n +4 "$changelog_file" >> "$temp_file"
        else
            cat "$changelog_file" >> "$temp_file"
        fi
    fi
    
    mv "$temp_file" "$changelog_file"
    log INFO "Updated CHANGELOG.md with version $new_version"
}

# Commit changes
commit_changes() {
    local new_version="$1"
    local tag_version="$2"
    local dry_run="$3"
    
    if [[ "$dry_run" == "true" ]]; then
        log INFO "Would commit version bump to $new_version"
        if [[ "$tag_version" == "true" ]]; then
            log INFO "Would create git tag: ${VERSION_PREFIX:-v}$new_version"
        fi
        return 0
    fi
    
    # Stage modified files
    git add -A
    
    # Create commit
    git commit -m "chore: bump version to $new_version

- Update version numbers in project files
- Prepare for $new_version release

🤖 Generated by version bump script"
    
    log INFO "Created commit for version $new_version"
    
    # Create tag if requested
    if [[ "$tag_version" == "true" ]]; then
        local tag_name="${VERSION_PREFIX:-v}$new_version"
        git tag -a "$tag_name" -m "Release $new_version

🏷️ Auto-generated release tag"
        log INFO "Created git tag: $tag_name"
    fi
}

# Push changes
push_changes() {
    local push_tags="$1"
    local dry_run="$2"
    
    if [[ "$dry_run" == "true" ]]; then
        log INFO "Would push changes to remote repository"
        if [[ "$push_tags" == "true" ]]; then
            log INFO "Would push tags to remote repository"
        fi
        return 0
    fi
    
    # Push commits
    git push
    log INFO "Pushed commits to remote repository"
    
    # Push tags if requested
    if [[ "$push_tags" == "true" ]]; then
        git push --tags
        log INFO "Pushed tags to remote repository"
    fi
}

# Main execution
main() {
    cd "$PROJECT_ROOT"
    
    # Parse arguments
    local increment_type=""
    local dry_run=false
    local commit=false
    local tag=false
    local push=false
    local changelog=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            major|minor|patch|prerelease)
                increment_type="$1"
                ;;
            --dry-run)
                dry_run=true
                ;;
            --commit)
                commit=true
                ;;
            --tag)
                tag=true
                ;;
            --push)
                push=true
                ;;
            --changelog)
                changelog=true
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
    
    # Validate arguments
    if [[ -z "$increment_type" ]]; then
        log ERROR "Increment type is required"
        show_usage
        exit 1
    fi
    
    log INFO "Starting version bump: $increment_type"
    if [[ "$dry_run" == "true" ]]; then
        log INFO "Dry run mode - no changes will be made"
    fi
    
    # Get current version
    local current_version
    current_version=$(get_current_version)
    log INFO "Current version: $current_version"
    
    # Calculate new version
    local new_version
    new_version=$(calculate_new_version "$increment_type" "$current_version")
    log INFO "New version: $new_version"
    
    # Update version files
    for file in "${VERSION_FILES[@]}"; do
        update_version_in_file "$file" "$current_version" "$new_version" "$dry_run"
    done
    
    # Update changelog if requested
    if [[ "$changelog" == "true" ]]; then
        update_changelog "$new_version" "$dry_run"
    fi
    
    # Commit changes if requested
    if [[ "$commit" == "true" ]]; then
        commit_changes "$new_version" "$tag" "$dry_run"
    fi
    
    # Push changes if requested
    if [[ "$push" == "true" ]]; then
        if [[ "$commit" != "true" ]]; then
            log WARN "Cannot push without committing. Use --commit flag."
        else
            push_changes "$tag" "$dry_run"
        fi
    fi
    
    # Summary
    echo ""
    log INFO "Version bump completed successfully!"
    echo "  Previous: $current_version"
    echo "  New:      $new_version"
    echo ""
    
    if [[ "$dry_run" != "true" ]]; then
        echo "Next steps:"
        if [[ "$commit" != "true" ]]; then
            echo "  • Review changes and commit: git add -A && git commit"
        fi
        if [[ "$tag" != "true" ]]; then
            echo "  • Create release tag: git tag ${VERSION_PREFIX:-v}$new_version"
        fi
        if [[ "$push" != "true" ]]; then
            echo "  • Push to remote: git push && git push --tags"
        fi
        echo "  • Monitor release pipeline for automated deployment"
    fi
}

# Run main function with all arguments
main "$@"