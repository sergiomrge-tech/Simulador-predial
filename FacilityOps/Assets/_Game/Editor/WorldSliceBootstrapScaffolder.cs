using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps.Editor
{
    public static class WorldSliceBootstrapScaffolder
    {
        public const string SourceBootstrap = "Assets/_Game/Scenes/Bootstrap.unity";
        public const string SliceBootstrap = "Assets/_Game/Scenes/WorldSliceBootstrap.unity";

        [MenuItem("Facility Ops/World/Create World Slice Bootstrap")]
        public static void Create()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(SourceBootstrap) == null)
                throw new FileNotFoundException("Bootstrap scene missing.", SourceBootstrap);

            string originalPath = SceneManager.GetActiveScene().path;

            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(SliceBootstrap) == null)
            {
                if (!AssetDatabase.CopyAsset(SourceBootstrap, SliceBootstrap))
                    throw new IOException("Could not copy Bootstrap to " + SliceBootstrap);
                AssetDatabase.Refresh();
            }

            try
            {
                Scene scene = EditorSceneManager.OpenScene(SliceBootstrap, OpenSceneMode.Single);
                GameRuntime game = Object.FindFirstObjectByType<GameRuntime>();
                if (game == null)
                    throw new MissingReferenceException("WorldSliceBootstrap requires one GameRuntime.");

                GameObject rig = GameObject.Find("World Slice Integration");
                if (rig == null)
                    rig = new GameObject("World Slice Integration");

                WorldStreamService service = rig.GetComponent<WorldStreamService>();
                if (service == null)
                    service = rig.AddComponent<WorldStreamService>();

                WorldStreamingDebugOverlay overlay = rig.GetComponent<WorldStreamingDebugOverlay>();
                if (overlay == null)
                    overlay = rig.AddComponent<WorldStreamingDebugOverlay>();

                WorldSliceRuntimeBridge bridge = rig.GetComponent<WorldSliceRuntimeBridge>();
                if (bridge == null)
                    bridge = rig.AddComponent<WorldSliceRuntimeBridge>();

                bridge.Configure(game, service, overlay);
                overlay.StreamService = service;

                EditorUtility.SetDirty(rig);
                EditorSceneManager.MarkSceneDirty(scene);
                if (!EditorSceneManager.SaveScene(scene))
                    throw new IOException("Could not save " + SliceBootstrap);

                Debug.Log(
                    "WORLD SLICE BOOTSTRAP READY: " + SliceBootstrap +
                    ". Normal Bootstrap was not modified.");
            }
            finally
            {
                if (!string.IsNullOrEmpty(originalPath) &&
                    AssetDatabase.LoadAssetAtPath<SceneAsset>(originalPath) != null)
                    EditorSceneManager.OpenScene(originalPath, OpenSceneMode.Single);
            }
        }
    }
}
