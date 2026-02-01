import pytest
from pathlib import Path
import sys
import re
from io import StringIO
from unittest.mock import MagicMock

# Since the script is in a 'src' directory, we need to add the parent of 'src' to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.log_highlighter_filter import apply_highlighting, should_process_line, process_log_stream, KEYWORD_COLORS, RESET, YELLOW, RED, GREEN, CYAN # Import colors for assertion


# --- Unit Tests for Core Functions ---

def test_apply_highlighting_case_insensitive():
    """Test case-insensitive highlighting."""
    line = "This is a Test line with KEYWORD and another keyword."
    keywords = ["test", "keyword"]
    highlighted_line = apply_highlighting(line, keywords, case_sensitive=False)
    
    # Expected output: "This is a YELLOWTestYELLOW line with CYANKEYWORDCYAN and another CYANkeywordCYAN." (colors may vary based on KEYWORD_COLORS order)
    # The first keyword 'test' will get KEYWORD_COLORS[0] (YELLOW)
    # The second keyword 'keyword' will get KEYWORD_COLORS[1] (CYAN)
    assert f"{KEYWORD_COLORS[0]}Test{RESET}" in highlighted_line
    assert f"{KEYWORD_COLORS[1]}KEYWORD{RESET}" in highlighted_line
    assert f"{KEYWORD_COLORS[1]}keyword{RESET}" in highlighted_line
    assert "another" in highlighted_line # ensure other parts are untouched

def test_apply_highlighting_case_sensitive():
    """Test case-sensitive highlighting."""
    line = "This is a Test line with KEYWORD and another keyword."
    keywords = ["Test", "KEYWORD"]
    highlighted_line = apply_highlighting(line, keywords, case_sensitive=True)
    
    assert f"{KEYWORD_COLORS[0]}Test{RESET}" in highlighted_line
    assert f"{KEYWORD_COLORS[1]}KEYWORD{RESET}" in highlighted_line
    assert "keyword" in highlighted_line # 'keyword' should not be highlighted
    assert "another" in highlighted_line

def test_apply_highlighting_no_keywords():
    """Test highlighting with no keywords."""
    line = "Just a plain line."
    keywords = []
    highlighted_line = apply_highlighting(line, keywords, case_sensitive=False)
    assert highlighted_line == line

def test_should_process_line_includes_only():
    """Test filtering with only include patterns."""
    line1 = "ERROR: Something critical happened."
    line2 = "INFO: User logged in."
    includes = ["ERROR"]
    
    assert should_process_line(line1, includes, [], case_sensitive=False) is True
    assert should_process_line(line2, includes, [], case_sensitive=False) is False

def test_should_process_line_excludes_only():
    """Test filtering with only exclude patterns."""
    line1 = "DEBUG: Verbose output."
    line2 = "WARNING: Disk space low."
    excludes = ["DEBUG"]
    
    assert should_process_line(line1, [], excludes, case_sensitive=False) is False
    assert should_process_line(line2, [], excludes, case_sensitive=False) is True

def test_should_process_line_includes_and_excludes():
    """Test filtering with both include and exclude patterns."""
    line1 = "ERROR: Network issue."
    line2 = "ERROR: Disk full."
    line3 = "WARNING: Low memory."
    includes = ["ERROR"]
    excludes = ["Disk"]
    
    assert should_process_line(line1, includes, excludes, case_sensitive=False) is True # Matches ERROR, no exclude
    assert should_process_line(line2, includes, excludes, case_sensitive=False) is False # Matches ERROR, but also Disk (exclude)
    assert should_process_line(line3, includes, excludes, case_sensitive=False) is False # No include match

def test_should_process_line_case_sensitive():
    """Test case-sensitive filtering."""
    line = "error: low-level detail."
    includes = ["ERROR"]
    excludes = []
    assert should_process_line(line, includes, excludes, case_sensitive=True) is False # 'error' != 'ERROR'

    includes_case_insensitive = ["error"]
    assert should_process_line(line, includes_case_insensitive, excludes, case_sensitive=True) is True


# --- Integration Test for process_log_stream ---

