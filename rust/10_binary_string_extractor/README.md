# 10. Binary String Extractor

## Overview

The Binary String Extractor is a command-line utility designed to extract human-readable strings from binary files. This tool is useful in various cybersecurity contexts, such as malware analysis, reverse engineering, and digital forensics, where identifying embedded text strings can provide crucial insights into a file's purpose, capabilities, or origin.

## Features

*   **String Extraction:** Scans binary files for sequences of printable characters.
*   **Minimum Length Filtering:** Allows specifying a minimum length for extracted strings to reduce noise.
*   **CLI Interface:** Provides a simple command-line interface for ease of use.
*   **Standard Output/File Output:** Can print extracted strings to the console or save them to a file.

## Design Constraints & Rationale

*   **Line Limit (<=300 lines):** Encourages concise and efficient implementation, demonstrating the ability to focus on core functionality.
*   **Standard Library Only:** Ensures the tool is self-contained and avoids external dependencies, highlighting fundamental Rust programming skills.
*   **CLI-Only Interface:** Focuses on the core string extraction logic without the overhead of GUI development.
*   **One Tool = One Problem:** Addresses the specific problem of extracting printable strings from binary data.

## Installation

To build this tool, navigate to the tool's directory (`phase_1/RUST/10_binary_string_extractor`) and run:

```bash
cargo build --release
```

The executable will be found in `target/release/binary_string_extractor`.

## Usage

```bash
binary_string_extractor -i <INPUT_FILE> [-o <OUTPUT_FILE>] [-m <MIN_LENGTH>] [-v | --verbose] [--help]
```

### Arguments

*   `-i`, `--input <FILE>`: Path to the binary input file to extract strings from.
*   `-o`, `--output <FILE>`: (Optional) Path to save the extracted strings. If not provided, output is printed to stdout.
*   `-m`, `--min-length <LENGTH>`: (Optional) Minimum length of strings to extract (default: 4).
*   `-v`, `--verbose`: (Optional) Enable verbose output.
*   `--help`: Display the help message.

## Example

### Extract strings from a binary file (default minimum length)

```bash
binary_string_extractor -i sample.exe -o extracted_strings.txt
```

This command will extract all strings of default minimum length (4) from `sample.exe` and save them to `extracted_strings.txt`.

### Extract strings with a custom minimum length and verbose output

```bash
binary_string_extractor -i /bin/ls -m 8 -v
```

This command will extract strings of minimum length 8 from the `/bin/ls` executable, printing them to the console along with verbose processing information.

## ⚠️ Important Disclaimer
This tool is a portfolio demonstration artifact and should not be used in production environments.