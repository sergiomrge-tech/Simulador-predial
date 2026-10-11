using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using Object = UnityEngine.Object;

namespace ResortAurora.Tests
{
    public sealed class RealisticHumanPassTests
    {
        string save;
        string Folder => Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT");

        [SetUp] public void Setup()
        {
            save = Path.Combine(Path.GetTempPath(), "human_pass_" + Guid.NewGuid().ToString("N") + ".json");
            Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", save);
            Environment.SetEnvironmentVariable("RESORT_STAGE", "1");
            Time.timeScale = 1f;
        }
        [TearDown] public void Cleanup()
        {
            Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            Time.timeScale = 1f;
            if (File.Exists(save)) File.Delete(save);
        }
        static IEnumerator Load()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
            yield return null; yield return null;
            Object.FindAnyObjectByType<ResortGame>().Clock.Restore(1, 720f);
            Object.FindAnyObjectByType<PlayerController>().Frozen = true;
        }
        IEnumerator GameShot(string name)
        {
            if (string.IsNullOrEmpty(Folder)) yield break;
            Directory.CreateDirectory(Folder);
            // ScreenCapture captures the actual Unity Game view at end of frame,
            // including the HUD; no external renderer or synthetic composition.
            ScreenCapture.CaptureScreenshot(Path.Combine(Folder, name + "_game.png"));
            yield return new WaitForSeconds(.15f);
            Assert.IsTrue(File.Exists(Path.Combine(Folder, name + "_game.png")));
        }

