using System;
using System.Collections.Generic;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEngine;
using UnityEngine.AI;

namespace FacilityOps.Editor
{
    /// <summary>
    /// Builds the continuous-walk route (Lar -> street -> Oficina -> street -> Horizonte gate -> lobby -> stair -> 4th-floor panel -> out -> Mercearia -> Lar)
    /// from the reference NavMesh baked from the imported colliders, and writes it to StreamingAssets/world-walk-route.json for the Play Mode gate and the
    /// Development player autopilot. Every leg must be a complete NavMesh path: a failed leg is an error, never patched with a straight line.
    /// </summary>
    public static class WorldSliceWalkRouteBuilder
    {
        public const string RoutePath = "Assets/StreamingAssets/world-walk-route.json";
        private static readonly Vector3 LarSpawn = new Vector3(-2860f, 17.65f, -2266f);

        [MenuItem("Facility Ops/World/Build Continuous Walk Route")]
        public static void Build()
        {
            var nav = AssetDatabase.LoadAssetAtPath<NavMeshData>(WorldSliceWalkabilityQa.NavAsset);
            if (nav == null) throw new FileNotFoundException("Run WorldSliceWalkabilityQa.BuildReference first.", WorldSliceWalkabilityQa.NavAsset);
            var instance = NavMesh.AddNavMeshData(nav);
            try
            {
                var steps = new List<WorldSliceQaWalker.Step>();
                var garage = WorldSliceDestinationRegistry.Require("garage").FallbackPosition;
                var grocery = WorldSliceDestinationRegistry.Require("grocery").FallbackPosition;
                Vector3 arrive = new Vector3(-2350f, 27.05f, -1831f);
                Vector3 intercomFront = new Vector3(-2352.2f, 27.05f, -1829.2f);
                Vector3 gateIn = new Vector3(-2350f, 27.05f, -1824.8f);
                Vector3 lobby = new Vector3(-2350f, 27.08f, -1810f);
                Vector3 stairDoorFront = new Vector3(-2347.4f, 27.08f, -1800.4f);
                Vector3 firstTread = new Vector3(-2346.875f, 27.3f, -1797.4f);
                Vector3 stairMid = new Vector3(-2347.1f, 28.2f, -1796.0f);
                Vector3 landing = new Vector3(-2347.7f, 29.25f, -1794.6f);
                Vector3 tfArrive = new Vector3(-2348.1f, 37.08f, -1797.8f);
                Vector3 tfDoorFront = new Vector3(-2347.4f, 37.08f, -1800.4f);
                Vector3 panel = new Vector3(-2345.5f, 37.05f, -1800.3f);
                Vector3 panelAim = new Vector3(-2345.5f, 38.45f, -1799.3f);

                steps.Add(new WorldSliceQaWalker.Step { kind = "accept", name = "accept", label = "accept the prologue contract so the panel binds to QD-01" });
                steps.Add(Teleport(LarSpawn, 180f));
                steps.Add(Mark("01 Lar"));
                steps.Add(Capture("01-lar", new Vector3(-2860f, 22f, -2285f)));
                steps.Add(new WorldSliceQaWalker.Step { kind = "tablet", name = "tablet", label = "open and close the tablet" });
                steps.Add(Mark("02 Lar -> rua -> Oficina"));
                var leg = Leg(LarSpawn, garage, "Lar -> Oficina");
                Split(leg, .5f, out var first, out var second);
                steps.Add(Walk("Lar -> rua", first));
                steps.Add(Capture("02-rua", first[first.Length - 1] + (first[first.Length - 1] - first[first.Length - 2]).normalized * 12f + Vector3.up * 1.5f));
                steps.Add(Walk("rua -> Oficina", second));
                steps.Add(Capture("03-oficina", new Vector3(-2690f, 25f, -2150f)));
                steps.Add(Mark("03 Oficina -> rua -> Horizonte"));
                var toHorizonte = Leg(garage, arrive, "Oficina -> Horizonte");
                Split(toHorizonte, .5f, out var a1, out var a2);
                steps.Add(Walk("Oficina -> rua", a1));
                steps.Add(Capture("13-streaming-overlay", a1[a1.Length - 1] + (a1[a1.Length - 1] - a1[a1.Length - 2]).normalized * 12f + Vector3.up * 1.5f));
                steps.Add(Walk("rua -> Horizonte", a2));
                steps.Add(Capture("04-horizonte-chegada", new Vector3(-2350f, 35f, -1800f)));
                steps.Add(Mark("04 Horizonte: portão"));
                steps.Add(Walk("rua -> interfone", Leg(arrive, intercomFront, "interfone")));
                steps.Add(Interact("interfone abre o portão", new Vector3(-2352.5f, 28.25f, -1827.45f)));
                steps.Add(Wait(1.6f));
                steps.Add(Capture("05-portao", new Vector3(-2350f, 28.0f, -1827.4f)));
                steps.Add(Walk("portão -> portaria", Leg(intercomFront, lobby, "portão -> portaria")));
                steps.Add(Capture("06-portaria", new Vector3(-2347.4f, 28.4f, -1799.2f)));
                steps.Add(Mark("05 Horizonte: escada e 4º andar"));
                steps.Add(Walk("portaria -> porta da escada", Leg(lobby, stairDoorFront, "porta da escada")));
                steps.Add(Walk("porta da escada -> 1º degrau", Leg(stairDoorFront, firstTread, "1º degrau")));
                steps.Add(Walk("lance 1", Leg(firstTread, stairMid, "lance 1")));
                steps.Add(Capture("07-escada", landing + Vector3.up * 1.2f));
                steps.Add(Walk("patamar de giro", Leg(stairMid, landing, "patamar")));
                steps.Add(Capture("08-patamar", tfArrive + Vector3.up * 3f));
                steps.Add(Walk("pisos seguintes -> 4º andar", Leg(landing, tfArrive, "4º andar")));
                steps.Add(Capture("09-4andar", tfDoorFront + Vector3.up * 1.4f));
                steps.Add(Walk("4º andar -> corredor", Leg(tfArrive, tfDoorFront, "corredor")));
                steps.Add(Walk("corredor -> quadro", Leg(tfDoorFront, panel, "quadro")));
                steps.Add(Capture("10-quadro", panelAim));
                steps.Add(Interact("quadro técnico (QD-01)", panelAim));
                steps.Add(new WorldSliceQaWalker.Step { kind = "save", name = "save", label = "save at the panel" });
                steps.Add(new WorldSliceQaWalker.Step { kind = "verifysave", name = "verify", label = "after QD-01 at the panel" });
                steps.Add(Mark("06 saída do Horizonte"));
                steps.Add(Walk("quadro -> 4º andar -> térreo -> rua", Leg(panel, arrive, "saída")));
                steps.Add(Capture("11-saida", new Vector3(-2350f, 33f, -1815f)));
                steps.Add(Mark("07 Horizonte -> Mercearia"));
                steps.Add(Walk("rua -> Mercearia", Leg(arrive, grocery, "Mercearia")));
                steps.Add(Capture("12-mercearia", new Vector3(-2580f, 28f, -1480f)));
                steps.Add(Mark("08 Mercearia -> Lar"));
                // The NavMesh pathfinder gives up on one ~800 m query (PathPartial), so the way back is walked as the same three complete legs, reversed.
                steps.Add(Walk("retorno: Mercearia -> Horizonte", Leg(grocery, arrive, "retorno 1")));
                steps.Add(Walk("retorno: Horizonte -> Oficina", Leg(arrive, garage, "retorno 2")));
                steps.Add(Walk("retorno: Oficina -> Lar", Leg(garage, LarSpawn, "retorno 3")));
                steps.Add(Capture("15-retorno-lar", new Vector3(-2860f, 22f, -2285f)));
                steps.Add(new WorldSliceQaWalker.Step { kind = "verifysave", name = "verify", label = "after returning to the Lar" });
                steps.Add(Capture("14-performance", new Vector3(-2860f, 22f, -2285f)));

                var route = new WorldSliceQaWalker.Route
                {
                    version = 1,
                    note = "Generated by WorldSliceWalkRouteBuilder from the reference NavMesh (doors open for the bake only). Doors are closed in the game and are opened by the walker's real [E] interaction.",
                    steps = steps.ToArray()
                };
                Directory.CreateDirectory(Path.GetDirectoryName(RoutePath));
                File.WriteAllText(RoutePath, JsonUtility.ToJson(route, true));
                AssetDatabase.ImportAsset(RoutePath, ImportAssetOptions.ForceUpdate);
                float length = 0f; int walks = 0;
                foreach (var s in steps) if (s.kind == "walk") { walks++; for (int i = 1; i < s.corners.Length; i++) length += Vector3.Distance(s.corners[i - 1].V, s.corners[i].V); }
                Debug.Log($"WORLD WALK ROUTE: {steps.Count} steps, {walks} walks, {length:F0} m -> {RoutePath}");
            }
            finally { instance.Remove(); }
        }

