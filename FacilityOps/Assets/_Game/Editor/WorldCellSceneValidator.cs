using System;
using System.Collections.Generic;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps.Editor
{
    public static class WorldCellSceneValidator
    {
        private const string SceneRoot = "Assets/_Game/World/SantaAurora/OldTown/Cells";

        [MenuItem("Facility Ops/World/Validate Pilot Cell Scenes")]
        public static void ValidatePilotScenesFromMenu()
        {
            ValidatePilotScenes();
            Debug.Log("PILOT CELL SCENES: PASS");
        }

        public static void ValidatePilotScenes()
        {
            var errors = new List<string>();
            string[] guids = AssetDatabase.FindAssets("t:Scene", new[] { SceneRoot });

            if (guids.Length == 0)
            {
                Debug.Log("PILOT CELL SCENES: no scaffolds generated yet; validation skipped.");
                return;
            }

            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            Scene active = SceneManager.GetActiveScene();
            string activePath = active.path;

            try
            {
                foreach (string guid in guids)
                {
                    string path = AssetDatabase.GUIDToAssetPath(guid);
                    string file = Path.GetFileNameWithoutExtension(path);

                    if (!WorldStreamingSceneNaming.TryParseSceneName(file, out var expectedId))
                    {
                        errors.Add("Unexpected scene name under cell root: " + path);
                        continue;
                    }

                    Scene scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
                    WorldCellRoot[] roots = UnityEngine.Object.FindObjectsByType<WorldCellRoot>(FindObjectsInactive.Include, FindObjectsSortMode.None);

                    if (roots.Length != 1)
                    {
                        errors.Add($"{file}: expected exactly 1 WorldCellRoot, found {roots.Length}");
                        continue;
                    }

                    WorldCellRoot root = roots[0];
                    if (!root.TryGetStreamingId(out var actualId))
                    {
                        errors.Add(file + ": metadata has invalid cell id " + root.CellId);
                        continue;
                    }

                    if (actualId != expectedId)
                        errors.Add($"{file}: scene/metadata id mismatch ({expectedId} vs {actualId})");

                    if (root.transform.position != Vector3.zero ||
                        root.transform.rotation != Quaternion.identity ||
                        root.transform.localScale != Vector3.one)
                        errors.Add(file + ": cell root transform must be identity at world origin");

                    foreach (string layer in new[]
                    {
                        "Terrain", "Roads", "Architecture", "Infrastructure",
                        "Props", "Vegetation", "Lighting", "Gameplay"
                    })
                    {
                        if (root.transform.Find(layer) == null)
                            errors.Add(file + ": missing layer root " + layer);
                    }

                    WorldCellContentStamp stamp = root.GetComponent<WorldCellContentStamp>();
                    if (stamp == null)
                    {
                        errors.Add(file + ": missing WorldCellContentStamp; scene is still an empty/unvalidated scaffold");
                        continue;
                    }

                    if (!string.Equals(stamp.CellId, root.CellId, StringComparison.Ordinal))
                        errors.Add(file + ": content stamp cell id does not match WorldCellRoot");

                    if (!stamp.ImportValidated)
                        errors.Add(file + ": imported content stamp is not validated");

                    if (!stamp.TerrainPresent || !stamp.RoadsPresent || !stamp.ArchitecturePresent)
                        errors.Add(file + ": imported content stamp requires Terrain + Roads + Architecture");

                    if (stamp.ImportedObjectCount <= 0 || stamp.ImportedRendererCount <= 0)
                        errors.Add(file + ": imported cell has no real renderable content");

                    if (stamp.EstimatedTriangles <= 0)
                        errors.Add(file + ": imported cell triangle estimate is empty");
                }
            }
            finally
            {
                if (!string.IsNullOrEmpty(activePath) &&
                    AssetDatabase.LoadAssetAtPath<SceneAsset>(activePath) != null)
                    EditorSceneManager.OpenScene(activePath, OpenSceneMode.Single);
            }

            if (errors.Count > 0)
            {
                string message = "PILOT CELL SCENE VALIDATION FAILED:\n- " + string.Join("\n- ", errors);
                Debug.LogError(message);
                throw new BuildFailedException(message);
            }
        }
    }
}
