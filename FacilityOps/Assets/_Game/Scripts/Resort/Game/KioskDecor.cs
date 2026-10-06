using System.Text;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>A place to sit near the stall (plastic table on the sand). Customers who have been served may take a free one and drink there.</summary>
    public sealed class Seat
    {
        public Vector3 Pos; public float Yaw; public bool Taken, Enabled = true, NeedsTables;
    }

    /// <summary>
    /// Dresses the first-stage stall after REF 01/02: weathered plank counter and back wall, corrugated roof on rafters, shelves of bottles, an upright
    /// fridge and a chest freezer (both usable to check stock), a snack rack, crates, bin, cash register, string bulbs and a plastic table set
    /// on the sand with umbrellas. Everything dressing the structure is named "S1_*" so stage 2 (the exported kiosk model) can hide it, while the
    /// stations (fridge, freezer, counter) keep their colliders and prompts.
    /// </summary>
    public static class KioskDecor
    {
        static readonly Color W1 = new Color(0.50f, 0.36f, 0.22f), W2 = new Color(0.60f, 0.45f, 0.28f), W3 = new Color(0.42f, 0.30f, 0.18f);
        static readonly Color White = new Color(0.93f, 0.94f, 0.95f), Yellow = new Color(0.97f, 0.80f, 0.12f), Dark = new Color(0.14f, 0.15f, 0.16f);
        static readonly Color[] Bottles =
        {
            new Color(0.20f, 0.50f, 0.25f), new Color(0.70f, 0.40f, 0.10f), new Color(0.75f, 0.85f, 0.90f), new Color(0.75f, 0.15f, 0.12f),
            new Color(0.90f, 0.50f, 0.15f), new Color(0.12f, 0.10f, 0.10f), new Color(0.95f, 0.85f, 0.2f),
        };

        static GameObject Cyl(string name, Transform p, Vector3 pos, float d, float h, Color c)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            g.name = name; g.transform.SetParent(p, false); g.transform.localPosition = pos; g.transform.localScale = new Vector3(d, h * 0.5f, d);
            g.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(c, 0.25f);
            Object.Destroy(g.GetComponent<Collider>());
            return g;
        }

        static Color Plank(int i) => (i % 3) switch { 0 => W1, 1 => W2, _ => W3 };

        public static void Dress(ResortGame game, StallLayout layout, Transform root)
        {
            GameObject b(string n, Transform p, Vector3 pos, Vector3 size, Color c, bool collider = true, bool emissive = false) => StallBuilder.Box(n, p, pos, size, c, collider, emissive);

            // roof frame under the corrugated slabs
            foreach (var z in new[] { -1.95f, 1.95f }) b("S1_Beam", root, new Vector3(0f, 2.5f, z), new Vector3(5.6f, 0.13f, 0.13f), W3, collider: false);
            for (int i = 0; i < 7; i++) b("S1_Rafter", root, new Vector3(-2.6f + i * 0.87f, 2.55f, 0f), new Vector3(0.08f, 0.1f, 4.2f), W1, collider: false);
            for (int i = 0; i < 4; i++)
            {
                var br = b("S1_Brace", root, new Vector3(i < 2 ? -2.45f : 2.45f, 2.2f, i % 2 == 0 ? -1.5f : 1.5f), new Vector3(0.07f, 0.07f, 0.8f), W2, collider: false);
                br.transform.localRotation = Quaternion.Euler(i % 2 == 0 ? 35f : -35f, 0f, 0f);
            }

            // plank counter front and back wall
            for (int i = 0; i < 15; i++) b("S1_CounterPlank", root, new Vector3(-2.0f + i * 0.286f, 0.52f, 1.57f), new Vector3(0.27f, 1.02f, 0.03f), Plank(i), collider: false);
            for (int i = 0; i < 17; i++) b("S1_WallPlank", root, new Vector3(-2.4f + i * 0.3f, 1.15f, -1.9f), new Vector3(0.28f, 2.3f, 0.04f), Plank(i + 1), collider: false);
            var wall = new GameObject("BackWall"); wall.transform.SetParent(root, false); wall.transform.localPosition = new Vector3(0f, 1.2f, -1.97f);
            wall.AddComponent<BoxCollider>().size = new Vector3(5.1f, 2.4f, 0.12f);

            // shelves with bottles
            foreach (var y in new[] { 1.32f, 1.78f })
            {
                b("S1_Shelf", root, new Vector3(-1.45f, y, -1.72f), new Vector3(1.9f, 0.04f, 0.3f), W2, collider: false);
                for (int i = 0; i < 12; i++)
                {
                    var c = Bottles[(i * 3 + (int)(y * 10)) % Bottles.Length];
                    Cyl("S1_Bottle", root, new Vector3(-2.3f + i * 0.145f, y + 0.15f, -1.72f), 0.075f, 0.26f, c);
                }
            }
            // cash register and condiments on the counter
            b("S1_Register", root, new Vector3(0.9f, 1.26f, 1.1f), new Vector3(0.38f, 0.22f, 0.32f), Dark, collider: false);
            var screen = b("S1_RegisterScreen", root, new Vector3(0.9f, 1.46f, 1.0f), new Vector3(0.28f, 0.2f, 0.03f), new Color(0.2f, 0.5f, 0.45f), collider: false, emissive: true);
            screen.transform.localRotation = Quaternion.Euler(-12f, 0f, 0f);
            Cyl("S1_Ketchup", root, new Vector3(-0.25f, 1.25f, 1.1f), 0.06f, 0.22f, new Color(0.8f, 0.12f, 0.1f));
            Cyl("S1_Mustard", root, new Vector3(-0.1f, 1.25f, 1.1f), 0.06f, 0.22f, Yellow);
            for (int i = 0; i < 4; i++)
            {
                var coco = GameObject.CreatePrimitive(PrimitiveType.Sphere); coco.name = "S1_Coconut"; coco.transform.SetParent(root, false);
                coco.transform.localPosition = new Vector3(-1.2f + (i % 2) * 0.22f, 1.25f + (i / 2) * 0.17f, 1.1f); coco.transform.localScale = Vector3.one * 0.2f;
                coco.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(new Color(0.35f, 0.55f, 0.22f), 0.3f); Object.Destroy(coco.GetComponent<Collider>());
            }

            // upright fridge (glass door, lit) - station: check the cold drinks
            var fridge = b("S1_Fridge", root, new Vector3(0.35f, 0.95f, -1.5f), new Vector3(0.85f, 1.9f, 0.7f), White);
            var glass = b("S1_FridgeGlass", root, new Vector3(0.35f, 0.95f, -1.14f), new Vector3(0.7f, 1.6f, 0.02f), new Color(0.12f, 0.22f, 0.27f), collider: false, emissive: true);
            glass.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(new Color(0.22f, 0.4f, 0.46f), 0.9f, true);
            for (int row = 0; row < 4; row++) for (int i = 0; i < 5; i++)
                Cyl("S1_FridgeBottle", root, new Vector3(0.12f + i * 0.115f, 0.35f + row * 0.38f, -1.12f), 0.07f, 0.24f, Bottles[(row * 2 + i) % Bottles.Length]);
            var fs = fridge.AddComponent<ActionStation>();
            fs.prompt = g => "[E] Conferir a geladeira: " + StockLine(g, "drink.");
            fs.action = g => g.Say("Geladeira: " + StockLine(g, "drink."), 5f);

            // chest freezer: the existing "Cooler" box becomes the freezer - station: check the ice creams
            var freezer = root.Find("Cooler");
            if (freezer != null)
            {
                freezer.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(White, 0.3f);
                var fz = freezer.gameObject.AddComponent<ActionStation>();
                fz.prompt = g => "[E] Conferir o freezer: " + StockLine(g, "sweet.");
                fz.action = g => g.Say("Freezer: " + StockLine(g, "sweet."), 5f);
            }
            var lid = root.Find("CoolerLid"); if (lid != null) lid.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(new Color(0.78f, 0.8f, 0.82f), 0.3f);

            // snack rack, crates, bin
            var rack = b("S1_SnackRack", root, new Vector3(2.15f, 0.9f, -1.68f), new Vector3(0.45f, 1.8f, 0.3f), W3);
            var rs = rack.AddComponent<ActionStation>();
            rs.prompt = g => "[E] Conferir a prateleira: " + StockLine(g, "food.");
            rs.action = g => g.Say("Prateleira: " + StockLine(g, "food."), 5f);
            for (int row = 0; row < 3; row++) for (int i = 0; i < 3; i++)
                b("S1_Snack", root, new Vector3(2.0f + i * 0.14f, 0.6f + row * 0.5f, -1.5f), new Vector3(0.11f, 0.2f, 0.04f), Bottles[(row + i * 2) % Bottles.Length], collider: false);
            Color[] crate = { new Color(0.18f, 0.32f, 0.7f), new Color(0.75f, 0.18f, 0.15f), new Color(0.2f, 0.5f, 0.28f) };
            for (int i = 0; i < 5; i++) b("S1_Crate", root, new Vector3(2.35f + (i % 2) * 0.02f, 0.15f + (i / 2) * 0.28f, 0.65f + (i % 2) * 0.35f), new Vector3(0.5f, 0.27f, 0.36f), crate[i % 3], collider: false);
            Cyl("S1_Bin", root, new Vector3(-2.2f, 0.4f, -1.55f), 0.45f, 0.8f, new Color(0.17f, 0.18f, 0.19f));

            // string bulbs under the roof (they light up at night)
            var day = game.DayNight;
            foreach (var x in new[] { -1.6f, 0f, 1.6f })
            {
                if (day != null) { day.LampHead(root, new Vector3(x, 2.35f, 0.9f), 0.2f); day.AddLamp(root.position + new Vector3(x, 2.3f, 0.9f), 9f, 1.9f); }
                b("S1_Wire", root, new Vector3(x, 2.47f, 0.9f), new Vector3(0.015f, 0.2f, 0.015f), Dark, collider: false);
            }
            if (day != null) day.AddLamp(root.position + new Vector3(0f, 2.2f, -1.2f), 8f, 1.4f);       // work light over the grill and fridge

            // plastic table set on the sand, east of the stall (table 1 from the start, tables 2 and 3 with the "Mesas" upgrade)
            Table(layout, root, new Vector3(5.0f, 0f, -0.6f), false);
            Table(layout, root, new Vector3(7.5f, 0f, -2.3f), true);
            Table(layout, root, new Vector3(4.7f, 0f, -4.4f), true);
            // rope and post fence along the beach side, as in REF 01
            for (int i = 0; i < 6; i++)
            {
                float x = -8f + i * 3.2f; if (x > -2f && x < 11f) continue;
                var post = b("S1_FencePost", root, new Vector3(x, 0.45f, -5.8f), new Vector3(0.16f, 0.9f, 0.16f), new Color(0.45f, 0.34f, 0.22f), collider: false);
                post.name = "S1_FencePost";
            }
        }

        static void Table(StallLayout layout, Transform root, Vector3 local, bool extra)
        {
            GameObject b(string n, Transform p, Vector3 pos, Vector3 size, Color c, bool collider) => StallBuilder.Box(n, p, pos, size, c, collider);
            var t = new GameObject(extra ? "S1_TableExtra" : "S1_Table"); t.transform.SetParent(root, false); t.transform.localPosition = local;
            var yellow = new Color(0.97f, 0.80f, 0.12f);
            b("S1_TableTop", t.transform, new Vector3(0f, 0.72f, 0f), new Vector3(0.95f, 0.045f, 0.95f), yellow, true);
            foreach (var sx in new[] { -0.4f, 0.4f }) foreach (var sz in new[] { -0.4f, 0.4f })
                b("S1_TableLeg", t.transform, new Vector3(sx, 0.36f, sz), new Vector3(0.05f, 0.72f, 0.05f), yellow, false);
            // ketchup and mustard on every table
            Cyl("S1_Bottle", t.transform, new Vector3(-0.2f, 0.84f, 0.15f), 0.06f, 0.2f, new Color(0.8f, 0.12f, 0.1f));
            Cyl("S1_Bottle", t.transform, new Vector3(-0.08f, 0.84f, 0.15f), 0.06f, 0.2f, yellow);
            foreach (var side in new[] { -1f, 1f })
            {
                var c = new GameObject("S1_Chair"); c.transform.SetParent(t.transform, false); c.transform.localPosition = new Vector3(side * 0.78f, 0f, 0f);
                var col = side < 0 ? new Color(0.95f, 0.95f, 0.93f) : yellow;
                b("S1_ChairSeat", c.transform, new Vector3(0f, 0.45f, 0f), new Vector3(0.44f, 0.045f, 0.44f), col, false);
                b("S1_ChairBack", c.transform, new Vector3(side * 0.2f, 0.72f, 0f), new Vector3(0.04f, 0.5f, 0.44f), col, false);
                foreach (var lx in new[] { -0.18f, 0.18f }) foreach (var lz in new[] { -0.18f, 0.18f })
                    b("S1_ChairLeg", c.transform, new Vector3(lx, 0.22f, lz), new Vector3(0.04f, 0.44f, 0.04f), col, false);
                // the seat faces the table: yaw 90 for a chair west of it (looking east), 270 for the east one
                var ws = root.TransformPoint(local + new Vector3(side * 0.78f, 0f, 0f));
                layout.Seats.Add(new Seat { Pos = layout.Ground(ws), Yaw = side < 0 ? 90f : 270f, NeedsTables = extra, Enabled = !extra });
            }
            // umbrella over the table
            var pole = b("S1_UmbrellaPole", t.transform, new Vector3(0f, 1.15f, 0f), new Vector3(0.04f, 2.3f, 0.04f), new Color(0.8f, 0.8f, 0.78f), false);
            var canopy = new GameObject("S1_Umbrella"); canopy.transform.SetParent(t.transform, false); canopy.transform.localPosition = new Vector3(0f, 2.25f, 0f);
            canopy.AddComponent<MeshFilter>().sharedMesh = BeachLife.MakeUmbrella();
            canopy.AddComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(extra ? new Color(0.95f, 0.95f, 0.92f) : yellow, 0.2f);
            canopy.transform.localScale = Vector3.one * 1.05f;
            if (extra) { t.SetActive(false); layout.ExtraTables.Add(t); }
        }

        /// <summary>"Água 12, Refrigerante 8, ..." for the products whose id starts with <paramref name="prefix"/>.</summary>
        static string StockLine(ResortGame g, string prefix)
        {
            var sb = new StringBuilder(); bool any = false;
            foreach (var p in Catalog.Products)
            {
                if (!p.Id.StartsWith(prefix)) continue;
                int n = g.Stall.Stock(p.Id);
                if (any) sb.Append(", ");
                sb.Append(p.Name).Append(' ').Append(n); any = true;
            }
            return any ? sb.ToString() : "vazio";
        }
    }
}
