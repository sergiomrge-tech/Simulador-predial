using System;
using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps
{
    /// <summary>
    /// Temporary compatibility bridge for the first streamed-world build.
    ///
    /// Default gameplay remains unchanged. The bridge only activates with
    /// -worldSlice (or explicit Editor override), waits for the home cell to load,
    /// hides the procedural visual root, and teleports the existing player into
    /// the authored Santa Aurora coordinates.
    /// </summary>
    [DefaultExecutionOrder(-200)]
    public sealed class WorldSliceRuntimeBridge : MonoBehaviour
    {
        [SerializeField] private GameRuntime game;
        [SerializeField] private WorldStreamService streamService;
        [SerializeField] private WorldStreamingDebugOverlay debugOverlay;
        [SerializeField] private bool enableInEditor;
        [SerializeField] private Vector3 initialPosition = new Vector3(-2860f, 17.65f, -2266f);
        [SerializeField] private float initialYaw = 180f;
        [SerializeField] private float initialLoadTimeoutSeconds = 30f;

        private GameObject lastProceduralRoot;
        private Coroutine routing;

        public bool Active { get; private set; }
        public string LastError { get; private set; }

        public void Configure(
            GameRuntime runtime,
            WorldStreamService service,
            WorldStreamingDebugOverlay overlay = null)
        {
            game = runtime;
            streamService = service;
            debugOverlay = overlay;
        }

        private IEnumerator Start()
        {
            bool commandLine = Array.IndexOf(
                Environment.GetCommandLineArgs(),
                "-worldSlice") >= 0;

            if (!commandLine && !(Application.isEditor && enableInEditor))
                yield break;

            if (game == null)
                game = FindAnyObjectByType<GameRuntime>();
            if (streamService == null)
                streamService = GetComponent<WorldStreamService>();

            if (game == null || streamService == null)
            {
                Fail("World slice bridge requires GameRuntime and WorldStreamService.");
                yield break;
            }
            SceneManager.sceneLoaded += OnCellLoaded;

            float playerDeadline = Time.realtimeSinceStartup + 10f;
            while (game.Player == null && Time.realtimeSinceStartup < playerDeadline)
                yield return null;

            if (game.Player == null)
            {
                Fail("GameRuntime did not create the first-person player.");
                yield break;
            }

            streamService.TrackedTransform = game.Player.transform;
            streamService.StreamingEnabled = false;

            var homeCell = WorldStreamingId.FromWorldPosition(
                initialPosition.x,
                initialPosition.z);

            streamService.Refresh(homeCell);

            float deadline = Time.realtimeSinceStartup + Mathf.Max(5f, initialLoadTimeoutSeconds);
            while (!streamService.IsLoaded(homeCell) &&
                   Time.realtimeSinceStartup < deadline)
                yield return null;

            if (!streamService.IsLoaded(homeCell))
            {
                Fail(
                    "Initial world cell did not load: " +
                    WorldStreamingSceneNaming.SceneName(homeCell));
                yield break;
            }

            if (game.World != null && game.World.Root != null)
            {
                lastProceduralRoot = game.World.Root;
                game.World.Root.SetActive(false);
            }

            game.Player.Teleport(initialPosition, initialYaw);
            streamService.StreamingEnabled = true;

            if (debugOverlay != null)
                debugOverlay.StreamService = streamService;

            game.SetTablet(false);
            game.Notify(
                "CIDADE ANTIGA / vertical slice técnico. Streaming ativo. " +
                "O gameplay autoral ainda usa o runtime compatível enquanto a integração dos markers é validada.");

            Active = true;
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "-worldSliceQaTour") >= 0 && debugOverlay != null)
                StartCoroutine(gameObject.AddComponent<WorldSliceQaTour>().Run(game, streamService, debugOverlay));
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "-worldSliceQaWalk") >= 0 && debugOverlay != null)
                StartCoroutine(RunQaWalk());
            Debug.Log(
                "WORLD SLICE BRIDGE ACTIVE: " +
                homeCell.Name +
                " @ " +
                initialPosition);
        }

        // Development-player autopilot: continuous walk with screenshots and per-segment metrics (see WorldSliceQaWalker).
        private IEnumerator RunQaWalk()
        {
            // -worldSliceRoute <file>: a different autopilot route (evidence tour); the default is the continuous corridor walk.
            string routeFile = "world-walk-route.json";
            string[] args = Environment.GetCommandLineArgs();
            int ri = Array.IndexOf(args, "-worldSliceRoute");
            if (ri >= 0 && ri + 1 < args.Length) routeFile = args[ri + 1];
            string routeTag = System.IO.Path.GetFileNameWithoutExtension(routeFile);
            string path = System.IO.Path.Combine(Application.streamingAssetsPath, routeFile);
            if (!System.IO.File.Exists(path)) { Debug.LogError("WORLD WALK: route missing " + path); Application.Quit(2); yield break; }
            var route = JsonUtility.FromJson<WorldSliceQaWalker.Route>(System.IO.File.ReadAllText(path));
            var walker = gameObject.AddComponent<WorldSliceQaWalker>();
            walker.CaptureFolder = System.IO.Path.Combine(Application.persistentDataPath, routeFile == "world-walk-route.json" ? "WalkCaptures" : "Captures_" + routeTag);
            walker.SummaryPath = System.IO.Path.Combine(Application.persistentDataPath, routeFile == "world-walk-route.json" ? "world-walk-qa.json" : routeTag + "-qa.json");
            yield return StartCoroutine(walker.Run(game, streamService, debugOverlay, route));
            Debug.Log("WORLD WALK SUMMARY: " + walker.SummaryPath);
            yield return new WaitForSeconds(1f);
            Application.Quit(walker.Result.status == "PASS" ? 0 : 1);
        }

        private void Update()
        {
            if (!Active || game == null || game.World == null)
                return;

            GameObject currentRoot = game.World.Root;
            if (currentRoot == null || currentRoot == lastProceduralRoot)
                return;

            lastProceduralRoot = currentRoot;
            game.SetTablet(true);

            // Stop automatic position-driven refresh before the procedural runtime's
            // temporary small-coordinate teleport can pull in the wrong part of town.
            streamService.StreamingEnabled = false;

            if (routing != null)
                StopCoroutine(routing);
            routing = StartCoroutine(RouteToCurrentRuntimeContext());
        }

        private IEnumerator RouteToCurrentRuntimeContext()
        {
            string facilityId = ResolveRuntimeFacility();
            if (!WorldSliceDestinationRegistry.TryGet(
                    facilityId,
                    out WorldSliceDestination destinationInfo))
            {
                Fail(
                    "Runtime requested a facility outside the first playable corridor: " +
                    facilityId);
                yield break;
            }

            Vector3 fallback = destinationInfo.FallbackPosition;
            float yaw = destinationInfo.FallbackYaw;
            WorldStreamingId targetCell = destinationInfo.Cell;
            streamService.Refresh(targetCell);

            float deadline = Time.realtimeSinceStartup + Mathf.Max(5f, initialLoadTimeoutSeconds);
            while (!streamService.IsLoaded(targetCell) &&
                   Time.realtimeSinceStartup < deadline)
                yield return null;

            if (!streamService.IsLoaded(targetCell))
            {
                Fail("Destination cell did not load: " + WorldStreamingSceneNaming.SceneName(targetCell));
                yield break;
            }

            Vector3 destination = fallback;
            float markerYaw = yaw;

            if (!string.IsNullOrEmpty(destinationInfo.PreferredMarkerSuffix) &&
                TryFindMarker(
                    facilityId,
                    destinationInfo.PreferredMarkerSuffix,
                    out WorldGameplayMarker marker))
            {
                destination = marker.transform.position;
                markerYaw = marker.transform.eulerAngles.y;
            }

            game.Player.Teleport(destination, markerYaw);
            if (game.World?.Root != null) game.World.Root.SetActive(false);
            game.SetTablet(false);
            streamService.StreamingEnabled = true;
            routing = null;

            Debug.Log(
                "WORLD SLICE ROUTE: " + facilityId +
                " -> " + targetCell.Name +
                " @ " + destination);
        }

        private string ResolveRuntimeFacility()
        {
            if (game.PreviewLocation != null) return game.PreviewLocation.id;
            if (game.AtOffice)
                return "garage";

            if (game.Session != null)
            {
                if (game.Session.IsPrologue)
                    return "horizonte";

                ServiceDefinition job = game.Session.ActiveJob;
                if (job != null && !string.IsNullOrEmpty(job.locationId))
                    return job.locationId;
            }

            return "horizonte";
        }

        private static bool TryFindMarker(
            string facilityId,
            string nameSuffix,
            out WorldGameplayMarker found)
        {
            WorldGameplayMarker[] markers = UnityEngine.Object.FindObjectsByType<WorldGameplayMarker>(
                FindObjectsInactive.Exclude);

            foreach (WorldGameplayMarker marker in markers)
            {
                if (!string.Equals(marker.FacilityId, facilityId, StringComparison.Ordinal))
                    continue;
                if (!marker.MarkerName.EndsWith(nameSuffix, StringComparison.Ordinal))
                    continue;

                found = marker;
                return true;
            }

            found = null;
            return false;
        }

        private void Fail(string message)
        {
            LastError = message;
            Active = false;
            if (streamService != null) streamService.StreamingEnabled = false;
            if (game?.World?.Root != null) game.World.Root.SetActive(true);
            Debug.LogError("WORLD SLICE BRIDGE: " + message);
        }

        private void OnDestroy() => SceneManager.sceneLoaded -= OnCellLoaded;

        private void OnCellLoaded(Scene scene, LoadSceneMode mode)
        {
            // Bind the existing authored panel collider to the preserved QD-01
            // station logic. No proxy mesh, marker relocation or save schema change.
            foreach (var root in scene.GetRootGameObjects())
                foreach (var marker in root.GetComponentsInChildren<WorldGameplayMarker>())
                {
                    if (marker.FacilityId != "horizonte" ||
                        !marker.MarkerName.EndsWith("GP_quadro_tecnico", StringComparison.Ordinal)) continue;
                    foreach (var collider in root.GetComponentsInChildren<MeshCollider>())
                        if (collider.name.EndsWith("W2_horizonte__F03_quadro_tecnico", StringComparison.Ordinal))
                        {
                            var station = collider.GetComponent<TechnicalStation>();
                            if (station == null) station = collider.gameObject.AddComponent<TechnicalStation>();
                            station.id = StationId.Distribution;
                            station.label = "QD-01 / QUADRO TÉCNICO";
                        }
                }
        }
    }
}
