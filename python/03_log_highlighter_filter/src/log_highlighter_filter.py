#!/usr/bin/env python3
"""
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of a log highlighter and filter tool.
PURPOSE: Show skill in text processing, regular expressions, and CLI utility development.
CONSTRAINTS: <=300 lines, no external dependencies (intentional).
STATUS: In-Progress - Implementation.
EVALUATION: Assess what this demonstrates, not production readiness.
"""

import argparse
import sys
import re

# --- Configuration ---
# ANSI escape codes for coloring output
# Reset all attributes
RESET = "\033[0m"
# Text colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# A rotating list of colors for keywords
KEYWORD_COLORS = [YELLOW, CYAN, MAGENTA, GREEN, BLUE, RED]

# --- Core Functions ---

def apply_highlighting(line: str, keywords: list, case_sensitive: bool) -> str:
    """
    Applies highlighting to keywords in a given line using ANSI escape codes.
    """
    modified_line = line
    flags = 0 if case_sensitive else re.IGNORECASE
    
    for i, keyword in enumerate(keywords):
        color = KEYWORD_COLORS[i % len(KEYWORD_COLORS)]
        # Use regex to find and replace all occurrences of the keyword
        # Escape special characters in the keyword
        escaped_keyword = re.escape(keyword)
        modified_line = re.sub(f'({escaped_keyword})', f'{color}\1{RESET}', modified_line, flags=flags)
    return modified_line

def should_process_line(line: str, includes: list, excludes: list, case_sensitive: bool) -> bool:
    """
    Determines if a line should be processed based on include and exclude regex patterns.
    """
    flags = 0 if case_sensitive else re.IGNORECASE

    # Check exclude patterns first
    for exclude_pattern in excludes:
        if re.search(exclude_pattern, line, flags=flags):
            return False # Exclude if any exclude pattern matches

    # If no include patterns are specified, include by default
    if not includes:
        return True

    # Check include patterns
    for include_pattern in includes:
        if re.search(include_pattern, line, flags=flags):
            return True # Include if any include pattern matches

    return False # Exclude if no include pattern matches (and includes list is not empty)

def process_log_stream(infile, outfile, args):
    """
    Reads from infile, processes each line, and writes to outfile.
    """
    if args.verbose:
        print("[INFO] Starting log processing...", file=sys.stderr)

    line_count = 0
    processed_count = 0
    try:
        for line in infile:
            line_count += 1
            if should_process_line(line, args.include, args.exclude, args.case_sensitive):
                processed_line = apply_highlighting(line.strip(), args.keywords, args.case_sensitive)
                outfile.write(processed_line + '\n')
                processed_count += 1
    except Exception as e:
        print(f"[ERROR] An error occurred during processing: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"[INFO] Processed {line_count} lines, wrote {processed_count} lines to output.", file=sys.stderr)
        print("[INFO] Log processing complete.", file=sys.stderr)

# --- Main Execution ---

def main():
    """
    Main function to parse arguments and orchestrate the log processing.
    """
    parser = argparse.ArgumentParser(
        description="A demonstration tool to highlight and filter log files.",
        epilog="This is a proof-of-concept for a security portfolio and is not intended for production use."
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Path to the input log file. Reads from stdin if not specified."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path to the output file. Writes to stdout if not specified."
    )
    parser.add_argument(
        "-k", "--keywords",
        nargs='*',
        default=[],
        help="List of keywords to highlight in the output. Case-insensitive by default."
    )
    parser.add_argument(
        "--include",
        nargs='*',
        default=[],
        help="Regular expression pattern(s) to include lines. Only lines matching any pattern will be processed."
    )
    parser.add_argument(
        "--exclude",
        nargs='*',
        default=[],
        help="Regular expression pattern(s) to exclude lines. Lines matching any pattern will be ignored."
    )
    parser.add_argument(
        "-c", "--case-sensitive",
        action="store_true",
        help="Perform case-sensitive matching for keywords and patterns."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output to show processing details to stderr."
    )
    args = parser.parse_args()

    # Determine input and output streams
    infile = sys.stdin
    outfile = sys.stdout

    if args.input:
        try:
            infile = open(args.input, 'r', encoding='utf-8')
        except FileNotFoundError:
            print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Could not open input file {args.input}: {e}", file=sys.stderr)
            sys.exit(1)

    if args.output:
        try:
            outfile = open(args.output, 'w', encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Could not open output file {args.output}: {e}", file=sys.stderr)
            if infile != sys.stdin:
                infile.close()
            sys.exit(1)

    try:
        process_log_stream(infile, outfile, args)
    finally:
        if infile != sys.stdin:
            infile.close()
        if outfile != sys.stdout:
            outfile.close()

if __name__ == "__main__":
    main()
