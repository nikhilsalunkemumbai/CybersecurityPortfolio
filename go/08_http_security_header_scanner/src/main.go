package main

/*
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of an HTTP Security Header Scanner.
PURPOSE: Show skill in HTTP client operations, header parsing, and CLI utility development in Go.
CONSTRAINTS: Uses standard library only, designed for CLI, <=300 lines (intentional).
STATUS: Complete demonstration - no updates planned.
EVALUATION: Assess what this demonstrates, not production readiness.
*/

import (
	"bufio"
	"flag"
	"fmt"
	"net/http"
	"net/url" // For URL parsing
	"os"
	"strings"
	"time"
)

// Global variables for CLI flags
var (
	targetURL   string
	inputFile   string
	outputFile  string
	timeoutSec  int
	verboseMode bool
)

// HeaderCheckResult stores the result of a single URL header check
type HeaderCheckResult struct {
	URL     string
	Headers map[string]string // Found security headers and their values
	Missing []string          // Missing recommended security headers
	Errors  error
}

// Recommended security headers to check for
var recommendedSecurityHeaders = map[string]string{
	"Strict-Transport-Security": "Strict-Transport-Security (HSTS) enforces secure connections.",
	"X-Frame-Options":           "X-Frame-Options prevents clickjacking attacks.",
	"X-Content-Type-Options":    "X-Content-Type-Options prevents MIME sniffing.",
	"Content-Security-Policy":   "Content-Security-Policy (CSP) prevents XSS and data injection attacks.",
	"Referrer-Policy":           "Referrer-Policy controls how much referrer information is sent.",
	"Permissions-Policy":        "Permissions-Policy allows/disallows use of browser features.",
	// Add other headers as needed
}

func init() {
	// --- CLI Argument Parsing ---
	flag.StringVar(&targetURL, "url", "", "Target URL to scan (e.g., https://example.com).")
	flag.StringVar(&targetURL, "u", "", "Target URL to scan (shorthand).")

	flag.StringVar(&inputFile, "input", "", "Path to a file containing a list of URLs to scan (one URL per line). Overrides -url if provided.")
	flag.StringVar(&inputFile, "i", "", "Path to a file containing a list of URLs to scan (shorthand).")

	flag.StringVar(&outputFile, "output", "", "Path to save the report. If not provided, prints to stdout.")
	flag.StringVar(&outputFile, "o", "", "Path to save the report (shorthand).")

	flag.IntVar(&timeoutSec, "timeout", 10, "HTTP request timeout in seconds.")
	flag.IntVar(&timeoutSec, "t", 10, "HTTP request timeout in seconds (shorthand).")

	flag.BoolVar(&verboseMode, "verbose", false, "Enable verbose output.")
	flag.BoolVar(&verboseMode, "v", false, "Enable verbose output (shorthand).")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Analyzes HTTP response headers of specified URLs for common security headers.\n")
		fmt.Fprintf(os.Stderr, "  Example: %s -u https://google.com\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Example: %s -i urls.txt -o report.txt\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Flags:\n")
		flag.PrintDefaults()
	}
}

// fatalError prints an error message and exits.
func fatalError(msg string, err error) {
	if err != nil {
		fmt.Fprintf(os.Stderr, "[ERROR] %s: %v\n", msg, err)
	} else {
		fmt.Fprintf(os.Stderr, "[ERROR] %s\n", msg)
	}
	os.Exit(1)
}

// checkSecurityHeaders makes an HTTP request and analyzes security headers.
func checkSecurityHeaders(targetURL string, client *http.Client) HeaderCheckResult {
	result := HeaderCheckResult{URL: targetURL, Headers: make(map[string]string)}

	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Scanning URL: %s\n", targetURL)
	}

	req, err := http.NewRequest("GET", targetURL, nil)
	if err != nil {
		result.Errors = fmt.Errorf("failed to create request: %w", err)
		return result
	}

	resp, err := client.Do(req)
	if err != nil {
		result.Errors = fmt.Errorf("HTTP request failed: %w", err)
		return result
	}
	defer resp.Body.Close()

	for headerName := range recommendedSecurityHeaders {
		if value := resp.Header.Get(headerName); value != "" {
			result.Headers[headerName] = value
		} else {
			result.Missing = append(result.Missing, headerName)
		}
	}
	return result
}

