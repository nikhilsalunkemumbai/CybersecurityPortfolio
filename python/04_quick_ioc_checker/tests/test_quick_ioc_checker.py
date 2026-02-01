import pytest
from pathlib import Path
import sys
import re
from io import StringIO
from unittest.mock import MagicMock

# Since the script is in a 'src' directory, we need to add the parent of 'src' to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quick_ioc_checker import load_iocs, scan_target_file, write_report

# --- Sample Data ---
SAMPLE_IOC_CONTENT = """192.168.1.100
malicious.com
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
suspicious-app.exe
"""

SAMPLE_TARGET_CONTENT = """Log entry from 2026-01-01: connection from 192.168.1.100
User logged in from innocent.com
Found a file named suspicious-app.exe with hash E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
Access attempt from MALICIOUS.COM to internal server.
Normal system activity.
"""

# --- Fixtures ---

@pytest.fixture
def sample_iocs_file(tmp_path: Path) -> Path:
    """Create a sample IOCs file."""
    ioc_path = tmp_path / "iocs.txt"
    ioc_path.write_text(SAMPLE_IOC_CONTENT)
    return ioc_path

@pytest.fixture
def sample_target_file(tmp_path: Path) -> Path:
    """Create a sample target file to scan."""
    target_path = tmp_path / "target.log"
    target_path.write_text(SAMPLE_TARGET_CONTENT)
    return target_path

# --- Helper to parse report output ---
def parse_report_output(report_content: str) -> list:
    """Parses the generated report content into a list of dictionaries."""
    matches = []
    current_match = {}
    for line in report_content.split('\n'):
        if line.startswith("IOC Found:"):
            current_match['ioc'] = line.split(":", 1)[1].strip()
        elif line.startswith("Line Number:"):
            current_match['line_num'] = int(line.split(":", 1)[1].strip())
        elif line.startswith("Line Content:"):
            current_match['line_content'] = line.split(":", 1)[1].strip()
        elif line.startswith("---") and current_match:
            matches.append(current_match)
            current_match = {}
    return matches

# --- Unit Tests ---

def test_load_iocs_success(sample_iocs_file: Path):
    """Test successful loading of IOCs."""
    iocs = load_iocs(sample_iocs_file)
    assert len(iocs) == 4
    assert "192.168.1.100" in iocs
    assert "malicious.com" in iocs
    assert "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in iocs
    assert "suspicious-app.exe" in iocs

def test_load_iocs_file_not_found(tmp_path: Path, capsys):
    """Test loading IOCs from a non-existent file."""
    non_existent_file = tmp_path / "non_existent.txt"
    with pytest.raises(SystemExit) as excinfo:
        load_iocs(non_existent_file)
    assert excinfo.value.code == 1
    outerr = capsys.readouterr()
    assert "ERROR] IOC file not found" in outerr.err

# --- Integration Tests ---

def test_scan_target_file_case_insensitive(sample_iocs_file: Path, sample_target_file: Path):
    """Test scanning with default (case-insensitive) matching."""
    iocs = load_iocs(sample_iocs_file)
    output_stream = StringIO()
    
    matches_count = scan_target_file(sample_target_file, iocs, output_stream, case_sensitive=False, verbose=False)
    report = output_stream.getvalue()
    parsed_matches = parse_report_output(report)

    assert matches_count == 4
    assert len(parsed_matches) == 4

    # Verify specific matches
    assert any(m['ioc'] == '192.168.1.100' and m['line_num'] == 1 for m in parsed_matches)
    assert any(m['ioc'] == 'suspicious-app.exe' and m['line_num'] == 3 for m in parsed_matches)
    assert any(m['ioc'].lower() == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'.lower() and m['line_num'] == 3 for m in parsed_matches)
    assert any(m['ioc'].lower() == 'malicious.com'.lower() and m['line_num'] == 4 for m in parsed_matches)

def test_scan_target_file_case_sensitive(sample_iocs_file: Path, sample_target_file: Path):
    """Test scanning with case-sensitive matching."""
    iocs = load_iocs(sample_iocs_file)
    output_stream = StringIO()
    
    matches_count = scan_target_file(sample_target_file, iocs, output_stream, case_sensitive=True, verbose=False)
    report = output_stream.getvalue()
    parsed_matches = parse_report_output(report)

    assert matches_count == 2
    assert len(parsed_matches) == 2

    # Verify specific matches (malicious.com and the hash should not match due to case)
    assert any(m['ioc'] == '192.168.1.100' and m['line_num'] == 1 for m in parsed_matches)
    assert any(m['ioc'] == 'suspicious-app.exe' and m['line_num'] == 3 for m in parsed_matches)
    assert not any(m['ioc'] == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' for m in parsed_matches) # Hash is case-sensitive no match
    assert not any(m['ioc'] == 'malicious.com' for m in parsed_matches) # Should not find case-insensitive match

def test_scan_target_file_no_iocs_found(sample_iocs_file: Path, tmp_path: Path):
    """Test scanning when no IOCs are found."""
    non_ioc_target_content = "This is a clean log file with no threats."
    non_ioc_target_file = tmp_path / "clean.log"
    non_ioc_target_file.write_text(non_ioc_target_content)

    iocs = load_iocs(sample_iocs_file) # Use existing IOCs
    output_stream = StringIO()
    
    matches_count = scan_target_file(non_ioc_target_file, iocs, output_stream, case_sensitive=False, verbose=False)
    report = output_stream.getvalue()

    assert matches_count == 0
    assert "No Indicators of Compromise found." in report
