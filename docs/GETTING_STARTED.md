# Getting Started

This guide provides instructions on how to set up your environment and use the security tools featured in this portfolio. These tools are designed to be self-contained and run using standard language runtimes.

## Prerequisites

Ensure you have the following installed on your system:

*   **Python:** Version 3.8 or higher.
*   **Go:** Version 1.19 or higher.
*   **Rust:** Version 1.65 or higher.
*   **.NET:** Version 6.0 or higher (for C# tools).

## Cloning the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/nikhilsalunkemumbai/CybersecurityPortfolio.git
cd cybersecurity-tools
```

## Running the Tools

Each tool is located within its respective language directory (`python/`, `go/`, `rust/`, `csharp/`) under the `phase_1/` directory. Refer to individual tool `README.md` files for specific usage instructions and arguments.

### Python Tools

Navigate to the tool's directory and execute using Python.

```bash
# Example: Running the CSV Security Report Cleaner
cd phase_1/PYTHON/01_csv_security_cleaner
python csv_cleaner.py -i ../../sample_input/vulnerability_scan.csv -o ../../sample_output/cleaned_report.csv -v
```

### Go Tools

Navigate to the tool's directory and run using `go run`.

```bash
# Example: Running the Network Service Monitor
cd phase_1/GO/05_network_service_monitor
go run main.go -i ../../sample_input/services.txt -o ../../sample_output/report.txt -v
```

### Rust Tools

Navigate to the tool's directory, build the project, and run the executable.

```bash
# Example: Running the Memory-Efficient Log Search
cd phase_1/RUST/11_memory_efficient_log_search
cargo build --release
./target/release/memory_efficient_log_search -i ../../sample_input/debug_log.txt -p "DEBUG" -a 1 -v
```

### C# Tools

Navigate to the tool's directory, build the project using .NET CLI, and run the executable.

```bash
# Example: Running the Active Directory User Report
cd phase_1/CSHARP/13_active_directory_user_report
dotnet build --configuration Release
./bin/Release/net8.0/ActiveDirectoryUserReport.exe -e -v --mock 
```
*(Note: C# tool execution might require specific environment setup or administrative privileges depending on the tool's functionality and the host system's Active Directory configuration. The `--mock` flag is used here for demonstration.)*

## Testing

Each tool is accompanied by tests. You can run all tests for a specific language or all tests in the repository:

```bash
# Run all tests across all languages (from the repository root)
python ./scripts/run_all_tests.py

# Test specific language (example for Python)
cd phase_1/PYTHON/01_csv_security_cleaner
python -m pytest tests/
```

## Documentation Structure

*   **Tool-specific:** Each tool has its own `README.md` in its respective directory, detailing its purpose, features, usage, and constraints.
*   **Language-specific:** Directories like `python/`, `go/`, `rust/`, `csharp/` may contain additional language-specific guidelines or patterns.
*   **Repository-wide:** Documents in the `docs/` folder provide overall architecture, disclaimers, and general guidance.
