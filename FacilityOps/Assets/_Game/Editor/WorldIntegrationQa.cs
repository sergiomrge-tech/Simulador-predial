using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FacilityOps;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldIntegrationQa
    {
        private const string SceneRoot = "Assets/_Game/World/SantaAurora/OldTown/Cells";
        private const int ExpectedPilotScenes = 15;

        [MenuItem("Facility Ops/World/Run Pilot Integration QA")]
        public static void RunPilotGateFromMenu()
        {
            RunPilotGate(true);
        }

        public static void RunPilotGateBatch()
        {
            RunPilotGate(false);
        }

        public static void RunPilotGate(bool showDialog)
        {
            var checks = new List<string>();
            try
            {
                WorldStreamingManifestValidator.ValidateOrThrow();
                checks.Add("streaming_manifest");

                string[] scenePaths = PilotScenePaths();
                Require(scenePaths.Length == ExpectedPilotScenes,
                    $"Expected {ExpectedPilotScenes} pilot cell scenes, found {scenePaths.Length}");
                checks.Add("pilot_scene_count");

                WorldCellSceneValidator.ValidatePilotScenes();
                checks.Add("pilot_scene_structure");
                WorldCellBuildSettingsUtility.ValidateCellScenesInBuildSettings();
                checks.Add("pilot_build_settings");

                ProjectBuilder.RunRules();
                checks.Add("existing_gameplay_rules");

                WriteReport("PASS", checks, null, scenePaths.Length);
                Debug.Log("WORLD INTEGRATION QA: PASS");

                if (showDialog)
                    EditorUtility.DisplayDialog(
                        "Facility Ops",
                        "Pilot world integration QA passed.",
                        "OK");
            }
            catch (Exception ex)
            {
                WriteReport("FAIL", checks, ex.ToString(), PilotScenePaths().Length);
                Debug.LogError("WORLD INTEGRATION QA: FAIL\n" + ex);

                if (showDialog)
                    EditorUtility.DisplayDialog(
                        "Facility Ops",
                        "Pilot world integration QA failed. Check Console and Logs/world-integration-qa.json.",
                        "OK");

                throw;
            }
        }

        public static string[] PilotScenePaths()
        {
            if (!AssetDatabase.IsValidFolder(SceneRoot)) return Array.Empty<string>();
            return AssetDatabase.FindAssets("t:Scene", new[] { SceneRoot })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path =>
                    WorldStreamingSceneNaming.TryParseSceneName(
                        Path.GetFileNameWithoutExtension(path),
                        out _))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToArray();
        }

        private static void Require(bool condition, string message)
        {
            if (!condition)
                throw new BuildFailedException(message);
        }

        private static void WriteReport(
            string status,
            IReadOnlyList<string> checks,
            string error,
            int sceneCount)
        {
            string logs = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "Logs"));
            Directory.CreateDirectory(logs);
            string path = Path.Combine(logs, "world-integration-qa.json");

            var report = new QaReport
            {
                schemaVersion = 1,
                status = status,
                unityVersion = Application.unityVersion,
                utc = DateTime.UtcNow.ToString("O"),
                pilotSceneCount = sceneCount,
                checks = checks.ToArray(),
                error = error
            };
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
        }

        [Serializable]
        private sealed class QaReport
        {
            public int schemaVersion;
            public string status;
            public string unityVersion;
            public string utc;
            public int pilotSceneCount;
            public string[] checks;
            public string error;
        }
    }
}
