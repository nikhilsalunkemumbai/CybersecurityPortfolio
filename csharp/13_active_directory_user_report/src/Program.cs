// Program.cs
//
// Active Directory User Report
//
// Overview:
// This C# command-line utility generates basic reports of users within an Active Directory domain.
// It demonstrates interaction with Active Directory services, a fundamental skill in enterprise
// cybersecurity for tasks like auditing, identifying stale accounts, or reviewing group memberships.
//
// Design Constraints & Rationale:
// - Line Limit (<=300 lines): Encourages focused AD interaction and reporting logic.
// - Standard Library Only (.NET Framework): Emphasizes C# features and .NET's AD integration
//   (`System.DirectoryServices`), avoiding unnecessary external NuGet packages.
// - CLI-Only Interface: Focuses on core AD interaction without GUI overhead.
// - One Tool = One Problem: Specifically addresses basic AD user reporting.

using System;
using System.Collections.Generic;
using System.DirectoryServices; // For DirectoryEntry and DirectorySearcher
using System.IO;
using System.Linq;
using System.Text;

namespace ActiveDirectoryUserReport
{
    class Program
    {
        // Constants for output formatting
        private const string INFO_PREFIX = "[INFO] ";
        private const string ERROR_PREFIX = "[ERROR] ";

        /// <summary>
        /// Prints an error message to stderr and exits the application with a non-zero exit code.
        /// </summary>
        /// <param name="message">The error message to print.</param>
        static void FatalError(string message)
        {
            Console.Error.WriteLine($"{ERROR_PREFIX}{message}");
            Environment.Exit(1);
        }

        /// <summary>
        /// Prints an informational message to stderr if verbose mode is enabled.
        /// </summary>
        /// <param name="message">The message to print.</param>
        /// <param name="verbose">Whether verbose mode is enabled.</param>
        static void Info(string message, bool verbose)
        {
            if (verbose)
            {
                Console.Error.WriteLine($"{INFO_PREFIX}{message}");
            }
        }

        /// <summary>
        /// Prints the help message to the console.
        /// </summary>
        static void PrintHelp()
        {
            Console.WriteLine(@"Active Directory User Report

Usage: ActiveDirectoryUserReport.exe [-d <DOMAIN_NAME>] [-o <OUTPUT_FILE>] [-e | --enabled-only] [-s | --show-properties <PROP1,PROP2>] [-v | --verbose] [--help] 

Arguments:
  -d, --domain <DOMAIN>          (Optional) The Active Directory domain to query. Defaults to the current domain.
  -o, --output <FILE>            (Optional) Path to save the report (e.g., CSV). If not provided, prints to stdout.
  -e, --enabled-only             (Optional) Only show enabled user accounts.
  -s, --show-properties <PROP1,PROP2> (Optional) Comma-separated list of additional AD user properties to display (e.g., mail,description).
  -v, --verbose                  (Optional) Enable verbose output.
  --help                         Display this help message.

NOTE: This tool requires access to an Active Directory domain and appropriate permissions to query user information.
It is intended for use in controlled lab environments or on systems with proper AD access configured.
");
        }

        /// <summary>
        /// Parses the command-line arguments.
        /// </summary>
        /// <param name="args">The command-line arguments.</param>
        /// <returns>A tuple containing the parsed arguments.</returns>
        static (string domain, string outputPath, bool enabledOnly, List<string> showProperties, bool verbose) ParseArgs(string[] args)
        {
            string domain = null;
            string outputPath = null;
            bool enabledOnly = false;
            List<string> showProperties = new List<string>();
            bool verbose = false;

            for (int i = 0; i < args.Length; i++)
            {
                switch (args[i].ToLower())
                {
                    case "-d":
                    case "--domain":
                        if (i + 1 < args.Length)
                        {
                            domain = args[++i];
                        }
                        else FatalError("Missing value for --domain");
                        break;
                    case "-o":
                    case "--output":
                        if (i + 1 < args.Length)
                        {
                            outputPath = args[++i];
                        }
                        else FatalError("Missing value for --output");
                        break;
                    case "-e":
                    case "--enabled-only":
                        enabledOnly = true;
                        break;
                    case "-s":
                    case "--show-properties":
                        if (i + 1 < args.Length)
                        {
                            showProperties = args[++i].Split(',', StringSplitOptions.RemoveEmptyEntries).Select(p => p.Trim()).ToList();
                        }
                        else FatalError("Missing value for --show-properties");
                        break;
                    case "-v":
                    case "--verbose":
                        verbose = true;
                        break;
                    case "--help":
                        PrintHelp();
                        Environment.Exit(0);
                        break;
                    default:
                        FatalError($"Unknown argument: {args[i]}");
                        break;
                }
            }
            return (domain, outputPath, enabledOnly, showProperties, verbose);
        }

        /// <summary>
        /// Converts an Active Directory large integer timestamp to a DateTime object.
        /// </summary>
        /// <param name="adsValue">The Active Directory timestamp value.</param>
        /// <returns>A DateTime object or null if conversion fails.</returns>
        public static DateTime? ConvertADSToDateTime(object adsValue)
        {
            if (adsValue == null) return null;
            try
            {
                long largeInt = (long)adsValue;
                // AD time is 100-nanosecond intervals since 1601/01/01
                return DateTime.FromFileTime(largeInt);
            } 
            catch { return null; }
        }

        /// <summary>
        /// Gets a list of users from a real Active Directory.
        /// </summary>
        public static (List<Dictionary<string, string>> reportData, HashSet<string> allHeaders) GetUsers(string domain, bool enabledOnly, List<string> showProperties, bool verbose)
        {
            var reportData = new List<Dictionary<string, string>>();
            var allHeaders = new HashSet<string>();

            string ldapPath = string.IsNullOrEmpty(domain) ? "LDAP://" : $"LDAP://{domain}";
            using (DirectoryEntry searchRoot = new DirectoryEntry(ldapPath))
            {
                using (DirectorySearcher searcher = new DirectorySearcher(searchRoot))
                {
                    searcher.Filter = "(&(objectCategory=person)(objectClass=user))";
                    searcher.PropertiesToLoad.Add("sAMAccountName");
                    searcher.PropertiesToLoad.Add("displayName");
                    searcher.PropertiesToLoad.Add("userAccountControl");
                    searcher.PropertiesToLoad.Add("lastLogonTimestamp");

                    foreach (var prop in showProperties)
                    {
                        if (!searcher.PropertiesToLoad.Contains(prop.ToLower()))
                        {
                            searcher.PropertiesToLoad.Add(prop.ToLower());
                        }
                    }

                    using (SearchResultCollection results = searcher.FindAll())
                    {
                        foreach (SearchResult result in results)
                        {
                            using (DirectoryEntry userEntry = result.GetDirectoryEntry())
                            {
                                // Check for null userEntry.Properties before accessing
                                if (userEntry.Properties["userAccountControl"] == null || userEntry.Properties["userAccountControl"].Value == null)
                                {
                                    continue;
                                }

                                bool isEnabled = !userEntry.Properties["userAccountControl"].Contains(0x2);

                                if (enabledOnly && !isEnabled)
                                {
                                    continue;
                                }

                                var userData = new Dictionary<string, string>();
                                userData["sAMAccountName"] = userEntry.Properties["sAMAccountName"]?.Value?.ToString() ?? "N/A";
                                userData["displayName"] = userEntry.Properties["displayName"]?.Value?.ToString() ?? "N/A";
                                userData["Enabled"] = isEnabled.ToString();

                                DateTime? lastLogonDt = ConvertADSToDateTime(userEntry.Properties["lastLogonTimestamp"]?.Value);
                                userData["LastLogonDate"] = lastLogonDt.HasValue ? lastLogonDt.Value.ToString("yyyy-MM-dd HH:mm:ss") : "N/A";

                                allHeaders.Add("sAMAccountName");
                                allHeaders.Add("displayName");
                                allHeaders.Add("Enabled");
                                allHeaders.Add("LastLogonDate");

                                foreach (var prop in showProperties)
                                {
                                    string propValue = userEntry.Properties[prop.ToLower()]?.Value?.ToString() ?? "N/A";
                                    userData[prop.ToLower()] = propValue;
                                    allHeaders.Add(prop.ToLower());
                                }
                                reportData.Add(userData);
                            }
                        }
                    }
                }
            }
            return (reportData, allHeaders);
        }

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        /// <param name="args">The command-line arguments.</param>
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                PrintHelp();
                Environment.Exit(0);
            }

