using System;
using System.Collections;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using ResortAurora.Game;
using ResortAurora.Site;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEditor.SceneManagement;
using Object = UnityEngine.Object;

namespace ResortAurora.Tests
{
    public sealed class UrbanVisualPassTests
    {
        string save, oldSave, oldStage, output;
        [SetUp] public void Setup()
        {
            oldSave = Environment.GetEnvironmentVariable("RESORT_SAVE_PATH");
            oldStage = Environment.GetEnvironmentVariable("RESORT_STAGE");
            save = Path.Combine(Path.GetTempPath(), "codex_urban_" + Guid.NewGuid().ToString("N") + ".json");
            Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", save);
            Environment.SetEnvironmentVariable("RESORT_STAGE", "1");
            output = Path.GetFullPath("Captures/CodexUrbanPass/" + DateTime.Now.ToString("yyyyMMdd_HHmmss"));
            Directory.CreateDirectory(output);
        }
        [TearDown] public void Cleanup()
        {
            Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", oldSave);
            Environment.SetEnvironmentVariable("RESORT_STAGE", oldStage);
            if (File.Exists(save)) File.Delete(save);
            Time.timeScale = 1;
        }
        void Shot(Camera camera, ResortSite site, Vector3 from, Vector3 at, string name)
        {
            var position = camera.transform.position; var rotation = camera.transform.rotation;
            var target = camera.targetTexture; var active = RenderTexture.active;
            var rt = new RenderTexture(1600, 900, 24);
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            try
            {
                from = site.transform.TransformPoint(from); at = site.transform.TransformPoint(at);
                camera.transform.SetPositionAndRotation(from, Quaternion.LookRotation(at - from));
                camera.targetTexture = rt; camera.Render(); RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
                File.WriteAllBytes(Path.Combine(output, name + ".png"), tex.EncodeToPNG());
            }
            finally
            {
                camera.transform.SetPositionAndRotation(position, rotation);
                camera.targetTexture = target; RenderTexture.active = active;
                Object.Destroy(rt); Object.Destroy(tex);
            }
        }
        [UnityTest] public IEnumerator ConnectedGroundAndScansPreserveKiosk()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
            yield return null; yield return null;
            var game = Object.FindAnyObjectByType<ResortGame>(); Assert.NotNull(game);
            game.OpenPanel(Panel.Help); game.Clock.Restore(1, 720);
            var site = Object.FindAnyObjectByType<ResortSite>(); Assert.IsTrue(site.Ready);
            var data = site.Data;
            Assert.IsTrue(CoastalUrbanAssets.Available);
            var urban = site.transform.Find("Vila/VilaRealista_F02"); Assert.NotNull(urban);
            Assert.Greater(urban.GetComponentsInChildren<MeshRenderer>().Length, 0);
            Assert.IsTrue(site.transform.Find("Vila").GetComponentsInChildren<MeshCollider>().All(c => c.enabled));
            Assert.IsTrue(site.transform.Find("Vila").GetComponentsInChildren<MeshRenderer>()
                .Where(r => !r.transform.IsChildOf(urban)).All(r => !r.enabled));
            foreach (var ns in data.streetsNS)
            {
                for (float z = data.avenue.z; z < ns.to; z += 1)
                    Assert.IsTrue(CoastalUrbanGround.IsRoad(data, ns.x, z), "connected NS carriageway");
                foreach (var ew in data.streetsEW)
                { Assert.IsTrue(CoastalUrbanGround.IsRoad(data, ns.x, ew.z)); Assert.IsFalse(CoastalUrbanGround.IsSidewalk(data, ns.x, ew.z)); }
            }
            var walkMesh = site.transform.Find("UrbanGroundPBR/BlockSidewalks").GetComponent<MeshFilter>().sharedMesh;
            var vertices = walkMesh.vertices;
            for (int i = 0; i < vertices.Length; i += 4)
            {
                var p = (vertices[i] + vertices[i + 1] + vertices[i + 2] + vertices[i + 3]) / 4;
                Assert.IsFalse(CoastalUrbanGround.IsRoad(data, p.x, p.z), "sidewalk quad crosses a road");
            }
            foreach (string name in new[] { "FrontagePaving", "CommercialServiceAprons" })
            {
                var apron = site.transform.Find("UrbanGroundPBR/" + name); Assert.NotNull(apron, name);
                Assert.IsNull(apron.GetComponent<Collider>(), "visual paving preserves original collision");
                var points = apron.GetComponent<MeshFilter>().sharedMesh.vertices;
                Assert.Greater(points.Length, 0, name);
                for (int i = 0; i < points.Length; i += 4)
                {
                    var centre = (points[i]+points[i+1]+points[i+2]+points[i+3])/4;
                    foreach (var corner in points.Skip(i).Take(4))
                    {
                        var p=Vector3.Lerp(corner,centre,.01f);
                        Assert.IsFalse(CoastalUrbanGround.IsRoad(data,p.x,p.z), name+" overlaps road");
                        Assert.IsFalse(CoastalUrbanGround.IsSidewalk(data,p.x,p.z), name+" overlaps sidewalk");
                    }
                }
            }
            var props = site.transform.Find("UrbanPropsRealistic_F02"); Assert.NotNull(props);
            var promenadeLamps=game.DayNight.transform.Find("PromenadeLamps"); Assert.NotNull(promenadeLamps);
            Assert.AreEqual(12,promenadeLamps.childCount,"retain existing kiosk exclusion and lamp spacing");
            var pointLights=game.DayNight.GetComponentsInChildren<Light>().Where(l=>l.type==LightType.Point).ToArray();
            Assert.AreEqual(8,pointLights.Length,"scanned fixtures reuse the existing light pool");
            foreach(Transform post in promenadeLamps)
            {
                var pole=post.Find("Pole");
                Assert.IsTrue(pole.GetComponent<Collider>().enabled,"preserve original post collision");
                Assert.IsFalse(pole.GetComponent<Renderer>().enabled);
                Assert.IsFalse(post.Find("Arm").GetComponent<Renderer>().enabled);
                var scan=post.Find("PromenadeLampScan"); Assert.NotNull(scan);
                var rs=scan.GetComponentsInChildren<Renderer>(); var b=rs[0].bounds;
                foreach(var r in rs.Skip(1)) b.Encapsulate(r.bounds);
                Assert.That(b.size.y,Is.InRange(4.19f,4.21f));
                Assert.That(Mathf.Abs(b.min.y-post.position.y),Is.LessThan(.01f));
                Assert.Less(Mathf.Max(b.size.x,b.size.z),1,"metric vertical lamp, not a sideways FBX");
                Assert.NotNull(scan.GetComponent<LODGroup>());
                var mats=rs.SelectMany(r=>r.sharedMaterials).ToArray();
                Assert.IsTrue(mats.Any(m=>m.name=="LampHead"),"scan bulb follows shared dusk/night emission");
                Assert.IsFalse(post.Find("LampHead").GetComponent<Renderer>().enabled,"no prototype sphere outside the lantern");
                foreach(var glass in mats.Where(m=>m.name.EndsWith("_glass")))
                { Assert.AreEqual(1,glass.GetFloat("_Surface")); Assert.Less(glass.GetColor("_BaseColor").a,.3f); }
            }
            foreach (Transform prop in props)
            {
                if (prop.name == "FacadeDetails") continue;
                var renderers = prop.GetComponentsInChildren<Renderer>(); Assert.Greater(renderers.Length, 0);
                var b = renderers[0].bounds; foreach (var r in renderers.Skip(1)) b.Encapsulate(r.bounds);
                var p = site.transform.InverseTransformPoint(new Vector3(b.center.x, b.min.y, b.center.z));
                if (prop.name.StartsWith("Manhole")) Assert.That(b.size.y, Is.InRange(.06f, .08f));
                else
                {
                    float expected = site.HeightAt(p.x, p.z) + (CoastalUrbanGround.IsSidewalk(data, p.x, p.z) ? .085f : .035f);
                    Assert.That(Mathf.Abs(p.y - expected), Is.LessThan(.012f), "prop feet are not grounded: " + prop.name);
                }
                if (prop.name.Contains("Lamp"))
                {
                    Assert.That(b.size.y, Is.InRange(4.7f, 4.9f));
                    Assert.Less(Mathf.Max(b.size.x,b.size.z), 1.8f, "FBX axis conversion lost: horizontal giant lamp");
                }
                if (prop.name.StartsWith("Hydrant")) Assert.That(b.size.y, Is.InRange(.8f, .84f));
            }
            foreach (var renderer in site.GetComponentsInChildren<Renderer>())
                if (renderer.enabled)
                    foreach (var m in renderer.sharedMaterials)
                    { Assert.NotNull(m, renderer.name); Assert.NotNull(m.shader); Assert.IsTrue(m.shader.isSupported); Assert.AreNotEqual("Hidden/InternalErrorShader", m.shader.name); }
            foreach (var r in props.GetComponentsInChildren<Renderer>())
                foreach (var m in r.sharedMaterials)
                    if (m.GetTexture("_BaseMap") != null)
                    { Assert.NotNull(m.GetTexture("_BumpMap"), m.name); Assert.NotNull(m.GetTexture("_MetallicGlossMap"), m.name); }
            Assert.NotNull(game.Layout.Root.Find("Counter").GetComponent<CounterStation>());
            Assert.NotNull(game.Layout.Root.Find("Cooler").GetComponent<ActionStation>());
            Assert.NotNull(game.Layout.Root.Find("S1_Fridge").GetComponent<ActionStation>());
            var jobs=game.Layout.Root.Find("JobBoard");
            Assert.NotNull(jobs.GetComponent<PanelStation>()); Assert.IsTrue(jobs.GetComponent<Collider>().enabled);
            Assert.IsFalse(jobs.GetComponent<MeshRenderer>().enabled);
            Assert.NotNull(game.Layout.Root.Find("Codex_KioskJobBoard"));
            Assert.AreEqual(Panel.Hire, jobs.GetComponent<PanelStation>().panel);
            game.Layout.SetKioskLook(true);
            Assert.IsTrue(jobs.GetComponent<Collider>().enabled);
            Assert.IsFalse(jobs.GetComponent<MeshRenderer>().enabled);
            Assert.IsTrue(game.Layout.Root.Find("Codex_KioskJobBoard").GetComponentInChildren<Renderer>().enabled);
            game.Layout.SetKioskLook(false);
            Assert.IsFalse(jobs.GetComponent<MeshRenderer>().enabled);
            var dimensions = new StringBuilder("name\twidth\theight\tdepth\n");
            foreach (Transform prop in props.Find("FacadeDetails"))
            {
                var rs=prop.GetComponentsInChildren<Renderer>(); var b=rs[0].bounds;
                foreach(var r in rs.Skip(1)) b.Encapsulate(r.bounds);
                dimensions.AppendLine($"{prop.name}\t{b.size.x}\t{b.size.y}\t{b.size.z}");
                if(prop.name.StartsWith("ShopServiceShutter"))
                { Assert.That(b.size.x,Is.InRange(.9f,1.3f)); Assert.That(b.size.z,Is.InRange(.15f,.4f)); }
                if(prop.name.StartsWith("FacadeDownpipe"))
                { Assert.Less(b.size.x,.3f); Assert.Less(b.size.z,.3f); }
            }
            File.WriteAllText(Path.Combine(output,"facade_dimensions.tsv"),dimensions.ToString());
            yield return new WaitForSeconds(.1f);
            Shot(Camera.main, site, new Vector3(150, 60, 340), new Vector3(150, 4, 440), "01_connected_waterfront");
            Shot(Camera.main, site, new Vector3(128, 24, 279), new Vector3(150, 4, 308), "02_avenue_junction");
            Shot(Camera.main, site, new Vector3(190, 7, 427), new Vector3(190, 5, 410), "03_street_frontages");
            Shot(Camera.main, site, new Vector3(185, 9, 385), new Vector3(185, 5, 410), "04_rear_and_sides");
            var bench = props.Cast<Transform>().First(t => t.name.StartsWith("PromenadeBench"));
            var bp = site.transform.InverseTransformPoint(bench.position);
            Shot(Camera.main, site, bp + new Vector3(2, 1.5f, 2.7f), bp + Vector3.up * .6f, "05_scan_furniture");
            var ac = props.GetComponentsInChildren<Transform>().First(t => t.name.StartsWith("FacadeAC"));
            var ap = site.transform.InverseTransformPoint(ac.position);
            Shot(Camera.main, site, ap + new Vector3(2, 1.1f, -3), ap + Vector3.up * .35f, "06_facade_detail");
            var kp = site.transform.InverseTransformPoint(game.Layout.Root.position);
            Shot(Camera.main, site, kp + new Vector3(7, 2, 6), kp + Vector3.up, "07_kiosk_preserved");
            var shutter = props.GetComponentsInChildren<Transform>().First(t=>t.name.StartsWith("ShopServiceShutter"));
            var sp=site.transform.InverseTransformPoint(shutter.position);
            Shot(Camera.main,site,sp+new Vector3(2,1.7f,-3),sp+Vector3.up,"08_shop_service_detail");
            var lampPost=promenadeLamps.Cast<Transform>().OrderBy(p=>Mathf.Abs(p.position.x-game.Layout.Root.position.x)).First();
            var lp=site.transform.InverseTransformPoint(lampPost.position);
            Shot(Camera.main,site,lp+new Vector3(3,1.7f,-5),lp+Vector3.up*2.5f,"09_promenade_scan_day");
            var reviewCamera=Camera.main; var oldPosition=reviewCamera.transform.position; var oldRotation=reviewCamera.transform.rotation;
            reviewCamera.transform.position=site.transform.TransformPoint(lp+new Vector3(3,1.7f,-5));
            game.Clock.Restore(1,21*60);
            // The existing nearest-light pool must see the review camera during
            // Update, rather than moving it only for an immediate offscreen render.
            yield return new WaitForSeconds(.5f);
            var emitter=lampPost.Find("LampHead").position;
            Assert.IsTrue(pointLights.Any(l=>l.enabled && (l.transform.position-emitter).sqrMagnitude<.01f),
                "nearby scanned lantern retains its pooled real night light at the bulb");
            Assert.Greater(lampPost.Find("LampHead").GetComponent<Renderer>().sharedMaterial.GetColor("_EmissionColor").maxColorComponent,1);
            Shot(Camera.main,site,lp+new Vector3(3,1.7f,-5),lp+Vector3.up*2.5f,"10_promenade_scan_night");
            reviewCamera.transform.SetPositionAndRotation(oldPosition,oldRotation);
            File.WriteAllText(Path.Combine(output, "validation.txt"),
                $"Urban integration PASS; lots={data.lots.Length}; buildingRenderers={urban.GetComponentsInChildren<Renderer>().Length}; " +
                $"streetProps={props.childCount - 1}; sidewalkVertices={vertices.Length}; original collision and kiosk stations preserved.\n" +
                "Shader support checks passed. Screenshot inspection is still required; visual phase is NOT approved.\n");
            Debug.Log("CODEX_URBAN_VALIDATION captures=" + output);
        }
    }
}
