// main.rs
//
// Safe Config Parser & Linter
//
// Overview:
// The Safe Config Parser & Linter is a command-line utility designed to parse configuration files
// (e.g., TOML, YAML, JSON) with a focus on security. It validates configurations against a defined
// schema or a set of security best practices, reporting any potential misconfigurations, deviations,
// or errors. This tool is essential for ensuring that application and system configurations adhere
// to security guidelines, reducing the attack surface.
//
// Design Constraints & Rationale:
// - Line Limit (<=300 lines): Encourages concise and focused logic for configuration parsing and
//   security linting.
// - Standard Library Only: Ensures no external dependencies are required for core functionality,
//   demonstrating fundamental Rust capabilities.
// - CLI-Only Interface: Focuses on the core security validation logic.
// - One Tool = One Problem: Specifically addresses secure configuration parsing and linting.

use std::env;
use std::fs;
use std::io::{self, Write};
use std::process;

// Constants for output formatting
const INFO_PREFIX: &str = "[INFO] ";
const ERROR_PREFIX: &str = "[ERROR] ";
const WARNING_PREFIX: &str = "[WARNING] ";

// --- Shared Abstractions ---
// Consistent CLI Argument Parsing: Uses `std::env::args` for CLI flags.
// Standardized Error Handling & Exit Codes: Exits with 0 on success, non-zero on error.
// Unified Logging/Output Format: Uses INFO, WARNING, ERROR prefixes.

/// Prints an error message to stderr and exits the program with a non-zero status code.
fn fatal_error(message: &str) {
    eprintln!("{}{}", ERROR_PREFIX, message);
    process::exit(1);
}

/// Prints a warning message to stderr.
fn warn(message: &str) {
    eprintln!("{}{}", WARNING_PREFIX, message);
}

/// Prints an informational message to stdout if verbose mode is enabled.
fn info(message: &str, verbose: bool) {
    if verbose {
        println!("{}{}", INFO_PREFIX, message);
    }
}

/// Parses command-line arguments.
/// Returns (config_file_path, schema_file_path, output_file_path, verbose)
fn parse_args() -> (String, String, Option<String>, bool) {
    let args: Vec<String> = env::args().collect();

    let mut config_file_path: Option<String> = None;
    let mut schema_file_path: Option<String> = None;
    let mut output_file_path: Option<String> = None;
    let mut verbose = false;

    // Skip the first argument which is the program name
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-c" | "--config" => {
                i += 1;
                if i < args.len() {
                    config_file_path = Some(args[i].clone());
                } else {
                    fatal_error("Missing value for --config");
                }
            }
            "-s" | "--schema" => {
                i += 1;
                if i < args.len() {
                    schema_file_path = Some(args[i].clone());
                } else {
                    fatal_error("Missing value for --schema");
                }
            }
            "-o" | "--output" => {
                i += 1;
                if i < args.len() {
                    output_file_path = Some(args[i].clone());
                } else {
                    fatal_error("Missing value for --output");
                }
            }
            "-v" | "--verbose" => {
                verbose = true;
            }
            "--help" => {
                print_help();
                process::exit(0);
            }
            _ => {
                fatal_error(&format!("Unknown argument: {}", args[i]));
            }
        }
        i += 1;
    }

    let config_path = config_file_path.unwrap_or_else(|| {
        print_help();
        fatal_error("Configuration file path is required.");
        // This line is technically unreachable due to fatal_error, but Rust requires a return
        // for `unwrap_or_else` if the closure doesn't diverge. We add a dummy value.
        String::new()
    });
    let schema_path = schema_file_path.unwrap_or_else(|| {
        print_help();
        fatal_error("Schema file path is required.");
        String::new()
    });

    (config_path, schema_path, output_file_path, verbose)
}

/// Prints the help message for the tool.
fn print_help() {
    println!(
        "Safe Config Parser & Linter

Usage: safe_config_linter -c <CONFIG_FILE> -s <SCHEMA_FILE> [-o <OUTPUT_FILE>] [-v | --verbose] [--help]

Arguments:
  -c, --config <FILE>    Path to the configuration file to parse and lint.
  -s, --schema <FILE>    Path to the security schema file for validation.
  -o, --output <FILE>    (Optional) Path to save the linting report. If not provided, output is printed to stdout.
  -v, --verbose          (Optional) Enable verbose output.
  --help                 Display this help message."
    );
}

/// Reads the content of a file.
fn read_file_content(file_path: &str) -> String {
    fs::read_to_string(file_path)
        .unwrap_or_else(|e| {
            fatal_error(&format!("Failed to read file {}: {}", file_path, e));
            String::new() // Unreachable, but satisfies type checker
        })
}

/// Cleans a value by removing surrounding quotes if present.
fn clean_value(value: &str) -> String {
    let trimmed = value.trim();
    if (trimmed.starts_with('\"') && trimmed.ends_with('\"')) ||
       (trimmed.starts_with('\'') && trimmed.ends_with('\'')) {
        trimmed[1..trimmed.len() - 1].to_string()
    } else {
        trimmed.to_string()
    }
}

/// Parses a configuration file (simplified for demonstration, assumes key-value pairs).
/// In a real tool, this would handle TOML, YAML, JSON. For now, it's a basic parser.
fn parse_config(content: &str) -> Vec<(String, String)> {
    content
        .lines()
        .filter_map(|line| {
            let trimmed = line.trim();
            if trimmed.starts_with('#') || trimmed.is_empty() {
                None // Skip comments and empty lines
            } else {
                let parts: Vec<&str> = trimmed.splitn(2, '=').collect();
                if parts.len() == 2 {
                    Some((parts[0].trim().to_string(), clean_value(parts[1])))
                } else {
                    warn(&format!("Skipping malformed config line: {}", trimmed));
                    None
                }
            }
        })
        .collect()
}