            var (domain, outputPath, enabledOnly, showProperties, verbose) = ParseArgs(args);

            Info($"Target domain: {(string.IsNullOrEmpty(domain) ? "Current" : domain)}", verbose);
            Info($"Enabled users only: {enabledOnly}", verbose);
            if (showProperties.Any())
            {
                Info($"Additional properties to show: {string.Join(", ", showProperties)}", verbose);
            }

            try
            {
                var (reportData, allHeaders) = GetUsers(domain, enabledOnly, showProperties, verbose);

                if (reportData.Count == 0)
                {
                    Info("No users found matching criteria.", verbose);
                    Environment.Exit(0);
                }

                // Prepare CSV headers
                var finalHeaders = allHeaders.ToList();
                // Sort headers for consistency, placing common ones first
                finalHeaders.Remove("sAMAccountName"); finalHeaders.Insert(0, "sAMAccountName");
                finalHeaders.Remove("displayName"); finalHeaders.Insert(1, "displayName");
                finalHeaders.Remove("Enabled"); finalHeaders.Insert(2, "Enabled");
                finalHeaders.Remove("LastLogonDate"); finalHeaders.Insert(3, "LastLogonDate");
                
                // Sort remaining properties alphabetically
                var remainingHeaders = finalHeaders.Skip(4).OrderBy(h => h).ToList();
                finalHeaders = finalHeaders.Take(4).Concat(remainingHeaders).ToList();

                StringBuilder csvContent = new StringBuilder();
                csvContent.AppendLine(string.Join(",", finalHeaders.Select(h =>
                {
                    // Escape internal quotes and enclose in double quotes
                    string headerValue = h;
                    return "\"" + headerValue.Replace("\"", "\"\"") + "\"";
                })));

                foreach (var row in reportData)
                {
                    csvContent.AppendLine(string.Join(",", finalHeaders.Select(h =>
                    {
                        string value = row.GetValueOrDefault(h, "N/A");
                        return "\"" + value.Replace("\"", "\"\"") + "\"";
                    })));
                }

                if (string.IsNullOrEmpty(outputPath))
                {
                    Console.WriteLine(csvContent.ToString());
                    Info("Report printed to console.", verbose);
                }
                else
                {
                    File.WriteAllText(outputPath, csvContent.ToString());
                    Info($"Report saved to: {outputPath}", verbose);
                }
            }
            catch (Exception ex)
            {
                FatalError($"An error occurred: {ex.Message}");
            }

            Environment.Exit(0);
        }
    }
}