        private static WorldSliceQaWalker.Step Mark(string name) => new WorldSliceQaWalker.Step { kind = "mark", name = name };
        private static WorldSliceQaWalker.Step Wait(float seconds) => new WorldSliceQaWalker.Step { kind = "wait", name = "wait", seconds = seconds };
        private static WorldSliceQaWalker.Step Teleport(Vector3 p, float yaw) => new WorldSliceQaWalker.Step { kind = "teleport", name = "start", corners = new[] { new WorldSliceQaWalker.Vec3(p) }, yaw = yaw };
        private static WorldSliceQaWalker.Step Capture(string name, Vector3 aim) => new WorldSliceQaWalker.Step { kind = "capture", name = name, aim = new WorldSliceQaWalker.Vec3(aim) };
        private static WorldSliceQaWalker.Step Interact(string label, Vector3 aim) => new WorldSliceQaWalker.Step { kind = "interact", name = "interact", label = label, aim = new WorldSliceQaWalker.Vec3(aim) };
        private static WorldSliceQaWalker.Step Walk(string label, Vector3[] corners)
        {
            var c = new WorldSliceQaWalker.Vec3[corners.Length];
            for (int i = 0; i < c.Length; i++) c[i] = new WorldSliceQaWalker.Vec3(corners[i]);
            return new WorldSliceQaWalker.Step { kind = "walk", name = label, label = label, corners = c };
        }

