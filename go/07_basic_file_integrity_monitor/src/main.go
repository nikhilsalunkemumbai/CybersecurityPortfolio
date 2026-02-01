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

// FileHash stores the path and SHA256 hash of a file
type FileHash struct {
	Path string `json:"path"`
	Hash string `json:"hash"`
}

// Baseline represents a collection of FileHashes
type Baseline map[string]string // Map of file path to hash

// ReportEntry stores the result of an integrity check
type ReportEntry struct {
	Path        string `json:"path"`
	Status      string `json:"status"` // e.g., "OK", "MODIFIED", "ADDED", "DELETED"
	OldHash     string `json:"old_hash,omitempty"`
	NewHash     string `json:"new_hash,omitempty"`
	Message     string `json:"message,omitempty"`
}

func init() {
	// --- CLI Argument Parsing ---
	flag.StringVar(&createBaselineFile, "create-baseline", "", "Path to a JSON file to save the baseline hashes.")
	flag.StringVar(&verifyBaselineFile, "verify-baseline", "", "Path to a JSON baseline file to compare against.")
	flag.StringVar(&pathArg, "path", ".", "Directory to monitor. Defaults to current directory if -i is not used.")

	flag.StringVar(&inputFile, "i", "", "Path to a file containing a list of files/directories to monitor (one path per line).")
	flag.StringVar(&outputFile, "o", "", "Path to save the verification report. If not provided, prints to stdout.")
	flag.BoolVar(&verboseMode, "v", false, "Enable verbose output.")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Generates and verifies cryptographic hashes for files to detect unauthorized modifications.\n")
		fmt.Fprintf(os.Stderr, "  Example (Create Baseline): %s --create-baseline baseline.json --path .\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Example (Verify Baseline): %s --verify-baseline baseline.json -i files_to_monitor.txt -o report.txt -v\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Flags:\n")
		flag.PrintDefaults()
	}
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

// collectFiles collects paths of files to monitor, resolving relative paths against baseDir if provided.
func collectFiles(rootPath string, inputPaths []string, baseDir string) ([]string, error) {
	var files []string
	if len(inputPaths) > 0 {
		for _, p := range inputPaths {
			var resolvedPath string
			if baseDir != "" && !filepath.IsAbs(p) {
				resolvedPath = filepath.Join(baseDir, p)
			} else {
				resolvedPath = p
			}
			
			absPath, err := filepath.Abs(resolvedPath) // Still use Abs to ensure full path
			if err != nil {
				return nil, fmt.Errorf("failed to get absolute path for %s (original: %s): %w", resolvedPath, p, err)
			}
			info, err := os.Stat(absPath)
			if err != nil {
				// If file doesn't exist, we skip it here. It will be detected as DELETED by verifyBaseline
				// if it was present in the baseline.
				if os.IsNotExist(err) {
					if verboseMode {
						fmt.Fprintf(os.Stderr, "[INFO] Skipping non-existent path from input for current scan: %s\n", absPath)
					}
					continue // Skip this path if it doesn't exist
				}
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
	} else {
		// If no input file, walk the specified root path
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
			// If file is not found, it will not be part of the baseline
			if os.IsNotExist(err) {
				if verboseMode {
					fmt.Fprintf(os.Stderr, "[INFO] Skipping non-existent file for baseline: %s\n", filePath)
				}
				continue
			}
			return fmt.Errorf("failed to hash %s: %w", filePath, err)
		}
		baseline[filePath] = hash
	}

	data, err := json.MarshalIndent(baseline, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal baseline to JSON: %w", err)
	}

	err = os.WriteFile(baselineFilePath, data, 0644)
	if err != nil {
		return fmt.Errorf("failed to write baseline file %s: %w", baselineFilePath, err)
	}

	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Baseline created at: %s with %d files.\n", baselineFilePath, len(baseline))
	}
	return nil
}

