using System.Text;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.Profiling;
using UnityEngine.SceneManagement;
using UnityEngine.AI;

namespace FacilityOps
{
    // Development-only diagnostics rendered by the real player camera.
    public sealed class WorldStreamingDebugOverlay : MonoBehaviour
    {
        [SerializeField] private WorldStreamService streamService;
        [SerializeField] private bool visible = true;
        private Canvas canvas;
        private UnityEngine.UI.Text label;
        private readonly StringBuilder buffer = new StringBuilder(640);
        private ProfilerRecorder gc, draws, triangles, batches, setPass;
        private float sampleTime, nextText;
        private int frames;
        public float FramesPerSecond { get; private set; }
        public float MaximumFrameMilliseconds { get; private set; }
        public long AllocatedMemoryBytes => Profiler.GetTotalAllocatedMemoryLong();
        public long ReservedMemoryBytes => Profiler.GetTotalReservedMemoryLong();
        public long GcBytesLastFrame => gc.Valid && gc.Count > 0 ? gc.LastValue : -1;
        private static long RenderValue(ProfilerRecorder recorder) => recorder.Valid && recorder.Count > 0 && recorder.LastValue > 0 ? recorder.LastValue : -1;
        public long DrawCallsLastFrame => RenderValue(draws);
        public long BatchesLastFrame => RenderValue(batches);
        public long SetPassCallsLastFrame => RenderValue(setPass);
        public long VisibleTrianglesLastFrame => RenderValue(triangles);
        public WorldStreamService StreamService { get => streamService; set => streamService = value; }
        private void OnEnable()
        {
            if (!VerticalSliceQaFlags.Overlay) return;
            gc = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame", 1);
            draws = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Draw Calls Count", 1);
            triangles = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Triangles Count", 1);
            batches = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Batches Count", 1);
            setPass = ProfilerRecorder.StartNew(ProfilerCategory.Render, "SetPass Calls Count", 1);
        }
        private void OnDisable()
        {
            gc.Dispose(); draws.Dispose(); triangles.Dispose(); batches.Dispose(); setPass.Dispose();
            if (canvas != null) canvas.enabled = false;
        }
        private void OnDestroy() { if (canvas != null) Destroy(canvas.gameObject); }
        private void Update()
        {
            if (!visible || streamService == null || !streamService.StreamingEnabled ||
                !VerticalSliceQaFlags.Overlay)
            { if (canvas != null) canvas.enabled = false; return; }
            if (Camera.main == null) return;
            if (canvas == null) CreateCanvas(Camera.main);
            canvas.worldCamera = Camera.main; canvas.enabled = true;
            float dt = Time.unscaledDeltaTime;
            MaximumFrameMilliseconds = Mathf.Max(MaximumFrameMilliseconds, dt * 1000f);
            sampleTime += dt; frames++;
            if (sampleTime >= 1f) { FramesPerSecond = frames / sampleTime; frames = 0; sampleTime = 0f; }
            if (Time.unscaledTime < nextText) return;
            nextText = Time.unscaledTime + .5f;
            buffer.Clear();
            buffer.AppendLine("SANTA AURORA / STREAMING QA");
            buffer.Append("Cell: ").AppendLine(streamService.HasCurrentCell ? streamService.CurrentCell.Name : "n/a");
            buffer.Append("Loaded: ").Append(streamService.LoadedCells.Count).Append(" / scenes: ").Append(SceneManager.sceneCount).AppendLine();
            buffer.Append("Pending load/unload: ").Append(streamService.PendingLoadCount).Append('/').Append(streamService.PendingUnloadCount).AppendLine();
            buffer.Append("FPS: ").Append(FramesPerSecond.ToString("F1")).Append(" / frame ms: ").Append((dt * 1000f).ToString("F1")).AppendLine();
            buffer.Append("Max frame ms: ").Append(MaximumFrameMilliseconds.ToString("F1")).AppendLine();
            buffer.Append("Load/unload ms: ").Append(streamService.LastLoadMilliseconds.ToString("F1")).Append('/').Append(streamService.LastUnloadMilliseconds.ToString("F1")).AppendLine();
            buffer.Append("Memory used/reserved MiB: ").Append((AllocatedMemoryBytes / 1048576d).ToString("F1")).Append('/').Append((ReservedMemoryBytes / 1048576d).ToString("F1")).AppendLine();
            buffer.Append("GC bytes/frame: ").Append(Metric(GcBytesLastFrame)).AppendLine();
            buffer.Append("Draw/batch/pass/tris: ").Append(Metric(DrawCallsLastFrame)).Append('/').Append(Metric(BatchesLastFrame)).Append('/').Append(Metric(SetPassCallsLastFrame)).Append('/').Append(Metric(VisibleTrianglesLastFrame)).AppendLine();
            if (streamService.TrackedTransform != null)
            {
                Vector3 position = streamService.TrackedTransform.position;
                buffer.Append("Player: ").Append(position.ToString("F2")).AppendLine();
                buffer.Append("NavMesh: ").Append(NavMesh.SamplePosition(position, out _, 1f, NavMesh.AllAreas) ? "ON SURFACE" : "NO SURFACE / NOT LOADED");
            }
            label.text = buffer.ToString();
        }
        private void CreateCanvas(Camera camera)
        {
            var go = new GameObject("Streaming QA Canvas", typeof(RectTransform), typeof(Canvas), typeof(UnityEngine.UI.CanvasScaler));
            canvas = go.GetComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = camera; canvas.planeDistance = .5f; canvas.sortingOrder = 100;
            var scaler = go.GetComponent<UnityEngine.UI.CanvasScaler>();
            scaler.uiScaleMode = UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720); scaler.matchWidthOrHeight = .5f;
            var panel = new GameObject("Streaming Diagnostics", typeof(RectTransform), typeof(UnityEngine.UI.Image));
            panel.transform.SetParent(go.transform, false);
            var rect = panel.GetComponent<RectTransform>();
            rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = new Vector2(12, -12); rect.sizeDelta = new Vector2(550, 285);
            var background = panel.GetComponent<UnityEngine.UI.Image>();
            background.color = new Color(.02f, .03f, .05f, .9f); background.raycastTarget = false;
            var text = new GameObject("Live Metrics", typeof(RectTransform), typeof(UnityEngine.UI.Text));
            text.transform.SetParent(panel.transform, false);
            var tr = text.GetComponent<RectTransform>(); tr.anchorMin = Vector2.zero; tr.anchorMax = Vector2.one;
            tr.offsetMin = new Vector2(10, 8); tr.offsetMax = new Vector2(-10, -8);
            label = text.GetComponent<UnityEngine.UI.Text>(); label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = 15; label.color = Color.white; label.raycastTarget = false; label.alignment = TextAnchor.UpperLeft;
        }
        private static string Metric(long value) => value < 0 ? "INDISPONÍVEL" : value.ToString();
    }
}
