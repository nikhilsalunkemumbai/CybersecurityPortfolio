/*
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of a network service monitor.
PURPOSE: Show skill in network programming, concurrency (goroutines), and CLI utility development in Go.
CONSTRAINTS: Uses standard library only, designed for CLI, <=300 lines (intentional).
STATUS: Complete demonstration - no updates planned.
EVALUATION: Assess what this demonstrates, not production readiness.
*/

package main

import (
	"bufio"
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
)

// Global variables for CLI flags
var (
	host        string
	port        int
	inputFile   string
	outputFile  string
	timeoutSec  int
	verboseMode bool
)

// ServiceCheckResult stores the result of a single service check
type ServiceCheckResult struct {
	Address string
	Status  string
	Error   error
}

func init() {
	// --- CLI Argument Parsing ---
	flag.StringVar(&host, "host", "", "Host IP address or hostname to monitor.")
	flag.StringVar(&host, "h", "", "Host IP address or hostname to monitor (shorthand).")

	flag.IntVar(&port, "port", 0, "Port number to monitor.")
	flag.IntVar(&port, "p", 0, "Port number to monitor (shorthand).")

	flag.StringVar(&inputFile, "input", "", "Path to a file containing services to monitor (host:port per line). Overrides -host and -port if provided.")
	flag.StringVar(&inputFile, "i", "", "Path to a file containing services to monitor (shorthand).")

	flag.StringVar(&outputFile, "output", "", "Path to save the monitoring report. If not provided, prints to stdout.")
	flag.StringVar(&outputFile, "o", "", "Path to save the monitoring report (shorthand).")

	flag.IntVar(&timeoutSec, "timeout", 3, "Connection timeout in seconds.")
	flag.IntVar(&timeoutSec, "t", 3, "Connection timeout in seconds (shorthand).")

	flag.BoolVar(&verboseMode, "verbose", false, "Enable verbose output.")
	flag.BoolVar(&verboseMode, "v", false, "Enable verbose output (shorthand).")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Monitors the reachability and response of specified network services.\n")
		fmt.Fprintf(os.Stderr, "  Example: %s -h [REDACTED] -p 80\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Example: %s -i services.txt -o report.txt\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Flags:\n")
		flag.PrintDefaults()
	}
}

// checkService attempts to establish a TCP connection to the given address.
func checkService(address string, timeout time.Duration) ServiceCheckResult {
	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Checking service: %s\n", address)
	}
	conn, err := net.DialTimeout("tcp", address, timeout)
	if err != nil {
		return ServiceCheckResult{Address: address, Status: "DOWN", Error: err}
	}
	defer conn.Close()
	return ServiceCheckResult{Address: address, Status: "UP", Error: nil}
}

// loadServicesFromFile reads host:port pairs from a specified file.
func loadServicesFromFile(filePath string) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("[ERROR] Failed to open input file %s: %w", filePath, err)
	}
	defer file.Close()

	var services []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" {
			services = append(services, line)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("[ERROR] Error reading input file %s: %w", filePath, err)
	}
	return services, nil
}

// writeReport generates the monitoring report.
func writeReport(results []ServiceCheckResult, output *os.File) {
	fmt.Fprintf(output, "--- Network Service Monitor Report ---\n\n")
	if len(results) == 0 {
		fmt.Fprintln(output, "No services were monitored or no results to report.")
		return
	}

	for _, result := range results {
		fmt.Fprintf(output, "Service: %s\n", result.Address)
		fmt.Fprintf(output, "Status: %s\n", result.Status)
		if result.Error != nil {
			fmt.Fprintf(output, "Error: %v\n", result.Error)
		}
		fmt.Fprintln(output, "------------------------------")
	}
}

// main is the entry point of the Network Service Monitor tool.
func main() {
	flag.Parse()

	// Validate arguments
	if inputFile == "" && (host == "" || port == 0) {
		flag.Usage()
		fmt.Fprintln(os.Stderr, "\n[ERROR] Either an input file (-i) or a host (-h) and port (-p) must be provided.")
		os.Exit(1)
	}
	if inputFile != "" && (host != "" || port != 0) {
		fmt.Fprintln(os.Stderr, "[WARNING] Input file (-i) provided. -host and -port flags will be ignored.")
	}

	var servicesToMonitor []string
	if inputFile != "" {
		loadedServices, err := loadServicesFromFile(inputFile)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		servicesToMonitor = loadedServices
	} else {
		servicesToMonitor = []string{net.JoinHostPort(host, fmt.Sprintf("%d", port))}
	}

	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Monitoring %d service(s)...\n", len(servicesToMonitor))
	}

	results := make(chan ServiceCheckResult, len(servicesToMonitor))
	timeoutDuration := time.Duration(timeoutSec) * time.Second

	for _, service := range servicesToMonitor {
		go func(svc string) {
			results <- checkService(svc, timeoutDuration)
		}(service)
	}

	var serviceCheckResults []ServiceCheckResult
	for i := 0; i < len(servicesToMonitor); i++ {
		serviceCheckResults = append(serviceCheckResults, <-results)
	}

	output := os.Stdout
	if outputFile != "" {
		var err error
		output, err = os.Create(outputFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to create output file %s: %v\n", outputFile, err)
			os.Exit(1)
		}
		defer output.Close()
	}

	writeReport(serviceCheckResults, output)

	if verboseMode {
		fmt.Fprintln(os.Stderr, "[INFO] Monitoring complete.")
	}
	os.Exit(0)
}
