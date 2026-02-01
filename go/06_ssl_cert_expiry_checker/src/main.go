package main

/*
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of an SSL/TLS Certificate Expiry Checker.
PURPOSE: Show skill in network programming (TLS), certificate handling, and CLI utility development in Go.
CONSTRAINTS: Uses standard library only, designed for CLI, <=300 lines (intentional).
STATUS: Complete demonstration - no updates planned.
EVALUATION: Assess what this demonstrates, not production readiness.
*/

import (
	"bufio"
	"crypto/tls"
	"crypto/x509"
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
	port        string
	inputFile   string
	outputFile  string
	timeoutSec  int
	warnDays    int
	verboseMode bool
)

// CertCheckResult stores the result of a single certificate check
type CertCheckResult struct {
	Host        string
	ExpiryDate  time.Time
	DaysLeft    int
	Status      string
	Error       error
}

func init() {
	// --- CLI Argument Parsing ---
	flag.StringVar(&host, "host", "", "Hostname to check (e.g., example.com).")
	flag.StringVar(&host, "h", "", "Hostname to check (shorthand).")

	flag.StringVar(&port, "port", "443", "Port number for SSL/TLS connection.")
	flag.StringVar(&port, "p", "443", "Port number for SSL/TLS connection (shorthand).")

	flag.StringVar(&inputFile, "input", "", "Path to a file containing hosts to check (one host:port or host per line). Overrides -host if provided.")
	flag.StringVar(&inputFile, "i", "", "Path to a file containing hosts to check (shorthand).")

	flag.StringVar(&outputFile, "output", "", "Path to save the report. If not provided, prints to stdout.")
	flag.StringVar(&outputFile, "o", "", "Path to save the report (shorthand).")

	flag.IntVar(&timeoutSec, "timeout", 5, "Connection timeout in seconds.")
	flag.IntVar(&timeoutSec, "t", 5, "Connection timeout in seconds (shorthand).")

	flag.IntVar(&warnDays, "warn-days", 30, "Number of days before expiry to issue a warning.")
	flag.IntVar(&warnDays, "w", 30, "Number of days before expiry to issue a warning (shorthand).")

	flag.BoolVar(&verboseMode, "verbose", false, "Enable verbose output.")
	flag.BoolVar(&verboseMode, "v", false, "Enable verbose output (shorthand).")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Checks the SSL/TLS certificate expiry date for specified hosts.\n")
		fmt.Fprintf(os.Stderr, "  Example: %s -h google.com\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Example: %s -i hosts.txt -o report.txt\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Flags:\n")
		flag.PrintDefaults()
	}
}

// checkCertExpiry connects to a host, retrieves its SSL cert, and checks its expiry.
func checkCertExpiry(targetHostPort string, timeout time.Duration, warnThreshold int) CertCheckResult {
	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Checking certificate for: %s\n", targetHostPort)
	}

	conn, err := tls.DialWithDialer(&net.Dialer{Timeout: timeout}, "tcp", targetHostPort, &tls.Config{
		InsecureSkipVerify: true, // Not secure, but simplifies demo and avoids cert chain issues
	})
	if err != nil {
		return CertCheckResult{Host: targetHostPort, Status: "ERROR", Error: fmt.Errorf("TLS connection failed: %w", err)}
	}
	defer conn.Close()

	peerCerts := conn.ConnectionState().PeerCertificates
	if len(peerCerts) == 0 {
		return CertCheckResult{Host: targetHostPort, Status: "ERROR", Error: fmt.Errorf("no certificates found")}
	}

	// Use the first certificate in the chain (usually the leaf certificate)
	var cert *x509.Certificate = peerCerts[0]

	daysLeft := int(time.Until(cert.NotAfter).Hours() / 24)

	status := "VALID"
	if daysLeft < 0 {
		status = "EXPIRED"
	} else if daysLeft <= warnThreshold {
		status = fmt.Sprintf("EXPIRING SOON (%d days)", daysLeft)
	}

	return CertCheckResult{Host: targetHostPort, ExpiryDate: cert.NotAfter, DaysLeft: daysLeft, Status: status, Error: nil}
}

// loadHostsFromFile reads host:port or host entries from a specified file.
func loadHostsFromFile(filePath string, defaultPort string) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("[ERROR] Failed to open input file %s: %w", filePath, err)
	}
	defer file.Close()

	var hosts []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		// If line doesn't contain a port, append defaultPort
		if !strings.Contains(line, ":") {
			line = net.JoinHostPort(line, defaultPort)
		}
		hosts = append(hosts, line)
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("[ERROR] Error reading input file %s: %w", filePath, err)
	}
	return hosts, nil
}

// writeReport generates the certificate expiry report.
func writeReport(results []CertCheckResult, output *os.File) {
	fmt.Fprintf(output, "--- SSL Certificate Expiry Report ---\n\n")
	if len(results) == 0 {
		fmt.Fprintln(output, "No hosts were checked or no results to report.")
		return
	}

	for _, result := range results {
		fmt.Fprintf(output, "Host: %s\n", result.Host)
		fmt.Fprintf(output, "Status: %s\n", result.Status)
		if result.ExpiryDate.IsZero() {
			fmt.Fprintf(output, "Expiry Date: N/A\n")
			fmt.Fprintf(output, "Days Left: N/A\n")
		} else {
			fmt.Fprintf(output, "Expiry Date: %s\n", result.ExpiryDate.Format("2006-01-02"))
			fmt.Fprintf(output, "Days Left: %d\n", result.DaysLeft)
		}
		if result.Error != nil {
			fmt.Fprintf(output, "Error: %v\n", result.Error)
		}
		fmt.Fprintln(output, "------------------------------")
	}
}

// main is the entry point of the SSL Certificate Expiry Checker tool.
func main() {
	flag.Parse()

	// Validate arguments
	if inputFile == "" && host == "" {
		flag.Usage()
		fmt.Fprintln(os.Stderr, "\n[ERROR] Either an input file (-i) or a hostname (-h) must be provided.")
		os.Exit(1)
	}
	if inputFile != "" && host != "" {
		fmt.Fprintln(os.Stderr, "[WARNING] Input file (-i) provided. -host flag will be ignored.")
	}

	var hostsToMonitor []string
	if inputFile != "" {
		loadedHosts, err := loadHostsFromFile(inputFile, port)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		hostsToMonitor = loadedHosts
	} else {
		hostsToMonitor = []string{net.JoinHostPort(host, port)}
	}

	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Checking %d host(s) for SSL certificate expiry...\n", len(hostsToMonitor))
	}

	resultsChan := make(chan CertCheckResult, len(hostsToMonitor))
	timeoutDuration := time.Duration(timeoutSec) * time.Second

	for _, target := range hostsToMonitor {
		go func(t string) {
			resultsChan <- checkCertExpiry(t, timeoutDuration, warnDays)
		}(target)
		time.Sleep(200 * time.Millisecond) // Introduce a small delay
	}

	var certCheckResults []CertCheckResult
	for i := 0; i < len(hostsToMonitor); i++ {
		certCheckResults = append(certCheckResults, <-resultsChan)
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

	writeReport(certCheckResults, output)

	if verboseMode {
		fmt.Fprintln(os.Stderr, "[INFO] SSL certificate expiry check complete.")
	}
	os.Exit(0)
}
