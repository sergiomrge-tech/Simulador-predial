using ResortAurora.CameraSystem;
using ResortAurora.Grid;
using ResortAurora.Placement;
using ResortAurora.Site;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ResortAurora.EditorTools
{
    /// <summary>Menu: Resort Aurora > Create Site Scene. Builds Assets/_Game/Scenes/ResortSite.unity wired and ready to press Play.</summary>
    public static class ResortSceneBuilder
    {
        const string ScenePath = "Assets/_Game/Scenes/ResortSite.unity";

        [MenuItem("Resort Aurora/Create Site Scene")]
        public static void Create()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.1f;
            sun.color = new Color(1f, 0.96f, 0.88f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(50f, -35f, 0f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.55f, 0.62f, 0.7f);

            var gridGo = new GameObject("Grid");
            var grid = gridGo.AddComponent<GridManager>();

            var rig = new GameObject("CameraRig");
            var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
            camGo.transform.SetParent(rig.transform, false);
            var cam = camGo.AddComponent<Camera>();
            cam.farClipPlane = 1500f;
            cam.clearFlags = CameraClearFlags.Skybox;
            camGo.AddComponent<AudioListener>();
            var controller = rig.AddComponent<CameraController>();

            var siteGo = new GameObject("ResortSite");
            var site = siteGo.AddComponent<ResortSite>();
            Set(site, "grid", grid);
            Set(site, "cameraController", controller);

            var placement = new GameObject("Placement").AddComponent<PlacementSystem>();
            Set(placement, "gridManager", grid);

            System.IO.Directory.CreateDirectory("Assets/_Game/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log("Resort Aurora: scene saved to " + ScenePath);
        }

        static void Set(Object target, string field, Object value)
        {
            var so = new SerializedObject(target);
            so.FindProperty(field).objectReferenceValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        /// <summary>Batch entry point: Unity -batchmode -executeMethod ResortAurora.EditorTools.ResortSceneBuilder.CreateBatch</summary>
        public static void CreateBatch() => Create();
    }
}
