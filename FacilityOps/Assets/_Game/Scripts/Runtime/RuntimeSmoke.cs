using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FacilityOps
{
    // Explicit opt-in build QA. Never reads or writes the player's real career.
    public sealed class RuntimeSmoke : MonoBehaviour
    {
        public GameRuntime game;
        private string directory;
        private void Capture(string path)
        {
            var target = new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);
            target.Create();
            RenderPipeline.SubmitRenderRequest(game.Player.view,new UniversalRenderPipeline.SingleCameraRequest { destination=target });
            RenderTexture previous=RenderTexture.active;
            RenderTexture.active=target;
            var texture=new Texture2D(1280,720,TextureFormat.RGB24,false);
            texture.ReadPixels(new Rect(0,0,1280,720),0,0);texture.Apply();
            File.WriteAllBytes(path,texture.EncodeToPNG());
            RenderTexture.active=previous;target.Release();Destroy(target);Destroy(texture);
        }
        private void Start() { directory = Path.Combine(Application.dataPath, "..", "QA"); Directory.CreateDirectory(directory); StartCoroutine(Run()); }
        private void Check(bool value, string message)
        {
            if (!value) { File.WriteAllText(Path.Combine(directory, "FAILED.txt"), message); Debug.LogError("SMOKE FAILED: " + message); Application.Quit(1); throw new Exception(message); }
            Debug.Log("SMOKE PASS: " + message);
        }
        private IEnumerator Run()
        {
            yield return new WaitForSeconds(2);
            game.SetTablet(true);
            Capture(Path.Combine(directory, "01-hub-tablet.png"));
            yield return new WaitForSeconds(.5f);
            game.SetTablet(false);
            Capture(Path.Combine(directory, "02-office.png"));
            yield return new WaitForSeconds(.5f);
            for (int cause = 0; cause < 3; cause++)
            {
                Check(game.Session.Accept((FailureCause)cause), "Accept cause " + cause);
                game.LoadLocation(false); game.SetTablet(false);
                yield return new WaitForSeconds(.4f);
                var panelArt=GameObject.Find("Blender / QD01");
                Check(panelArt != null,"Blender equipment loaded");
                Bounds artBounds=new Bounds();bool firstRenderer=true;
                foreach(var renderer in panelArt.GetComponentsInChildren<Renderer>())
                {
                    if(firstRenderer){artBounds=renderer.bounds;firstRenderer=false;}else artBounds.Encapsulate(renderer.bounds);
                }
                Check(artBounds.size.y>1.2f && artBounds.size.y<1.6f,"Imported panel is upright and metre-scaled");
                // Exercise CharacterController grounding and collision, beyond data-only tests.
                game.Player.Teleport(new Vector3(0, 1, 2));
                var cc = game.Player.GetComponent<CharacterController>();
                for (int frame = 0; frame < 20; frame++) { cc.Move(Vector3.down * .1f); yield return null; }
                Check(game.Player.transform.position.y > -.1f && game.Player.transform.position.y < .1f, "Floor collision and grounding");
                cc.Move(Vector3.left * 20);
                Check(game.Player.transform.position.x > -3.5f, "Wall blocks movement");
                foreach (var station in game.World.Stations)
                {
                    Vector3 position = station.transform.position;
                    Vector3 approach = station.id == StationId.Distribution ? new Vector3(1.8f, 0, 0) : station.id == StationId.Controller ? new Vector3(-1.8f, 0, 0) : new Vector3(0, 0, -1.8f);
                    game.Player.Teleport(new Vector3(position.x, .01f, position.z) + approach);
                    game.Player.AimAt(position);
                    Physics.SyncTransforms(); game.Player.RefreshFocus();
                    Check(game.Player.Focus == (IInteractable)station, "Raycast reaches " + station.id);
                    game.Tool = ToolMode.Inspect; game.Player.Focus.Interact(game);
                    game.Tool = ToolMode.Scanner; game.Player.Focus.Interact(game);
                    game.Tool = ToolMode.SignalProbe; game.Player.Focus.Interact(game);
                    if (cause == 0 && station.id == StationId.Distribution)
                    {
                        Capture(Path.Combine(directory, "03-diagnostics.png"));
                        yield return new WaitForSeconds(.5f);
                    }
                }
                Check(game.Session.Active.testedNodes.Count == 6, "All measurement tools produce evidence");
                game.Save();
                var loaded = SaveService.Load(game.SavePath);
                Check(loaded.active != null && loaded.active.evidence.Count == game.Session.Active.evidence.Count, "Active service save/load");
                game.Diagnose((FailureCause)cause);
                game.Tool = ToolMode.Repair;
                game.World.Stations[cause].Interact(game);
                Check(game.Session.Active.repaired, "Repair resolves cause " + cause);
                Check(game.World.WorkLights.TrueForAll(light => light.enabled), "Lighting visually restored");
                if (cause == 0)
                {
                    game.Player.Teleport(new Vector3(0, .01f, 5));
                    game.Player.AimAt(new Vector3(0, 1.8f, 13));
                    game.Notify("Iluminação restaurada. Teste integrado pendente.");
                    Capture(Path.Combine(directory, "04-repaired-corridor.png"));
                    yield return new WaitForSeconds(.5f);
                }
                game.Tool = ToolMode.Verify;
                game.World.Stations[0].Interact(game);
                Check(game.Session.Active.validated, "Final verification");
                game.Deliver();
                Check(game.AtOffice && game.Session.Active == null, "Settlement returns to hub");
                Check(game.Session.Career.completed == cause + 1, "Exactly one payment per service");
                yield return new WaitForSeconds(.4f);
            }
            game.Save();
            Check(SaveService.Load(game.SavePath).completed == 3, "Career persisted after all three causes");
            Check(game.Session.Career.money == 1600, "Economy total after three clean jobs");
            Capture(Path.Combine(directory, "05-completed.png"));
            yield return new WaitForSeconds(1);
            Check(game.Campaign != null && game.Campaign.locations.Length == 24, "Campaign catalog: 24 locations");
            int connections = 0, floors = 0;
            foreach (var location in game.Campaign.locations)
            {
                for (int f = 0; f < location.floors.Length; f++)
                {
                    game.VisitPreview(location, f);
                    yield return null;
                    Physics.SyncTransforms();
                    FloorData floor = location.floors[f];
                    foreach (var link in floor.connections)
                    {
                        var from = Array.Find(floor.rooms, room => room.id == link.from);
                        var to = Array.Find(floor.rooms, room => room.id == link.to);
                        game.Player.Teleport(new Vector3(from.x,.05f,from.z));
                        var target = new Vector3(to.x,.05f,to.z);
                        game.Player.GetComponent<CharacterController>().Move(target - game.Player.transform.position);
                        Check(Vector3.Distance(game.Player.transform.position,target)<.3f,"Door route "+link.from+" → "+link.to);
                        connections++;
                    }
                    floors++;
                    if (location.id == "central" && f == 0)
                    {
                        game.Player.Teleport(new Vector3(0,.05f,0));
                        Capture(Path.Combine(directory,"06-central-layout.png"));
                        yield return new WaitForSeconds(.5f);
                    }
                }
            }
            Check(game.Session.Career.completed == 3 && game.Session.Career.money == 1600, "Map previews never alter career rewards");
            game.ReturnToOffice();
            File.WriteAllText(Path.Combine(directory, "PASSED.txt"), "Windows runtime smoke passed: three causes, first-person camera, raycasts, collision, evidence, repair, lighting, final test, settlement, save/load. Campaign previews: " + floors + " floors / " + connections + " traversable door connections.\n" + DateTime.UtcNow.ToString("O"));
            Application.Quit(0);
        }
    }
}
