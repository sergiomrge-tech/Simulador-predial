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
            // ledger invariant
            var bus = new EventBus(); var l = new Ledger(bus, 100);
            ok &= !l.TrySpend(1, "x", 101) && l.Balance == 100 && l.TrySpend(1, "x", 40) && l.Balance == 60;
            // save round trip
            var save = new ResortSave { balance = 123, day = 4 }; var back = JsonUtility.FromJson<ResortSave>(JsonUtility.ToJson(save));
            ok &= back.balance == 123 && back.day == 4;
            Debug.Log(ok ? "SMOKE PASS" : "SMOKE FAIL");
            EditorApplication.Exit(ok ? 0 : 1);
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
