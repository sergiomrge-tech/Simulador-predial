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
        [SerializeField] string naturalHeightsPath = "Resort/ResortSiteHeights_natural";

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

        float[] heights, gradedHeights, naturalHeights;
        GameObject terrainGraded, terrainNatural;

        /// <summary>True once the platô is graded (stage 6+): terraces exist. Before that the land is the natural slope.</summary>
        public bool Graded { get; private set; }

        /// <summary>Swaps the terrain between the natural land and the graded platô (collider and ground height follow).</summary>
        public void SetGraded(bool graded)
        {
            if (!Ready) return;
            Graded = graded;
            heights = graded ? gradedHeights : naturalHeights;
            terrainGraded.SetActive(graded);
            terrainNatural.SetActive(!graded);
        }

        public void Build()
        {
            var json = Resources.Load<TextAsset>(resourcePath);
            var bytes = Resources.Load<TextAsset>(heightsPath);
            if (json == null || bytes == null) { Debug.LogError("ResortSite: exported site data not found in Resources/Resort."); return; }
            Data = JsonUtility.FromJson<SiteData>(json.text);
            gradedHeights = new float[Data.columns * Data.rows];
            Buffer.BlockCopy(bytes.bytes, 0, gradedHeights, 0, gradedHeights.Length * sizeof(float));
            var nat = Resources.Load<TextAsset>(naturalHeightsPath);
            naturalHeights = gradedHeights;
            if (nat != null)
            {
                naturalHeights = new float[gradedHeights.Length];
                Buffer.BlockCopy(nat.bytes, 0, naturalHeights, 0, naturalHeights.Length * sizeof(float));
            }
            heights = gradedHeights;
            Ready = true;

            var mat = TerrainMaterial();                       // shared colour map (built from the graded heights)
            terrainGraded = BuildTerrain(gradedHeights, "Terrain_graded", mat);
            terrainNatural = BuildTerrain(naturalHeights, "Terrain_natural", mat);
            terrainGraded.transform.SetParent(transform, false);
            terrainNatural.transform.SetParent(transform, false);
            SetGraded(false);
            BuildSea().transform.SetParent(transform, false);
            BuildVila().transform.SetParent(transform, false);

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

        readonly Dictionary<int, float> waterlineCache = new Dictionary<int, float>();

        /// <summary>Local Z of the waterline (where the sand drops under the sea) at local X, scanned seaward from the promenade edge; cached per 4 m.</summary>
        public float WaterlineZ(float x)
        {
            int key = Mathf.RoundToInt(x / 4f);
            if (waterlineCache.TryGetValue(key, out var z)) return z;
            z = PromenadeZ(x) - 6f;
            while (z > 20f && HeightAt(x, z) > 0.05f) z -= 0.75f;
            return waterlineCache[key] = z;
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

        GameObject BuildTerrain(float[] heights, string objectName, Material material)
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

            var go = new GameObject(objectName);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = material;
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

        /// <summary>Seaward distance (m) of each row of the water surface from the local waterline; the first row hides under the beach.</summary>
        static readonly float[] SeaRows = { -30f, 0f, 3f, 8f, 16f, 30f, 55f, 95f, 160f, 260f, 420f, 700f, 1100f, 1500f };

        GameObject BuildSea()
        {
            var root = new GameObject("Sea");
            // fallback sheet (flat, deep colour) under the real surface, so a lagoon or a bay that the waterline scan skips never shows the void
            var plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
            plane.name = "SeaBase"; plane.transform.SetParent(root.transform, false);
            Destroy(plane.GetComponent<Collider>());
            plane.transform.localScale = new Vector3((Data.size.x + 3200f) / 10f, 1f, 90f);
            plane.transform.localPosition = new Vector3(Data.size.x * 0.5f, Data.seaLevel - 0.06f, -100f);
            var baseMat = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "BairroSeaBase" };
            baseMat.SetColor("_BaseColor", new Color(0.03f, 0.22f, 0.32f, 1f));
            baseMat.SetFloat("_Smoothness", 0.5f);
            plane.GetComponent<MeshRenderer>().sharedMaterial = baseMat;

            // the surface: columns along the coast, rows by distance from the waterline (colour = shallowness and opacity per vertex)
            var shader = Shader.Find("ResortAurora/Sea");
            if (shader == null) return root;
            const float colStep = 8f;
            float x0 = -1500f, x1 = Data.size.x + 1500f;
            int cols = Mathf.CeilToInt((x1 - x0) / colStep) + 1, rows = SeaRows.Length;
            var verts = new Vector3[cols * rows]; var colors = new Color[cols * rows]; var tris = new int[(cols - 1) * (rows - 1) * 6];
            float y = Data.seaLevel;
            for (int i = 0; i < cols; i++)
            {
                float x = x0 + i * colStep, shore = WaterlineZ(Mathf.Clamp(x, 0f, Data.size.x));
                for (int r = 0; r < rows; r++)
                {
                    float d = SeaRows[r];
                    verts[i * rows + r] = new Vector3(x, y, shore - d);
                    float shallow = 1f - Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(d / 130f));
                    float opacity = Mathf.Lerp(0.5f, 1f, Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(d / 22f)));
                    colors[i * rows + r] = new Color(shallow, opacity, 0f, 1f);
                }
            }
            int k = 0;
            for (int i = 0; i < cols - 1; i++)
                for (int r = 0; r < rows - 1; r++)
                {
                    int a = i * rows + r, b = a + 1, c = a + rows, e = c + 1;                  // winding is irrelevant: the shader is double-sided
                    tris[k++] = a; tris[k++] = b; tris[k++] = c; tris[k++] = c; tris[k++] = b; tris[k++] = e;
                }
            var mesh = new Mesh { name = "SeaSurface", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.vertices = verts; mesh.colors = colors; mesh.triangles = tris; mesh.RecalculateBounds();
            var surface = new GameObject("SeaSurface"); surface.transform.SetParent(root.transform, false);
            surface.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = surface.AddComponent<MeshRenderer>();
            mr.sharedMaterial = new Material(shader) { name = "BairroSea" };
            mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; mr.receiveShadows = false;
            return root;
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