        [UnityTest] public IEnumerator ThreeScansRetargetEveryUprightClipAndKeepGroundContact()
        {
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>();
            var cam = Camera.main;
            var origin = game.Layout.Ground(game.Layout.Root.position + new Vector3(4f, 0f, 5f));
            var report = new List<string> { "variant,clip,minSoleY,maxSoleY,leftFootLift,vertexMotion" };
            var failures = new List<string>();
            string[] names = { "Eric", "Carla", "Claudia" };
            for (int v = 0; v < 3; v++)
            {
                var parent = new GameObject("HumanPass_" + names[v]);
                parent.transform.position = origin;
                // Also verify that parent height variation survives normalization.
                parent.transform.localScale = Vector3.one * (v == 1 ? .94f : 1f);
                var hv = HumanVisual.Create(parent.transform, new HumanVisual.Look { female = v > 0, realisticEligible = true, variantSeed = v == 1 ? 1 : 0 }, new System.Random(71 + v));
                Assert.NotNull(hv);
                Assert.AreEqual(names[v], hv.RealisticVariant);
                Assert.IsTrue(hv.Animator.avatar.isHuman && hv.Animator.avatar.isValid);
                Assert.IsFalse(hv.Animator.applyRootMotion);
                var renderer = hv.GetComponentInChildren<SkinnedMeshRenderer>(true);
                var source = Resources.Load<GameObject>("RealisticHumans/" + names[v]).GetComponentInChildren<SkinnedMeshRenderer>();
                Assert.AreSame(source.sharedMesh, renderer.sharedMesh, "original UVs, normals, skin weights and shared mesh retained");
                Assert.AreEqual(1, renderer.sharedMaterials.Length);
                Assert.AreEqual("Universal Render Pipeline/Lit", renderer.sharedMaterial.shader.name);
                Assert.IsTrue(renderer.sharedMaterial.shader.isSupported);
                foreach (var map in new[] { "_BaseMap", "_BumpMap", "_MetallicGlossMap" }) Assert.NotNull(renderer.sharedMaterial.GetTexture(map));
                Assert.That(hv.transform.localScale.x * source.bounds.size.y, Is.InRange(1.70f, 1.78f));
                hv.Show(true);
                var mesh = new Mesh();
                foreach (HumanVisual.Clip clip in Enum.GetValues(typeof(HumanVisual.Clip)))
                {
                    float speed = clip == HumanVisual.Clip.Run ? 3.9f : clip == HumanVisual.Clip.Walk ? 1.45f : 0f;
                    hv.Drive(clip, speed, 1f, .3f + v * .2f);
                    yield return new WaitForSeconds(.45f);
                    renderer.BakeMesh(mesh);
                    var before = mesh.vertices;
                    float footLo = float.MaxValue, footHi = float.MinValue, soleLo = float.MaxValue, soleHi = float.MinValue, motion = 0f;
                    float start = Time.time;
                    while (Time.time - start < 1.3f)
                    {
                        hv.Drive(clip, speed, Time.deltaTime, .3f + v * .2f);
                        renderer.BakeMesh(mesh);
                        var after = mesh.vertices;
                        float lowest = float.MaxValue;
                        for (int i = 0; i < after.Length; i++)
                        {
                            lowest = Mathf.Min(lowest, renderer.transform.TransformPoint(after[i]).y - origin.y);
                            motion = Mathf.Max(motion, Vector3.Distance(before[i], after[i]));
                        }
                        soleLo = Mathf.Min(soleLo, lowest); soleHi = Mathf.Max(soleHi, lowest);
                        float ankle = hv.Animator.GetBoneTransform(HumanBodyBones.LeftFoot).position.y;
                        footLo = Mathf.Min(footLo, ankle); footHi = Mathf.Max(footHi, ankle);
                        yield return null;
                    }
                    string row = FormattableString.Invariant($"{names[v]},{clip},{soleLo:F4},{soleHi:F4},{footHi-footLo:F4},{motion:F4}");
                    report.Add(row); Debug.Log("REALISTIC_HUMAN " + row);
                    if (soleLo < -.08f || soleLo > .08f) failures.Add(row + " contact outside 8cm");
                    if (clip == HumanVisual.Clip.Walk && footHi-footLo < .04f) failures.Add(row + " walk foot not lifting");
                    if (clip == HumanVisual.Clip.Run && footHi-footLo < .08f) failures.Add(row + " run foot not lifting");
                    if (motion < .001f) failures.Add(row + " static skinned mesh");
                    var shoulder = hv.Animator.GetBoneTransform(HumanBodyBones.LeftUpperArm);
                    var hand = hv.Animator.GetBoneTransform(HumanBodyBones.LeftHand);
                    if (clip == HumanVisual.Clip.Idle1 && shoulder.position.y - hand.position.y < .20f) failures.Add(row + " possible T pose");
                    cam.transform.SetPositionAndRotation(origin + new Vector3(0f, 1.25f, 3.4f), Quaternion.LookRotation(origin + Vector3.up - (origin + new Vector3(0f, 1.25f, 3.4f))));
                    yield return GameShot(names[v] + "_" + clip);
                }
                hv.Show(false); Object.Destroy(parent); Object.Destroy(mesh); yield return null;
            }
            if (!string.IsNullOrEmpty(Folder)) File.WriteAllLines(Path.Combine(Folder, "retarget-ground-metrics.csv"), report);
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [UnityTest] public IEnumerator ExistingBeachLifeSelectsThreeScansAndKeepsItsBudget()
        {
            yield return Load();
            var game = Object.FindAnyObjectByType<ResortGame>();
            var cam = Camera.main;
            var root = game.Layout.Root.position;
            float x = root.x - 12f, z = game.Site.PromenadeZ(x);
            var pos = new Vector3(x, game.Site.HeightAt(x, z) + 1.7f, z + 1f);
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(new Vector3(x + 18f, pos.y - .5f, z + 1f) - pos));
            yield return new WaitForSeconds(6f);
            var shown = Object.FindObjectsByType<HumanVisual>(FindObjectsSortMode.None).Where(h => h.Shown && h.IsRealistic).ToArray();
            var variants = shown.Select(h => h.RealisticVariant).Distinct().OrderBy(s => s).ToArray();
            string text = $"natural BeachLife: population={game.Life.ActiveCount}; skinned={HumanVisual.ActiveCount}/{HumanVisual.MaxActive}; realistic={shown.Length}; variants={string.Join(",", variants)}; lod={string.Join(",",game.Life.LodCounts)}; drawCalls={UnityEditor.UnityStats.drawCalls}; triangles={UnityEditor.UnityStats.triangles}";
            Debug.Log("REALISTIC_HUMAN_CROWD " + text);
            if (!string.IsNullOrEmpty(Folder)) File.WriteAllText(Path.Combine(Folder, "natural-crowd-metrics.txt"), text);
            yield return GameShot("natural_beachlife_promenade");
            Assert.That(variants, Is.EquivalentTo(new[] { "Eric", "Carla", "Claudia" }));
            Assert.LessOrEqual(HumanVisual.ActiveCount, HumanVisual.MaxActive);
            foreach (var group in shown.GroupBy(h => h.RealisticVariant))
            {
                var materials = group.Select(h => h.GetComponentInChildren<SkinnedMeshRenderer>().sharedMaterial).Distinct().ToArray();
                Assert.AreEqual(1, materials.Length, "one shared atlas material per scan");
            }
        }
    }
}
