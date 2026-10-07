using System.Collections;
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using Pose = ResortAurora.Game.Pose;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

namespace ResortAurora.Tests
{
    /// <summary>
    /// The optional skinned bodies (free Human Basic Motions pack, local only): near and medium people walk, run, idle and talk with real clips,
    /// everything else stays procedural, and without the pack the game falls back to the procedural body.
    /// </summary>
    public sealed class HumanVisualTests
    {
        string savePath;

        [SetUp] public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_hv_" + System.Guid.NewGuid().ToString("N") + ".json");
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

        [UnityTest]
        public IEnumerator SkinnedPeopleAnimateAndOtherPosesStayProcedural()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            if (!HumanVisual.Available) { Debug.Log("HUMAN pack not present: procedural fallback in use"); Assert.Ignore("Human Basic Motions pack not installed locally"); }
            g.Clock.Restore(1, 11f * 60f);
            var cam = Camera.main; var root = g.Layout.Root.position;
            float pz = g.Site.PromenadeZ(root.x);
            var rng = new System.Random(77);
            var spots = new List<(PersonRig rig, Pose pose, float speed, Gesture gesture)>();
            var kinds = new[] { PersonKind.Casual, PersonKind.Beach, PersonKind.Active, PersonKind.Casual, PersonKind.Beach, PersonKind.Kid, PersonKind.Casual };
            var poses = new[] { Pose.Walk, Pose.Walk, Pose.Run, Pose.Stand, Pose.Stand, Pose.Walk, Pose.SitSand };
            var gestures = new[] { Gesture.None, Gesture.None, Gesture.None, Gesture.Chat, Gesture.None, Gesture.None, Gesture.None };
            var speeds = new[] { 1.3f, 1.1f, 3.4f, 0f, 0f, 1.0f, 0f };
            float x0 = root.x - 5.5f, z = pz - 12f;
            for (int i = 0; i < kinds.Length; i++)
            {
                var rig = PersonRig.Create(rng, kinds[i], "Lineup" + i);
                float x = x0 + i * 1.8f;
                rig.transform.position = new Vector3(x, g.Site.HeightAt(x, z), z);
                rig.transform.rotation = Quaternion.Euler(0f, 180f - (i - 3) * 8f, 0f);          // facing the camera, fanned a little
                rig.Gesture = gestures[i]; rig.SetLod(0);
                spots.Add((rig, poses[i], speeds[i], gestures[i]));
            }
            var camPos = new Vector3(root.x, g.Site.HeightAt(root.x, z - 7f) + 1.55f, z - 7.5f);
            var look = new Vector3(root.x, g.Site.HeightAt(root.x, z) + 1.0f, z);
            cam.transform.SetPositionAndRotation(camPos, Quaternion.LookRotation(look - camPos));

            var footY = new List<float>[spots.Count]; for (int i = 0; i < footY.Length; i++) footY[i] = new List<float>();
            float t0 = Time.time; int f = 0;
            while (Time.time - t0 < 2.5f)
            {
                f++;
                for (int i = 0; i < spots.Count; i++)
                {
                    var s = spots[i]; s.rig.Animate(s.pose, s.speed, Time.deltaTime);
                    var an = s.rig.GetComponentInChildren<Animator>();
                    if (s.rig.HumanShown && an != null && Time.time - t0 > 0.8f) footY[i].Add(an.GetBoneTransform(HumanBodyBones.LeftFoot).position.y);
                }
                yield return null;
            }

            string dir = Path.GetFullPath("../ArtSource/Blender/World/Reviews/F02"); Directory.CreateDirectory(dir);
            var rt = new RenderTexture(1600, 900, 24); cam.targetTexture = rt; cam.Render(); RenderTexture.active = rt;
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(dir, "f02_6_pessoas_animadas.png"), tex.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt); Object.Destroy(tex);