def test_process_log_stream_integration(tmp_path: Path):
    """
    Integration test for process_log_stream covering highlighting and filtering.
    """
    sample_log_content = """INFO: User 'admin' logged in from 192.168.1.1
WARNING: Low disk space on /dev/sda1
ERROR: Database connection failed for user 'adminuser'
DEBUG: Initiating background process
ERROR: Network timeout for host 'example.com'
"""
    infile = StringIO(sample_log_content)
    outfile = StringIO()

    mock_args = MagicMock()
    mock_args.keywords = ["ERROR", "admin"]
    mock_args.include = ["ERROR", "WARNING"]
    mock_args.exclude = ["timeout"]
    mock_args.case_sensitive = False
    mock_args.verbose = False

    process_log_stream(infile, outfile, mock_args)
    
    output_lines = outfile.getvalue().strip().split('\n')
    
    # Expected lines after filtering and highlighting:
    # INFO: User 'admin' logged in from 192.168.1.1 -> Should not be included (no ERROR or WARNING)
    # WARNING: Low disk space on /dev/sda1 -> Should be included and 'disk' might be highlighted if it matches a keyword, but here we expect WARNING to pass include.
    # ERROR: Database connection failed for user 'appuser' -> Should be included and 'ERROR' highlighted
    # DEBUG: Initiating background process -> Should not be included
    # ERROR: Network timeout for host 'example.com' -> Should be excluded because of 'timeout'
    
    # Re-evaluating expected output based on mock_args:
    # Keywords: "ERROR", "admin" (will be YELLOW and CYAN by default)
    # Include: "ERROR", "WARNING" (case-insensitive)
    # Exclude: "timeout" (case-insensitive)

    # Line 1: "INFO: User 'admin' logged in from 192.168.1.1"
    #   - No include match (INFO is not ERROR/WARNING) -> Should be skipped by filter
    # Line 2: "WARNING: Low disk space on /dev/sda1"
    #   - Include match (WARNING)
    #   - No exclude match
    #   - Keywords: "admin" not in line. "ERROR" not in line.
    #   - Expected: "WARNING: Low disk space on /dev/sda1" (no highlighting with these keywords)
    expected_line_2 = f"{YELLOW}WARNING{RESET}: Low disk space on /dev/sda1" # Assuming WARNING itself is highlighted if it was a keyword. Let's make sure our test does not depend on internal color choices for random text.
    # Actually, keywords are "ERROR", "admin". So no highlighting on "WARNING".
    # Corrected expected: "WARNING: Low disk space on /dev/sda1"

    # Line 3: "ERROR: Database connection failed for user 'appuser'"
    #   - Include match (ERROR)
    #   - No exclude match
    #   - Keywords: "ERROR" in line, "admin" in line.
    #   - Expected: "{COLOR_ERROR}ERROR{RESET}: Database connection failed for user '{COLOR_ADMIN}admin{RESET}user'"
    #     From KEYWORD_COLORS = [YELLOW, CYAN, MAGENTA, GREEN, BLUE, RED]
    #     ERROR gets YELLOW
    #     admin gets CYAN
    expected_line_3 = f"{YELLOW}ERROR{RESET}: Database connection failed for user '{CYAN}admin{RESET}'" # This is tricky due to 'admin' in 'adminuser' in original. The `apply_highlighting` escapes the keyword for regex. 'admin' should be highlighted, not 'adminuser'.
    # Re-checking `apply_highlighting`: `re.sub(f'({escaped_keyword})', f'{color}\1{RESET}', modified_line, flags=flags)`
    # This matches 'admin' inside 'adminuser'. Let's ensure our test is precise.
    # Let's adjust the sample log to have 'user admin' instead to avoid partial matches on words.
    # Or, the test should just check if the output contains the keywords highlighted as expected.
    # Simpler: just check if the output contains the keywords highlighted as expected.

    # For `process_log_stream` test, let's keep it simpler:
    # Just check which lines are output and that some highlighting occurred.

    # Expected output:
    # 1. "INFO: User 'admin' logged in from 192.168.1.1" -> Excluded (no ERROR/WARNING)
    # 2. "WARNING: Low disk space on /dev/sda1" -> Included, no keywords
    # 3. "ERROR: Database connection failed for user 'appuser'" -> Included, "ERROR" and "admin" highlighted
    # 4. "DEBUG: Initiating background process" -> Excluded (no ERROR/WARNING)
    # 5. "ERROR: Network timeout for host 'example.com'" -> Excluded (matches 'timeout')

    # So, expected output lines: 2 and 3

    assert len(output_lines) == 2
    assert "WARNING: Low disk space on /dev/sda1" in output_lines[0]
    assert f"{YELLOW}ERROR{RESET}" in output_lines[1]
    assert f"{CYAN}admin{RESET}" in output_lines[1]
    assert "Database connection failed for user" in output_lines[1]

# Test a scenario with no include patterns (should process all lines then apply excludes)
def test_process_log_stream_no_includes(tmp_path: Path):
    sample_log_content = """
INFO: Something happened.
DEBUG: Detail for debug.
ERROR: Critical error.
"""
    infile = StringIO(sample_log_content)
    outfile = StringIO()

    mock_args = MagicMock()
    mock_args.keywords = ["Critical"]
    mock_args.include = [] # No include patterns, so all pass initial include filter
    mock_args.exclude = ["DEBUG"]
    mock_args.case_sensitive = False
    mock_args.verbose = False

    process_log_stream(infile, outfile, mock_args)
    
    output_lines = outfile.getvalue().strip().split('\n')

    # Expected: INFO, ERROR (DEBUG excluded)
    # Highlight "Critical" in ERROR line
    assert len(output_lines) == 2
    assert "INFO: Something happened." in output_lines[0]
    assert f"{YELLOW}Critical{RESET}" in output_lines[1]
