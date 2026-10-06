using ResortAurora.Placement;
using ResortAurora.Site;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ResortAurora.EditorTools
{
    /// <summary>Batch screenshot of the site for review: Unity -batchmode -executeMethod ResortAurora.EditorTools.ResortCapture.Run (needs a GPU, no -nographics).</summary>
    public static class ResortCapture
    {
        public static void Run()
        {
            EditorSceneManager.OpenScene("Assets/_Game/Scenes/ResortSite.unity");
            var site = Object.FindAnyObjectByType<ResortSite>();
            site.Build();
            var cam = Camera.main;
            string dir = System.IO.Path.GetFullPath("../ArtSource/Blender/World/Reviews/R1");
            System.IO.Directory.CreateDirectory(dir);
            Shot(cam, dir + "/r1_site_aerea.png", site.PadCenter + new Vector3(-60f, 90f, -170f), site.PadCenter);
            Shot(cam, dir + "/r1_site_praia.png", new Vector3(160f, 45f, 20f), new Vector3(160f, 0f, 250f));
            Debug.Log("ResortCapture: pad " + site.PadCenter);
        }

        static void Shot(Camera cam, string path, Vector3 pos, Vector3 look)
        {
            cam.transform.parent.position = Vector3.zero;
            cam.transform.parent.rotation = Quaternion.identity;
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
            var rt = new RenderTexture(1600, 900, 24);
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var t = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            t.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0);
            System.IO.File.WriteAllBytes(path, t.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null;
        }
    }
}
