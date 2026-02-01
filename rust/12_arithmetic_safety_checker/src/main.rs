// main.rs
//
// Arithmetic Safety Checker
//
// Overview:
// The Arithmetic Safety Checker analyzes code snippets for potential integer overflow/underflow
// vulnerabilities. Such vulnerabilities can have severe security implications, leading to
// unexpected program states, buffer overflows, or incorrect calculations that could be
// exploited. This tool provides a conceptual demonstration of identifying these issues
// at a static analysis level within a Rust context.
//
// Design Constraints & Rationale:
// - Line Limit (<=300 lines): Focuses on the core logic of arithmetic safety concepts.
// - Standard Library Only: Highlights fundamental Rust features for value manipulation.
// - CLI-Only Interface: Prioritizes the conceptual analysis logic.
// - One Tool = One Problem: Dedicated to checking arithmetic safety.

use std::env;
use std::fs::File;
use std::io::{self, BufReader, BufRead, Write};
use std::path::PathBuf;
use std::process;
use std::str::FromStr; // Required for parsing integer types from string

// Constants for output formatting
const INFO_PREFIX: &str = "[INFO] ";
const ERROR_PREFIX: &str = "[ERROR] ";

// --- Shared Abstractions ---
// Consistent CLI Argument Parsing: Uses `std::env::args` for CLI flags.
// Standardized Error Handling & Exit Codes: Exits with 0 on success, non-zero on error.
// Unified Logging/Output Format: Uses INFO, ERROR prefixes.

/// Prints an error message to stderr and exits the program with a non-zero status code.
fn fatal_error(message: &str) -> ! {
    eprintln!("{}{}", ERROR_PREFIX, message);
    process::exit(1);
}

/// Prints an informational message to stderr if verbose mode is enabled.
fn info(message: &str, verbose: bool) {
    if verbose {
        eprintln!("{}{}", INFO_PREFIX, message);
    }
}

/// Represents the type of integer being simulated for arithmetic checks.
#[derive(Debug)] // Add this line to derive the Debug trait
enum IntegerType {
    U8,
    I8,
    U16,
    I16,
    U32,
    I32,
    U64,
    I64,
    U128,
    I128,
}

impl FromStr for IntegerType {
    type Err = &'static str;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "u8" => Ok(IntegerType::U8),
            "i8" => Ok(IntegerType::I8),
            "u16" => Ok(IntegerType::U16),
            "i16" => Ok(IntegerType::I16),
            "u32" => Ok(IntegerType::U32),
            "i32" => Ok(IntegerType::I32),
            "u64" => Ok(IntegerType::U64),
            "i64" => Ok(IntegerType::I64),
            "u128" => Ok(IntegerType::U128),
            "i128" => Ok(IntegerType::I128),
            _ => Err("Invalid integer type specified. Choose from u8, i8, u16, i16, u32, i32, u64, i64, u128, i128."),
        }
    }
}

