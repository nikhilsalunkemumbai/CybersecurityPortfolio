# Quick IOC Checker

## Overview
`quick_ioc_checker.py` is a command-line tool designed for rapid detection of Indicators of Compromise (IOCs) within text-based data, such as log files, reports, or configuration files. It takes a list of known IOCs and scans a target file for their presence, reporting any matches found.

## Features
*   **IOC List Input:** Accept a file containing a list of IOCs (e.g., IP addresses, domains, hashes).
*   **Target File Scanning:** Scan a specified target file for the presence of any listed IOCs.
*   **Match Reporting:** Report details of each match, including the IOC found, the line number, and the context (optional).
*   **CLI Interface:** Easy to use from the command line.

## Usage

### Basic IOC Checking
To check a log file against a list of IOCs:
```bash
python quick_ioc_checker.py -i ioc_list.txt -t target_log.txt -o report.txt
```

### Arguments
*   `-i, --iocs <file>`: Path to a file containing Indicators of Compromise (one IOC per line). **Required.**
*   `-t, --target <file>`: Path to the target file to scan for IOCs. **Required.**
*   `-o, --output <file>`: Path to save the report of found IOCs. If not provided, prints to stdout.
*   `-c, --case-sensitive`: Perform case-sensitive matching for IOCs.
*   `-v, --verbose`: Enable verbose output, showing more details about the scanning process.

## Demonstration (Proof-of-Concept)
This tool is a demonstration artifact to showcase skills in file I/O, string matching, and CLI utility development in Python. It adheres to strict development constraints:

*   **Single File:** All code is contained within `quick_ioc_checker.py`.
*   **Standard Library Only:** No external dependencies are used.
*   **Line Limit:** The source code is kept under 300 lines to promote conciseness.
*   **CLI-Only:** Interactions are exclusively via the command line.

**Note:** This is not production-ready software. It is intended for educational and portfolio purposes only.
