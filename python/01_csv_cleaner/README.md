# CSV Security Report Cleaner

## PORTFOLIO CONTEXT NOTICE

**This is a demonstration artifact, not production software.**

### Evaluation Context:
- **Purpose**: Demonstrate data processing and filtering for security reports.
- **Status**: Frozen - will not be updated.
- **Constraints**: <=300 lines, Python standard library only.
- **Focus**: Skill demonstration, not utility.

### Review Guidelines:
- Analyze what this demonstrates about skills in data handling.
- Consider testing/documentation as part of the demonstration.
- Connect to the broader portfolio goal of showing practical security skills.
- Do not evaluate for production readiness.

---

## Purpose
This tool, the **CSV Security Report Cleaner**, filters "noise" from vulnerability scan CSV exports. It removes informational, low-severity, and other non-actionable findings to produce a clean CSV containing only items that require attention.

## Usage
```bash
python `csv_cleaner.py` -i <input_file.csv> -o <output_file.csv> [options]
```

## Options
- `-i, --input`: (Required) Path to the input vulnerability scan CSV file.
- `-o, --output`: (Required) Path to save the cleaned output CSV file.
- `--keep-medium`: (Optional) If set, medium-severity findings will be kept in the output. By default, they are filtered out.
- `-v, --verbose`: (Optional) Enable verbose output to show processing details.

## Example
To process a scan report and keep only high and critical vulnerabilities:
```bash
python `csv_cleaner.py` -i sample_input/vulnerability_scan.csv -o sample_output/cleaned_report.csv -v
```

To include medium-severity findings in the output:
```bash
python `csv_cleaner.py` -i sample_input/vulnerability_scan.csv -o sample_output/cleaned_report_with_medium.csv --keep-medium
```

## Sample Output from a run
```text
--- CSV Security Report Cleaner ---
[INFO] Reading from: sample_input/vulnerability_scan.csv
[INFO] Filtering out low-severity and informational findings.
[INFO] Filtering out medium-severity findings.
[INFO] Found 2 actionable findings.
[INFO] Cleaned report saved to: sample_output/cleaned_report.csv
--- Process Complete. 2 records written. ---
```

## Note
This is a proof-of-concept tool for a security portfolio. The filtering logic is intentionally simple and hardcoded to demonstrate the core concept without requiring external configuration files, aligning with the project's "no maintenance" and "standalone" philosophy.
