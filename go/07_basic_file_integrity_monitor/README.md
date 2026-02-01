# Basic File Integrity Monitor

## Overview
`basic_file_integrity_monitor` is a command-line utility written in Go that helps maintain the integrity of files by generating and verifying cryptographic hashes. It can create a baseline of file hashes for a given directory or list of files and then detect any unauthorized modifications by comparing current hashes against the baseline.

## Features
*   **Baseline Creation:** Generate cryptographic hashes (SHA256) for a set of files and store them as a baseline.
*   **Integrity Verification:** Compare current file hashes against a previously created baseline to detect changes (modifications, additions, deletions).
*   **CLI Interface:** Easy to use from the command line.

## Usage

### Creating a Baseline
To create a baseline for files in the current directory:
```bash
go run main.go --create-baseline baseline.json --path .
```
Or for specific files listed in `files_to_monitor.txt`:
```bash
go run main.go --create-baseline baseline.json --input files_to_monitor.txt
```

### Verifying Integrity
To verify files against an existing baseline:
```bash
go run main.go --verify-baseline baseline.json --path .
```
Or for specific files listed in `files_to_monitor.txt`:
```bash
go run main.go --verify-baseline baseline.json --input files_to_monitor.txt
```

### Arguments
*   `--create-baseline <file>`: Path to a JSON file to save the baseline hashes.
*   `--verify-baseline <file>`: Path to a JSON baseline file to compare against.
*   `--path <directory>`: Directory to monitor. Defaults to current directory if `--input` is not used.
*   `-i, --input <file>`: Path to a file containing a list of files/directories to monitor (one path per line).
*   `-o, --output <file>`: Path to save the verification report. If not provided, prints to stdout.
*   `-v, --verbose`: Enable verbose output.

## Demonstration (Proof-of-Concept)
This tool is a demonstration artifact to showcase skills in file system interaction, cryptographic hashing, JSON marshaling/unmarshaling, and CLI utility development in Go. It adheres to strict development constraints:

*   **Single File:** All code is contained within `main.go`.
*   **Standard Library Only:** No external dependencies are used. (Uses `crypto/sha256`, `encoding/json`, `io`, `os`, `path/filepath`).
*   **Line Limit:** The source code is kept under 300 lines to promote conciseness.
*   **CLI-Only:** Interactions are exclusively via the command line.

**Note:** This is not production-ready software. It is intended for educational and portfolio purposes only.
