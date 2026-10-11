using System;
using System.IO;
using ResortAurora.Site;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.EditorTools
{
    public static class IslandVisualCapture
    {
        const string Out=@"D:\ProjectResort_Autonomy\Island2km2_20261007\Captures";
        public static void Run()
        {
            Directory.CreateDirectory(Out);
            EditorSceneManager.OpenScene("Assets/_Game/Scenes/ResortPrologue.unity", OpenSceneMode.Single);
            var site=UnityEngine.Object.FindAnyObjectByType<ResortSite>();
            if(site==null) throw new InvalidOperationException("Island scene not loaded");
            if(!site.Ready)site.Build();
            if(!site.Ready||site.Data.size.x!=2000f)throw new InvalidOperationException("Wrong world");
            var stagePreview=new GameObject("IslandPhotoStage1");
            var stages=stagePreview.AddComponent<ResortStages>();
            stages.Init(site);stages.SetStage(1);
            var go=new GameObject("IslandPhotoRealCamera");
            var cam=go.AddComponent<Camera>();cam.fieldOfView=66;cam.farClipPlane=5000;
            cam.clearFlags=CameraClearFlags.Skybox;cam.allowHDR=true;
            var oldSun=RenderSettings.sun;
            bool oldEnabled=oldSun!=null&&oldSun.enabled;
            var oldMode=RenderSettings.ambientMode;
            var oldSky=RenderSettings.ambientSkyColor;
            var oldEq=RenderSettings.ambientEquatorColor;
            var oldGround=RenderSettings.ambientGroundColor;
            if(oldSun!=null)oldSun.enabled=false;
            var sun=new GameObject("IslandDaylight");
            var light=sun.AddComponent<Light>();
            light.type=LightType.Directional;light.shadows=LightShadows.Soft;
            light.intensity=1.5f;light.color=new Color(1f,.95f,.89f);
            light.transform.rotation=Quaternion.Euler(52f,-28f,0);
            RenderSettings.sun=light;
            RenderSettings.ambientMode=AmbientMode.Trilight;
            RenderSettings.ambientSkyColor=new Color(.75f,.85f,.94f);
            RenderSettings.ambientEquatorColor=new Color(.66f,.73f,.79f);
            RenderSettings.ambientGroundColor=new Color(.34f,.39f,.35f);
            try
            {
                var h=site.Data.home;
                Shot(cam,"01_casa_spawn.png",
                    new Vector3(h.x,site.HeightAt(h.x,h.doorZ)+2.0f,h.doorZ-7f),
                    new Vector3(h.x,site.HeightAt(h.x,h.z)+2.2f,h.z));
                Shot(cam,"02_praia_sul.png",
                    new Vector3(1040f,site.HeightAt(1040f,site.PromenadeZ(1040f))+15f,site.PromenadeZ(1040f)+6f),
                    new Vector3(1000f,0f,site.WaterlineZ(1000f)-60f));
                Shot(cam,"03_costa_norte.png",
                    new Vector3(1000f,site.HeightAt(1000f,886f)+24f,886f),
                    new Vector3(1000f,-.25f,1020f));
                Shot(cam,"04_costa_leste.png",
                    new Vector3(1900f,site.HeightAt(1900f,580f)+29f,580f),
                    new Vector3(2100f,-.25f,580f));
                Shot(cam,"05_costa_oeste.png",
                    new Vector3(110f,site.HeightAt(110f,575f)+26f,575f),
                    new Vector3(-210f,-.25f,575f));
                Shot(cam,"06_mapa_ilha_aereo.png",
                    new Vector3(1000f,1170f,400f),new Vector3(1000f,0f,500f));
                Debug.Log("ISLAND_CAPTURE_SUCCESS count=6 source=UnityEditor.Camera.Render");
            }
            finally
            {
                RenderSettings.sun=oldSun;
                if(oldSun!=null)oldSun.enabled=oldEnabled;
                RenderSettings.ambientMode=oldMode;
                RenderSettings.ambientSkyColor=oldSky;
                RenderSettings.ambientEquatorColor=oldEq;
                RenderSettings.ambientGroundColor=oldGround;
                UnityEngine.Object.DestroyImmediate(sun);
                UnityEngine.Object.DestroyImmediate(go);
                UnityEngine.Object.DestroyImmediate(stagePreview);
            }
        }
        static void Shot(Camera cam,string file,Vector3 from,Vector3 target)
        {
            cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(target-from));
            var active=RenderTexture.active;
            var targetTexture=new RenderTexture(1280,720,24);
            var snapshot=new Texture2D(1280,720,TextureFormat.RGB24,false);
            try {
                cam.targetTexture=targetTexture;cam.Render();
                RenderTexture.active=targetTexture;
                snapshot.ReadPixels(new Rect(0,0,1280,720),0,0);
                snapshot.Apply();File.WriteAllBytes(Path.Combine(Out,file),snapshot.EncodeToPNG());
            } finally {
                cam.targetTexture=null;RenderTexture.active=active;
                targetTexture.Release();
                UnityEngine.Object.DestroyImmediate(targetTexture);
                UnityEngine.Object.DestroyImmediate(snapshot);
            }
        }
    }
}
