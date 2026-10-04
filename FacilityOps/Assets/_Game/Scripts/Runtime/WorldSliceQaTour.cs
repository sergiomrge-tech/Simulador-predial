using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Development-player measurement tour (opt-in: <c>-worldSlice -worldSliceQaTour</c>). It teleports through the four destinations the way the
    /// Editor gate does, waits for the cell to stream in, then records every frame for a few seconds. It is a measurement aid, not gameplay and
    /// not a continuous town walk: the numbers describe a stationary player after each load, plus the load/unload cost of the cell change.
    /// </summary>
    public sealed class WorldSliceQaTour : MonoBehaviour
    {
        [Serializable] private sealed class Sample
        {
            public string location; public int cells, loads, unloads; public int frames; public float seconds, avgFps, p99FrameMs, maxFrameMs;
            public float streamInMaxFrameMs; public int streamInFramesOver33ms; public long batchesAvg, setPassAvg; public double maxLoadMs, maxUnloadMs; public long usedBytes, reservedBytes, gcBytesPerFrameAvg, drawCallsAvg, drawCallsMax, trianglesAvg, trianglesMax;
            public int gcCollections;
        }
        [Serializable] private sealed class Report
        {
            public string unityVersion, device, resolution, scope; public bool development; public Sample[] samples;
        }

        public IEnumerator Run(GameRuntime game, WorldStreamService service, WorldStreamingDebugOverlay overlay)
        {
            var report = new Report
            {
                unityVersion = Application.unityVersion, device = SystemInfo.graphicsDeviceName, development = Debug.isDebugBuild,
                resolution = Screen.width + "x" + Screen.height,
                scope = "Windows x64 Development player; teleport tour with a stationary player after each stream-in. Not a continuous walk or a long soak."
            };
            var samples = new List<Sample>();
            game.Player.enabled = false;
            foreach (string id in new[] { "home.starter", "garage", "horizonte", "grocery", "home.starter" })
            {
                var destination = WorldSliceDestinationRegistry.Require(id);
                service.StreamingEnabled = false;
                service.Refresh(destination.Cell);
                float deadline = Time.realtimeSinceStartup + 60f;
                while (!service.IsLoaded(destination.Cell) && Time.realtimeSinceStartup < deadline) yield return null;
                game.Player.Teleport(destination.FallbackPosition, destination.FallbackYaw);
                service.StreamingEnabled = true;
                float streamInMax = 0f; int over33 = 0;
                float settleStart = Time.realtimeSinceStartup;
                while (Time.realtimeSinceStartup - settleStart < 6f)                // stream neighbours in and let shaders/caches settle; hitches here are the load cost
                {
                    yield return null;
                    float ms = Time.unscaledDeltaTime * 1000f;
                    streamInMax = Math.Max(streamInMax, ms); if (ms > 33.4f) over33++;
                }
                int gcBefore = GC.CollectionCount(0);
                var frameMs = new List<float>(1024);
                double gc = 0, draws = 0, tris = 0, batchSum = 0, setPassSum = 0; long drawsMax = 0, trisMax = 0; int n = 0;
                float start = Time.realtimeSinceStartup;
                while (Time.realtimeSinceStartup - start < 8f)
                {
                    yield return null;
                    frameMs.Add(Time.unscaledDeltaTime * 1000f);
                    gc += Math.Max(0, overlay.GcBytesLastFrame); draws += Math.Max(0, overlay.DrawCallsLastFrame); tris += Math.Max(0, overlay.VisibleTrianglesLastFrame);
                    batchSum += Math.Max(0, overlay.BatchesLastFrame); setPassSum += Math.Max(0, overlay.SetPassCallsLastFrame);
                    drawsMax = Math.Max(drawsMax, overlay.DrawCallsLastFrame); trisMax = Math.Max(trisMax, overlay.VisibleTrianglesLastFrame); n++;
                }
                frameMs.Sort();
                float total = 0f; foreach (float f in frameMs) total += f;
                samples.Add(new Sample
                {
                    location = id, cells = service.LoadedCells.Count, loads = service.TotalLoads, unloads = service.TotalUnloads, frames = n,
                    seconds = Time.realtimeSinceStartup - start, avgFps = n * 1000f / Math.Max(1f, total), maxFrameMs = frameMs[frameMs.Count - 1],
                    p99FrameMs = frameMs[Mathf.Min(frameMs.Count - 1, Mathf.CeilToInt(frameMs.Count * .99f) - 1)],
                    maxLoadMs = service.MaxLoadMilliseconds, maxUnloadMs = service.MaxUnloadMilliseconds, usedBytes = overlay.AllocatedMemoryBytes,
                    reservedBytes = overlay.ReservedMemoryBytes, gcBytesPerFrameAvg = (long)(gc / Math.Max(1, n)), drawCallsAvg = (long)(draws / Math.Max(1, n)),
                    drawCallsMax = drawsMax, batchesAvg = (long)(batchSum / Math.Max(1, n)), setPassAvg = (long)(setPassSum / Math.Max(1, n)), streamInMaxFrameMs = streamInMax, streamInFramesOver33ms = over33, trianglesAvg = (long)(tris / Math.Max(1, n)), trianglesMax = trisMax, gcCollections = GC.CollectionCount(0) - gcBefore
                });
                Debug.Log("WORLD TOUR SAMPLE: " + JsonUtility.ToJson(samples[samples.Count - 1]));
            }
            report.samples = samples.ToArray();
            string path = Path.Combine(Application.persistentDataPath, "world-tour-qa.json");
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
            Debug.Log("WORLD TOUR DONE: " + path);
            Application.Quit();
        }
    }
}
