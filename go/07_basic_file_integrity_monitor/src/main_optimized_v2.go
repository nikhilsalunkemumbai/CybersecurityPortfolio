package main

/*
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of a basic file integrity monitor.
PURPOSE: Show skill in file system interaction, cryptographic hashing, JSON serialization, and CLI utility development in Go.
CONSTRAINTS: Uses standard library only, designed for CLI, <=300 lines (intentional, achieved through optimization).
STATUS: Complete demonstration - no updates planned.
EVALUATION: Assess what this demonstrates, not production readiness.
*/

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
	createB, verifyB, pathArg, inputFile, outputFile string
	verbose                                           bool
)

// Baseline stores file paths and their corresponding SHA256 hashes.
type Baseline map[string]string

// Report represents an integrity check finding.
type Report struct {
	Path, Status, OldHash, NewHash, Message string
}

// hashFile computes the SHA256 hash of a given file.
func hashFile(p string) (string, error) {
	f, err := os.Open(p)
	if err != nil {
		return "", err
	}
	defer f.Close()
	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

// collectFiles recursively gathers files from a given root path or a list,
// resolving relative paths against a base directory.
func collectFiles(root string, list []string, base string) ([]string, error) {
	var files []string
	addFile := func(p string) error {
		abs, err := filepath.Abs(p)
		if err != nil {
			return err
		}
		info, err := os.Stat(abs)
		if err != nil {
			if os.IsNotExist(err) {
				if verbose {
					fmt.Fprintln(os.Stderr, "[INFO] Missing:", abs)
				}
				return nil
			}
			return err
		}
		if info.IsDir() {
			return filepath.Walk(abs, func(p string, i os.FileInfo, e error) error {
				if e == nil && !i.IsDir() {
					files = append(files, p)
				}
				return e
			})
		}
		files = append(files, abs)
		return nil
	}

	if len(list) > 0 {
		for _, p := range list {
			if base != "" && !filepath.IsAbs(p) {
				p = filepath.Join(base, p)
			}
			if err := addFile(p); err != nil {
				return nil, err
			}
		}
	} else {
		if err := addFile(root); err != nil {
			return nil, err
		}
	}
	return files, nil
}

// createBaseline generates a new baseline file (JSON) with hashes of the given files.
func createBaseline(files []string, out string) error {
	b := Baseline{}
	for _, f := range files {
		h, err := hashFile(f)
		if err == nil {
			b[f] = h
		}
	}
	data, _ := json.MarshalIndent(b, "  ", "  ")
	return os.WriteFile(out, data, 0644)
}

// verifyBaseline compares current file hashes against a previously saved baseline.
func verifyBaseline(bfile string, files []string) ([]Report, error) {
	data, err := os.ReadFile(bfile)
	if err != nil {
		return nil, err
	}
	var base Baseline
	json.Unmarshal(data, &base)

	found := map[string]bool{}
	var r []Report

	for _, f := range files {
		found[f] = true
		h, err := hashFile(f)
		if err != nil {
			if old, ok := base[f]; ok {
				r = append(r, Report{f, "DELETED", old, "", "File deleted"})
			}
			continue
		}
		if old, ok := base[f]; ok {
			if old != h {
				r = append(r, Report{f, "MODIFIED", old, h, "Hash mismatch"})
			} else {
				r = append(r, Report{f, "OK", old, "", ""})
			}
		} else {
			r = append(r, Report{f, "ADDED", "", h, "New file"})
		}
	}

	for f, h := range base {
		if !found[f] {
			r = append(r, Report{f, "DELETED", h, "", "File deleted"})
		}
	}
	return r, nil
}

// writeReport writes the integrity report to the specified writer.
func writeReport(r []Report, w io.Writer) {
	fmt.Fprintln(w, "--- File Integrity Report ---")
	for _, e := range r {
		fmt.Fprintf(w, "\nPath: %s\nStatus: %s\n", e.Path, e.Status)
		if e.OldHash != "" {
			fmt.Fprintln(w, "Old:", e.OldHash)
		}
		if e.NewHash != "" {
			fmt.Fprintln(w, "New:", e.NewHash)
		}
		if e.Message != "" {
			fmt.Fprintln(w, "Msg:", e.Message)
		}
	}
}

// main is the entry point of the Basic File Integrity Monitor tool.
func main() {
	flag.StringVar(&createB, "create-baseline", "", "Path to output baseline file. Creates a new baseline.")
	flag.StringVar(&verifyB, "verify-baseline", "", "Path to existing baseline file. Verifies against this baseline.")
	flag.StringVar(&pathArg, "path", ".", "Path to a file or directory to monitor. Used if -i is not specified.")
	flag.StringVar(&inputFile, "i", "", "Path to a file listing files/directories to monitor (one per line).")
	flag.StringVar(&outputFile, "o", "", "Path to save the report. Prints to stdout if not specified.")
	flag.BoolVar(&verbose, "v", false, "Enable verbose output.")
	flag.Parse()

	if (createB == "") == (verifyB == "") {
		fmt.Fprintln(os.Stderr, "[ERROR] Specify exactly one of --create-baseline or --verify-baseline")
		os.Exit(1)
	}

	var list []string
	baseDir := ""
	if inputFile != "" {
		f, err := os.Open(inputFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to open input file %s: %v\n", inputFile, err)
			os.Exit(1)
		}
		sc := bufio.NewScanner(f)
		for sc.Scan() {
			list = append(list, filepath.Clean(sc.Text()))
		}
		f.Close()
		baseDir = filepath.Dir(inputFile)
	}

	out := os.Stdout
	if outputFile != "" {
		var err error
		out, err = os.Create(outputFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to create output file %s: %v\n", outputFile, err)
			os.Exit(1)
		}
		defer out.Close()
	}

	files, err := collectFiles(pathArg, list, baseDir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "[ERROR] Failed to collect files: %v\n", err)
		os.Exit(1)
	}

	if createB != "" {
		if verbose {
			fmt.Fprintln(os.Stderr, "[INFO] Creating baseline...")
		}
		if err := createBaseline(files, createB); err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to create baseline: %v\n", err)
			os.Exit(1)
		}
		if verbose {
			fmt.Fprintf(os.Stderr, "[INFO] Baseline created at %s\n", createB)
		}
	} else {
		if verbose {
			fmt.Fprintln(os.Stderr, "[INFO] Verifying against baseline...")
		}
		r, err := verifyBaseline(verifyB, files)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[ERROR] Failed to verify baseline: %v\n", err)
			os.Exit(1)
		}
		writeReport(r, out)
		if verbose {
			fmt.Fprintln(os.Stderr, "[INFO] Verification complete.")
		}
		// Exit with non-zero if changes were detected
		if len(r) > 0 {
			os.Exit(1)
		}
	}
	os.Exit(0)
}
