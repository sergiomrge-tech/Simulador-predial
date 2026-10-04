using System;
using System.Collections;
using UnityEngine;

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
                game = FindFirstObjectByType<GameRuntime>();
            if (streamService == null)
                streamService = GetComponent<WorldStreamService>();

            if (game == null || streamService == null)
            {
                Fail("World slice bridge requires GameRuntime and WorldStreamService.");
                yield break;
            }

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
            while (!streamService.LoadedCells.Contains(homeCell) &&
                   Time.realtimeSinceStartup < deadline)
                yield return null;

            if (!streamService.LoadedCells.Contains(homeCell))
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
            Debug.Log(
                "WORLD SLICE BRIDGE ACTIVE: " +
                homeCell.Name +
                " @ " +
                initialPosition);
        }

        private void Update()
        {
            if (!Active || game == null || game.World == null)
                return;

            GameObject currentRoot = game.World.Root;
            if (currentRoot == null || currentRoot == lastProceduralRoot)
                return;

            lastProceduralRoot = currentRoot;
            currentRoot.SetActive(false);

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
            Vector3 fallback = ResolveFallbackPosition(facilityId);
            float yaw = ResolveFallbackYaw(facilityId);

            var targetCell = WorldStreamingId.FromWorldPosition(fallback.x, fallback.z);
            streamService.Refresh(targetCell);

            float deadline = Time.realtimeSinceStartup + Mathf.Max(5f, initialLoadTimeoutSeconds);
            while (!streamService.LoadedCells.Contains(targetCell) &&
                   Time.realtimeSinceStartup < deadline)
                yield return null;

            if (!streamService.LoadedCells.Contains(targetCell))
            {
                Fail("Destination cell did not load: " + WorldStreamingSceneNaming.SceneName(targetCell));
                yield break;
            }

            Vector3 destination = fallback;
            float markerYaw = yaw;

            if (facilityId == "horizonte" &&
                TryFindMarker("horizonte", "GP_prologue_spawn_corridor", out WorldGameplayMarker marker))
            {
                destination = marker.transform.position;
                markerYaw = marker.transform.eulerAngles.y;
            }

            game.Player.Teleport(destination, markerYaw);
            streamService.StreamingEnabled = true;
            routing = null;

            Debug.Log(
                "WORLD SLICE ROUTE: " + facilityId +
                " -> " + targetCell.Name +
                " @ " + destination);
        }

        private string ResolveRuntimeFacility()
        {
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

        private static Vector3 ResolveFallbackPosition(string facilityId)
        {
            switch (facilityId)
            {
                case "garage":
                    return new Vector3(-2710f, 21.7f, -2150f);
                case "grocery":
                    return new Vector3(-2598f, 25.9f, -1480f);
                case "horizonte":
                    return new Vector3(-2350f, 28.0f, -1831f);
                case "home.starter":
                    return new Vector3(-2860f, 17.65f, -2266f);
                default:
                    return new Vector3(-2350f, 28.0f, -1831f);
            }
        }

        private static float ResolveFallbackYaw(string facilityId)
        {
            switch (facilityId)
            {
                case "garage": return 90f;
                case "grocery": return 90f;
                case "horizonte": return 0f;
                default: return 180f;
            }
        }

        private static bool TryFindMarker(
            string facilityId,
            string nameSuffix,
            out WorldGameplayMarker found)
        {
            WorldGameplayMarker[] markers = FindObjectsByType<WorldGameplayMarker>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None);

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
            Debug.LogError("WORLD SLICE BRIDGE: " + message);
        }
    }
}
