package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// Global variables for CLI flags
var (
	createBaselineFile string
	verifyBaselineFile string
	pathArg            string
	inputFile          string
	outputFile         string
	verboseMode        bool
)

// Baseline represents a collection of file paths to hashes
type Baseline map[string]string

// ReportEntry stores the result of an integrity check
type ReportEntry struct {
	Path        string `json:"path"`
	Status      string `json:"status"` // e.g., "OK", "MODIFIED", "ADDED", "DELETED", "MISSING"
	OldHash     string `json:"old_hash,omitempty"`
	NewHash     string `json:"new_hash,omitempty"`
	Message     string `json:"message,omitempty"`
}
func init() {
	flag.StringVar(&createBaselineFile, "create-baseline", "", "Path to a JSON file to save the baseline hashes.")
	flag.StringVar(&verifyBaselineFile, "verify-baseline", "", "Path to a JSON baseline file to compare against.")
	flag.StringVar(&pathArg, "path", ".", "Directory to monitor. Defaults to current directory if -i is not used.")
	flag.StringVar(&inputFile, "i", "", "Path to a file containing a list of files/directories to monitor (one path per line).")
	flag.StringVar(&outputFile, "o", "", "Path to save the verification report. If not provided, prints to stdout.")
	flag.BoolVar(&verboseMode, "v", false, "Enable verbose output.")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [--create-baseline BASLINE_FILE | --verify-baseline BASELINE_FILE] [--path DIR | -i INPUT_FILE] [-o OUTPUT_FILE] [-v]\n", os.Args[0])
		fmt.Fprintln(os.Stderr, "  Generates/verifies cryptographic hashes for files. See default flags below.")
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

// calculateSHA256Hash calculates the SHA256 hash of a file.
func calculateSHA256Hash(filePath string) (string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return "", fmt.Errorf("failed to open file %s: %w", filePath, err)
	}
	defer file.Close()

	hasher := sha256.New()
	if _, err := io.Copy(hasher, file); err != nil {
		return "", fmt.Errorf("failed to hash file %s: %w", filePath, err)
	}
	return hex.EncodeToString(hasher.Sum(nil)), nil
}

// collectFiles collects paths of files to monitor.
// It returns only existing files if baseDir is used for relative path resolution.
func collectFiles(rootPath string, inputPaths []string, baseDir string) ([]string, error) {
	var files []string
	if len(inputPaths) > 0 {
		for _, p := range inputPaths {
			resolvedPath := p
			if baseDir != "" && !filepath.IsAbs(p) {
				resolvedPath = filepath.Join(baseDir, p)
			}
			absPath, err := filepath.Abs(resolvedPath)
			if err != nil {
				return nil, fmt.Errorf("failed to get absolute path for %s (original: %s): %w", resolvedPath, p, err)
			}
			info, err := os.Stat(absPath)
			if err != nil {
				
				return nil, fmt.Errorf("failed to stat path %s: %w", absPath, err)
			}
			if info.IsDir() {
				err := filepath.Walk(absPath, func(path string, info os.FileInfo, err error) error {
					if err != nil {
						return err
					}
					if !info.IsDir() {
						files = append(files, path)
					}
					return nil
				})
				if err != nil {
					return nil, fmt.Errorf("failed to walk directory %s: %w", absPath, err)
				}
			} else {
				files = append(files, absPath)
			}
		}
	} else { // No input file, walk the specified root path
		err := filepath.Walk(rootPath, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() {
				files = append(files, path)
			}
			return nil
		})
		if err != nil {
			return nil, fmt.Errorf("failed to walk directory %s: %w", rootPath, err)
		}
	}
	return files, nil
}

// createBaseline generates a new baseline.
func createBaseline(targetPaths []string, baselineFilePath string) error {
	baseline := make(Baseline)
	for _, filePath := range targetPaths {
		hash, err := calculateSHA256Hash(filePath)
		if err != nil {
			// This should not happen if collectFiles only returns existing files,
			// but as a safeguard.

			return fmt.Errorf("failed to hash %s: %w", filePath, err)
		}
		baseline[filePath] = hash
	}
	data, err := json.MarshalIndent(baseline, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal baseline to JSON: %w", err)
	}
	if err = os.WriteFile(baselineFilePath, data, 0644); err != nil {
		return fmt.Errorf("failed to write baseline file %s: %w", baselineFilePath, err)
	}

	return nil
}