        private static Vector3[] Leg(Vector3 from, Vector3 to, string name)
        {
            if (!NavMesh.SamplePosition(from, out var a, 1.5f, NavMesh.AllAreas) || !NavMesh.SamplePosition(to, out var b, 1.5f, NavMesh.AllAreas))
                throw new InvalidOperationException($"Route leg '{name}': endpoint is not on the NavMesh ({from} -> {to})");
            var path = new NavMeshPath();
            if (!NavMesh.CalculatePath(a.position, b.position, NavMesh.AllAreas, path) || path.status != NavMeshPathStatus.PathComplete)
                throw new InvalidOperationException($"Route leg '{name}' is not a complete NavMesh path ({path.status}) {a.position} -> {b.position}");
            return path.corners;
        }

        private static void Split(Vector3[] corners, float fraction, out Vector3[] first, out Vector3[] second)
        {
            float total = 0f;
            for (int i = 1; i < corners.Length; i++) total += Vector3.Distance(corners[i - 1], corners[i]);
            float target = total * fraction, walked = 0f;
            for (int i = 1; i < corners.Length; i++)
            {
                float d = Vector3.Distance(corners[i - 1], corners[i]);
                if (walked + d >= target)
                {
                    Vector3 mid = Vector3.Lerp(corners[i - 1], corners[i], Mathf.Clamp01((target - walked) / Mathf.Max(.001f, d)));
                    var f = new List<Vector3>(); for (int k = 0; k < i; k++) f.Add(corners[k]); f.Add(mid);
                    var s = new List<Vector3> { mid }; for (int k = i; k < corners.Length; k++) s.Add(corners[k]);
                    first = f.ToArray(); second = s.ToArray(); return;
                }
                walked += d;
            }
            first = corners; second = new[] { corners[corners.Length - 1], corners[corners.Length - 1] };
        }
    }
}
