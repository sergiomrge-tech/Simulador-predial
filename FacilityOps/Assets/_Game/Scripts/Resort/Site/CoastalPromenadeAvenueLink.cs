using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Site
{
    /// <summary>
    /// Continuous coastal pedestrian esplanade connecting the existing beach promenade
    /// to the seaward edge of the avenue, leaving precisely one metre for the curb buffer.
    /// The avenue, urban intersections, kiosk, parcels and gameplay stay in place.
    /// </summary>
    public static class CoastalPromenadeAvenueLink
    {
        public const float AvenueBufferMetres = 1f;
        const float ExistingPromenadeHalfWidth = 5.95f;
        const float XStep = 1.5f;
        const float ZStep = 1f;

        public static float RoadEdge(SiteData data) =>
            data.avenue.z - data.avenue.width * .5f;

        public static float LinkEnd(SiteData data) => RoadEdge(data) - AvenueBufferMetres;

        public static float LinkStart(ResortSite site, float x) =>
            site.PromenadeZ(x) + ExistingPromenadeHalfWidth - .04f;

        public static void Build(ResortSite site)
        {
            if (site == null || site.Data == null || site.Data.avenue == null) return;
            float endZ = LinkEnd(site.Data);
            float largest = 0f;
            for (float x = 0; x <= site.Data.size.x; x += 3f)
                largest = Mathf.Max(largest, endZ - LinkStart(site, x));
            if (largest <= .15f) return;

            int columns = Mathf.CeilToInt(site.Data.size.x / XStep) + 1;
            int rows = Mathf.CeilToInt(largest / ZStep) + 1;
            var v = new Vector3[columns * rows];
            var uv = new Vector2[v.Length];
            for (int i = 0; i < columns; i++)
            {
                float x = Mathf.Min(i * XStep, site.Data.size.x);
                float startZ = LinkStart(site, x);
                if (endZ < startZ) startZ = endZ;
                for (int j = 0; j < rows; j++)
                {
                    float u = j / (float)(rows - 1);
                    float z = Mathf.Lerp(startZ, endZ, u);
                    float lift = Mathf.Lerp(.02f, .115f, Mathf.SmoothStep(0f, 1f, u));
                    int k = i * rows + j;
                    v[k] = new Vector3(x, site.HeightAt(x, z) + lift, z);
                    uv[k] = new Vector2(x, z) / 2f;
                }
            }
            var t = new int[(columns - 1) * (rows - 1) * 6];
            int idx = 0;
            for (int i = 0; i < columns - 1; i++)
                for (int j = 0; j < rows - 1; j++)
                {
                    int a = i * rows + j, b = a + rows, c = a + 1, d = b + 1;
                    t[idx++] = a; t[idx++] = c; t[idx++] = b;
                    t[idx++] = b; t[idx++] = c; t[idx++] = d;
                }
            var mesh = new Mesh {
                name = "PromenadeAvenueLink_1mBuffer",
                indexFormat = IndexFormat.UInt32, vertices = v, uv = uv, triangles = t
            };
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();

            var obj = new GameObject("PromenadeAvenueLink_1mBuffer");
            obj.transform.SetParent(site.transform, false);
            obj.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = obj.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = ResortSurfaceMaterials.Create("pedra_portuguesa",
                new Color(.95f, .93f, .88f), 2f);
            renderer.shadowCastingMode = ShadowCastingMode.Off;

            // The last metre is a thin planting/curb strip. It has no collider
            // and does not move, bury or widen the drivable avenue.
            var strip = new GameObject("CoastalAvenueBuffer_Exactly1m");
            strip.transform.SetParent(site.transform, false);
            var stripMesh = new Mesh {
                name = "CoastalAvenueBuffer_Exactly1m",
                indexFormat = IndexFormat.UInt32
            };
            var sv = new Vector3[columns * 2];
            var suv = new Vector2[sv.Length];
            var st = new int[(columns - 1) * 6]; int n = 0;
            for (int i = 0; i < columns; i++)
            {
                float x = Mathf.Min(i * XStep, site.Data.size.x);
                sv[i * 2] = new Vector3(x, site.HeightAt(x, endZ) + .12f, endZ);
                sv[i * 2 + 1] = new Vector3(x, site.HeightAt(x, endZ + AvenueBufferMetres) + .12f,
                    endZ + AvenueBufferMetres);
                suv[i * 2] = new Vector2(x / 2f, 0f);
                suv[i * 2 + 1] = new Vector2(x / 2f, .5f);
                if (i == columns - 1) continue;
                int a = i * 2, b = a + 2;
                st[n++] = a; st[n++] = a + 1; st[n++] = b;
                st[n++] = b; st[n++] = a + 1; st[n++] = b + 1;
            }
            stripMesh.vertices = sv; stripMesh.uv = suv; stripMesh.triangles = st;
            stripMesh.RecalculateNormals(); stripMesh.RecalculateBounds();
            strip.AddComponent<MeshFilter>().sharedMesh = stripMesh;
            var stripRenderer = strip.AddComponent<MeshRenderer>();
            stripRenderer.sharedMaterial = ResortSurfaceMaterials.Create("urban_concrete",
                new Color(.76f, .75f, .70f), 2f);
            stripRenderer.shadowCastingMode = ShadowCastingMode.Off;
            Debug.Log($"COASTAL_1M avenueEdge={RoadEdge(site.Data):0.00} " +
                $"promenadeEnd={endZ:0.00} buffer={AvenueBufferMetres:0.00}");
        }
    }
}
