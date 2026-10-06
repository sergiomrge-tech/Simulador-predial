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
            Debug.Log($"PERF {label}: avg {avg:0.0} ms ({1000f / avg:0} fps), p95 {p95:0.0} ms, worst {times[times.Count - 1]:0.0} ms");
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

                // aerial over the whole bairro
                rig.gameObject.SetActive(true);
                cam.transform.SetPositionAndRotation(new Vector3(215f, 100f, -20f), Quaternion.LookRotation(new Vector3(520f, 8f, 410f) - new Vector3(215f, 100f, -20f)));
                yield return Measure($"stage{stage} aerea", 120, results);

                // ground level, in front of the Grande Hotel
                float gy = g.Site.HeightAt(550f, 300f);
                cam.transform.SetPositionAndRotation(new Vector3(550f, gy + 1.7f, 300f), Quaternion.LookRotation(new Vector3(550f, gy + 8f, 360f) - new Vector3(550f, gy + 1.7f, 300f)));
                yield return Measure($"stage{stage} nivel do chao", 120, results);

                if (stage == 7)
                {
                    float py = g.Site.HeightAt(450f, 484f);
                    cam.transform.SetPositionAndRotation(new Vector3(450f, py + 1.8f, 484f), Quaternion.LookRotation(new Vector3(450f, py + 14f, 640f) - new Vector3(450f, py + 1.8f, 484f)));
                    yield return Measure("stage7 eixo central", 120, results);
                }
            }
            foreach (var r in results) Assert.Less(r, 100f, "average frame time under 100 ms (10 fps) even in a headless batch run");
        }
    }
}