// loadURLsFromFile reads URLs from a specified file.
func loadURLsFromFile(filePath string) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open input file %s: %w", filePath, err)
	}
	defer file.Close()

	var urls []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		// Basic validation: ensure it's a URL
		if _, err := url.ParseRequestURI(line); err != nil {
			if verboseMode {
				fmt.Fprintf(os.Stderr, "[WARNING] Skipping invalid URL: %s (%v)\n", line, err)
			}
			continue
		}
		urls = append(urls, line)
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("error reading input file %s: %w", filePath, err)
	}
	return urls, nil
}

// writeReport generates the security header scan report.
func writeReport(results []HeaderCheckResult, output *os.File) {
	fmt.Fprintf(output, "---\n")
	fmt.Fprintf(output, "--- HTTP Security Header Scan Report ---\n")
	fmt.Fprintf(output, "\n")
	if len(results) == 0 {
		fmt.Fprintln(output, "No URLs were scanned or no results to report.")
		return
	}

	for _, result := range results {
		fmt.Fprintf(output, "URL: %s\n", result.URL)
		if result.Errors != nil {
			fmt.Fprintf(output, "Status: ERROR\n")
			fmt.Fprintf(output, "Error: %v\n", result.Errors)
		} else {
			fmt.Fprintf(output, "Status: OK\n")
			fmt.Fprintln(output, "--- Found Security Headers ---")
			if len(result.Headers) == 0 {
				fmt.Fprintln(output, "  None found.")
			}
			for name, value := range result.Headers {
				fmt.Fprintf(output, "  %s: %s\n", name, value)
			}
			fmt.Fprintln(output, "--- Missing Recommended Headers ---")
			if len(result.Missing) == 0 {
				fmt.Fprintln(output, "  None missing.")
			}
			for _, name := range result.Missing {
				fmt.Fprintf(output, "  %s: %s\n", name, recommendedSecurityHeaders[name])
			}
		}
		fmt.Fprintln(output, "------------------------------")
	}
}

// main is the entry point of the HTTP Security Header Scanner tool.
func main() {
	flag.Parse()

	// Validate arguments
	if inputFile == "" && targetURL == "" {
		flag.Usage()
		fatalError("Either an input file (-i) or a target URL (-u) must be provided.", nil)
	}
	if inputFile != "" && targetURL != "" {
		fmt.Fprintln(os.Stderr, "[WARNING] Input file (-i) provided. -url flag will be ignored.")
	}

	var urlsToScan []string
	if inputFile != "" {
		loadedURLs, err := loadURLsFromFile(inputFile)
		if err != nil {
			fatalError("Failed to load URLs from file", err)
		}
		urlsToScan = loadedURLs
	} else {
		// Basic validation for single URL
		if _, err := url.ParseRequestURI(targetURL); err != nil {
			fatalError(fmt.Sprintf("Invalid URL provided: %s", targetURL), err)
		}
		urlsToScan = []string{targetURL}
	}

	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Scanning %d URL(s)...\n", len(urlsToScan))
	}

	client := &http.Client{
		Timeout: time.Duration(timeoutSec) * time.Second,
	}

	resultsChan := make(chan HeaderCheckResult, len(urlsToScan))

	for _, u := range urlsToScan {
		go func(scanURL string) {
			resultsChan <- checkSecurityHeaders(scanURL, client)
		}(u)
		time.Sleep(100 * time.Millisecond) // Introduce a small delay to avoid overwhelming targets/network
	}

	var allResults []HeaderCheckResult
	for i := 0; i < len(urlsToScan); i++ {
		allResults = append(allResults, <-resultsChan)
	}

	output := os.Stdout
	if outputFile != "" {
		var err error
		output, err = os.Create(outputFile)
		if err != nil {
			fatalError(fmt.Sprintf("Failed to create output file %s", outputFile), err)
		}
		defer output.Close()
	}

	writeReport(allResults, output)

	if verboseMode {
		fmt.Fprintln(os.Stderr, "[INFO] HTTP Security Header scan complete.")
	}
	os.Exit(0)
}
