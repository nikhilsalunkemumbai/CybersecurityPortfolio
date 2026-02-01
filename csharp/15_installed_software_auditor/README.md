# 15. Installed Software Auditor

## Overview

The **Installed Software Auditor** is a command-line utility designed to audit installed software on Windows systems. It enumerates installed applications and their metadata, allowing users to identify unauthorized, outdated, or potentially vulnerable software. This tool is crucial for maintaining a secure software baseline and ensuring compliance within an organization.

## Purpose

Maintaining an accurate inventory of installed software is a fundamental security practice. Organizations need to know what software is running on their endpoints to assess their attack surface, manage licensing, and respond to vulnerabilities. This tool automates the collection and filtering of installed software information, aiding in proactive security posture management.

## Functionality

*   **Software Enumeration:** Discovers applications installed via various methods, including MSI packages, Win32 applications, and potentially modern UWP apps (depending on API availability and PoC scope).
*   **Metadata Collection:** Gathers details such as software name, version, publisher, and installation date.
*   **Filtering Capabilities:** Allows users to filter the audit results based on:
    *   Specific software names (e.g., to find all versions of a particular browser).
    *   Publishers.
    *   Installation dates (e.g., to find recently installed software).
*   **Output Formats:** Presents the audited software list in a readable format, either to the console or an output file (e.g., CSV, plain text).

## Usage

```bash
# Basic usage example (detailed CLI arguments will be specified during implementation)
InstalledSoftwareAuditor.exe --list-all --output-file installed_software_report.csv
InstalledSoftwareAuditor.exe --filter-name "VLC media player" -v
```

## Core Logic Description

The tool will primarily interact with the Windows Registry (`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` and `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`) to enumerate installed applications. It will parse the relevant registry keys and values to extract software metadata. Additionally, it might explore COM interfaces or WMI queries for more comprehensive data, especially for per-user installations or UWP apps, while keeping the line limit in mind.

It will implement logic to:
1.  Parse command-line arguments for filtering and output preferences.
2.  Query the Windows Registry (and potentially other sources) to get a list of installed software.
3.  Collect relevant metadata for each application.
4.  Apply filters based on user input.
5.  Format the collected data into a report.

## Shared Abstractions

This tool adheres to the project's [Shared Abstraction Principles](../../../CONTEXT/SHARED_ABSTRACTIONS_CHECKLIST.md), specifically:
*   **Consistent CLI Argument Parsing:** Command-line arguments will be parsed using a standardized approach (e.g., `System.CommandLine`), providing clear `-l`, `-f`, `-o`, `-v`, and other relevant flags.
*   **Standardized Error Handling & Exit Codes:** The tool will exit with `0` on success and non-zero codes for specific errors (e.g., `1` for invalid arguments, `2` for access denied), directing error messages to `stderr`.
*   **Unified Logging/Output Format:** Informational messages, warnings, and errors will be formatted consistently with `[INFO]`, `[WARNING]`, `[ERROR]` prefixes when verbose output is enabled.
*   **Declarative Tool Metadata:** This `README.md` along with comments in the `Program.cs` file serves as the declarative metadata for the tool.

## Constraints

This tool adheres to the [Programming Standards, Discipline, and Constraints](../../../CONTEXT/PROGRAMMING_STANDARDS.md) defined for this portfolio, including:
*   **Line Limit:** The core logic will be constrained to approximately 300 lines of code to ensure conciseness and focus.
*   **Standard Library Only:** Relies primarily on .NET standard libraries for registry interaction and data processing.
*   **CLI-Only Interface:** Provides functionality exclusively through a command-line interface.
*   **One Tool = One Problem:** Focuses solely on auditing installed software.

## Development Notes

*   Prioritize registry-based enumeration for robustness and simplicity within the PoC.
*   Consider both 32-bit and 64-bit registry views for comprehensive results (`HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall`).
*   Error handling for registry access permissions.

## ⚠️ Important Disclaimer
This tool is a portfolio demonstration artifact and should not be used in production environments.
