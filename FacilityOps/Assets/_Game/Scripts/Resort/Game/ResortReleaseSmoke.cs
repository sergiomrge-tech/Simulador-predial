using System;
using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;
namespace ResortAurora.Game
{
    // Explicit opt-in for isolated release QA. No component is added during normal play.
    public sealed class ResortReleaseSmoke : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Install()
        {
            if(!string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("RESORT_RELEASE_SMOKE_ROOT")))
                new GameObject("ResortReleaseSmoke").AddComponent<ResortReleaseSmoke>();
        }
        string folder;
        void Capture(Camera cam,string name)
        {
            var old=cam.targetTexture;var active=RenderTexture.active;
            var rt=new RenderTexture(1600,900,24);var tex=new Texture2D(1600,900,TextureFormat.RGB24,false);
            try {cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1600,900),0,0);tex.Apply();File.WriteAllBytes(Path.Combine(folder,name+".png"),tex.EncodeToPNG());}
            finally {cam.targetTexture=old;RenderTexture.active=active;Destroy(rt);Destroy(tex);}
        }
        IEnumerator Start()
        {
            folder=Environment.GetEnvironmentVariable("RESORT_RELEASE_SMOKE_ROOT");Directory.CreateDirectory(folder);
            ResortGame game=null;
            for(int i=0;i<600;i++){game=FindAnyObjectByType<ResortGame>();if(game!=null&&game.Layout!=null&&game.Stages!=null)break;yield return null;}
            if(game==null||game.Layout==null||game.Stages==null){Debug.LogError("RELEASE_SMOKE_FAILED startup");Application.Quit(2);yield break;}
            yield return new WaitForSecondsRealtime(2f);
            var cam=Camera.main;var home=FindAnyObjectByType<PlayerController>().transform.position;
            bool spawn=Mathf.Abs(home.x-880f)<1f&&Mathf.Abs(home.z-338.5f)<1f&&home.y>game.Site.Data.seaLevel;
            Debug.Log("RELEASE_SMOKE_HOME position="+home+" verified="+spawn);
            Capture(cam,"home_spawn");
            game.OpenPanel(Panel.Help);
            game.Stages.SetStage(2);game.Layout.SetKioskLook(true);
            var origin=game.Layout.Root.position;
            foreach(float hour in new[]{12f,21f})
            {
                game.Clock.Restore(1,hour*60f);
                var from=origin+new Vector3(13f,2f,12f);cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(origin+new Vector3(0,1.6f,-1)-from));
                yield return new WaitForSecondsRealtime(1f);Capture(cam,hour<18?"kiosk_day":"kiosk_night");
                from=origin+new Vector3(-3.7f,1.8f,-3.1f);cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(origin+new Vector3(2f,1.25f,-4.9f)-from));
                yield return new WaitForSecondsRealtime(.7f);Capture(cam,hour<18?"interior_day":"interior_night");
            }
            game.Clock.Restore(1,720f);yield return new WaitForSecondsRealtime(2f);
            // Batch Update frequency is not GPU FPS. Force a full HD render and readback per sample.
            var previous=cam.targetTexture;var active=RenderTexture.active;
            var perfTarget=new RenderTexture(1920,1080,24);var pixel=new Texture2D(1,1,TextureFormat.RGB24,false);
            cam.targetTexture=perfTarget;
            for(int i=0;i<20;i++){cam.Render();yield return null;}
            int frames=90;var times=new float[frames];
            for(int i=0;i<frames;i++)
            {
                var watch=System.Diagnostics.Stopwatch.StartNew();
                cam.Render();RenderTexture.active=perfTarget;pixel.ReadPixels(new Rect(0,0,1,1),0,0);
                times[i]=(float)watch.Elapsed.TotalMilliseconds;yield return null;
            }
            cam.targetTexture=previous;RenderTexture.active=active;Destroy(perfTarget);Destroy(pixel);
            Array.Sort(times);float mean=times.Average();float fps=1000f/mean;
            Debug.Log(FormattableString.Invariant($"RELEASE_RENDER_PERF fullHD avgMS={mean:F2} p95MS={times[85]:F2} worstMS={times[89]:F2} FPS={fps:F1} samples=90 GPUReadback=true"));
            var shell=game.Stages.Instances.Single(g=>g.name=="E2-7_quiosque");
            bool seats=game.Layout.Seats.Count(s=>s.Enabled)==10;
            bool stations=game.Layout.Root.GetComponentsInChildren<Interactable>(true).All(s=>s.GetComponent<Collider>()!=null&&s.GetComponent<Collider>().enabled);
            var vila=game.Site.transform.Find("Vila/VilaRealista_F02");
            int vrbn=vila!=null?vila.Cast<Transform>().Count(t=>t.name.StartsWith("VRBN_Lot_")):0;
            string text=FormattableString.Invariant($"spawn={spawn} stations={stations} seats={seats} kioskActive={shell.activeSelf} km2={game.Site.Data.size.x*game.Site.Data.size.z/1000000f:F2} vrbnLots={vrbn}/{game.Site.Data.lots.Length} renderFPS={fps:F1} renderResolution=1920x1080 window={Screen.width}x{Screen.height} GPU={SystemInfo.graphicsDeviceName}");
            File.WriteAllText(Path.Combine(folder,"smoke-result.txt"),text);
            bool ok=spawn&&stations&&seats&&shell.activeSelf;
            Debug.Log("RELEASE_SMOKE_"+(ok?"PASS ":"FAILED ")+text);Application.Quit(ok?0:2);
        }
    }
}
