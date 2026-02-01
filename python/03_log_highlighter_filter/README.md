# Log Highlighter & Filter

## Overview
`log_highlighter_filter.py` is a command-line utility designed to process log files. It can highlight specific keywords in the log output and filter lines based on inclusion and exclusion patterns. This tool is intended for quick analysis and readability improvement of verbose log data.

## Features
*   **Keyword Highlighting:** Emphasize critical information within log entries.
*   **Include/Exclude Filtering:** Focus on relevant log lines by specifying patterns to include or exclude.
*   **CLI Interface:** Easy to use from the command line with standard input/output redirection.

## Usage

### Basic Highlighting
To highlight specific keywords in a log file:
```bash
python log_highlighter_filter.py -i <input_log_file> -o <output_log_file> -k "ERROR" "WARNING"
```

### Filtering Log Lines
To include only lines containing "Failed Login" and exclude lines containing "[REDACTED]":
```bash
python log_highlighter_filter.py -i <input_log_file> -o <output_log_file> --include "Failed Login" --exclude "[REDACTED]"
```

### Combined Highlighting and Filtering
```bash
python log_highlighter_filter.py -i <input_log_file> -o <output_log_file> -k "CRITICAL" --include "session_id=\\d+" 
```

### Arguments
*   `-i, --input <file>`: Path to the input log file. If not provided, reads from stdin.
*   `-o, --output <file>`: Path to the output file. If not provided, writes to stdout.
*   `-k, --keywords <word1> [<word2> ...]`: List of keywords to highlight in the output.
*   `--include <pattern>`: Regular expression pattern to include lines. Only lines matching this pattern will be processed. Can be specified multiple times.
*   `--exclude <pattern>`: Regular expression pattern to exclude lines. Lines matching this pattern will be ignored. Can be specified multiple times.
*   `-c, --case-sensitive`: Perform case-sensitive matching for keywords and patterns.
*   `-v, --verbose`: Enable verbose output, showing processing details.

## Demonstration (Proof-of-Concept)
This tool is a demonstration artifact to showcase skills in text processing, regular expressions, and CLI utility development in Python. It adheres to strict development constraints:

*   **Single File:** All code is contained within `log_highlighter_filter.py`.
*   **Standard Library Only:** No external dependencies are used.
*   **Line Limit:** The source code is kept under 300 lines to promote conciseness.
*   **CLI-Only:** Interactions are exclusively via the command line.

**Note:** This is not production-ready software. It is intended for educational and portfolio purposes only.
