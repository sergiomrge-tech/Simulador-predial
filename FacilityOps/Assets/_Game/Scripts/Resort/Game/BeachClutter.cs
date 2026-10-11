using System.Collections.Generic;
using ResortAurora.Site;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Permanent beach dressing (Phase 02 "living world"): rented umbrellas with towels, bags and sandals, sandcastles, driftwood on the
    /// high-tide line. It costs nothing from the 70-person ambient budget of <see cref="BeachLife"/> and keeps the open sand beside the
    /// kiosk from reading as empty. Everything is collider-free and each cluster is switched off beyond <see cref="ShowRange"/>.
    /// </summary>
    public sealed class BeachClutter : MonoBehaviour
    {
        const float ShowRange = 80f;
        static readonly Color Sand = new Color(0.80f, 0.70f, 0.48f);
        static readonly Color[] Fabrics =
        {
            new Color(0.93f, 0.40f, 0.30f), new Color(0.25f, 0.55f, 0.82f), new Color(0.96f, 0.82f, 0.30f),
            new Color(0.35f, 0.72f, 0.58f), new Color(0.90f, 0.90f, 0.86f), new Color(0.84f, 0.45f, 0.70f)
        };
        static readonly Color[] Umbrellas =
        {
            new Color(0.97f, 0.80f, 0.15f), new Color(0.95f, 0.95f, 0.92f), new Color(0.2f, 0.42f, 0.8f), new Color(0.92f, 0.35f, 0.25f)
        };

        sealed class Cluster { public GameObject go; public Vector3 pos; }

        readonly List<Cluster> clusters = new List<Cluster>();
        readonly List<Vector3> taken = new List<Vector3>();
        ResortSite site; System.Random rng; float sx, kioskZ, timer;
        Transform cam;

        public int Count => clusters.Count;
        public int UmbrellaCount { get; private set; }

        public void Init(ResortGame g, IEnumerable<Vector3> reserved)
        {
            site = g.Site; sx = g.Layout.Root.position.x; kioskZ = g.Layout.Root.position.z;
            rng = new System.Random(g.Seed * 17 + 3);
            taken.AddRange(reserved);
            for (int i = 0; i < 12; i++) Place(Umbrella, 36f + i * 5f, 5.2f);
            for (int i = 0; i < 6; i++) Place(Sandcastle, 60f, 3.5f);
            for (int i = 0; i < 4; i++) Place(Bag, 60f, 3.2f);
            for (int i = 0; i < 9; i++) PlaceDriftwood();
        }

        /// <summary>Picks a dry-sand spot clear of the kiosk, the ambient beach spots and earlier clutter, then builds the cluster there.</summary>
        void Place(System.Func<Transform, GameObject> build, float halfWidth, float clearance)
        {
            for (int tries = 0; tries < 80; tries++)
            {
                float x = sx + ((float)rng.NextDouble() - 0.5f) * 2f * halfWidth;
                float edge = site.PromenadeZ(x) - 6f, shore = site.WaterlineZ(x);
                float u = Mathf.Pow((float)rng.NextDouble(), 1.6f);
                float z = edge - 5f - u * Mathf.Max(4f, edge - shore - 10f);
                if (Accept(x, z, clearance)) { Add(build, x, z); return; }
            }
        }

        void PlaceDriftwood()
        {
            for (int tries = 0; tries < 80; tries++)
            {
                float x = sx + ((float)rng.NextDouble() - 0.5f) * 2f * 90f;
                float z = site.WaterlineZ(x) + 2f + (float)rng.NextDouble() * 3.5f;
                if (Accept(x, z, 4f)) { Add(Driftwood, x, z); return; }
            }
        }

        bool Accept(float x, float z, float clearance)
        {
            if (site.HeightAt(x, z) < 0.45f) return false;                                  // wet sand
            if (x > sx - 13f && x < sx + 14f && z > kioskZ - 16f) return false;             // the kiosk, its tables and its queue
            foreach (var t in taken) if ((t.x - x) * (t.x - x) + (t.z - z) * (t.z - z) < clearance * clearance) return false;
            return true;
        }

        void Add(System.Func<Transform, GameObject> build, float x, float z)
        {
            var pos = new Vector3(x, site.HeightAt(x, z), z);
            var root = new GameObject("BeachCluster"); root.transform.SetParent(transform, false);
            root.transform.SetPositionAndRotation(pos, Quaternion.Euler(0f, 180f + ((float)rng.NextDouble() - 0.5f) * 70f, 0f));
            build(root.transform);
            taken.Add(pos);
            clusters.Add(new Cluster { go = root, pos = pos });
        }

        // ---------------------------------------------------------------- cluster builders (local space: +z faces the sea after the yaw)

        GameObject Umbrella(Transform root)
        {
            UmbrellaCount++;
            var pole = StallBuilder.Box("Pole", root, new Vector3(0f, 1.1f, 0f), new Vector3(0.04f, 2.2f, 0.04f), new Color(0.82f, 0.82f, 0.8f), collider: false);
            pole.transform.localRotation = Quaternion.Euler(0f, 0f, -5f);
            var canopy = new GameObject("Canopy"); canopy.transform.SetParent(root, false);
            canopy.transform.localPosition = new Vector3(-0.05f, 2.1f, 0f); canopy.transform.localRotation = Quaternion.Euler(0f, rng.Next(360), -5f);
            canopy.AddComponent<MeshFilter>().sharedMesh = BeachLife.MakeUmbrella();
            canopy.AddComponent<MeshRenderer>().sharedMaterial = RealisticKioskAssets.CanopyMaterial(Umbrellas[rng.Next(Umbrellas.Length)]);
            int towels = 1 + rng.Next(2);
            for (int i = 0; i < towels; i++)
            {
                var fabric = Fabrics[rng.Next(Fabrics.Length)];
                var t = StallBuilder.Box("Towel", root, new Vector3(-0.55f + i * 1.0f, 0.012f, 0.55f), new Vector3(0.8f, 0.02f, 1.7f), fabric, collider: false);
                t.transform.localRotation = Quaternion.Euler(0f, (float)(rng.NextDouble() - 0.5) * 14f, 0f);
                if (rng.NextDouble() < 0.5)                                                  // a stripe
                    StallBuilder.Box("Stripe", t.transform, new Vector3(0f, 0.6f, 0.12f), new Vector3(1.01f, 0.6f, 0.14f), Color.Lerp(fabric, Color.white, 0.7f), collider: false);
            }
            if (rng.NextDouble() < 0.8) BagAt(root, new Vector3(0.7f, 0f, -0.2f));
            Sandals(root, new Vector3(-0.2f, 0f, 1.6f));
            return root.gameObject;
        }

        GameObject Bag(Transform root)
        {
            var fabric = Fabrics[rng.Next(Fabrics.Length)];
            var t = StallBuilder.Box("Towel", root, new Vector3(0f, 0.012f, 0f), new Vector3(0.9f, 0.02f, 1.7f), fabric, collider: false);
            t.transform.localRotation = Quaternion.Euler(0f, (float)(rng.NextDouble() - 0.5) * 20f, 0f);
            BagAt(root, new Vector3(0.1f, 0f, -0.55f));
            Sandals(root, new Vector3(0.45f, 0f, 0.85f));
            return root.gameObject;
        }

        void BagAt(Transform root, Vector3 p)
        {
            var c = Fabrics[rng.Next(Fabrics.Length)] * 0.8f; c.a = 1f;
            StallBuilder.Box("Bag", root, p + new Vector3(0f, 0.17f, 0f), new Vector3(0.46f, 0.34f, 0.24f), c, collider: false);
            StallBuilder.Box("BagStrap", root, p + new Vector3(0f, 0.36f, 0f), new Vector3(0.28f, 0.03f, 0.03f), c * 0.6f, collider: false);
        }

        void Sandals(Transform root, Vector3 p)
        {
            var c = Fabrics[rng.Next(Fabrics.Length)];
            for (int i = 0; i < 2; i++)
            {
                var s = StallBuilder.Box("Sandal", root, p + new Vector3(i * 0.16f, 0.02f, i * 0.05f), new Vector3(0.1f, 0.03f, 0.26f), c, collider: false);
                s.transform.localRotation = Quaternion.Euler(0f, (i == 0 ? 8f : -14f), 0f);
            }
        }

        GameObject Sandcastle(Transform root)
        {
            var wall = Sand * 0.96f; wall.a = 1f;
            Cylinder(root, new Vector3(0f, 0.09f, 0f), new Vector3(0.9f, 0.09f, 0.9f), Sand);
            Cylinder(root, new Vector3(0f, 0.26f, 0f), new Vector3(0.55f, 0.1f, 0.55f), wall);
            for (int i = 0; i < 4; i++)
            {
                float a = i * Mathf.PI * 0.5f + 0.4f;
                Cylinder(root, new Vector3(Mathf.Cos(a) * 0.5f, 0.2f, Mathf.Sin(a) * 0.5f), new Vector3(0.2f, 0.16f, 0.2f), wall);
            }
            var flagPole = StallBuilder.Box("Flag", root, new Vector3(0f, 0.55f, 0f), new Vector3(0.012f, 0.5f, 0.012f), new Color(0.8f, 0.75f, 0.6f), collider: false);
            StallBuilder.Box("FlagCloth", flagPole.transform, new Vector3(8f, 0.38f, 0f), new Vector3(14f, 0.24f, 1f), Fabrics[rng.Next(Fabrics.Length)], collider: false);
            return root.gameObject;
        }

        static void Cylinder(Transform root, Vector3 pos, Vector3 halfScale, Color c)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            g.name = "Mound"; g.transform.SetParent(root, false);
            g.transform.localPosition = pos; g.transform.localScale = new Vector3(halfScale.x, halfScale.y, halfScale.z);
            g.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(c, 0.05f);
            Destroy(g.GetComponent<Collider>());
        }

        GameObject Driftwood(Transform root)
        {
            var bark = new Color(0.42f + (float)rng.NextDouble() * 0.1f, 0.36f, 0.30f);
            int logs = 1 + rng.Next(3);
            for (int i = 0; i < logs; i++)
            {
                float len = 0.9f + (float)rng.NextDouble() * 1.8f, d = 0.07f + (float)rng.NextDouble() * 0.09f;
                var log = StallBuilder.Box("Log", root, new Vector3(i * 0.35f, d * 0.5f, i * 0.25f), new Vector3(d, d, len), bark, collider: false);
                log.transform.localRotation = Quaternion.Euler((float)(rng.NextDouble() - 0.5) * 8f, (float)(rng.NextDouble() - 0.5) * 70f, 0f);
            }
            return root.gameObject;
        }

        // ---------------------------------------------------------------- distance culling

        void Update()
        {
            timer -= Time.deltaTime;
            if (timer > 0f) return;
            timer = 0.5f;
            if (cam == null) { var c = Camera.main; if (c == null) return; cam = c.transform; }
            float r2 = ShowRange * ShowRange;
            foreach (var c in clusters)
            {
                float dx = c.pos.x - cam.position.x, dz = c.pos.z - cam.position.z;
                bool on = dx * dx + dz * dz < r2;
                if (c.go.activeSelf != on) c.go.SetActive(on);
            }
        }
    }
}
