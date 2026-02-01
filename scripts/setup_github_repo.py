import os
from pathlib import Path

def create_github_repo_structure(base_path):
    print("Setting up Phase 1 GitHub Repository")
    print("========================================")

    # Create fresh repository structure
    print("Creating directory structure...")
    (base_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (base_path / "docs").mkdir(parents=True, exist_ok=True)
    (base_path / "scripts").mkdir(parents=True, exist_ok=True)
    (base_path / "python").mkdir(parents=True, exist_ok=True)
    (base_path / "go").mkdir(parents=True, exist_ok=True)
    (base_path / "rust").mkdir(parents=True, exist_ok=True)
    (base_path / "csharp").mkdir(parents=True, exist_ok=True)

    print("Creating essential files...")

    # Create main README
    readme_content = """# [Title will be added after sanitization]
# See docs/ for complete README
"""
    (base_path / "README.md").write_text(readme_content)

    # Create clean .gitignore
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Go
go.sum
go.mod
*.exe
*.exe~
*.dll
*.so
*.dylib

# Rust
target/
**/*.rs.bk

# C# 
bin/
obj/
*.user
*.suo
*.cache
*.docstates

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets
.env
*.key
*.pem
*.crt

# Large files
*.log
*.db
*.sqlite
"""
    (base_path / ".gitignore").write_text(gitignore_content)

    # Create MIT License (clean)
    license_content = """MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    (base_path / "LICENSE").write_text(license_content)

    # Create security policy
    security_md_content = """# Security Policy

## Supported Versions
These are portfolio demonstration artifacts - no versions are actively supported.

## Reporting a Vulnerability
If you believe you have found a security vulnerability in this demonstration code:
1. Do not disclose it publicly
2. Consider that this is not production code
3. These tools are not intended for real security use
4. Vulnerabilities in demonstration code do not pose real-world risk

## Security Considerations
- These tools use synthetic data only
- No real credentials or secrets are included
- Tools are intentionally simple for demonstration
- Not intended for production security monitoring
"""
    (base_path / "SECURITY.md").write_text(security_md_content)

    # Create contribution guidelines
    contributing_md_content = """# Contributing Guidelines

## About This Repository
This repository contains **portfolio demonstration artifacts**. The code is intentionally frozen to serve as examples of cybersecurity skills.

## What Contributions Are Welcome
- Documentation improvements
- Typo fixes
- Test case additions (with synthetic data)
- Clarification of examples
- Non-functional improvements

## What Contributions Are NOT Accepted
- Changes to core implementations (these are demonstration artifacts)
- Feature additions (tools are intentionally minimal)
- Productionization suggestions
- Dependency additions

## Process
1. Fork the repository
2. Create a branch for your changes
3. Submit a pull request with clear description
4. Ensure all tests pass
5. Maintain the "demonstration only" nature

## Important
All contributions must maintain:
- No PII/PHI in code or data
- Synthetic test data only
- Clear "demonstration" context
- Original work only
"""
    (base_path / "CONTRIBUTING.md").write_text(contributing_md_content)

    print("Repository structure created")
    print("")
    print("Next steps:")
    print("1. Run sanitization script: python sanitize_content.py")
    print("2. Validate all content: ./scripts/pre_github_validation.py")
    print("3. Initialize git: git init")
    print("4. Add all files: git add .")
    print("5. Commit: git commit -m 'Phase 1: 15 cybersecurity tools'")
    print("6. Create GitHub repository")
    print("7. Push: git push origin main")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    github_repo_root = script_dir.parent
    create_github_repo_structure(github_repo_root)