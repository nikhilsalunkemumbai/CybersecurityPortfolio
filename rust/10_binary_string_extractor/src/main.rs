// main.rs
//
// Binary String Extractor
//
// Overview:
// The Binary String Extractor is a command-line utility that scans binary files for sequences
// of printable characters, often referred to as "strings." This tool is valuable in cybersecurity
// tasks such as malware analysis, reverse engineering, and digital forensics, as it helps identify
// embedded text that can reveal functionality, configuration, or intellectual property.
//
// Design Constraints & Rationale:
// - Line Limit (<=300 lines): Enforces a focused and efficient implementation.
// - Standard Library Only: Demonstrates core Rust capabilities without external crates.
// - CLI-Only Interface: Prioritizes the string extraction logic.
// - One Tool = One Problem: Solely focused on extracting strings from binary data.

use std::env;
use std::fs::File;
use std::io::{self, BufReader, Read, Write};
use std::path::PathBuf;
use std::process;

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

/// Parses command-line arguments.
/// Returns (input_file_path, output_file_path, min_length, verbose)
fn parse_args() -> (PathBuf, Option<PathBuf>, usize, bool) {
    let args: Vec<String> = env::args().collect();

    let mut input_file_path: Option<PathBuf> = None;
    let mut output_file_path: Option<PathBuf> = None;
    let mut min_length: usize = 4; // Default minimum string length
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
            "-m" | "--min-length" => {
                i += 1;
                if i < args.len() {
                    min_length = args[i].parse::<usize>().unwrap_or_else(|_| {
                        fatal_error("Invalid value for --min-length. Must be a positive integer.");
                    });
                    if min_length == 0 {
                        fatal_error("Minimum length must be greater than 0.");
                    }
                } else {
                    fatal_error("Missing value for --min-length");
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

    (input_path, output_file_path, min_length, verbose)
}

/// Prints the help message for the tool.
fn print_help() {
    println!(
        "Binary String Extractor

Usage: binary_string_extractor -i <INPUT_FILE> [-o <OUTPUT_FILE>] [-m <MIN_LENGTH>] [-v | --verbose] [--help]

Arguments:
  -i, --input <FILE>        Path to the binary input file to extract strings from.
  -o, --output <FILE>       (Optional) Path to save the extracted strings. If not provided, output is printed to stdout.
  -m, --min-length <LENGTH> (Optional) Minimum length of strings to extract (default: 4).
  -v, --verbose             (Optional) Enable verbose output.
  --help                    Display this help message."
    );
}

/// Extracts printable ASCII strings from a Read stream.
fn extract_strings<R: Read>(reader: &mut R, min_len: usize, verbose: bool) -> Vec<String> {
    let mut current_string_bytes = Vec::new();
    let mut strings = Vec::new();

    let mut buffer = [0; 4096]; // Read in chunks
    info("Starting string extraction...", verbose);

    loop {
        let bytes_read = reader.read(&mut buffer).unwrap_or_else(|e| {
            fatal_error(&format!("Failed to read from input: {}", e));
        });

        if bytes_read == 0 {
            break; // End of file
        }

        for &byte in &buffer[..bytes_read] {
            // Check if the byte is a printable ASCII character (0x20 to 0x7E)
            // or common extended ASCII characters if desired, but for this demo, keeping it simple.
            if byte >= 0x20 && byte <= 0x7E {
                current_string_bytes.push(byte);
            } else {
                // Non-printable character found, terminate current string
                if current_string_bytes.len() >= min_len {
                    // It's safe to unwrap here because we've filtered for valid UTF-8 range (ASCII)
                    strings.push(String::from_utf8(current_string_bytes.clone()).unwrap());
                }
                current_string_bytes.clear();
            }
        }
    }

    // Add any remaining string at EOF
    if current_string_bytes.len() >= min_len {
        strings.push(String::from_utf8(current_string_bytes).unwrap());
    }

    info(&format!("Finished extraction. Found {} potential strings.", strings.len()), verbose);
    strings
}

/// Writes extracted strings to a Write stream.
fn write_strings<W: Write>(writer: &mut W, strings: &[String], verbose: bool) {
    info(&format!("Writing {} strings to output...", strings.len()), verbose);
    for s in strings {
        writeln!(writer, "{}", s).unwrap_or_else(|e| {
            fatal_error(&format!("Failed to write to output: {}", e));
        });
    }
    info("Successfully wrote strings to output.", verbose);
}

/// The main entry point for the application.
/// Parses arguments, extracts strings from the input file, and writes them to the output.
fn main() {
    let (input_path, output_path, min_length, verbose) = parse_args();

    info(&format!("Input file: {:?}", input_path), verbose);
    info(&format!("Minimum string length: {}", min_length), verbose);

    let mut input_file = File::open(&input_path).unwrap_or_else(|e| {
        fatal_error(&format!("Failed to open input file {:?}: {}", input_path, e));
    });
    let mut reader = BufReader::new(&mut input_file);

    let strings = extract_strings(&mut reader, min_length, verbose);

    let mut writer: Box<dyn Write> = if let Some(path) = output_path {
        info(&format!("Output file: {:?}", path), verbose);
        Box::new(File::create(&path).unwrap_or_else(|e| {
            fatal_error(&format!("Failed to create output file {:?}: {}", path, e));
        }))
    } else {
        info("Outputting to stdout.", verbose);
        Box::new(io::stdout())
    };

    write_strings(&mut writer, &strings, verbose);

    info("Binary string extraction complete.", verbose);
    process::exit(0);
}
