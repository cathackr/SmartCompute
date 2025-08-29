# 🔐 GitHub Security Features Activation Guide

## 🚨 CRITICAL ACTION #2 - Manual GitHub Configuration Required

### Overview
This guide provides step-by-step instructions to activate essential GitHub security features for the SmartCompute repository. These features must be **manually activated** through the GitHub web interface.

---

## 📋 Required Actions

### 1. **Repository Settings → Security & analysis**

Navigate to: `https://github.com/YOUR_USERNAME/smartcompute/settings/security_analysis`

#### ✅ Dependency Graph
- **Status**: Should be auto-enabled for public repos
- **Action**: Verify it's enabled
- **Purpose**: Visualizes project dependencies

#### ✅ Dependabot Alerts
- **Action**: Click "Enable" button
- **Purpose**: Automated vulnerability alerts for dependencies
- **Configuration**: 
  ```
  ✅ Enable Dependabot alerts
  ✅ Enable Dependabot security updates
  ✅ Enable Dependabot version updates (optional)
  ```

#### ✅ Secret Scanning
- **Action**: Click "Enable" button  
- **Purpose**: Detects secrets in repository history
- **Note**: Will scan entire git history (including our cleaned version)

#### ✅ Code Scanning (CodeQL)
- **Action**: Click "Set up" → "Set up with GitHub Actions"
- **Purpose**: Static Application Security Testing (SAST)
- **Configuration**: Accept default CodeQL workflow

---

## 📁 Required Files (Already Created)

### Dependabot Configuration
File: `.github/dependabot.yml`
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "YOUR_USERNAME"
```

### CodeQL Workflow  
File: `.github/workflows/codeql.yml`
```yaml
name: "CodeQL Security Analysis"
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 2 AM

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write
    
    strategy:
      fail-fast: false
      matrix:
        language: [ 'python' ]
        
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}
        
    - name: Autobuild
      uses: github/codeql-action/autobuild@v3
      
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
```

---

## 🔧 Post-Activation Configuration

### 1. **Dependabot PR Reviews**
- Set up automatic reviews for security updates
- Configure merge criteria (require CI passing)

### 2. **Secret Scanning Custom Patterns**
Add custom patterns in Settings → Security → Secret scanning:
```regex
# API Keys
[Aa]pi[_-]?[Kk]ey[_-]?[=:]\s*['\"]?[a-zA-Z0-9]{32,}['\"]?

# JWT Tokens  
[Ee]y[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*

# Database URLs
[Pp]ostgres://[^\\s]*
[Mm]ysql://[^\\s]*

# Cloud Credentials
AKIA[0-9A-Z]{16}  # AWS Access Key
```

### 3. **Branch Protection Rules**
Navigate to Settings → Branches → Add rule:
```
Branch name pattern: main
☑️ Require a pull request before merging
☑️ Require status checks to pass before merging  
☑️ Require branches to be up to date before merging
☑️ Include administrators
☑️ Allow force pushes (temporarily for history rewrite)
```

---

## 📊 Verification Checklist

### After Activation, Verify:

#### ✅ Dependabot
```bash
# Check for dependabot.yml
ls -la .github/dependabot.yml

# Verify Python dependencies are scanned
pip-audit --desc --format=json
```

#### ✅ Secret Scanning
- Check Security tab → Secret scanning alerts
- Verify no secrets found in cleaned history
- Test with dummy secret in branch (then remove)

#### ✅ CodeQL
```bash
# Verify workflow exists
ls -la .github/workflows/codeql.yml

# Check workflow runs in Actions tab
# Verify Python code analysis completes
```

#### ✅ Alerts & Notifications
- Settings → Notifications → Security alerts
- Enable email notifications for:
  - Dependabot alerts
  - Secret scanning alerts  
  - Code scanning alerts

---

## 🚀 Testing Security Features

### 1. **Test Dependabot**
Create PR with outdated dependency:
```bash
# Create test branch
git checkout -b test-dependabot
echo "requests==2.25.0" >> requirements-test.txt
git add . && git commit -m "test: add outdated dependency"
git push origin test-dependabot
```

### 2. **Test Secret Scanning**
Create PR with dummy secret (remove after test):
```bash
# Create test branch  
git checkout -b test-secret
echo "api_key = 'sk-1234567890abcdef'" >> test_secret.py
git add . && git commit -m "test: add dummy secret"  
git push origin test-secret
# After test: delete branch and file
```

### 3. **Test CodeQL**
Trigger analysis by pushing to main or wait for scheduled run.

---

## 🔄 Maintenance Schedule

### Weekly
- Review Dependabot PRs
- Check security alerts
- Review CodeQL findings

### Monthly  
- Review secret scanning patterns
- Update branch protection rules
- Security audit of repository access

### Quarterly
- Review and update security policies
- Test incident response procedures
- Update security documentation

---

## 📞 Emergency Response

### If Secrets Are Found:
1. **Immediately revoke** the exposed credentials
2. **Generate new credentials** 
3. **Update all systems** using those credentials
4. **Document the incident**
5. **Review access logs** for unauthorized usage

### Critical Security Alert Process:
1. **Assess impact** and affected systems
2. **Notify stakeholders** immediately  
3. **Implement fixes** or temporary mitigations
4. **Document resolution** and lessons learned

---

## 🎯 Success Criteria

✅ All security features activated
✅ Zero critical vulnerabilities in dependencies  
✅ No secrets detected in repository
✅ CodeQL analysis passes without high-severity issues
✅ Automated security monitoring active
✅ Team notification system working
✅ Security incident response plan documented

---

## 📚 Additional Resources

- [GitHub Security Features Documentation](https://docs.github.com/en/code-security)
- [Dependabot Configuration Guide](https://docs.github.com/en/code-security/dependabot)  
- [CodeQL Query Documentation](https://codeql.github.com/)
- [Secret Scanning Patterns](https://docs.github.com/en/code-security/secret-scanning)

---

**🔴 REMINDER**: Complete this activation **IMMEDIATELY** before making the repository public or sharing with external collaborators.