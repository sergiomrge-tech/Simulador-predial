using System.Collections;
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
    /// <summary>Phase 02 ambient coast: the beach is a believable distance from the kiosk, surf rolls in, gulls fly by day, palms sway, and the soundscape follows the hour.</summary>
    public sealed class AmbientLifeTests
    {
        string savePath;

        [SetUp] public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_amb_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
        }

        [TearDown] public void TearDown()
        {
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        static IEnumerator Load()
        {
#if UNITY_EDITOR
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null; yield return null;
        }

        static void Peak(AudioClip c, out float peak, out float rms)
        {
            var d = new float[c.samples]; c.GetData(d, 0);
            peak = 0f; double sum = 0;
            foreach (var v in d) { peak = Mathf.Max(peak, Mathf.Abs(v)); sum += v * v; }
            rms = (float)System.Math.Sqrt(sum / d.Length);
        }

        [UnityTest]
        public IEnumerator TheCoastMovesAndSoundsAndTheSeaIsCloseToTheKiosk()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            Assert.NotNull(g.Ambient, "ambient life exists");
            var root = g.Layout.Root.position;
            float water = g.Site.WaterlineZ(root.x), dist = root.z - water;
            Debug.Log($"COAST kiosk z {root.z:0.0}, waterline z {water:0.0}, kiosk-to-sea {dist:0.0} m, promenade-to-sea {g.Site.PromenadeZ(root.x) - water:0.0} m");
            Assert.Greater(dist, 30f, "room for a beach"); Assert.Less(dist, 75f, "the sea is in the same scene as the kiosk (REF 01)");

            g.Clock.Restore(1, 12f * 60f);
            yield return new WaitForSeconds(3f);
            var a = g.Ambient;
            Assert.AreEqual(5, a.Waves);
            Assert.Greater(a.WaveAlphaMax, 0.3f, "foam lines are visible");
            Assert.GreaterOrEqual(a.GullsFlying, 6, "gulls fly by day");
            Debug.Log($"AMBIENT palm crowns {a.PalmCrowns}, gulls {a.GullsFlying}, wind {a.Wind:0.00}");
            Assert.GreaterOrEqual(a.PalmCrowns, 8, "the welded palm foliage was split into crowns");
            yield return new WaitForSeconds(1.5f);
            Assert.Greater(a.MaxSwayAngle(), 0.2f, "palms sway in the breeze");

            Assert.IsTrue(a.Audio.SurfPlaying, "surf plays");
            Assert.Greater(a.Audio.SurfVolume, 0.3f);
            Assert.Greater(a.Audio.MurmurVolume, 0.02f, "the promenade has a murmur at noon");
            Assert.Less(a.Audio.InsectVolume, 0.02f, "no insects at noon");
            foreach (var clip in new[] { a.Audio.SurfClip, a.Audio.MurmurClip })
            {
                Peak(clip, out float peak, out float rms);
                Debug.Log($"AUDIO {clip.name}: {clip.length:0.0} s, peak {peak:0.00}, rms {rms:0.000}");
                Assert.LessOrEqual(peak, 1.0f, clip.name + " does not clip"); Assert.Greater(rms, 0.01f, clip.name + " is audible");
            }

            string dir = Path.GetFullPath(Path.Combine(System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT") ?? "../ArtSource/Blender/World/Reviews", "F02")); Directory.CreateDirectory(dir);
            var cam = Camera.main; var pos = root + new Vector3(4f, 2.1f, -6f); var look = root + new Vector3(-10f, 8f, -80f);
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
            yield return new WaitForSeconds(0.5f);
            var rt = new RenderTexture(1600, 900, 24); cam.targetTexture = rt; cam.Render(); RenderTexture.active = rt;
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(dir, "f02_5_ondas_e_gaivotas.png"), tex.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt); Object.Destroy(tex);

            g.Clock.Restore(1, 21f * 60f);
            yield return new WaitForSeconds(3.5f);
            Assert.AreEqual(0, a.GullsFlying, "gulls roost at night");
            Assert.Greater(a.Audio.InsectVolume, 0.03f, "insects sing at night");
            Assert.Greater(a.Wind, 0f);
        }
    }
}
