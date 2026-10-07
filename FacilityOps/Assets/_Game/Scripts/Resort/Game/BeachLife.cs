using System.Collections.Generic;
using ResortAurora.Site;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Ambient population of the beach and promenade (Phase 02 "living world"). People are pooled <see cref="PersonRig"/>s steered by tiny
    /// state machines (no NavMeshAgents): groups that stroll and stop to look at the sea, joggers, cyclists, sunbathers who lie down and sit up,
    /// kids digging, swimmers who wade in and out. How many of each is decided by <see cref="PopulationModel"/> (hour, weather, reputation,
    /// stage) and people arrive and leave on foot, so nobody pops into view. Simulation level of detail follows the distance to the camera:
    /// full animation near, stepped limbs mid-range, a body-only silhouette far away and plain arithmetic beyond that.
    /// </summary>
    public sealed class BeachLife : MonoBehaviour
    {
        public enum Role { Stroller, Jogger, Cyclist, Sunbather, Swimmer, Kid, Player, Vendor }
        const float RangeHalf = 120f;                         // promenade stretch that is populated, either side of the kiosk
        const int MaxAdults = 84, MaxKids = 24;

        sealed class Spot { public Vector3 pos; public float yaw; public GameObject props; public readonly List<Ambient> who = new List<Ambient>(); public bool active; }

        sealed class Ambient
        {
            public PersonRig rig; public Role role; public bool active, leaving, isKid;
            public Vector3 pos; public float yaw, speed, timer, dtAccum, lane;
            public int state, dir; public Pose pose;
            public Ambient leader; public Vector3 offset;
            public Spot spot; public Vector3 anchor, target; public float bob;
            public GameObject towel, ball, cooler;              // ball: owned by the first player of a pair; cooler: carried by a vendor
        }

        ResortGame game; ResortSite site; StallLayout lay;
        System.Random rng;
        float sx, kioskZ;
        readonly List<Ambient> all = new List<Ambient>();
        readonly List<Spot> spots = new List<Spot>();
        readonly Stack<PersonRig> freeAdults = new Stack<PersonRig>(), freeKids = new Stack<PersonRig>();
        int createdAdults, createdKids;
        float lodTimer, popTimer, lastHours = -1f;
        Transform folder;
        Mesh umbrellaMesh;
        Material ballMat, coolerMat, lidMat;
        public int[] LodCounts { get; } = new int[4];

        public int ActiveCount { get; private set; }
        public int Spawned => createdAdults + createdKids;
        public PopulationModel.Mix Target { get; private set; }

        public int CountOf(Role r) { int n = 0; foreach (var a in all) if (a.active && a.role == r && a.leader == null) n++; return n; }
        public int PeopleOf(Role r) { int n = 0; foreach (var a in all) if (a.active && a.role == r) n++; return n; }

        public struct Snap { public Vector3 pos; public Role role; public int lod; public Pose pose; }
        public IEnumerable<Snap> Snapshot()
        {
            foreach (var a in all) if (a.active) yield return new Snap { pos = a.pos, role = a.role, lod = a.rig.Lod, pose = a.pose };
        }

        public void Init(ResortGame g)
        {
            game = g; site = g.Site; lay = g.Layout; sx = lay.Root.position.x; kioskZ = lay.Root.position.z;
            rng = new System.Random(g.Seed * 31 + 7);
            folder = new GameObject("BeachLifePeople").transform; folder.SetParent(transform, false);
            BuildSpots(28);
            Settle();
        }

        // ---------------------------------------------------------------- site queries

        float EdgeZ(float x) => site.PromenadeZ(x) - 6f;

        float ShoreZ(float x) => site.WaterlineZ(x);

        float WaterZ(float x, float depth)
        {
            float z = ShoreZ(x);
            while (z > 5f && site.HeightAt(x, z) > -depth) z -= 0.5f;
            return z;
        }

        float LaneZ(Ambient a, float x)
        {
            float pz = site.PromenadeZ(x), lz = pz + a.lane;
            float near = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(9f, 4f, Mathf.Abs(x - sx)));   // keep clear of the kiosk queue
            return Mathf.Lerp(lz, Mathf.Max(lz, pz + 1.2f), near);
        }

        // ---------------------------------------------------------------- pool

        PersonRig Rig(bool kid, PersonKind kind)
        {
            var stack = kid ? freeKids : freeAdults;
            if (stack.Count > 0) { var r = stack.Pop(); r.gameObject.SetActive(true); return r; }
            if (kid ? createdKids >= MaxKids : createdAdults >= MaxAdults) return null;
            if (kid) createdKids++; else createdAdults++;
            var rig = PersonRig.Create(rng, kid ? PersonKind.Kid : kind, kid ? "Kid" : "Person");
            rig.transform.SetParent(folder, false);
            return rig;
        }

        Ambient Spawn(Role role, Vector3 pos, float yaw, bool kid = false, PersonKind kind = PersonKind.Casual)
        {
            var rig = Rig(kid, kind);
            if (rig == null) return null;
            if (role == Role.Cyclist) rig.AddBike(Color.HSVToRGB((float)rng.NextDouble(), 0.6f, 0.7f));
            var a = new Ambient { rig = rig, role = role, active = true, pos = pos, yaw = yaw, isKid = kid, pose = Pose.Stand };
            rig.Gesture = Gesture.None;
            all.Add(a);
            Place(a);
            return a;
        }

        void Release(Ambient a)
        {
            a.active = false;
            if (a.towel != null) Destroy(a.towel);
            if (a.ball != null) { Destroy(a.ball); a.ball = null; }
            if (a.cooler != null) { Destroy(a.cooler); a.cooler = null; }
            a.rig.HitPulse = 0f;
            a.rig.Gesture = Gesture.None; a.rig.BodyOffset = Vector3.zero; a.rig.SetLod(3);
            a.rig.gameObject.SetActive(false);
            (a.isKid ? freeKids : freeAdults).Push(a.rig);
            if (a.role == Role.Cyclist) a.rig.ClearProps();
            all.Remove(a);
        }

        void Place(Ambient a)
        {
            float y = site.HeightAt(a.pos.x, a.pos.z);
            if (a.role == Role.Swimmer)
            {
                float depth = -y;
                float f = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.55f, 1.1f, depth));
                y = Mathf.Lerp(y, -0.30f + Mathf.Sin(Time.time * 1.3f + a.bob) * 0.04f, f);
            }
            a.pos.y = y;
            a.rig.transform.SetPositionAndRotation(a.pos, Quaternion.Euler(0f, a.yaw, 0f));
            if (a.cooler != null)                                                           // hangs at the hip, only drawn while the vendor is close
            {
                a.cooler.SetActive(a.rig.Lod <= 1);
                a.cooler.transform.SetPositionAndRotation(a.pos + Quaternion.Euler(0f, a.yaw, 0f) * new Vector3(0.34f, 0.9f, 0.05f), Quaternion.Euler(0f, a.yaw, 0f));
            }
        }

        // ---------------------------------------------------------------- beach spots (towels and umbrellas)

        void BuildSpots(int n)
        {
            var tries = 0;
            while (spots.Count < n && tries++ < 600)
            {
                float x = sx + ((float)rng.NextDouble() - 0.5f) * 2f * 95f;
                float u = Mathf.Pow((float)rng.NextDouble(), 2.1f);
                float z = EdgeZ(x) - 4f - u * 105f;
                if (site.HeightAt(x, z) < 0.5f) continue;                               // not on wet sand
                if (x > sx - 10f && x < sx + 11f && z > kioskZ - 10f) continue;          // the kiosk, its tables and its path
                bool close = false;
                foreach (var s in spots) if ((s.pos.x - x) * (s.pos.x - x) + (s.pos.z - z) * (s.pos.z - z) < 3.8f * 3.8f) { close = true; break; }
                if (close) continue;
                var spot = new Spot { pos = new Vector3(x, site.HeightAt(x, z), z), yaw = 180f + ((float)rng.NextDouble() - 0.5f) * 50f };
                spot.props = BuildSpotProps(spot, rng.NextDouble() < 0.65);
                spot.props.SetActive(false);
                spots.Add(spot);
            }
        }

        static readonly Color[] Umbrellas = { new Color(0.97f, 0.80f, 0.15f), new Color(0.95f, 0.95f, 0.92f), new Color(0.2f, 0.42f, 0.8f), new Color(0.92f, 0.35f, 0.25f), new Color(0.97f, 0.80f, 0.15f) };

        GameObject BuildSpotProps(Spot s, bool umbrella)
        {
            var root = new GameObject("BeachSpot"); root.transform.SetParent(folder, false);
            root.transform.SetPositionAndRotation(s.pos, Quaternion.Euler(0f, s.yaw, 0f));
            if (umbrella)
            {
                if (umbrellaMesh == null) umbrellaMesh = MakeUmbrella();
                var pole = StallBuilder.Box("Pole", root.transform, new Vector3(0.9f, 1.15f, 0.6f), new Vector3(0.04f, 2.3f, 0.04f), new Color(0.82f, 0.82f, 0.8f), collider: false);
                pole.transform.localRotation = Quaternion.Euler(0f, 0f, -6f);
                var canopy = new GameObject("Canopy"); canopy.transform.SetParent(root.transform, false);
                canopy.transform.localPosition = new Vector3(0.85f, 2.2f, 0.6f); canopy.transform.localRotation = Quaternion.Euler(0f, 0f, -6f);
                canopy.AddComponent<MeshFilter>().sharedMesh = umbrellaMesh;
                var mr = canopy.AddComponent<MeshRenderer>(); mr.sharedMaterial = StallBuilder.Mat(Umbrellas[rng.Next(Umbrellas.Length)], 0.2f);
            }
            return root;
        }

        /// <summary>A double-sided cone (apex up), 2.4 m across: reads as a beach umbrella canopy from above and below.</summary>
        static Mesh umbrellaShared;
        public static Mesh MakeUmbrella()
        {
            if (umbrellaShared != null) return umbrellaShared;
            const int n = 14; const float r = 1.2f, h = 0.42f;
            // top and underside use their own vertices: sharing them would average the opposite normals to zero and render the canopy black
            var v = new List<Vector3>(); var t = new List<int>();
            for (int side = 0; side < 2; side++)
            {
                int o = v.Count;
                v.Add(new Vector3(0f, h, 0f));
                for (int i = 0; i < n; i++) { float a = i * Mathf.PI * 2f / n; v.Add(new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r)); }
                for (int i = 0; i < n; i++)
                {
                    int b = o + 1 + i, c = o + 1 + (i + 1) % n;
                    if (side == 0) t.AddRange(new[] { o, c, b }); else t.AddRange(new[] { o, b, c });
                }
            }
            var m = new Mesh { name = "Umbrella" }; m.SetVertices(v); m.SetTriangles(t, 0); m.RecalculateNormals(); m.RecalculateBounds();
            return umbrellaShared = m;
        }

        GameObject Towel(Vector3 pos, float yaw)
        {
            var g = StallBuilder.Box("Towel", folder, Vector3.zero, new Vector3(0.85f, 0.02f, 1.8f), Color.HSVToRGB((float)rng.NextDouble(), 0.55f, 0.95f), collider: false);
            g.transform.SetPositionAndRotation(pos + Vector3.up * 0.015f, Quaternion.Euler(0f, yaw, 0f));
            return g;
        }

        // ---------------------------------------------------------------- population control

        /// <summary>Fills the scene to the target for the current hour at once (start of the game, after the clock jumps). People are placed, not walked in.</summary>
        public void Settle()
        {
            var mix = Target = PopulationModel.MixFor(game.Clock.Hours, game.Weather, game.Stall.Reputation, game.Stages != null ? game.Stages.Stage : 1);
            lastHours = game.Clock.Hours;
            for (int i = CountOf(Role.Stroller); i < mix.Strollers; i++) SpawnGroup(true);
            for (int i = CountOf(Role.Jogger); i < mix.Joggers; i++) SpawnRunner(Role.Jogger, true);
            for (int i = CountOf(Role.Cyclist); i < mix.Cyclists; i++) SpawnRunner(Role.Cyclist, true);
            FillBeach(mix, true);
            for (int i = PeopleOf(Role.Swimmer); i < mix.Swimmers; i++) SpawnSwimmer();
            for (int i = CountOf(Role.Player); i < mix.Players; i++) SpawnPair(true);
            for (int i = CountOf(Role.Vendor); i < mix.Vendors; i++) SpawnVendor(true);
        }

        void Rebalance()
        {
            float h = game.Clock.Hours;
            if (Mathf.Abs(h - lastHours) > 1.2f) { Clear(); Settle(); return; }           // the clock jumped (next morning, a test): rebuild instead of walking in
            lastHours = h;
            var mix = Target = PopulationModel.MixFor(h, game.Weather, game.Stall.Reputation, game.Stages != null ? game.Stages.Stage : 1);
            Steer(Role.Stroller, mix.Strollers, () => SpawnGroup(false));
            Steer(Role.Jogger, mix.Joggers, () => SpawnRunner(Role.Jogger, false));
            Steer(Role.Cyclist, mix.Cyclists, () => SpawnRunner(Role.Cyclist, false));
            FillBeach(mix, false);
            Steer(Role.Player, mix.Players, () => SpawnPair(false));
            Steer(Role.Vendor, mix.Vendors, () => SpawnVendor(false));
            int swim = PeopleOf(Role.Swimmer);
            if (swim < mix.Swimmers && rng.NextDouble() < 0.6) SpawnSwimmer();
            else if (swim > mix.Swimmers) foreach (var a in all) if (a.active && a.role == Role.Swimmer && !a.leaving) { a.leaving = true; break; }
        }

        void Clear() { for (int i = all.Count - 1; i >= 0; i--) { if (all[i].spot != null) all[i].spot.who.Clear(); Release(all[i]); } foreach (var s in spots) { s.active = false; s.props.SetActive(false); } }

        void Steer(Role role, int target, System.Action spawn)
        {
            int n = 0; foreach (var a in all) if (a.active && a.role == role && a.leader == null && !a.leaving) n++;
            if (n < target) { if (rng.NextDouble() < 0.7) spawn(); }
            else if (n > target) foreach (var a in all) if (a.active && a.role == role && a.leader == null && !a.leaving) { a.leaving = true; break; }
        }

        // ---------------------------------------------------------------- spawners

        static readonly float[] StrollLanes = { -3.6f, -2.2f, 1.4f, 3.4f };

        void SpawnGroup(bool anywhere)
        {
            int dir = rng.NextDouble() < 0.5 ? 1 : -1;
            float x = anywhere ? sx + ((float)rng.NextDouble() - 0.5f) * 2f * (RangeHalf - 8f) : sx - dir * RangeHalf;
            float roll = (float)rng.NextDouble();
            int adults = roll < 0.35f ? 1 : roll < 0.65f ? 2 : roll < 0.80f ? 3 : 2;
            int kids = roll >= 0.80f ? 1 + rng.Next(2) : 0;
            float lane = StrollLanes[rng.Next(StrollLanes.Length)] + ((float)rng.NextDouble() - 0.5f) * 0.6f;
            var leader = Spawn(Role.Stroller, new Vector3(x, 0f, site.PromenadeZ(x) + lane), dir > 0 ? 90f : 270f, false, rng.NextDouble() < 0.3 ? PersonKind.Beach : PersonKind.Casual);
            if (leader == null) return;
            leader.dir = dir; leader.lane = lane; leader.speed = 1.05f + 0.35f * (float)rng.NextDouble(); leader.timer = 6f + 20f * (float)rng.NextDouble();
            leader.state = 0; leader.pose = Pose.Walk;
            for (int i = 1; i < adults + kids; i++)
            {
                bool kid = i >= adults;
                var f = Spawn(Role.Stroller, leader.pos, leader.yaw, kid, PersonKind.Casual);
                if (f == null) break;
                f.leader = leader; f.speed = leader.speed; f.isKid = kid;
                f.offset = kid ? new Vector3((i % 2 == 0 ? -0.5f : 0.55f), 0f, 0.6f + 0.4f * i) : new Vector3(0.6f * i * (i % 2 == 0 ? -1f : 1f), 0f, -0.2f * i);
            }
        }

        void SpawnRunner(Role role, bool anywhere)
        {
            int dir = rng.NextDouble() < 0.5 ? 1 : -1;
            float x = anywhere ? sx + ((float)rng.NextDouble() - 0.5f) * 2f * (RangeHalf - 8f) : sx - dir * RangeHalf;
            float lane = role == Role.Cyclist ? 4.9f : 2.9f + ((float)rng.NextDouble() - 0.5f) * 0.8f;
            var a = Spawn(role, new Vector3(x, 0f, site.PromenadeZ(x) + lane), dir > 0 ? 90f : 270f, false, PersonKind.Active);
            if (a == null) return;
            a.dir = dir; a.lane = lane; a.pose = role == Role.Cyclist ? Pose.Bike : Pose.Run;
            a.speed = role == Role.Cyclist ? 4.4f + 1.4f * (float)rng.NextDouble() : 2.7f + 0.7f * (float)rng.NextDouble();
        }

        void FillBeach(PopulationModel.Mix mix, bool instant)
        {
            int people = PeopleOf(Role.Sunbather), kids = PeopleOf(Role.Kid);
            if (people < mix.Beach && (instant || rng.NextDouble() < 0.5))
            {
                int guard = 0;
                while (people < mix.Beach && guard++ < 40)
                {
                    Spot s = null; foreach (var c in spots) if (!c.active) { s = c; break; }
                    if (s == null) break;
                    int cap = 1 + rng.Next(3);
                    s.active = true; s.props.SetActive(true);
                    for (int i = 0; i < cap; i++)
                    {
                        float side = (i - (cap - 1) * 0.5f) * 1.05f;
                        var sp = s.pos + Quaternion.Euler(0f, s.yaw, 0f) * new Vector3(side, 0f, 0f);
                        Vector3 start = instant ? sp : new Vector3(sp.x, 0f, EdgeZ(sp.x) + 0.5f);
                        var a = Spawn(Role.Sunbather, start, s.yaw, false, PersonKind.Beach);
                        if (a == null) break;
                        a.spot = s; a.anchor = sp; a.state = instant ? 1 : 0; a.timer = 20f + 90f * (float)rng.NextDouble(); a.speed = 1.2f;
                        a.pose = instant ? (rng.NextDouble() < 0.5 ? Pose.LieBack : Pose.LieFront) : Pose.Walk;
                        if (instant) { a.pos = sp; a.towel = Towel(sp, s.yaw); }
                        s.who.Add(a); people++;
                    }
                    if (!instant) break;
                }
            }
            else if (people > mix.Beach)
            {
                for (int i = spots.Count - 1; i >= 0; i--) if (spots[i].active) { foreach (var a in spots[i].who) a.leaving = true; spots[i].active = false; break; }
            }
            // a kid digging near an occupied umbrella
            if (kids < mix.Kids)
                foreach (var s in spots)
                    if (s.active && s.who.Count > 0 && !HasKid(s) && (instant || rng.NextDouble() < 0.3))
                    {
                        var k = Spawn(Role.Kid, instant ? s.pos + new Vector3(2f, 0f, -1.5f) : new Vector3(s.pos.x, 0f, EdgeZ(s.pos.x) + 0.5f), s.yaw, true, PersonKind.Kid);
                        if (k != null) { k.spot = s; k.anchor = s.pos + new Vector3(1.8f, 0f, -2.2f); k.speed = 2.0f; k.state = instant ? 2 : 0; k.timer = 3f + 5f * (float)rng.NextDouble(); }
                        break;
                    }
            if (kids > mix.Kids) foreach (var a in all) if (a.active && a.role == Role.Kid && !a.leaving) { a.leaving = true; break; }
        }

        bool HasKid(Spot s) { foreach (var a in all) if (a.active && a.role == Role.Kid && a.spot == s) return true; return false; }

        void SpawnSwimmer()
        {
            float x = sx + ((float)rng.NextDouble() - 0.5f) * 2f * 85f;
            float z = ShoreZ(x) + 1.5f;
            var a = Spawn(Role.Swimmer, new Vector3(x, 0f, z), 180f, false, PersonKind.Beach);
            if (a == null) return;
            a.state = 0; a.speed = 1.0f + 0.3f * (float)rng.NextDouble(); a.bob = (float)rng.NextDouble() * 6f;
            a.target = new Vector3(x + ((float)rng.NextDouble() - 0.5f) * 8f, 0f, WaterZ(x, 0.95f + 0.25f * (float)rng.NextDouble()));
            a.pose = Pose.Walk;
        }

        /// <summary>Two people on the sand knocking a ball back and forth (frescobol): they walk down from the promenade, face each other and play.</summary>
        void SpawnPair(bool instant)
        {
            float cx = 0f, cz = 0f; bool found = false;
            for (int tries = 0; tries < 40 && !found; tries++)
            {
                cx = sx + ((float)rng.NextDouble() - 0.5f) * 2f * 85f;
                cz = EdgeZ(cx) - 12f - (float)rng.NextDouble() * 55f;
                if (cx > sx - 14f && cx < sx + 15f && cz > kioskZ - 14f) continue;                 // the kiosk, its tables and its path
                if (site.HeightAt(cx - 3.3f, cz) < 0.6f || site.HeightAt(cx + 3.3f, cz) < 0.6f) continue;   // both ends on dry sand
                found = true;
                foreach (var s in spots) if ((s.pos.x - cx) * (s.pos.x - cx) + (s.pos.z - cz) * (s.pos.z - cz) < 6f * 6f) { found = false; break; }
                if (found) foreach (var o in all) if (o.active && o.role == Role.Player && (o.anchor.x - cx) * (o.anchor.x - cx) + (o.anchor.z - cz) * (o.anchor.z - cz) < 8f * 8f) { found = false; break; }
            }
            if (!found) return;
            float half = 2.6f + 0.7f * (float)rng.NextDouble();
            var first = SpawnPlayer(cx - half, cz, instant, 90f);
            if (first == null) return;
            var second = SpawnPlayer(cx + half, cz, instant, 270f);
            if (second == null) { Release(first); return; }
            second.leader = first;
            first.timer = 45f + 90f * (float)rng.NextDouble();
            var ball = GameObject.CreatePrimitive(PrimitiveType.Sphere); ball.name = "BeachBall";
            Destroy(ball.GetComponent<Collider>());
            ball.transform.SetParent(folder, false); ball.transform.localScale = Vector3.one * 0.2f;
            if (ballMat == null) ballMat = StallBuilder.Mat(new Color(0.95f, 0.85f, 0.25f), 0.35f);
            ball.GetComponent<MeshRenderer>().sharedMaterial = ballMat;
            ball.SetActive(instant);
            first.ball = ball;
        }

        /// <summary>A beach seller: steps down from the promenade, walks a row of the sand with a cooler box on the hip, stopping now and then to call out.</summary>
        void SpawnVendor(bool instant)
        {
            int dir = rng.NextDouble() < 0.5 ? 1 : -1;
            float x = instant ? sx + ((float)rng.NextDouble() - 0.5f) * 2f * 70f : sx - dir * 80f;
            float row = EdgeZ(x) - 8f - (float)rng.NextDouble() * 22f;
            var a = Spawn(Role.Vendor, instant ? new Vector3(x, 0f, VendorRowZ(x, row)) : new Vector3(x, 0f, EdgeZ(x) + 0.5f), dir > 0 ? 90f : 270f, false, PersonKind.Beach);
            if (a == null) return;
            a.dir = dir; a.lane = row; a.speed = 1.0f + 0.2f * (float)rng.NextDouble(); a.state = instant ? 1 : 0; a.timer = 6f + 14f * (float)rng.NextDouble();
            a.pose = Pose.Walk;
            if (coolerMat == null) { coolerMat = StallBuilder.Mat(new Color(0.93f, 0.94f, 0.95f), 0.3f); lidMat = StallBuilder.Mat(new Color(0.85f, 0.18f, 0.16f), 0.3f); }
            var box = StallBuilder.Box("VendorCooler", folder, Vector3.zero, new Vector3(0.5f, 0.3f, 0.34f), new Color(0.93f, 0.94f, 0.95f), collider: false);
            box.GetComponent<MeshRenderer>().sharedMaterial = coolerMat;
            var lid = StallBuilder.Box("Lid", box.transform, Vector3.zero, new Vector3(0.52f, 0.05f, 0.36f), new Color(0.85f, 0.18f, 0.16f), collider: false);
            lid.transform.localPosition = new Vector3(0f, 0.58f, 0f); lid.transform.localScale = new Vector3(1.04f, 0.17f, 1.06f);
            lid.GetComponent<MeshRenderer>().sharedMaterial = lidMat;
            box.SetActive(false);
            a.cooler = box;
        }

        /// <summary>The row of sand a vendor walks: kept on dry sand and clear of the stall, its tables and its queue.</summary>
        float VendorRowZ(float x, float row)
        {
            float z = row;
            if (x > sx - 14f && x < sx + 15f) z = Mathf.Min(z, kioskZ - 14f);
            return Mathf.Max(z, ShoreZ(x) + 4f);
        }

        Ambient SpawnPlayer(float x, float z, bool instant, float yaw)
        {
            Vector3 start = instant ? new Vector3(x, 0f, z) : new Vector3(x, 0f, EdgeZ(x) + 0.5f);
            var a = Spawn(Role.Player, start, yaw, false, PersonKind.Active);
            if (a == null) return null;
            a.anchor = new Vector3(x, 0f, z); a.speed = 1.3f; a.state = instant ? 1 : 0;
            a.pose = instant ? Pose.Stand : Pose.Walk;
            if (instant) a.rig.Gesture = Gesture.Hit;
            return a;
        }

        // ---------------------------------------------------------------- per frame

        void Update()
        {
            if (game == null || game.Clock == null) return;
            float dt = Time.deltaTime;
            popTimer -= dt; lodTimer -= dt;
            if (popTimer <= 0f) { popTimer = 2f; Rebalance(); }
            var cam = Camera.main; var cp = cam != null ? cam.transform.position : Vector3.zero;
            if (lodTimer <= 0f) { lodTimer = 0.2f; UpdateLod(cp); }

            for (int i = all.Count - 1; i >= 0; i--)
            {
                var a = all[i];
                if (!a.active) continue;
                int lod = a.rig.Lod;
                a.dtAccum += dt;
                float step = lod <= 1 ? 0f : lod == 2 ? 0.1f : 1f;
                if (a.dtAccum < step) continue;
                float sdt = a.dtAccum; a.dtAccum = 0f;
                Tick(a, sdt, lod == 0 ? cp : (Vector3?)null);
                if (a.active) { Place(a); a.rig.Animate(a.pose, a.speed, sdt); }
            }
        }

        void UpdateLod(Vector3 cp)
        {
            for (int i = 0; i < LodCounts.Length; i++) LodCounts[i] = 0;
            int active = 0;
            foreach (var a in all)
            {
                if (!a.active) continue;
                active++;
                float dx = a.pos.x - cp.x, dz = a.pos.z - cp.z, d2 = dx * dx + dz * dz + (a.pos.y - cp.y) * (a.pos.y - cp.y) * 0.25f;
                int l = d2 < 38f * 38f ? 0 : d2 < 100f * 100f ? 1 : d2 < 230f * 230f ? 2 : 3;
                a.rig.SetLod(l); LodCounts[l]++;
            }
            ActiveCount = active;
        }

        void Tick(Ambient a, float dt, Vector3? player)
        {
            switch (a.role)
            {
                case Role.Stroller: if (a.leader != null) TickFollower(a, dt); else TickWalker(a, dt, true); break;
                case Role.Jogger:
                case Role.Cyclist: TickWalker(a, dt, false); break;
                case Role.Sunbather: TickSunbather(a, dt); break;
                case Role.Kid: TickKid(a, dt); break;
                case Role.Swimmer: TickSwimmer(a, dt); break;
                case Role.Player: TickPlayer(a, dt); break;
                case Role.Vendor: TickVendor(a, dt); break;
            }
            if (player.HasValue && a.active) Yield(a, player.Value);
        }

        /// <summary>Personal space: people near the player step aside instead of standing inside the camera.</summary>
        static void Yield(Ambient a, Vector3 p)
        {
            float dx = a.pos.x - p.x, dz = a.pos.z - p.z, d = Mathf.Sqrt(dx * dx + dz * dz);
            if (d < 0.8f && d > 0.001f) { a.pos.x += dx / d * (0.8f - d); a.pos.z += dz / d * (0.8f - d); }
        }

        void TickWalker(Ambient a, float dt, bool mayStop)
        {
            if (a.state == 1)                                                              // stopped to look at the sea
            {
                a.timer -= dt; a.pose = Pose.Stand;
                if (a.timer <= 0f) { a.state = 0; a.rig.Gesture = Gesture.None; a.timer = 8f + 25f * (float)rng.NextDouble(); a.pose = Pose.Walk; a.yaw = a.dir > 0 ? 90f : 270f; }
                return;
            }
            float x = a.pos.x + a.dir * a.speed * dt;
            a.pos = new Vector3(x, 0f, Mathf.MoveTowards(a.pos.z, LaneZ(a, x), 1.5f * dt));
            a.yaw = Mathf.LerpAngle(a.yaw, a.dir > 0 ? 90f : 270f, 6f * dt);
            if (mayStop)
            {
                a.timer -= dt;
                if (a.timer <= 0f)
                {
                    if (rng.NextDouble() < 0.35) { a.state = 1; a.timer = 5f + 8f * (float)rng.NextDouble(); a.yaw = 180f; a.rig.Gesture = rng.NextDouble() < 0.5 ? Gesture.Phone : Gesture.Chat; }
                    else a.timer = 8f + 25f * (float)rng.NextDouble();
                }
            }
            if (Mathf.Abs(x - sx) > RangeHalf + 4f && (x - sx) * a.dir > 0f) EndOfWalk(a);
        }

        void EndOfWalk(Ambient a)
        {
            // The leader going away takes its group with it; followers notice and leave too.
            Release(a);
        }

        void TickFollower(Ambient a, float dt)
        {
            var l = a.leader;
            if (!l.active) { Release(a); return; }
            float cy = Mathf.Cos(l.yaw * Mathf.Deg2Rad), sy = Mathf.Sin(l.yaw * Mathf.Deg2Rad);
            var right = new Vector3(cy, 0f, -sy);
            var fwd = new Vector3(sy, 0f, cy);
            var want = l.pos + right * a.offset.x + fwd * a.offset.z;                      // offset.z < 0 is behind the leader
            if (a.isKid) want += right * Mathf.Sin(Time.time * 1.7f + a.offset.z * 3f) * 0.5f;
            var to = want - a.pos; to.y = 0f;
            float d = to.magnitude, sp = a.speed * (d > 1.2f ? 1.6f : 1f);
            if (l.state == 1) sp = d > 0.3f ? 1.1f : 0f;                                   // the group stopped: close up, then stand
            if (d > 0.04f) a.pos += to / d * Mathf.Min(d, sp * dt);
            a.pose = d > 0.5f && sp > 0.2f ? (a.isKid && d > 1.2f ? Pose.Run : Pose.Walk) : Pose.Stand;
            a.yaw = l.state == 1 ? Mathf.LerpAngle(a.yaw, 180f, 4f * dt) : Mathf.LerpAngle(a.yaw, l.yaw, 6f * dt);
            if (l.state == 1 && a.rig.Gesture == Gesture.None) a.rig.Gesture = rng.NextDouble() < 0.5 ? Gesture.Phone : Gesture.Chat;
            if (l.state != 1 && a.rig.Gesture != Gesture.None) a.rig.Gesture = Gesture.None;
        }

        void TickSunbather(Ambient a, float dt)
        {
            var s = a.spot;
            switch (a.state)
            {
                case 0:                                                                    // arriving: walk from the promenade to the towel
                {
                    var to = a.anchor - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.speed = 1.2f; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, a.anchor), 8f * dt);
                    if (d < 0.15f) { a.state = 1; a.pos = a.anchor; a.yaw = s.yaw; a.pose = rng.NextDouble() < 0.5 ? Pose.LieBack : Pose.LieFront; a.towel = Towel(a.anchor, s.yaw); }
                    else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
                case 1:                                                                    // lying in the sun
                    a.timer -= dt; a.speed = 0.4f;
                    if (a.leaving) { StartLeaving(a); break; }
                    if (a.timer <= 0f) { a.state = 2; a.timer = 20f + 50f * (float)rng.NextDouble(); a.pose = Pose.SitSand; a.rig.Gesture = (Gesture)(1 + rng.Next(3)); }
                    break;
                case 2:                                                                    // sitting up: phone, a drink, a chat, looking at the sea
                    a.timer -= dt;
                    if (a.leaving) { StartLeaving(a); break; }
                    if (a.timer <= 0f) { a.state = 1; a.timer = 40f + 80f * (float)rng.NextDouble(); a.rig.Gesture = Gesture.None; a.pose = rng.NextDouble() < 0.5 ? Pose.LieBack : Pose.LieFront; }
                    break;
                case 3:                                                                    // leaving: back to the promenade, then gone
                {
                    var goal = new Vector3(a.pos.x, 0f, EdgeZ(a.pos.x) + 0.6f);
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.speed = 1.3f; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, goal), 8f * dt);
                    if (d < 0.3f || OutOfSight(a)) { if (s != null) s.who.Remove(a); Release(a); }
                    else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
            }
        }

        void StartLeaving(Ambient a)
        {
            a.state = 3; a.rig.Gesture = Gesture.None;
            if (a.towel != null) { Destroy(a.towel); a.towel = null; }
            if (a.spot != null && a.spot.who.TrueForAll(w => w.state == 3 || w == a || !w.active)) a.spot.props.SetActive(false);
        }

        bool OutOfSight(Ambient a)
        {
            var cam = Camera.main; if (cam == null) return true;
            var d = a.pos - cam.transform.position; d.y = 0f;
            return d.sqrMagnitude > 120f * 120f;
        }

        /// <summary>Ball game: walk to the mark, face the partner and hit the ball back and forth in an arc until the game ends, then walk off.</summary>
        void TickPlayer(Ambient a, float dt)
        {
            var lead = a.leader ?? a;
            if (a.state != 3 && (lead.leaving || !lead.active || (a.leader != null && lead.state == 3)))
            {
                a.state = 3; a.rig.Gesture = Gesture.None; a.rig.HitPulse = 0f;
                if (a.ball != null) a.ball.SetActive(false);
            }
            switch (a.state)
            {
                case 0:                                                                    // walking to the mark
                {
                    var to = a.anchor - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, a.anchor), 8f * dt);
                    if (d < 0.15f) { a.state = 1; a.pos = a.anchor; a.pose = Pose.Stand; a.rig.Gesture = Gesture.Hit; }
                    else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
                case 1:                                                                    // playing
                {
                    a.pose = Pose.Stand;
                    a.yaw = Mathf.LerpAngle(a.yaw, a.leader == null ? 90f : 270f, 8f * dt);       // the first player stands at the west end
                    if (a.leader != null) break;                                           // the first player runs the game
                    a.timer -= dt;
                    if (a.timer <= 0f) { a.leaving = true; break; }
                    var other = Partner(a);
                    if (other == null || other.state != 1) { if (a.ball != null) a.ball.SetActive(false); a.rig.HitPulse = 0f; break; }
                    // one hop of the ball every ~1.5 s: u runs 0 -> 1 (to the partner) and back
                    float u = Mathf.PingPong(Time.time * 0.66f + a.bob, 1f);
                    var hA = a.pos + Vector3.up * 1.15f + new Vector3(0.15f, 0f, 0f);
                    var hB = other.pos + Vector3.up * 1.15f - new Vector3(0.15f, 0f, 0f);
                    bool visible = a.rig.Lod <= 1;
                    if (a.ball != null)
                    {
                        a.ball.SetActive(visible);
                        a.ball.transform.position = Vector3.Lerp(hA, hB, u) + Vector3.up * (4f * u * (1f - u) * 1.9f);
                    }
                    a.rig.HitPulse = Mathf.Clamp01(1f - u / 0.2f);
                    other.rig.HitPulse = Mathf.Clamp01(1f - (1f - u) / 0.2f);
                    break;
                }
                case 3:                                                                    // leaving: up the beach to the promenade
                {
                    var goal = new Vector3(a.pos.x, 0f, EdgeZ(a.pos.x) + 0.6f);
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, goal), 8f * dt);
                    if (d < 0.3f || OutOfSight(a)) Release(a); else a.pos += to / d * Mathf.Min(d, 1.3f * dt);
                    break;
                }
            }
        }

        /// <summary>Beach seller: down to the sand, then along it; every so often stops, faces the sunbathers and calls out; leaves when asked or at the end of the beach.</summary>
        void TickVendor(Ambient a, float dt)
        {
            if (a.leaving && a.state != 3) { a.state = 3; a.rig.Gesture = Gesture.None; }
            switch (a.state)
            {
                case 0:                                                                    // from the promenade down to the row
                {
                    var goal = new Vector3(a.pos.x, 0f, VendorRowZ(a.pos.x, a.lane));
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, goal), 8f * dt);
                    if (d < 0.3f) a.state = 1; else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
                case 1:                                                                    // walking the row
                {
                    float x = a.pos.x + a.dir * a.speed * dt;
                    a.pos = new Vector3(x, 0f, Mathf.MoveTowards(a.pos.z, VendorRowZ(x, a.lane), 1.2f * dt));
                    a.yaw = Mathf.LerpAngle(a.yaw, a.dir > 0 ? 90f : 270f, 6f * dt); a.pose = Pose.Walk;
                    a.timer -= dt;
                    if (a.timer <= 0f) { a.state = 2; a.timer = 5f + 6f * (float)rng.NextDouble(); a.rig.Gesture = Gesture.Chat; }
                    if (Mathf.Abs(x - sx) > 95f && (x - sx) * a.dir > 0f) a.state = 3;
                    break;
                }
                case 2:                                                                    // calling out to the umbrellas
                    a.timer -= dt; a.pose = Pose.Stand; a.yaw = Mathf.LerpAngle(a.yaw, 0f, 4f * dt);
                    if (a.timer <= 0f) { a.state = 1; a.timer = 12f + 25f * (float)rng.NextDouble(); a.rig.Gesture = Gesture.None; }
                    break;
                case 3:                                                                    // up the beach to the promenade
                {
                    var goal = new Vector3(a.pos.x, 0f, EdgeZ(a.pos.x) + 0.6f);
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, goal), 8f * dt);
                    if (d < 0.3f || OutOfSight(a)) Release(a); else a.pos += to / d * Mathf.Min(d, 1.3f * dt);
                    break;
                }
            }
        }

        Ambient Partner(Ambient first) { foreach (var o in all) if (o.active && o.leader == first && o.role == Role.Player) return o; return null; }

        void TickKid(Ambient a, float dt)
        {
            if (a.leaving && a.state != 3) { a.state = 3; a.rig.Gesture = Gesture.None; }
            switch (a.state)
            {
                case 0: case 1:                                                            // run to a spot near the umbrella
                {
                    var goal = a.state == 0 ? a.anchor : a.target; goal.y = 0f;
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Run; a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, goal), 10f * dt);
                    if (d < 0.25f) { a.state = 2; a.timer = 4f + 6f * (float)rng.NextDouble(); a.rig.Gesture = Gesture.Dig; a.pose = Pose.SitSand; }
                    else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
                case 2:                                                                    // digging in the sand
                    a.timer -= dt;
                    if (a.timer <= 0f)
                    {
                        a.state = 1; a.rig.Gesture = Gesture.None;
                        a.target = a.anchor + new Vector3(((float)rng.NextDouble() - 0.5f) * 8f, 0f, ((float)rng.NextDouble() - 0.5f) * 6f);
                    }
                    break;
                case 3:
                {
                    var goal = new Vector3(a.pos.x, 0f, EdgeZ(a.pos.x) + 0.6f);
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Run; a.yaw = PersonRig.YawTowards(a.pos, goal);
                    if (d < 0.3f || OutOfSight(a)) Release(a); else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
            }
        }

        void TickSwimmer(Ambient a, float dt)
        {
            float ground = site.HeightAt(a.pos.x, a.pos.z);
            switch (a.state)
            {
                case 0:                                                                    // wade in
                {
                    var to = a.target - a.pos; to.y = 0f; float d = to.magnitude;
                    a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, a.target), 6f * dt);
                    a.pose = ground < -0.85f ? Pose.Swim : Pose.Walk;
                    if (d < 0.5f) { a.state = 1; a.timer = 20f + 40f * (float)rng.NextDouble(); a.target = a.pos; }
                    else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
                case 1:                                                                    // swim and bob around
                    a.timer -= dt; a.pose = ground < -0.85f ? Pose.Swim : Pose.Stand;
                    if ((a.target - a.pos).sqrMagnitude < 0.5f) a.target = new Vector3(a.pos.x + ((float)rng.NextDouble() - 0.5f) * 10f, 0f, Mathf.Clamp(a.pos.z + ((float)rng.NextDouble() - 0.5f) * 5f, WaterZ(a.pos.x, 1.3f), ShoreZ(a.pos.x) - 1.5f));
                    {
                        var to = a.target - a.pos; to.y = 0f; float d = to.magnitude;
                        a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, a.target), 4f * dt);
                        if (d > 0.05f) a.pos += to / d * Mathf.Min(d, 0.55f * dt);
                    }
                    if (a.timer <= 0f || a.leaving) { a.state = 2; }
                    break;
                case 2:                                                                    // wade out
                {
                    var goal = new Vector3(a.pos.x, 0f, ShoreZ(a.pos.x) + 3f);
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.yaw = Mathf.LerpAngle(a.yaw, PersonRig.YawTowards(a.pos, goal), 6f * dt);
                    a.pose = ground < -0.85f ? Pose.Swim : Pose.Walk; a.speed = 1.0f;
                    if (d < 0.4f) { if (a.leaving) { if (OutOfSight(a)) Release(a); else a.state = 4; } else { a.state = 3; a.timer = 8f + 12f * (float)rng.NextDouble(); a.dir = rng.NextDouble() < 0.5 ? 1 : -1; } }
                    else a.pos += to / d * Mathf.Min(d, a.speed * dt);
                    break;
                }
                case 3:                                                                    // stroll along the water line, then go back in
                    a.timer -= dt; a.pose = Pose.Walk;
                    a.pos.x += a.dir * 0.8f * dt; a.pos.z = ShoreZ(a.pos.x) + 2.5f; a.yaw = a.dir > 0 ? 90f : 270f;
                    if (a.leaving) a.state = 4;
                    else if (a.timer <= 0f) { a.state = 0; a.target = new Vector3(a.pos.x + ((float)rng.NextDouble() - 0.5f) * 8f, 0f, WaterZ(a.pos.x, 0.95f + 0.25f * (float)rng.NextDouble())); }
                    break;
                case 4:                                                                    // leaving: up the beach to the promenade
                {
                    var goal = new Vector3(a.pos.x, 0f, EdgeZ(a.pos.x) + 0.6f);
                    var to = goal - a.pos; to.y = 0f; float d = to.magnitude;
                    a.pose = Pose.Walk; a.yaw = PersonRig.YawTowards(a.pos, goal);
                    if (d < 0.5f || OutOfSight(a)) Release(a); else a.pos += to / d * Mathf.Min(d, 1.3f * dt);
                    break;
                }
            }
        }
    }
}
