using System.Collections;
using System.Collections.Generic;
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
    /// <summary>Phase 02 living world: the clock's light, the ambient population (pooled, with level of detail), the day/night scene and the kiosk fittings.</summary>
    public sealed class LivingWorldTests
    {
        string savePath;

        [SetUp] public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_life_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown] public void TearDown()
        {
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            QualitySettings.vSyncCount = 1; Application.targetFrameRate = -1;
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        static IEnumerator Load()
        {
#if UNITY_EDITOR
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null; yield return null;
        }

        /// <summary>Renders the camera at a pose into a PNG and returns the mean luminance (0..1) so night captures can be checked for "not black, not blown out".</summary>
        static float Snap(Camera cam, Vector3 pos, Vector3 look, string path)
        {
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
            var rt = new RenderTexture(1600, 900, 24); cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt;
            var t = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            t.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); t.Apply();
            File.WriteAllBytes(path, t.EncodeToPNG());
            var px = t.GetPixels32(); double sum = 0; int n = 0;
            for (int i = 0; i < px.Length; i += 17) { sum += (0.2126 * px[i].r + 0.7152 * px[i].g + 0.0722 * px[i].b) / 255.0; n++; }
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt); Object.Destroy(t);
            return (float)(sum / n);
        }

        // ---------------------------------------------------------------- pure models

        [Test]
        public void DaylightHasDawnNoonSunsetAndNight()
        {
            Assert.AreEqual(0f, Daylight.Night(12f), 0.001f, "noon is full daylight");
            Assert.AreEqual(1f, Daylight.Night(3f), 0.001f, "3 am is full night");
            Assert.AreEqual(1f, Daylight.Night(23f), 0.001f);
            Assert.Greater(Daylight.Night(5.0f), 0.5f, "before sunrise is still dark");
            Assert.AreEqual(0f, Daylight.Night(7f), 0.001f, "by 7 the day has begun");
            Assert.Less(Daylight.Night(18f), 0.5f, "at sunset it is dusk, not night");
            Assert.Greater(Daylight.Night(19.5f), 0.9f, "an hour and a half after sunset it is night");
            float prev = Daylight.Night(16f);
            for (float h = 16.1f; h <= 21f; h += 0.1f) { float n = Daylight.Night(h); Assert.GreaterOrEqual(n, prev - 1e-4f, "twilight only deepens at " + h); prev = n; }
            Assert.Greater(Daylight.SunElevation(12f), 70f);
            Assert.Less(Daylight.SunElevation(20f), 0f);
            Assert.IsFalse(Daylight.LampsOn(12f)); Assert.IsTrue(Daylight.LampsOn(19f));
            Assert.AreEqual(DayPhase.Amanhecer, Daylight.PhaseOf(6f)); Assert.AreEqual(DayPhase.Manha, Daylight.PhaseOf(9f));
            Assert.AreEqual(DayPhase.MeioDia, Daylight.PhaseOf(12f)); Assert.AreEqual(DayPhase.Tarde, Daylight.PhaseOf(16f));
            Assert.AreEqual(DayPhase.PorDoSol, Daylight.PhaseOf(18f)); Assert.AreEqual(DayPhase.Noite, Daylight.PhaseOf(21f));
        }

        [Test]
        public void HudHintsPointToTheNextStepAndFlagLowStock()
        {
            var s = new ServiceSnapshot { TotalStock = 20 };
            StringAssert.Contains("Abra o quiosque", ServiceHints.NextStep(s));
            s.TotalStock = 0; StringAssert.Contains("compre", ServiceHints.NextStep(s));
            s.TotalStock = 20; s.Open = true;
            StringAssert.Contains("Aguardando", ServiceHints.NextStep(s));
            s.Queue = 2; StringAssert.Contains("anote", ServiceHints.NextStep(s));
            s.TicketsToCook = 1; StringAssert.Contains("chapa", ServiceHints.NextStep(s));
            s.Ready = 1; StringAssert.Contains("entregue", ServiceHints.NextStep(s));
            s.Open = false; s.Closing = true; StringAssert.Contains("últimos clientes", ServiceHints.NextStep(s));
            s.Queue = 0; s.TicketsToCook = 0; s.Ready = 0; StringAssert.Contains("Fechando", ServiceHints.NextStep(s));
            s.Closing = false; s.AwaitingSleep = true; StringAssert.Contains("durma", ServiceHints.NextStep(s));

            var stall = new StallModel();
            Assert.AreNotEqual("", ServiceHints.LowStock(stall), "an empty stall reports everything as low");
            var ledger = new Ledger(new ResortAurora.Core.EventBus(), 100000);
            foreach (var p in Catalog.Products) stall.Buy(p.Id, 10, ledger, 1);
            Assert.AreEqual("", ServiceHints.LowStock(stall));
            Assert.AreEqual(10 * Catalog.Products.Length, ServiceHints.TotalStock(stall));
            stall.TryConsume(Catalog.Products[0].Id);
            for (int i = 0; i < 6; i++) stall.TryConsume(Catalog.Products[0].Id);
            StringAssert.Contains(Catalog.Products[0].Name + " 3", ServiceHints.LowStock(stall));
        }

        [Test]
        public void PopulationFollowsTheHourAndTheWeather()
        {
            Assert.Greater(PopulationModel.Density(12f, Weather.Sunny, 0.5f, 1), PopulationModel.Density(20f, Weather.Sunny, 0.5f, 1));
            Assert.Greater(PopulationModel.Density(20f, Weather.Sunny, 0.5f, 1), PopulationModel.Density(3f, Weather.Sunny, 0.5f, 1));
            var noon = PopulationModel.MixFor(12f, Weather.Sunny, 0.5f, 1);
            Assert.GreaterOrEqual(noon.Beach, 10); Assert.GreaterOrEqual(noon.Swimmers, 3); Assert.GreaterOrEqual(noon.Strollers, 8);
            Assert.LessOrEqual(noon.Total, 70, "the ambient crowd stays inside its pool budget");
            var night = PopulationModel.MixFor(22f, Weather.Sunny, 0.5f, 1);
            Assert.AreEqual(0, night.Beach); Assert.AreEqual(0, night.Swimmers); Assert.AreEqual(0, night.Kids);
            Assert.GreaterOrEqual(night.Strollers, 1, "the promenade is quieter at night, never empty");
            Assert.Less(PopulationModel.MixFor(12f, Weather.Cloudy, 0.5f, 1).Total, PopulationModel.MixFor(12f, Weather.Hot, 0.5f, 1).Total, "bad weather empties the beach");
            Assert.Greater(PopulationModel.MixFor(7f, Weather.Sunny, 0.5f, 1).Joggers, 0, "mornings belong to joggers");
            Assert.Greater(PopulationModel.Density(12f, Weather.Sunny, 1f, 5), PopulationModel.Density(12f, Weather.Sunny, 0f, 1), "reputation and growth bring people");
        }

        // ---------------------------------------------------------------- the beach is alive

        [UnityTest]
        public IEnumerator BeachIsAliveByDayAndQuieterAtNight()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            Assert.NotNull(g.Life, "beach life exists"); Assert.NotNull(g.DayNight, "day/night exists");
            var life = g.Life; float sx = g.Layout.Root.position.x, kz = g.Layout.Root.position.z;

            g.Clock.Restore(1, 12f * 60f);
            yield return new WaitForSeconds(2.6f);
            int day = life.ActiveCount;
            Debug.Log($"LIFE noon: active {day} (strollers {life.PeopleOf(BeachLife.Role.Stroller)}, sunbathers {life.PeopleOf(BeachLife.Role.Sunbather)}, kids {life.PeopleOf(BeachLife.Role.Kid)}, swimmers {life.PeopleOf(BeachLife.Role.Swimmer)}, joggers {life.PeopleOf(BeachLife.Role.Jogger)}, cyclists {life.PeopleOf(BeachLife.Role.Cyclist)}) pool {life.Spawned} weather {g.Weather}");
            Assert.GreaterOrEqual(day, 30, "beach and promenade are populated at noon");
            Assert.LessOrEqual(day, 110, "within the pool");
            Assert.Greater(life.PeopleOf(BeachLife.Role.Stroller), 0, "people stroll");
            Assert.Greater(life.PeopleOf(BeachLife.Role.Sunbather), 0, "people sit and lie on the sand");
            Assert.Greater(life.PeopleOf(BeachLife.Role.Swimmer), 0, "people are in the water");

            int sum = 0; foreach (var c in life.LodCounts) sum += c;
            Assert.AreEqual(life.ActiveCount, sum, "every active person has a level of detail");
            Assert.Greater(life.LodCounts[1] + life.LodCounts[2] + life.LodCounts[3], 0, "far people are simplified");
            Assert.LessOrEqual(life.LodCounts[0], 45, "full-detail people near the camera are capped by distance");

            var seen = new HashSet<string>();
            foreach (var s in life.Snapshot())
            {
                Assert.IsFalse(float.IsNaN(s.pos.x) || float.IsNaN(s.pos.y) || float.IsNaN(s.pos.z), "finite position");
                float ground = g.Site.HeightAt(s.pos.x, s.pos.z);
                if (s.role == BeachLife.Role.Swimmer) Assert.That(s.pos.y, Is.InRange(Mathf.Min(ground, 0.05f) - 0.01f, Mathf.Max(ground, 0.05f) + 0.01f), "swimmers float at the water surface or wade on the bottom");
                else Assert.AreEqual(ground, s.pos.y, 0.02f, s.role + " stands on the ground (no floating, no sinking)");
                if (s.role == BeachLife.Role.Sunbather)
                    Assert.IsFalse(s.pos.x > sx - 9f && s.pos.x < sx + 10f && s.pos.z > kz - 9f && s.pos.z < kz + 6f, "nobody lies inside the stall and its tables");
                seen.Add(s.role.ToString());
            }
            Debug.Log("LIFE roles seen: " + string.Join(",", seen));

            // night: the beach empties, the promenade stays alive
            g.Clock.Restore(1, 21f * 60f);
            yield return new WaitForSeconds(2.6f);
            Debug.Log($"LIFE night: active {life.ActiveCount} sunbathers {life.PeopleOf(BeachLife.Role.Sunbather)} swimmers {life.PeopleOf(BeachLife.Role.Swimmer)} strollers {life.PeopleOf(BeachLife.Role.Stroller)}");
            Assert.AreEqual(0, life.PeopleOf(BeachLife.Role.Sunbather), "nobody sunbathes at night");
            Assert.AreEqual(0, life.PeopleOf(BeachLife.Role.Swimmer), "nobody swims at night");
            Assert.Less(life.ActiveCount, day, "fewer people at night");
            Assert.IsTrue(g.DayNight.LampsOn, "lamps are on at 21:00");

            // next morning: joggers and locals
            g.Clock.Restore(2, 6f * 60f);
            yield return new WaitForSeconds(2.6f);
            Debug.Log($"LIFE morning: active {life.ActiveCount} joggers {life.PeopleOf(BeachLife.Role.Jogger)}");
            Assert.Greater(life.ActiveCount, 0, "the morning promenade has people");
        }

        [UnityTest]
        public IEnumerator FrameTimeWithTheCrowd()
        {
            QualitySettings.vSyncCount = 0; Application.targetFrameRate = -1;
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            var cam = Camera.main; var root = g.Layout.Root.position;
            g.Clock.Restore(1, 12f * 60f);
            yield return new WaitForSeconds(2.6f);
            g.OpenPanel(Panel.Help);                                                   // freeze input; the scene keeps rendering
            cam.transform.SetPositionAndRotation(root + new Vector3(2f, 2.0f, -8f), Quaternion.LookRotation(new Vector3(0f, -0.04f, -1f)));
            var rt = new RenderTexture(1920, 1080, 24); var px = new Texture2D(1, 1, TextureFormat.RGB24, false); cam.targetTexture = rt;
            for (int i = 0; i < 20; i++) { cam.Render(); yield return null; }
            var times = new List<float>();
            for (int i = 0; i < 90; i++)
            {
                float t0 = Time.realtimeSinceStartup;
                cam.Render(); RenderTexture.active = rt; px.ReadPixels(new Rect(0, 0, 1, 1), 0, 0); RenderTexture.active = null;
                times.Add((Time.realtimeSinceStartup - t0) * 1000f);
                yield return null;
            }
            cam.targetTexture = null; Object.Destroy(rt);
            times.Sort(); float avg = 0f; foreach (var t in times) avg += t; avg /= times.Count;
            Debug.Log($"PERF livingworld noon beach view: avg {avg:0.0} ms ({1000f / avg:0} fps), p95 {times[(int)(times.Count * 0.95f)]:0.0} ms, worst {times[times.Count - 1]:0.0} ms, active people {g.Life.ActiveCount}, lod [{g.Life.LodCounts[0]},{g.Life.LodCounts[1]},{g.Life.LodCounts[2]},{g.Life.LodCounts[3]}], lamps {g.DayNight.LampCount}");
            Assert.Less(avg, 100f, "average frame under 100 ms even in a headless batch run with the crowd");
        }

        // ---------------------------------------------------------------- day, sunset, night (real Unity captures)

        [UnityTest]
        public IEnumerator DayDuskAndNightAreLitAndCaptured()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            var cam = Camera.main; var root = g.Layout.Root.position; float pz = g.Site.PromenadeZ(root.x);
            string dir = Path.GetFullPath("../ArtSource/Blender/World/Reviews/F02");
            Directory.CreateDirectory(dir);
            var views = new (string name, Vector3 pos, Vector3 look)[]
            {
                ("kiosque_da_calcada", root + new Vector3(9f, 1.7f, 13f), root + new Vector3(0f, 1.3f, 0.5f)),
                ("praia_para_o_mar", root + new Vector3(3f, 2.0f, -9f), root + new Vector3(-6f, 0.4f, -95f)),
                ("mesas_na_areia", root + new Vector3(10f, 1.8f, 1.5f), root + new Vector3(6f, 0.8f, -2.8f)),
                ("calcadao_leste", new Vector3(root.x - 45f, g.Site.HeightAt(root.x - 45f, pz + 2f) + 1.7f, pz + 2f), new Vector3(root.x + 60f, g.Site.HeightAt(root.x + 60f, pz) + 1.6f, pz)),
                ("aerea", root + new Vector3(40f, 45f, -55f), root + new Vector3(0f, 0f, 20f)),
            };
            var hours = new (string tag, float h)[] { ("1_dia", 11.5f), ("2_tarde_dourada", 17.4f), ("3_por_do_sol", 18.4f), ("4_noite", 20.5f) };
            var light = new Dictionary<string, float>();
            foreach (var hr in hours)
            {
                g.Clock.Restore(1, hr.h * 60f);
                yield return new WaitForSeconds(2.6f);
                foreach (var v in views)
                {
                    cam.transform.SetPositionAndRotation(v.pos, Quaternion.LookRotation(v.look - v.pos));
                    yield return new WaitForSeconds(0.45f);                            // lamp pool and level of detail follow the camera
                    light[hr.tag + "/" + v.name] = Snap(cam, v.pos, v.look, Path.Combine(dir, "f02_" + hr.tag + "_" + v.name + ".png"));
                }
                if (hr.tag == "1_dia")
                {
                    Assert.AreEqual(0f, g.DayNight.NightFactor, 0.01f); Assert.IsFalse(g.DayNight.LampsOn);
                    Assert.Greater(RenderSettings.sun.intensity, 0.9f, "full sun at 11:30");
                }
                if (hr.tag == "4_noite")
                {
                    Assert.Greater(g.DayNight.NightFactor, 0.9f); Assert.IsTrue(g.DayNight.LampsOn);
                    Assert.Greater(g.DayNight.LightsActive, 0, "street, kiosk or home lamps carry real lights at night");
                    Assert.IsFalse(RenderSettings.sun.enabled && RenderSettings.sun.intensity > 0.05f, "the sun is down");
                }
            }
            foreach (var kv in light) Debug.Log($"LIGHT {kv.Key}: mean luminance {kv.Value:0.000}");
            Assert.Greater(light["1_dia/kiosque_da_calcada"], 0.15f, "daytime capture is bright");
            Assert.Less(light["4_noite/kiosque_da_calcada"], light["1_dia/kiosque_da_calcada"], "night is darker than day");
            Assert.Greater(light["4_noite/kiosque_da_calcada"], 0.02f, "night is readable, not black");
            Assert.Less(light["4_noite/kiosque_da_calcada"], 0.5f, "night is not blown out");
        }

        // ---------------------------------------------------------------- kiosk fittings

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

        [UnityTest]
        public IEnumerator FridgeAndFreezerReportStockAndServedCustomersTakeTables()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            g.Ledger.Add(1, "teste", 5000);
            foreach (var p in Catalog.Products) g.Stall.Buy(p.Id, 12, g.Ledger, 1);

            var fridge = GameObject.Find("S1_Fridge").GetComponent<ActionStation>();
            Assert.NotNull(fridge, "fridge is a station");
            StringAssert.Contains("Água 12", fridge.Prompt(g)); StringAssert.Contains("Cerveja", fridge.Prompt(g));
            fridge.Use(g); StringAssert.Contains("Geladeira", g.Toast);
            var freezer = g.Layout.Root.Find("Cooler").GetComponent<ActionStation>();
            Assert.NotNull(freezer, "freezer is a station"); StringAssert.Contains("Picolé 12", freezer.Prompt(g));
            var rack = GameObject.Find("S1_SnackRack").GetComponent<ActionStation>();
            StringAssert.Contains("Lanche 12", rack.Prompt(g));

            // tables: one from the start, three with the upgrade
            Assert.AreEqual(6, g.Layout.Seats.FindAll(s => !s.Kiosk).Count);
            Assert.AreEqual(2, g.Layout.Seats.FindAll(s => s.Enabled).Count, "one table at the start");
            Assert.AreEqual(0, g.Layout.Seats.FindAll(s => s.Kiosk && s.Enabled).Count, "kiosk chairs stay off at stage 1");
            Assert.IsTrue(g.Stall.BuyUpgrade("up.mesas", g.Ledger, 1));
            g.Layout.RefreshUpgrades(g);
            Assert.AreEqual(6, g.Layout.Seats.FindAll(s => s.Enabled).Count, "three tables with the Mesas upgrade");
            foreach (var t in g.Layout.ExtraTables) Assert.IsTrue(t.activeSelf);

            // run a morning: some served customers sit down, drink and leave without leaving a taken seat behind
            GameObject.Find("OpenSign").GetComponent<ActionStation>().Use(g);
            Time.captureDeltaTime = 0.05f; Time.timeScale = 4f;
            bool sat = false; int guard = 0;
            while (guard++ < 12000 && !sat && g.OpenedPanel != Panel.Summary)
            {
                Pilot(g, Time.deltaTime);
                if (g.Layout.Seats.Exists(s => s.Taken)) sat = true;
                yield return null;
            }
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            Assert.IsTrue(sat, "a served customer took a table");
            Assert.Greater(g.Service.Served, 0);
        }

        [UnityTest]
        public IEnumerator ServedCustomersSitOnTheDeckTablesOfTheStageTwoKiosk()
        {
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", "2");
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            g.Ledger.Add(1, "teste", 5000);
            foreach (var p in Catalog.Products) g.Stall.Buy(p.Id, 40, g.Ledger, 1);
            var lay = g.Layout;

            Assert.AreEqual(10, lay.Seats.FindAll(s => s.Enabled).Count, "five deck tables, two chairs each");
            Assert.AreEqual(0, lay.Seats.FindAll(s => !s.Kiosk && s.Enabled).Count, "no stage-1 plastic chairs at stage 2");
            foreach (var s in lay.Seats.FindAll(s => s.Kiosk))
            {
                Assert.IsTrue(lay.OnDeck(s.Pos), "kiosk chair on the deck");
                Assert.AreEqual(lay.Root.position.y + StallLayout.DeckLift, lay.Ground(s.Pos).y, 0.001f, "deck height");
            }
            // the queue in front of the counter is on the deck, so people stand on it and not 14 cm inside it
            Assert.AreEqual(lay.Root.position.y + StallLayout.DeckLift, lay.QueueSlot(0).y, 0.001f);

            GameObject.Find("OpenSign").GetComponent<ActionStation>().Use(g);
            Time.captureDeltaTime = 0.05f; Time.timeScale = 4f;
            bool sat = false, grounded = true; int guard = 0, seatedFrames = 0;
            while (guard++ < 16000 && g.OpenedPanel != Panel.Summary && seatedFrames < 20)
            {
                Pilot(g, Time.deltaTime);
                foreach (var a in Object.FindObjectsByType<CustomerAgent>(FindObjectsSortMode.None))
                {
                    var gy = lay.Ground(a.transform.position).y;
                    if (Mathf.Abs(a.transform.position.y - gy) > 0.35f) grounded = false;
                }
                var taken = lay.Seats.Find(s => s.Taken && s.Kiosk);
                if (taken != null)
                {
                    sat = true;
                    var near = false;
                    foreach (var a in Object.FindObjectsByType<CustomerAgent>(FindObjectsSortMode.None))
                        if (Vector3.Distance(a.transform.position, taken.Pos) < 0.05f) near = true;
                    if (near) seatedFrames++;
                    if (near && seatedFrames == 10)
                    {
                        string dir = Path.GetFullPath("../ArtSource/Blender/World/Reviews/F02"); Directory.CreateDirectory(dir);
                        var cam = Camera.main; var r = lay.Root.position; var sp = taken.Pos;
                        Snap(cam, new Vector3(sp.x + Mathf.Sign(sp.x - r.x) * 5f, r.y + 2.4f, sp.z + 6f), new Vector3(sp.x, r.y + 0.9f, sp.z), Path.Combine(dir, "f02_7_estagio2_clientes_no_deck.png"));
                    }
                }
                yield return null;
            }
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            Assert.IsTrue(sat, "a served customer took a deck chair");
            Assert.GreaterOrEqual(seatedFrames, 20, "a customer actually reached and stayed on the chair");
            Assert.IsTrue(grounded, "customers follow the deck height");
        }
    }
}
