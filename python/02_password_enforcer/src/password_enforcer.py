#!/usr/bin/env python3
"""
SECURITY PORTFOLIO ARTIFACT - DEMONSTRATION ONLY

CONTEXT: This code is a frozen demonstration of a password policy enforcer.
PURPOSE: Show skill in string manipulation, policy enforcement, and input validation.
CONSTRAINTS: <=300 lines, no external dependencies (intentional).
STATUS: Complete demonstration - no updates planned.
EVALUATION: Assess what this demonstrates, not production readiness.
"""

import argparse
import sys
import re
from pathlib import Path

# --- Configuration ---
# Default password policy for demonstration purposes.
DEFAULT_POLICY = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True,
}

# --- Core Functions ---

def check_password_strength(password: str, policy: dict) -> list:
    """
    Evaluates a single password against the defined policy.
    Returns a list of policy violations.
    """
    violations = []

    # Check minimum length
    if len(password) < policy['min_length']:
        violations.append(f"Minimum length of {policy['min_length']} characters not met.")

    # Check for required character types
    if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
        violations.append("Missing uppercase character.")
    if policy['require_lowercase'] and not re.search(r'[a-z]', password):
        violations.append("Missing lowercase character.")
    if policy['require_digit'] and not re.search(r'\d', password):
        violations.append("Missing digit.")
    if policy['require_special'] and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]', password):
        violations.append("Missing special character.")

    return violations

def enforce_policy_on_file(input_path: Path, output_path: Path, policy: dict, verbose: bool):
    """
    Reads passwords from an input file, checks them against the policy,
    and writes a compliance report.
    """
    if verbose:
        print(f"[INFO] Reading passwords from: {input_path}")
        print(f"[INFO] Applying policy: Min Length={policy['min_length']}, U/L/D/S={'Yes' if policy['require_uppercase'] else 'No'}/{'Yes' if policy['require_lowercase'] else 'No'}/{'Yes' if policy['require_digit'] else 'No'}/{'Yes' if policy['require_special'] else 'No'}")

    results = []
    total_passwords = 0
    non_compliant_count = 0
    try:
        with input_path.open('r', encoding='utf-8') as infile:
            for line_num, line in enumerate(infile, 1):
                total_passwords += 1
                password = line.strip()
                if not password:
                    continue # Skip empty lines

                violations = check_password_strength(password, policy)
                status = "COMPLIANT" if not violations else "NON-COMPLIANT"
                if status == "NON-COMPLIANT":
                    non_compliant_count += 1
                
                results.append({
                    'password': password,
                    'status': status,
                    'violations': "; ".join(violations) if violations else "N/A",
                    'line_num': line_num
                })

    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"[ERROR] An error occurred while reading passwords: {e}", file=sys.stderr)
        return 0

    if verbose:
        compliant_count = sum(1 for r in results if r['status'] == 'COMPLIANT')
        print(f"[INFO] Processed {total_passwords} passwords: {compliant_count} COMPLIANT, {total_passwords - compliant_count} NON-COMPLIANT.")

    try:
        with output_path.open('w', encoding='utf-8') as outfile:
            outfile.write("--- Password Policy Enforcement Report ---\n\n")
            for result in results:
                outfile.write(f"Password: {result['password']}\n")
                outfile.write(f"Status: {result['status']}\n")
                if result['violations'] != "N/A":
                    outfile.write(f"Violations: {result['violations']}\n")
                outfile.write(f"Line: {result['line_num']}\n")
                outfile.write("-" * 30 + "\n")
        if verbose:
            print(f"[INFO] Report saved to: {output_path}")
    except Exception as e:
        print(f"[ERROR] An error occurred while writing the report: {e}", file=sys.stderr)
        return 0
    
    return results, total_passwords, non_compliant_count

# --- Main Execution ---

def main():
    """
    Main function to parse arguments and orchestrate password policy enforcement.
    """
    parser = argparse.ArgumentParser(
        description="A demonstration tool to enforce basic password policies on a list of passwords.",
        epilog="This is a proof-of-concept for a security portfolio and is not intended for production use."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        type=Path,
        help="Path to the input file containing passwords (one per line)."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        type=Path,
        help="Path to save the password policy enforcement report."
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=DEFAULT_POLICY['min_length'],
        help=f"Minimum password length (default: {DEFAULT_POLICY['min_length']})."
    )
    parser.add_argument(
        "--no-upper",
        action="store_true",
        help="Do not require uppercase characters."
    )
    parser.add_argument(
        "--no-lower",
        action="store_true",
        help="Do not require lowercase characters."
    )
    parser.add_argument(
        "--no-digit",
        action="store_true",
        help="Do not require digits."
    )
    parser.add_argument(
        "--no-special",
        action="store_true",
        help="Do not require special characters."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output to show processing details."
    )
    args = parser.parse_args()

    # Update policy based on CLI arguments
    policy = DEFAULT_POLICY.copy()
    policy['min_length'] = args.min_length
    policy['require_uppercase'] = not args.no_upper
    policy['require_lowercase'] = not args.no_lower
    policy['require_digit'] = not args.no_digit
    policy['require_special'] = not args.no_special

    # Ensure output directory exists
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Could not create output directory: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print("--- Password Policy Enforcer ---")

    all_results, total_passwords_processed, non_compliant_count = enforce_policy_on_file(args.input, args.output, policy, args.verbose)

    if args.verbose:
        print(f"--- Process Complete. {total_passwords_processed} passwords processed. ---")

    if total_passwords_processed > 0 and non_compliant_count > 0:
        sys.exit(1) # Indicate some passwords were non-compliant
    sys.exit(0) # All processed and all compliant (or no passwords processed)

if __name__ == "__main__":
    main()
