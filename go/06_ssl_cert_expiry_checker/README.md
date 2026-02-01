# SSL Certificate Expiry Checker

## Overview
`ssl_cert_expiry_checker` is a command-line utility written in Go that checks the SSL/TLS certificate expiry date for specified hosts. It can connect to a list of target hosts, retrieve their certificates, and report on their validity and expiration status.

## Features
*   **Certificate Retrieval:** Connects to HTTPS services to retrieve their SSL/TLS certificates.
*   **Expiry Date Check:** Determines the expiration date of the retrieved certificate.
*   **Validity Status:** Reports if a certificate is valid, expired, or expiring soon.
*   **Multiple Hosts:** Check multiple hosts listed in an input file.
*   **CLI Interface:** Easy to use from the command line.

## Usage

### Basic Certificate Check
To check a single host:
```bash
go run main.go -host example.com
```

### Checking Multiple Hosts
To check hosts listed in a file:
```bash
go run main.go -i hosts.txt -o report.txt
```

### Arguments
*   `-h, --host <hostname>`: Hostname (e.g., example.com) or IP address to check.
*   `-p, --port <port_number>`: Port number for SSL/TLS connection (default: 443).
*   `-i, --input <file>`: Path to a file containing hosts to check (one hostname:port per line, or hostname only defaulting to port 443). Overrides `-host` if provided.
*   `-o, --output <file>`: Path to save the report. If not provided, prints to stdout.
*   `-t, --timeout <seconds>`: Connection timeout in seconds (default: 5).
*   `-w, --warn-days <days>`: Number of days before expiry to issue a warning (default: 30).
*   `-v, --verbose`: Enable verbose output.

## Demonstration (Proof-of-Concept)
This tool is a demonstration artifact to showcase skills in network programming (TLS), certificate parsing, and CLI utility development in Go. It adheres to strict development constraints:

*   **Single File:** All code is contained within `main.go`.
*   **Standard Library Only:** No external dependencies are used. (Uses `crypto/tls` and `x509` which are standard).
*   **Line Limit:** The source code is kept under 300 lines to promote conciseness.
*   **CLI-Only:** Interactions are exclusively via the command line.

**Note:** This is not production-ready software. It is intended for educational and portfolio purposes only.