            foreach (var s0 in spots) { var hv = s0.rig.GetComponentInChildren<HumanVisual>(true); if (hv != null) Debug.Log($"HUMAN state {s0.rig.name}: clip {hv.Current} t={hv.ClipTime:0.00} shown={hv.Shown}"); }
            for (int i = 0; i < 6; i++) Assert.IsTrue(spots[i].rig.HumanShown, $"person {i} ({spots[i].pose}) uses the skinned body");
            Assert.IsFalse(spots[6].rig.HumanShown, "sitting on the sand stays procedural");
            Assert.GreaterOrEqual(HumanVisual.ActiveCount, 6);
            float Range(List<float> l) { float lo = float.MaxValue, hi = float.MinValue; foreach (var v in l) { lo = Mathf.Min(lo, v); hi = Mathf.Max(hi, v); } return hi - lo; }
            Debug.Log($"HUMAN foot lift range: walk {Range(footY[0]):0.000} m, walk {Range(footY[1]):0.000} m, run {Range(footY[2]):0.000} m, idle {Range(footY[4]):0.000} m, talk {Range(footY[3]):0.000} m; active {HumanVisual.ActiveCount}");
            Assert.Greater(Range(footY[0]), 0.04f, "the walking foot lifts"); Assert.Greater(Range(footY[2]), 0.08f, "the running foot lifts higher");
            Assert.Less(Range(footY[4]), Range(footY[0]), "an idle person does not step like a walker");

            // standing on the ground, human sized: the lowest renderer point of a person is at the feet, the top is 1.4-2.0 m up
            foreach (var s in spots)
            {
                if (!s.rig.HumanShown || s.pose == Pose.SitSand) continue;
                var b = new Bounds(s.rig.transform.position, Vector3.zero); bool any = false;
                foreach (var r in s.rig.GetComponentsInChildren<SkinnedMeshRenderer>()) { if (!any) { b = r.bounds; any = true; } else b.Encapsulate(r.bounds); }
                float h = b.max.y - s.rig.transform.position.y;
                var foot = s.rig.GetComponentInChildren<HumanVisual>().Animator.GetBoneTransform(HumanBodyBones.LeftFoot);
                float ankle = foot.position.y - s.rig.transform.position.y;
                Debug.Log($"HUMAN {s.rig.name} {s.pose}: height {h:0.00} m, left ankle {ankle:0.00} m above the ground");
                float minH = s.rig.Scale < 0.8f ? 0.9f : 1.4f;
                Assert.That(h, Is.InRange(minH, 2.4f), "plausible height"); Assert.That(ankle, Is.InRange(-0.04f, 0.5f), "feet are on the ground");
            }

            // sitting people are released from the skinned body, and far LOD hides it
            spots[0].rig.SetLod(2); spots[0].rig.Animate(Pose.Walk, 1.3f, 0.02f);
            Assert.IsFalse(spots[0].rig.HumanShown, "far LOD drops the skinned body");
            foreach (var s in spots) Object.Destroy(s.rig.gameObject);
            yield return null;
        }

        [UnityTest]
        public IEnumerator TheBeachCrowdUsesSkinnedBodiesNearTheCameraWithinTheBudget()
        {
            yield return Load();
            var g = Object.FindAnyObjectByType<ResortGame>();
            if (!HumanVisual.Available) Assert.Ignore("Human Basic Motions pack not installed locally");
            g.Clock.Restore(1, 12f * 60f);
            var cam = Camera.main; var root = g.Layout.Root.position; float pz = g.Site.PromenadeZ(root.x);
            cam.transform.position = new Vector3(root.x - 12f, g.Site.HeightAt(root.x - 12f, pz) + 1.7f, pz + 1f);
            yield return new WaitForSeconds(6f);
            Debug.Log($"HUMAN crowd: {HumanVisual.ActiveCount} skinned of {g.Life.ActiveCount} active (lod [{g.Life.LodCounts[0]},{g.Life.LodCounts[1]},{g.Life.LodCounts[2]},{g.Life.LodCounts[3]}])");
            Assert.Greater(HumanVisual.ActiveCount, 0, "people near the camera use skinned bodies");
            Assert.LessOrEqual(HumanVisual.ActiveCount, HumanVisual.MaxActive, "within the skinned-body budget");
        }
    }
}
