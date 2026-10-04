using System;
using System.Collections.Generic;
using System.Linq;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldCellBuildSettingsUtility
    {
        private const string SceneRoot = "Assets/_Game/World/SantaAurora/OldTown/Cells";

        [MenuItem("Facility Ops/World/Sync Cell Scenes To Build Settings")]
        public static void SyncCellScenes()
        {
            string[] guids = AssetDatabase.FindAssets("t:Scene", new[] { SceneRoot });
            var cellScenes = guids
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path =>
                    WorldStreamingSceneNaming.TryParseSceneName(
                        System.IO.Path.GetFileNameWithoutExtension(path),
                        out _))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToArray();

            if (cellScenes.Length == 0)
            {
                throw new InvalidOperationException("No generated cell scenes found.");
            }

            var existing = EditorBuildSettings.scenes.ToList();
            var existingPaths = new HashSet<string>(
                existing.Select(scene => scene.path),
                StringComparer.Ordinal);

            int added = 0;
            foreach (string path in cellScenes)
            {
                if (existingPaths.Contains(path))
                {
                    foreach (var scene in existing.Where(s => s.path == path)) scene.enabled = true;
                    continue;
                }

                existing.Add(new EditorBuildSettingsScene(path, true));
                existingPaths.Add(path);
                added++;
            }

            EditorBuildSettings.scenes = existing.ToArray();
            Debug.Log(
                $"World cell Build Settings sync complete: discovered={cellScenes.Length}, added={added}, totalBuildScenes={existing.Count}. " +
                "Existing non-cell scenes and their order were preserved.");
        }

        [MenuItem("Facility Ops/World/Validate Cell Scenes In Build Settings")]
        public static void ValidateCellScenesInBuildSettings()
        {
            var errors = new List<string>();
            var build = new HashSet<string>(
                EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path),
                StringComparer.Ordinal);

            string[] guids = AssetDatabase.FindAssets("t:Scene", new[] { SceneRoot });
            if (guids.Length != 15) errors.Add("Expected exactly 15 pilot scenes in Build Settings validation.");
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                string sceneName = System.IO.Path.GetFileNameWithoutExtension(path);
                if (!WorldStreamingSceneNaming.TryParseSceneName(sceneName, out _))
                    continue;

                if (!build.Contains(path))
                    errors.Add("Cell scene not enabled in Build Settings: " + path);
            }

            if (errors.Count > 0)
            {
                string message = "CELL BUILD SETTINGS VALIDATION FAILED:\n- " + string.Join("\n- ", errors);
                Debug.LogError(message);
                throw new UnityEditor.Build.BuildFailedException(message);
            }

            Debug.Log("CELL BUILD SETTINGS: PASS");
        }
    }
}
