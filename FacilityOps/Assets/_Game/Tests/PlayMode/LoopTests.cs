using System.Collections;
using System.IO;
using NUnit.Framework;
using ResortAurora.Game;
using ResortAurora.Sim;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

namespace ResortAurora.Tests
{
    /// <summary>Phase 02 gate: home -> beach -> open -> stock -> serve -> cash close -> home -> sleep -> next day, twice, then reload keeps everything.</summary>
    public sealed class LoopTests
    {
        string savePath;

        [SetUp] public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_loop_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown] public void TearDown()
        {
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        static IEnumerator Load()
        {
#if UNITY_EDITOR
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null; yield return null;
        }

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

        static void Snap(Camera cam, Vector3 pos, Vector3 look, string path)
        {
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
            var rt = new RenderTexture(1600, 900, 24); cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt;
            var t = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            t.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); t.Apply();
            File.WriteAllBytes(path, t.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt);
        }

        static T Station<T>(string objectName) where T : Component
        {
            var go = GameObject.Find(objectName);
            Assert.NotNull(go, objectName + " exists");
            return go.GetComponent<T>();
        }

        IEnumerator PlayDay(ResortGame g, bool closeEarly)
        {
            // stock up at the supplier crate (same call the market panel makes), open from the sign
            foreach (var p in Catalog.Products) g.Stall.Buy(p.Id, p.Id == "sweet.picole" ? 8 : 16, g.Ledger, g.Clock.Day);
            var sign = Station<ActionStation>("OpenSign");
            Assert.IsTrue(sign.CanUse(g)); StringAssert.Contains("Abrir", sign.Prompt(g));
            sign.Use(g);
            Assert.IsTrue(g.ShopOpen, "opened from the sign");
            StringAssert.Contains("Fechar", sign.Prompt(g));

            Time.captureDeltaTime = 0.05f; Time.timeScale = 4f;
            int guard = 0; bool closed = false;
            while (g.OpenedPanel != Panel.Summary && guard++ < 40000)
            {
                Pilot(g, Time.deltaTime);
                if (closeEarly && !closed && g.Clock.Hours > 17f) { g.RequestClose(); closed = true; }
                yield return null;
            }
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            Assert.AreEqual(Panel.Summary, g.OpenedPanel, "cash closed with a summary");
            Assert.IsFalse(g.ShopOpen);
            Assert.Greater(g.LastSummary.served, 0);
            if (closeEarly) Assert.Less(g.Clock.Hours, 20f, "closed early from the sign, not by the 22:00 clock");
        }

        IEnumerator GoHomeAndSleep(ResortGame g, int expectedDay)
        {
            var bed = Station<ActionStation>("HomeBed");
            Assert.IsFalse(bed.CanUse(g), "no sleeping before the day is closed");
            g.GoHome();
            Assert.IsTrue(g.AwaitingSleep);
            Assert.IsTrue(bed.CanUse(g)); StringAssert.Contains("Dormir", bed.Prompt(g));
            bed.Use(g);
            yield return null;
            Assert.AreEqual(expectedDay, g.Clock.Day, "next day started");
            Assert.AreEqual(GameClock.DayStart, g.Clock.Minutes, 0.5f, "06:00");
            Assert.IsFalse(g.ShopOpen, "the stall starts closed");
            Assert.IsFalse(g.AwaitingSleep);
        }

        [UnityTest]
        public IEnumerator TwoDaysHomeToBedAndReload()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            var player = Object.FindAnyObjectByType<PlayerController>();

            // the day starts at the door of the Apto 12, a short walk from the stall
            var door = g.Site.HomeDoor;
            Assert.Less(Vector3.Distance(player.transform.position, door), 3f, "day 1 starts at home");
            float commute = Vector2.Distance(new Vector2(door.x, door.z), new Vector2(g.Layout.Root.position.x, g.Layout.Root.position.z));
            Assert.Less(commute, 220f, "home to stall is a short walk");
            Debug.Log($"LOOP commute {commute:0} m");

            g.Clock.Restore(1, 11f * 60f);
            yield return null; yield return null;
            string dir = Path.GetFullPath(Path.Combine(System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT") ?? "../ArtSource/Blender/World/Reviews", "R5"));
            Directory.CreateDirectory(dir);
            var cam = Camera.main; var h = g.Site.Data.home;
            float ox = h.x - h.width / 2f, oz = h.z - h.depth / 2f, gy = g.Site.HeightAt(h.x, oz);
            Snap(cam, new Vector3(h.x + 6f, gy + 2.2f, oz - 9f), new Vector3(h.x, gy + 1.8f, oz + 2f), dir + "/r5_lar_fachada.png");
            Snap(cam, new Vector3(ox + 6.1f, gy + 1.6f, oz + 1.0f), new Vector3(ox + 9.2f, gy + 0.8f, oz + 6.6f), dir + "/r5_lar_cama.png");
            Snap(cam, g.Layout.PlayerSpawn + new Vector3(-2f, 1.6f, -3f), g.Layout.PlayerSpawn + new Vector3(0.5f, 1.2f, 2f), dir + "/r5_quiosque_balcao_placa.png");
            g.Clock.Restore(1, GameClock.DayStart);
            yield return PlayDay(g, closeEarly: false);
            yield return GoHomeAndSleep(g, 2);
            Assert.Less(Vector3.Distance(player.transform.position, door), 4f, "day 2 starts at home too");
            yield return PlayDay(g, closeEarly: true);

            int day = g.Clock.Day, balance = g.Ledger.Balance, stock = 0; float rep = g.Stall.Reputation;
            foreach (var p in Catalog.Products) stock += g.Stall.Stock(p.Id);
            Debug.Log($"LOOP after 2 days: day={day} balance={balance} stock={stock} rep={rep:0.000}");
            Assert.IsTrue(File.Exists(savePath));

            // reload: resumes on the next morning with the same money, stock and reputation (the closed day is not replayed)
            yield return Load();
            var g2 = Object.FindAnyObjectByType<ResortGame>();
            Assert.AreEqual(day + 1, g2.Clock.Day, "resumes the morning after the last closed day");
            Assert.AreEqual(balance, g2.Ledger.Balance, "money kept");
            int stock2 = 0; foreach (var p in Catalog.Products) stock2 += g2.Stall.Stock(p.Id);
            Assert.AreEqual(stock, stock2, "stock kept");
            Assert.AreEqual(rep, g2.Stall.Reputation, 0.001f, "reputation kept");
            Assert.IsFalse(g2.ShopOpen);
        }
    }
}
