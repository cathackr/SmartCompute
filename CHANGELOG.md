# Changelog

All notable changes to the SmartCompute project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2026-02-14

### Breaking Changes
- Complete project restructure from flat files to `src/smartcompute/` Python package
- Entry point changed from `python main.py` to `smartcompute` CLI or `python -m smartcompute`
- Docker entry point changed from `app.api.main:app` to `smartcompute.api.main:app`
- All imports now use `smartcompute.*` package namespace

### Added
- **Licensing system**: Offline RSA-based license validation with `@requires_tier()` decorators
  - `smartcompute activate <token>` to activate paid tiers
  - `smartcompute status` to check license and hardware ID
  - Hardware fingerprinting for machine-bound licenses
  - Tier hierarchy: starter (free) < enterprise < industrial
- **Unified CLI** with subcommands: `scan`, `monitor`, `report`, `activate`, `status`, `serve`, `enterprise`, `industrial`
- **pyproject.toml** with hatchling build backend and optional dependency groups:
  - `pip install smartcompute` (Starter, core only)
  - `pip install smartcompute[free]` (Dashboard + network discovery)
  - `pip install smartcompute[enterprise]` (Enterprise features, includes free)
  - `pip install smartcompute[industrial]` (Industrial features)
  - `pip install smartcompute[dev]` (Development tools)
- **LICENSE-COMMERCIAL** for enterprise/industrial modules
- **FastAPI application** at `smartcompute.api.main:app` with health, status, activate, and webhook endpoints
- Comprehensive test suite: `tests/unit/test_licensing.py`, `tests/unit/test_core_monitor.py`, `tests/unit/test_core_osi.py`, `tests/unit/test_cli.py`
- Test fixtures with RSA keypair generation for license testing

### Changed
- **Project structure**: Reorganized 60+ root Python files into categorized package:
  - `core/` — Starter features (monitor, OSI analysis, system resources, reports, config, dashboard)
  - `enterprise/` — Enterprise features organized into xdr/, siem/, ml/, mcp/, auth/, compliance/, ops/
  - `industrial/` — Industrial features organized into protocols/, scada/, compliance/, variables/
  - `licensing/` — License validation, decorators, hardware ID
  - `api/` — FastAPI endpoints
  - `payments/`, `network/`, `utils/` — Supporting modules
- Updated Dockerfile for `src/` layout and pyproject.toml-based installation
- Updated Makefile with new paths and `install-dev` target
- Updated CI workflow (`.github/workflows/ci.yml`) for Python 3.9-3.12 matrix with new package structure
- Updated `.gitignore` for new project structure
- **Pricing**: Updated from $15k/$25k to $200-750/year (Enterprise) and $5,000/3 years (Industrial)

### Removed
- Legacy flat file structure (files remain in root for reference during migration)
- Direct `requirements.txt` usage for installation (now use pyproject.toml)

## [2.0.3] - 2026-02-09

### Marketing & Documentation
- **ENHANCED**: README improvements preserving bilingual structure
  - Added badges at top (Python 3.8+, Docker, MIT License, Grafana 10.1)
  - Added link to English version (README_EN.md)
  - Added "Demo Rápido (30 segundos)" section highlighting smartcompute_express.py
  - Integrated 3 existing screenshots:
    - Grafana dashboard in Description section
    - Docker deployment stack in Architecture section
    - Benchmark results in Benefits section
  - Maintained Spanish-primary, bilingual documentation structure

### Added
- `QUICKSTART.md` - 30-second and 2-minute quick start guides
- `MARKETING_POSTS.md` - Ready-to-use posts for Reddit, LinkedIn, Twitter, HN, Dev.to
- `GOOD_FIRST_ISSUES.md` - 22 beginner-friendly contribution opportunities
- `tools/capture_screenshots.py` - Automated screenshot capture tool
- GitHub issue templates (bug report, feature request)

### Changed
- Updated package.json description to highlight observability features
- README now showcases Express demo prominently (no hardware required)
- README emphasizes Docker Compose quickstart (2 minutes)
- Documentation now targets self-hosted/DevOps audience in addition to industrial

### Documentation
- Added detailed API documentation structure
- Added security configuration guide
- Added Docker build instructions
- Added testing guide
- Added contribution guidelines

