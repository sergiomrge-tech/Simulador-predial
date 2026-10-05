using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Development-only autopilot for the vertical slice (opt-in: <c>-worldSlice -worldSliceQaWalk</c> in a Development player, or the Play Mode gate in the
    /// Editor). It drives the real <see cref="FirstPersonController"/> CharacterController continuously along a route computed from the reference NavMesh
    /// (no teleport except the initial placement): in real time, with 60 Hz physics sub-steps, recentring on corridors/jambs, opening any closed door it
    /// meets with the real raycast + <c>[E]</c> path, and recording per-segment frame/memory/GC/streaming metrics and screenshots.
    /// </summary>
    public sealed class WorldSliceQaWalker : MonoBehaviour
    {
        [Serializable] public struct Vec3 { public float x, y, z; public Vector3 V => new Vector3(x, y, z); public Vec3(Vector3 v) { x = v.x; y = v.y; z = v.z; } }
        [Serializable] public sealed class Step
        {
            public string kind;        // teleport | walk | capture | interact | save | verifysave | tablet | mark | wait
            public string name;        // segment / capture name
            public string label;       // human text
            public Vec3[] corners;     // walk
            public Vec3 aim;           // capture / interact
            public float seconds;      // wait
            public float yaw;          // teleport
        }
        [Serializable] public sealed class Route { public int version; public string note; public Step[] steps; }
        [Serializable] public sealed class Hitch { public float ms; public string segment; public string cell; public Vec3 position; public int cellOps; }
        [Serializable] public sealed class Segment
        {
            public string name; public int frames; public float seconds, avgFps, minFps, avgFrameMs, p99FrameMs, maxFrameMs; public int over33ms, over50ms, over100ms;
            public int cellLoads, cellUnloads; public float usedMiB, reservedMiB; public long gcBytesPerFrameAvg, setPassAvg, trianglesAvg, trianglesMax, drawCallsAvg, batchesAvg;
            public bool drawCallsAvailable, batchesAvailable; public float distance;
            public string gcStatus, drawStatus, batchesStatus, setPassStatus, trianglesStatus;
        }
        [Serializable] public sealed class Report
        {
            public string status, failure, unityVersion, device, resolution, scope, savePath; public bool development;
            public int doorsOpenedByInteraction, tabletToggles, saveChecks, prompts; public string[] promptLog;
            public float totalSeconds, totalDistance, maxFloorGap; public int airborneFrames, maxAirborneStreak, penetrationFrames, stuckEvents;
            public int cellLoads, cellUnloads, maxLoadedCells; public double maxLoadMs, maxUnloadMs;
            public float minY, maxY; public Segment[] segments; public Hitch[] worstHitches; public string[] captures;
        }

        public Action<string, Vector3> CaptureHook;      // (file name, aim); default: ScreenCapture of the player's camera
        public string CaptureFolder;
        public string SummaryPath;
        public Report Result { get; private set; }
        public bool Finished { get; private set; }

        private const float Step60 = 1f / 60f;
        private const float WalkSpeed = 3f;
        private GameRuntime game; private WorldStreamService service; private WorldStreamingDebugOverlay overlay; private CharacterController body;
        private readonly List<float> segMs = new List<float>(4096);
        private readonly List<Segment> segments = new List<Segment>();
        private readonly List<Hitch> hitches = new List<Hitch>();
        private readonly List<string> prompts = new List<string>(), captureNames = new List<string>();
        private string segName = "start"; private double segGc, segSetPass, segTris, segDraw, segBatches; private long segTrisMax; private int segLoads0, segUnloads0; private float segT0, segDist;
        private float vertical; private int airborneStreak; private Vector3 lastPos;
        private int gcSamples, drawSamples, batchSamples, passSamples, triSamples;
        private float maxFloorGap, minY = 1e9f, maxY = -1e9f; private int airborne, maxStreak, penetration, stuck, doorOps, tabletToggles, saveChecks, prevLoads, prevUnloads, frameIndex;

        public IEnumerator Run(GameRuntime runtime, WorldStreamService streaming, WorldStreamingDebugOverlay debugOverlay, Route route)
        {
            game = runtime; service = streaming; overlay = debugOverlay; body = game.Player.GetComponent<CharacterController>();
            Result = new Report
            {
                unityVersion = Application.unityVersion, device = SystemInfo.graphicsDeviceName, resolution = Screen.width + "x" + Screen.height,
                development = Debug.isDebugBuild, savePath = game.SavePath, status = "RUNNING",
                scope = "Continuous walk driven frame by frame on the real CharacterController: Lar -> street -> Oficina -> street -> Horizonte (gate, lobby, stair, 4th floor, panel) -> out -> Mercearia -> back to the Lar."
            };
            game.Player.enabled = false;               // input only: controller, colliders, streaming, doors and renderer stay live
            BeginSegment("start");
            float started = Time.realtimeSinceStartup;
            foreach (Step step in route.steps)
            {
                IEnumerator run = null;
                switch (step.kind)
                {
                    case "accept": run = Accept(); break;
                    case "teleport": run = Teleport(step); break;
                    case "walk": run = Walk(step); break;
                    case "capture": run = Capture(step); break;
                    case "interact": run = InteractAt(step.aim.V, step.label); break;
                    case "save": run = Save(); break;
                    case "verifysave": run = VerifySave(step.label); break;
                    case "tablet": run = TabletCycle(); break;
                    case "wait": run = Wait(step.seconds); break;
                    case "mark": EndSegment(); BeginSegment(step.name); break;
                }
                if (run != null) yield return StartCoroutine(run);
                if (Result.failure != null) break;
            }
            EndSegment();
            Result.totalSeconds = Time.realtimeSinceStartup - started;
            Result.segments = segments.ToArray();
            hitches.Sort((a, b) => b.ms.CompareTo(a.ms));
            Result.worstHitches = hitches.GetRange(0, Mathf.Min(12, hitches.Count)).ToArray();
            Result.doorsOpenedByInteraction = doorOps; Result.tabletToggles = tabletToggles; Result.saveChecks = saveChecks; Result.prompts = prompts.Count; Result.promptLog = prompts.ToArray();
            Result.maxFloorGap = maxFloorGap; Result.airborneFrames = airborne; Result.maxAirborneStreak = maxStreak; Result.penetrationFrames = penetration; Result.stuckEvents = stuck;
            Result.cellLoads = service.TotalLoads; Result.cellUnloads = service.TotalUnloads; Result.maxLoadMs = service.MaxLoadMilliseconds; Result.maxUnloadMs = service.MaxUnloadMilliseconds;
            Result.minY = minY; Result.maxY = maxY; Result.captures = captureNames.ToArray();
            foreach (var s in segments) Result.totalDistance += s.distance;
            if (Result.failure == null) Result.status = "PASS"; else Result.status = "FAIL";
            string json = JsonUtility.ToJson(Result, true);
            if (!string.IsNullOrEmpty(SummaryPath)) { Directory.CreateDirectory(Path.GetDirectoryName(SummaryPath)); File.WriteAllText(SummaryPath, json); }
            Debug.Log("WORLD WALK DONE: " + Result.status + " " + (Result.failure ?? ""));
            Finished = true;
        }

        // ------------------------------------------------------------------------------------------------ walking
        private IEnumerator Walk(Step step)
        {
            Vector3[] pts = Array.ConvertAll(step.corners, c => c.V);
            for (int i = 1; i < pts.Length; i++)
            {
                Vector3 from = i == 1 ? game.Player.transform.position : pts[i - 1];
                int pieces = Mathf.Max(1, Mathf.CeilToInt(Vector3.Distance(from, pts[i]) / .5f));
                for (int k = 1; k <= pieces; k++)
                {
                    Vector3 target = Vector3.Lerp(from, pts[i], k / (float)pieces);
                    if (k < pieces) target = Centre(target, pts[i] - from);
                    yield return StartCoroutine(WalkTo(target, k == pieces && i == pts.Length - 1 ? .3f : .28f));
                    if (Result.failure != null) yield break;
                }
            }
        }

        private IEnumerator WalkTo(Vector3 target, float reach)
        {
            float bestRemaining = float.MaxValue, lastProgress = Time.realtimeSinceStartup;
            while (true)
            {
                Vector3 position = game.Player.transform.position;
                Vector3 flat = target - position; flat.y = 0f;
                if (flat.magnitude < reach && Mathf.Abs(target.y - position.y) < 1.3f) yield break;
                if (flat.magnitude < bestRemaining - .3f) { bestRemaining = flat.magnitude; lastProgress = Time.realtimeSinceStartup; }
                else if (Time.realtimeSinceStartup - lastProgress > 12f)
                {
                    stuck++;
                    Result.failure = "No progress for 12 s at " + position.ToString("F2") + " toward " + target.ToString("F2") + " in segment " + segName;
                    yield break;
                }
                if (position.y < minY) minY = position.y;
                if (position.y > maxY) maxY = position.y;
                if (position.y < target.y - 6f) { Result.failure = "Player fell " + (target.y - position.y).ToString("F1") + " m below the route at " + position.ToString("F2") + " (" + segName + ")"; yield break; }
                // A closed door ahead is opened the way a player does: aim at it, read the prompt, press [E].
                if (TryFindClosedDoorAhead(position, flat.normalized, out WorldDoor door, out Vector3 hitPoint))
                {
                    yield return StartCoroutine(InteractAt(hitPoint, "door ahead: " + door.DoorId, door.GetComponent<Collider>()));
                    float wait = Time.realtimeSinceStartup;
                    while (door.IsMoving && Time.realtimeSinceStartup - wait < 5f) yield return null;
                    if (Result.failure != null) yield break;
                    continue;
                }
                if (!GroundAhead(position, flat.normalized))               // streaming must have the floor in place before the player reaches it
                {
                    float wait = Time.realtimeSinceStartup;
                    while (!GroundAhead(game.Player.transform.position, flat.normalized) && Time.realtimeSinceStartup - wait < 20f) { yield return null; RecordFrame(); }
                    if (!GroundAhead(game.Player.transform.position, flat.normalized)) { Result.failure = "No floor ahead (cell not streamed in) at " + position.ToString("F2"); yield break; }
                }
                float dt = Mathf.Min(Time.deltaTime, .1f);
                int sub = Mathf.Clamp(Mathf.RoundToInt(dt / Step60), 1, 6);
                for (int s = 0; s < sub; s++) SubStep(flat.normalized);
                RecordFrame();
                yield return null;
            }
        }

        private void SubStep(Vector3 direction)
        {
            if (direction.sqrMagnitude > 0f)
                game.Player.transform.rotation = Quaternion.RotateTowards(game.Player.transform.rotation, Quaternion.LookRotation(direction), 360f * Step60);
            if (body.isGrounded && vertical < 0) vertical = -2f;
            vertical -= 20f * Step60;
            body.Move((direction * WalkSpeed + Vector3.up * vertical) * Step60);
            if (body.isGrounded) airborneStreak = 0; else { airborne++; airborneStreak++; maxStreak = Mathf.Max(maxStreak, airborneStreak); }
            Vector3 now = game.Player.transform.position;
            segDist += Vector3.Distance(lastPos, now); lastPos = now;
            if (Physics.Raycast(now + Vector3.up * .6f, Vector3.down, out var floor, 1.5f, ~0, QueryTriggerInteraction.Ignore)) maxFloorGap = Mathf.Max(maxFloorGap, now.y - floor.point.y);
            var overlaps = Physics.OverlapCapsule(now + Vector3.up * .45f, now + Vector3.up * 1.4f, .2f, ~0, QueryTriggerInteraction.Ignore);
            foreach (var hit in overlaps) if (hit != body && !hit.isTrigger && hit.GetComponentInParent<WorldDoor>() == null) { penetration++; break; }
        }

        private bool TryFindClosedDoorAhead(Vector3 position, Vector3 direction, out WorldDoor door, out Vector3 hitPoint)
        {
            door = null; hitPoint = default;
            if (direction.sqrMagnitude < .01f) return false;
            if (!Physics.SphereCast(position + Vector3.up * .8f, .22f, direction, out var hit, 1.5f, ~0, QueryTriggerInteraction.Ignore)) return false;
            door = hit.collider.GetComponentInParent<WorldDoor>();
            if (door == null || door.IsOpen || door.IsMoving) { door = null; return false; }
            hitPoint = hit.point; return true;
        }
        private static bool GroundAhead(Vector3 position, Vector3 direction)
        {
            Vector3 probe = position + direction * 1.2f;
            return Physics.Raycast(probe + Vector3.up * .8f, Vector3.down, 30f, ~0, QueryTriggerInteraction.Ignore);   // deep enough to see the ground floor under the open stairwell
        }
        // A player does not hug jambs: push the point toward the middle of the free space (capped), exactly like the Play Mode gate's walker.
        private static Vector3 Centre(Vector3 p, Vector3 along)
        {
            along.y = 0f;
            if (along.sqrMagnitude < .01f) return p;
            Vector3 side = Vector3.Cross(Vector3.up, along.normalized);
            float left = Clear(p, -side), right = Clear(p, side);
            const float want = .45f; float shift = 0f;
            if (left < want && right > left) shift = Mathf.Min(want - left, (right - left) * .5f, .3f);
            else if (right < want && left > right) shift = -Mathf.Min(want - right, (left - right) * .5f, .3f);
            return p + side * shift;
        }
        private static float Clear(Vector3 p, Vector3 d)
        {
            float best = 1.2f;
            foreach (float h in new[] { .45f, 1.0f, 1.6f })
                if (Physics.Raycast(p + Vector3.up * h, d, out var hit, 1.2f, ~0, QueryTriggerInteraction.Ignore) && hit.collider.GetComponentInParent<WorldDoor>() == null) best = Mathf.Min(best, hit.distance);
            return best;
        }

        // ------------------------------------------------------------------------------------------------ steps
        private IEnumerator Accept()
        {
            // Same precondition as the Editor gates: the prologue contract is accepted, which makes the bridge route the player to the Horizonte; the walk
            // then places the player back at the Lar and walks everything else.
            game.Accept();
            yield return null;
            float deadline = Time.realtimeSinceStartup + 60f;
            while (game.World != null && game.World.Root != null && game.World.Root.activeSelf && Time.realtimeSinceStartup < deadline) yield return null;
            yield return new WaitForSeconds(2f);
        }
        private IEnumerator Teleport(Step step)
        {
            Vector3 p = step.corners[0].V;
            var cell = WorldStreamingId.FromWorldPosition(p.x, p.z);
            service.StreamingEnabled = false; service.Refresh(cell);
            float deadline = Time.realtimeSinceStartup + 60f;
            while (!service.IsLoaded(cell) && Time.realtimeSinceStartup < deadline) yield return null;
            if (!service.IsLoaded(cell)) { Result.failure = "Start cell did not load: " + cell.Name; yield break; }
            game.Player.Teleport(p, step.yaw); vertical = 0f; Physics.SyncTransforms(); lastPos = game.Player.transform.position;
            service.StreamingEnabled = true;
            yield return StartCoroutine(Settle());
            yield return new WaitForSeconds(3f);           // let the 3x3 ring stream in before the walk starts
        }
        private IEnumerator Settle()
        {
            for (int i = 0; i < 90; i++)
            {
                if (body.isGrounded && vertical < 0) vertical = -2f;
                vertical -= 20f * Step60; body.Move(Vector3.up * vertical * Step60);
                RecordFrame(); yield return null;
            }
            if (!body.isGrounded) Result.failure = "Initial placement is not on the ground";
            lastPos = game.Player.transform.position;
        }
        private IEnumerator Wait(float seconds)
        {
            float t = Time.realtimeSinceStartup;
            while (Time.realtimeSinceStartup - t < seconds) { RecordFrame(); yield return null; }
        }
        private IEnumerator InteractAt(Vector3 aim, string label, Collider target = null)
        {
            Vector3 flat = aim - game.Player.transform.position; flat.y = 0f;
            if (flat.sqrMagnitude > .01f) game.Player.transform.rotation = Quaternion.LookRotation(flat);
            // A player looks at the middle of the door/panel, not at the spot the walker's sweep touched: try the touch point, then the target's centre and upper body.
            var aims = new List<Vector3> { aim };
            if (target != null) { Bounds b = target.bounds; aims.Add(new Vector3(b.center.x, b.min.y + 1.2f, b.center.z)); aims.Add(new Vector3(b.center.x, b.min.y + 1.6f, b.center.z)); aims.Add(b.center); }
            string seen = "";
            foreach (Vector3 candidate in aims)
            {
                game.Player.AimAt(candidate);
                yield return null;
                game.Player.RefreshFocus();
                if (game.Player.Focus != null) break;
                Transform cam = game.Player.view.transform;
                seen += (Physics.Raycast(cam.position, cam.forward, out var blocker, 3, ~(1 << 2)) ? blocker.collider.name : "nothing") + "; ";
            }
            if (game.Player.Focus == null) { Result.failure = "Nothing interactable in the crosshair at " + aim.ToString("F2") + " (" + label + "); rays hit: " + seen; yield break; }
            string prompt = game.Player.Focus.GetPrompt(game.Tool);
            if (string.IsNullOrEmpty(prompt)) { yield return new WaitForSeconds(.8f); prompt = game.Player.Focus.GetPrompt(game.Tool); }
            prompts.Add(label + " => " + prompt);
            bool door = game.Player.Focus is WorldDoor || game.Player.Focus is WorldDoorRemote;
            game.Player.Focus.Interact(game);
            if (door) doorOps++;
            game.Player.view.transform.localRotation = Quaternion.identity;
            RecordFrame();
        }
        private IEnumerator Capture(Step step)
        {
            if (string.IsNullOrEmpty(CaptureFolder) && CaptureHook == null) yield break;
            game.Player.AimAt(step.aim.V);
            yield return new WaitForSeconds(.4f);
            string file = step.name + ".png";
            if (CaptureHook != null) CaptureHook(file, step.aim.V);
            else
            {
                Directory.CreateDirectory(CaptureFolder);
                yield return new WaitForEndOfFrame();
                ScreenCapture.CaptureScreenshot(Path.Combine(CaptureFolder, file));
                yield return null; yield return null;
            }
            captureNames.Add(file);
            game.Player.view.transform.localRotation = Quaternion.identity;
        }
        private IEnumerator Save()
        {
            game.Save();
            if (!string.IsNullOrEmpty(game.SaveError)) Result.failure = "Save failed: " + game.SaveError;
            yield return null;
        }
        private IEnumerator VerifySave(string label)
        {
            // The file written by SaveService must read back (validation + .bak policy included) to exactly the in-memory career.
            string memory = Comparable(game.Session.Career);
            CareerData loaded;
            try { loaded = SaveService.Load(game.SavePath); }
            catch (Exception e) { Result.failure = "Save did not load back (" + label + "): " + e.Message; yield break; }
            string disk = Comparable(loaded);
            if (memory != disk) { Result.failure = "Loaded career differs from memory (" + label + ")"; yield break; }
            new ServiceSession(loaded);                                                         // a new session accepts it, as a restart would
            saveChecks++;
        }
        // The running service clock keeps ticking between the write and the read-back, so it is the one field compared out of the snapshot.
        private static string Comparable(CareerData career)
        {
            var copy = JsonUtility.FromJson<CareerData>(JsonUtility.ToJson(career));
            if (copy.active != null) copy.active.elapsed = 0f;
            return JsonUtility.ToJson(copy);
        }
        private IEnumerator TabletCycle()
        {
            game.SetTablet(true); tabletToggles++;
            yield return new WaitForSeconds(.6f);
            if (!game.TabletOpen) { Result.failure = "Tablet did not open"; yield break; }
            Vector3 before = game.Player.transform.position;
            yield return new WaitForSeconds(.4f);
            if (Vector3.Distance(before, game.Player.transform.position) > .05f) { Result.failure = "Player moved while the tablet was open"; yield break; }
            game.SetTablet(false); tabletToggles++;
            yield return new WaitForSeconds(.3f);
            if (game.TabletOpen) Result.failure = "Tablet did not close";
        }

        // ------------------------------------------------------------------------------------------------ metrics
        private void BeginSegment(string name)
        {
            segName = name; segMs.Clear(); segGc = segSetPass = segTris = segDraw = segBatches = 0; segTrisMax = 0; segDist = 0f;
            gcSamples = drawSamples = batchSamples = passSamples = triSamples = 0;
            segLoads0 = service.TotalLoads; segUnloads0 = service.TotalUnloads; segT0 = Time.realtimeSinceStartup; prevLoads = segLoads0; prevUnloads = segUnloads0;
        }
        private void RecordFrame()
        {
            float ms = Time.unscaledDeltaTime * 1000f;
            frameIndex++;
            if (frameIndex < 2) return;
            segMs.Add(ms);
            if (overlay.GcBytesLastFrame >= 0) { segGc += overlay.GcBytesLastFrame; gcSamples++; }
            if (overlay.SetPassCallsLastFrame >= 0) { segSetPass += overlay.SetPassCallsLastFrame; passSamples++; }
            if (overlay.DrawCallsLastFrame >= 0) { segDraw += overlay.DrawCallsLastFrame; drawSamples++; }
            if (overlay.BatchesLastFrame >= 0) { segBatches += overlay.BatchesLastFrame; batchSamples++; }
            if (overlay.VisibleTrianglesLastFrame >= 0) { segTris += overlay.VisibleTrianglesLastFrame; triSamples++; segTrisMax = Math.Max(segTrisMax, overlay.VisibleTrianglesLastFrame); }
            int ops = (service.TotalLoads - prevLoads) + (service.TotalUnloads - prevUnloads);
            prevLoads = service.TotalLoads; prevUnloads = service.TotalUnloads;
            Result.maxLoadedCells = Mathf.Max(Result.maxLoadedCells, service.LoadedCells.Count);
            if (ms > 33.4f)
            {
                var hitch = new Hitch { ms = ms, segment = segName, cell = service.HasCurrentCell ? service.CurrentCell.Name : "n/a", position = new Vec3(game.Player.transform.position), cellOps = ops };
                if (hitches.Count < 12) hitches.Add(hitch);
                else
                {
                    int smallest = 0;
                    for (int i = 1; i < hitches.Count; i++) if (hitches[i].ms < hitches[smallest].ms) smallest = i;
                    if (ms > hitches[smallest].ms) hitches[smallest] = hitch;
                }
            }
        }
        private void EndSegment()
        {
            if (segMs.Count == 0) return;
            var sorted = new List<float>(segMs); sorted.Sort();
            float total = 0f; foreach (float f in segMs) total += f;
            int n = segMs.Count;
            var seg = new Segment
            {
                name = segName, frames = n, seconds = Time.realtimeSinceStartup - segT0, avgFrameMs = total / n, avgFps = n * 1000f / Mathf.Max(1f, total),
                maxFrameMs = sorted[n - 1], minFps = 1000f / Mathf.Max(1f, sorted[n - 1]), p99FrameMs = sorted[Mathf.Min(n - 1, Mathf.CeilToInt(n * .99f) - 1)],
                cellLoads = service.TotalLoads - segLoads0, cellUnloads = service.TotalUnloads - segUnloads0,
                usedMiB = overlay.AllocatedMemoryBytes / 1048576f, reservedMiB = overlay.ReservedMemoryBytes / 1048576f,
                gcBytesPerFrameAvg = Mean(segGc, gcSamples), setPassAvg = Mean(segSetPass, passSamples), trianglesAvg = Mean(segTris, triSamples), trianglesMax = triSamples > 0 ? segTrisMax : -1,
                drawCallsAvg = Mean(segDraw, drawSamples), batchesAvg = Mean(segBatches, batchSamples), distance = segDist,
                gcStatus = Status(gcSamples), drawStatus = Status(drawSamples), batchesStatus = Status(batchSamples), setPassStatus = Status(passSamples), trianglesStatus = Status(triSamples)
            };
            foreach (float f in segMs) { if (f > 33.4f) seg.over33ms++; if (f > 50f) seg.over50ms++; if (f > 100f) seg.over100ms++; }
            seg.drawCallsAvailable = segDraw > 0; seg.batchesAvailable = segBatches > 0;
            segments.Add(seg);
        }
        private static long Mean(double sum, int count) => count > 0 ? (long)(sum / count) : -1;
        private static string Status(int count) => count > 0 ? "MEDIDO" : "INDISPONÍVEL";
    }
}