// verifyBaseline compares current file hashes against a loaded baseline.
func verifyBaseline(baselineFilePath string, targetPaths []string) ([]ReportEntry, error) {
	var currentBaseline Baseline
	baselineData, err := os.ReadFile(baselineFilePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read baseline file %s: %w", baselineFilePath, err)
	}
	if err := json.Unmarshal(baselineData, &currentBaseline); err != nil {
		return nil, fmt.Errorf("failed to unmarshal baseline JSON from %s: %w", baselineFilePath, err)
	}

	report := []ReportEntry{}
	currentFiles := make(map[string]struct{})

	for _, filePath := range targetPaths {
		currentFiles[filePath] = struct{}{}
		newHash, err := calculateSHA256Hash(filePath)
		if err != nil {
			if os.IsNotExist(err) {
				// If file is not found during verification, and it was in the baseline,
				// it means the file has been deleted. Report it and continue.
				if oldHash, exists := currentBaseline[filePath]; exists {
					report = append(report, ReportEntry{
						Path:    filePath,
						Status:  "DELETED",
						OldHash: oldHash,
						Message: "File deleted",
					})
					// Remove from currentFiles map so it's not double-counted later
					delete(currentFiles, filePath)
				} else {
					// File not found and not in baseline (e.g., a path in input file that never existed)
					report = append(report, ReportEntry{
						Path:    filePath,
						Status:  "MISSING",
						Message: "File specified for verification is missing and not in baseline",
					})
				}
				continue // IMPORTANT: Continue to the next file in targetPaths
			}
			// For any other error (e.g., permission denied), return the error
			return nil, fmt.Errorf("failed to hash %s during verification: %w", filePath, err)
		}

		if oldHash, exists := currentBaseline[filePath]; exists {
			if oldHash != newHash {
				report = append(report, ReportEntry{
					Path:    filePath,
					Status:  "MODIFIED",
					OldHash: oldHash,
					NewHash: newHash,
					Message: "Hash mismatch",
				})
			} else {
				report = append(report, ReportEntry{
					Path:   filePath,
					Status: "OK",
					OldHash: oldHash,
				})
			}
		} else {
			report = append(report, ReportEntry{
				Path:    filePath,
				Status:  "ADDED",
				NewHash: newHash,
				Message: "New file added",
			})
		}
	}

	// Check for DELETED files not present in current scan but in baseline
	for oldPath, oldHash := range currentBaseline {
		if _, exists := currentFiles[oldPath]; !exists {
			// This covers files that were deleted AND were part of the initial `targetPaths`
			// OR were part of the baseline but not explicitly passed in `targetPaths`
			// (e.g., if --path was used for verify and a file in that path was deleted).
			// For simplicity with `--path .` usage, we consider files implicitly.
			// However, if targetPaths was *explicitly* provided, and oldPath is not in targetPaths,
			// this indicates it was not meant to be scanned this time.
			// Given `--path .` as default, this is relevant.
			
			// Re-evaluating this logic to ensure it makes sense with how `collectFiles` works.
			// `collectFiles` only returns files that currently exist (or were from inputPaths).
			// So, if an oldPath from baseline is not in currentFiles, it means it's deleted.
			report = append(report, ReportEntry{
				Path:    oldPath,
				Status:  "DELETED",
				OldHash: oldHash,
				Message: "File deleted",
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
		fmt.Fprintln(os.Stderr, "[ERROR] Cannot use --create-baseline and --verify-baseline simultaneously.")
		os.Exit(1)
	}
	if createBaselineFile == "" && verifyBaselineFile == "" {
		flag.Usage()
		fmt.Fprintln(os.Stderr, "\n[ERROR] Either --create-baseline or --verify-baseline must be specified.")
		os.Exit(1)
	}

	var inputPaths []string
	var inputDir string // New variable to store the directory of the input file
	if inputFile != "" {
		file, err := os.Open(inputFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to open input file %s: %v\n", inputFile, err)
			os.Exit(1)
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
			fmt.Fprintf(os.Stderr, "[ERROR] Error reading input file %s: %v\n", inputFile, err)
			os.Exit(1)
		}
		inputDir = filepath.Dir(inputFile) // Get the directory of the input file
	}

	// Prepare output stream
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

	// Collect files based on pathArg or inputFile
	targetFiles, err := collectFiles(pathArg, inputPaths, inputDir) // Pass inputDir
	if err != nil {
		fmt.Fprintf(os.Stderr, "[ERROR] Failed to collect files: %v\v", err)
		os.Exit(1)
	}

	if verboseMode {
		fmt.Fprintf(os.Stderr, "[INFO] Collected %d files for processing.\n", len(targetFiles))
	}

	if createBaselineFile != "" {
		if verboseMode {
			fmt.Fprintln(os.Stderr, "[INFO] Creating baseline...")
		}
		err := createBaseline(targetFiles, createBaselineFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to create baseline: %v\n", err)
			os.Exit(1)
		}
	} else if verifyBaselineFile != "" {
		if verboseMode {
			fmt.Fprintln(os.Stderr, "[INFO] Verifying integrity...")
		}
		report, err := verifyBaseline(verifyBaselineFile, targetFiles)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to verify baseline: %v\n", err)
			os.Exit(1)
		}
		writeVerificationReport(report, output)
	}

	if verboseMode {
		fmt.Fprintln(os.Stderr, "[INFO] Integrity monitoring complete.")
	}
	os.Exit(0)
}
