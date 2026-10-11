using System;
using System.Collections;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using ResortAurora.Site;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using Object = UnityEngine.Object;
namespace ResortAurora.Tests
{
 public sealed class VRBNIntegrationTests
 {
  void Shot(Camera camera,ResortSite site,Vector3 from,Vector3 to,string path)
  {
   var pos=camera.transform.position;var rot=camera.transform.rotation;var target=camera.targetTexture;var active=RenderTexture.active;
   var rt=new RenderTexture(1600,900,24);var texture=new Texture2D(1600,900,TextureFormat.RGB24,false);
   try {camera.transform.SetPositionAndRotation(site.transform.TransformPoint(from),Quaternion.LookRotation(site.transform.TransformPoint(to)-site.transform.TransformPoint(from)));camera.targetTexture=rt;camera.Render();RenderTexture.active=rt;texture.ReadPixels(new Rect(0,0,1600,900),0,0);texture.Apply();File.WriteAllBytes(path,texture.EncodeToPNG());}
   finally {camera.transform.SetPositionAndRotation(pos,rot);camera.targetTexture=target;RenderTexture.active=active;Object.Destroy(rt);Object.Destroy(texture);}
  }
  [UnityTest] public IEnumerator LicensedBuildingsFitLotsAndPreserveCollision()
  {
   var oldSave=Environment.GetEnvironmentVariable("RESORT_SAVE_PATH");var oldStage=Environment.GetEnvironmentVariable("RESORT_STAGE");
   var output=Path.GetFullPath("../Evidence");Directory.CreateDirectory(output);
   var save=Path.Combine(output,"isolated_vrbn_test_save.json");
   Environment.SetEnvironmentVariable("RESORT_SAVE_PATH",save);Environment.SetEnvironmentVariable("RESORT_STAGE","1");
   try
   {
    yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity",new LoadSceneParameters(LoadSceneMode.Single));yield return null;yield return null;
    var site=Object.FindAnyObjectByType<ResortSite>();Assert.IsTrue(site.Ready);
    var game=Object.FindAnyObjectByType<ResortGame>();game.OpenPanel(Panel.Help);game.Clock.Restore(1,720);yield return new WaitForSeconds(.3f);
    var vila=site.transform.Find("Vila");var urban=vila.Find("VilaRealista_F02");Assert.NotNull(urban);
    var models=urban.Cast<Transform>().Where(t=>t.name.StartsWith("VRBN_Lot_")).ToArray();Assert.Greater(models.Length,0);
    Assert.IsTrue(vila.GetComponentsInChildren<MeshCollider>().Where(c=>!c.transform.IsChildOf(urban)).All(c=>c.enabled));
    Assert.IsTrue(vila.GetComponentsInChildren<MeshRenderer>().Where(r=>!r.transform.IsChildOf(urban)).All(r=>!r.enabled));
    var report=new StringBuilder("lot,model,scale,width,depth,floor\n");
    foreach(var root in models)
    {
     int index=int.Parse(root.name.Substring("VRBN_Lot_".Length));var lot=site.Data.lots[index];var model=root.GetChild(0);var scale=model.localScale;
     Assert.That(scale.x,Is.InRange(.85f,1f));Assert.AreEqual(scale.x,scale.y);Assert.AreEqual(scale.x,scale.z);
     Assert.IsTrue(CoastalVRBNAssets.TryDescribe(site,lot,out var frame));Assert.LessOrEqual(frame.width,lot.w);Assert.LessOrEqual(frame.depth,lot.d);
     var lod=model.GetComponentInChildren<LODGroup>();Assert.GreaterOrEqual(lod.GetLODs().Length,3);
     Assert.IsTrue(model.GetComponentsInChildren<Collider>(true).All(c=>!c.enabled));
     foreach(var renderer in model.GetComponentsInChildren<Renderer>(true)) foreach(var material in renderer.sharedMaterials)
      {Assert.NotNull(material);Assert.IsTrue(material.shader.isSupported);Assert.IsFalse(UnityEditor.ShaderUtil.ShaderHasError(material.shader),material.shader.name);Assert.AreNotEqual("Hidden/InternalErrorShader",material.shader.name);}
     report.AppendLine(FormattableString.Invariant($"{index},{model.name},{scale.x},{frame.width},{frame.depth},{frame.floor}"));
    }
    File.WriteAllText(Path.Combine(output,"applied_lots.csv"),report.ToString());
    var focus=site.Data.lots[int.Parse(models[0].name.Substring("VRBN_Lot_".Length))];float ground=site.HeightAt(focus.x,focus.z);
    Shot(Camera.main,site,new Vector3(focus.x-16,ground+8,focus.z+23),new Vector3(focus.x,ground+3,focus.z),Path.Combine(output,"vrbn_front.png"));
    Shot(Camera.main,site,new Vector3(focus.x+16,ground+8,focus.z-23),new Vector3(focus.x,ground+3,focus.z),Path.Combine(output,"vrbn_rear.png"));
    Shot(Camera.main,site,new Vector3(150,60,340),new Vector3(150,4,440),Path.Combine(output,"waterfront.png"));
    Shot(Camera.main,site,new Vector3(128,24,279),new Vector3(150,4,308),Path.Combine(output,"avenue.png"));
    File.WriteAllText(Path.Combine(output,"integration_result.txt"),$"VRBN_RUNTIME_PASS replaced={models.Length} totalLots={site.Data.lots.Length} originalCollision=preserved uniformScale=.85..1 visualApproval=pending\n");
   }
   finally {Environment.SetEnvironmentVariable("RESORT_SAVE_PATH",oldSave);Environment.SetEnvironmentVariable("RESORT_STAGE",oldStage);Time.timeScale=1;}
  }
 }
}
