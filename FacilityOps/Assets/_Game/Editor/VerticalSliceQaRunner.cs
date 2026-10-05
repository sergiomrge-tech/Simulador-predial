using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using FacilityOps;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;

namespace FacilityOps.Editor
{
    public static class VerticalSliceQaRunner
    {
        [Serializable] public sealed class RouteLeg
        {
            public string id, status, failure; public Vector3 from, to, failurePosition; public float distance;
            public Vector3[] corners; public string[] requiredCells;
        }
        [Serializable] public sealed class Report
        {
            public string status, fingerprint, unityVersion, utc; public bool READY_FOR_USER_TEST;
            public float totalDistance; public VerticalSliceQaItem[] items; public RouteLeg[] route;
        }
        [Serializable] private sealed class RuntimeVerdict
        {
            public string status, fingerprint, scope; public int criticalErrors, captures; public bool streaming, saveLoad, continuous;
        }
        [Serializable] private sealed class ProcessVerdict { public string status, fingerprint; public int exitCode, criticalLogErrors; }
        private static string Root => Path.GetFullPath(Path.Combine(Application.dataPath, "../.."));
        public static string EvidenceFolder => Path.Combine(Root, "Docs/ValidationEvidence/VerticalSliceQA");
        public static string RoutePath => Path.Combine(EvidenceFolder, "route.json");
        private static readonly List<VerticalSliceQaItem> items = new List<VerticalSliceQaItem>();

