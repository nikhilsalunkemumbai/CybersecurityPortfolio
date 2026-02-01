using System;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.Text;
using System.IO;
using System.Collections.Generic;
using Microsoft.Win32;
using System.Linq;

namespace InstalledSoftwareAuditor
{
    public class Program
    {
        // Define exit codes
        private const int SuccessExitCode = 0;
        private const int ErrorExitCode = 1;

        public static int Main(string[] args)
        {
            // Define command-line options
            var listAllOption = new Option<bool>(
                aliases: new string[] { "--list-all", "-l" },
                description: "List all installed software."
            );

            var filterNameOption = new Option<string>(
                aliases: new string[] { "--filter-name", "-f" },
                description: "Filter software by name (case-insensitive, partial match)."
            );

            var outputFileOption = new Option<string>(
                aliases: new string[] { "--output-file", "-o" },
                description: "Path to an output file to write the audit results. If not specified, output to console."
            );

            var verboseOption = new Option<bool>(
                aliases: new string[] { "--verbose", "-v" },
                description: "Enable verbose output, including [INFO] messages."
            );

            // Create a root command
            var rootCommand = new RootCommand("Audits installed software on Windows systems.")
            {
                listAllOption,
                filterNameOption,
                outputFileOption,
                verboseOption
            };

            rootCommand.SetHandler((InvocationContext context) =>
            {
                var listAll = context.ParseResult.GetValueForOption(listAllOption);
                var filterName = context.ParseResult.GetValueForOption(filterNameOption);
                var outputFile = context.ParseResult.GetValueForOption(outputFileOption);
                var verbose = context.ParseResult.GetValueForOption(verboseOption);

                int result = RunAuditor(listAll, filterName, outputFile, verbose);
                context.ExitCode = result;
            });

            return rootCommand.Invoke(args);
        }

        /// <summary>
        /// Represents installed software information.
        /// </summary>
        public class SoftwareInfo
        {
            public string Name { get; set; } = string.Empty;
            public string Version { get; set; } = string.Empty;
            public string Publisher { get; set; } = string.Empty;
            public string InstallDate { get; set; } = string.Empty;
            public string UninstallString { get; set; } = string.Empty;

            public override string ToString()
            {
                return $"Name: {Name}\nVersion: {Version}\nPublisher: {Publisher}\nInstall Date: {InstallDate}\nUninstall String: {UninstallString}\n";
            }
        }

        /// <summary>
        /// Core logic for auditing installed software.
        /// </summary>
        private static int RunAuditor(bool listAll, string? filterName, string? outputFile, bool verbose)
        {
            TextWriter outputWriter = Console.Out;
            if (outputFile != null)
            {
                try
                {
                    outputWriter = new StreamWriter(outputFile, append: false, Encoding.UTF8);
                    if (verbose) LogInfo($"[INFO] Writing output to: {outputFile}", Console.Out);
                }
                catch (Exception ex)
                {
                    LogError($"[ERROR] Could not open output file '{outputFile}': {ex.Message}");
                    return ErrorExitCode;
                }
            }

            try
            {
                if (verbose) LogInfo("[INFO] Starting installed software audit...", Console.Out);

                var installedSoftware = GetInstalledSoftware(verbose);

                if (!string.IsNullOrEmpty(filterName))
                {
                    installedSoftware = installedSoftware
                        .Where(s => s.Name.Contains(filterName, StringComparison.OrdinalIgnoreCase))
                        .ToList();
                    if (verbose) LogInfo($"[INFO] Applied filter: '{filterName}'", Console.Out);
                }

                if (installedSoftware.Any())
                {
                    outputWriter.WriteLine("--- Installed Software Report ---");
                    foreach (var software in installedSoftware.OrderBy(s => s.Name))
                    {
                        outputWriter.WriteLine(software.ToString());
                    }
                    outputWriter.WriteLine("-------------------------------");
                }
                else
                {
                    outputWriter.WriteLine("No installed software found matching criteria.");
                }

                if (verbose) LogInfo("[INFO] Audit completed.", Console.Out);
            }
            catch (UnauthorizedAccessException ex)
            {
                LogError($"[ERROR] Access denied. Run as administrator: {ex.Message}");
                return ErrorExitCode;
            }
            catch (Exception ex)
            {
                LogError($"[ERROR] An unexpected error occurred: {ex.Message}");
                return ErrorExitCode;
            }
            finally
            {
                if (outputFile != null && outputWriter is StreamWriter sw)
                {
                    sw.Close();
                    sw.Dispose();
                }
            }

            return SuccessExitCode;
        }

