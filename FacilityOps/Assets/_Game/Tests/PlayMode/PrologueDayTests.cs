using System.Collections;
using System.IO;
using NUnit.Framework;
using ResortAurora.Game;
using ResortAurora.Sim;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace ResortAurora.Tests
{
    /// <summary>Plays the stall stage end to end with an autopilot standing in for the player (same verbs the player uses).</summary>
    public sealed class PrologueDayTests
    {
        string savePath;
        const string Scene = "Assets/_Game/Scenes/ResortPrologue.unity";

        [SetUp]
        public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_save_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown]
        public void TearDown()
        {
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        static IEnumerator Load()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode(Scene, new LoadSceneParameters(LoadSceneMode.Single));
            yield return null; yield return null;
        }

        // Autopilot state
        Customer cooking; float cookLeft;
        void Pilot(ResortGame g, float dt)
        {
            var sv = g.Service;
            if (cooking != null) { cookLeft -= dt; if (cookLeft <= 0f) { sv.FinishPrepare(cooking); cooking = null; } return; }
            if (sv.CanHandOver) { sv.HandOver(); return; }
            if (sv.CanTakeOrder) { sv.TakeOrder(); return; }
            var t = sv.NextTicket();
            if (t != null && sv.BeginPrepare(t)) { cooking = t; cookLeft = sv.PrepareDuration(t, 0.5f); }
        }

        static void Shoot(ResortGame g)
        {
            string dir = Path.GetFullPath("../ArtSource/Blender/World/Reviews/R2");
            Directory.CreateDirectory(dir);
            var cam = Camera.main;
            var parent = cam.transform.parent; var pos = cam.transform.position; var rot = cam.transform.rotation;
            Debug.Log("PLAYTEST cam rel stall = " + (cam.transform.position - g.Layout.Root.position) + " fwd=" + cam.transform.forward);
            cam.transform.SetPositionAndRotation(g.Layout.Root.position + new Vector3(0f, 1.78f, -0.3f), Quaternion.Euler(12f, 0f, 0f));
            Snap(cam, dir + "/r2_primeira_pessoa_meio_dia.png");
            var root = g.Layout.Root.position;
            cam.transform.SetParent(null);
            cam.transform.SetPositionAndRotation(root + new Vector3(-7f, 5f, -9f), Quaternion.LookRotation(root + new Vector3(0f, 1.2f, 6f) - (root + new Vector3(-7f, 5f, -9f))));
            Snap(cam, dir + "/r2_barraca_visao_geral.png");
            cam.transform.SetParent(parent); cam.transform.SetPositionAndRotation(pos, rot);
        }

        static void Snap(Camera cam, string path)
        {
            var rt = new RenderTexture(1600, 900, 24);
            cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt;
            var t = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            t.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); t.Apply();
            File.WriteAllBytes(path, t.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt);
        }

        [UnityTest]
        public IEnumerator PlayAFullDayThenHireAndSaveAndReload()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            Assert.NotNull(g, "ResortGame in scene");
            Assert.IsTrue(g.Site.Ready, "site built");
            Assert.NotNull(g.Layout, "stall built");

            foreach (var p in Catalog.Products) g.Stall.Buy(p.Id, p.Id == "sweet.picole" ? 10 : 25, g.Ledger, g.Clock.Day);
            Assert.Less(g.Ledger.Balance, 150, "stock cost money");

            Time.captureDeltaTime = 0.05f;   // fixed step per frame so the test is deterministic and fast in batch mode
            Time.timeScale = 4f;
            bool shot = false; int guard = 0;
            while (g.OpenedPanel != Panel.Summary && guard++ < 40000)
            {
                Pilot(g, Time.deltaTime);
                if (!shot && g.Clock.Hours > 12f) { shot = true; Shoot(g); }
                yield return null;
            }
            Assert.AreEqual(Panel.Summary, g.OpenedPanel, "day closes with a summary");
            Assert.Greater(g.Service.Served, 0, "customers were served");
            Assert.Greater(g.LastSummary.revenue, 0);
            Assert.IsTrue(File.Exists(savePath), "autosave written at day end");
            int served = g.Service.Served, balance = g.Ledger.Balance;
            Debug.Log($"PLAYTEST day1 served={served} lost={g.Service.Lost} revenue={g.LastSummary.revenue} balance={balance} rep={g.Stall.Reputation:0.000}");

            // Next day with a hired cook
            g.StartNextDay();
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            foreach (var p in Catalog.Products) g.Stall.Buy(p.Id, 20, g.Ledger, g.Clock.Day);
            g.Ledger.Add(g.Clock.Day, "teste", 200);
            Assert.IsTrue(g.Roster.Hire("staff.marisa", g.Ledger, g.Clock.Day), "hire Marisa");
            yield return null;
            Assert.AreEqual(1, g.Layout.StaffVisuals.Count, "staff visual spawned");
            Assert.IsFalse(g.Roster.Hire("staff.marisa", g.Ledger, g.Clock.Day), "cannot hire twice");

            // Save round-trip
            g.SaveNow();
            var s = SaveStore.Read();
            Assert.NotNull(s); Assert.AreEqual(g.Clock.Day, s.day); Assert.AreEqual(1, s.staff.Count); Assert.AreEqual(g.Ledger.Balance, s.balance);
        }
    }
}
