using ResortAurora.CameraSystem;
using ResortAurora.Game;
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

        const string ProloguePath = "Assets/_Game/Scenes/ResortPrologue.unity";

        /// <summary>Menu: Resort Aurora > Create Prologue Scene. The playable beach-stall stage (first person).</summary>
        [MenuItem("Resort Aurora/Create Prologue Scene")]
        public static void CreatePrologue()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional; sun.shadows = LightShadows.Soft; sun.intensity = 1.1f;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;

            var siteGo = new GameObject("ResortSite");
            var site = siteGo.AddComponent<ResortSite>();

            var playerGo = new GameObject("Player") { tag = "Player" };
            var cc = playerGo.AddComponent<CharacterController>();
            cc.height = 1.8f; cc.radius = 0.3f; cc.center = new Vector3(0f, 0.9f, 0f); cc.stepOffset = 0.35f;
            var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
            camGo.transform.SetParent(playerGo.transform, false);
            camGo.transform.localPosition = new Vector3(0f, 1.68f, 0f);
            var cam = camGo.AddComponent<Camera>();
            cam.nearClipPlane = 0.05f; cam.farClipPlane = 1500f; cam.fieldOfView = 70f;
            camGo.AddComponent<AudioListener>();
            var player = playerGo.AddComponent<PlayerController>();
            Set(player, "head", camGo.transform);

            var gameGo = new GameObject("ResortGame");
            var game = gameGo.AddComponent<ResortGame>();
            Set(game, "site", site); Set(game, "player", player); Set(game, "sun", sun);
            var hud = gameGo.AddComponent<ResortHud>();
            Set(hud, "game", game); Set(hud, "player", player);

            System.IO.Directory.CreateDirectory("Assets/_Game/Scenes");
            EditorSceneManager.SaveScene(scene, ProloguePath);
            Debug.Log("Resort Aurora: scene saved to " + ProloguePath);
        }

        public static void CreatePrologueBatch() => CreatePrologue();

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
