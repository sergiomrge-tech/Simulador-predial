using System;
using ResortAurora.CameraSystem;
using ResortAurora.Grid;
using UnityEngine;

namespace ResortAurora.Site
{
    [Serializable]
    sealed class SiteData
    {
        [Serializable] public sealed class V2 { public float x, z; }
        [Serializable] public sealed class Pad { public int x, z, width, depth; public float height, cell; }
        public string name;
        public V2[] promenade;
        public V2 worldOrigin, size;
        public float step, seaLevel;
        public int columns, rows;
        public Pad pad;
    }

    /// <summary>
    /// Builds the Praia das Palmeiras build site from the exported heightfield (Tools/Map/export_resort_site.py):
    /// terrain mesh + collider, sea, and aligns the <see cref="GridManager"/> and camera limits to the flat build pad.
    /// Local frame: X east, Z north, origin at the site's south-west corner (sea side), so world positions match the masterplan offsets.
    /// </summary>
    public sealed class ResortSite : MonoBehaviour
    {
        [SerializeField] GridManager grid;
        [SerializeField] CameraController cameraController;
        [SerializeField] string resourcePath = "Resort/ResortSite";
        [SerializeField] string heightsPath = "Resort/ResortSiteHeights";

        public Vector3 PadCenter { get; private set; }
        public bool Ready { get; private set; }

        SiteData data;
        float[] heights;

        /// <summary>Ground height (bilinear over the exported heightfield). Cheap enough to call per agent per frame.</summary>
        public float HeightAt(float x, float z)
        {
            if (!Ready) return 0f;
            float fx = Mathf.Clamp(x / data.step, 0f, data.columns - 1.001f), fz = Mathf.Clamp(z / data.step, 0f, data.rows - 1.001f);
            int i = (int)fx, j = (int)fz; float tx = fx - i, tz = fz - j, n = data.columns;
            float a = heights[j * data.columns + i], b = heights[j * data.columns + i + 1];
            float c = heights[(j + 1) * data.columns + i], d = heights[(j + 1) * data.columns + i + 1];
            return Mathf.Lerp(Mathf.Lerp(a, b, tx), Mathf.Lerp(c, d, tx), tz);
        }

        /// <summary>Centre line of the promenade (stone walkway) at local X.</summary>
        public float PromenadeZ(float x) => PromenadeZ(data, x);

        static float PromenadeZ(SiteData d, float x)
        {
            var p = d.promenade;
            if (p == null || p.Length == 0) return 0f;
            if (x <= p[0].x) return p[0].z;
            for (int i = 1; i < p.Length; i++)
                if (x <= p[i].x) return Mathf.Lerp(p[i - 1].z, p[i].z, (x - p[i - 1].x) / Mathf.Max(0.001f, p[i].x - p[i - 1].x));
            return p[p.Length - 1].z;
        }

        void Awake() => Build();

        public void Build()
        {
            var json = Resources.Load<TextAsset>(resourcePath);
            var bytes = Resources.Load<TextAsset>(heightsPath);
            if (json == null || bytes == null) { Debug.LogError("ResortSite: exported site data not found in Resources/Resort."); return; }
            var d = JsonUtility.FromJson<SiteData>(json.text);
            heights = new float[d.columns * d.rows];
            Buffer.BlockCopy(bytes.bytes, 0, heights, 0, heights.Length * sizeof(float));

            data = d; Ready = true;
            var terrain = BuildTerrain(d, heights);
            terrain.transform.SetParent(transform, false);
            BuildSea(d).transform.SetParent(transform, false);

            // Grid lies on the flat pad; cell (0,0) is its south-west corner.
            if (grid != null)
            {
                grid.transform.position = new Vector3(d.pad.x, d.pad.height, d.pad.z);
                grid.Configure(new Vector2Int(Mathf.RoundToInt(d.pad.width / d.pad.cell), Mathf.RoundToInt(d.pad.depth / d.pad.cell)), d.pad.cell);
            }
            PadCenter = new Vector3(d.pad.x + d.pad.width * 0.5f, d.pad.height, d.pad.z + d.pad.depth * 0.5f);
            if (cameraController != null)
            {
                cameraController.SetBounds(new Vector2(0f, d.size.x), new Vector2(0f, d.size.z));
                cameraController.transform.position = PadCenter;
                cameraController.FocusOn(PadCenter);
            }
        }

