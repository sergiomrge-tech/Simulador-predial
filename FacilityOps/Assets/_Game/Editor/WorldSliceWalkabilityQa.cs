using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;

namespace FacilityOps.Editor
{
    // Reference bake for validation only: no agents, links or production scene changes.
    public static class WorldSliceWalkabilityQa
    {
        public const string NavAsset = "Assets/_Game/World/SantaAurora/OldTown/QA/CorridorWalkability.asset";
        [Serializable] public sealed class Route
        {
            public string name; public string status; public Vector3 start; public Vector3 end; public Vector3[] corners;
        }
        [Serializable] public sealed class Report
        {
            public string status; public string unityVersion; public string fingerprint; public int sourceCount; public double bakeSeconds;
            public string geometry; public float radius; public float height; public Route[] routes;
        }
        // Same radius/height as the FirstPersonController CharacterController. A wider agent (.36 = radius + skin) makes the corridor panel route
        // fail although the controller physically walks it (original gate), so the radius stays the controller's and the Play Mode walker re-centres
        // on the line (WorldSliceStairWalkGateTests) the way a player would, instead of hugging jambs.
        public const float AgentRadius = .28f;
        public static string ReportPath => Path.GetFullPath(Path.Combine(Application.dataPath, "../../Logs/world-walkability-qa.json"));

