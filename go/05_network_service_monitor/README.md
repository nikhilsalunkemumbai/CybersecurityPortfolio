# Network Service Monitor

## Overview
`network_service_monitor` is a command-line utility written in Go that monitors the reachability and response of specified network services (IP:Port combinations). It can be used to quickly check if a service is up and responsive on the network.

## Features
*   **Service Reachability:** Check if a given IP address and port is open and responding.
*   **Multiple Services:** Monitor multiple services listed in an input file.
*   **CLI Interface:** Easy to use from the command line.

## Usage

### Basic Service Check
To check a single service:
```bash
go run main.go -host [REDACTED] -port 80
```

### Monitoring Multiple Services
To monitor services listed in a file:
```bash
go run main.go -i services.txt -o report.txt
```

### Arguments
*   `-h, --host <ip_address>`: Host IP address to monitor.
*   `-p, --port <port_number>`: Port number to monitor.
*   `-i, --input <file>`: Path to a file containing services to monitor (one `host:port` per line). Overrides `-host` and `-port` if provided.
*   `-o, --output <file>`: Path to save the monitoring report. If not provided, prints to stdout.
*   `-t, --timeout <seconds>`: Connection timeout in seconds (default: 3).
*   `-v, --verbose`: Enable verbose output.

## Demonstration (Proof-of-Concept)
This tool is a demonstration artifact to showcase skills in network programming, concurrency (for multiple service checks), and CLI utility development in Go. It adheres to strict development constraints:

*   **Single File:** All code is contained within `main.go`.
*   **Standard Library Only:** No external dependencies are used.
*   **Line Limit:** The source code is kept under 300 lines to promote conciseness.
*   **CLI-Only:** Interactions are exclusively via the command line.

**Note:** This is not production-ready software. It is intended for educational and portfolio purposes only.
