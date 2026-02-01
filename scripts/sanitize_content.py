# sanitize_content.py
"""
Clean all content before GitHub push
"""
import re
from pathlib import Path

def sanitize_file(filepath):
    """Remove PII/PHI patterns from file"""
    patterns_to_remove = [
        # Email patterns (replace with [REDACTED])
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # IP addresses (replace with [REDACTED] - TEST-NET-1)
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        
        # Phone numbers
        r'\b(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        
        # Credit card numbers
        r'\b(?:\d[ -]*?){13,16}\b',
        
        # SSN
        r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
        
        # Specific names (common test names)
        r'\b(?:[REDACTED]|[REDACTED]|[REDACTED]|[REDACTED]|[REDACTED])\b',
    ]
    
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Replace patterns
    cleaned = content
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '[REDACTED]', cleaned, flags=re.IGNORECASE)
    
    # Log if changes were made
    if cleaned != content:
        print(f"Sanitized: {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
    
    return cleaned != content

def validate_synthetic_data():
    """Ensure all sample data is synthetic"""
    synthetic_indicators = [
        'example.com',
        '[REDACTED]', 
        '192.0.2.',      # TEST-NET-1
        '203.0.113.',    # TEST-NET-3
        '198.51.100.',   # TEST-NET-2
        'localhost',
        'dummy',
        'synthetic',
        'fake',
        'placeholder'
    ]
    
    sample_dirs = list(Path('.').rglob('sample_data'))
    sample_dirs.extend(list(Path('.').rglob('test_data')))
    
    for dir_path in sample_dirs:
        if dir_path.is_dir():
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        # Check if contains synthetic indicators
                        if any(indicator in content for indicator in synthetic_indicators):
                            print(f"Synthetic: {file_path}")
                        else:
                            print(f"Check: {file_path} may need synthetic data")
                    except:
                        pass  # Skip binary files

if __name__ == "__main__":
    # Run on all code files
    extensions = ['.py', '.go', '.rs', '.cs', '.md', '.txt', '.json', '.yaml', '.yml', '.csproj'] # Added .csproj
    
    for ext in extensions:
        for filepath in Path('.').rglob(f'*{ext}'):
            if filepath.is_file():
                sanitize_file(filepath)
    
    validate_synthetic_data()
    print("Content sanitization complete")