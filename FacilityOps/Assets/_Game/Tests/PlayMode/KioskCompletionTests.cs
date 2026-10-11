using System.Collections;
using System.IO;
using System.Linq;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEditor.SceneManagement;

namespace ResortAurora.Tests
{
    public sealed class KioskCompletionTests
    {
        string save;
        [SetUp] public void Setup()
        {
            save = Path.Combine(Path.GetTempPath(), "kiosk_completion_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", save);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", "2");
        }
        [TearDown] public void Cleanup()
        {
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            Time.timeScale = 1f;
            if (File.Exists(save)) File.Delete(save);
        }
        static void Snap(Camera cam, string name)
        {
            string dir = System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT");
            if (string.IsNullOrEmpty(dir)) return;
            dir = Path.Combine(dir, "KioskCompletion"); Directory.CreateDirectory(dir);
            var old = cam.targetTexture; var active = RenderTexture.active;
            var rt = new RenderTexture(1600, 900, 24); var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            try
            {
                cam.targetTexture = rt; cam.Render(); RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
                File.WriteAllBytes(Path.Combine(dir, name + ".png"), tex.EncodeToPNG());
            }
            finally { cam.targetTexture = old; RenderTexture.active = active; Object.Destroy(rt); Object.Destroy(tex); }
        }
        [UnityTest] public IEnumerator KioskHasPBRArchitectureClearAislesAndReversibleProgression()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
            yield return null; yield return null;
            var game = Object.FindAnyObjectByType<ResortGame>(); var root = game.Layout.Root;
            game.OpenPanel(Panel.Help);
            var shell = game.Stages.Instances.Single(g => g.name == "E2-7_quiosque");
            Assert.IsTrue(shell.activeSelf);
            var structure = shell.GetComponentsInChildren<MeshRenderer>().First(r => r.sharedMaterials.Any(m => m.name.StartsWith("Kiosk_")));
            foreach (var m in structure.sharedMaterials)
            {
                Assert.AreEqual("Universal Render Pipeline/Lit", m.shader.name);
                Assert.NotNull(m.GetTexture("_BaseMap"), m.name + " albedo missing");
                Assert.NotNull(m.GetTexture("_BumpMap"), m.name + " normal missing");
            }
            var architectureLOD = shell.GetComponent<LODGroup>(); Assert.NotNull(architectureLOD);
            var levels = architectureLOD.GetLODs(); Assert.AreEqual(2, levels.Length);
            var fullMesh = levels[0].renderers[0].GetComponent<MeshFilter>().sharedMesh;
            var lowMesh = levels[1].renderers[0].GetComponent<MeshFilter>().sharedMesh;
            long TriangleCount(Mesh m) { long n=0;for(int i=0;i<m.subMeshCount;i++)n+=(long)m.GetIndexCount(i)/3;return n; }
            Assert.Less(TriangleCount(lowMesh), TriangleCount(fullMesh)*.45f);
            Assert.Less(Vector3.Distance(levels[0].renderers[0].bounds.center, levels[1].renderers[0].bounds.center), .03f);
            Assert.IsNull(levels[1].renderers[0].GetComponent<MeshCollider>(), "distant visual does not duplicate physics");
            Assert.That(structure.bounds.size.x, Is.InRange(18.9f, 19.1f));
            Assert.That(structure.bounds.size.y, Is.InRange(3.7f, 3.85f));
            Assert.AreEqual(24, shell.transform.Cast<Transform>().Count(t => t.name == "Kiosk_ShelfBottle"));
            Assert.AreEqual(6, shell.GetComponentsInChildren<Transform>().Count(t => t.name == "Kiosk_NightEmitter"));
            Assert.IsFalse(root.Find("BackWall").GetComponent<Collider>().enabled, "old rear wall blocks the enlarged kitchen");
            Assert.IsFalse(root.Find("S1_Table/S1_TableTop").GetComponent<Collider>().enabled, "invisible old table collision");
            foreach (var station in root.GetComponentsInChildren<Interactable>(true))
                Assert.IsTrue(station.GetComponent<Collider>().enabled, station.name + " must remain interactable");
            Physics.SyncTransforms();
            var shots = new[] {
                ("Counter", new Vector3(0,1.65f,3), new Vector3(0,.9f,1.625f)),
                ("Grill", new Vector3(-1.5f,1.65f,.25f), new Vector3(-1.5f,.8f,-.63f)),
                ("Cooler", new Vector3(1.4f,1.65f,.35f), new Vector3(1.4f,.65f,-.86f)),
                ("S1_Fridge", new Vector3(.35f,1.65f,-.35f), new Vector3(.35f,1.1f,-1.1f)),
                ("OpenSign", new Vector3(-5.7f,1.65f,1.85f), new Vector3(-4.45f,1.25f,1.85f)),
                ("HelpBoard", new Vector3(-5.7f,1.8f,1.85f), new Vector3(-4.45f,1.95f,1.85f)),
                ("S1_SnackRack", new Vector3(3.6f,1.65f,-1.8f), new Vector3(3.6f,.5f,-3.1f)),
                ("SupplierCrate", new Vector3(2f,1.65f,.65f), new Vector3(2f,.45f,-.1f)) };
            foreach(var shot in shots)
            {
                var from=root.position+shot.Item2;var direction=(shot.Item3-shot.Item2).normalized;
                Assert.IsTrue(Physics.Raycast(from,direction,out var hit,2.6f,~0,QueryTriggerInteraction.Collide),shot.Item1+" no physical hit");
                var target=PlayerController.ResolveInteractionHit(hit);
                Assert.NotNull(target,shot.Item1+" surface obscures original interaction (hit "+hit.collider.name+")");
                Assert.AreEqual(shot.Item1,target.name,"Wrong station selected from actual view ray");
            }
            Assert.NotNull(shell.GetComponentInChildren<KioskTerminalDisplay>());
            Assert.NotNull(shell.GetComponentsInChildren<CounterStation>().Single(s=>s.name=="Kiosk_ModernPOS"));
            // Real physics sweep at torso/foot clearance, not just collider configuration.
            foreach (var pair in new[] {
                (new Vector3(-3.5f,.8f,-2.7f), new Vector3(2.6f,.8f,-2.7f)),
                (new Vector3(4.95f,.8f,3f), new Vector3(4.95f,.8f,-4.2f)),
                (new Vector3(-7.9f,.8f,-5.1f), new Vector3(-7.9f,.8f,-7.5f)) })
            {
                var a=root.position+pair.Item1; var b=root.position+pair.Item2;
                Assert.IsFalse(Physics.CapsuleCast(a, a+Vector3.up*.7f, .25f, (b-a).normalized, out var hit, Vector3.Distance(a,b), ~0, QueryTriggerInteraction.Ignore),
                    "Blocked kitchen/access/washroom aisle: " + (hit.collider != null ? hit.collider.name : "unknown"));
            }
            var privacyDoor = shell.GetComponentsInChildren<ActionStation>().Single(s => s.name == "Kiosk_WashroomDoor");
            privacyDoor.Use(game); Physics.SyncTransforms();
            Assert.IsTrue(Physics.Raycast(root.position + new Vector3(-7.9f,1.1f,-5.1f), Vector3.back, out var doorHit, 1.3f), "closed washroom door must physically block entry");
            Assert.AreEqual("Kiosk_WashroomDoor", doorHit.collider.name);
            privacyDoor.Use(game); Physics.SyncTransforms();
            Assert.IsFalse(Physics.Raycast(root.position + new Vector3(-7.9f,1.1f,-5.1f), Vector3.back, 1.3f), "opening door restores entry");
            foreach (int stage in new[] { 1, 2, 3, 7, 1, 2 })
            {
                game.Stages.SetStage(stage); game.Layout.SetKioskLook(stage >= 2); yield return null;
                Assert.AreEqual(stage >= 2, shell.activeSelf);
                Assert.AreEqual(stage < 2, root.Find("BackWall").GetComponent<Collider>().enabled);
                Assert.AreEqual(stage >= 2 ? 10 : 2, game.Layout.Seats.Count(s => s.Enabled));
            }
            var cam=Camera.main;
            var views=new[] {
                ("exterior",new Vector3(13,2,12),new Vector3(0,1.6f,-1)),
                ("interior",new Vector3(-3.7f,1.8f,-3.1f),new Vector3(2,1.25f,-4.9f)),
                ("service",new Vector3(0,1.8f,4.4f),new Vector3(0,1.5f,-2)),
                ("washroom",new Vector3(-7.9f,1.8f,-5.1f),new Vector3(-7.5f,1,-8.5f)) };
            foreach (float hour in new[] { 12f, 21f })
            {
                game.Clock.Restore(1,hour*60f);
                foreach (var v in views)
                {
                    var from=root.position+v.Item2;
                    cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(root.position+v.Item3-from));
                    yield return new WaitForSeconds(.65f);
                    Snap(cam,v.Item1+(hour<18?"_day":"_night"));
                }
            }
            game.Clock.Restore(1,720f);
            var far = root.position + new Vector3(220f,55f,250f);
            cam.transform.SetPositionAndRotation(far, Quaternion.LookRotation(root.position+Vector3.up*1.6f-far));
            architectureLOD.ForceLOD(1); yield return new WaitForSeconds(.5f); Snap(cam,"architecture_lod1_far"); architectureLOD.ForceLOD(-1);
            var used = new System.Collections.Generic.HashSet<string>();
            foreach (var renderer in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None).Where(r => r.enabled && r.gameObject.activeInHierarchy))
            {
                                var filter = renderer.GetComponent<MeshFilter>();
                Mesh mesh = renderer is SkinnedMeshRenderer skinned ? skinned.sharedMesh : (filter != null ? filter.sharedMesh : null);
                if (mesh != null) { var path = UnityEditor.AssetDatabase.GetAssetPath(mesh); if (!string.IsNullOrEmpty(path)) used.Add(path); }
                foreach (var material in renderer.sharedMaterials.Where(m => m != null))
                    foreach (var prop in material.GetTexturePropertyNames())
                    {
                        var texture = material.GetTexture(prop); if (texture == null) continue;
                        var path = UnityEditor.AssetDatabase.GetAssetPath(texture); if (!string.IsNullOrEmpty(path)) used.Add(path);
                    }
            }
            var captureRoot = System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT");
            if (!string.IsNullOrEmpty(captureRoot)) File.WriteAllLines(Path.Combine(captureRoot, "active-stage2-asset-source-paths.txt"), used.OrderBy(p => p));
            Debug.Log("RESORT_ACTIVE_STAGE2_SOURCE_FILES=" + used.Count);
            Debug.Log("KIOSK_COMPLETION_QA stations="+root.GetComponentsInChildren<Interactable>(true).Length+" seats=10 shelfBottles=24 lightEmitters=6 clearAisles=3");
        }
    }
}
