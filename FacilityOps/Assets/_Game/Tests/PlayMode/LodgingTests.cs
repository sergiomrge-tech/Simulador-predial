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
    /// <summary>Buying the sobrado opens the pousada: rooms, reception desk, nightly arrivals, reviews, save and reload.</summary>
    public sealed class LodgingTests
    {
        string savePath;

        [SetUp]
        public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_lodging_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown]
        public void TearDown()
        {
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

        [UnityTest]
        public IEnumerator BuyingThePousadaOpensRoomsAndTheNightRuns()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            Assert.IsFalse(g.Lodging.Unlocked, "no pousada at the start");
            g.Ledger.Add(1, "teste", 100000);
            g.Stall.Reputation = 0.6f;
            Assert.IsTrue(g.Parcels.Buy("P1", g.Ledger, 1, 0.6f));
            Assert.IsTrue(g.Parcels.Buy("P2", g.Ledger, 1, 0.6f));
            yield return null;
            Assert.IsTrue(g.Lodging.Unlocked, "rooms exist after buying P2");
            Assert.AreEqual(LodgingModel.RoomsPerPousada, g.Lodging.Rooms.Count);
            Assert.GreaterOrEqual(g.Roster.Capacity, 4, "pousada makes room for more staff");
            Assert.NotNull(GameObject.Find("LodgingDesk"), "reception desk placed");
            Assert.AreEqual(3, g.Stages.Stage, "stage 3 shows the sobrado");

            // hire a maid, set a fair price and close three days; guests should arrive
            Assert.IsTrue(g.Roster.Hire("staff.nilza", g.Ledger, 1));
            foreach (var r in g.Lodging.Rooms) g.Lodging.SetPrice(r.id, 60);
            int guests = 0;
            for (int day = 0; day < 3; day++)
            {
                g.Clock.Restore(g.Clock.Day, GameClock.DayEnd - 1f);
                g.Clock.Skip(5f);                                       // reaches 22:00 and fires DayEnded
                int guard = 0;
                while (g.OpenedPanel != Panel.Summary && guard++ < 600) yield return null;
                Assert.AreEqual(Panel.Summary, g.OpenedPanel, "day closed");
                Assert.NotNull(g.LastSummary.lodging, "summary has the lodging night");
                guests += g.LastSummary.lodging.checkedIn;
                g.StartNextDay();
                yield return null;
            }
            Assert.Greater(guests + g.Lodging.OccupiedCount(), 0, "at least one guest arrived in three nights");
            Assert.IsTrue(File.Exists(savePath));
            var save = SaveStore.Read();
            Assert.AreEqual(LodgingModel.RoomsPerPousada, save.rooms.Count, "rooms saved");
            Assert.AreEqual(g.Lodging.TotalGuests, save.totalGuests);
            Debug.Log($"LODGING test: guests={g.Lodging.TotalGuests} occupied={g.Lodging.OccupiedCount()} reviews={g.Lodging.Reviews.Count} balance={g.Ledger.Balance}");
        }

        [UnityTest]
        public IEnumerator RoomsComeBackAfterReload()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            g.Ledger.Add(1, "teste", 100000);
            g.Stall.Reputation = 0.6f;
            g.Parcels.Buy("P1", g.Ledger, 1, 0.6f); g.Parcels.Buy("P2", g.Ledger, 1, 0.6f);
            yield return null;
            g.Lodging.SetPrice(3, 77);
            Assert.IsTrue(g.Lodging.Upgrade(3, g.Ledger, 1));
            g.SaveNow();
            yield return Load();
            var g2 = Object.FindAnyObjectByType<ResortGame>();
            Assert.IsTrue(g2.Lodging.Unlocked);
            Assert.AreEqual(77, g2.Lodging.Rooms[2].price);
            Assert.AreEqual(1, g2.Lodging.Rooms[2].quality);
            Assert.IsTrue(g2.Parcels.Owns("P2"));
            Assert.AreEqual(3, g2.Stages.Stage);
        }
    }
}
