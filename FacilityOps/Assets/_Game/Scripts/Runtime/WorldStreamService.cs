using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps
{
    /// <summary>
    /// Opt-in additive scene streamer for Santa Aurora.
    ///
    /// It is deliberately inert unless enabled and attached to a scene.
    /// It does not replace WorldBuilder, does not touch saves, and only loads scenes
    /// that Unity reports as available in the build.
    /// </summary>
    public sealed class WorldStreamService : MonoBehaviour
    {
        [SerializeField] private Transform trackedTransform;
        [SerializeField] private bool streamingEnabled;
        [SerializeField] private float refreshIntervalSeconds = 0.25f;

        private readonly HashSet<WorldStreamingId> loaded = new HashSet<WorldStreamingId>();
        private readonly HashSet<WorldStreamingId> pendingLoads = new HashSet<WorldStreamingId>();
        private readonly HashSet<WorldStreamingId> pendingUnloads = new HashSet<WorldStreamingId>();
        private float nextRefresh;
        private WorldStreamingId currentCell;
        private bool hasCurrentCell;
        private HashSet<WorldStreamingId> desiredLoads = new HashSet<WorldStreamingId>();
        private HashSet<WorldStreamingId> desiredKeep = new HashSet<WorldStreamingId>();
        private readonly List<WorldStreamingId> unloadScratch = new List<WorldStreamingId>();

        private void OnEnable()
        {
            RebuildLoadedIndex();
        }

        public bool StreamingEnabled
        {
            get => streamingEnabled;
            set => streamingEnabled = value;
        }

        public Transform TrackedTransform
        {
            get => trackedTransform;
            set => trackedTransform = value;
        }

        public WorldStreamingId CurrentCell => currentCell;
        public bool HasCurrentCell => hasCurrentCell;
        public IReadOnlyCollection<WorldStreamingId> LoadedCells => loaded;
        public bool IsLoaded(WorldStreamingId id) => loaded.Contains(id) && !pendingUnloads.Contains(id);
        public int PendingLoadCount => pendingLoads.Count;
        public int PendingUnloadCount => pendingUnloads.Count;
        public double LastLoadMilliseconds { get; private set; }
        public double LastUnloadMilliseconds { get; private set; }
        public double MaxLoadMilliseconds { get; private set; }
        public double MaxUnloadMilliseconds { get; private set; }
        public int TotalLoads { get; private set; }
        public int TotalUnloads { get; private set; }

        private void Update()
        {
            if (!streamingEnabled || trackedTransform == null || Time.unscaledTime < nextRefresh)
                return;

            nextRefresh = Time.unscaledTime + Mathf.Max(0.05f, refreshIntervalSeconds);
            var nextCell = WorldStreamingId.FromWorldPosition(
                trackedTransform.position.x,
                trackedTransform.position.z);

            Refresh(nextCell);
        }

        public void Refresh(WorldStreamingId center)
        {
            if (!center.IsInWorldBounds)
                throw new System.ArgumentOutOfRangeException(nameof(center));
            if (!hasCurrentCell || center != currentCell)
            {
                currentCell = center;
                hasCurrentCell = true;
                desiredLoads = WorldStreamingPolicy.BuildLoadSet(center);
                desiredKeep = WorldStreamingPolicy.BuildKeepSet(center);
            }
            RebuildLoadedIndex();
            EnsureLoaded(center);
            foreach (var cell in desiredLoads)
                EnsureLoaded(cell);
            unloadScratch.Clear();
            foreach (var cell in loaded)
                if (!desiredKeep.Contains(cell))
                    unloadScratch.Add(cell);
            foreach (var cell in unloadScratch)
                EnsureUnloaded(cell);
        }

        private void RebuildLoadedIndex()
        {
            loaded.Clear();
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                Scene scene = SceneManager.GetSceneAt(i);
                if (scene.isLoaded && WorldStreamingSceneNaming.TryParseSceneName(scene.name, out var id))
                    loaded.Add(id);
            }
        }

        private void EnsureLoaded(WorldStreamingId id)
        {
            if (loaded.Contains(id) || pendingLoads.Contains(id) || pendingUnloads.Contains(id))
                return;
            // Bound activation/memory spikes. Refresh retries the remaining desired cells.
            if (pendingLoads.Count >= 2) return;

            string sceneName = WorldStreamingSceneNaming.SceneName(id);
            if (!Application.CanStreamedLevelBeLoaded(sceneName))
                return;

            pendingLoads.Add(id);
            double started = Time.realtimeSinceStartupAsDouble;
            AsyncOperation op;
            try { op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive); }
            catch (System.Exception ex)
            {
                pendingLoads.Remove(id);
                Debug.LogError("WORLD CELL LOAD FAILED: " + sceneName + " / " + ex);
                return;
            }
            if (op == null)
            {
                pendingLoads.Remove(id);
                return;
            }

            op.completed += _ =>
            {
                if (this == null) return;
                pendingLoads.Remove(id);
                LastLoadMilliseconds = (Time.realtimeSinceStartupAsDouble - started) * 1000d;
                MaxLoadMilliseconds = System.Math.Max(MaxLoadMilliseconds, LastLoadMilliseconds);
                TotalLoads++;
                Scene scene = SceneManager.GetSceneByName(sceneName);
                if (scene.IsValid() && scene.isLoaded)
                    loaded.Add(id);
                if (hasCurrentCell && !desiredKeep.Contains(id))
                    EnsureUnloaded(id);
            };
        }

        private void EnsureUnloaded(WorldStreamingId id)
        {
            if (!loaded.Contains(id) || pendingUnloads.Contains(id))
                return;

            string sceneName = WorldStreamingSceneNaming.SceneName(id);
            Scene scene = SceneManager.GetSceneByName(sceneName);
            if (!scene.IsValid() || !scene.isLoaded)
            {
                loaded.Remove(id);
                return;
            }

            pendingUnloads.Add(id);
            double started = Time.realtimeSinceStartupAsDouble;
            AsyncOperation op;
            try { op = SceneManager.UnloadSceneAsync(scene); }
            catch (System.Exception ex)
            {
                pendingUnloads.Remove(id);
                Debug.LogError("WORLD CELL UNLOAD FAILED: " + sceneName + " / " + ex);
                return;
            }
            if (op == null)
            {
                pendingUnloads.Remove(id);
                return;
            }

            op.completed += _ =>
            {
                if (this == null) return;
                pendingUnloads.Remove(id);
                LastUnloadMilliseconds = (Time.realtimeSinceStartupAsDouble - started) * 1000d;
                MaxUnloadMilliseconds = System.Math.Max(MaxUnloadMilliseconds, LastUnloadMilliseconds);
                TotalUnloads++;
                loaded.Remove(id);
                if (hasCurrentCell && desiredLoads.Contains(id))
                    EnsureLoaded(id);
            };
        }
    }
}