/// Parses a schema file (simplified for demonstration, assumes key-value pairs representing rules).
fn parse_schema(content: &str) -> Vec<(String, String)> {
    // Similar to parse_config, but specific to schema rules.
    // For this basic demo, assume schema lines are "key=expected_value" or "key=rule_type"
    parse_config(content)
}

/// Validates the configuration against the schema.
/// This is a highly simplified validation for demonstration.
/// A real linter would have complex rule engines.
fn validate_config(
    config: &[(String, String)],
    schema: &[(String, String)],
    _verbose: bool,
) -> Vec<String> {
    let mut warnings = Vec::new();

    // Collect schema rules into a more accessible map
    let schema_map: std::collections::HashMap<String, String> =
        schema.iter().map(|(k, v)| (k.clone(), v.clone())).collect();

    // Check for keys in config that are not in schema (potential unknown/unmanaged settings)
    for (config_key, _) in config {
        if !schema_map.contains_key(config_key) {
            warnings.push(format!(
                "Config key '{}' not found in schema. Consider defining its security posture.",
                config_key
            ));
        }
    }

    // Basic validation: iterate through schema rules and apply them to config
    for (schema_key, schema_rule) in schema {
        match config.iter().find(|(k, _)| k == schema_key) {
            Some((_, config_value)) => {
                match schema_rule.as_str() {
                    "https://" => { // database_url rule
                        if !config_value.starts_with("https://") {
                            warnings.push(format!(
                                "Insecure setting: '{}' should use HTTPS (starts with 'https://').",
                                schema_key
                            ));
                        }
                    }
                    "false" => { // debug_mode rule
                        if config_value == "true" {
                            warnings.push(format!(
                                "Insecure setting: '{}' should be 'false' in production.",
                                schema_key
                            ));
                        }
                    }
                    "no_default_password" => { // admin_password rule
                        if config_value == "password123" {
                            warnings.push(format!(
                                "Critical: '{}' uses default password 'password123'. Change immediately!",
                                schema_key
                            ));
                        }
                    }
                    "INFO" => { // log_level rule
                        if config_value != "INFO" {
                            warnings.push(format!(
                                "Logging level: '{}' is not 'INFO'. Consider 'INFO' for standard operation.",
                                schema_key
                            ));
                        }
                    }
                    "min_length_8" => { // api_key_length rule
                        if let Ok(length) = config_value.parse::<usize>() {
                            if length < 8 {
                                warnings.push(format!(
                                    "Weak setting: '{}' has length {}. Recommended minimum: 8.",
                                    schema_key, length
                                ));
                            }
                        } else {
                            warnings.push(format!(
                                "Schema rule for '{}' expects an integer length, but config value '{}' is not a valid integer.",
                                schema_key, config_value
                            ));
                        }
                    }
                    _ => {
                        // Generic check for exact value match if no specific rule type is recognized
                        if config_value != schema_rule {
                            warnings.push(format!(
                                "Config key '{}' value '{}' does not match schema rule '{}'.",
                                schema_key, config_value, schema_rule
                            ));
                        }
                    }
                }
            }
            None => {
                // Key from schema is missing in config
                warnings.push(format!(
                    "Missing configuration key: '{}' as defined in schema.",
                    schema_key
                ));
            }
        }
    }

    warnings
}

/// Writes the report to the specified output file or stdout.
fn write_report(output_path: Option<&str>, warnings: &[String], verbose: bool) {
    let mut writer: Box<dyn Write> = match output_path {
        Some(path) => Box::new(fs::File::create(path).unwrap_or_else(|e| {
            fatal_error(&format!("Failed to create output file {}: {}", path, e));
            process::exit(1); // Diverging function, never returns
        })),
        None => Box::new(io::stdout()),
    };

    if warnings.is_empty() {
        writeln!(writer, "No security warnings or misconfigurations found.").unwrap_or_else(|e| {
            fatal_error(&format!("Failed to write to report: {}", e));
        });
        info("Configuration is compliant with the provided schema.", verbose);
    } else {
        writeln!(writer, "Security Linter Report:").unwrap_or_else(|e| {
            fatal_error(&format!("Failed to write to report: {}", e));
        });
        for warning in warnings {
            writeln!(writer, "- {}", warning).unwrap_or_else(|e| {
                fatal_error(&format!("Failed to write to report: {}", e));
            });
        }
        info(&format!("Found {} potential security issues.", warnings.len()), verbose);
    }
}

/// The main entry point for the application.
/// Parses arguments, reads config and schema, validates the config, and reports findings.
fn main() {
    let (config_path, schema_path, output_path, verbose) = parse_args();

    info(&format!("Loading configuration from: {}", config_path), verbose);
    let config_content = read_file_content(&config_path);
    let config = parse_config(&config_content);
    info("Configuration loaded and parsed.", verbose);

    info(&format!("Loading schema from: {}", schema_path), verbose);
    let schema_content = read_file_content(&schema_path);
    let schema = parse_schema(&schema_content);
    info("Schema loaded and parsed.", verbose);

    info("Starting configuration validation...", verbose);
    let warnings = validate_config(&config, &schema, verbose);
    info("Validation complete.", verbose);

    info("Generating report...", verbose);
    write_report(output_path.as_deref(), &warnings, verbose);
    info("Report generated successfully.", verbose);

    if !warnings.is_empty() {
        process::exit(1); // Exit with error if warnings were found
    }
}
