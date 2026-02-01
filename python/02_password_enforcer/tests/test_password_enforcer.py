import pytest
from pathlib import Path
import sys
import re

# Since the script is in a 'src' directory, we need to add the parent of 'src' to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.password_enforcer import check_password_strength, enforce_policy_on_file, DEFAULT_POLICY

# Sample password data for testing
SAMPLE_PASSWORDS_CONTENT = """Password123!\nshort!\nnouppercase123!\nNOLOWERCASE123!\nNoDigit!\nNoSpecial123\nPassword!\n"""

@pytest.fixture
def sample_passwords_file(tmp_path: Path) -> Path:
    """Create a sample input password file for tests."""
    passwords_path = tmp_path / "passwords.txt"
    passwords_path.write_text(SAMPLE_PASSWORDS_CONTENT)
    return passwords_path

def parse_report(report_content: str) -> list:
    """Helper to parse the generated report content."""
    entries = report_content.strip().split("-" * 30 + "\n")
    parsed_results = []
    for entry in entries:
        if not entry.strip():
            continue
        
        password_match = re.search(r"Password: (.+)\n", entry)
        status_match = re.search(r"Status: (.+)\n", entry)
        violations_match = re.search(r"Violations: (.+)\n", entry)
        line_match = re.search(r"Line: (.+)\n", entry)

        parsed_results.append({
            'password': password_match.group(1) if password_match else None,
            'status': status_match.group(1) if status_match else None,
            'violations': violations_match.group(1) if violations_match else "N/A",
            'line_num': int(line_match.group(1)) if line_match else None
        })
    return parsed_results

def test_check_password_strength_default_policy():
    """Unit test check_password_strength with default policy."""
    policy = DEFAULT_POLICY

    # Compliant password
    assert check_password_strength("Password123!", policy) == []
    # Too short
    assert "Minimum length of 8 characters not met." in check_password_strength("short!", policy)
    # Missing uppercase
    assert "Missing uppercase character." in check_password_strength("nouppercase123!", policy)
    # Missing lowercase
    assert "Missing lowercase character." in check_password_strength("NOLOWERCASE123!", policy)
    # Missing digit
    assert "Missing digit." in check_password_strength("NoDigit!", policy)
    # Missing special
    assert "Missing special character." in check_password_strength("NoSpecial123", policy)

def test_check_password_strength_custom_policy():
    """Unit test check_password_strength with a custom policy."""
    custom_policy = {
        'min_length': 6,
        'require_uppercase': False,
        'require_lowercase': True,
        'require_digit': False,
        'require_special': False,
    }
    assert check_password_strength("password", custom_policy) == []
    assert "Minimum length of 6 characters not met." in check_password_strength("pass", custom_policy)
    assert "Missing lowercase character." in check_password_strength("PASSWORD", custom_policy)

def test_enforce_policy_on_file_default(sample_passwords_file: Path, tmp_path: Path):
    """Test enforce_policy_on_file with default policy."""
    output_path = tmp_path / "report_default.txt"
    policy = DEFAULT_POLICY

    results, total, non_compliant = enforce_policy_on_file(sample_passwords_file, output_path, policy, verbose=False)

    assert output_path.exists()
    report_content = output_path.read_text()
    parsed_report = parse_report(report_content)

    assert total == 7
    assert non_compliant == 6 # Adjusted to 6
    assert len(parsed_report) == 7

    # Verify specific results
    assert parsed_report[0]['password'] == "Password123!"
    assert parsed_report[0]['status'] == "COMPLIANT"

    assert parsed_report[1]['password'] == "short!"
    assert parsed_report[1]['status'] == "NON-COMPLIANT"
    assert "Minimum length of 8 characters not met." in parsed_report[1]['violations']

    assert parsed_report[4]['password'] == "NoDigit!"
    assert parsed_report[4]['status'] == "NON-COMPLIANT"
    assert "Missing digit." in parsed_report[4]['violations']

    assert parsed_report[5]['password'] == "NoSpecial123"
    assert parsed_report[5]['status'] == "NON-COMPLIANT"
    assert "Missing special character." in parsed_report[5]['violations']

def test_enforce_policy_on_file_custom(sample_passwords_file: Path, tmp_path: Path):
    """Test enforce_policy_on_file with a custom relaxed policy."""
    output_path = tmp_path / "report_custom.txt"
    custom_policy = {
        'min_length': 6,
        'require_uppercase': False,
        'require_lowercase': True,
        'require_digit': False,
        'require_special': False,
    }

    results, total, non_compliant = enforce_policy_on_file(sample_passwords_file, output_path, custom_policy, verbose=False)

    assert output_path.exists()
    report_content = output_path.read_text()
    parsed_report = parse_report(report_content)

    assert total == 7
    assert non_compliant == 1 # Adjusted to 1
    assert len(parsed_report) == 7
    # Verify specific results
    assert parsed_report[0]['password'] == "Password123!"
    assert parsed_report[0]['status'] == "COMPLIANT"

    assert parsed_report[1]['password'] == "short!"
    assert parsed_report[1]['status'] == "COMPLIANT" # Now compliant with min_length=6, no other requirements

    assert parsed_report[2]['password'] == "nouppercase123!"
    assert parsed_report[2]['status'] == "COMPLIANT" # Now compliant (no uppercase needed)

    assert parsed_report[3]['password'] == "NOLOWERCASE123!"
    assert parsed_report[3]['status'] == "NON-COMPLIANT" # Still non-compliant (missing lowercase)

    assert parsed_report[4]['password'] == "NoDigit!"
    assert parsed_report[4]['status'] == "COMPLIANT" # Adjusted expectation

    assert parsed_report[5]['password'] == "NoSpecial123"
    assert parsed_report[5]['status'] == "COMPLIANT" # Adjusted expectation

    assert non_compliant == 1 # Adjusted from 2 to 1
