"""
Setup Verification Script

Checks that all dependencies and configurations are properly set up.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check Python version is 3.10+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check required packages are installed."""
    required_packages = [
        "autogen",
        "requests",
        "dotenv",
        "yaml"
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "yaml":
                __import__("yaml")
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    return len(missing) == 0

def check_env_file():
    """Check .env file exists and has required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found. Copy .env.example to .env and add your API keys.")
        return False
    
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_") or value.endswith("_here"):
            print(f"❌ {var} not set or using placeholder value")
            missing.append(var)
        else:
            # Show partial key for verification
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {var} is set ({masked})")
    
    return len(missing) == 0

def check_project_structure():
    """Check project structure is correct."""
    required_dirs = [
        "agents",
        "orchestration",
        "evaluation",
        "config",
        "utils",
        "tests"
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "config/agent_configs.yaml",
        "config/prompts.yaml"
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Directory {dir_name}/ exists")
        else:
            print(f"❌ Directory {dir_name}/ missing")
            all_good = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ File {file_name} exists")
        else:
            print(f"❌ File {file_name} missing")
            all_good = False
    
    return all_good

def main():
    """Run all checks."""
    print("="*60)
    print("Research Assistant Setup Verification")
    print("="*60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_file),
        ("Project Structure", check_project_structure)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        result = check_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to use the Research Assistant.")
        print("\nTo get started:")
        print("  python main.py \"Your research query here\"")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
