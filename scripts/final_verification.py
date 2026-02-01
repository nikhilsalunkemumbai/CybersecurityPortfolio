# scripts/final_verification.py
import os
import sys
import subprocess
from pathlib import Path

RED = '\033[0;31m'
GREEN = '\033[0;32m'
NC = '\033[0m' # No Color

def run_script(script_path, cwd=None):
    try:
        command = [sys.executable, script_path]
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False) # check=False to get exit code
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except FileNotFoundError:
        print(f"{RED}Error: Script not found at {script_path}{NC}", file=sys.stderr)
        return 1

def main():
    print("FINAL GITHUB PUSH VERIFICATION")
    print("==================================")

    base_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/ 
    github_repo_root = os.path.join(base_dir, '..') # github_repo/

    overall_status = 0 # 0 for success, 1 for failure

    # 1. CONTENT VALIDATION (using pre_github_validation.py)
    print("\n1. Running pre-GitHub validation...")
    if run_script(os.path.join(base_dir, 'pre_github_validation.py'), cwd=github_repo_root) != 0:
        overall_status = 1
    else:
        print(f"  Pre-GitHub validation passed")

    # 2. Checking repository structure (basic required files)
    print("\n2. Checking repository structure...")
    required_repo_files = ["README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md"]
    for file in required_repo_files:
        if os.path.exists(os.path.join(github_repo_root, file)):
            print(f"  {file} present")
        else:
            print(f"  {RED}Missing: {file}{NC}")
            overall_status = 1

    # 3. Running all tests (using run_all_tests.py)
    print("\n3. Running all tests...")
    if run_script(os.path.join(base_dir, 'run_all_tests.py'), cwd=github_repo_root) != 0:
        overall_status = 1
    else:
        print(f"  All tests passed")

    print(f"\n==================================")
    if overall_status == 0:
        print(f"REPOSITORY READY FOR GITHUB")
        print("\nNext steps:")
        print("1. git init")
        print("2. git add .")
        print("3. git commit -m 'Phase 1: 15 cybersecurity tools'")
        print("4. Create GitHub repository on GitHub.com (e.g., 'cybersecurity-tools-phase1')")
        print("5. git remote add origin https://github.com/YOUR_USERNAME/cybersecurity-tools-phase1.git")
        print("6. git branch -M main")
        print("7. git push -u origin main")
    else:
        print(f"{RED}❌ REPOSITORY HAS FAILURES. PLEASE FIX BEFORE PUSH.{NC}")
    
    sys.exit(overall_status)

if __name__ == "__main__":
    main()
