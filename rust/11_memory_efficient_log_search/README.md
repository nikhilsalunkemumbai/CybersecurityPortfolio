# 11. Memory-Efficient Log Search

## Overview

The Memory-Efficient Log Search tool is a command-line utility designed for searching large log files for specific patterns (e.g., regex, keywords) without loading the entire file into memory. This is crucial for analyzing extensive log datasets, common in cybersecurity for incident response, threat hunting, and auditing, where memory constraints or file sizes prohibit traditional in-memory processing.

## Features

*   **Pattern-Based Search:** Searches for keywords or regular expression patterns.
*   **Large File Handling:** Processes files line by line, ensuring low memory footprint regardless of log file size.
*   **Contextual Output:** Can display surrounding lines (before and after) a match for better understanding.
*   **CLI Interface:** Provides a simple command-line interface.
*   **Standard Output/File Output:** Can print matching lines to the console or save them to a file.

## Design Constraints & Rationale

*   **Line Limit (<=300 lines):** Encourages a focused and optimized implementation for memory efficiency.
*   **Standard Library Only:** Demonstrates core Rust capabilities for file I/O and string processing without external crates, emphasizing performance control.
*   **CLI-Only Interface:** Focuses on the core search logic without GUI overhead.
*   **One Tool = One Problem:** Specifically addresses the challenge of memory-efficient pattern searching in large log files.

## Installation

To build this tool, navigate to the tool's directory (`phase_1/RUST/11_memory_efficient_log_search`) and run:

```bash
cargo build --release
```

The executable will be found in `target/release/memory_efficient_log_search`.

## Usage

```bash
memory_efficient_log_search -i <LOG_FILE> -p <PATTERN> [-o <OUTPUT_FILE>] [-b <LINES>] [-a <LINES>] [-c | --case-sensitive] [-v | --verbose] [--help]
```

### Arguments

*   `-i`, `--input <FILE>`: Path to the input log file to search.
*   `-p`, `--pattern <PATTERN>`: The search pattern (string or regex).
*   `-o`, `--output <FILE>`: (Optional) Path to save the matching lines. If not provided, output is printed to stdout.
*   `-b`, `--before-context <LINES>`: (Optional) Number of lines to show before a match (default: 0).
*   `-a`, `--after-context <LINES>`: (Optional) Number of lines to show after a match (default: 0).
*   `-c`, `--case-sensitive`: (Optional) Perform case-sensitive matching.
*   `-v`, `--verbose`: (Optional) Enable verbose output.
*   `--help`: Display the help message.

## Example

### Search for an error message with context

```bash
memory_efficient_log_search -i access.log -p "ERROR 500" -b 2 -a 3 -o errors.log -v
```

This command will search `access.log` for lines containing "ERROR 500", outputting 2 lines before and 3 lines after each match to `errors.log`, with verbose information.

### Case-insensitive search for a keyword

```bash
memory_efficient_log_search -i syslog.log -p "failed login" -c
```

This command will perform a case-sensitive search for "failed login" in `syslog.log` and print matching lines to stdout.

## ⚠️ Important Disclaimer
This tool is a portfolio demonstration artifact and should not be used in production environments.