/// Parses command-line arguments.
/// Returns (input_file_path, output_file_path, integer_type, verbose)
fn parse_args() -> (PathBuf, Option<PathBuf>, IntegerType, bool) {
    let args: Vec<String> = env::args().collect();

    let mut input_file_path: Option<PathBuf> = None;
    let mut output_file_path: Option<PathBuf> = None;
    let mut integer_type = IntegerType::I32; // Default to i32
    let mut verbose = false;

    // Skip the first argument which is the program name
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-i" | "--input" => {
                i += 1;
                if i < args.len() {
                    input_file_path = Some(PathBuf::from(&args[i]));
                } else {
                    fatal_error("Missing value for --input");
                }
            }
            "-o" | "--output" => {
                i += 1;
                if i < args.len() {
                    output_file_path = Some(PathBuf::from(&args[i]));
                } else {
                    fatal_error("Missing value for --output");
                }
            }
            "-t" | "--type" => {
                i += 1;
                if i < args.len() {
                    integer_type = args[i].parse::<IntegerType>().unwrap_or_else(|e| {
                        fatal_error(e);
                    });
                } else {
                    fatal_error("Missing value for --type");
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

    let input_path = input_file_path.unwrap_or_else(|| {
        print_help();
        fatal_error("Input file path is required.");
    });

    (input_path, output_file_path, integer_type, verbose)
}

/// Prints the help message for the tool.
fn print_help() {
    println!(
        "Arithmetic Safety Checker

Usage: arithmetic_safety_checker -i <CODE_SNIPPET_FILE> [-o <OUTPUT_FILE>] [-t <TYPE>] [-v | --verbose] [--help]

Arguments:
  -i, --input <FILE>        Path to a file containing code snippets or arithmetic expressions to check.
  -o, --output <FILE>       (Optional) Path to save the analysis report. If not provided, output is printed to stdout.
  -t, --type <TYPE>         (Optional) Integer type to simulate (e.g., u8, i16, i32, u64). Defaults to i32.
  -v, --verbose             (Optional) Enable verbose output.
  --help                    Display this help message."
    );
}

/// Performs a conceptual check for arithmetic overflow/underflow.
/// This is a simplified demonstration, assuming expressions are "VALUE OPERATOR VALUE".
fn check_arithmetic_safety(
    expression: &str,
    int_type: &IntegerType,
    verbose: bool,
) -> String {
    let parts: Vec<&str> = expression.split_whitespace().collect();
    if parts.len() != 3 {
        return format!("WARN: Skipping malformed expression: {}", expression);
    }

    let op1_str = parts[0];
    let operator = parts[1];
    let op2_str = parts[2];

    macro_rules! check_op {
        ($type:ty, $min_val:expr, $max_val:expr) => {{
            let op1 = match op1_str.parse::<$type>() {
                Ok(val) => val,
                Err(_) => return format!("ERROR: Invalid operand '{}' for type {:?} in expression: {}", op1_str, int_type, expression),
            };
            let op2 = match op2_str.parse::<$type>() {
                Ok(val) => val,
                Err(_) => return format!("ERROR: Invalid operand '{}' for type {:?} in expression: {}", op2_str, int_type, expression),
            };

            info(&format!("Checking expression: {} {} {} as {}", op1, operator, op2, stringify!($type)), verbose);

            match operator {
                "+" => {
                    if let Some(res) = op1.checked_add(op2) {
                        format!("OK: {} {} {} = {}", op1, operator, op2, res)
                    } else {
                        format!("WARNING: Overflow detected for {} {} {} as {}", op1, operator, op2, stringify!($type))
                    }
                }
                "-" => {
                    if let Some(res) = op1.checked_sub(op2) {
                        format!("OK: {} {} {} = {}", op1, operator, op2, res)
                    } else {
                        format!("WARNING: Underflow detected for {} {} {} as {}", op1, operator, op2, stringify!($type))
                    }
                }
                "*" => {
                    if let Some(res) = op1.checked_mul(op2) {
                        format!("OK: {} {} {} = {}", op1, operator, op2, res)
                    } else {
                        format!("WARNING: Overflow detected for {} {} {} as {}", op1, operator, op2, stringify!($type))
                    }
                }
                "/" => {
                    if op2 == 0 {
                        return format!("ERROR: Division by zero detected in expression: {}", expression);
                    }
                    if let Some(res) = op1.checked_div(op2) {
                        format!("OK: {} {} {} = {}", op1, operator, op2, res)
                    } else {
                        format!("WARNING: Division overflow/underflow detected for {} {} {} as {}", op1, operator, op2, stringify!($type))
                    }
                }
                _ => format!("ERROR: Unsupported operator '{}' in expression: {}", operator, expression),
            }
        }};
    }

    match int_type {
        IntegerType::U8 => check_op!(u8, u8::MIN, u8::MAX),
        IntegerType::I8 => check_op!(i8, i8::MIN, i8::MAX),
        IntegerType::U16 => check_op!(u16, u16::MIN, u16::MAX),
        IntegerType::I16 => check_op!(i16, i16::MIN, i16::MAX),
        IntegerType::U32 => check_op!(u32, u32::MIN, u32::MAX),
        IntegerType::I32 => check_op!(i32, i32::MIN, i32::MAX),
        IntegerType::U64 => check_op!(u64, u64::MIN, u64::MAX),
        IntegerType::I64 => check_op!(i64, i64::MIN, i64::MAX),
        IntegerType::U128 => check_op!(u128, u128::MIN, u128::MAX),
        IntegerType::I128 => check_op!(i128, i128::MIN, i128::MAX),
    }
}

/// The main entry point for the application.
/// Parses arguments, reads expressions from the input file, checks them, and writes the report.
fn main() {
    let (input_path, output_path, integer_type, verbose) = parse_args();

    info(&format!("Input file: {:?}", input_path), verbose);
    info(&format!("Simulating type: {:?}", integer_type), verbose);

    let file = File::open(&input_path).unwrap_or_else(|e| {
        fatal_error(&format!("Failed to open input file {:?}: {}", input_path, e));
    });
    let reader = BufReader::new(file);

    let mut writer: Box<dyn Write> = if let Some(path) = output_path {
        info(&format!("Output file: {:?}", path), verbose);
        Box::new(File::create(&path).unwrap_or_else(|e| {
            fatal_error(&format!("Failed to create output file {:?}: {}", path, e));
        }))
    } else {
        info("Outputting to stdout.", verbose);
        Box::new(io::stdout())
    };

    info("Starting arithmetic safety checks...", verbose);
    let mut issues_found = false;
    for (line_num, read_line) in reader.lines().enumerate() {
        let expression = read_line.unwrap_or_else(|e| {
            fatal_error(&format!("Failed to read line from file: {}", e));
        });
        if expression.trim().is_empty() || expression.trim().starts_with('#') {
            continue;
        }

        let result = check_arithmetic_safety(&expression, &integer_type, verbose);
        writeln!(writer, "{}: {}", line_num + 1, result).unwrap_or_else(|e| {
            fatal_error(&format!("Failed to write to output: {}", e));
        });
        if result.starts_with("WARNING:") || result.starts_with("ERROR:") {
            issues_found = true;
        }
    }

    if issues_found {
        info("Arithmetic safety checks complete. Issues were found.", verbose);
        process::exit(1);
    } else {
        info("Arithmetic safety checks complete. No issues found.", verbose);
        process::exit(0);
    }
}