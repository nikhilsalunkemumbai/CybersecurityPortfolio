#!/usr/bin/env python3
"""
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of a quick IOC (Indicator of Compromise) checker.
PURPOSE: Show skill in file I/O, string matching, and CLI utility development.
CONSTRAINTS: <=300 lines, no external dependencies (intentional).
STATUS: In-Progress - Implementation.
EVALUATION: Assess what this demonstrates, not production readiness.
"""

import argparse
import sys
import re
from pathlib import Path

# --- Core Functions ---

def load_iocs(ioc_file_path: Path) -> set:
    """
    Loads Indicators of Compromise (IOCs) from a file, one per line.
    """
    iocs = set()
    try:
        with ioc_file_path.open('r', encoding='utf-8') as f:
            for line in f:
                ioc = line.strip()
                if ioc:
                    iocs.add(ioc)
    except FileNotFoundError:
        print(f"[ERROR] IOC file not found: {ioc_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An error occurred while loading IOCs from {ioc_file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    return iocs

def scan_target_file(target_file_path: Path, iocs: set, output_file, case_sensitive: bool, verbose: bool):
    """
    Scans a target file for the presence of loaded IOCs and writes a report.
    """
    matches_found = []
    flags = 0 if case_sensitive else re.IGNORECASE

    if verbose:
        print(f"[INFO] Scanning target file: {target_file_path}", file=sys.stderr)

    try:
        with target_file_path.open('r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for ioc in iocs:
                    if re.search(re.escape(ioc), line, flags=flags):
                        matches_found.append({
                            'ioc': ioc,
                            'line_num': line_num,
                            'line_content': line.strip()
                        })
                        if verbose:
                            print(f"[INFO] Found IOC '{ioc}' on line {line_num}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[ERROR] Target file not found: {target_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An error occurred while scanning {target_file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    write_report(matches_found, output_file)
    return len(matches_found)

def write_report(matches: list, output_file):
    """
    Writes the IOC scan report to the specified output file.
    """
    output_file.write("--- Quick IOC Checker Report ---\n\n")
    if not matches:
        output_file.write("No Indicators of Compromise found.\n")
        return

    for match in matches:
        output_file.write(f"IOC Found: {match['ioc']}\n")
        output_file.write(f"Line Number: {match['line_num']}\n")
        output_file.write(f"Line Content: {match['line_content']}\n")
        output_file.write("-" * 30 + "\n")

# --- Main Execution ---

def main():
    """
    Main function to parse arguments and orchestrate the IOC checking process.
    """
    parser = argparse.ArgumentParser(
        description="A demonstration tool for rapid detection of Indicators of Compromise (IOCs).",
        epilog="This is a proof-of-concept for a security portfolio and is not intended for production use."
    )
    parser.add_argument(
        "-i", "--iocs",
        required=True,
        type=Path,
        help="Path to a file containing Indicators of Compromise (one IOC per line)."
    )
    parser.add_argument(
        "-t", "--target",
        required=True,
        type=Path,
        help="Path to the target file to scan for IOCs."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Path to save the report of found IOCs. Prints to stdout if not specified."
    )
    parser.add_argument(
        "-c", "--case-sensitive",
        action="store_true",
        help="Perform case-sensitive matching for IOCs."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output to show processing details to stderr."
    )
    args = parser.parse_args()

    # Determine output stream
    output_stream = sys.stdout
    if args.output:
        try:
            output_stream = args.output.open('w', encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Could not open output file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)

    if args.verbose:
        print("--- Quick IOC Checker ---", file=sys.stderr)

    iocs_set = load_iocs(args.iocs)
    if args.verbose:
        print(f"[INFO] Loaded {len(iocs_set)} IOCs.", file=sys.stderr)

    matches_count = scan_target_file(args.target, iocs_set, output_stream, args.case_sensitive, args.verbose)

    if args.verbose:
        print(f"--- Process Complete. {matches_count} matches found. ---", file=sys.stderr)

    if output_stream != sys.stdout:
        output_stream.close()

    sys.exit(0)

if __name__ == "__main__":
    main()
