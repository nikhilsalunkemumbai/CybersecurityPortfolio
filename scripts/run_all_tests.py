# scripts/run_all_tests.py
import os
import subprocess
import sys

RED = '\033[0;31m'
GREEN = '\033[0;32m'
NC = '\033[0m' # No Color

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr, 0
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode
    except FileNotFoundError:
        return "", f"Error: Command not found or executable not in PATH: {command[0]}\n", 1
        
def run_python_tests(base_dir):
    print(f"\n{GREEN}Python Tools Testing{NC}")
    print("----------------------")
    failures = 0
    total = 0
    python_dir = os.path.join(base_dir, 'python')
    if not os.path.exists(python_dir):
        print(f"  {RED}Skipping Python: Directory not found ({python_dir}){NC}")
        return 0, 0, failures

    for tool_dir_name in os.listdir(python_dir):
        tool_path = os.path.join(python_dir, tool_dir_name)
        if os.path.isdir(tool_path) and os.path.exists(os.path.join(tool_path, 'tests')):
            print(f"Testing: {tool_dir_name}")
            total += 1
            
            # Install requirements if any
            reqs_path = os.path.join(tool_path, 'requirements.txt')
            if os.path.exists(reqs_path):
                stdout, stderr, exit_code = run_command([sys.executable, '-m', 'pip', 'install', '-r', reqs_path], cwd=tool_path)
                if exit_code != 0:
                    print(f"  {RED}Failed to install requirements for {tool_dir_name}:{NC}\n{stderr}")
                    failures += 1
                    continue

            # Run pytest
            stdout, stderr, exit_code = run_command([sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'], cwd=tool_path)
            if exit_code == 0:
                print(f"  {GREEN}PASS{NC}")
            else:
                print(f"  {RED}FAIL{NC}\n{stdout}{stderr}")
                failures += 1
    return total, total - failures, failures

def run_go_tests(base_dir):
    print(f"\n{GREEN}Go Tools Testing{NC}")
    print("------------------")
    failures = 0
    total = 0
    go_dir = os.path.join(base_dir, 'go')
    if not os.path.exists(go_dir):
        print(f"  {RED}Skipping Go: Directory not found ({go_dir}){NC}")
        return 0, 0, failures

    for tool_dir_name in os.listdir(go_dir):
        tool_path = os.path.join(go_dir, tool_dir_name)
        if os.path.isdir(tool_path) and os.path.exists(os.path.join(tool_path, 'go.mod')):
            print(f"Testing: {tool_dir_name}")
            total += 1
            stdout, stderr, exit_code = run_command(['go', 'test', './...'], cwd=tool_path)
            if exit_code == 0:
                print(f"  {GREEN}PASS{NC}")
            else:
                print(f"  {RED}FAIL{NC}\n{stdout}{stderr}")
                failures += 1
    return total, total - failures, failures

def run_rust_tests(base_dir):
    print(f"\n{GREEN}Rust Tools Testing{NC}")
    print("-------------------")
    failures = 0
    total = 0
    rust_dir = os.path.join(base_dir, 'rust')
    if not os.path.exists(rust_dir):
        print(f"  {RED}Skipping Rust: Directory not found ({rust_dir}){NC}")
        return 0, 0, failures

    for tool_dir_name in os.listdir(rust_dir):
        tool_path = os.path.join(rust_dir, tool_dir_name)
        if os.path.isdir(tool_path) and os.path.exists(os.path.join(tool_path, 'Cargo.toml')):
            print(f"Testing: {tool_dir_name}")
            total += 1
            stdout, stderr, exit_code = run_command(['cargo', 'test', '--quiet'], cwd=tool_path)
            if exit_code == 0:
                print(f"  {GREEN}PASS{NC}")
            else:
                print(f"  {RED}FAIL{NC}\n{stdout}{stderr}")
                failures += 1
    return total, total - failures, failures

def run_csharp_tests(base_dir):
    print(f"\n{GREEN}C# Tools Testing{NC}")
    print("------------------")
    failures = 0
    total = 0
    csharp_dir = os.path.join(base_dir, 'csharp')
    if not os.path.exists(csharp_dir):
        print(f"  {RED}Skipping C#: Directory not found ({csharp_dir}){NC}")
        return 0, 0, failures

    for tool_dir_name in os.listdir(csharp_dir):
        tool_path = os.path.join(csharp_dir, tool_dir_name)
        # Check for .csproj file directly within the tool_path
        if os.path.isdir(tool_path) and any(f.endswith('.csproj') for f in os.listdir(tool_path)):
            print(f"Testing: {tool_dir_name}")
            total += 1
            
            # Restore, Build, Test C# project
            # dotnet restore
            stdout, stderr, exit_code = run_command(['dotnet', 'restore'], cwd=tool_path)
            if exit_code != 0:
                print(f"  {RED}Restore failed for {tool_dir_name}:{NC}\n{stderr}")
                failures += 1
                continue
            
            # dotnet build
            stdout, stderr, exit_code = run_command(['dotnet', 'build', '--no-restore'], cwd=tool_path)
            if exit_code != 0:
                print(f"  {RED}Build failed for {tool_dir_name}:{NC}\n{stderr}")
                failures += 1
                continue
            
            # dotnet test
            # Note: --no-build assumes successful build in previous step.
            # Using --verbosity quiet for cleaner output, similar to original shell script intent
            stdout, stderr, exit_code = run_command(['dotnet', 'test', '--no-build', '--verbosity', 'quiet'], cwd=tool_path)
            if exit_code == 0:
                print(f"  {GREEN}PASS{NC}")
            else:
                print(f"  {RED}FAIL{NC}\n{stdout}{stderr}")
                failures += 1
    return total, total - failures, failures

def main():
    print(f"{GREEN}RUNNING ALL 15 TOOL TESTS{NC}")
    print("==============================\n")

    base_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/ 
    base_dir = os.path.join(base_dir, '..') # github_repo/ 

    overall_failures = 0
    overall_total = 0
    
    # Run Python tests
    total, passed, failures = run_python_tests(base_dir)
    overall_total += total
    overall_failures += failures

    # Run Go tests
    total, passed, failures = run_go_tests(base_dir)
    overall_total += total
    overall_failures += failures
    
    # Run Rust tests
    total, passed, failures = run_rust_tests(base_dir)
    overall_total += total
    overall_failures += failures
    
    # Run C# tests
    total, passed, failures = run_csharp_tests(base_dir)
    overall_total += total
    overall_failures += failures

    print(f"\n{GREEN}=============================={NC}")
    print(f"{GREEN} TEST SUMMARY{NC}")
    print(f"Total tools tested: {overall_total}/15")
    print(f"Failures: {overall_failures}")

    if overall_failures == 0:
        print(f"{GREEN}ALL TESTS PASSED{NC}")
        sys.exit(0)
    else:
        print(f"{RED}{overall_failures} TESTS FAILED{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