        /// <summary>
        /// Enumerates installed software from the Windows Registry.
        /// </summary>
        private static List<SoftwareInfo> GetInstalledSoftware(bool verbose)
        {
            var softwareList = new List<SoftwareInfo>();

            string[] uninstallKeys =
            {
                @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                @"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            };

            foreach (string uninstallKey in uninstallKeys)
            {
                using (RegistryKey? baseKey = Registry.LocalMachine.OpenSubKey(uninstallKey))
                {
                    if (baseKey == null) continue;

                    foreach (string subkeyName in baseKey.GetSubKeyNames())
                    {
                        using (RegistryKey? subkey = baseKey.OpenSubKey(subkeyName))
                        {
                            if (subkey == null) continue;

                            // Ensure it's an application and not just an update or hotfix
                            string? displayName = subkey.GetValue("DisplayName")?.ToString();
                            if (string.IsNullOrEmpty(displayName)) continue;

                            string? systemComponent = subkey.GetValue("SystemComponent")?.ToString();
                            if (systemComponent == "1") continue; // Skip system components

                            string? windowsInstaller = subkey.GetValue("WindowsInstaller")?.ToString();
                            if (windowsInstaller == "1" && string.IsNullOrEmpty(subkey.GetValue("UninstallString")?.ToString()))
                            {
                                continue; // Skip Windows Installer components without uninstall string
                            }

                            softwareList.Add(new SoftwareInfo
                            {
                                Name = displayName,
                                Version = subkey.GetValue("DisplayVersion")?.ToString() ?? string.Empty,
                                Publisher = subkey.GetValue("Publisher")?.ToString() ?? string.Empty,
                                InstallDate = subkey.GetValue("InstallDate")?.ToString() ?? string.Empty,
                                UninstallString = subkey.GetValue("UninstallString")?.ToString() ?? string.Empty
                            });
                        }
                    }
                }
            }
            
            // Add current user installed software (e.g., some modern apps)
            using (RegistryKey? baseKey = Registry.CurrentUser.OpenSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"))
            {
                if (baseKey != null)
                {
                     foreach (string subkeyName in baseKey.GetSubKeyNames())
                    {
                        using (RegistryKey? subkey = baseKey.OpenSubKey(subkeyName))
                        {
                            if (subkey == null) continue;

                            string? displayName = subkey.GetValue("DisplayName")?.ToString();
                            if (string.IsNullOrEmpty(displayName)) continue;

                            softwareList.Add(new SoftwareInfo
                            {
                                Name = displayName,
                                Version = subkey.GetValue("DisplayVersion")?.ToString() ?? string.Empty,
                                Publisher = subkey.GetValue("Publisher")?.ToString() ?? string.Empty,
                                InstallDate = subkey.GetValue("InstallDate")?.ToString() ?? string.Empty,
                                UninstallString = subkey.GetValue("UninstallString")?.ToString() ?? string.Empty
                            });
                        }
                    }
                }
            }

            if (verbose) LogInfo($"[INFO] Found {softwareList.Count} installed software entries.", Console.Out);
            return softwareList.DistinctBy(s => s.Name).ToList(); // Remove duplicates by name
        }

        /// <summary>
        /// Logs an informational message to the specified writer.
        /// </summary>
        private static void LogInfo(string message, TextWriter writer)
        {
            writer.WriteLine(message);
        }

        /// <summary>
        /// Logs an error message to stderr.
        /// </summary>
        private static void LogError(string message)
        {
            Console.Error.WriteLine(message);
        }
    }
}