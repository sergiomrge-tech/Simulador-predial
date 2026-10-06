using System;
using System.Collections.Generic;
using ResortAurora.CameraSystem;
using ResortAurora.Grid;
using UnityEngine;

namespace ResortAurora.Site
{
    [Serializable] public sealed class V2 { public float x, z; }
    [Serializable] public sealed class StreetNS { public float x, from, to, width; }
    [Serializable] public sealed class StreetEW { public float z, width; }
    [Serializable] public sealed class AvenueData { public float z, width; }
    [Serializable] public sealed class Rect2 { public string id, name, note, locked, parcel; public int price; public bool owned; public float x, z, width, depth, height; }
    [Serializable] public sealed class LotData { public float x, z, w, d, h, rot; public int c; }
    [Serializable] public sealed class HomeData { public string name, unit; public float x, z, width, depth, height, doorZ; }
    [Serializable] public sealed class StallData { public float x; }

    [Serializable]
    public sealed class SiteData
    {
        public string name;
        public V2[] promenade;
        public V2 worldOrigin, size;
        public float step, seaLevel;
        public int columns, rows;
        public AvenueData avenue;
        public StreetNS[] streetsNS;
        public StreetEW[] streetsEW;
        public Rect2[] parcels, terraces;
        public LotData[] lots;
        public HomeData home;
        public StallData stall;
    }

    /// <summary>
    /// Builds the Bairro das Palmeiras from the exported heightfield and layout (Tools/Map/export_resort_site.py): terrain mesh and collider,
    /// streets painted on the ground, the vila (instanced as combined meshes), the home building and the sea.
    /// Local frame: X east, Z north, origin at the south-west corner (sea side).
    /// </summary>
    public sealed class ResortSite : MonoBehaviour
    {
        [SerializeField] GridManager grid;                  // optional: RTS prototype scene
        [SerializeField] CameraController cameraController; // optional: RTS prototype scene
        [SerializeField] string resourcePath = "Resort/ResortSite";
        [SerializeField] string heightsPath = "Resort/ResortSiteHeights";

        static readonly Color[] Walls =
        {
            new Color(0.93f, 0.88f, 0.78f), new Color(0.88f, 0.74f, 0.55f), new Color(0.72f, 0.82f, 0.82f), new Color(0.90f, 0.62f, 0.52f),
            new Color(0.82f, 0.86f, 0.62f), new Color(0.95f, 0.93f, 0.88f), new Color(0.65f, 0.72f, 0.80f), new Color(0.85f, 0.80f, 0.70f),
        };

        public bool Ready { get; private set; }
        public Vector3 PadCenter { get; private set; }
        public SiteData Data { get; private set; }
        public float StallX => Data.stall.x;
        public Vector3 HomeDoor => new Vector3(Data.home.x, HeightAt(Data.home.x, Data.home.doorZ), Data.home.doorZ);

        float[] heights;

        public void Build()
        {
            var json = Resources.Load<TextAsset>(resourcePath);
            var bytes = Resources.Load<TextAsset>(heightsPath);
            if (json == null || bytes == null) { Debug.LogError("ResortSite: exported site data not found in Resources/Resort."); return; }
            Data = JsonUtility.FromJson<SiteData>(json.text);
            heights = new float[Data.columns * Data.rows];
            Buffer.BlockCopy(bytes.bytes, 0, heights, 0, heights.Length * sizeof(float));
            Ready = true;

            BuildTerrain().transform.SetParent(transform, false);
            BuildSea().transform.SetParent(transform, false);
            BuildVila().transform.SetParent(transform, false);
            BuildHome().transform.SetParent(transform, false);

            var p5 = Array.Find(Data.parcels, p => p.id == "P5");
            PadCenter = p5 != null ? new Vector3(p5.x + p5.width * 0.5f, HeightAt(p5.x + p5.width * 0.5f, p5.z), p5.z + p5.depth * 0.5f) : Vector3.zero;
            ConfigureOptionalRts();
        }

        void ConfigureOptionalRts()
        {
            var p3 = Array.Find(Data.parcels, p => p.id == "P3");
            if (grid != null && p3 != null)
            {
                grid.transform.position = new Vector3(p3.x, HeightAt(p3.x + p3.width * 0.5f, p3.z + p3.depth * 0.5f), p3.z);
                grid.Configure(new Vector2Int(Mathf.RoundToInt(p3.width), Mathf.RoundToInt(p3.depth)), 1f);
            }
            if (cameraController != null)
            {
                cameraController.SetBounds(new Vector2(0f, Data.size.x), new Vector2(0f, Data.size.z));
                cameraController.transform.position = PadCenter;
                cameraController.FocusOn(PadCenter);
            }
        }

