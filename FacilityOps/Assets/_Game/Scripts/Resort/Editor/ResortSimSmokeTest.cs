using System;
using ResortAurora.Core;
using ResortAurora.Sim;
using UnityEditor;
using UnityEngine;

namespace ResortAurora.EditorTools
{
    /// <summary>Headless balance/regression check of the stall simulation. Unity -batchmode -nographics -executeMethod ResortAurora.EditorTools.ResortSimSmokeTest.Run</summary>
    public static class ResortSimSmokeTest
    {
        public static void Run()
        {
            bool ok = true;
            foreach (var staff in new[] { new string[0], new[] { "staff.dudu" }, new[] { "staff.dudu", "staff.marisa" } })
            {
                var r = SimulateDays(7, staff, player: false);
                Debug.Log($"SMOKE staff=[{string.Join(",", staff)}] 7 days: balance={r.balance} served={r.served} lost={r.lost} rep={r.rep:0.00}");
                ok &= r.served >= 0;
            }
            var solo = SimulateDays(7, new string[0], player: true);
            Debug.Log($"SMOKE player alone 7 days: balance={solo.balance} served={solo.served} lost={solo.lost} rep={solo.rep:0.00}");
            var withPlayer = SimulateDays(7, new[] { "staff.dudu" }, player: true);
            Debug.Log($"SMOKE player+Dudu 7 days: balance={withPlayer.balance} served={withPlayer.served} lost={withPlayer.lost} rep={withPlayer.rep:0.00}");
            foreach (var cfg in new[] { (price: 55, maid: false, upgrade: false), (price: 55, maid: true, upgrade: false), (price: 90, maid: true, upgrade: true), (price: 140, maid: true, upgrade: false) })
            {
                var lr = SimulateLodging(30, cfg.price, cfg.maid, cfg.upgrade);
                Debug.Log($"SMOKE pousada price={cfg.price} maid={cfg.maid} upgraded={cfg.upgrade} 30 nights: revenue={lr.revenue} occupancy={lr.occupancy:0.00} guests={lr.guests} avgStars={lr.stars:0.0} rep={lr.rep:0.00} dirtyAtEnd={lr.dirty}");
                ok &= lr.guests >= 0;
            }
            // ledger invariant
            var bus = new EventBus(); var l = new Ledger(bus, 100);
            ok &= !l.TrySpend(1, "x", 101) && l.Balance == 100 && l.TrySpend(1, "x", 40) && l.Balance == 60;
            // save round trip
            var save = new ResortSave { balance = 123, day = 4 }; var back = JsonUtility.FromJson<ResortSave>(JsonUtility.ToJson(save));
            ok &= back.balance == 123 && back.day == 4;
            Debug.Log(ok ? "SMOKE PASS" : "SMOKE FAIL");
            EditorApplication.Exit(ok ? 0 : 1);
        }

        struct LodgingResult { public int revenue, guests, dirty; public float occupancy, stars, rep; }

        static LodgingResult SimulateLodging(int nights, int price, bool maid, bool upgrade)
        {
            var bus = new EventBus();
            var ledger = new Ledger(bus, 5000);
            var stall = new StallModel { ReputationCap = 0.85f };
            stall.Reputation = 0.4f;
            var roster = new StaffRoster(bus) { Capacity = 4 };
            if (maid) { ledger.Add(1, "teste", 200); roster.Hire("staff.nilza", ledger, 1); }
            var lod = new LodgingModel(bus);
            lod.Unlock();
            foreach (var r in lod.Rooms) { lod.SetPrice(r.id, price); if (upgrade) lod.Upgrade(r.id, ledger, 1); }
            var rng = new System.Random(7);
            int revenue = 0, occ = 0;
            for (int d = 1; d <= nights; d++)
            {
                var w = DemandModel.WeatherFor(1, d);
                var n = lod.RunNight(d, stall, roster, ledger, w, rng);
                revenue += n.revenue; occ += n.occupied;
                if (!maid) foreach (var r in lod.Rooms) lod.Clean(r.id);   // the player cleans by hand every day
            }
            return new LodgingResult { revenue = revenue, guests = lod.TotalGuests, dirty = lod.DirtyCount(), occupancy = occ / (float)(nights * lod.Rooms.Count), stars = lod.AverageStars(), rep = stall.Reputation };
        }

        struct Result { public int balance, served, lost; public float rep; }

        /// <summary>Plays N days with a simple stand-in for the player: restock, then act whenever work exists with a human reaction delay.</summary>
        static Result SimulateDays(int days, string[] hires, bool player)
        {
            var bus = new EventBus();
            var ledger = new Ledger(bus, 150);
            var stall = new StallModel();
            var roster = new StaffRoster(bus) { Capacity = 2 };
            int day = 1;
            var svc = new StallService(bus, stall, ledger, roster, () => day);
            var rng = new System.Random(42);
            foreach (var h in hires) { ledger.Add(1, "teste", 100); roster.Hire(h, ledger, 1); }
            int totalServed = 0, totalLost = 0;
            for (day = 1; day <= days; day++)
            {
                var w = DemandModel.WeatherFor(1, day);
                svc.ResetDay();
                foreach (var p in Catalog.Products) { int want = p.Id == "sweet.picole" ? 15 : 30; int have = stall.Stock(p.Id); if (have < want) stall.Buy(p.Id, want - have, ledger, day); }
                float playerTimer = 0f, playerCook = 0f; Customer playerTicket = null;
                for (float t = GameClock.DayStart; t < GameClock.DayEnd; t += 1f / 4f) // 15-second steps
                {
                    // 1 step = 0.25 game minutes = 0.1875 s real at 0.75 s/min; use game-seconds directly for the service tick
                    float dt = 15f * 0.75f / 60f * 4f; // seconds of real play per step (0.75*0.25=0.1875 -> scaled below)
                    dt = 0.75f * 0.25f;
                    int hour = (int)(t / 60f);
                    float lam = DemandModel.Passersby(hour, w) * DemandModel.StopChance(stall) * 0.25f / 60f; // customers per step
                    if (rng.NextDouble() < lam) svc.Arrive(DemandModel.Pick(stall, w, rng));
                    svc.Tick(dt);
                    if (player)
                    {
                        playerTimer -= dt;
                        if (playerTicket != null) { playerCook += dt; if (playerCook >= svc.PrepareDuration(playerTicket, 0.5f)) { svc.FinishPrepare(playerTicket); playerTicket = null; } }
                        else if (playerTimer <= 0f)
                        {
                            if (svc.CanHandOver) { svc.HandOver(); playerTimer = 1.5f; }
                            else if (svc.CanTakeOrder) { svc.TakeOrder(); playerTimer = 1.8f; }
                            else { var tk = svc.NextTicket(); if (tk != null && svc.BeginPrepare(tk)) { playerTicket = tk; playerCook = 0f; } }
                        }
                    }
                }
                totalServed += svc.Served; totalLost += svc.Lost;
                ledger.Add(day, "salarios", -roster.DailyPayroll());
                stall.MeltStock();
            }
            return new Result { balance = ledger.Balance, served = totalServed, lost = totalLost, rep = stall.Reputation };
        }
    }
}
