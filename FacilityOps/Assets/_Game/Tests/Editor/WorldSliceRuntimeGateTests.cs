using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using FacilityOps.Editor;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace FacilityOps.Tests
{
    public sealed class WorldSliceRuntimeGateTests
    {
        [Serializable] public sealed class Sample
        {
            public string location; public Vector3 grounded; public int cells, scenes, loads, unloads;
            public float fps, maxFrameMs; public double loadMs, unloadMs;
            public long memoryBytes, reservedBytes, gcBytes, drawCalls, visibleTriangles;
        }
        [Serializable] public sealed class Report
        {
            public string status, fingerprint, unityVersion, device, scope, panelCollider, interaction;
            public bool initialRootPreserved, initialLoadReady, uniqueScenes, panelReachable;
            public Sample[] samples;
        }

        [UnityTest, Timeout(600000)]
        public IEnumerator Streamed_Corridor_And_Horizonte_Physical_Gate()
        {
            if (Environment.GetEnvironmentVariable("FACILITY_WORLD_QA") != "1")
                Assert.Ignore("Opt-in: FACILITY_WORLD_QA=1 with -worldSlice -worldSliceQa after ImportPilot.");
            EditorSceneManager.OpenScene(WorldSliceBootstrapScaffolder.SliceBootstrap, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            var bridge = UnityEngine.Object.FindAnyObjectByType<WorldSliceRuntimeBridge>();
            var game = UnityEngine.Object.FindAnyObjectByType<GameRuntime>();
            var service = UnityEngine.Object.FindAnyObjectByType<WorldStreamService>();
            var overlay = UnityEngine.Object.FindAnyObjectByType<WorldStreamingDebugOverlay>();
            var report = new Report { unityVersion = Application.unityVersion, device = SystemInfo.graphicsDeviceName,
                scope = "Unity Editor Play Mode; timed teleport/load cycles, CharacterController gravity and corridor walk. Not a continuous town walk or standalone benchmark.",
                initialRootPreserved = true, uniqueScenes = true };
            float deadline = Time.realtimeSinceStartup + 60f;
            while (!bridge.Active && Time.realtimeSinceStartup < deadline)
            {
                if (game.World?.Root != null && !game.World.Root.activeSelf) report.initialRootPreserved = false;
                yield return null;
            }
            Assert.That(bridge.LastError, Is.Null);
            Assert.That(bridge.Active, Is.True, "Initial streamed cell timed out");
            report.initialLoadReady = service.IsLoaded(WorldSliceDestinationRegistry.Require("home.starter").Cell);
            Assert.That(game.World.Root.activeSelf, Is.False);
            // Freeze input only, leaving GameRuntime, renderer, bridge and streamer live.
            game.Player.enabled = false;
            var controller = game.Player.GetComponent<CharacterController>();
            var samples = new List<Sample>();
            foreach (string id in new[] { "home.starter", "garage", "horizonte", "grocery", "home.starter", "horizonte", "home.starter" })
            {
                var destination = WorldSliceDestinationRegistry.Require(id);
                service.StreamingEnabled = false;
                service.Refresh(destination.Cell);
                deadline = Time.realtimeSinceStartup + 45f;
                while (!service.IsLoaded(destination.Cell) && Time.realtimeSinceStartup < deadline) yield return null;
                Assert.That(service.IsLoaded(destination.Cell), Is.True, id + " cell missing");
                game.Player.Teleport(destination.FallbackPosition, destination.FallbackYaw);
                service.StreamingEnabled = true;
                yield return Settle(controller);
                yield return new WaitForSecondsRealtime(2f);
                Assert.That(controller.isGrounded, Is.True, id + " floor missing");
                var names = new HashSet<string>();
                for (int i = 0; i < SceneManager.sceneCount; i++)
                    if (!names.Add(SceneManager.GetSceneAt(i).path)) report.uniqueScenes = false;
                samples.Add(Snapshot(id, game.Player, service, overlay));
                Vector3 aim = destination.FallbackPosition + Quaternion.Euler(0, destination.FallbackYaw, 0) * Vector3.forward * 15f + Vector3.up * 3f;
                if (id == "home.starter") aim = new Vector3(-2860f, 22f, -2285f);
                if (id == "garage") aim = new Vector3(-2690f, 25f, -2150f);
                if (id == "horizonte") aim = new Vector3(-2350f, 45f, -1800f);
                if (id == "grocery") aim = new Vector3(-2580f, 28f, -1480f);
                Capture(game.Player.view, aim, id.Replace('.', '-') + "-runtime.png");
                if (id == "home.starter") Capture(game.Player.view, game.Player.transform.position + Vector3.right * 40f + Vector3.up * 2f, "street-runtime.png");
                Debug.Log("WORLD RUNTIME QA SAMPLE: " + JsonUtility.ToJson(samples[samples.Count - 1]));
            }
            game.Accept();
            yield return null;
            deadline = Time.realtimeSinceStartup + 45f;
            while (game.World.Root.activeSelf && Time.realtimeSinceStartup < deadline) yield return null;
            Assert.That(game.World.Root.activeSelf, Is.False, "Prologue context did not finish streaming route");
            var horizon = WorldSliceDestinationRegistry.Require("horizonte");
            service.StreamingEnabled = false; service.Refresh(horizon.Cell);
            deadline = Time.realtimeSinceStartup + 45f;
            while (!service.IsLoaded(horizon.Cell) && Time.realtimeSinceStartup < deadline) yield return null;
            WorldGameplayMarker spawn = null, panel = null;
            foreach (var marker in UnityEngine.Object.FindObjectsByType<WorldGameplayMarker>(FindObjectsSortMode.None))
            {
                if (marker.MarkerName.EndsWith("GP_prologue_spawn_corridor", StringComparison.Ordinal)) spawn = marker;
                if (marker.MarkerName.EndsWith("GP_quadro_tecnico", StringComparison.Ordinal)) panel = marker;
            }
            Assert.That(spawn, Is.Not.Null); Assert.That(panel, Is.Not.Null);
            game.Player.Teleport(spawn.transform.position, spawn.transform.eulerAngles.y);
            service.StreamingEnabled = true;
            yield return Settle(controller);
            Capture(game.Player.view, panel.transform.position, "horizonte-corridor-runtime.png");
            Vector3 target = panel.transform.position + panel.transform.forward - Vector3.up * 1.4f;
            float vertical = 0f;
            deadline = Time.realtimeSinceStartup + 12f;
            while (Vector2.Distance(new Vector2(game.Player.transform.position.x, game.Player.transform.position.z), new Vector2(target.x, target.z)) > .35f && Time.realtimeSinceStartup < deadline)
            {
                Vector3 direction = target - game.Player.transform.position; direction.y = 0f;
                if (controller.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * Time.deltaTime;
                controller.Move((direction.normalized * 3f + Vector3.up * vertical) * Time.deltaTime);
                yield return null;
            }
            report.panelReachable = Vector3.Distance(game.Player.transform.position, target) < 1f && controller.isGrounded;
            game.Player.AimAt(panel.transform.position);
            game.Player.RefreshFocus();
            report.interaction = game.Player.Focus?.GetType().Name ?? "NONE";
            if (game.Player.Focus != null)
            {
                game.Player.Focus.Interact(game);
                Assert.That(game.Notice, Does.Contain("QD-01"), "Raycast focus must use original prologue station logic");
            }
            if (Physics.Raycast(game.Player.view.transform.position, game.Player.view.transform.forward, out var hit, 3f))
                report.panelCollider = hit.collider.name;
            Capture(game.Player.view, panel.transform.position, "horizonte-panel-runtime.png");
            samples.Add(Snapshot("horizonte.quadro", game.Player, service, overlay));
            report.samples = samples.ToArray();
            report.fingerprint = WorldSliceBuildGate.Fingerprint();
            report.status = report.initialRootPreserved && report.initialLoadReady && report.uniqueScenes && report.panelReachable && report.interaction != "NONE" ? "PASS" : "FAIL";
            string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Logs"));
            Directory.CreateDirectory(folder);
            File.WriteAllText(Path.Combine(folder, "world-runtime-qa.json"), JsonUtility.ToJson(report, true));
            Debug.Log("WORLD RUNTIME QA: " + report.status);
            yield return new ExitPlayMode();
            Assert.That(report.initialRootPreserved && report.initialLoadReady && report.uniqueScenes, Is.True);
            Assert.That(report.panelReachable, Is.True, "Cannot walk from spawn to panel approach on authored colliders");
            Assert.That(report.interaction, Is.Not.EqualTo("NONE"), "Authored panel is not bound to IInteractable");
        }

        private static IEnumerator Settle(CharacterController controller)
        {
            Physics.SyncTransforms(); float vertical = 0f;
            for (int i = 0; i < 90; i++)
            {
                if (controller.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * .02f; controller.Move(Vector3.up * vertical * .02f);
                yield return null;
            }
        }
        private static Sample Snapshot(string id, FirstPersonController player, WorldStreamService service, WorldStreamingDebugOverlay overlay) => new Sample
        {
            location = id, grounded = player.transform.position, cells = service.LoadedCells.Count, scenes = SceneManager.sceneCount,
            loads = service.TotalLoads, unloads = service.TotalUnloads, fps = overlay.FramesPerSecond, maxFrameMs = overlay.MaximumFrameMilliseconds,
            loadMs = service.MaxLoadMilliseconds, unloadMs = service.MaxUnloadMilliseconds, memoryBytes = overlay.AllocatedMemoryBytes,
            reservedBytes = overlay.ReservedMemoryBytes, gcBytes = overlay.GcBytesLastFrame, drawCalls = overlay.DrawCallsLastFrame,
            visibleTriangles = overlay.VisibleTrianglesLastFrame
        };
        private static void Capture(Camera camera, Vector3 aim, string file)
        {
            camera.transform.LookAt(aim); camera.ResetWorldToCameraMatrix(); camera.ResetProjectionMatrix();
            Canvas.ForceUpdateCanvases();
            var target = new RenderTexture(1280, 720, 24, RenderTextureFormat.ARGB32); target.Create();
            var previous = RenderTexture.active;
            var image = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            try
            {
                RenderPipeline.SubmitRenderRequest(camera, new UniversalRenderPipeline.SingleCameraRequest { destination = target });
                RenderTexture.active = target; image.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); image.Apply();
                string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Docs/Previews/UnityValidation"));
                Directory.CreateDirectory(folder); File.WriteAllBytes(Path.Combine(folder, file), image.EncodeToPNG());
            }
            finally { RenderTexture.active = previous; target.Release(); UnityEngine.Object.Destroy(target); UnityEngine.Object.Destroy(image); }
        }
    }
}
