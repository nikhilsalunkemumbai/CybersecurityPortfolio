# 12. Arithmetic Safety Checker

## Overview

The Arithmetic Safety Checker is a command-line utility designed to analyze Rust code (or conceptual snippets of code) for potential arithmetic overflow/underflow vulnerabilities. In security, such vulnerabilities can lead to unexpected program behavior, buffer overflows, or incorrect calculations that could be exploited by attackers. This tool demonstrates awareness of safe arithmetic practices in systems programming.

## Features

*   **Integer Overflow/Underflow Detection:** Analyzes integer operations for potential overflow/underflow conditions based on integer type limits.
*   **Compile-Time (Conceptual) Analysis:** Focuses on demonstrating the *concept* of identifying unsafe arithmetic at a static analysis level.
*   **Configurable Integer Sizes:** Can simulate checks for different integer sizes (e.g., `u8`, `i32`, `u64`).
*   **CLI Interface:** Provides a simple command-line interface.
*   **Report Generation:** Outputs potential issues to the console or a file.

## Design Constraints & Rationale

*   **Line Limit (<=300 lines):** Encourages a focused demonstration of arithmetic safety concepts without complex parsing or AST analysis.
*   **Standard Library Only:** Emphasizes fundamental Rust features for basic static analysis and value manipulation. Avoids heavy external crates for parsing or formal verification.
*   **CLI-Only Interface:** Focuses on the core logic of identifying arithmetic safety issues.
*   **One Tool = One Problem:** Specifically addresses the detection of potential arithmetic overflow/underflow conditions.

## Installation

To build this tool, navigate to the tool's directory (`phase_1/RUST/12_arithmetic_safety_checker`) and run:

```bash
cargo build --release
```

The executable will be found in `target/release/arithmetic_safety_checker`.

## Usage

```bash
arithmetic_safety_checker -i <CODE_SNIPPET_FILE> [-o <OUTPUT_FILE>] [-t <TYPE>] [-v | --verbose] [--help]
```

### Arguments

*   `-i`, `--input <FILE>`: Path to a file containing code snippets or arithmetic expressions to check.
*   `-o`, `--output <FILE>`: (Optional) Path to save the analysis report. If not provided, output is printed to stdout.
*   `-t`, `--type <TYPE>`: (Optional) Integer type to simulate (e.g., `u8`, `i16`, `i32`, `u64`). Defaults to `i32`.
*   `-v`, `--verbose`: (Optional) Enable verbose output.
*   `--help`: Display the help message.

## Example

### Check for overflow in a u8 context

Assume `expressions.txt` contains:
```
250 + 10
10 * 30
127 + 1
0 - 1
```

```bash
arithmetic_safety_checker -i expressions.txt -t u8 -o report.txt -v
```

This command will analyze the expressions in `expressions.txt` as if they were `u8` operations, saving a report of potential overflows/underflows to `report.txt`, with verbose information.

### Check for underflow in an i32 context

Assume `negative_ops.txt` contains:
```
-[REDACTED] - 1
```

```bash
arithmetic_safety_checker -i negative_ops.txt -t i32
```

This command will check the expression for potential `i32` underflow and print the result to stdout.

## ⚠️ Important Disclaimer
This tool is a portfolio demonstration artifact and should not be used in production environments.