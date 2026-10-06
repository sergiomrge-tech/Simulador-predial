using System.Collections;
using System.IO;
using NUnit.Framework;
using ResortAurora.Game;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

namespace ResortAurora.Tests
{
    /// <summary>The sobrado of the pousada has a walkable interior: through the gate into the reception, and up the outdoor stair to the first floor.</summary>
    public sealed class PousadaInteriorTests
    {
        string savePath;

        [SetUp] public void SetUp()
        {
            savePath = Path.Combine(Path.GetTempPath(), "resort_test_pousada_" + System.Guid.NewGuid().ToString("N") + ".json");
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", savePath);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", "3");
        }

        [TearDown] public void TearDown()
        {
            System.Environment.SetEnvironmentVariable("RESORT_SAVE_PATH", null);
            System.Environment.SetEnvironmentVariable("RESORT_STAGE", null);
            if (File.Exists(savePath)) File.Delete(savePath);
        }

        static void Walk(CharacterController cc, Vector3 to, float step = 0.08f)
        {
            for (int i = 0; i < 400; i++)
            {
                var d = to - cc.transform.position; d.y = 0f;
                if (d.magnitude < step) break;
                cc.Move(d.normalized * step);
                cc.Move(Vector3.down * 0.15f);
            }
        }

        static void Snap(Camera cam, Vector3 pos, Vector3 look, string path)
        {
            cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(look - pos));
            var rt = new RenderTexture(1600, 900, 24); cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt;
            var t = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            t.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); t.Apply();
            File.WriteAllBytes(path, t.EncodeToPNG());
            cam.targetTexture = null; RenderTexture.active = null; Object.Destroy(rt);
        }

        [UnityTest]
        public IEnumerator ThePlayerCanEnterTheReceptionAndClimbToTheFirstFloor()
        {
#if UNITY_EDITOR
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/ResortPrologue.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null; yield return null;
            var g = Object.FindAnyObjectByType<ResortGame>();
            var player = Object.FindAnyObjectByType<PlayerController>();
            var cc = player.GetComponent<CharacterController>();
            float gy(float x, float z) => g.Site.HeightAt(x, z);

            // 1) through the open gate (x 394) and the front door into the reception (ground floor)
            player.Teleport(new Vector3(394f, gy(394f, 327f) + 0.2f, 327f), Quaternion.identity);
            yield return null;
            Walk(cc, new Vector3(394f, 0f, 337f));
            Assert.Greater(player.transform.position.z, 336f, "walked through the gate and the front door");
            Assert.Less(player.transform.position.y, gy(394f, 342f) + 1.5f, "still on the ground floor");

            // 2) round the east side and up the outdoor stair to the first-floor corridor
            player.Teleport(new Vector3(402.7f, gy(402.7f, 358f) + 0.2f, 358f), Quaternion.identity);
            yield return null;
            Walk(cc, new Vector3(402.7f, 0f, 348.9f));
            Walk(cc, new Vector3(402.7f, 0f, 347.7f));
            Walk(cc, new Vector3(398.5f, 0f, 347.7f));
            float floorY = gy(398.5f, 347.7f);
            Assert.Greater(player.transform.position.y, floorY + 3.4f, "up on the first floor");
            g.Clock.Restore(1, 12f * 60f);
            yield return null; yield return null;
            string dir = Path.GetFullPath("../ArtSource/Blender/World/Reviews/R4");
            Directory.CreateDirectory(dir);
            var cam = Camera.main;
            var rootY = gy(394f, 342f);
            Snap(cam, new Vector3(394f, rootY + 1.7f, 332f), new Vector3(394f, rootY + 1.4f, 346f), dir + "/r4_unity_pousada_recepcao.png");
            Snap(cam, new Vector3(398.5f, floorY + 4.6f, 347.7f), new Vector3(388f, floorY + 4.3f, 347.7f), dir + "/r4_unity_pousada_corredor.png");
            Snap(cam, new Vector3(412f, floorY + 6.5f, 352f), new Vector3(402f, floorY + 4.8f, 347.7f), dir + "/r4_unity_pousada_escada_externa.png");
            Snap(cam, new Vector3(387f, rootY + 1.5f, 330f) + Vector3.up * 3.0f, new Vector3(394f, rootY + 4f, 345f), dir + "/r4_unity_pousada_fachada.png");
            Assert.Less(player.transform.position.x, 401.5f, "inside the corridor");

        }
    }
}
