import pytest
from pathlib import Path
import csv
import sys
from unittest.mock import patch

# Since the script is in a 'src' directory, we need to add the parent of 'src' to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.csv_cleaner import clean_csv_report, should_keep_row

# Sample CSV data for testing
SAMPLE_CSV_CONTENT = """Severity,Plugin Name,Description
High,Kernel Exploit,Remote code execution vulnerability
Critical,Apache Struts,CVE-2017-5638 allows remote code execution
Medium,SSL Certificate Issue,"The certificate is expiring soon"
Low,Informational Finding,Best practice recommendation
Info,PCI Compliance Scan,This is a PCI compliance scan report
High,SQL Injection,User input is not properly sanitized
Medium,Weak Cipher Suite,The server supports weak cipher suites
"""

@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample input CSV file for tests."""
    csv_path = tmp_path / "input.csv"
    csv_path.write_text(SAMPLE_CSV_CONTENT)
    return csv_path

def test_clean_csv_default(sample_csv: Path, tmp_path: Path):
    """Test the default cleaning behavior (medium severity is filtered out)."""
    output_path = tmp_path / "output_default.csv"
    
    # Run the core function
    clean_csv_report(input_path=sample_csv, output_path=output_path, keep_medium=False, verbose=False)

    # Assert the output
    assert output_path.exists()
    with output_path.open('r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # Should keep 'High' and 'Critical'
        assert len(rows) == 3
        severities = {row['Severity'] for row in rows}
        assert "High" in severities
        assert "Critical" in severities
        assert "Medium" not in severities
        assert "Low" not in severities

def test_clean_csv_keep_medium(sample_csv: Path, tmp_path: Path):
    """Test the cleaning behavior with the --keep-medium flag."""
    output_path = tmp_path / "output_keep_medium.csv"
    
    # Run the core function
    clean_csv_report(input_path=sample_csv, output_path=output_path, keep_medium=True, verbose=False)

    # Assert the output
    assert output_path.exists()
    with output_path.open('r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # Should keep 'High', 'Critical', and 'Medium'
        assert len(rows) == 5
        severities = {row['Severity'] for row in rows}
        assert "High" in severities
        assert "Critical" in severities
        assert "Medium" in severities
        assert "Low" not in severities

def test_should_keep_row_logic():
    """Unit test the should_keep_row function directly."""
    high_sev_row = {'Severity': 'High', 'Description': 'Something critical'}
    medium_sev_row = {'Severity': 'Medium', 'Description': 'Something medium'}
    low_sev_row = {'Severity': 'Low', 'Description': 'Something low'}
    info_sev_row = {'Severity': 'Info', 'Description': 'pci compliance issue'}

    # Default behavior (keep_medium=False)
    assert should_keep_row(high_sev_row, keep_medium=False) is True
    assert should_keep_row(medium_sev_row, keep_medium=False) is False
    assert should_keep_row(low_sev_row, keep_medium=False) is False
    
    # Behavior with keep_medium=True
    assert should_keep_row(high_sev_row, keep_medium=True) is True
    assert should_keep_row(medium_sev_row, keep_medium=True) is True
    assert should_keep_row(low_sev_row, keep_medium=True) is False

    # Test false positive pattern filtering
    assert should_keep_row(info_sev_row, keep_medium=True) is False
