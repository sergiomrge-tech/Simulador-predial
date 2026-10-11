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
    public sealed class ResortMapEvidenceTests
    {
        string save;
        [SetUp] public void Setup(){save=Path.Combine(Path.GetTempPath(),"resort_map_evidence_"+System.Guid.NewGuid().ToString("N")+".json");System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH",save);System.Environment.SetEnvironmentVariable("RESORT_STAGE","2");}
        [TearDown] public void Cleanup(){System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH",null);System.Environment.SetEnvironmentVariable("RESORT_STAGE",null);if(File.Exists(save))File.Delete(save);}
        static void Shot(Camera cam,string name)
        {
            var root=System.Environment.GetEnvironmentVariable("RESORT_TEST_CAPTURE_ROOT");if(string.IsNullOrEmpty(root))return;
            root=Path.Combine(root,"MapEvidence");Directory.CreateDirectory(root);
            var previous=cam.targetTexture;var active=RenderTexture.active;var rt=new RenderTexture(1600,900,24);var tex=new Texture2D(1600,900,TextureFormat.RGB24,false);
            try{cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1600,900),0,0);tex.Apply();File.WriteAllBytes(Path.Combine(root,name+".png"),tex.EncodeToPNG());}
            finally{cam.targetTexture=previous;RenderTexture.active=active;Object.Destroy(rt);Object.Destroy(tex);}
        }
        [UnityTest] public IEnumerator CaptureCurrentBuildingsPoolAndWholeIsland()
        {
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity",new LoadSceneParameters(LoadSceneMode.Single));yield return null;yield return null;
            var game=Object.FindAnyObjectByType<ResortGame>();game.OpenPanel(Panel.Help);var cam=Camera.main;cam.farClipPlane=5000f;
            foreach(float hour in new[]{12f,21f})
            {
                game.Clock.Restore(1,hour*60f);
                foreach(var target in new[]{("pousada",3,"E3-7_pousada"),("hotel",4,"E4-7_hotel"),("piscina",4,"E4-7_hotel_piscina"),("spa",5,"E5-7_spa"),("grande_hotel",7,"E6-7_grande_hotel")})
                {
                    game.Stages.SetStage(target.Item2);game.Layout.SetKioskLook(true);yield return null;
                    var model=game.Stages.Instances.FirstOrDefault(g=>g.name==target.Item3);Assert.NotNull(model,target.Item3);
                    var renderers=model.GetComponentsInChildren<MeshRenderer>();Assert.Greater(renderers.Length,0);
                    var bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);
                    cam.fieldOfView=60f; float span=Mathf.Max(bounds.size.x,bounds.size.z); Debug.Log("MAP_BOUNDS "+target.Item1+" "+bounds);
                    var from=bounds.center+new Vector3(span*.65f,Mathf.Max(15f,bounds.size.y+span*.8f),-span*.95f);
                    cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(bounds.center-from));yield return new WaitForSeconds(.6f);
                    Shot(cam,target.Item1+(hour<18?"_day":"_night"));
                }
                game.Stages.SetStage(7);yield return null;
                cam.fieldOfView=45f; var fromIsland=new Vector3(game.Site.Data.size.x*.5f,1650f,game.Site.Data.size.z*.5f);var center=new Vector3(game.Site.Data.size.x*.5f,0f,game.Site.Data.size.z*.5f);
                cam.transform.SetPositionAndRotation(fromIsland,Quaternion.LookRotation(center-fromIsland));yield return new WaitForSeconds(.6f);Shot(cam,"whole_island"+(hour<18?"_day":"_night"));
            }
            cam.fieldOfView=60f; var vila=game.Site.transform.Find("Vila/VilaRealista_F02");Assert.NotNull(vila);
            var lot=vila.Cast<Transform>().First(t=>t.name.StartsWith("VRBN_Lot_"));
            var rs=lot.GetComponentsInChildren<Renderer>();var lotBounds=rs[0].bounds;foreach(var r in rs)lotBounds.Encapsulate(r.bounds);
            game.Clock.Restore(1,720f);var fromLot=lotBounds.center+new Vector3(20f,8f,-25f);
            cam.transform.SetPositionAndRotation(fromLot,Quaternion.LookRotation(lotBounds.center-fromLot));yield return new WaitForSeconds(.6f);Shot(cam,"houses_current_day");
            Debug.Log("MAP_EVIDENCE_CAPTURED currentSceneOnly visualApproval=pending");
        }
    }
}