        static GameObject BuildTerrain(SiteData d, float[] h)
        {
            int nx = d.columns, nz = d.rows;
            var verts = new Vector3[nx * nz];
            var uv = new Vector2[nx * nz];
            for (int j = 0; j < nz; j++)
                for (int i = 0; i < nx; i++)
                {
                    int k = j * nx + i;
                    verts[k] = new Vector3(i * d.step, h[k], j * d.step);
                    uv[k] = new Vector2(i / (float)(nx - 1), j / (float)(nz - 1));
                }
            var tris = new int[(nx - 1) * (nz - 1) * 6];
            int t = 0;
            for (int j = 0; j < nz - 1; j++)
                for (int i = 0; i < nx - 1; i++)
                {
                    int a = j * nx + i, b = a + 1, c = a + nx, e = c + 1;
                    tris[t++] = a; tris[t++] = c; tris[t++] = b;   // clockwise seen from above (Unity front face)
                    tris[t++] = b; tris[t++] = c; tris[t++] = e;
                }
            var mesh = new Mesh { name = "ResortSiteTerrain", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.vertices = verts; mesh.uv = uv; mesh.triangles = tris;
            mesh.RecalculateNormals(); mesh.RecalculateBounds();

            var go = new GameObject("Terrain");
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = TerrainMaterial(d, h);
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
            return go;
        }

        /// <summary>Prototype shading: a colour map from height/slope (sand, grass, the paved pad). Replaced by PBR splat later.</summary>
        static Material TerrainMaterial(SiteData d, float[] h)
        {
            int nx = d.columns, nz = d.rows;
            var tex = new Texture2D(nx, nz, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear };
            var px = new Color[nx * nz];
            var sand = new Color(0.86f, 0.78f, 0.58f);
            var wet = new Color(0.62f, 0.55f, 0.40f);
            var grass = new Color(0.34f, 0.46f, 0.22f);
            var pad = new Color(0.55f, 0.55f, 0.52f);
            for (int j = 0; j < nz; j++)
                for (int i = 0; i < nx; i++)
                {
                    float y = h[j * nx + i];
                    float wx = i * d.step, wz = j * d.step;
                    Color c = y < 0.5f ? Color.Lerp(wet, sand, Mathf.InverseLerp(-1f, 0.5f, y)) : Color.Lerp(sand, grass, Mathf.InverseLerp(2.6f, 4.2f, y));
                    bool inPad = wx >= d.pad.x && wx <= d.pad.x + d.pad.width && wz >= d.pad.z && wz <= d.pad.z + d.pad.depth;
                    if (inPad) c = Color.Lerp(c, pad, 0.55f);
                    if (Mathf.Abs(wz - PromenadeZ(d, wx)) < 6f) c = new Color(0.72f, 0.70f, 0.66f); // stone promenade
                    px[j * nx + i] = c;
                }
            tex.SetPixels(px); tex.Apply();
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "ResortSiteTerrain" };
            m.SetTexture("_BaseMap", tex);
            m.SetFloat("_Smoothness", 0.05f);
            return m;
        }

        static GameObject BuildSea(SiteData d)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Plane);
            go.name = "Sea";
            Destroy(go.GetComponent<Collider>());
            // Plane primitive is 10x10 units; cover the whole site width and the part seaward of the beach (to z = 140 m).
            go.transform.localScale = new Vector3(d.size.x / 10f, 1f, 140f / 10f);
            go.transform.localPosition = new Vector3(d.size.x * 0.5f, d.seaLevel, 70f);
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "ResortSea" };
            m.SetColor("_BaseColor", new Color(0.05f, 0.35f, 0.45f, 1f));
            m.SetFloat("_Smoothness", 0.92f);
            go.GetComponent<MeshRenderer>().sharedMaterial = m;
            return go;
        }
    }
}
