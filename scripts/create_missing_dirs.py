# scripts/create_missing_dirs.py
import os
from pathlib import Path

def create_missing_dirs(base_path):
    print(f"Ensuring 'sample_data' and 'tests' directories exist for all tools in {base_path}...")
    
    tools_checked = 0
    for lang_dir_name in ['python', 'go', 'rust', 'csharp']:
        lang_path = os.path.join(base_path, lang_dir_name)
        if os.path.isdir(lang_path):
            for tool_dir_name in os.listdir(lang_path):
                tool_path = os.path.join(lang_path, tool_dir_name)
                if os.path.isdir(tool_path):
                    tools_checked += 1
                    
                    sample_data_path = os.path.join(tool_path, 'sample_data')
                    if not os.path.exists(sample_data_path):
                        os.makedirs(sample_data_path)
                        print(f"  Created: {sample_data_path}")
                    
                    tests_path = os.path.join(tool_path, 'tests')
                    if not os.path.exists(tests_path):
                        os.makedirs(tests_path)
                        print(f"  Created: {tests_path}")
    
    print(f"Checked {tools_checked} tools. Missing directories created.")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    github_repo_root = script_dir.parent # This assumes script is in github_repo/scripts
    create_missing_dirs(github_repo_root)
