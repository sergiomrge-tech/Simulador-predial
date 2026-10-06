using System.Collections;
using System.IO;
using NUnit.Framework;
using ResortAurora.Game;
using ResortAurora.Site;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

namespace ResortAurora.Tests
{
    /// <summary>The exported resort pieces line up with the Unity terrain, and the stage follows the land owned.</summary>
    public sealed class StagesTests
    {
        const string Scene = "Assets/_Game/Scenes/ResortPrologue.unity";
        string savePath;

        [SetUp]
        public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_stage_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown]
        public void TearDown()
        {
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        static IEnumerator Load()
        {
#if UNITY_EDITOR
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode(Scene, new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null; yield return null;
        }

        static Bounds BoundsOf(GameObject go)
        {
            var rs = go.GetComponentsInChildren<Renderer>(true);
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }

        static void Snap(Camera cam, Vector3 pos, Vector3 look, string path)
        {
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
            var rt = new RenderTexture(1600, 900, 24);
            cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt;
            var t = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            t.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); t.Apply();
            File.WriteAllBytes(path, t.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt);
        }

        [UnityTest]
        public IEnumerator PiecesLineUpWithTheTerrainAndTheStageFollowsTheLand()
        {
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", "7");
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            Assert.NotNull(g.Stages); Assert.Greater(g.Stages.PieceCount, 30, "pieces loaded");
            Assert.AreEqual(7, g.Stages.Stage);
            Assert.IsTrue(g.Site.Graded, "graded terrain at stage 7");

            GameObject find(string n) { foreach (var go in g.Stages.Instances) if (go.name == n) return go; return null; }
            var hotel = find("E6-7_grande_hotel");
            Assert.NotNull(hotel); Assert.IsTrue(hotel.activeSelf);
            var hb = BoundsOf(hotel);
            // Blender site-local X 505..595 (+ portico), Y 330..420 -> Unity x, z; height above the pad
            Assert.That(hb.center.x, Is.InRange(535f, 565f), "hotel x");
            Assert.That(hb.center.z, Is.InRange(335f, 395f), "hotel z (north = +z, not mirrored)");
            Assert.That(hb.min.y, Is.GreaterThan(g.Site.HeightAt(550f, 358f) - 3f), "hotel sits on the ground");
            Assert.That(hb.size.x, Is.InRange(85f, 110f), "hotel width");

            var aur = find("E7-7_Arq_Tower");
            Assert.NotNull(aur);
            var tb = BoundsOf(aur);
            Assert.That(tb.center.x, Is.InRange(440f, 470f), "tower x");
            Assert.That(tb.center.z, Is.InRange(620f, 660f), "tower z");
            Assert.That(tb.max.y, Is.GreaterThan(60f), "tower height");

            var cam = Camera.main;
            string dir = Path.GetFullPath("../ArtSource/Blender/World/Reviews/R4");
            Directory.CreateDirectory(dir);
            g.Stages.SetStage(7);
            Snap(cam, new Vector3(215f, 100f, -20f), new Vector3(520f, 8f, 410f), dir + "/r4_unity_etapa7_aerea.png");
            Snap(cam, new Vector3(450f, 62f, 30f), new Vector3(450f, 14f, 560f), dir + "/r4_unity_etapa7_plato.png");
            g.Stages.SetStage(1);
            Assert.IsFalse(g.Site.Graded, "natural land at stage 1");
            Snap(cam, new Vector3(215f, 100f, -20f), new Vector3(520f, 8f, 410f), dir + "/r4_unity_etapa1_aerea.png");

            Assert.AreEqual(1, ResortStages.StageFor(g.Parcels));
            g.Ledger.Add(1, "teste", 500000);
            g.Stall.Reputation = 0.6f;
            Assert.IsTrue(g.Parcels.Buy("P1", g.Ledger, 1, 0.6f));
            Assert.AreEqual(2, ResortStages.StageFor(g.Parcels));
        }
    }
}