// verifyBaseline compares current file hashes against a loaded baseline.
func verifyBaseline(baselineFilePath string, targetPaths []string) ([]ReportEntry, error) {
	var oldBaseline Baseline
	baselineData, err := os.ReadFile(baselineFilePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read baseline file %s: %w", baselineFilePath, err)
	}
	if err = json.Unmarshal(baselineData, &oldBaseline); err != nil {
		return nil, fmt.Errorf("failed to unmarshal baseline JSON from %s: %w", baselineFilePath, err)
	}

	report := []ReportEntry{}
	currentHashes := make(Baseline) // Map to store current hashes for comparison

	// Calculate current hashes for existing files
	for _, filePath := range targetPaths {
		hash, err := calculateSHA256Hash(filePath)
		if err != nil {
			if os.IsNotExist(err) { // Should not happen if collectFiles works correctly
				continue
			}
			return nil, fmt.Errorf("failed to hash %s during verification: %w", filePath, err)
		}
		currentHashes[filePath] = hash
	}

	// Compare old baseline with current state
	for oldPath, oldHash := range oldBaseline {
		if newHash, exists := currentHashes[oldPath]; exists {
			if oldHash != newHash {
				report = append(report, ReportEntry{
					Path:    oldPath,
					Status:  "MODIFIED",
					OldHash: oldHash,
					NewHash: newHash,
					Message: "Hash mismatch",
				})
			} else {
				report = append(report, ReportEntry{
					Path:   oldPath,
					Status: "OK",
				})
			}
		} else {
			report = append(report, ReportEntry{
					Path:    oldPath,
					Status:  "DELETED",
					OldHash: oldHash,
					Message: "File deleted",
				})
		}
	}

	// Check for newly ADDED files (present in current scan but not in old baseline)
	for newPath, newHash := range currentHashes {
		if _, exists := oldBaseline[newPath]; !exists {
			report = append(report, ReportEntry{
					Path:    newPath,
					Status:  "ADDED",
					NewHash: newHash,
					Message: "New file added",
				})
		}
	}

	return report, nil
}

// writeVerificationReport outputs the integrity report.
func writeVerificationReport(report []ReportEntry, output *os.File) {
	fmt.Fprintf(output, "--- File Integrity Monitor Report ---\n\n")
	if len(report) == 0 {
		fmt.Fprintln(output, "No integrity changes detected.")
		return
	}

	for _, entry := range report {
		fmt.Fprintf(output, "Path: %s\n", entry.Path)
		fmt.Fprintf(output, "Status: %s\n", entry.Status)
		if entry.OldHash != "" {
			fmt.Fprintf(output, "Old Hash: %s\n", entry.OldHash)
		}
		if entry.NewHash != "" {
			fmt.Fprintf(output, "New Hash: %s\n", entry.NewHash)
		}
		if entry.Message != "" {
			fmt.Fprintf(output, "Message: %s\n", entry.Message)
		}
		fmt.Fprintln(output, "------------------------------")
	}
}

func main() {
	flag.Parse()

	// Validate argument combinations
	if createBaselineFile != "" && verifyBaselineFile != "" {
		fatalError("Cannot use --create-baseline and --verify-baseline simultaneously.", nil)
	}
	if createBaselineFile == "" && verifyBaselineFile == "" {
		flag.Usage()
		fatalError("Either --create-baseline or --verify-baseline must be specified.", nil)
	}

	var inputPaths []string
	var inputDir string // New variable to store the directory of the input file
	if inputFile != "" {
		file, err := os.Open(inputFile)
		if err != nil {
			fatalError(fmt.Sprintf("Failed to open input file %s", inputFile), err)
		}
		defer file.Close()
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			line := filepath.Clean(scanner.Text())
			if line != "" {
				inputPaths = append(inputPaths, line)
			}
		}
		if err := scanner.Err(); err != nil {
			fatalError(fmt.Sprintf("Error reading input file %s", inputFile), err)
		}
		inputDir = filepath.Dir(inputFile) // Get the directory of the input file
	}

	// Prepare output stream
	output := os.Stdout
	if outputFile != "" {
		var err error
		output, err = os.Create(outputFile)
		if err != nil {
			fatalError(fmt.Sprintf("Failed to create output file %s", outputFile), err)
		}
		defer output.Close()
	}

	// Collect files based on pathArg or inputFile
	targetFiles, err := collectFiles(pathArg, inputPaths, inputDir)
	if err != nil {
		fatalError("Failed to collect files", err)
	}



	if createBaselineFile != "" {

		err := createBaseline(targetFiles, createBaselineFile)
		if err != nil {
			fatalError("Failed to create baseline", err)
		}
	} else if verifyBaselineFile != "" {

		report, err := verifyBaseline(verifyBaselineFile, targetFiles)
		if err != nil {
			fatalError("Failed to verify baseline", err)
		}
		writeVerificationReport(report, output)
	}


	os.Exit(0)
}
