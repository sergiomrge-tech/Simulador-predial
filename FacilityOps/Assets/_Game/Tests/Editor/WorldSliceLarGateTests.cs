using System;
using System.Collections;
using System.IO;
using FacilityOps.Editor;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.TestTools;

namespace FacilityOps.Tests
{
    public sealed class WorldSliceLarGateTests
    {
        [UnityTest]
        public IEnumerator Lar_Imported_Player_Grounds_And_Walks_On_Street()
        {
            if (Environment.GetEnvironmentVariable("FACILITY_LAR_QA") != "1")
                Assert.Ignore("Opt-in integration gate: set FACILITY_LAR_QA=1 after ImportLar.");
            EditorSceneManager.OpenScene(WorldCellSceneScaffolder.ScenePathFor(WorldSliceImportPipeline.HomeCell), OpenSceneMode.Single);
            yield return new EnterPlayMode();
            var root = UnityEngine.Object.FindAnyObjectByType<WorldCellRoot>();
            Assert.That(root, Is.Not.Null);
            Assert.That(root.GetComponent<WorldCellContentStamp>().ImportValidated, Is.True);
            var runtime = new GameObject("Lar QA / no career load or save").AddComponent<GameRuntime>();
            runtime.enabled = false;
            var player = new GameObject("Lar QA FirstPersonController").AddComponent<FirstPersonController>();
            player.Initialize(runtime);
            player.Teleport(WorldSliceDestinationRegistry.Require("home.starter").FallbackPosition);
            var controller = player.GetComponent<CharacterController>();
            Physics.SyncTransforms();
            Vector3 initial = player.transform.position;
            float vertical = 0f;
            for (int frame = 0; frame < 120; frame++)
            {
                if (controller.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * .02f;
                controller.Move(Vector3.up * vertical * .02f);
                yield return null;
            }
            Assert.That(controller.isGrounded, Is.True, "Player fell or did not find authored street collider");
            Assert.That(player.transform.position.y, Is.InRange(initial.y - 3f, initial.y + .3f));
            Vector3 start = player.transform.position;
            Capture(player.view, "Lar-runtime.png");
            for (int frame = 0; frame < 120; frame++)
            {
                if (controller.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * .02f;
                controller.Move((Vector3.right * 3f + Vector3.up * vertical) * .02f);
                yield return null;
            }
            Assert.That(controller.isGrounded, Is.True, "Player lost street collision while walking");
            Assert.That(player.transform.position.x - start.x, Is.GreaterThan(5f), "Street blocked by collider");
            Assert.That(player.transform.position.y, Is.GreaterThan(start.y - 3f));
            Capture(player.view, "Lar-street-runtime.png");
            string logs = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Logs"));
            Directory.CreateDirectory(logs);
            File.WriteAllText(Path.Combine(logs, "lar-playmode-gate.txt"),
                $"PASS\nUnity={Application.unityVersion}\nInitial={initial:F4}\nGrounded={start:F4}\nWalked={player.transform.position:F4}\n" +
                "Real CharacterController.Move in Play Mode. No player career loaded or saved.\n" +
                "Editor integration run; these frame times are not a standalone performance claim.\n");
            yield return new ExitPlayMode();
        }

        private static void Capture(Camera camera, string file)
        {
            var sun = new GameObject("Lar QA capture lighting").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1f;
            sun.transform.rotation = Quaternion.Euler(50f, -25f, 0f);
            var target = new RenderTexture(1280, 720, 24, RenderTextureFormat.ARGB32);
            target.Create();
            var previous = RenderTexture.active;
            try
            {
                RenderPipeline.SubmitRenderRequest(camera, new UniversalRenderPipeline.SingleCameraRequest { destination = target });
                RenderTexture.active = target;
                var image = new Texture2D(1280, 720, TextureFormat.RGB24, false);
                image.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); image.Apply();
                string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Docs/Previews/UnityValidation"));
                Directory.CreateDirectory(folder);
                File.WriteAllBytes(Path.Combine(folder, file), image.EncodeToPNG());
                UnityEngine.Object.Destroy(image);
            }
            finally
            {
                RenderTexture.active = previous;
                target.Release(); UnityEngine.Object.Destroy(target); UnityEngine.Object.Destroy(sun.gameObject);
            }
        }
    }
}
