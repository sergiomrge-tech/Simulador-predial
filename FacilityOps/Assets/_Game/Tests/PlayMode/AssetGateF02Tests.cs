using System.Collections;
using System.IO;
using System.Linq;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEditor.SceneManagement;

namespace ResortAurora.Tests
{
    /// <summary>Asset integration checks, not final visual gate approval.</summary>
    public sealed class AssetGateF02Tests
    {
        string save;
        [SetUp] public void Setup()
        {
            save = Path.Combine(Path.GetTempPath(), "asset_gate_f02_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", save);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", "1");
            Time.timeScale = 1f;
        }
        [TearDown] public void Cleanup()
        {
            Time.timeScale = 1f;
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            if (File.Exists(save)) File.Delete(save);
        }
        static IEnumerator Load()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
            yield return null; yield return null;
            Object.FindAnyObjectByType<ResortGame>().OpenPanel(Panel.Help);
        }
        static void Capture(Camera cam, Vector3 from, Vector3 at, string name)
        {
            var folder = System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT");
            if (string.IsNullOrEmpty(folder)) return;
            folder = Path.Combine(folder, "AssetGateF02"); Directory.CreateDirectory(folder);
            cam.transform.SetPositionAndRotation(from, Quaternion.LookRotation(at - from));
            var old = cam.targetTexture; var active = RenderTexture.active;
            var rt = new RenderTexture(1600, 900, 24);
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            try
            {
                cam.targetTexture = rt; cam.Render(); RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
                File.WriteAllBytes(Path.Combine(folder, name + ".png"), tex.EncodeToPNG());
            }
            finally { cam.targetTexture = old; RenderTexture.active = active; Object.Destroy(rt); Object.Destroy(tex); }
        }

        [UnityTest] public IEnumerator ScannedAdultsRetargetHBMAndKeepOriginalUVs()
        {
            if (Resources.Load<GameObject>("RealisticHumans/Eric") == null || Resources.Load<GameObject>("RealisticHumans/Carla") == null)
                Assert.Ignore("Local licensed scans missing: human asset gate remains open.");
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>(); game.Clock.Restore(1, 720f);
            var root = game.Layout.Root.position;
            foreach (bool female in new[] { false, true })
            {
                var parent = new GameObject("ScannedAdult_ValidationRig");
                parent.transform.position = game.Layout.Ground(root + new Vector3(4f, 0f, 5f));
                var hv = HumanVisual.Create(parent.transform, new HumanVisual.Look { female = female, realisticEligible = true, scale = 1f }, new System.Random(43));
                Assert.NotNull(hv); Assert.IsTrue(hv.IsRealistic); Assert.IsTrue(hv.Animator.isHuman);
                hv.Show(true); hv.Drive(HumanVisual.Clip.Walk, 1.45f, 1f, 0.5f);
                yield return new WaitForSeconds(0.1f);
                var renderer = hv.GetComponentInChildren<SkinnedMeshRenderer>();
                var source = Resources.Load<GameObject>("RealisticHumans/" + hv.RealisticVariant).GetComponentInChildren<SkinnedMeshRenderer>();
                Assert.AreSame(source.sharedMesh, renderer.sharedMesh, "scan UVs/weights stay unchanged; palette painting is bypassed");
                Assert.NotNull(renderer.sharedMaterial.GetTexture("_BaseMap"));
                Assert.NotNull(renderer.sharedMaterial.GetTexture("_BumpMap"));
                Assert.NotNull(renderer.sharedMaterial.GetTexture("_MetallicGlossMap"));
                Assert.That(renderer.bounds.size.y, Is.InRange(1.45f, 1.95f), "adult metric scale");
                var mesh = new Mesh(); renderer.BakeMesh(mesh); var before = mesh.vertices; float time = hv.ClipTime;
                yield return new WaitForSeconds(0.37f);
                renderer.BakeMesh(mesh); var after = mesh.vertices;
                Assert.Greater(hv.ClipTime, time, "HBM playable advances on the retargeted avatar");
                Assert.Greater(before.Zip(after, (a,b) => Vector3.Distance(a,b)).Max(), 0.01f, "skinned vertices actually move, not just an animation flag");
                var pos = parent.transform.position;
                Capture(Camera.main, pos + new Vector3(0.15f, 1.6f, 1.15f), pos + new Vector3(0f, 1.5f, 0f), female ? "human_female_close" : "human_male_close");
                Capture(Camera.main, pos + new Vector3(0f, 1.35f, 3.1f), pos + new Vector3(0f, 1f, 0f), female ? "human_female_medium" : "human_male_medium");
                hv.Show(false); Object.Destroy(parent); Object.Destroy(mesh); yield return null;
            }
        }

