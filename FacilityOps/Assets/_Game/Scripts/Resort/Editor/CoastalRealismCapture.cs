using System;
using System.IO;
using ResortAurora.Site;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.EditorTools
{
    /// <summary>Captures REAL images from Unity at the resort beach. Never generates illustrative mockups.</summary>
    public static class CoastalRealismCapture
    {
        public static void Run()
        {
            string destination = @"D:\ProjectResort_Autonomy\BeachOceanLiveQA\Captures";
            Directory.CreateDirectory(destination);
            EditorSceneManager.OpenScene("Assets/_Game/Scenes/ResortSite.unity", OpenSceneMode.Single);
            var site = UnityEngine.Object.FindAnyObjectByType<ResortSite>();
            if (site == null) throw new InvalidOperationException("ResortSite missing from scene");
            if (!site.Ready) site.Build();
            if (!site.Ready) throw new InvalidOperationException("ResortSite build failed");

            var ocean = site.transform.Find("Sea/CoastalOcean");
            if (ocean == null)
                ocean = site.transform.Find("CoastalOcean");
            if (ocean == null || ocean.GetComponentsInChildren<MeshRenderer>().Length < 4)
                throw new InvalidOperationException("New ocean mesh not found in scene");

            var sand = site.transform.Find("BeachSandPBR");
            if (sand == null) throw new InvalidOperationException("PBR beach absent");
            var sandRenderer = sand.GetComponent<MeshRenderer>();
            if (sandRenderer == null || sandRenderer.sharedMaterial == null ||
                sandRenderer.sharedMaterial.shader == null ||
                !sandRenderer.sharedMaterial.shader.isSupported)
                throw new InvalidOperationException("PBR sand shader unsupported");

            var cameraGo = new GameObject("CoastalRealismQA_Camera");
            var cam = cameraGo.AddComponent<Camera>();
            cam.fieldOfView = 67f;
            cam.nearClipPlane = 0.07f;
            cam.farClipPlane = 4000f;
            cam.clearFlags = CameraClearFlags.Skybox;
            cam.allowHDR = true;
            var source = Camera.main;
            if (source != null) {
                cam.cullingMask = source.cullingMask;
                cam.clearFlags = source.clearFlags;
            }
            // Diagnostic daylight: isolate from the editor scene's potentially uninitialised game clock.
            var existingSun = RenderSettings.sun;
            bool oldSunEnabled = existingSun != null && existingSun.enabled;
            var previousAmbientMode = RenderSettings.ambientMode;
            var previousAmbientSky = RenderSettings.ambientSkyColor;
            var previousAmbientEquator = RenderSettings.ambientEquatorColor;
            var previousAmbientGround = RenderSettings.ambientGroundColor;
            if (existingSun != null) existingSun.enabled = false;
            var testSun = new GameObject("CoastalRealismQA_Sun");
            var light = testSun.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.65f;
            light.color = new Color(1f, .97f, .91f);
            light.shadows = LightShadows.Soft;
            light.transform.rotation = Quaternion.Euler(48f, -35f, 0f);
            RenderSettings.sun = light;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.84f, .90f, .97f);
            RenderSettings.ambientEquatorColor = new Color(.69f, .77f, .85f);
            RenderSettings.ambientGroundColor = new Color(.38f, .38f, .35f);
            try {
                float x = Mathf.Clamp(site.StallX + 80f, 60f, site.Data.size.x - 60f);
                float edge = site.PromenadeZ(x), shore = site.WaterlineZ(x);
                Shot(cam, Path.Combine(destination, "01_praia_relevo.png"),
                    new Vector3(x + 17f, site.HeightAt(x, edge) + 9f, edge + 5f),
                    new Vector3(x, 0.45f, shore - 22f));
                Shot(cam, Path.Combine(destination, "02_mar_arrebentacao.png"),
                    new Vector3(x + 6f, 4.2f, shore + 19f),
                    new Vector3(x - 5f, .4f, shore - 50f));
                Shot(cam, Path.Combine(destination, "03_orla_panoramica.png"),
                    new Vector3(x + 85f, 57f, edge + 95f),
                    new Vector3(x, 1.5f, shore - 35f));
                float roadEdge = CoastalPromenadeAvenueLink.RoadEdge(site.Data);
                Shot(cam, Path.Combine(destination, "04_calcada_avenida_1m.png"),
                    new Vector3(x + 8f, site.HeightAt(x, roadEdge - 9f) + 6f, roadEdge - 9f),
                    new Vector3(x, site.HeightAt(x, roadEdge) + .6f, roadEdge + 10f));
                float grassZ = site.Data.avenue.z + site.Data.avenue.width * .5f + 22f;
                Shot(cam, Path.Combine(destination, "05_gramado_vegetacao_cc0.png"),
                    new Vector3(193f, site.HeightAt(193f, grassZ)+2.8f, grassZ),
                    new Vector3(204f, site.HeightAt(204f, grassZ+44f)+.8f, grassZ+44f));
                Shot(cam, Path.Combine(destination, "06_jardins_CC0_aereo.png"),
                    new Vector3(195f, site.HeightAt(195f, grassZ)+26f, grassZ-12f),
                    new Vector3(205f, site.HeightAt(205f, grassZ+62f)+.5f, grassZ+62f));
                var flora=site.transform.Find("ScannedUnderstory_CC0_FernsShrubs");
                if(flora!=null && flora.childCount>0)
                {
                    Transform candidate=null;
                    float best=float.MaxValue;
                    for(int i=0;i<flora.childCount;i++)
                    {
                        var plant=flora.GetChild(i);
                        var pos=plant.position;
                        if(pos.z>site.Data.avenue.z+site.Data.avenue.width*.5f+75f)continue;
                        float score=Mathf.Abs(pos.x-193f)+Mathf.Abs(pos.z-grassZ);
                        if(score<best){best=score;candidate=plant;}
                    }
                    if(candidate!=null)
                    {
                        Vector3 p=candidate.position;
                        Shot(cam,Path.Combine(destination,"07_novos_arbustos_CC0_closeup.png"),
                            p+new Vector3(-4f,1.6f,-6f),p+new Vector3(0f,.35f,0f));
                    }
                }
                Debug.Log("COASTAL_QA_SUCCESS: 7 real screenshots captured at " + destination +
                    ", ocean renderers=" + ocean.GetComponentsInChildren<MeshRenderer>().Length +
                    ", sand shader=" + sandRenderer.sharedMaterial.shader.name);
            } finally {
                RenderSettings.sun = existingSun;
                if (existingSun != null) existingSun.enabled = oldSunEnabled;
                RenderSettings.ambientMode = previousAmbientMode;
                RenderSettings.ambientSkyColor = previousAmbientSky;
                RenderSettings.ambientEquatorColor = previousAmbientEquator;
                RenderSettings.ambientGroundColor = previousAmbientGround;
                UnityEngine.Object.DestroyImmediate(testSun);
                UnityEngine.Object.DestroyImmediate(cameraGo);
            }
        }

        static void Shot(Camera camera, string path, Vector3 from, Vector3 towards)
        {
            camera.transform.SetPositionAndRotation(from, Quaternion.LookRotation(towards - from));
            var old = RenderTexture.active;
            var rt = new RenderTexture(1600, 900, 24);
            var image = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            try {
                camera.targetTexture = rt;
                camera.Render();
                RenderTexture.active = rt;
                image.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0);
                image.Apply();
                File.WriteAllBytes(path, image.EncodeToPNG());
            } finally {
                camera.targetTexture = null;
                RenderTexture.active = old;
                rt.Release();
                UnityEngine.Object.DestroyImmediate(rt);
                UnityEngine.Object.DestroyImmediate(image);
            }
        }
    }
}
