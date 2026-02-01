# HTTP Security Header Scanner

## Overview
`http_security_header_scanner` is a command-line utility written in Go that analyzes HTTP response headers of specified URLs to identify the presence and configuration of common security headers. This helps assess web application security posture.

## Features
*   **HTTP Request:** Make HTTP GET requests to target URLs.
*   **Header Analysis:** Extract and evaluate security-related HTTP response headers (e.g., `Strict-Transport-Security`, `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`).
*   **Security Assessment:** Report on the presence, absence, and recommended configuration of these headers.
*   **Multiple URLs:** Scan multiple URLs listed in an input file.
*   **CLI Interface:** Easy to use from the command line.

## Usage

### Basic Scan of a Single URL
To scan a single URL:
```bash
go run main.go -url https://example.com
```

### Scanning Multiple URLs
To scan URLs listed in a file:
```bash
go run main.go -i urls.txt -o report.txt
```

### Arguments
*   `-u, --url <url>`: Target URL to scan (e.g., `https://example.com`).
*   `-i, --input <file>`: Path to a file containing a list of URLs to scan (one URL per line). Overrides `-url` if provided.
*   `-o, --output <file>`: Path to save the report. If not provided, prints to stdout.
*   `-t, --timeout <seconds>`: HTTP request timeout in seconds (default: 10).
*   `-v, --verbose`: Enable verbose output.

## Demonstration (Proof-of-Concept)
This tool is a demonstration artifact to showcase skills in HTTP networking, header parsing, and CLI utility development in Go. It adheres to strict development constraints:

*   **Single File:** All code is contained within `main.go`.
*   **Standard Library Only:** No external dependencies are used.
*   **Line Limit:** The source code is kept under 300 lines to promote conciseness.
*   **CLI-Only:** Interactions are exclusively via the command line.

**Note:** This is not production-ready software. It is intended for educational and portfolio purposes only.
