using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using FacilityOps;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace FacilityOps.Editor
{
    /// <summary>
    /// Read-only validation bridge between the Blender-generated Old Town manifest
    /// and the Unity project. It installs no packages and changes no assets.
    /// </summary>
    public static class WorldStreamingManifestValidator
    {
        private static readonly Regex SchemaRegex = new Regex("\\\"schemaVersion\\\"\\s*:\\s*(\\d+)", RegexOptions.Compiled);
        private static readonly Regex SubcellKeyRegex = new Regex("\\\"(SA_M\\d{2}_\\d{2}_S\\d{2}_\\d{2})\\\"\\s*:", RegexOptions.Compiled);
        private static readonly Regex SubcellRefRegex = new Regex("\\\"subcell\\\"\\s*:\\s*\\\"(SA_M\\d{2}_\\d{2}_S\\d{2}_\\d{2})\\\"", RegexOptions.Compiled);
        private static readonly Regex LotIdRegex = new Regex("\\\"id\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"\\s*,\\s*\\\"variant\\\"", RegexOptions.Compiled);
        private static readonly Regex HeroIdRegex = new Regex("\\\"id\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"", RegexOptions.Compiled);
        private static readonly Regex BuildingInstancesRegex = new Regex("\\\"buildingInstances\\\"\\s*:\\s*(\\d+)", RegexOptions.Compiled);
        private static readonly Regex ReportSubcellsRegex = new Regex("\\\"subcells\\\"\\s*:\\s*(\\d+)", RegexOptions.Compiled);

        [MenuItem("Facility Ops/World/Validate Streaming Manifest")]
        public static void ValidateFromMenu()
        {
            ValidateOrThrow();
            Debug.Log("WORLD STREAMING MANIFEST: PASS");
        }

        public static void ValidateOrThrow()
        {
            string repositoryRoot = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string worldRoot = Path.Combine(repositoryRoot, "ArtSource", "Blender", "World", "OldTown");
            string manifestPath = Path.Combine(worldRoot, "oldtown_streaming_manifest_v1.json");
            string heroesPath = Path.Combine(worldRoot, "oldtown_heroes_v1.json");
            string reportPath = Path.Combine(worldRoot, "oldtown_generation_report.json");

            var errors = new List<string>();
            if (!File.Exists(manifestPath)) errors.Add("Missing manifest: " + manifestPath);
            if (!File.Exists(heroesPath)) errors.Add("Missing hero registry: " + heroesPath);
            if (!File.Exists(reportPath)) errors.Add("Missing generation report: " + reportPath);
            if (errors.Count > 0)
                Fail(errors);

            string manifest = File.ReadAllText(manifestPath);
            string heroRegistry = File.ReadAllText(heroesPath);
            string report = File.ReadAllText(reportPath);

            if (!LooksLikeBalancedJsonObject(manifest))
                errors.Add("Manifest is not a balanced JSON object.");

            foreach (string required in new[] { "schemaVersion", "families", "props", "subcells", "heroes", "lots" })
                if (manifest.IndexOf("\"" + required + "\"", StringComparison.Ordinal) < 0)
                    errors.Add("Manifest missing top-level key: " + required);

            Match schema = SchemaRegex.Match(manifest);
            if (!schema.Success || schema.Groups[1].Value != "1")
                errors.Add("Unsupported or missing manifest schemaVersion (expected 1).");

            var subcellKeys = new HashSet<string>(
                SubcellKeyRegex.Matches(manifest).Cast<Match>().Select(m => m.Groups[1].Value),
                StringComparer.Ordinal);

            foreach (string cell in subcellKeys)
                if (!WorldStreamingId.TryParse(cell, out _))
                    errors.Add("Invalid subcell key: " + cell);

            var referencedCells = new HashSet<string>(
                SubcellRefRegex.Matches(manifest).Cast<Match>().Select(m => m.Groups[1].Value),
                StringComparer.Ordinal);

            foreach (string missing in referencedCells.Except(subcellKeys).Take(25))
                errors.Add("Manifest references a subcell that has no subcell entry: " + missing);

            var lotIds = LotIdRegex.Matches(manifest).Cast<Match>().Select(m => m.Groups[1].Value).ToList();
            foreach (var duplicate in lotIds.GroupBy(x => x, StringComparer.Ordinal).Where(g => g.Count() > 1).Take(25))
                errors.Add($"Duplicate lot id: {duplicate.Key} ({duplicate.Count()}x)");

            string heroesArray = ExtractNamedArray(heroRegistry, "heroes");
            if (heroesArray == null)
            {
                errors.Add("Hero registry is missing a readable heroes array.");
                heroesArray = string.Empty;
            }

            var expectedHeroes = HeroIdRegex.Matches(heroesArray).Cast<Match>()
                .Select(m => m.Groups[1].Value)
                .Distinct(StringComparer.Ordinal)
                .ToArray();

            foreach (string heroId in expectedHeroes)
                if (!Regex.IsMatch(manifest, "\\\"" + Regex.Escape(heroId) + "\\\"\\s*:"))
                    errors.Add("Hero registry id missing from manifest heroes: " + heroId);

            int expectedLots = ReadInt(BuildingInstancesRegex, report, "buildingInstances", errors);
            if (expectedLots >= 0 && lotIds.Count != expectedLots)
                errors.Add($"Lot count mismatch: manifest={lotIds.Count}, report={expectedLots}");

            int expectedSubcells = ReadInt(ReportSubcellsRegex, report, "subcells", errors);
            if (expectedSubcells >= 0 && subcellKeys.Count != expectedSubcells)
                errors.Add($"Subcell count mismatch: manifest={subcellKeys.Count}, report={expectedSubcells}");

            if (subcellKeys.Count == 0)
                errors.Add("Manifest contains no streaming subcells.");

            if (expectedHeroes.Length != 9)
                errors.Add("Expected exactly 9 Old Town hero locations, found " + expectedHeroes.Length + ".");

            if (errors.Count > 0)
                Fail(errors);

            Debug.Log(
                $"Streaming manifest validated: schema=1, subcells={subcellKeys.Count}, lots={lotIds.Count}, heroes={expectedHeroes.Length}. " +
                "No files were modified.");
        }

        private static string ExtractNamedArray(string json, string property)
        {
            int propertyIndex = json.IndexOf("\"" + property + "\"", StringComparison.Ordinal);
            if (propertyIndex < 0)
                return null;

            int start = json.IndexOf('[', propertyIndex);
            if (start < 0)
                return null;

            int depth = 0;
            bool inString = false;
            bool escape = false;

            for (int i = start; i < json.Length; i++)
            {
                char c = json[i];

                if (inString)
                {
                    if (escape) { escape = false; continue; }
                    if (c == '\\') { escape = true; continue; }
                    if (c == '"') inString = false;
                    continue;
                }

                if (c == '"') { inString = true; continue; }
                if (c == '[') depth++;
                else if (c == ']')
                {
                    depth--;
                    if (depth == 0)
                        return json.Substring(start, i - start + 1);
                    if (depth < 0)
                        return null;
                }
            }

            return null;
        }

        private static int ReadInt(Regex regex, string text, string field, List<string> errors)
        {
            Match match = regex.Match(text);
            if (!match.Success || !int.TryParse(match.Groups[1].Value, out int value))
            {
                errors.Add("Generation report missing integer field: " + field);
                return -1;
            }

            return value;
        }

        private static bool LooksLikeBalancedJsonObject(string text)
        {
            int depth = 0;
            bool inString = false;
            bool escape = false;
            bool sawObject = false;

            foreach (char c in text)
            {
                if (inString)
                {
                    if (escape) { escape = false; continue; }
                    if (c == '\\') { escape = true; continue; }
                    if (c == '"') inString = false;
                    continue;
                }

                if (c == '"') { inString = true; continue; }
                if (c == '{') { depth++; sawObject = true; }
                else if (c == '}')
                {
                    depth--;
                    if (depth < 0) return false;
                }
            }

            return sawObject && !inString && depth == 0;
        }

        private static void Fail(IReadOnlyCollection<string> errors)
        {
            string message = "WORLD STREAMING MANIFEST FAILED:\n- " + string.Join("\n- ", errors);
            Debug.LogError(message);
            throw new BuildFailedException(message);
        }
    }
}