        [MenuItem("Facility Ops/QA/Run Vertical Slice QA (read-only assets)")]
        public static void Run() => Execute(false);
        public static void ValidateStaticBatch() => Execute(true);
        private static void Execute(bool throwOnFailure)
        {
            items.Clear(); Directory.CreateDirectory(EvidenceFolder);
            Check("compilation", () => { }); // Entry point cannot execute before Unity finishes compiling.
            Check("manifest", WorldStreamingManifestValidator.ValidateOrThrow);
            Check("references", WorldCellSceneValidator.ValidatePilotScenes);
            Check("build_settings", WorldCellBuildSettingsUtility.ValidateCellScenesInBuildSettings);
            Check("save_load", SaveRoundTrip);
            Check("legacy_rules", ProjectBuilder.RunRules);
            Check("navmesh", WorldSliceWalkabilityQa.BuildReference);
            var report = new Report { fingerprint = WorldSliceBuildGate.Fingerprint(), unityVersion = Application.unityVersion, utc = DateTime.UtcNow.ToString("O") };
            Check("cells", () => InspectAndPlan(report));
            report.fingerprint = WorldSliceBuildGate.Fingerprint();
            MergeRuntime("editor-runtime.json", false);
            MergeRuntime("player-qa.json", true);
            report.items = items.ToArray();
            report.READY_FOR_USER_TEST = VerticalSliceDeliveryGate.Ready(report.items);
            report.status = items.Any(i => i.status == "FAIL") ? "FAIL" : report.READY_FOR_USER_TEST ? "PASS" : "PENDING_PLAYER_VALIDATION";
            File.WriteAllText(Path.Combine(EvidenceFolder, "qa.json"), JsonUtility.ToJson(report, true));
            var md = new StringBuilder("# Vertical Slice QA\n\n" + report.status + "\n\nREADY_FOR_USER_TEST = " + report.READY_FOR_USER_TEST.ToString().ToUpperInvariant() + "\n\n| Item | Result | Detail |\n| --- | --- | --- |\n");
            foreach (var item in report.items) md.AppendLine($"| {item.id} | {item.status} | {item.detail.Replace("\n", " ").Replace("|", "/")} @ {item.position:F2} |");
            md.AppendLine($"\nRoute distance: {report.totalDistance:F1} m. NavMesh is a planning reference; only the continuous controller run proves physical traversal.\nFingerprint: `{report.fingerprint}`\n");
            File.WriteAllText(Path.Combine(EvidenceFolder, "qa.md"), md.ToString());
            Debug.Log("VERTICAL SLICE QA: " + report.status + " / " + EvidenceFolder);
            string[] runtimeOnly = { "player", "log", "route", "streaming", "runtime_save", "editor_route", "performance" };
            if (throwOnFailure && items.Any(i => i.status == "FAIL" && !runtimeOnly.Contains(i.id)))
                throw new BuildFailedException("Static vertical slice QA failed; see qa.md.");
        }
        private static void Check(string id, Action action)
        {
            try { action(); items.Add(new VerticalSliceQaItem(id, "PASS", "Validated")); }
            catch (Exception e) { items.Add(new VerticalSliceQaItem(id, "FAIL", e.Message)); }
        }
        private static void SaveRoundTrip()
        {
            string path = Path.Combine(EvidenceFolder, "Scratch", Guid.NewGuid() + ".json");
            try
            {
                var career = new CareerData { money = 3210 };
                SaveService.Save(career, path);
                if (SaveService.Load(path).money != 3210) throw new InvalidDataException("QA-only career differs after reload.");
                career.money = 4321; SaveService.Save(career, path);
                if (SaveService.Load(path).money != 4321 || !File.Exists(path + ".bak")) throw new InvalidDataException("Backup roundtrip failed.");
            }
            finally { foreach (string suffix in new[] { "", ".bak", ".tmp" }) if (File.Exists(path + suffix)) File.Delete(path + suffix); }
        }
        private static void InspectAndPlan(Report report)
        {
            string[] paths = WorldIntegrationQa.PilotScenePaths();
            if (paths.Length != 15) throw new InvalidDataException("Expected 15 cell scenes, found " + paths.Length);
            var setup = EditorSceneManager.GetSceneManagerSetup();
            NavMeshDataInstance navInstance = default;
            try
            {
                var ids = new HashSet<string>(); var markers = new List<WorldGameplayMarker>();
                var markerNames = new HashSet<string>(); int missing = 0;
                for (int i = 0; i < paths.Length; i++)
                {
                    var scene = EditorSceneManager.OpenScene(paths[i], i == 0 ? OpenSceneMode.Single : OpenSceneMode.Additive);
                    var roots = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<WorldCellRoot>(true)).ToArray();
                    if (roots.Length != 1 || !ids.Add(roots[0].CellId)) throw new InvalidDataException("Duplicate/missing cell root: " + paths[i]);
                    var root = roots[0];
                    foreach (var marker in root.GetComponentsInChildren<WorldGameplayMarker>(true))
                    {
                        if (!markerNames.Add(marker.MarkerName)) items.Add(new VerticalSliceQaItem("marker_duplicate", "FAIL", marker.MarkerName, marker.transform.position));
                        markers.Add(marker);
                    }
                    foreach (string layerName in new[] { "Terrain", "Roads", "Architecture" })
                    {
                        Transform layer = root.transform.Find(layerName);
                        if (layer == null) throw new InvalidDataException(root.CellId + " missing " + layerName);
                        foreach (var mesh in layer.GetComponentsInChildren<MeshFilter>(true))
                            if (mesh.sharedMesh != null && mesh.GetComponent<Collider>() == null)
                            {
                                missing++; items.Add(new VerticalSliceQaItem("collider", "FAIL", root.CellId + "/" + layerName + "/" + mesh.name, mesh.transform.position));
                            }
                    }
                    foreach (var door in root.GetComponentsInChildren<WorldDoor>(true))
                    {
                        if (door.GetComponent<Collider>() == null) items.Add(new VerticalSliceQaItem("door_collider", "FAIL", door.DoorId, door.transform.position));
                        door.SetOpenImmediate(true); // Reference pose only; never save the scene.
                    }
                }
                items.Add(new VerticalSliceQaItem("colliders", missing == 0 ? "PASS" : "FAIL", missing + " render meshes without colliders in physical layers"));
                items.Add(new VerticalSliceQaItem("markers", "PASS", markerNames.Count + " unique marker names inspected"));
                Physics.SyncTransforms();
                var nav = AssetDatabase.LoadAssetAtPath<NavMeshData>(WorldSliceWalkabilityQa.NavAsset);
                if (nav == null) throw new InvalidDataException("Reference NavMesh unavailable after bake.");
                navInstance = NavMesh.AddNavMeshData(nav);
                Vector3 home = DestinationFloor("home.starter"), garage = DestinationFloor("garage"), horizon = DestinationFloor("horizonte"), grocery = DestinationFloor("grocery");
                Vector3 gate = Marker(markers, "horizonte", "entrance__pedestrian_gate").transform.position;
                Vector3 lobby = Marker(markers, "horizonte", "entrance__lobby").transform.position;
                var spawn = Marker(markers, "horizonte", "GP_prologue_spawn_corridor");
                var panel = Marker(markers, "horizonte", "GP_quadro_tecnico");
                Vector3 panelApproach = panel.transform.position + panel.transform.forward - Vector3.up * 1.4f;
                ProbeSpawn("portão", gate, "portal_"); ProbeSpawn("portaria", lobby, "portal_");
                if (Physics.OverlapSphere(panel.transform.position, .6f, ~0, QueryTriggerInteraction.Ignore).Length == 0)
                    items.Add(new VerticalSliceQaItem("important_object", "FAIL", "Technical interaction marker has no nearby collider", panel.transform.position));
                foreach (var point in new[] { ("Lar", home), ("Oficina", garage), ("Horizonte", horizon), ("Mercearia", grocery), ("Prólogo", spawn.transform.position - Vector3.up * .9f) })
                    ProbeSpawn(point.Item1, point.Item2);
                items.Add(new VerticalSliceQaItem("spawn", items.Any(x => x.id.StartsWith("spawn_") && x.status == "FAIL") ? "FAIL" : "PASS", "ID/marker-based physical floor and capsule probes"));
                var waypoints = new[] { home, garage, horizon, gate, lobby, spawn.transform.position - Vector3.up * .9f, panelApproach, lobby, gate, grocery, home };
                var names = new[] { "Lar→Oficina", "Oficina→Horizonte", "Horizonte→portão", "portão→portaria", "portaria→4º andar", "4º andar→área técnica", "área técnica→portaria", "portaria→portão", "portão→Mercearia", "Mercearia→Lar" };
                var legs = new List<RouteLeg>();
                for (int i = 0; i < names.Length; i++)
                {
                    var leg = PlanLeg(names[i], waypoints[i], waypoints[i + 1], ids);
                    legs.Add(leg); report.totalDistance += leg.distance;
                    items.Add(new VerticalSliceQaItem("route:" + leg.id, leg.status, leg.failure ?? (leg.distance.ToString("F1") + " m; cells: " + string.Join(",", leg.requiredCells)), leg.failurePosition));
                }
                report.route = legs.ToArray();
                bool pass = legs.All(l => l.status == "PASS");
                items.Add(new VerticalSliceQaItem("route_plan", pass ? "PASS" : "FAIL", "Continuous NavMesh legs; doors opened in reference pose, no links/proxy floors added"));
                if (pass) WriteWalkerRoute(legs, home, markers, panel);
                else if (File.Exists(RoutePath)) File.Delete(RoutePath); // Never leave a stale runnable plan after a failure.
            }
            finally { if (navInstance.valid) navInstance.Remove(); EditorSceneManager.RestoreSceneManagerSetup(setup); }
        }
        private static Vector3 DestinationFloor(string id) => WorldSliceDestinationRegistry.Require(id).FallbackPosition - Vector3.up;
        private static WorldGameplayMarker Marker(IEnumerable<WorldGameplayMarker> markers, string facility, string suffix)
        {
            var found = markers.Where(m => m.FacilityId == facility && m.MarkerName.EndsWith(suffix, StringComparison.Ordinal)).ToArray();
            if (found.Length != 1) throw new InvalidDataException(facility + "/" + suffix + " expected one marker, found " + found.Length);
            return found[0];
        }
        private static void ProbeSpawn(string name, Vector3 nearFloor, string prefix = "spawn_")
        {
            if (!Physics.Raycast(nearFloor + Vector3.up * 2f, Vector3.down, out var hit, 4f, ~0, QueryTriggerInteraction.Ignore))
            { items.Add(new VerticalSliceQaItem(prefix + name, "FAIL", "No floor / potential falling player", nearFloor)); return; }
            Vector3 feet = hit.point + Vector3.up * .06f;
            var blockers = Physics.OverlapCapsule(feet + Vector3.up * .4f, feet + Vector3.up * 1.4f, .2f, ~0, QueryTriggerInteraction.Ignore);
            items.Add(new VerticalSliceQaItem(prefix + name, blockers.Length == 0 ? "PASS" : "FAIL", blockers.Length == 0 ? "Floor and clear capsule" : "Capsule overlaps " + string.Join(",", blockers.Select(c => c.name)), feet));
        }
        public static RouteLeg PlanLeg(string id, Vector3 from, Vector3 to, ISet<string> availableCells)
        {
            var leg = new RouteLeg { id = id, from = from, to = to, status = "FAIL", corners = Array.Empty<Vector3>(), requiredCells = Array.Empty<string>() };
            if (!NavMesh.SamplePosition(from, out var a, 1.25f, NavMesh.AllAreas)) { leg.failure = "No NavMesh at start"; leg.failurePosition = from; return leg; }
            if (!NavMesh.SamplePosition(to, out var b, 1.25f, NavMesh.AllAreas)) { leg.failure = "No NavMesh at endpoint"; leg.failurePosition = to; return leg; }
            var path = new NavMeshPath(); NavMesh.CalculatePath(a.position, b.position, NavMesh.AllAreas, path); leg.corners = path.corners;
            if (path.status != NavMeshPathStatus.PathComplete) { leg.failure = path.status.ToString(); leg.failurePosition = leg.corners.Length > 0 ? leg.corners[leg.corners.Length - 1] : from; return leg; }
            var cells = new HashSet<string>();
            for (int i = 1; i < leg.corners.Length; i++)
            {
                Vector3 start = leg.corners[i - 1], end = leg.corners[i]; float distance = Vector3.Distance(start, end); leg.distance += distance;
                int samples = Math.Max(1, Mathf.CeilToInt(distance));
                Vector3? previousSurface = null;
                for (int j = 0; j <= samples; j++)
                {
                    Vector3 point = Vector3.Lerp(start, end, j / (float)samples);
                    string cell = WorldStreamingId.FromWorldPosition(point.x, point.z).Name; cells.Add(cell);
                    if (!availableCells.Contains(cell)) { leg.failure = "Required streaming cell absent: " + cell; leg.failurePosition = point; return leg; }
                    // NavMesh corners encode turns, not every terrain height change.
                    // Project the probe onto the closest physical floor before
                    // checking coverage, rather than treating a hillside chord as a gap.
                    var floors = Physics.RaycastAll(point + Vector3.up * 8f, Vector3.down, 16f, ~0, QueryTriggerInteraction.Ignore)
                        .Where(h => h.normal.y > .5f).OrderBy(h => Mathf.Abs(h.point.y - point.y)).ToArray();
                    bool covered = false;
                    foreach (var floor in floors)
                        if (NavMesh.SamplePosition(floor.point, out var projected, .45f, NavMesh.AllAreas) &&
                            Vector2.Distance(new Vector2(projected.position.x, projected.position.z), new Vector2(point.x, point.z)) < .4f)
                        {
                            covered = true;
                            if (previousSurface.HasValue)
                            {
                                Vector3 movement = projected.position - previousSurface.Value;
                                if (movement.magnitude > .01f && Physics.CapsuleCast(previousSurface.Value + Vector3.up * .45f, previousSurface.Value + Vector3.up * 1.35f,
                                    .18f, movement.normalized, out var obstruction, movement.magnitude, ~0, QueryTriggerInteraction.Ignore) && obstruction.normal.y < .5f && obstruction.collider.GetComponentInParent<WorldDoor>() == null)
                                { leg.failure = "NavMesh crosses physical wall: " + obstruction.collider.name; leg.failurePosition = obstruction.point; return leg; }
                            }
                            previousSurface = projected.position;
                            break;
                        }
                    if (!covered) { leg.failure = "No physical floor with NavMesh coverage (gap or missing collision)"; leg.failurePosition = point; return leg; }
                }
            }
            leg.requiredCells = cells.OrderBy(c => c).ToArray(); leg.status = "PASS"; return leg;
        }
        private static void WriteWalkerRoute(List<RouteLeg> legs, Vector3 home, List<WorldGameplayMarker> markers, WorldGameplayMarker panel)
        {
            var steps = new List<WorldSliceQaWalker.Step>();
            WorldSliceQaWalker.Step Capture(string name, Vector3 aim) => new WorldSliceQaWalker.Step { kind = "capture", name = name, aim = new WorldSliceQaWalker.Vec3(aim) };
            steps.Add(new WorldSliceQaWalker.Step { kind = "accept" });
            steps.Add(new WorldSliceQaWalker.Step { kind = "teleport", name = "initial placement only", yaw = WorldSliceDestinationRegistry.Require("home.starter").FallbackYaw, corners = new[] { new WorldSliceQaWalker.Vec3(WorldSliceDestinationRegistry.Require("home.starter").FallbackPosition) } });
            steps.Add(Capture("01-lar", home + Quaternion.Euler(0, WorldSliceDestinationRegistry.Require("home.starter").FallbackYaw, 0) * Vector3.forward * 15f + Vector3.up * 3f));
            steps.Add(Capture("11-streaming-overlay", home + Vector3.up * 2f + Vector3.right * 15f));
            steps.Add(Capture("02-rua", home + Vector3.up * 2f + Vector3.right * 35f));
            string[] shots = { "03-oficina", "04-horizonte-exterior", "05-portao", "06-portaria", "08-quarto-andar", "09-area-tecnica", null, null, "10-mercearia", "13-retorno" };
            for (int i = 0; i < legs.Count; i++)
            {
                var leg = legs[i];
                steps.Add(new WorldSliceQaWalker.Step { kind = "mark", name = leg.id });
                Vector3[] corners = leg.corners;
                if (i == 4 && corners.Length >= 3)
                {
                    int mid = corners.Length / 2;
                    steps.Add(Walk(leg.id + "/stair", corners.Take(mid + 1).ToArray()));
                    steps.Add(Capture("07-escada", corners[Math.Min(mid + 1, corners.Length - 1)] + Vector3.up * 1.5f));
                    steps.Add(Walk(leg.id, corners.Skip(mid).ToArray()));
                }
                else steps.Add(Walk(leg.id, corners));
                if (shots[i] != null) steps.Add(Capture(shots[i], i == 5 ? panel.transform.position : leg.to + Vector3.up * 2.5f + Vector3.forward * 8f));
                if (i == 5) { steps.Add(new WorldSliceQaWalker.Step { kind = "interact", aim = new WorldSliceQaWalker.Vec3(panel.transform.position), label = "QD-01" }); steps.Add(Capture("12-performance-overlay", panel.transform.position)); }
            }
            steps.Add(new WorldSliceQaWalker.Step { kind = "save" }); steps.Add(new WorldSliceQaWalker.Step { kind = "verifysave", label = "continuous route completed" });
            File.WriteAllText(RoutePath, JsonUtility.ToJson(new WorldSliceQaWalker.Route { version = 1, note = "Derived from facility IDs/markers and current colliders. One initial placement; continuous thereafter. No art changes.", steps = steps.ToArray() }, true));
        }
        private static WorldSliceQaWalker.Step Walk(string name, Vector3[] corners) => new WorldSliceQaWalker.Step { kind = "walk", name = name, corners = Array.ConvertAll(corners, p => new WorldSliceQaWalker.Vec3(p)) };
        private static void MergeRuntime(string file, bool player)
        {
            string path = Path.Combine(EvidenceFolder, file);
            if (!File.Exists(path))
            { items.Add(new VerticalSliceQaItem(player ? "player" : "editor_route", "PENDING", "Run " + (player ? "Development Player" : "continuous Play Mode test"))); return; }
            var verdict = JsonUtility.FromJson<RuntimeVerdict>(File.ReadAllText(path));
            bool fresh = verdict != null && verdict.fingerprint == WorldSliceBuildGate.Fingerprint();
            bool pass = fresh && verdict.status == "PASS";
            if (!player) { items.Add(new VerticalSliceQaItem("editor_route", pass ? "PASS" : "FAIL", fresh ? verdict.status : "Stale runtime evidence")); return; }
            string processPath = Path.Combine(EvidenceFolder, "process-receipt.json");
            var process = File.Exists(processPath) ? JsonUtility.FromJson<ProcessVerdict>(File.ReadAllText(processPath)) : null;
            bool processPass = process != null && process.status == "PASS" && process.fingerprint == WorldSliceBuildGate.Fingerprint() && process.exitCode == 0 && process.criticalLogErrors == 0;
            items.Add(new VerticalSliceQaItem("player", pass && processPass && verdict.scope == "PLAYER" && verdict.captures == 13 ? "PASS" : "FAIL", "Fresh Player receipt, clean process exit and 13 checkpoint images required"));
            items.Add(new VerticalSliceQaItem("route", pass && verdict.continuous ? "PASS" : "FAIL", "Physical continuous walk, not teleport tour"));
            items.Add(new VerticalSliceQaItem("streaming", pass && verdict.streaming ? "PASS" : "FAIL", "Load/unload and unique scene checks"));
            items.Add(new VerticalSliceQaItem("runtime_save", pass && verdict.saveLoad ? "PASS" : "FAIL", "Player career loaded back after the complete walk"));
            items.Add(new VerticalSliceQaItem("log", fresh && processPass && verdict.criticalErrors == 0 ? "PASS" : "FAIL", fresh ? verdict.criticalErrors + " critical errors; process/log proof required" : "Evidence missing/stale"));
            string performance = Path.Combine(EvidenceFolder, "performance.json");
            if (File.Exists(performance))
            {
                var measurement = JsonUtility.FromJson<VerticalSliceProfiler.Report>(File.ReadAllText(performance));
                items.Add(new VerticalSliceQaItem("performance", measurement.frames > 0 && string.IsNullOrEmpty(measurement.warning) ? "PASS" : "WARNING", measurement.warning ?? measurement.scope));
            }
        }
        public static void AssertReadyBatch()
        {
            Run(); var report = JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(EvidenceFolder, "qa.json")));
            if (!report.READY_FOR_USER_TEST) throw new BuildFailedException("READY_FOR_USER_TEST is FALSE; see qa.md.");
        }
    }
}
