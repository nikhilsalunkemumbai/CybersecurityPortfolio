using System;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.Diagnostics.Eventing.Reader;
using System.Text;
using System.IO;
using System.Collections.Generic;
using System.Linq;

namespace WindowsEventLogSummarizer
{
    public class Program
    {
        // Define exit codes
        private const int SuccessExitCode = 0;
        private const int ErrorExitCode = 1;

        public static int Main(string[] args)
        {
            // Define command-line options
            var logNameOption = new Option<string>(
                aliases: new string[] { "--log-name", "-l" },
                getDefaultValue: () => "Security",
                description: "Name of the Windows Event Log to read (e.g., 'Security', 'System', 'Application')."
            );

            var filterOption = new Option<string>(
                aliases: new string[] { "--filter", "-f" },
                description: "XPath-like query string to filter events."
            );

            var timeRangeOption = new Option<string>(
                aliases: new string[] { "--time-range", "-t" },
                description: "Time range for events (e.g., '24h' for last 24 hours, '7d' for last 7 days, '30m' for last 30 minutes)."
            );

            var outputFileOption = new Option<string>(
                aliases: new string[] { "--output-file", "-o" },
                description: "Path to an output file to write the summary. If not specified, output to console."
            );

            var verboseOption = new Option<bool>(
                aliases: new string[] { "--verbose", "-v" },
                description: "Enable verbose output, including [INFO] messages."
            );

            // Create a root command
            var rootCommand = new RootCommand("Summarizes Windows Event Logs based on various criteria.")
            {
                logNameOption,
                filterOption,
                timeRangeOption,
                outputFileOption,
                verboseOption
            };

            rootCommand.SetHandler((InvocationContext context) =>
            {
                var logName = context.ParseResult.GetValueForOption(logNameOption)!;
                var filter = context.ParseResult.GetValueForOption(filterOption);
                var timeRange = context.ParseResult.GetValueForOption(timeRangeOption);
                var outputFile = context.ParseResult.GetValueForOption(outputFileOption);
                var verbose = context.ParseResult.GetValueForOption(verboseOption);

                int result = RunSummarizer(logName, filter, timeRange, outputFile, verbose);
                context.ExitCode = result;
            });

            return rootCommand.Invoke(args);
        }

        /// <summary>
        /// Core logic for summarizing Windows Event Logs.
        /// </summary>
        private static int RunSummarizer(string logName, string? filter, string? timeRange, string? outputFile, bool verbose)
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
                // Calculate time filter if provided
                DateTime? startTime = null;
                if (!string.IsNullOrEmpty(timeRange))
                {
                    startTime = ParseTimeRange(timeRange);
                    if (startTime == null)
                    {
                        LogError($"[ERROR] Invalid time range format: {timeRange}. Examples: '24h', '7d', '30m'.");
                        return ErrorExitCode;
                    }
                }

                if (verbose) LogInfo($"[INFO] Starting Event Log summarization for '{logName}'...", Console.Out);
                if (verbose && filter != null) LogInfo($"[INFO] Filter query: {filter}", Console.Out);
                if (verbose && startTime != null) LogInfo($"[INFO] Events from: {startTime.Value.ToUniversalTime():yyyy-MM-dd HH:mm:ss UTC}", Console.Out);

                var query = BuildEventLogQuery(logName, filter, startTime);
                var eventCounts = new Dictionary<string, int>();

                using (var logReader = new EventLogReader(query))
                {
                    for (EventRecord eventRecord = logReader.ReadEvent();
                         eventRecord != null;
                         eventRecord = logReader.ReadEvent())
                    {
                        var eventInstance = (EventLogRecord)eventRecord;
                        try
                        {
                            // Apply time filter in-memory if query was simplified and couldn't handle it
                            if (startTime != null && eventInstance.TimeCreated < startTime)
                            {
                                continue;
                            }

                            string eventId = $"ID: {eventInstance.Id} (Source: {eventInstance.ProviderName})";
                            if (!eventCounts.ContainsKey(eventId))
                            {
                                eventCounts[eventId] = 0;
                            }
                            eventCounts[eventId]++;
                        }
                        catch (EventLogException ex)
                        {
                            if (verbose) LogInfo($"[WARNING] Could not read event properties: {ex.Message}", Console.Error);
                        }
                    }
                }

                // Output Summary
                outputWriter.WriteLine($"--- Event Log Summary for '{logName}' ---");
                if (eventCounts.Count == 0)
                {
                    outputWriter.WriteLine("No events found matching criteria.");
                }
                else
                {
                    foreach (var entry in eventCounts.OrderByDescending(x => x.Value))
                    {
                        outputWriter.WriteLine($"{entry.Key}: {entry.Value} occurrences");
                    }
                }
                outputWriter.WriteLine("-------------------------------------");

                if (verbose) LogInfo($"[INFO] Summarization completed for '{logName}'.", Console.Out);
            }
            catch (EventLogException ex)
            {
                LogError($"[ERROR] Failed to access Event Log '{logName}': {ex.Message}");
                if (ex.InnerException != null) LogError($"[ERROR] Inner exception: {ex.InnerException.Message}");
                return ErrorExitCode;
            }
            catch (UnauthorizedAccessException ex)
            {
                LogError($"[ERROR] Access denied to Event Log '{logName}'. Run as administrator or check permissions: {ex.Message}");
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
        /// Parses a time range string (e.g., "24h", "7d") into a DateTime object.
        /// </summary>
        private static DateTime? ParseTimeRange(string timeRange)
        {
            if (string.IsNullOrEmpty(timeRange) || timeRange.Length < 2) return null;

            char unit = timeRange.Last();
            if (!int.TryParse(timeRange.AsSpan(0, timeRange.Length - 1), out int value)) return null;

            return unit switch
            {
                'h' => DateTime.Now.AddHours(-value),
                'd' => DateTime.Now.AddDays(-value),
                'm' => DateTime.Now.AddMinutes(-value),
                _ => null
            };
        }

        /// <summary>
        /// Builds an EventLogQuery object based on provided log name, filter, and start time.
        /// </summary>
        private static EventLogQuery BuildEventLogQuery(string logName, string? filter, DateTime? startTime)
        {
            // For a basic PoC, we will only use the logName for the query
            // and perform filtering (like time range) in-memory if needed.
            return new EventLogQuery(logName, PathType.LogName);
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