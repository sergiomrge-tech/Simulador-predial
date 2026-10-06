using System.Collections.Generic;
using ResortAurora.Site;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>Where things are around the stall (world space). The stall faces +Z (north, toward the promenade).</summary>
    public sealed class StallLayout
    {
        public Transform Root;
        public ResortSite Site;
        public Vector3 PlayerSpawn, AttendantPos, CookPos, PickupPos;
        public float PromenadeZ, LaneZ, WestX, EastX, CounterFrontZ;
        public readonly List<GameObject> StaffVisuals = new List<GameObject>();
        public readonly List<Seat> Seats = new List<Seat>();
        public readonly List<GameObject> ExtraTables = new List<GameObject>();
        bool kioskLook, tablesOwned;

        /// <summary>Stage-1 tables: one from the start, the other two with the "Mesas de plástico" upgrade; none once the exported kiosk model takes over.</summary>
        public void RefreshUpgrades(ResortGame game)
        {
            tablesOwned = game.Stall.Has("up.mesas");
            foreach (var t in ExtraTables) t.SetActive(tablesOwned && !kioskLook);
            foreach (var s in Seats) s.Enabled = !kioskLook && (!s.NeedsTables || tablesOwned);
        }

        public Seat TakeSeat()
        {
            var free = Seats.FindAll(s => s.Enabled && !s.Taken);
            if (free.Count == 0) return null;
            var seat = free[Random.Range(0, free.Count)];
            seat.Taken = true;
            return seat;
        }

        public Vector3 QueueSlot(int i) => Ground(new Vector3(Root.position.x, 0f, CounterFrontZ + 0.9f + i * 0.85f));
        public Vector3 Ground(Vector3 p) { p.y = Site.HeightAt(p.x, p.z); return p; }
        public Vector3 LanePoint(float x) => Ground(new Vector3(x, 0f, LaneZ));

        static readonly HashSet<string> StallLookParts = new HashSet<string>
        { "Deck", "Post", "Awning0", "Awning1", "Awning2", "Awning3", "Awning4", "Awning5", "Counter", "CounterTop", "Grill", "GrillGlow", "Cooler", "CoolerLid" };

        /// <summary>From stage 2 the exported kiosk model replaces the stall's look. The stations (counter, grill, crate, boards) keep their colliders and
        /// prompts at the same spots, so play is unchanged; only the structural visuals are hidden.</summary>
        public void SetKioskLook(bool kiosk)
        {
            kioskLook = kiosk;
            foreach (var r in Root.GetComponentsInChildren<Renderer>(true))
                if (StallLookParts.Contains(r.gameObject.name) || r.gameObject.name.StartsWith("S1_")) r.enabled = !kiosk;
            foreach (var t in Root.GetComponentsInChildren<TextMesh>(true))
                if (t.text == "LANCHES DO MAR") t.gameObject.SetActive(!kiosk);
            foreach (var s in Seats) s.Enabled = !kiosk && (!s.NeedsTables || tablesOwned);
            foreach (var t in ExtraTables) t.SetActive(tablesOwned && !kiosk);
        }

        public void RefreshStaff(ResortGame game)
        {
            foreach (var go in StaffVisuals) if (go != null) Object.Destroy(go);
            StaffVisuals.Clear();
            foreach (var s in game.Roster.Hired)
            {
                var pos = s.role == StaffRole.Cozinheiro ? CookPos : AttendantPos;
                // A second helper of the same role stands a step aside.
                int dup = StaffVisuals.Count > 0 && StaffVisuals.Exists(g => g.name.StartsWith(s.role.ToString())) ? 1 : 0;
                var rig = PersonRig.Create(new System.Random(s.name.GetHashCode()), PersonKind.Staff, s.name, StaffAgent.ColorFor(s));
                var go = rig.gameObject;
                go.transform.position = pos + Vector3.right * 0.9f * dup;
                go.name = s.role + ":" + s.name;
                go.transform.SetParent(Root, true);
                go.AddComponent<StaffAgent>().Init(game, s);
                StaffVisuals.Add(go);
            }
        }
    }

    /// <summary>Builds the beach stall procedurally (prototype art; replaced by authored models later). Everything is a primitive with a URP Lit colour.</summary>
    public static class StallBuilder
    {
        static readonly Dictionary<Color, Material> mats = new Dictionary<Color, Material>();

        public static Material Mat(Color c, float smooth = 0.15f, bool emissive = false)
        {
            var key = c; if (emissive) key.a = 0.5f;
            if (mats.TryGetValue(key, out var m) && m != null) return m;
            m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { color = c };
            m.SetColor("_BaseColor", c); m.SetFloat("_Smoothness", smooth);
            if (emissive) { m.EnableKeyword("_EMISSION"); m.SetColor("_EmissionColor", c * 1.6f); }
            mats[key] = m;
            return m;
        }

        public static GameObject Box(string name, Transform parent, Vector3 localPos, Vector3 size, Color color, bool collider = true, bool emissive = false)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cube);
            g.name = name;
            g.transform.SetParent(parent, false);
            g.transform.localPosition = localPos;
            g.transform.localScale = size;
            g.GetComponent<MeshRenderer>().sharedMaterial = Mat(color, 0.15f, emissive);
            if (!collider) Object.Destroy(g.GetComponent<Collider>());
            return g;
        }

        public static TextMesh Label(Transform parent, Vector3 localPos, string text, int size = 48, float scale = 0.05f)
        {
            var g = new GameObject("Label"); g.transform.SetParent(parent, false); g.transform.localPosition = localPos;
            var t = g.AddComponent<TextMesh>();
            t.text = text; t.fontSize = size; t.characterSize = scale; t.anchor = TextAnchor.MiddleCenter; t.alignment = TextAlignment.Center;
            t.color = Color.white;
            g.AddComponent<Billboard>();
            return t;
        }

        public static StallLayout Build(ResortGame game, ResortSite site, float x)
        {
            float promZ = site.PromenadeZ(x);
            float counterFront = promZ - 6f;                 // south edge of the stone promenade
            float z = counterFront - 1.2f;                    // stall origin: counter front sits 1.2 m ahead of it
            var rootGo = new GameObject("BeachStall");
            rootGo.transform.position = new Vector3(x, site.HeightAt(x, z), z);
            var root = rootGo.transform;

            var wood = new Color(0.50f, 0.36f, 0.22f); var wood2 = new Color(0.58f, 0.43f, 0.27f);
            var white = new Color(0.93f, 0.92f, 0.88f); var steel = new Color(0.45f, 0.47f, 0.5f);
            var zinc = new Color(0.56f, 0.58f, 0.59f); var zinc2 = new Color(0.64f, 0.66f, 0.66f);

            Box("Deck", root, new Vector3(0f, 0.05f, 0f), new Vector3(5.2f, 0.1f, 3.8f), wood2);
            foreach (var px in new[] { -2.4f, 2.4f }) foreach (var pz in new[] { -1.6f, 1.6f })
                Box("Post", root, new Vector3(px, 1.3f, pz), new Vector3(0.16f, 2.6f, 0.16f), wood, collider: false);
            // corrugated zinc roof (tilted slabs over timber rafters) - upgraded to a bigger one by "toldo"
            for (int i = 0; i < 6; i++)
            {
                var s = Box("Awning" + i, root, new Vector3(-2.2f + i * 0.88f, 2.65f, 0.1f), new Vector3(0.88f, 0.06f, 4.4f), i % 2 == 0 ? zinc : zinc2, collider: false);
                s.transform.localRotation = Quaternion.Euler(-6f, 0f, 0f);
            }
            // counter (front)
            var counter = Box("Counter", root, new Vector3(0f, 0.55f, 1.2f), new Vector3(4.2f, 1.1f, 0.7f), wood);
            Box("CounterTop", root, new Vector3(0f, 1.12f, 1.2f), new Vector3(4.4f, 0.06f, 0.85f), new Color(0.66f, 0.5f, 0.3f), collider: false);
            counter.AddComponent<CounterStation>();
            // grill (back left)
            var grill = Box("Grill", root, new Vector3(-1.5f, 0.45f, -1.0f), new Vector3(1.2f, 0.9f, 0.7f), steel);
            Box("GrillGlow", root, new Vector3(-1.5f, 0.93f, -1.0f), new Vector3(1.0f, 0.05f, 0.5f), new Color(1f, 0.45f, 0.1f), collider: false, emissive: true);
            grill.AddComponent<GrillStation>().holdSeconds = 3f;
            // chest freezer (back right); KioskDecor repaints it and makes it a stock-check station
            Box("Cooler", root, new Vector3(1.4f, 0.4f, -1.2f), new Vector3(1.1f, 0.8f, 0.6f), new Color(0.2f, 0.45f, 0.75f));
            Box("CoolerLid", root, new Vector3(1.4f, 0.83f, -1.2f), new Vector3(1.15f, 0.06f, 0.65f), white, collider: false);
            // supplier crate (market + upgrades)
            var crate = Box("SupplierCrate", root, new Vector3(2.0f, 0.3f, -0.1f), new Vector3(0.7f, 0.6f, 0.7f), wood2);
            Box("CrateSign", root, new Vector3(2.0f, 0.9f, -0.1f), new Vector3(0.5f, 0.25f, 0.05f), new Color(0.95f, 0.8f, 0.2f), collider: false);
            var market = crate.AddComponent<PanelStation>(); market.panel = Panel.Market; market.label = "Estoque, preços e melhorias";
            // open / close sign (the day starts closed: opening is a decision)
            var sign = Box("OpenSign", root, new Vector3(-2.45f, 1.25f, 1.15f), new Vector3(0.1f, 0.55f, 0.75f), new Color(0.2f, 0.62f, 0.3f));
            var act = sign.AddComponent<ActionStation>();
            act.prompt = g => g.ShopOpen ? "[E] Fechar o quiosque e conferir o caixa" : "[E] Abrir o quiosque";
            act.canUse = g => !g.Clock.DayOver && !g.AwaitingSleep;
            act.action = g => { if (g.ShopOpen) g.RequestClose(); else g.OpenShop(); };
            Label(root, new Vector3(-2.45f, 1.85f, 1.15f), "ABERTO / FECHADO", 36, 0.04f);
            // help board on a post
            var help = Box("HelpBoard", root, new Vector3(-2.4f, 1.1f, 0.4f), new Vector3(0.08f, 0.6f, 0.5f), new Color(0.15f, 0.3f, 0.2f));
            var hp = help.AddComponent<PanelStation>(); hp.panel = Panel.Help; hp.label = "Como jogar";
            // job board in front-right, on the promenade side
            var jobs = Box("JobBoard", root, new Vector3(3.6f, 1.0f, 1.9f), new Vector3(0.9f, 1.2f, 0.08f), new Color(0.94f, 0.9f, 0.7f));
            Box("JobPost", root, new Vector3(3.6f, 0.4f, 1.9f), new Vector3(0.08f, 0.8f, 0.08f), wood, collider: false);
            var jb = jobs.AddComponent<PanelStation>(); jb.panel = Panel.Hire; jb.label = "Mural de vagas (contratar)";
            Label(root, new Vector3(3.6f, 1.75f, 1.9f), "PRECISA-SE\nAJUDANTE", 40, 0.04f);
            Label(root, new Vector3(0f, 3.1f, 1.6f), "LANCHES DO MAR", 60, 0.07f);

            var layout = new StallLayout
            {
                Root = root, Site = site, PromenadeZ = promZ, CounterFrontZ = counterFront,
                LaneZ = promZ + 2.5f, WestX = Mathf.Max(8f, x - 75f), EastX = Mathf.Min(site.Data.size.x - 8f, x + 75f),
            };
            layout.PlayerSpawn = root.position + new Vector3(0f, 0.15f, -0.2f);
            layout.AttendantPos = root.position + new Vector3(0.8f, 0.1f, 0.35f);
            layout.CookPos = root.position + new Vector3(-1.3f, 0.1f, -0.2f);
            layout.PickupPos = layout.Ground(new Vector3(x + 2.9f, 0f, counterFront + 1.3f));
            KioskDecor.Dress(game, layout, root);
            layout.RefreshUpgrades(game);
            return layout;
        }
    }

    /// <summary>Keeps world-space labels facing the camera.</summary>
    public sealed class Billboard : MonoBehaviour
    {
        void LateUpdate()
        {
            var c = Camera.main;
            if (c != null) transform.rotation = Quaternion.LookRotation(transform.position - c.transform.position);
        }
    }
}
