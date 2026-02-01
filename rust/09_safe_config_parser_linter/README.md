# Safe Config Parser & Linter

## Overview
The **Safe Config Parser & Linter** is a command-line utility designed to parse configuration files (e.g., TOML, YAML, JSON) with a focus on security. It validates configurations against a defined schema or a set of security best practices, reporting any potential misconfigurations, deviations, or errors. This tool is essential for ensuring that application and system configurations adhere to security guidelines, reducing the attack surface.

## Features
*   **Schema-Based Validation:** Validate configuration files against a predefined security schema.
*   **Best Practice Linting:** Check for common security misconfigurations based on established guidelines.
*   **Multiple Format Support:** Designed to support popular configuration formats like TOML, YAML, and JSON.
*   **Detailed Reporting:** Generates comprehensive reports highlighting validation failures and security warnings.

## Usage

### Prerequisites
*   Rust toolchain

### Build
```bash
# Navigate to the tool's directory
cd phase_1/RUST/09_safe_config_parser_linter
cargo build --release
```

### Run
The compiled executable will be located in `target/release/`.

```bash
# Basic usage: lint a config file against a schema
./target/release/safe_config_linter -c <path/to/config.toml> -s <path/to/schema.toml> -o <path/to/report.txt>

# Example with verbose output
./target/release/safe_config_linter -c ./sample_input/insecure_config.toml -s ./sample_input/security_schema.toml -o ./sample_output/lint_report.txt -v
```

### Arguments
*   `-c, --config <FILE>`: Path to the configuration file to parse and lint.
*   `-s, --schema <FILE>`: Path to the security schema file for validation.
*   `-o, --output <FILE>`: (Optional) Path to save the linting report. If not provided, output is printed to stdout.
*   `-v, --verbose`: (Optional) Enable verbose output.

## Examples
*   **Linting an Insecure Configuration:**
    `./target/release/safe_config_linter -c ./sample_input/insecure_config.toml -s ./sample_input/security_schema.toml -o ./sample_output/insecure_report.txt`
*   **Linting a Secure Configuration:**
    `./target/release/safe_config_linter -c ./sample_input/secure_config.toml -s ./sample_input/security_schema.toml -o ./sample_output/secure_report.txt`

## Shared Abstractions Applied
*   **Consistent CLI Argument Parsing:** Uses `std::env::args` (or a similar crate if needed for parsing convenience while adhering to the "no external dependencies" constraint for core logic) for `config`, `schema`, `output`, and `verbose` flags.
*   **Standardized Error Handling & Exit Codes:** Exits with 0 for success, non-zero for errors (e.g., file not found, parsing errors, validation failures). Errors are written to `stderr`.
*   **Unified Logging/Output Format:** Informational messages, warnings, and errors use `[INFO]`, `[WARNING]`, `[ERROR]` prefixes, especially with verbose output.
*   **Declarative Tool Metadata:** Purpose, core logic, and usage are documented in this `README.md` and will be clearly commented in the `src/main.rs` file.

## Design Constraints & Rationale
*   **Line Limit (<=300 lines):** Encourages concise and focused logic for configuration parsing and security linting.
*   **Standard Library Only:** Ensures no external dependencies are required for core functionality, demonstrating fundamental Rust capabilities.
*   **CLI-Only Interface:** Focuses on the core security validation logic.
*   **One Tool = One Problem:** Specifically addresses secure configuration parsing and linting.

## ⚠️ Important Disclaimer
This tool is a portfolio demonstration artifact and should not be used in production environments.
