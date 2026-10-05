using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace FacilityOps
{
    public sealed class VerticalSlicePlayerQa : MonoBehaviour
    {
        [Serializable] public sealed class Verdict
        {
            public string status, fingerprint, scope, failure, captureFolder; public int criticalErrors, captures;
            public bool streaming, saveLoad, continuous; public string[] errors;
        }
        private readonly List<string> errors = new List<string>();
        private int criticalErrors; private bool duplicateScenes; private bool running;
        private float nextSceneCheck;
        private readonly HashSet<string> scenePaths = new HashSet<string>();
        public Verdict Result { get; private set; }
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (Application.isEditor || !Debug.isDebugBuild || !VerticalSliceQaFlags.Has("-verticalSliceQa")) return;
            if (FindAnyObjectByType<VerticalSlicePlayerQa>() != null) return;
            new GameObject("Vertical Slice QA (flag only)").AddComponent<VerticalSlicePlayerQa>().StartCoroutine(AutoRun());
        }
        private static IEnumerator AutoRun()
        {
            var harness = FindAnyObjectByType<VerticalSlicePlayerQa>();
            string root = VerticalSliceQaFlags.Value("-verticalSliceQaRoot", Path.GetFullPath(Path.Combine(Application.dataPath, "..")));
            string evidence = Path.Combine(root, "Docs/ValidationEvidence/VerticalSliceQA");
            string fingerprint = VerticalSliceQaFlags.Value("-verticalSliceQaFingerprint");
            string routePath = VerticalSliceQaFlags.Value("-verticalSliceQaRoute", Path.Combine(evidence, "route.json"));
            if (!VerticalSliceQaFlags.Has("-worldSlice") || string.IsNullOrEmpty(fingerprint) || !File.Exists(routePath))
            { harness.WriteFailure(evidence, fingerprint, "Required -worldSlice, fingerprint or route file absent"); Application.Quit(2); yield break; }
            var game = FindAnyObjectByType<GameRuntime>(); var service = FindAnyObjectByType<WorldStreamService>();
            var overlay = FindAnyObjectByType<WorldStreamingDebugOverlay>(); var bridge = FindAnyObjectByType<WorldSliceRuntimeBridge>();
            var profiler = harness.gameObject.AddComponent<VerticalSliceProfiler>(); profiler.Configure(service);
            float deadline = Time.realtimeSinceStartup + 90f;
            while (bridge != null && !bridge.Active && Time.realtimeSinceStartup < deadline) yield return null;
            if (bridge == null || !bridge.Active || game == null || service == null || overlay == null)
            { harness.WriteFailure(evidence, fingerprint, "Runtime bootstrap timeout / missing components"); profiler.Write(evidence); Application.Quit(2); yield break; }
            WorldSliceQaWalker.Route route = null;
            try { route = JsonUtility.FromJson<WorldSliceQaWalker.Route>(File.ReadAllText(routePath)); ValidateRoute(route); }
            catch (Exception e) { harness.WriteFailure(evidence, fingerprint, e.Message); }
            if (route == null || harness.Result != null) { Application.Quit(2); yield break; }
            var nav = Resources.Load<NavMeshData>("QA/VerticalSliceReference");
            if (nav == null) { harness.WriteFailure(evidence, fingerprint, "Development QA NavMesh not packaged"); Application.Quit(2); yield break; }
            var instance = NavMesh.AddNavMeshData(nav);
            try { yield return harness.Run(game, service, overlay, route, evidence, fingerprint, "PLAYER", Path.Combine(root, "Docs/Previews/UnityVerticalSliceV01", DateTime.UtcNow.ToString("yyyyMMdd-HHmmss"))); }
            finally { instance.Remove(); }
            profiler.Write(evidence);
            Application.Quit(harness.Result.status == "PASS" ? 0 : 1);
        }
        private void OnEnable() => Application.logMessageReceivedThreaded += OnLog;
        private void OnDisable() => Application.logMessageReceivedThreaded -= OnLog;
        private void OnLog(string condition, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert) return;
            lock (errors) { criticalErrors++; if (errors.Count < 40) errors.Add(condition + "\n" + stack); }
        }
        private void Update()
        {
            if (!running || Time.realtimeSinceStartup < nextSceneCheck) return;
            nextSceneCheck = Time.realtimeSinceStartup + .25f;
            scenePaths.Clear();
            for (int i = 0; i < SceneManager.sceneCount; i++)
                if (!scenePaths.Add(SceneManager.GetSceneAt(i).path)) duplicateScenes = true;
        }
        public static void ValidateRoute(WorldSliceQaWalker.Route route)
        {
            if (route?.steps == null || route.version != 1) throw new InvalidDataException("Route schema invalid");
            int placements = 0, walks = 0; bool moved = false; Vector3? last = null;
            foreach (var step in route.steps)
            {
                if (step.kind == "teleport")
                {
                    if (moved || ++placements > 1 || step.corners == null || step.corners.Length != 1) throw new InvalidDataException("Teleport allowed only for one initial placement");
                    last = step.corners[0].V;
                }
                else if (step.kind == "accept" && moved) throw new InvalidDataException("Accept cannot reroute the actor after the continuous walk begins");
                else if (step.kind == "walk")
                {
                    if (placements != 1 || step.corners == null || step.corners.Length < 2) throw new InvalidDataException("Missing placement / walk corners");
                    foreach (var corner in step.corners) if (!float.IsFinite(corner.x) || !float.IsFinite(corner.y) || !float.IsFinite(corner.z)) throw new InvalidDataException("Nonfinite waypoint");
                    if (last.HasValue && Vector3.Distance(last.Value, step.corners[0].V) > 2f) throw new InvalidDataException("Disconnected walk segment: " + step.name);
                    moved = true; walks++; last = step.corners[step.corners.Length - 1].V;
                }
                else if (Array.IndexOf(new[] { "accept", "capture", "interact", "save", "verifysave", "tablet", "mark", "wait" }, step.kind) < 0)
                    throw new InvalidDataException("Unknown route action: " + step.kind);
            }
            if (walks == 0 || placements != 1) throw new InvalidDataException("No continuous walk in route");
        }
        public IEnumerator Run(GameRuntime game, WorldStreamService service, WorldStreamingDebugOverlay overlay, WorldSliceQaWalker.Route route,
            string evidence, string fingerprint, string scope, string captureFolder, Action<string, Vector3> captureHook = null)
        {
            ValidateRoute(route);
            running = true;
            var walker = gameObject.AddComponent<WorldSliceQaWalker>();
            walker.CaptureFolder = captureFolder; walker.CaptureHook = captureHook;
            walker.SummaryPath = Path.Combine(evidence, scope == "PLAYER" ? "continuous-walk.json" : "editor-continuous-walk.json");
            yield return walker.Run(game, service, overlay, route);
            if (scope == "PLAYER")
            {
                float deadline = Time.realtimeSinceStartup + 10f;
                while ((!Directory.Exists(captureFolder) || Directory.GetFiles(captureFolder, "*.png").Length < 13) && Time.realtimeSinceStartup < deadline) yield return null;
            }
            running = false;
            Result = new Verdict { fingerprint = fingerprint, scope = scope, failure = walker.Result.failure, captureFolder = captureFolder,
                streaming = !duplicateScenes && service.TotalLoads > 0 && service.TotalUnloads > 0 && service.LoadedCells.Count <= 15,
                saveLoad = walker.Result.saveChecks > 0, continuous = walker.Result.status == "PASS",
                captures = captureFolder != null && Directory.Exists(captureFolder) ? Directory.GetFiles(captureFolder, "*.png").Length : 0 };
            lock (errors) { Result.criticalErrors = criticalErrors; Result.errors = errors.ToArray(); }
            Result.status = Result.continuous && Result.streaming && Result.saveLoad && Result.criticalErrors == 0 && (scope != "PLAYER" || Result.captures == 13) ? "PASS" : "FAIL";
            Directory.CreateDirectory(evidence);
            File.WriteAllText(Path.Combine(evidence, scope == "PLAYER" ? "player-qa.json" : "editor-runtime.json"), JsonUtility.ToJson(Result, true));
        }
        private void WriteFailure(string evidence, string fingerprint, string failure)
        {
            Directory.CreateDirectory(evidence); Result = new Verdict { status = "FAIL", scope = "PLAYER", fingerprint = fingerprint, failure = failure, criticalErrors = criticalErrors };
            File.WriteAllText(Path.Combine(evidence, "player-qa.json"), JsonUtility.ToJson(Result, true));
        }
    }
}
