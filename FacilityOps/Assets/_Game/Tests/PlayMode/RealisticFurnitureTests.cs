using System.Collections;
using System.IO;
using System.Linq;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;

namespace ResortAurora.Tests
{
    public sealed class RealisticFurnitureTests
    {
        string save;
        [SetUp] public void SetUp()
        {
            save = Path.Combine(Path.GetTempPath(), "resort_furniture_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", save);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", "1");
        }
        [TearDown] public void TearDown()
        {
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            if (File.Exists(save)) File.Delete(save);
        }
        static IEnumerator Load()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
            yield return null; yield return null;
        }
        static void Capture(Camera camera, string name)
        {
            var folder = System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT");
            if (string.IsNullOrEmpty(folder)) return;
            folder = Path.Combine(folder, "RealisticFurniture"); Directory.CreateDirectory(folder);
            var previous = camera.targetTexture; var active = RenderTexture.active;
            var rt = new RenderTexture(1600, 900, 24); var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            try
            {
                camera.targetTexture = rt; camera.Render(); RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
                File.WriteAllBytes(Path.Combine(folder, name + ".png"), tex.EncodeToPNG());
            }
            finally { camera.targetTexture = previous; RenderTexture.active = active; Object.Destroy(rt); Object.Destroy(tex); }
        }

        [UnityTest] public IEnumerator FurnitureIsMetreScaledAndKeepsUpgradeAndStageBehavior()
        {
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>(); var root = game.Layout.Root;
            game.OpenPanel(Panel.Help);
            var tables = root.GetComponentsInChildren<MeshRenderer>(true).Where(r => r.name == "S1_RealisticTable").ToArray();
            var chairs = root.GetComponentsInChildren<MeshRenderer>(true).Where(r => r.name == "S1_RealisticChair").ToArray();
            Assert.AreEqual(3, tables.Length); Assert.AreEqual(6, chairs.Length);
            Assert.That(tables[0].bounds.size.y, Is.InRange(0.70f, 0.75f), "table is physically scaled in metres");
            Assert.That(chairs[0].bounds.size.y, Is.InRange(0.83f, 0.89f), "chair is physically scaled in metres");
            foreach (var r in chairs.Concat(tables))
            {
                var m = r.sharedMaterial;
                Assert.NotNull(m.GetTexture("_BaseMap")); Assert.NotNull(m.GetTexture("_BumpMap")); Assert.NotNull(m.GetTexture("_MetallicGlossMap"));
                Assert.IsTrue(m.IsKeywordEnabled("_NORMALMAP")); Assert.IsTrue(m.IsKeywordEnabled("_METALLICSPECGLOSSMAP"));
                Assert.NotNull(r.GetComponentInParent<LODGroup>(true), "distance culling remains available");
            }
            Assert.AreSame(tables[0].sharedMaterial, tables[1].sharedMaterial);
            Assert.AreSame(chairs[0].GetComponent<MeshFilter>().sharedMesh, chairs[1].GetComponent<MeshFilter>().sharedMesh);
            Assert.AreEqual(2, game.Layout.Seats.Count(s => s.Enabled));
            Assert.AreEqual(2, game.Layout.ExtraTables.Count); Assert.IsTrue(game.Layout.ExtraTables.All(t => !t.activeSelf));
            game.Ledger.Add(1, "test furniture upgrade", 5000);
            Assert.IsTrue(game.Stall.BuyUpgrade("up.mesas", game.Ledger, 1)); game.Layout.RefreshUpgrades(game);
            Assert.AreEqual(6, game.Layout.Seats.Count(s => s.Enabled)); Assert.IsTrue(game.Layout.ExtraTables.All(t => t.activeSelf));
            Assert.NotNull(root.Find("S1_Table/S1_TableTop").GetComponent<BoxCollider>());
            var promenade = GameObject.Find("PromenadePBR"); Assert.NotNull(promenade);
            Assert.IsNull(promenade.GetComponent<Collider>(), "existing terrain supplies collision");
            var camera = Camera.main; var pos = root.position;
            foreach (float hour in new[] { 12f, 20.5f })
            {
                game.Clock.Restore(1, hour * 60f);
                camera.transform.SetPositionAndRotation(pos + new Vector3(8f, 1.65f, 4f), Quaternion.LookRotation(pos + new Vector3(4.5f, 0.7f, -1.8f) - (pos + new Vector3(8f, 1.65f, 4f))));
                yield return new WaitForSeconds(0.6f);
                Capture(camera, hour < 18f ? "tables_day" : "tables_night");
                if (hour > 18f)
                {
                    Assert.AreEqual("ResortAurora/Sky", RenderSettings.skybox.shader.name);
                    var horizon = RenderSettings.skybox.GetColor("_Horizon");
                    Assert.Greater(horizon.b, horizon.r * 1.5f, "Atlantic night horizon stays navy, not olive");
                }
            }
            game.Layout.SetKioskLook(true);
            yield return null;
            Assert.IsTrue(chairs.Concat(tables).All(r => !r.enabled), "stage change hides all stage-one furniture");
            game.Layout.SetKioskLook(false);
            Assert.IsTrue(chairs.Concat(tables).All(r => r.enabled));
            Assert.IsNull(root.Find("S1_Table/S1_TableTop").GetComponent<MeshRenderer>(), "stage switch cannot reveal prototype furniture over the real meshes");
        }

        [UnityTest] public IEnumerator ParcelOverlaysOnlyAppearDuringPurchaseMode()
        {
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>();
            var markers = Object.FindAnyObjectByType<ParcelMarkers>();
            var lines = markers.GetComponentsInChildren<LineRenderer>(true); Assert.Greater(lines.Length, 0);
            var p = game.Site.Data.parcels.First(parcel => parcel.id != "P0");
            game.OpenPanel(Panel.Help);
            Camera.main.transform.position = new Vector3(p.x + 1f, game.Site.HeightAt(p.x + 1f, p.z + 1f) + 1.7f, p.z + 1f);
            yield return null;
            Assert.IsTrue(lines.All(l => !l.enabled), "even nearby boundaries stay hidden in normal play");
            game.OpenPanel(Panel.Parcels); yield return null;
            Assert.IsTrue(lines.Any(l => l.enabled), "nearby boundaries are visible when buying land");
            game.ClosePanel(true); yield return null;
            Assert.IsTrue(lines.All(l => !l.enabled), "closing purchase mode immediately restores the normal world");
            Assert.IsTrue(markers.GetComponentsInChildren<TextMesh>(true).All(t => !t.gameObject.activeSelf));
        }
    }
}