        // ---------------------------------------------------------------- queries

        /// <summary>Ground height (bilinear over the exported heightfield). Cheap enough to call per agent per frame.</summary>
        public float HeightAt(float x, float z)
        {
            if (!Ready) return 0f;
            float fx = Mathf.Clamp(x / Data.step, 0f, Data.columns - 1.001f), fz = Mathf.Clamp(z / Data.step, 0f, Data.rows - 1.001f);
            int i = (int)fx, j = (int)fz; float tx = fx - i, tz = fz - j;
            float a = heights[j * Data.columns + i], b = heights[j * Data.columns + i + 1];
            float c = heights[(j + 1) * Data.columns + i], d = heights[(j + 1) * Data.columns + i + 1];
            return Mathf.Lerp(Mathf.Lerp(a, b, tx), Mathf.Lerp(c, d, tx), tz);
        }

        /// <summary>Centre line of the promenade (stone walkway) at local X.</summary>
        public float PromenadeZ(float x)
        {
            var p = Data.promenade;
            if (p == null || p.Length == 0) return 0f;
            if (x <= p[0].x) return p[0].z;
            for (int i = 1; i < p.Length; i++)
                if (x <= p[i].x) return Mathf.Lerp(p[i - 1].z, p[i].z, (x - p[i - 1].x) / Mathf.Max(0.001f, p[i].x - p[i - 1].x));
            return p[p.Length - 1].z;
        }

        // ---------------------------------------------------------------- terrain

