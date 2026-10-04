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
        public bool IsLoaded(WorldStreamingId id) => loaded.Contains(id);
        public int PendingLoadCount => pendingLoads.Count;
        public int PendingUnloadCount => pendingUnloads.Count;

        private void Update()
        {
            if (!streamingEnabled || trackedTransform == null || Time.unscaledTime < nextRefresh)
                return;

            nextRefresh = Time.unscaledTime + Mathf.Max(0.05f, refreshIntervalSeconds);
            var nextCell = WorldStreamingId.FromWorldPosition(
                trackedTransform.position.x,
                trackedTransform.position.z);

            if (hasCurrentCell && nextCell == currentCell)
                return;

            currentCell = nextCell;
            hasCurrentCell = true;
            Refresh(nextCell);
        }

        public void Refresh(WorldStreamingId center)
        {
            RebuildLoadedIndex();

            var loadSet = WorldStreamingPolicy.BuildLoadSet(center);
            var keepSet = WorldStreamingPolicy.BuildKeepSet(center);

            foreach (var cell in loadSet)
                EnsureLoaded(cell);

            var unload = new List<WorldStreamingId>();
            foreach (var cell in loaded)
                if (!keepSet.Contains(cell))
                    unload.Add(cell);

            foreach (var cell in unload)
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
            if (loaded.Contains(id) || pendingLoads.Contains(id))
                return;

            string sceneName = WorldStreamingSceneNaming.SceneName(id);
            if (!Application.CanStreamedLevelBeLoaded(sceneName))
                return;

            pendingLoads.Add(id);
            AsyncOperation op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
            if (op == null)
            {
                pendingLoads.Remove(id);
                return;
            }

            op.completed += _ =>
            {
                pendingLoads.Remove(id);
                Scene scene = SceneManager.GetSceneByName(sceneName);
                if (scene.IsValid() && scene.isLoaded)
                    loaded.Add(id);
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
            AsyncOperation op = SceneManager.UnloadSceneAsync(scene);
            if (op == null)
            {
                pendingUnloads.Remove(id);
                return;
            }

            op.completed += _ =>
            {
                pendingUnloads.Remove(id);
                loaded.Remove(id);
            };
        }
    }
}
