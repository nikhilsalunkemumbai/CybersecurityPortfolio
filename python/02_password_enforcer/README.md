# Password Policy Enforcer

## PORTFOLIO CONTEXT NOTICE

**This is a demonstration artifact, not production software.**

### Evaluation Context:
- **Purpose**: Demonstrate password policy enforcement and validation.
- **Status**: Frozen - will not be updated.
- **Constraints**: <=300 lines, Python standard library only.
- **Focus**: Skill demonstration, not utility.

### Review Guidelines:
- Analyze what this demonstrates about skills in string manipulation, regex, and policy application.
- Consider testing/documentation as part of the demonstration.
- Connect to the broader portfolio goal of showing practical security skills.
- Do not evaluate for production readiness.

---

## Purpose
The **Password Policy Enforcer** is a tool designed to validate a list of passwords against a defined policy (e.g., minimum length, required character types). It reports which passwords are compliant and which violate the policy, providing specific reasons for non-compliance.

## Usage
```bash
python `password_enforcer.py` -i <input_file.txt> -o <output_report.txt> [options]
```

## Options
- `-i, --input`: (Required) Path to the input file containing passwords (one per line).
- `-o, --output`: (Required) Path to save the password policy enforcement report.
- `--min-length`: (Optional) Minimum password length (default: 8).
- `--no-upper`: (Optional) Do not require uppercase characters.
- `--no-lower`: (Optional) Do not require lowercase characters.
- `--no-digit`: (Optional) Do not require digits.
- `--no-special`: (Optional) Do not require special characters.
- `-v, --verbose`: (Optional) Enable verbose output to show processing details.

## Example
To enforce a policy requiring a minimum length of 10, with at least one uppercase, lowercase, digit, and special character:
```bash
python `password_enforcer.py` -i sample_input/passwords.txt -o sample_output/policy_report.txt --min-length 10 -v
```

To enforce a policy requiring only a minimum length of 6, without other character type requirements:
```bash
python `password_enforcer.py` -i sample_input/passwords.txt -o sample_output/simple_policy_report.txt --min-length 6 --no-upper --no-lower --no-digit --no-special
```

## Sample Output from a run (policy: min_length=8, requires all character types)
```text
--- Password Policy Enforcer ---
[INFO] Reading passwords from: sample_input\passwords.txt
[INFO] Applying policy: Min Length=8, U/L/D/S=Yes/Yes/Yes/Yes
[INFO] Processed 5 passwords: 1 COMPLIANT, 4 NON-COMPLIANT.
[INFO] Report saved to: sample_output\policy_report.txt
--- Process Complete. 5 passwords processed. ---
```

## Note
This is a proof-of-concept tool for a security portfolio. The password policy logic is intentionally basic and does not include advanced checks like dictionary attacks, common password lists, or entropy calculations. It focuses on demonstrating fundamental policy enforcement within the defined constraints.
