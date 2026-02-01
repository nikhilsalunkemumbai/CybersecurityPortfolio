# 13. Active Directory User Report

## Overview

The Active Directory User Report tool is a command-line utility written in C# designed to generate basic reports of users within an Active Directory domain. This tool demonstrates interaction with Active Directory services, which is a fundamental skill in enterprise cybersecurity for tasks such as auditing user accounts, identifying stale accounts, or reviewing group memberships.

## Features

*   **User Listing:** Retrieves and displays a list of Active Directory user accounts.
*   **Filtering:** Allows basic filtering of users (e.g., enabled/disabled accounts).
*   **Property Selection:** Can specify which user properties to include in the report.
*   **CLI Interface:** Provides a simple command-line interface for ease of use.
*   **Standard Output/File Output:** Can print the report to the console or save it to a file (e.g., CSV).

## Design Constraints & Rationale

*   **Line Limit (<=300 lines):** Encourages a focused implementation, demonstrating core AD interaction and reporting logic.
*   **Standard Library Only (.NET Framework):** Emphasizes fundamental C# features and the .NET framework's built-in capabilities for Active Directory integration (specifically `System.DirectoryServices.AccountManagement`), avoiding unnecessary external NuGet packages beyond foundational framework extensions.
*   **CLI-Only Interface:** Focuses on the core logic of interacting with Active Directory without GUI overhead.
*   **One Tool = One Problem:** Specifically addresses the task of generating a basic Active Directory user report.

## Installation

To build this tool, navigate to the tool's directory (`phase_1/CSHARP/13_active_directory_user_report`) and run:

```bash
dotnet build --configuration Release
```

The executable will be found in `bin/Release/net8.0/ActiveDirectoryUserReport.exe`.

## Usage

```bash
ActiveDirectoryUserReport.exe [-d <DOMAIN_NAME>] [-o <OUTPUT_FILE>] [-e | --enabled-only] [-s | --show-properties <PROP1,PROP2>] [-v | --verbose] [--mock] [--help]
```

### Arguments

*   `-d`, `--domain <DOMAIN>`: (Optional) The Active Directory domain to query. Defaults to the current domain.
*   `-o`, `--output <FILE>`: (Optional) Path to save the report (e.g., CSV). If not provided, prints to stdout.
*   `-e`, `--enabled-only`: (Optional) Only show enabled user accounts.
*   `-s`, `--show-properties <PROP1,PROP2>`: (Optional) Comma-separated list of additional AD user properties to display (e.g., `mail,description`).
*   `-v`, `--verbose`: (Optional) Enable verbose output.
*   `--mock`: (Optional) Use mock data for testing instead of connecting to a real Active Directory.
*   `--help`: Display the help message.

## Example

### List all enabled users in the current domain to console

```bash
ActiveDirectoryUserReport.exe -e -v
```

### Export specific properties for all users to a CSV file

```bash
ActiveDirectoryUserReport.exe -o users.csv -s "mail,lastLogon"
```

### Run with mock data (for development/testing without AD access)

```bash
ActiveDirectoryUserReport.exe -e -v --mock
```

This command will export the mail and lastLogon properties for all users in the current domain to `users.csv`.
**NOTE:** This tool requires access to an Active Directory domain and appropriate permissions to query user information. It is intended for use in controlled lab environments or on systems with proper AD access configured.

## Testing

A dedicated test project, `ActiveDirectoryUserReport.Tests`, has been created to facilitate testing without direct access to a live Active Directory environment. This project uses `MSTest` and leverages a `MockADService` (implementing the `IADService` interface) to simulate Active Directory interactions.

### Running Tests

To run the unit tests, navigate to the tool's directory (`phase_1/CSHARP/13_active_directory_user_report`) and execute:

```bash
dotnet test ActiveDirectoryUserReport.Tests
```

This will build and run the tests, providing a quick verification of the application's logic against predefined mock data scenarios.

## ⚠️ Important Disclaimer
This tool is a portfolio demonstration artifact and should not be used in production environments.
