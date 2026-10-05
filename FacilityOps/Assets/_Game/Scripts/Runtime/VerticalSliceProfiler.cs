using System;
using System.IO;
using System.Text;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.Profiling;

namespace FacilityOps
{
    public sealed class VerticalSliceProfiler : MonoBehaviour
    {
        [Serializable] public sealed class Report
        {
            public string scope, unityVersion, device, utc, warning; public int frames, maxCells, loads, unloads;
            public VerticalSliceMetric fpsAverage, fpsMinimum, frameTimeAverageMs, worstFrameMs, memoryBytes, peakMemoryBytes,
                gcBytesPerFrame, drawCalls, batches, setPassCalls, triangles, maxLoadMs, maxUnloadMs, streamingHitchMs;
        }
        private WorldStreamService service;
        private ProfilerRecorder gc, draw, batch, pass, tri;
        private readonly VerticalSliceCounter gcMean = new VerticalSliceCounter(), drawMean = new VerticalSliceCounter(),
            batchMean = new VerticalSliceCounter(), passMean = new VerticalSliceCounter(), triMean = new VerticalSliceCounter();
        private int frames, maxCells, previousOps; private double seconds, worst, streamWorst; private long peakMemory;
        public float AverageFps => seconds > 0 ? (float)(frames / seconds) : 0;
        public void Configure(WorldStreamService stream) => service = stream;
        private void OnEnable()
        {
            gc = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame", 1);
            draw = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Draw Calls Count", 1);
            batch = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Batches Count", 1);
            pass = ProfilerRecorder.StartNew(ProfilerCategory.Render, "SetPass Calls Count", 1);
            tri = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Triangles Count", 1);
        }
        private void OnDisable() { gc.Dispose(); draw.Dispose(); batch.Dispose(); pass.Dispose(); tri.Dispose(); }
        private void LateUpdate()
        {
            if (service == null) return;
            double dt = Time.unscaledDeltaTime;
            if (dt <= 0 || double.IsNaN(dt) || double.IsInfinity(dt)) return;
            frames++; seconds += dt; worst = Math.Max(worst, dt);
            int ops = service.TotalLoads + service.TotalUnloads;
            if (service.PendingLoadCount > 0 || service.PendingUnloadCount > 0 || ops != previousOps) streamWorst = Math.Max(streamWorst, dt);
            previousOps = ops; maxCells = Math.Max(maxCells, service.LoadedCells.Count);
            peakMemory = Math.Max(peakMemory, Profiler.GetTotalAllocatedMemoryLong());
            gcMean.Observe(gc.Valid && gc.Count > 0, gc.Valid ? gc.LastValue : -1);
            bool renderedPlayer = !Application.isEditor && SystemInfo.graphicsDeviceType != UnityEngine.Rendering.GraphicsDeviceType.Null;
            drawMean.Observe(renderedPlayer && draw.Valid && draw.Count > 0, draw.Valid ? draw.LastValue : -1, true);
            batchMean.Observe(renderedPlayer && batch.Valid && batch.Count > 0, batch.Valid ? batch.LastValue : -1, true);
            passMean.Observe(renderedPlayer && pass.Valid && pass.Count > 0, pass.Valid ? pass.LastValue : -1, true);
            triMean.Observe(renderedPlayer && tri.Valid && tri.Count > 0, tri.Valid ? tri.LastValue : -1, true);
        }
        public Report Snapshot() => new Report
        {
            scope = Application.isEditor ? "EDITOR — not a Player benchmark" : "Unity Development Player — continuous route including streaming and captures",
            unityVersion = Application.unityVersion, device = SystemInfo.graphicsDeviceName, utc = DateTime.UtcNow.ToString("O"),
            frames = frames, maxCells = maxCells, loads = service?.TotalLoads ?? 0, unloads = service?.TotalUnloads ?? 0,
            fpsAverage = frames > 0 ? VerticalSliceMetric.Measured(frames / seconds, "FPS") : VerticalSliceMetric.Unavailable("FPS"),
            fpsMinimum = frames > 0 ? VerticalSliceMetric.Measured(1 / worst, "FPS (slowest single frame)") : VerticalSliceMetric.Unavailable("FPS"),
            frameTimeAverageMs = frames > 0 ? VerticalSliceMetric.Measured(seconds * 1000 / frames, "ms") : VerticalSliceMetric.Unavailable("ms"),
            worstFrameMs = frames > 0 ? VerticalSliceMetric.Measured(worst * 1000, "ms") : VerticalSliceMetric.Unavailable("ms"),
            memoryBytes = VerticalSliceMetric.Measured(Profiler.GetTotalAllocatedMemoryLong(), "bytes"), peakMemoryBytes = frames > 0 ? VerticalSliceMetric.Measured(peakMemory, "bytes") : VerticalSliceMetric.Unavailable("bytes"),
            gcBytesPerFrame = gcMean.Mean("bytes/frame"), drawCalls = drawMean.Mean("calls/frame (positive observations)"), batches = batchMean.Mean("batches/frame (positive observations)"),
            setPassCalls = passMean.Mean("calls/frame (positive observations)"), triangles = triMean.Mean("tris/frame (positive observations)"),
            maxLoadMs = service != null && service.TotalLoads > 0 ? VerticalSliceMetric.Measured(service.MaxLoadMilliseconds, "ms") : VerticalSliceMetric.Unavailable("ms"),
            maxUnloadMs = service != null && service.TotalUnloads > 0 ? VerticalSliceMetric.Measured(service.MaxUnloadMilliseconds, "ms") : VerticalSliceMetric.Unavailable("ms"),
            streamingHitchMs = previousOps > 0 ? VerticalSliceMetric.Measured(streamWorst * 1000, "ms") : VerticalSliceMetric.Unavailable("ms"),
            warning = frames > 0 && frames / seconds < 60 ? "WARNING: average FPS below 60; technical build remains eligible if functional gates pass." : null
        };
        public void Write(string folder)
        {
            Directory.CreateDirectory(folder); var report = Snapshot();
            File.WriteAllText(Path.Combine(folder, "performance.json"), JsonUtility.ToJson(report, true));
            var md = new StringBuilder("# Performance\n\n" + report.scope + "\n\n");
            foreach (var field in typeof(Report).GetFields())
                if (field.GetValue(report) is VerticalSliceMetric metric) md.AppendLine($"- {field.Name}: {(metric.status == "MEDIDO" ? metric.value + " " + metric.unit : metric.status)}");
            md.AppendLine("\n" + report.warning); File.WriteAllText(Path.Combine(folder, "performance.md"), md.ToString());
        }
    }
}
