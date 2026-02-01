#!/usr/bin/env python3
"""
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of security report cleaning.
PURPOSE: Show skill in data processing for security, not provide production utility.
CONSTRAINTS: <=300 lines, no external dependencies (intentional).
STATUS: Complete demonstration - no updates planned.
EVALUATION: Assess what this demonstrates, not production readiness.
"""

import argparse
import csv
import sys
from pathlib import Path

# --- Configuration ---
# Hardcoded patterns for demonstration purposes, avoiding external config files.
# This aligns with the "Simple one-time proof of concept" philosophy.
FALSE_POSITIVE_PATTERNS = [
    "informational",
    "low severity",
    "best practice",
    "pci compliance",
    "policy violation",
]

# --- Core Functions ---

def clean_csv_report(input_path: Path, output_path: Path, keep_medium: bool, verbose: bool):
    """
    Reads a vulnerability scan CSV, filters it, and writes a cleaned version.
    """
    if verbose:
        print(f"[INFO] Reading from: {input_path}")
        print(f"[INFO] Filtering out low-severity and informational findings.")
        if not keep_medium:
            print("[INFO] Filtering out medium-severity findings.")

    actionable_rows = []
    try:
        with input_path.open('r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            headers = reader.fieldnames
            if not headers:
                print("[ERROR] CSV file is empty or headers are missing.", file=sys.stderr)
                return 0

            for row in reader:
                if should_keep_row(row, keep_medium):
                    actionable_rows.append(row)

    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"[ERROR] An error occurred while reading the CSV: {e}", file=sys.stderr)
        return 0

    if verbose:
        print(f"[INFO] Found {len(actionable_rows)} actionable findings.")

    try:
        with output_path.open('w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(actionable_rows)
        if verbose:
            print(f"[INFO] Cleaned report saved to: {output_path}")
    except Exception as e:
        print(f"[ERROR] An error occurred while writing the CSV: {e}", file=sys.stderr)
        return 0

    return len(actionable_rows)

def should_keep_row(row: dict, keep_medium: bool) -> bool:
    """
    Determines if a row from the vulnerability report should be kept.
    This logic is intentionally simple for this proof-of-concept tool.
    """
    # Normalize column names for broader compatibility
    severity = row.get('Severity', row.get('severity', '')).lower()
    description = row.get('Description', row.get('description', '')).lower()
    plugin_name = row.get('Plugin Name', row.get('plugin_name', '')).lower()
    synopsis = row.get('Synopsis', row.get('synopsis', '')).lower()

    combined_text = f"{description} {plugin_name} {synopsis}"

    # Filter based on false positive patterns
    for pattern in FALSE_POSITIVE_PATTERNS:
        if pattern in combined_text:
            return False

    # Filter based on severity
    if severity in ["low", "info", "informational"]:
        return False

    if severity == "medium" and not keep_medium:
        return False

    return True

# --- Main Execution ---

def main():
    """
    Main function to parse arguments and orchestrate the cleaning process.
    """
    parser = argparse.ArgumentParser(
        description="A demonstration tool to clean CSV security reports by filtering out low-priority findings.",
        epilog="This is a proof-of-concept for a security portfolio and is not intended for production use."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        type=Path,
        help="Path to the input vulnerability scan CSV file."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        type=Path,
        help="Path to save the cleaned output CSV file."
    )
    parser.add_argument(
        "--keep-medium",
        action="store_true",
        help="If set, medium-severity findings will be kept in the output."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output to show processing details."
    )
    args = parser.parse_args()

    # Ensure output directory exists
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Could not create output directory: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print("--- CSV Security Report Cleaner ---")

    cleaned_count = clean_csv_report(args.input, args.output, args.keep_medium, args.verbose)

    if args.verbose:
        print(f"--- Process Complete. {cleaned_count} records written. ---")

if __name__ == "__main__":
    main()