        GameObject BuildTerrain()
        {
            int nx = Data.columns, nz = Data.rows;
            var verts = new Vector3[nx * nz];
            var uv = new Vector2[nx * nz];
            for (int j = 0; j < nz; j++)
                for (int i = 0; i < nx; i++)
                {
                    int k = j * nx + i;
                    verts[k] = new Vector3(i * Data.step, heights[k], j * Data.step);
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
            var mesh = new Mesh { name = "BairroTerrain", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.vertices = verts; mesh.uv = uv; mesh.triangles = tris;
            mesh.RecalculateNormals(); mesh.RecalculateBounds();

            var go = new GameObject("Terrain");
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = TerrainMaterial();
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
            return go;
        }

        /// <summary>Prototype shading: a colour map from height and layout (sand, grass, asphalt, promenade stone, parcels). Replaced by PBR splat later.</summary>
        Material TerrainMaterial()
        {
            const int scale = 3;                                  // texture pixels per terrain cell
            int w = (Data.columns - 1) * scale, h = (Data.rows - 1) * scale;
            var tex = new Texture2D(w, h, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear, anisoLevel = 4 };
            var px = new Color32[w * h];
            Color wet = new Color(0.62f, 0.55f, 0.40f), sand = new Color(0.86f, 0.78f, 0.58f), grass = new Color(0.34f, 0.46f, 0.22f);
            Color road = new Color(0.22f, 0.22f, 0.24f), stone = new Color(0.72f, 0.70f, 0.66f), pad = new Color(0.62f, 0.58f, 0.5f);
            float cell = Data.step / scale;
            for (int j = 0; j < h; j++)
                for (int i = 0; i < w; i++)
                {
                    float x = (i + 0.5f) * cell, z = (j + 0.5f) * cell;
                    float y = HeightAt(x, z);
                    Color c = y < 0.5f ? Color.Lerp(wet, sand, Mathf.InverseLerp(-1f, 0.5f, y)) : Color.Lerp(sand, grass, Mathf.InverseLerp(2.6f, 4.2f, y));
                    // noise breakup so large flat colours do not read as a flat shader
                    float n = Mathf.PerlinNoise(x * 0.11f, z * 0.11f) * 0.12f - 0.06f;
                    c = new Color(c.r + n, c.g + n, c.b + n);
                    if (Mathf.Abs(z - PromenadeZ(x)) < 6f) c = stone;
                    else if (OnRoad(x, z)) c = road;
                    else if (InParcel(x, z)) c = Color.Lerp(c, pad, 0.5f);
                    px[j * w + i] = c;
                }
            tex.SetPixels32(px); tex.Apply();
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "BairroTerrain" };
            m.SetTexture("_BaseMap", tex);
            m.SetFloat("_Smoothness", 0.04f);
            return m;
        }

        bool OnRoad(float x, float z)
        {
            if (Mathf.Abs(z - Data.avenue.z) < Data.avenue.width * 0.5f) return true;
            foreach (var s in Data.streetsEW) if (Mathf.Abs(z - s.z) < s.width * 0.5f) return true;
            foreach (var s in Data.streetsNS) if (z >= s.from && z <= s.to && Mathf.Abs(x - s.x) < s.width * 0.5f) return true;
            return false;
        }

        bool InParcel(float x, float z)
        {
            foreach (var p in Data.parcels) if (x >= p.x && x <= p.x + p.width && z >= p.z && z <= p.z + p.depth) return true;
            return false;
        }

        GameObject BuildSea()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Plane);
            go.name = "Sea";
            Destroy(go.GetComponent<Collider>());
            go.transform.localScale = new Vector3((Data.size.x + 1200f) / 10f, 1f, 60f);                 // 600 m of open sea seaward of the site
            go.transform.localPosition = new Vector3(Data.size.x * 0.5f, Data.seaLevel, -100f);
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "BairroSea" };
            m.SetColor("_BaseColor", new Color(0.05f, 0.35f, 0.45f, 1f));
            m.SetFloat("_Smoothness", 0.92f);
            go.GetComponent<MeshRenderer>().sharedMaterial = m;
            return go;
        }

        // ---------------------------------------------------------------- vila (prototype massing, placed on real lot data)

        GameObject BuildVila()
        {
            var root = new GameObject("Vila");
            var groups = new Dictionary<int, List<CombineInstance>>();
            var roofs = new List<CombineInstance>();
            var cube = Resources.GetBuiltinResource<Mesh>("Cube.fbx");
            foreach (var l in Data.lots)
            {
                float y = Mathf.Min(HeightAt(l.x - l.w / 2, l.z), HeightAt(l.x + l.w / 2, l.z), HeightAt(l.x, l.z - l.d / 2), HeightAt(l.x, l.z + l.d / 2));
                float top = Mathf.Max(HeightAt(l.x, l.z), y) ;
                float hh = l.h + (top - y) + 1.2f;                              // sink the foundation into slopes
                var body = Matrix4x4.TRS(new Vector3(l.x, y - 1.2f + hh * 0.5f, l.z), Quaternion.Euler(0f, l.rot, 0f), new Vector3(l.w, hh, l.d));
                if (!groups.TryGetValue(l.c, out var list)) groups[l.c] = list = new List<CombineInstance>();
                list.Add(new CombineInstance { mesh = cube, transform = body });
                var roof = Matrix4x4.TRS(new Vector3(l.x, y + l.h + (top - y) + 0.15f, l.z), Quaternion.Euler(0f, l.rot, 0f), new Vector3(l.w + 0.6f, 0.3f, l.d + 0.6f));
                roofs.Add(new CombineInstance { mesh = cube, transform = roof });
            }
            foreach (var kv in groups) AddCombined(root.transform, "Walls" + kv.Key, kv.Value, Walls[kv.Key % Walls.Length]);
            AddCombined(root.transform, "Roofs", roofs, new Color(0.55f, 0.3f, 0.22f));
            return root;
        }

        static void AddCombined(Transform parent, string name, List<CombineInstance> parts, Color color)
        {
            var mesh = new Mesh { name = name, indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.CombineMeshes(parts.ToArray(), true, true);
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = Game.StallBuilder.Mat(color, 0.1f);
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
        }

        GameObject BuildHome()
        {
            var h = Data.home;
            var root = new GameObject(h.name);
            float y = HeightAt(h.x, h.z - h.depth / 2);
            root.transform.position = new Vector3(h.x, y, h.z);
            Game.StallBuilder.Box("Body", root.transform, new Vector3(0f, h.height / 2f - 0.5f, 0f), new Vector3(h.width, h.height + 1f, h.depth), new Color(0.80f, 0.74f, 0.62f));
            Game.StallBuilder.Box("Roof", root.transform, new Vector3(0f, h.height + 0.3f, 0f), new Vector3(h.width + 0.8f, 0.6f, h.depth + 0.8f), new Color(0.35f, 0.33f, 0.32f));
            Game.StallBuilder.Box("DoorFrame", root.transform, new Vector3(0f, 1.1f, -h.depth / 2 - 0.05f), new Vector3(1.6f, 2.2f, 0.12f), new Color(0.3f, 0.2f, 0.12f));
            for (int f = 1; f < 4; f++)                                      // window strips so the block reads as floors
                for (int k = -2; k <= 2; k++)
                    Game.StallBuilder.Box("Win", root.transform, new Vector3(k * 4.2f, f * 3.4f, -h.depth / 2 - 0.05f), new Vector3(1.6f, 1.5f, 0.1f), new Color(0.35f, 0.5f, 0.62f), collider: false);
            Game.StallBuilder.Label(root.transform, new Vector3(0f, 3.0f, -h.depth / 2 - 0.4f), $"{h.name}\n{h.unit}", 40, 0.12f);
            return root;
        }
    }
}
