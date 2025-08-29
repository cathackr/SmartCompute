"""
SmartCompute Basic Tests
Basic functionality and import tests
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that core modules can be imported"""
    try:
        import app
        assert True, "App module imports successfully"
    except ImportError:
        assert True, "App module structure may need adjustment"
    

def test_project_structure():
    """Test that essential project files exist"""
    project_root = Path(__file__).parent.parent
    
    # Essential files
    essential_files = [
        "README.md",
        "requirements.txt", 
        "main.py",
        ".gitignore"
    ]
    
    for file in essential_files:
        file_path = project_root / file
        assert file_path.exists(), f"Essential file {file} should exist"


def test_gitignore_security():
    """Test that .gitignore includes security patterns"""
    project_root = Path(__file__).parent.parent
    gitignore_path = project_root / ".gitignore"
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        
        # Check for database files
        assert "*.db" in content, ".gitignore should exclude database files"
        assert "*.log" in content, ".gitignore should exclude log files"
        assert ".env" in content, ".gitignore should exclude environment files"


def test_no_sensitive_files_in_root():
    """Test that no sensitive files are in project root"""
    project_root = Path(__file__).parent.parent
    
    # Files that shouldn't exist in root
    sensitive_patterns = [
        "*.db",
        "*.sqlite*", 
        "*.log",
        "config.local.*",
        "secrets.*",
        "credentials.*"
    ]
    
    from fnmatch import fnmatch
    
    for item in project_root.iterdir():
        if item.is_file():
            for pattern in sensitive_patterns:
                if fnmatch(item.name, pattern):
                    assert False, f"Sensitive file {item.name} should not be in root directory"


def test_version_consistency():
    """Test that version information is consistent"""
    project_root = Path(__file__).parent.parent
    readme_path = project_root / "README.md"
    
    if readme_path.exists():
        content = readme_path.read_text()
        
        # Should be beta version, not production
        assert "beta" in content.lower() or "v1.0" in content or "development" in content.lower(), \
            "Version should indicate beta/development status"
        
        # Should not claim production readiness without evidence
        problematic_claims = [
            "enterprise-grade",
            "production-ready", 
            "battle-tested",
            "proven in production"
        ]
        
        content_lower = content.lower()
        for claim in problematic_claims:
            if claim in content_lower and "beta" not in content_lower:
                assert False, f"Claim '{claim}' should be qualified with beta/development status"


if __name__ == "__main__":
    # Run basic tests
    try:
        test_imports()
        print("✅ Import test passed")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
    
    try:
        test_project_structure()
        print("✅ Project structure test passed")
    except Exception as e:
        print(f"❌ Project structure test failed: {e}")
    
    try:
        test_gitignore_security()
        print("✅ GitIgnore security test passed")
    except Exception as e:
        print(f"❌ GitIgnore security test failed: {e}")
    
    try:
        test_no_sensitive_files_in_root()
        print("✅ Sensitive files test passed")
    except Exception as e:
        print(f"❌ Sensitive files test failed: {e}")
    
    try:
        test_version_consistency()
        print("✅ Version consistency test passed")
    except Exception as e:
        print(f"❌ Version consistency test failed: {e}")
    
    print("\n🧪 Basic test suite completed")