        [UnityTest] public IEnumerator DeckFurnitureMatchesTenSeatAnchors()
        {
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>();
            Assert.IsTrue(RealisticKioskAssets.DeckAssetsAvailable);
            game.Stages.SetStage(2); game.Layout.SetKioskLook(true);
            yield return null;
            var shell = game.Stages.Instances.Single(g => g.name == "E2-7_quiosque");
            var furniture = shell.GetComponentsInChildren<Transform>();
            Assert.AreEqual(5, furniture.Count(t => t.name == "F02_DeckTable"));
            var chairs = furniture.Where(t => t.name == "F02_DeckChair").ToArray();
            Assert.AreEqual(10, chairs.Length);
            var seats = game.Layout.Seats.Where(s => s.Kiosk).ToArray();
            Assert.AreEqual(10, seats.Length);
            foreach (var seat in seats)
            {
                Assert.Less(chairs.Min(t => Vector3.Distance(t.position, seat.Pos)), .01f, "chair feet match existing customer root anchor");
                Assert.IsTrue(seat.Enabled);
            }
            foreach (var chair in chairs)
            {
                Assert.NotNull(chair.GetComponent<BoxCollider>());
                var renderer = chair.GetComponentInChildren<MeshRenderer>();
                Assert.NotNull(renderer.sharedMaterial.GetTexture("_BaseMap"));
                Assert.That(renderer.bounds.size.y, Is.InRange(.7f, 1.2f));
            }
            game.Clock.Restore(1, 720f); yield return null;
            var pos = game.Layout.Root.position;
            Capture(Camera.main, pos + new Vector3(13f, 3f, 2f), pos + new Vector3(7f, .8f, -4f), "deck_furniture_day");
            game.Clock.Restore(1, 1260f); yield return null;
            Capture(Camera.main, pos + new Vector3(13f, 3f, 2f), pos + new Vector3(7f, .8f, -4f), "deck_furniture_night");
            game.Stages.SetStage(1); yield return null;
            Assert.IsFalse(shell.activeSelf);
        }

        [UnityTest] public IEnumerator ShelfBottlesKeepStationsAndCannotRevealFallbacks()
        {
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>(); var root = game.Layout.Root;
            var bottles = root.GetComponentsInChildren<Transform>(true).Where(t => t.name == "S1_CC0ShelfBottle").ToArray();
            var fallback = root.GetComponentsInChildren<MeshRenderer>(true).Where(r => r.name == "S1_BottleFallback").ToArray();
            Assert.AreEqual(24, bottles.Length); Assert.AreEqual(24, fallback.Length);
            Assert.AreEqual(5, root.GetComponentsInChildren<Transform>(true).Count(t => t.name == "S1_CC0Crate" && t.parent == root));
            Assert.NotNull(root.Find("S1_CC0Register"));
            var renderer = bottles[0].GetComponentInChildren<MeshRenderer>();
            Assert.That(renderer.bounds.size.y, Is.InRange(0.25f, 0.27f));
            Assert.IsTrue(fallback.All(r => !r.enabled));
            Assert.NotNull(root.Find("Counter").GetComponent<CounterStation>());
            Assert.NotNull(root.Find("Cooler").GetComponent<ActionStation>());
            Assert.NotNull(root.Find("S1_Fridge").GetComponent<ActionStation>());
            foreach (var bottle in bottles)
            {
                Assert.AreSame(renderer.sharedMaterial, bottle.GetComponentInChildren<MeshRenderer>().sharedMaterial);
                Assert.IsNull(bottle.GetComponent<Collider>(), "shelf dressing does not add physics cost");
            }
            game.Layout.SetKioskLook(true); yield return null;
            Assert.IsTrue(bottles.All(t => !t.GetComponentInChildren<MeshRenderer>().enabled));
            game.Layout.SetKioskLook(false); yield return null;
            Assert.IsTrue(fallback.All(r => !r.enabled), "returning stage cannot overlap cylinders with scans");
            game.Clock.Restore(1, 720f); yield return null;
            var pos = root.position;
            Capture(Camera.main, pos + new Vector3(1.5f, 1.65f, 4.5f), pos + new Vector3(-0.2f, 1.2f, -1.1f), "kiosk_counter_close");
            Debug.Log("ASSET_GATE: 24 CC0 shelf bottles, shared 512 maps/mesh; stations preserved. Visual gate remains separate.");
        }
    }
}
