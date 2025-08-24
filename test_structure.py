#!/usr/bin/env python3
"""
Test script to verify Elixir AI package structure
This script checks that all files are in place and can be imported
"""

import os
import sys
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        "elixirai/__init__.py",
        "elixirai/core/__init__.py",
        "elixirai/core/config.py",
        "elixirai/core/utils.py",
        "elixirai/core/indexer.py",
        "elixirai/core/search.py",
        "elixirai/core/summarizer.py",
        "elixirai/core/graph.py",
        "elixirai/core/suggest.py",
        "elixirai/core/github.py",
        "elixirai/cli.py",
        "ui.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "LICENSE",
        ".gitignore",
        ".github/workflows/ci.yml",
        "tests/__init__.py",
        "tests/test_basic.py",
        "demo.py",
        "setup.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"[ERROR] Missing files: {missing_files}")
        return False
    else:
        print("[OK] All required files present")
        return True

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("\n🐍 Testing Python syntax...")
    
    python_files = [
        "elixirai/__init__.py",
        "elixirai/core/__init__.py",
        "elixirai/core/config.py",
        "elixirai/core/utils.py",
        "elixirai/core/indexer.py",
        "elixirai/core/search.py",
        "elixirai/core/summarizer.py",
        "elixirai/core/graph.py",
        "elixirai/core/suggest.py",
        "elixirai/core/github.py",
        "elixirai/cli.py",
        "ui.py",
        "demo.py",
        "setup.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
    
    if syntax_errors:
        print(f"[ERROR] Syntax errors found: {syntax_errors}")
        return False
    else:
        print("[OK] All Python files have valid syntax")
        return True

def test_config_values():
    """Test that configuration constants are properly defined"""
    print("\nTesting configuration...")
    
    try:
        # Add current directory to path for import
        sys.path.insert(0, '.')
        
        # Import config module
        from elixirai.core import config
        
        # Check that constants exist and have reasonable values
        assert hasattr(config, 'CODE_EXTS')
        assert hasattr(config, 'TEXT_EXTS')
        assert hasattr(config, 'IGNORE_DIRS')
        assert hasattr(config, 'MAX_FILE_BYTES')
        assert hasattr(config, 'CHUNK_LINES')
        assert hasattr(config, 'CHUNK_OVERLAP')
        
        assert len(config.CODE_EXTS) > 0
        assert len(config.TEXT_EXTS) > 0
        assert config.MAX_FILE_BYTES > 0
        assert config.CHUNK_LINES > 0
        assert config.CHUNK_OVERLAP >= 0
        
        print("[OK] Configuration constants properly defined")
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuration test failed: {e}")
        return False

def test_package_imports():
    """Test that package imports work (without external dependencies)"""
    print("\nTesting package imports...")
    
    try:
        # Test basic imports
        from elixirai.core import config
        print("[OK] Core config imported successfully")
        
        # Test that we can access the package
        assert hasattr(config, 'CODE_EXTS')
        print("[OK] Package attributes accessible")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Package import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Elixir AI Package Structure Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_config_values,
        test_package_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[ERROR] Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[OK] All tests passed! Package structure is correct.")
        return True
    else:
        print("[ERROR] Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
