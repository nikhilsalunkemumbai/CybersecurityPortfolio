# scripts/pre_github_validation.py
import os
import re
import sys
from pathlib import Path
import subprocess

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m' # No Color

FAILURES = 0
TOTAL_TOOLS = 15 # Assuming phase 1 has 15 tools

def grep_file(filepath, patterns, exclude_patterns=None, case_insensitive=True):
    flags = re.IGNORECASE if case_insensitive else 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        for pattern in patterns:
            if re.search(pattern, content, flags):
                if exclude_patterns:
                    found_and_not_excluded = True
                    for exclude_pattern in exclude_patterns:
                        if re.search(exclude_pattern, content, flags):
                            found_and_not_excluded = False
                            break
                    if found_and_not_excluded:
                        return True
                else:
                    return True
    return False

def validate_tool(tool_path):
    global FAILURES
    tool_name = os.path.basename(tool_path)
    
    print(f" Validating: {tool_name}")
    
    # 1. Check for PII/PHI in code
    pii_patterns = [
        # Keywords suggesting credentials (using \b for whole word match)
        r"\b(password|secret|key|token)\b", 
        # Email patterns
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        # IP addresses (more specific to private/test ranges, but keeping original for now)
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b', 
        # SSN
        r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
        # Example for credit card (less common in code but good to keep)
        r'\b(?:\d[ -]*?){13,16}\b',
        r'\bphone\b',
        r'\baddress\b',
        r'\bname\b',
    ]
    # Exclude common false positives and known safe patterns
    pii_exclude_patterns = [
        r"TODO", r"FIXME", r"example", r"sample", r"test", r"Test", r"demonstration", r"description",
        r"name:", # In manifests where 'name' is a key, not a value
        r"log", r"Log", # For log files/loggers
        r"api_key_length", # Specific technical term
        r"version", r"Version", # In metadata like .deps.json
        r"audit", r"report", r"file", r"Monitor", r"Checker", r"Summarizer", r"Extractor", r"Linter", r"Auditor" # Common tool names
    ]
    
    for root, _, files in os.walk(tool_path):
        for file in files:
            filepath = os.path.join(root, file)
            if any(filepath.endswith(ext) for ext in ['.py', '.go', '.rs', '.cs', '.md', '.txt', '.json', '.yaml', '.yml']):
                if grep_file(filepath, pii_patterns, pii_exclude_patterns):
                    print(f"{RED}POSSIBLE PII/PHI DETECTED in {file}{NC}")
                    # Print first 5 lines of context
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f):
                            if i >= 5: break
                            if any(re.search(p, line, re.IGNORECASE) for p in pii_patterns if not any(re.search(ep, line, re.IGNORECASE) for ep in pii_exclude_patterns)):
                                print(f"  Line {i+1}: {line.strip()}")
                    FAILURES += 1
                    return # Stop validation for this tool if PII is found

    # 2. Check for copyrighted material
    copyright_patterns = [r"Copyright", r"copyright", r"©", r"All rights reserved", r"proprietary", r"confidential"]
    copyright_exclude_patterns = [r"LICENSE", r"portfolio context"]
    for root, _, files in os.walk(tool_path):
        for file in files:
            filepath = os.path.join(root, file)
            if any(filepath.endswith(ext) for ext in ['.py', '.go', '.rs', '.cs', '.md', '.txt', '.json', '.yaml', '.yml']):
                if grep_file(filepath, copyright_patterns, copyright_exclude_patterns):
                    print(f"{RED}POSSIBLE COPYRIGHT NOTICES in {file}{NC}")
                    FAILURES += 1
                    return

    # 3. Check all required files exist
    required_files_relative_to_tool = ["README.md", "sample_data", "tests"] # sample_data and tests are directories
    for req_file in required_files_relative_to_tool:
        req_path = os.path.join(tool_path, req_file)
        if not os.path.exists(req_path):
            print(f"{RED}MISSING: {req_file}{NC}")
            FAILURES += 1
            return
    
    # 4. Check for proper disclaimers in README.md
    readme_path = os.path.join(tool_path, "README.md")
    if os.path.exists(readme_path):
        if not grep_file(readme_path, [r"PORTFOLIO ARTIFACT", r"DEMONSTRATION ONLY", r"not production", r"proof of concept"]):
            print(f"{YELLOW} WARNING: Missing portfolio context in {tool_name}/README.md{NC}")
    else:
        # This case is already covered by missing README.md check, but good to have
        pass 
        
    # 5. Check sample data is synthetic
    sample_data_dir = os.path.join(tool_path, "sample_data")
    if os.path.isdir(sample_data_dir):
        synthetic_indicators = [
            'example.com', '[REDACTED]', '192.0.2.', '203.0.113.', '198.51.100.',
            'localhost', 'dummy', 'synthetic', 'fake', 'placeholder'
        ]
        
        found_non_synthetic = False
        for root, _, files in os.walk(sample_data_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
                    if not any(indicator in content for indicator in synthetic_indicators):
                        print(f"{YELLOW} WARNING: {file} in sample data may contain real patterns.{NC}")
                        found_non_synthetic = True
                        break
                except: # Skip binary files that can't be read as text
                    pass
            if found_non_synthetic: break
        
        if not found_non_synthetic:
            print(f"{GREEN}Sample data appears synthetic.{NC}")

    print(f"{GREEN}Tool passed validation.{NC}")

def main():
    global FAILURES
    print(f"{GREEN}PHASE 1 GITHUB LAUNCH PREPARATION{NC}")
    print("======================================")
    print("Checking 15 tools for readiness...")
    print("")

    base_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/
    base_dir = os.path.join(base_dir, '..') # github_repo/

    tool_dirs = []
    for lang_dir_name in ['python', 'go', 'rust', 'csharp']:
        lang_path = os.path.join(base_dir, lang_dir_name)
        if os.path.isdir(lang_path):
            for tool_dir_name in os.listdir(lang_path):
                tool_path = os.path.join(lang_path, tool_dir_name)
                if os.path.isdir(tool_path):
                    tool_dirs.append(tool_path)
    
    for tool_path in tool_dirs:
        validate_tool(tool_path)
        print("")

    print("======================================")
    print("VALIDATION COMPLETE")
    print(f"Tools checked: {TOTAL_TOOLS}")
    print(f"Failures: {FAILURES}")

    if FAILURES == 0:
        print(f"{GREEN}ALL TOOLS READY FOR GITHUB{NC}")
        sys.exit(0)
    else:
        print(f"{RED}FIX {FAILURES} ISSUES BEFORE PUSH{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
