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
            game.Accept();
            Check(game.Session.IsPrologue && !game.World.WorkLights.TrueForAll(light => light.enabled), "Default campaign begins with authored prologue and dark corridor");
            var distribution = game.World.Stations[0];
            var luminaire = game.World.Stations[2];
            game.Tool = ToolMode.Restore; distribution.Interact(game);
            Check(game.World.WorkLights.TrueForAll(light => light.enabled), "Rearming temporarily restores visual lighting");
            game.SetTablet(true);
            yield return new WaitForSeconds(.3f);
            Check(game.Session.Active.heatSeconds == 0, "Tablet pauses thermal simulation");
            game.SetTablet(false);
            yield return new WaitForSeconds(5.2f);
            Check(!game.Session.Network.LightingHealthy && game.World.WorkLights.TrueForAll(light => !light.enabled), "Live runtime heat trips unrepaired circuit and turns lights off");
            game.Tool = ToolMode.Inspect; luminaire.Interact(game);
            game.Tool = ToolMode.Scanner; distribution.Interact(game);
            game.Tool = ToolMode.SignalProbe; luminaire.Interact(game);
            game.Diagnose(FailureCause.LightDriver);
            game.Tool = ToolMode.Repair; luminaire.Interact(game);
            Check(!game.Session.Active.repaired && game.Session.Career.driverParts == 1, "Unsafe attempt consumes no extra stock");
            game.Tool = ToolMode.Isolate; distribution.Interact(game);
            game.Tool = ToolMode.Verify; luminaire.Interact(game);
            game.Save();
            var prologueSave = SaveService.Load(game.SavePath);
            Check(prologueSave.active.isolated && prologueSave.active.insulationTested && prologueSave.campaignJournal.Count == 3, "Isolated prologue and mentor messages persist");
            game.Tool = ToolMode.Repair; luminaire.Interact(game);
            Check(game.Session.Active.repaired && !game.Session.Network.LightingHealthy, "Replacement leaves circuit isolated");
            game.Tool = ToolMode.Restore; distribution.Interact(game);
            game.Tool = ToolMode.Verify; distribution.Interact(game);
            Check(!game.Session.Active.validated, "Immediate final test rejected before soak");
            yield return new WaitForSeconds(5.2f);
            distribution.Interact(game);
            Check(game.Session.Active.validated && game.World.WorkLights.TrueForAll(light => light.enabled), "Authored repair passes thermal stability test");
            Capture(Path.Combine(directory,"07-prologue-stable.png"));
            game.Deliver();
            var career = SaveService.Load(game.SavePath);
            Check(game.AtOffice && career.prologueCompleted && career.completed == 4 && career.money == 2000 && career.campaignJournal.Count == 5, "Authored prologue payment, chapter frontier and journal saved");
            Check(!game.Session.AcceptPrologue(), "Finished prologue cannot be farmed");
            int missionRoutes=0;
            for(int jobIndex=0;jobIndex<ChapterOne.Jobs.Length;jobIndex++)
            {
                var job=ChapterOne.Jobs[jobIndex];
                game.Accept();
                yield return null;
                Check(game.Session.ActiveJob==job && game.World.CurrentLocationId==job.locationId,"Authored service loads matching campaign location "+job.locationId);
                var place=Array.Find(game.Campaign.locations,location=>location.id==job.locationId);
                var floor=place.floors[0];
                foreach(var link in floor.connections)
                {
                    var from=Array.Find(floor.rooms,room=>room.id==link.from);
                    var to=Array.Find(floor.rooms,room=>room.id==link.to);
                    game.Player.Teleport(new Vector3(from.x,.05f,from.z));
                    var target=new Vector3(to.x,.05f,to.z);
                    game.Player.GetComponent<CharacterController>().Move(target-game.Player.transform.position);
                    Check(Vector3.Distance(game.Player.transform.position,target)<.3f,"Equipment preserves door passage "+link.from+" → "+link.to);
                    missionRoutes++;
                }
                foreach(var station in game.World.Stations)
                {
                    game.Player.Teleport(new Vector3(station.transform.position.x,.01f,station.transform.position.z-1.8f));
                    game.Player.AimAt(station.transform.position);Physics.SyncTransforms();game.Player.RefreshFocus();
                    Check(game.Player.Focus==(IInteractable)station,"Authored equipment raycast "+job.id+" / "+station.id);
                    game.Tool=ToolMode.Inspect;game.Player.Focus.Interact(game);
                    game.Tool=ToolMode.Scanner;game.Player.Focus.Interact(game);
                    game.Tool=ToolMode.SignalProbe;game.Player.Focus.Interact(game);
                }
                if(job.hydraulic)
                {
                    Check(game.World.LeakVisual!=null && game.World.LeakVisual.activeSelf,"Faucet shows active leakage before intervention");
                    Capture(Path.Combine(directory,"08-restaurant-leak.png"));
                }
                game.Diagnose(job.cause);
                game.Tool=ToolMode.Isolate;game.World.Stations[0].Interact(game);
                game.Tool=ToolMode.Verify;game.World.Stations[(int)job.cause].Interact(game);
                game.ReturnToOffice();game.Resume();
                yield return null;
                Check(game.Session.Active.isolated && game.Session.Active.insulationTested,"Hub roundtrip preserves isolated authored visit");
                game.Tool=ToolMode.Repair;game.World.Stations[(int)job.cause].Interact(game);
                Check(game.Session.Active.repaired && !game.Session.Network.LightingHealthy,"Authored repair stays isolated");
                game.Tool=ToolMode.Restore;game.World.Stations[0].Interact(game);
                game.Tool=ToolMode.Verify;game.World.Stations[0].Interact(game);
                Check(!game.Session.Active.validated,"Authored job rejects premature stability test");
                yield return new WaitForSeconds(3.2f);
                game.World.Stations[0].Interact(game);
                Check(game.Session.Active.validated,"Authored job passes stable final test "+job.id);
                if(job.hydraulic)
                {
                    Check(!game.World.LeakVisual.activeSelf,"Reopened repaired faucet stops leakage");
                    var tap=game.World.Stations[2];
                    game.Player.Teleport(new Vector3(tap.transform.position.x,.01f,tap.transform.position.z-1.8f));
                    game.Player.AimAt(tap.transform.position);
                    Capture(Path.Combine(directory,"09-restaurant-repaired.png"));
                }
                game.Deliver();
                Check(game.AtOffice && game.Session.Career.completedChapterOneJobs.Count==jobIndex+1,"Chapter result registered once");
                yield return null;
            }
            var chapterSave=SaveService.Load(game.SavePath);
            Check(chapterSave.money==2980 && chapterSave.completed==7 && chapterSave.buildingHistory.Count==3 && chapterSave.recurringContractUnlocked,"Chapter payments, memories and Helena recommendation persisted");

            game.Accept();
            yield return null;
            Check(game.Session.IsFirstContract && game.World.CurrentLocationId=="recurringcondo","First recurring preventive contract loads indicated condominium");
            Check(game.World.LeakVisual==null,"Pump preventive uses dedicated blockout instead of faucet leakage");
            foreach(var station in game.World.Stations)
            {
                game.Tool=ToolMode.Inspect;station.Interact(game);
                game.Tool=ToolMode.Scanner;station.Interact(game);
                game.Tool=ToolMode.SignalProbe;station.Interact(game);
            }
            game.Diagnose(FailureCause.ControlRelay);
            game.Tool=ToolMode.Isolate;game.World.Stations[0].Interact(game);
            game.Tool=ToolMode.Verify;game.World.Stations[1].Interact(game);
            int pumpStockBefore=game.Session.Career.pumpKits;
            game.Tool=ToolMode.Repair;game.World.Stations[1].Interact(game);
            Check(game.Session.Active.repaired && game.Session.Career.pumpKits==pumpStockBefore-1,"Preventive pump kit is consumed only on confirmed intervention");
            game.Tool=ToolMode.Restore;game.World.Stations[0].Interact(game);
            game.Tool=ToolMode.Verify;game.World.Stations[0].Interact(game);
            Check(!game.Session.Active.validated,"Preventive contract rejects immediate final validation");
            yield return new WaitForSeconds(4.2f);
            game.World.Stations[0].Interact(game);
            Check(game.Session.Active.validated,"Preventive pump contract passes four-second stability test");
            game.Deliver();
            var contractSave=SaveService.Load(game.SavePath);
            Check(contractSave.firstContractCompleted && contractSave.preventiveRecommendationLogged && contractSave.money==3600 && contractSave.completed==8 && contractSave.buildingHistory.Count==4,"Preventive contract completion, payment and building history persist");

            var restaurant=Array.Find(game.Campaign.locations,location=>location.id=="restaurant");
            game.VisitPreview(restaurant);
            yield return null;
            Check(GameObject.Find("Histórico de manutenção")!=null,"Building remembers completed service in later preview");
            Check(game.Session.Career.money==3600,"History preview adds no duplicate payment");
            game.ReturnToOffice();
            var contractLocation=Array.Find(game.Campaign.locations,location=>location.id=="recurringcondo");
            game.VisitPreview(contractLocation);
            yield return null;
            Check(GameObject.Find("Histórico de manutenção")!=null,"Recurring condominium preserves preventive maintenance record");
            game.ReturnToOffice();
            File.WriteAllText(Path.Combine(directory, "PASSED.txt"), "Windows runtime smoke passed: three free-job causes, first-person camera, raycasts, collision, evidence, repair, lighting, final test, settlement, save/load. Campaign previews: " + floors + " floors / " + connections + " traversable door connections. Authored prologue: live thermal recurrence, tablet pause, isolation, blocked unsafe repair, restoration, thermal soak, mentor/client journal and persistent completion. Chapter I: three distinct locations, "+missionRoutes+" preserved door passages, equipment raycasts, isolated hub roundtrip, socket/lighting repairs, faucet leakage stopped after repair/reopening, independent hydraulic kit, payments, building memory and recurring-contract recommendation. Chapter II bridge: recurring condominium preventive pump contract, dedicated pump blockout, independent pump kit, four-second stability validation, persistent maintenance record and completion flag.\n" + DateTime.UtcNow.ToString("O"));
            Application.Quit(0);
        }
    }
}
