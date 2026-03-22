"""Verify project setup"""

import sys
from pathlib import Path

def check_directory_structure():
    """Check if all required directories exist"""
    required_dirs = [
        "app",
        "app/api",
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/services",
        "migrations",
        "migrations/versions",
        "tests",
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print("❌ Missing directories:")
        for d in missing:
            print(f"  - {d}")
        return False
    
    print("✅ All required directories exist")
    return True


def check_required_files():
    """Check if all required files exist"""
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/config.py",
        "app/core/logging.py",
        "app/db/session.py",
        "app/db/redis.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        ".env.example",
        ".gitignore",
        "alembic.ini",
        "pytest.ini",
        "README.md",
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print("✅ All required files exist")
    return True


def main():
    """Run all checks"""
    print("Verifying project setup...\n")
    
    checks = [
        check_directory_structure(),
        check_required_files(),
    ]
    
    if all(checks):
        print("\n✅ Project setup is complete!")
        return 0
    else:
        print("\n❌ Project setup is incomplete")
        return 1


if __name__ == "__main__":
    sys.exit(main())
