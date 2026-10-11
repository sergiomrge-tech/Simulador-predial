using System.Collections;
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

namespace ResortAurora.Tests
{
    /// <summary>Frame-time measurements of the resort scene in batch mode (real rendering, no vsync cap). Numbers are logged as PERF lines.</summary>
    public sealed class PerformanceTests
    {
        string savePath;

        [SetUp]
        public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_perf_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown]
        public void TearDown()
        {
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            QualitySettings.vSyncCount = 1;
            Application.targetFrameRate = -1;
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        /// <summary>The batch editor does not repaint on its own, so each sample renders the camera into a 1920x1080 target and reads one pixel back
        /// (forces the GPU to finish): the time is CPU submission + GPU, the real cost of a frame.</summary>
        static IEnumerator Measure(string label, int frames, List<float> sink)
        {
            var cam = Camera.main;
            var rt = new RenderTexture(1920, 1080, 24);
            var px = new Texture2D(1, 1, TextureFormat.RGB24, false);
            cam.targetTexture = rt;
            for (int i = 0; i < 20; i++) { cam.Render(); yield return null; }       // warm-up (shader compile, streaming)
            var times = new List<float>(frames);
            for (int i = 0; i < frames; i++)
            {
                float t0 = Time.realtimeSinceStartup;
                cam.Render();
                RenderTexture.active = rt; px.ReadPixels(new Rect(0, 0, 1, 1), 0, 0); RenderTexture.active = null;
                times.Add((Time.realtimeSinceStartup - t0) * 1000f);
                yield return null;
            }
            cam.targetTexture = null; Object.Destroy(rt);
            times.Sort();
            float avg = 0f; foreach (var t in times) avg += t; avg /= times.Count;
            float p95 = times[(int)(times.Count * 0.95f)];
#if UNITY_EDITOR
            string counts = $", drawCalls {UnityEditor.UnityStats.drawCalls}, setPass {UnityEditor.UnityStats.setPassCalls}, tris {UnityEditor.UnityStats.triangles / 1000}k, shadowCasters {UnityEditor.UnityStats.shadowCasters}";
#else
            string counts = "";
#endif
            Debug.Log($"PERF {label}: avg {avg:0.0} ms ({1000f / avg:0} fps), p95 {p95:0.0} ms, worst {times[times.Count - 1]:0.0} ms{counts}");
            sink.Add(avg);
        }

        [UnityTest]
        public IEnumerator FrameTimeAtStage1AndStage7()
        {
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = -1;
            var results = new List<float>();
            foreach (var stage in new[] { 1, 7 })
            {
                System.Environment.SetEnvironmentVariable("RESORT_STAGE", stage.ToString());
#if UNITY_EDITOR
                yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
                yield return null; yield return null;
                var g = Object.FindAnyObjectByType<ResortGame>();
                var cam = Camera.main;
                var rig = cam.transform.parent;
                g.Clock.Restore(1, 12f * 60f);
                g.OpenPanel(Panel.Help);                                        // freeze input; the scene keeps rendering

                float dx = ResortAurora.Site.ResortStages.LegacyKitOffsetX(g.Site.Data); // kit coordinates -> migrated site

                // aerial over the whole bairro
                rig.gameObject.SetActive(true);
                cam.transform.SetPositionAndRotation(new Vector3(215f + dx, 100f, -20f), Quaternion.LookRotation(new Vector3(520f + dx, 8f, 410f) - new Vector3(215f + dx, 100f, -20f)));
                yield return Measure($"stage{stage} aerea", 120, results);

                // ground level, in front of the Grande Hotel
                float gy = g.Site.HeightAt(550f + dx, 300f);
                cam.transform.SetPositionAndRotation(new Vector3(550f + dx, gy + 1.7f, 300f), Quaternion.LookRotation(new Vector3(550f + dx, gy + 8f, 360f) - new Vector3(550f + dx, gy + 1.7f, 300f)));
                yield return Measure($"stage{stage} nivel do chao", 120, results);

                if (stage == 7)
                {
                    float py = g.Site.HeightAt(450f + dx, 484f);
                    cam.transform.SetPositionAndRotation(new Vector3(450f + dx, py + 1.8f, 484f), Quaternion.LookRotation(new Vector3(450f + dx, py + 14f, 640f) - new Vector3(450f + dx, py + 1.8f, 484f)));
                    yield return Measure("stage7 eixo central", 120, results);
                }
            }
            foreach (var r in results) Assert.Less(r, 100f, "average frame time under 100 ms (10 fps) even in a headless batch run");
        }

        /// <summary>Opt-in (RESORT_PERF_DIAG=1): leave-one-out frame cost per direct child of the site root, at the beach (noon) and at stage 7 ground level.</summary>
        [UnityTest]
        public IEnumerator DiagnosticLeaveOneOutBreakdown()
        {
            if (System.Environment.GetEnvironmentVariable("RESORT_PERF_DIAG") != "1") { Assert.Ignore("set RESORT_PERF_DIAG=1"); yield break; }
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = -1;
            foreach (var stage in new[] { 1, 7 })
            {
                System.Environment.SetEnvironmentVariable("RESORT_STAGE", stage.ToString());
#if UNITY_EDITOR
                yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
                yield return null; yield return null;
                var g = Object.FindAnyObjectByType<ResortGame>();
                var cam = Camera.main;
                g.Clock.Restore(1, 12f * 60f);
                g.OpenPanel(Panel.Help);
                float dx = ResortAurora.Site.ResortStages.LegacyKitOffsetX(g.Site.Data);
                float gy = g.Site.HeightAt(550f + dx, 300f);
                cam.transform.SetPositionAndRotation(new Vector3(550f + dx, gy + 1.7f, 300f), Quaternion.LookRotation(new Vector3(550f + dx, gy + 8f, 360f) - new Vector3(550f + dx, gy + 1.7f, 300f)));
                int renderers = 0, active = 0;
                foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsInactive.Include, FindObjectsSortMode.None)) { renderers++; if (r.gameObject.activeInHierarchy && r.enabled) active++; }
                Debug.Log($"PERFDIAG stage{stage} renderers total {renderers}, enabled {active}");
                string shotDir = System.Environment.GetEnvironmentVariable("RESORT_PERF_SHOTS");
                if (!string.IsNullOrEmpty(shotDir))
                {
                    Directory.CreateDirectory(shotDir);
                    foreach (var prefix in new[] { "Tree_island_tree_02_", "Tree_tree_small_02_" })
                    {
                        Transform tree = null;
                        foreach (var lg in Object.FindObjectsByType<LODGroup>(FindObjectsSortMode.None))
                            if (lg.name.StartsWith(prefix) && lg.gameObject.activeInHierarchy) { tree = lg.transform; break; }
                        if (tree == null) continue;
                        foreach (var dist in new[] { 7f, 20f, 45f })
                        {
                            var look = tree.position + Vector3.up * 2f;
                            var pos = look + new Vector3(dist, dist * .12f, 0f);
                            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
                            var rt = new RenderTexture(1280, 720, 24); cam.targetTexture = rt; cam.Render();
                            RenderTexture.active = rt;
                            var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); tex.Apply();
                            File.WriteAllBytes(Path.Combine(shotDir, $"stage{stage}_{prefix}{dist:0}m.png"), tex.EncodeToPNG());
                            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt); Object.Destroy(tex);
                            yield return null;
                        }
                    }
                }
                var baseline = new List<float>();
                yield return Measure($"PERFDIAG stage{stage} baseline", 60, baseline);
                var roots = new List<Transform>();
                foreach (Transform t in g.Site.transform)
                {
                    if (t.name == "RealisticCoastalVegetation") foreach (Transform c in t) roots.Add(c);   // one level deeper: trees / ground cover / parcel groves
                    else roots.Add(t);
                }
                foreach (var folder in new[] { "island_tree_02/island_tree_02_LOD", "tree_small_02/tree_small_02_LOD" })
                    for (int lod = 0; lod < 3; lod++)
                    {
                        var prefab = Resources.Load<GameObject>("Art/Resort/Vegetation/" + folder + lod);
                        if (prefab == null) continue;
                        long tris = 0; int mats = 0;
                        foreach (var mf in prefab.GetComponentsInChildren<MeshFilter>(true)) { for (int sm = 0; sm < mf.sharedMesh.subMeshCount; sm++) tris += mf.sharedMesh.GetIndexCount(sm) / 3; }
                        foreach (var mr in prefab.GetComponentsInChildren<MeshRenderer>(true)) mats += mr.sharedMaterials.Length;
                        var bb = new Bounds(); bool first = true; foreach (var mf in prefab.GetComponentsInChildren<MeshFilter>(true)) { var wb = mf.sharedMesh.bounds; if (first) { bb = wb; first = false; } else bb.Encapsulate(wb); }
                        Debug.Log($"PERFDIAG mesh {folder}{lod}: {tris} triangles, {mats} material slots, bounds size {bb.size} center {bb.center}");
                    }
                foreach (var t in roots)
                {
                    if (!t.gameObject.activeSelf) continue;
                    int n = t.GetComponentsInChildren<Renderer>(false).Length;
                    t.gameObject.SetActive(false);
                    var sink = new List<float>();
                    yield return Measure($"PERFDIAG stage{stage} without '{t.name}' ({n} renderers)", 40, sink);
                    t.gameObject.SetActive(true);
                }
                var urp = UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline as UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset;
                if (urp != null)
                {
                    float d = urp.shadowDistance; urp.shadowDistance = 0f;
                    var sink = new List<float>();
                    yield return Measure($"PERFDIAG stage{stage} shadows off", 40, sink);
                    urp.shadowDistance = d;
                }
            }
        }
    }
}