        public static void BuildReference() => BakeReference(false);
        public static void BuildOpenDoorReference() => BakeReference(true);
        public static void DiagnoseHorizonteStair() => BakeReference(false, true);
        public static void DiagnoseHorizonteStairOpenDoors() => BakeReference(true, true);
        private static void BakeReference(bool openDoors, bool diagnose = false)
        {
            var all = new List<NavMeshBuildSource>();
            Vector3 spawn = default, panel = default;
            bool foundSpawn = false, foundPanel = false;
            string original = UnityEngine.SceneManagement.SceneManager.GetActiveScene().path;
            try
            {
                foreach (string cell in WorldCellSceneScaffolder.PilotCellIds)
                {
                    EditorSceneManager.OpenScene(WorldCellSceneScaffolder.ScenePathFor(cell), OpenSceneMode.Single);
                    var root = UnityEngine.Object.FindAnyObjectByType<WorldCellRoot>();
                    if (openDoors)
                        foreach (var leaf in root.GetComponentsInChildren<MeshFilter>())
                            if (leaf.name.Contains("_stair_door__leaf"))
                                leaf.transform.Rotate(Vector3.up, 90f, Space.World);
                    var sources = new List<NavMeshBuildSource>();
                    NavMeshBuilder.CollectSources(root.transform, ~0, NavMeshCollectGeometry.PhysicsColliders,
                        0, new List<NavMeshBuildMarkup>(), sources);
                    all.AddRange(sources);
                    foreach (var marker in root.GetComponentsInChildren<WorldGameplayMarker>())
                    {
                        if (marker.MarkerName.EndsWith("GP_prologue_spawn_corridor", StringComparison.Ordinal)) { spawn = marker.transform.position; foundSpawn = true; }
                        if (marker.MarkerName.EndsWith("GP_quadro_tecnico", StringComparison.Ordinal))
                        {
                            // Interaction origin is 1.4 m above the floor. Query the
                            // approach on this floor, never the floor above the panel.
                            panel = marker.transform.position + marker.transform.forward - Vector3.up * 1.4f;
                            foundPanel = true;
                        }
                    }
                }
                if (!foundSpawn || !foundPanel) throw new InvalidDataException("Critical Horizonte markers missing.");
                var settings = NavMesh.GetSettingsByIndex(0);
                settings.agentRadius = AgentRadius; settings.agentHeight = 1.8f;
                settings.agentClimb = .3f; settings.agentSlope = 45f;
                settings.overrideVoxelSize = true; settings.voxelSize = .1f;
                settings.overrideTileSize = true; settings.tileSize = 256;
                double started = UnityEditor.EditorApplication.timeSinceStartup;
                var data = NavMeshBuilder.BuildNavMeshData(settings, all,
                    new Bounds(new Vector3(-2625f, 75f, -1875f), new Vector3(850f, 200f, 1350f)),
                    Vector3.zero, Quaternion.identity);
                if (data == null) throw new InvalidDataException("Navigation QA bake produced no data.");
                Directory.CreateDirectory(Path.GetDirectoryName(NavAsset));
                AssetDatabase.Refresh();
                var existing = AssetDatabase.LoadAssetAtPath<NavMeshData>(NavAsset);
                if (existing == null) AssetDatabase.CreateAsset(data, NavAsset);
                else { EditorUtility.CopySerialized(data, existing); UnityEngine.Object.DestroyImmediate(data); data = existing; }
                AssetDatabase.SaveAssets();
                var instance = NavMesh.AddNavMeshData(data);
                try
                {
                    if (diagnose) { DiagnoseStair(); return; }
                    Vector3 home = WorldSliceDestinationRegistry.Require("home.starter").FallbackPosition;
                    Vector3 garage = WorldSliceDestinationRegistry.Require("garage").FallbackPosition;
                    Vector3 exterior = WorldSliceDestinationRegistry.Require("horizonte").FallbackPosition;
                    Vector3 grocery = WorldSliceDestinationRegistry.Require("grocery").FallbackPosition;
                    var routes = new[] { Find("Lar→Oficina", home, garage), Find("Oficina→Horizonte", garage, exterior),
                        Find("Horizonte→Mercearia", exterior, grocery), Find("Horizonte entrada→Prólogo", exterior, spawn),
                        Find("Prólogo spawn→Quadro", spawn, panel) };
                    bool pass = Array.TrueForAll(routes, r => r.status == "PathComplete");
                    var report = new Report { status = pass ? "PASS" : "FAIL", unityVersion = Application.unityVersion, fingerprint = WorldSliceBuildGate.Fingerprint(),
                        sourceCount = all.Count, bakeSeconds = UnityEditor.EditorApplication.timeSinceStartup - started,
                        geometry = "Imported physical colliders; no synthetic links; stair leaves " + (openDoors ? "opened 90 degrees for diagnostic bake only" : "closed as authored"), radius = AgentRadius, height = 1.8f, routes = routes };
                    Directory.CreateDirectory(Path.GetDirectoryName(ReportPath));
                    File.WriteAllText(openDoors ? ReportPath.Replace(".json", "-open-doors.json") : ReportPath, JsonUtility.ToJson(report, true));
                    Debug.Log("WORLD WALKABILITY QA: " + report.status + " / " + ReportPath);
                    // A failed path is evidence, never a reason to add invisible connecting floors.
                }
                finally { instance.Remove(); }
            }
            finally
            {
                if (!string.IsNullOrEmpty(original)) EditorSceneManager.OpenScene(original, OpenSceneMode.Single);
            }
        }
        // Validation-only probe: lists the walkable surfaces (physics rays) and NavMesh coverage over the Horizonte stair lanes.
        private static void DiagnoseStair()
        {
            Vector3 street = new Vector3(-2350f, 27.05f, -1831f), lobby = new Vector3(-2350f, 27.05f, -1810f);
            Vector3 beforeDoor = new Vector3(-2347.4f, 27.05f, -1799.6f), insideDoor = new Vector3(-2347.4f, 27.1f, -1798.4f);
            Vector3 stairBottom = new Vector3(-2346.875f, 27.3f, -1797.4f), spawn = new Vector3(-2361f, 37.05f, -1800f);
            var checks = new List<(string, Vector3, Vector3)> {
                ("rua→lobby", street, lobby), ("lobby→antes da porta", lobby, beforeDoor),
                ("antes da porta→dentro da escada", beforeDoor, insideDoor), ("dentro→1º degrau", insideDoor, stairBottom) };
            for (int f = 1; f <= 3; f++)
            {
                float y = 27.05f + (f == 1 ? 4f : 4f + 3f * (f - 1));
                Vector3 lane1Start = new Vector3(-2346.875f, y + .2f, -1797.4f), arrival = new Vector3(-2348.125f, y + .05f, -1797.8f);
                Vector3 previousLane1 = f == 1 ? stairBottom : new Vector3(-2346.875f, y - 3f + .2f, -1797.4f);
                checks.Add(($"1º degrau do lance→chegada piso {f}", previousLane1, arrival));
                if (f < 3) checks.Add(($"chegada piso {f}→1º degrau do lance seguinte", arrival, lane1Start));
            }
            checks.Add(("chegada piso 3→spawn do prólogo", new Vector3(-2348.125f, 37.1f, -1797.8f), spawn));
            Vector3 tfStrip = new Vector3(-2347.2f, 37.1f, -1798.3f), tfCorridor = new Vector3(-2347.4f, 37.1f, -1799.9f);
            checks.Add(("TF chegada→faixa de entrada", new Vector3(-2348.125f, 37.1f, -1797.8f), tfStrip));
            checks.Add(("TF faixa→corredor (porta)", tfStrip, tfCorridor));
            checks.Add(("TF corredor→spawn", tfCorridor, spawn));
            checks.Add(("TF corredor→quadro", tfCorridor, new Vector3(-2345.5f, 37.05f, -1800.3f)));
            checks.Add(("TF faixa→1º degrau do lance seguinte", tfStrip, new Vector3(-2346.875f, 37.34f, -1797.4f)));
            EditorSceneManager.OpenScene(WorldCellSceneScaffolder.ScenePathFor("SA_M01_02_S02_00"), OpenSceneMode.Single);
            Physics.SyncTransforms();
            foreach (var col in Physics.OverlapBox(new Vector3(-2347.4f, 28.3f, -1798.9f), new Vector3(1.6f, 1.4f, 1.1f), Quaternion.identity, ~0, QueryTriggerInteraction.Collide))
                Debug.Log("DIAGCOL " + col.name + " type=" + col.GetType().Name + " trig=" + col.isTrigger + " " + col.bounds.min.ToString("F2") + ".." + col.bounds.max.ToString("F2"));
            foreach (float x in new[] { -2347.7f, -2347.4f, -2347.1f })
                foreach (float y in new[] { 27.3f, 28.0f, 28.8f })
                {
                    Vector3 o = new Vector3(x, y, -1799.8f);
                    if (Physics.Raycast(o, Vector3.forward, out var h, 2.4f, ~0, QueryTriggerInteraction.Ignore))
                        Debug.Log("DIAGRAY x=" + x.ToString("F2") + " y=" + y.ToString("F2") + " first hit at z=" + h.point.z.ToString("F3") + " by " + h.collider.name);
                    else Debug.Log("DIAGRAY x=" + x.ToString("F2") + " y=" + y.ToString("F2") + " clear for 2.4 m");
                }
            foreach (var c in checks)
            {
                bool a = NavMesh.SamplePosition(c.Item2, out var sa, .7f, NavMesh.AllAreas), b = NavMesh.SamplePosition(c.Item3, out var sb, .7f, NavMesh.AllAreas);
                if (!a || !b) { Debug.Log("DIAGPATH " + c.Item1 + " = NoSample start=" + a + " end=" + b + " " + c.Item2.ToString("F2") + " -> " + c.Item3.ToString("F2")); continue; }
                var path = new NavMeshPath();
                NavMesh.CalculatePath(sa.position, sb.position, NavMesh.AllAreas, path);
                var corners = path.corners;
                string last = corners.Length > 0 ? corners[corners.Length - 1].ToString("F2") : "-";
                Debug.Log("DIAGPATH " + c.Item1 + " = " + path.status + " corners=" + corners.Length + " last=" + last + " start=" + sa.position.ToString("F2") + " end=" + sb.position.ToString("F2"));
            }
        }
        private static Route Find(string name, Vector3 start, Vector3 end)
        {
            if (!NavMesh.SamplePosition(start, out var a, 3f, NavMesh.AllAreas) ||
                !NavMesh.SamplePosition(end, out var b, 3f, NavMesh.AllAreas))
                return new Route { name = name, status = "NoWalkableEndpoint", start = start, end = end, corners = Array.Empty<Vector3>() };
            var path = new NavMeshPath();
            NavMesh.CalculatePath(a.position, b.position, NavMesh.AllAreas, path);
            return new Route { name = name, status = path.status.ToString(), start = a.position, end = b.position, corners = path.corners };
        }
    }
}
