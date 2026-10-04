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
    [DefaultExecutionOrder(200)]
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
                game.World.Root.SetActive(false);

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

        private void Fail(string message)
        {
            LastError = message;
            Active = false;
            Debug.LogError("WORLD SLICE BRIDGE: " + message);
        }
    }
}
