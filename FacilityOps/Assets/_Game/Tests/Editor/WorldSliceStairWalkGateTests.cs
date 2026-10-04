using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using FacilityOps.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.TestTools;

namespace FacilityOps.Tests
{
    // Walks the real FirstPersonController CharacterController (radius .28, height 1.8, default step/slope limits) from the street in
    // front of the Horizonte to the technical panel on the 4th floor, over the authored stairs and colliders. The NavMesh reference
    // only supplies the line to follow; it never moves the player and no collider, link or teleport is added to make this pass.
    public sealed class ControllerHitSpy : MonoBehaviour
    {
        public readonly List<string> Hits = new List<string>();
        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            string line = hit.collider.name + " p=" + hit.point.ToString("F3") + " n=" + hit.normal.ToString("F2") + " move=" + hit.moveDirection.ToString("F2");
            if (Hits.Count == 0 || Hits[Hits.Count - 1] != line) { Hits.Add(line); if (Hits.Count > 40) Hits.RemoveAt(0); }
        }
    }

    public sealed class WorldSliceStairWalkGateTests
    {
        [Serializable] public sealed class Milestone { public string name; public float seconds; public Vector3 position; }
        [Serializable] public sealed class Report
        {
            public string status, fingerprint, unityVersion, device, scope, interaction, failure;
            public int pathCorners, frames, airborneFrames, maxAirborneStreak, penetrationFrames, stuckWindows;
            public float pathLength, seconds, maxFloorGap, finalDistanceToTarget, maxHeight;
            public Vector3 start, target, end;
            public Milestone[] milestones;
        }

        // Fixed 60 Hz simulation step: the Editor test frame takes 50-75 ms (renders, streaming), which would make a 3 m/s walker take 20 cm
        // sweeps and behave unlike the shipped game at 60+ fps.
        private const float Step = 1f / 60f;

        [UnityTest, Timeout(900000)]
        public IEnumerator Horizonte_Street_To_Quadro_Over_Authored_Stairs_With_CharacterController()
        {
            if (Environment.GetEnvironmentVariable("FACILITY_STAIR_QA") != "1")
                Assert.Ignore("Opt-in: FACILITY_STAIR_QA=1 with -worldSlice -worldSliceQa after ImportPilot and WorldSliceWalkabilityQa.BuildReference.");
            EditorSceneManager.OpenScene(WorldSliceBootstrapScaffolder.SliceBootstrap, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            var bridge = UnityEngine.Object.FindAnyObjectByType<WorldSliceRuntimeBridge>();
            var game = UnityEngine.Object.FindAnyObjectByType<GameRuntime>();
            var service = UnityEngine.Object.FindAnyObjectByType<WorldStreamService>();
            var overlay = UnityEngine.Object.FindAnyObjectByType<WorldStreamingDebugOverlay>();
            var report = new Report
            {
                unityVersion = Application.unityVersion, device = SystemInfo.graphicsDeviceName,
                scope = "Unity Editor Play Mode: FirstPersonController CharacterController driven frame by frame (3 m/s, gravity -20) along the street->panel line over authored colliders. Editor, not a standalone benchmark."
            };
            float deadline = Time.realtimeSinceStartup + 60f;
            while (!bridge.Active && Time.realtimeSinceStartup < deadline) yield return null;
            Assert.That(bridge.Active, Is.True, "Initial streamed cell timed out");
            game.Player.enabled = false; // input only; the controller, colliders, streaming and renderer stay live
            var controller = game.Player.GetComponent<CharacterController>();
            // Same precondition as the original runtime gate: the prologue contract is accepted, so the panel binds to the original QD-01 logic.
            // The route teleport that Accept triggers is only a starting condition; the player is then placed on the street and walks.
            game.Accept();
            yield return null;
            deadline = Time.realtimeSinceStartup + 45f;
            while (game.World.Root.activeSelf && Time.realtimeSinceStartup < deadline) yield return null;
            Assert.That(game.World.Root.activeSelf, Is.False, "Prologue context did not finish streaming route");
            var horizonte = WorldSliceDestinationRegistry.Require("horizonte");
            service.StreamingEnabled = false; service.Refresh(horizonte.Cell);
            deadline = Time.realtimeSinceStartup + 60f;
            while (!service.IsLoaded(horizonte.Cell) && Time.realtimeSinceStartup < deadline) yield return null;
            Assert.That(service.IsLoaded(horizonte.Cell), Is.True, "Horizonte cell missing");
            WorldGameplayMarker panel = null;
            foreach (var marker in UnityEngine.Object.FindObjectsByType<WorldGameplayMarker>(FindObjectsSortMode.None))
                if (marker.MarkerName.EndsWith("GP_quadro_tecnico", StringComparison.Ordinal)) panel = marker;
            Assert.That(panel, Is.Not.Null, "GP_quadro_tecnico missing");
            game.Player.Teleport(horizonte.FallbackPosition, 0f);
            service.StreamingEnabled = true;
            yield return Settle(controller);
            Assert.That(controller.isGrounded, Is.True, "Street floor missing in front of the Horizonte");

            // This gate isolates the stair geometry; the doors are authored closed, so they are put in their open pose here. Door interaction
            // (closed leaf blocks, [E] opens, never traps) is exercised by the continuous-walk gate, which operates them through the real prompt.
            foreach (var door in WorldDoor.All) door.SetOpenImmediate(true);
            yield return null;
            var navData = AssetDatabase.LoadAssetAtPath<NavMeshData>(WorldSliceWalkabilityQa.NavAsset);
            Assert.That(navData, Is.Not.Null, "Run WorldSliceWalkabilityQa.BuildReference first");
            var navInstance = NavMesh.AddNavMeshData(navData);
            Vector3 target = panel.transform.position + panel.transform.forward - Vector3.up * 1.4f;
            Vector3 start = game.Player.transform.position;
            var path = new NavMeshPath();
            bool a = NavMesh.SamplePosition(start, out var sa, 3f, NavMesh.AllAreas), b = NavMesh.SamplePosition(target, out var sb, 3f, NavMesh.AllAreas);
            Assert.That(a && b && NavMesh.CalculatePath(sa.position, sb.position, NavMesh.AllAreas, path) && path.status == NavMeshPathStatus.PathComplete,
                Is.True, "Reference path street->panel is not complete");
            Vector3[] corners = path.corners; // read before removing the NavMesh: corners are evaluated lazily
            navInstance.Remove();
            corners = Centre(corners);
            report.pathCorners = corners.Length; report.start = start; report.target = target;
            for (int i = 0; i + 1 < corners.Length; i++) report.pathLength += Vector3.Distance(corners[i], corners[i + 1]);

            var milestones = new List<Milestone>();
            bool shotBase = false, shotMid = false, shotArrive = false, shotTop = false;
            float baseY = start.y, vertical = 0f, startedAt = Time.realtimeSinceStartup;
            int index = 1, airborne = 0, streak = 0;
            float lastProgressRemaining = report.pathLength, simTime = 0f, lastProgressTime = 0f;
            deadline = Time.realtimeSinceStartup + 240f;
            var self = controller;
            var spy = game.Player.gameObject.AddComponent<ControllerHitSpy>();
            Capture(game.Player.view, start + Vector3.up * 1.4f + Vector3.forward * 12f, "horizonte-exterior-walk-runtime.png");
            while (index < corners.Length && Time.realtimeSinceStartup < deadline)
            {
                Vector3 position = game.Player.transform.position;
                Vector3 flat = corners[index] - position; flat.y = 0f;
                bool last = index == corners.Length - 1;
                if (flat.magnitude < (last ? .3f : .25f) && Mathf.Abs(corners[index].y - position.y) < 1.3f) { index++; continue; }
                Vector3 direction = flat.normalized;
                if (direction.sqrMagnitude > 0f)
                    game.Player.transform.rotation = Quaternion.RotateTowards(game.Player.transform.rotation, Quaternion.LookRotation(direction), 360f * Step);
                if (controller.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * Step;
                controller.Move((direction * 3f + Vector3.up * vertical) * Step);
                report.frames++; simTime += Step;
                if (controller.isGrounded) streak = 0; else { airborne++; streak++; report.maxAirborneStreak = Mathf.Max(report.maxAirborneStreak, streak); }
                Vector3 now = game.Player.transform.position;
                report.maxHeight = Mathf.Max(report.maxHeight, now.y - baseY);
                if (Physics.Raycast(now + Vector3.up * .6f, Vector3.down, out var floor, 1.5f, ~0, QueryTriggerInteraction.Ignore))
                    report.maxFloorGap = Mathf.Max(report.maxFloorGap, now.y - floor.point.y);
                var overlaps = Physics.OverlapCapsule(now + Vector3.up * .45f, now + Vector3.up * 1.4f, .2f, ~0, QueryTriggerInteraction.Ignore);
                foreach (var hit in overlaps) if (hit != self && !hit.isTrigger) { report.penetrationFrames++; break; }
                float remaining = Vector3.Distance(now, corners[index]);
                for (int i = index; i + 1 < corners.Length; i++) remaining += Vector3.Distance(corners[i], corners[i + 1]);
                if (remaining < lastProgressRemaining - .5f) { lastProgressRemaining = remaining; lastProgressTime = simTime; }
                else if (simTime - lastProgressTime > 6f)
                {
                    report.stuckWindows++;
                    var near = new List<string>();
                    foreach (var hit in Physics.OverlapCapsule(now + Vector3.up * .45f, now + Vector3.up * 1.4f, .5f, ~0, QueryTriggerInteraction.Ignore))
                        if (hit != self) near.Add(hit.name + "@" + hit.bounds.min.ToString("F2") + ".." + hit.bounds.max.ToString("F2"));
                    var dirNow = corners[index] - now; dirNow.y = 0f; dirNow.Normalize();
                    foreach (var cast in Physics.CapsuleCastAll(now + Vector3.up * .28f, now + Vector3.up * 1.52f, .28f, dirNow, .4f, ~0, QueryTriggerInteraction.Ignore))
                        near.Add("CAST " + cast.collider.name + " d=" + cast.distance.ToString("F3") + " p=" + cast.point.ToString("F3") + " n=" + cast.normal.ToString("F2"));
                    for (float dx = -.35f; dx <= .351f; dx += .07f)
                    {
                        var row = new List<string>();
                        foreach (float h in new[] { .05f, .15f, .3f, .6f, .9f, 1.3f, 1.7f })
                            row.Add(Physics.Raycast(now + new Vector3(dx, h, 0f), Vector3.forward, out var rh, .8f, ~0, QueryTriggerInteraction.Ignore)
                                ? (rh.collider.name.Replace("EXPORT_W2_horizonte__", "") + ":" + rh.distance.ToString("F2")) : "-");
                        near.Add("RAYROW dx=" + dx.ToString("F2") + " heights(.05,.15,.3,.6,.9,1.3,1.7): " + string.Join(", ", row));
                    }
                    foreach (var probe in new[] { Vector3.forward, new Vector3(-1, 0, 1).normalized, Vector3.left, new Vector3(-1, 0, -1).normalized, Vector3.back, new Vector3(1, 0, -1).normalized, Vector3.right, new Vector3(1, 0, 1).normalized })
                    {
                        Vector3 before = game.Player.transform.position;
                        var flags = controller.Move(probe * .05f);
                        near.Add("PROBE " + probe.ToString("F2") + " moved=" + (game.Player.transform.position - before).ToString("F3") + " flags=" + flags);
                    }
                    near.Add("CC h=" + controller.height + " c=" + controller.center + " r=" + controller.radius + " bounds=" + controller.bounds.min.ToString("F3") + ".." + controller.bounds.max.ToString("F3") + " pos=" + game.Player.transform.position.ToString("F3") + " scale=" + game.Player.transform.lossyScale);
                    near.Add("LASTHITS " + string.Join(" // ", spy.Hits.GetRange(Mathf.Max(0, spy.Hits.Count - 6), Mathf.Min(6, spy.Hits.Count))));
                    near.Add("flags=" + controller.Move(dirNow * .02f) + " skin=" + controller.skinWidth + " step=" + controller.stepOffset + " slope=" + controller.slopeLimit + " minMove=" + controller.minMoveDistance + " dir=" + dirNow.ToString("F2"));
                    report.failure = "No progress for 6 simulated s at " + now.ToString("F2") + " heading to corner " + index + " " + corners[index].ToString("F2") + "; colliders within .5 m: " + string.Join(" | ", near);
                    break;
                }
                float rise = now.y - baseY; Vector3 ahead = corners[Mathf.Min(corners.Length - 1, index + 10)] + Vector3.up * 1.3f;   // look along the route (up the flight), not at the wall
                if (!shotBase && rise > .15f && rise < 1f && Mathf.Abs(now.x + 2347f) < 3f && now.z > -1800f) { shotBase = true; Capture(game.Player.view, ahead, "horizonte-escada-base-runtime.png"); milestones.Add(Mark("escada: primeiros degraus", simTime, now)); }
                if (!shotMid && rise > 2.3f) { shotMid = true; Capture(game.Player.view, ahead, "horizonte-escada-meio-runtime.png"); milestones.Add(Mark("escada: patamar do 1º andar (meio da subida)", simTime, now)); }
                if (!shotArrive && rise > 4.2f) { shotArrive = true; Capture(game.Player.view, ahead, "horizonte-escada-1andar-runtime.png"); milestones.Add(Mark("chegada ao 1º pavimento", simTime, now)); }
                if (!shotTop && rise > 9.7f) { shotTop = true; Capture(game.Player.view, ahead, "horizonte-escada-topo-runtime.png"); milestones.Add(Mark("chegada ao piso do prólogo (4º andar)", simTime, now)); }
                yield return null;
            }
            report.airborneFrames = airborne;
            report.seconds = simTime;
            report.end = game.Player.transform.position;
            report.finalDistanceToTarget = Vector3.Distance(new Vector3(report.end.x, 0, report.end.z), new Vector3(target.x, 0, target.z));
            report.milestones = milestones.ToArray();
            yield return Settle(controller);

            game.Player.AimAt(panel.transform.position);
            game.Player.RefreshFocus();
            report.interaction = game.Player.Focus?.GetType().Name ?? "NONE";
            string notice = null;
            if (game.Player.Focus != null) { game.Player.Focus.Interact(game); notice = game.Notice; }
            Capture(game.Player.view, panel.transform.position, "horizonte-panel-stair-walk-runtime.png");
            report.fingerprint = WorldSliceBuildGate.Fingerprint();
            bool reached = index >= corners.Length && report.finalDistanceToTarget < .6f && controller.isGrounded && report.end.y - baseY > 9.7f;
            bool clean = report.penetrationFrames == 0 && report.maxAirborneStreak <= 40 && report.maxFloorGap < .7f && report.stuckWindows == 0;
            report.status = reached && clean && report.interaction != "NONE" && notice != null && notice.Contains("QD-01") ? "PASS" : "FAIL";
            string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Logs"));
            Directory.CreateDirectory(folder);
            File.WriteAllText(Path.Combine(folder, "world-stair-walk-qa.json"), JsonUtility.ToJson(report, true));
            Debug.Log("WORLD STAIR WALK QA: " + report.status + " " + JsonUtility.ToJson(report));
            yield return new ExitPlayMode();
            Assert.That(reached, Is.True, "Did not reach the panel on foot: " + report.failure + " end=" + report.end);
            Assert.That(report.penetrationFrames, Is.EqualTo(0), "Player capsule penetrated authored colliders");
            Assert.That(report.maxAirborneStreak, Is.LessThanOrEqualTo(40), "CharacterController lost ground contact on the route");
            Assert.That(report.maxFloorGap, Is.LessThan(.7f), "CharacterController floated above the floor");
            Assert.That(report.stuckWindows, Is.EqualTo(0));
            Assert.That(report.interaction, Is.Not.EqualTo("NONE"));
            Assert.That(notice, Does.Contain("QD-01"));
        }

        // A player does not hug jambs: resample the reference line every .5 m and push each point toward the middle of the free space
        // (side rays at three heights, shift capped at .3 m), so the CharacterController's skin-inflated capsule keeps clear of door frames.
        private static Vector3[] Centre(Vector3[] corners)
        {
            var points = new List<Vector3> { corners[0] };
            for (int i = 0; i + 1 < corners.Length; i++)
            {
                Vector3 a = corners[i], b = corners[i + 1];
                int n = Mathf.Max(1, Mathf.CeilToInt(Vector3.Distance(a, b) / .5f));
                for (int k = 1; k <= n; k++)
                {
                    Vector3 p = Vector3.Lerp(a, b, k / (float)n);
                    Vector3 along = b - a; along.y = 0f;
                    if (k < n && along.sqrMagnitude > .01f)
                    {
                        Vector3 side = Vector3.Cross(Vector3.up, along.normalized);
                        float left = Clearance(p, -side), right = Clearance(p, side);
                        const float want = .45f;
                        float shift = 0f;
                        if (left < want && right > left) shift = Mathf.Min(want - left, (right - left) * .5f, .3f);
                        else if (right < want && left > right) shift = -Mathf.Min(want - right, (left - right) * .5f, .3f);
                        p += side * shift;
                    }
                    points.Add(p);
                }
            }
            return points.ToArray();
        }
        private static float Clearance(Vector3 p, Vector3 direction)
        {
            float best = 1.2f;
            foreach (float h in new[] { .45f, 1.0f, 1.6f })
                if (Physics.Raycast(p + Vector3.up * h, direction, out var hit, 1.2f, ~0, QueryTriggerInteraction.Ignore)) best = Mathf.Min(best, hit.distance);
            return best;
        }
        private static Milestone Mark(string name, float seconds, Vector3 position) => new Milestone { name = name, seconds = seconds, position = position };
        private static IEnumerator Settle(CharacterController controller)
        {
            Physics.SyncTransforms(); float vertical = 0f;
            for (int i = 0; i < 90; i++)
            {
                if (controller.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * .02f; controller.Move(Vector3.up * vertical * .02f);
                yield return null;
            }
        }
        private static void Capture(Camera camera, Vector3 aim, string file)
        {
            camera.transform.LookAt(aim); camera.ResetWorldToCameraMatrix(); camera.ResetProjectionMatrix();
            Canvas.ForceUpdateCanvases();
            var target = new RenderTexture(1280, 720, 24, RenderTextureFormat.ARGB32); target.Create();
            var previous = RenderTexture.active;
            var image = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            try
            {
                RenderPipeline.SubmitRenderRequest(camera, new UniversalRenderPipeline.SingleCameraRequest { destination = target });
                RenderTexture.active = target; image.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); image.Apply();
                string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Docs/Previews/UnityValidation"));
                Directory.CreateDirectory(folder); File.WriteAllBytes(Path.Combine(folder, file), image.EncodeToPNG());
            }
            finally { RenderTexture.active = previous; target.Release(); UnityEngine.Object.Destroy(target); UnityEngine.Object.Destroy(image); }
        }
    }
}