## [2.0.2] - 2026-02-09

### Security - CRITICAL
- **CRITICAL**: Removed hardcoded admin password `'***REMOVED***'` from `smartcompute_central_bridge_server.py`
- **CRITICAL**: Removed hardcoded operator password `'***REMOVED***'` from central bridge server
- **CRITICAL**: Removed hardcoded Flask SECRET_KEY from central bridge server
- **CRITICAL**: Removed weak default encryption password from `industrial_reports_exporter.py`
- **CRITICAL**: Removed hardcoded encryption salt from industrial reports

### Changed
- Admin/operator users now ONLY created if environment variables are set (`SMARTCOMPUTE_ADMIN_PASSWORD`, `SMARTCOMPUTE_OPERATOR_PASSWORD`)
- Flask SECRET_KEY now loaded from `SMARTCOMPUTE_FLASK_SECRET_KEY` or generated randomly
- Industrial reports encryption now REQUIRES `REPORTS_ENCRYPTION_PASSWORD` and `REPORTS_ENCRYPTION_SALT`
- Added clear warning messages when security-critical environment variables are not configured
- Updated `.env.example` with new required variables and generation instructions

### Added
- Automatic generation of Flask SECRET_KEY if not configured (with warning about non-persistence)
- Automatic generation of encryption salt with instructions to save it
- Comprehensive logging when security configurations are missing or insecure

## [2.0.1] - 2026-02-09

### Security
- **CRITICAL**: Moved hardcoded API credentials to environment variables
- Created secure configuration loader (`secure_config_loader.py`) with environment variable expansion
- Added `.env.example` and `client_config.json.example` templates for secure setup
- Protected credentials from accidental exposure in version control

### Fixed
- Added timeout parameter (5s) to all subprocess calls in `generate_html_reports.py` to prevent indefinite hangs
- Replaced generic exception handling with specific exception types in `smartcompute_industrial_gui.py`
  - Now catches: `tk.TclError`, `AttributeError`, `OSError`, `json.JSONDecodeError`, `PermissionError`, `TypeError`
  - Added detailed traceback logging for better debugging
- Converted blocking I/O to async operations in `smartcompute_hrm_proto/node/smart_detector.js`
  - Migrated `fs.readFileSync` → `fsPromises.readFile`
  - Migrated `fs.writeFileSync` → `fsPromises.writeFile`
  - Migrated `fs.existsSync` → `fsPromises.access`
  - Migrated `fs.mkdirSync` → `fsPromises.mkdir`
- Added comprehensive error handling to `quick_migration.sh` deployment script
  - Enabled bash strict mode (`set -e`, `set -u`, `set -o pipefail`)
  - Added logging function with timestamps
  - Added error_exit function for controlled failure
  - Added trap for automatic error capture
  - Added pre-flight checks (Python3 installation, file existence, permissions)

### Changed
- Client configuration now uses `${SMARTCOMPUTE_API_KEY}` placeholder instead of hardcoded values
- Improved error messages to be more descriptive without exposing sensitive information

## [2.0.0] - Previous Release

### Added
- Comprehensive security framework with TLS/mTLS support
- Mutual authentication system for service-to-service communication
- Advanced rate limiting with multiple strategies (token bucket, sliding window, adaptive)
- Circuit breaker pattern implementation for external API calls
- Automated release pipeline with multi-platform binary generation
- GPG signature verification for release artifacts
- Production-ready deployment scripts with security validation
- Complete Docker Compose setup with network isolation
- NGINX configuration with TLS termination and security headers
- Monitoring and observability integration

### Security
- End-to-end TLS encryption for all connections
- X.509 certificate management and validation
- JWT-based authentication with configurable permissions
- Rate limiting to prevent DoS attacks
- Circuit breakers for fault tolerance
- Security headers and Content Security Policy
- Defense in depth architecture

## Release Process

This project follows semantic versioning:

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Pre-release versions may be tagged with suffixes:
- **alpha** for early development releases
- **beta** for feature-complete releases in testing
- **rc** for release candidates

## Security Policy

For security vulnerabilities, please see [SECURITY.md](SECURITY.md) for reporting procedures.

---

*This changelog is automatically updated during the release process.*