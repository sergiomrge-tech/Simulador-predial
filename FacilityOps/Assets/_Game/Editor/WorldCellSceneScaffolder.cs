using System;
using System.Collections.Generic;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps.Editor
{
    public static class WorldCellSceneScaffolder
    {
        private const string SceneRoot = "Assets/_Game/World/SantaAurora/OldTown/Cells";
        private static readonly string[] PilotCells =
        {
            "SA_M01_01_S00_02",
            "SA_M01_01_S01_02",
            "SA_M01_01_S02_02",
            "SA_M01_01_S00_03",
            "SA_M01_01_S01_03",
            "SA_M01_01_S02_03",
            "SA_M01_02_S00_00",
            "SA_M01_02_S01_00",
            "SA_M01_02_S02_00",
            "SA_M01_02_S00_01",
            "SA_M01_02_S01_01",
            "SA_M01_02_S02_01",
            "SA_M01_02_S00_02",
            "SA_M01_02_S01_02",
            "SA_M01_02_S02_02"
        };

        private static readonly HashSet<string> HeroCells = new HashSet<string>(StringComparer.Ordinal)
        {
            "SA_M01_01_S00_02", // Lar
            "SA_M01_01_S01_03", // Oficina Aurora
            "SA_M01_02_S02_00", // Horizonte
            "SA_M01_02_S01_02"  // Mercearia
        };

        [MenuItem("Facility Ops/World/Create Pilot Cell Scene Scaffolds")]
        public static void CreatePilotScaffolds()
        {
            if (!EditorUtility.DisplayDialog(
                    "Facility Ops",
                    "Create missing additive Scene scaffolds for the 15-cell Old Town pilot corridor? Existing scenes will not be overwritten.",
                    "Create",
                    "Cancel"))
                return;

            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureAssetFolder(SceneRoot);

            Scene original = SceneManager.GetActiveScene();
            string originalPath = original.path;
            int created = 0;
            int skipped = 0;

            try
            {
                foreach (string cell in PilotCells)
                {
                    if (!WorldStreamingId.TryParse(cell, out var id))
                        throw new InvalidDataException("Invalid pilot cell id: " + cell);

                    string folder = SceneRoot + "/" + cell;
                    EnsureAssetFolder(folder);

                    string sceneName = WorldStreamingSceneNaming.SceneName(id);
                    string scenePath = folder + "/" + sceneName + ".unity";

                    if (AssetDatabase.LoadAssetAtPath<SceneAsset>(scenePath) != null)
                    {
                        skipped++;
                        continue;
                    }

                    Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                    var root = new GameObject(sceneName);
                    var metadata = root.AddComponent<WorldCellRoot>();
                    metadata.Configure(cell, HeroCells.Contains(cell), HeroCells.Contains(cell));
                    root.transform.position = Vector3.zero;

                    CreateLayerRoot(root.transform, "Terrain");
                    CreateLayerRoot(root.transform, "Roads");
                    CreateLayerRoot(root.transform, "Architecture");
                    CreateLayerRoot(root.transform, "Infrastructure");
                    CreateLayerRoot(root.transform, "Props");
                    CreateLayerRoot(root.transform, "Vegetation");
                    CreateLayerRoot(root.transform, "Lighting");
                    CreateLayerRoot(root.transform, "Gameplay");

                    if (!EditorSceneManager.SaveScene(scene, scenePath))
                        throw new IOException("Could not save cell scene: " + scenePath);

                    created++;
                }
            }
            finally
            {
                if (!string.IsNullOrEmpty(originalPath) &&
                    AssetDatabase.LoadAssetAtPath<SceneAsset>(originalPath) != null)
                    EditorSceneManager.OpenScene(originalPath, OpenSceneMode.Single);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Pilot cell scaffolds complete: created={created}, skipped existing={skipped}. No Build Settings were changed.");
        }

        private static void CreateLayerRoot(Transform parent, string layer)
        {
            var go = new GameObject(layer);
            go.transform.SetParent(parent, false);
        }

        private static void EnsureAssetFolder(string path)
        {
            string[] parts = path.Split('/');
            string current = parts[0];

            for (int i = 1; i < parts.Length; i++)
            {
                string next = current + "/" + parts[i];
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, parts[i]);
                current = next;
            }
        }
    }
}
