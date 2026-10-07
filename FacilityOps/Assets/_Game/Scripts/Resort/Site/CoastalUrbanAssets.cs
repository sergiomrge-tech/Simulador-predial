using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Site
{
    /// <summary>
    /// Fase-02 realistic visual replacement for the procedural Vila.
    /// Keeps the original combined meshes as invisible collision fallback and batches
    /// project-owned coastal building archetypes into a small set of PBR renderers.
    /// </summary>
    public static class CoastalUrbanAssets
    {
        struct Archetype
        {
            public string path;
            public Vector3 size;
            public Archetype(string path, float w, float h, float d)
            {
                this.path = path; size = new Vector3(w, h, d);
            }
        }

        static readonly Archetype Casa = new Archetype("Art/Resort/Urban/casa_terrea", 9f, 4.5f, 13f);
        static readonly Archetype Sobrado = new Archetype("Art/Resort/Urban/sobrado", 9f, 6.2f, 14f);
        static readonly Archetype Loja = new Archetype("Art/Resort/Urban/loja", 10f, 4.6f, 12f);
        static readonly Archetype Misto = new Archetype("Art/Resort/Urban/misto", 10f, 6.4f, 15f);
        static readonly Archetype Apartamento = new Archetype("Art/Resort/Urban/apartamento", 11f, 9.2f, 16f);
        static readonly Archetype Hotel = new Archetype("Art/Resort/Urban/hotel", 12f, 9.4f, 16f);
        static readonly Archetype Townhouse = new Archetype("Art/Resort/Urban/townhouse", 6.4f, 6.3f, 14f);
        static readonly Archetype Sacadas = new Archetype("Art/Resort/Urban/residencial_sacadas", 12f, 7.4f, 15f);

        static readonly Color[] Facade =
        {
            new Color(0.92f,0.88f,0.78f), new Color(0.78f,0.86f,0.87f),
            new Color(0.90f,0.72f,0.58f), new Color(0.82f,0.88f,0.70f),
            new Color(0.94f,0.93f,0.88f), new Color(0.74f,0.78f,0.84f),
            new Color(0.88f,0.82f,0.72f), new Color(0.84f,0.72f,0.67f),
        };
        static readonly Color[] RoofTint =
        {
            new Color(0.78f,0.50f,0.36f), new Color(0.64f,0.36f,0.27f), new Color(0.72f,0.58f,0.46f)
        };
        static readonly Color[] AwningTint =
        {
            new Color(0.28f,0.48f,0.58f), new Color(0.68f,0.28f,0.22f),
            new Color(0.82f,0.68f,0.28f), new Color(0.35f,0.52f,0.35f)
        };

        static readonly Dictionary<string, GameObject> prefabs = new Dictionary<string, GameObject>();
        static readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        static readonly Dictionary<string, Bounds> boundsCache = new Dictionary<string, Bounds>();

        public struct LotFrame
        {
            public float floor, width, depth, height, front, back, wallX;
            public bool commercial, pitchedRoof;
            public Quaternion rotation;
            public Vector3 Point(LotData lot, float x, float y, float z) =>
                new Vector3(lot.x, floor, lot.z) + rotation * new Vector3(x, y, z);
        }

        public static bool TryDescribeLot(ResortSite site, LotData lot, int index, out LotFrame frame)
        {
            frame = default;
            var archetype = Pick(lot, index); var prefab = Load(archetype.path);
            if (prefab == null) return false;
            if (!boundsCache.TryGetValue(archetype.path, out var b)) boundsCache[archetype.path] = b = LocalBounds(prefab);
            float scale = Mathf.Min(lot.w / b.size.x, lot.d / b.size.z);
            frame.width = b.size.x * scale; frame.depth = b.size.z * scale;
            frame.height = b.size.y * Mathf.Clamp(lot.h / b.size.y, 0.85f, 1.12f);
            // Blender's authored -Y frontage imports at Unity +Z. The southern
            // row has rot=0 and faces its EW street to the north (export_resort_site.py).
            frame.rotation = Quaternion.Euler(0, lot.rot, 0);
            frame.front = (archetype.size.z / 2 - b.center.z) * scale;
            frame.back = (-archetype.size.z / 2 - b.center.z) * scale;
            frame.wallX = archetype.size.x / 2 * scale;
            frame.floor = float.MinValue;
            for (int ix = -1; ix <= 1; ix++) for (int iz = -1; iz <= 1; iz++)
            {
                var p = frame.rotation * new Vector3(ix * frame.width / 2, 0, iz * frame.depth / 2);
                frame.floor = Mathf.Max(frame.floor, site.HeightAt(lot.x + p.x, lot.z + p.z) + 0.085f);
            }
            frame.commercial = archetype.path == Loja.path || archetype.path == Misto.path;
            frame.pitchedRoof = archetype.path == Casa.path || archetype.path == Loja.path;
            return true;
        }

        public static bool Available
        {
            get
            {
                return Load(Casa.path) != null && Load(Sobrado.path) != null &&
                       Load(Loja.path) != null && Load(Apartamento.path) != null &&
                       Load(Misto.path) != null && Load(Hotel.path) != null &&
                       Load(Townhouse.path) != null && Load(Sacadas.path) != null;
            }
        }

        static GameObject Load(string path)
        {
            if (prefabs.TryGetValue(path, out var p)) return p;
            p = Resources.Load<GameObject>(path);
            prefabs[path] = p;
            return p;
        }

        static Archetype Pick(LotData lot, int index)
        {
            if (lot.h <= 5.6f)
            {
                if (lot.w >= 9f && ((index + lot.c) % 4 == 0)) return Loja;
                return Casa;
            }
            if (lot.h <= 6.6f)
            {
                if (lot.w <= 7f) return Townhouse;
                if (lot.w >= 9f && ((index + lot.c) % 3 == 0)) return Misto;
                return Sobrado;
            }
            if (lot.h < 8.4f)
                return lot.w >= 10f ? Sacadas : Sobrado;
            if (lot.w >= 11f && ((index + lot.c) % 7 == 0)) return Hotel;
            return ((index + lot.c) & 1) == 0 ? Apartamento : Sacadas;
        }

        static Material Mat(string key, string surface, Color tint, float tile = 1f)
        {
            if (materials.TryGetValue(key, out var m) && m != null) return m;
            m = ResortSurfaceMaterials.Create(surface, tint, tile);
            m.name = "Urban_" + key;
            m.enableInstancing = true;
            materials[key] = m;
            return m;
        }

        static Material Glass()
        {
            if (materials.TryGetValue("glass", out var m) && m != null) return m;
            m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "Urban_Glass", enableInstancing = true };
            m.SetColor("_BaseColor", new Color(0.055f, 0.12f, 0.16f, 1f));
            m.SetFloat("_Metallic", 0.08f);
            m.SetFloat("_Smoothness", 0.84f);
            materials["glass"] = m;
            return m;
        }

        static Material MaterialFor(string part, LotData lot)
        {
            if (part.StartsWith("MAT_Wall"))
                return Mat("facade_" + (lot.c % Facade.Length), "urban_stucco", Facade[lot.c % Facade.Length], 2.2f);
            if (part.StartsWith("MAT_Trim"))
                return Mat("trim", "urban_concrete", new Color(0.91f,0.90f,0.86f), 1.5f);
            if (part.StartsWith("MAT_Glass")) return Glass();
            if (part.StartsWith("MAT_Wood"))
                return Mat("wood", "madeira", new Color(0.72f,0.64f,0.54f), 1.2f);
            if (part.StartsWith("MAT_Metal"))
                return Mat("metal", "galvanizado", new Color(0.68f,0.70f,0.72f), 1f);
            if (part.StartsWith("MAT_Roof"))
                return Mat("roof_" + (lot.c % RoofTint.Length), "urban_roof", RoofTint[lot.c % RoofTint.Length], 1.4f);
            if (part.StartsWith("MAT_Awning"))
            {
                int i = lot.c % AwningTint.Length;
                return Mat("awning_" + i, "plastico", AwningTint[i], 1.6f);
            }
            return Mat("concrete", "urban_concrete", new Color(0.68f,0.68f,0.66f), 1.7f);
        }

        static string BatchKey(string part, LotData lot)
        {
            if (part.StartsWith("MAT_Wall")) return "Facade_" + (lot.c % Facade.Length);
            if (part.StartsWith("MAT_Trim")) return "Trim";
            if (part.StartsWith("MAT_Glass")) return "Glass";
            if (part.StartsWith("MAT_Wood")) return "Wood";
            if (part.StartsWith("MAT_Metal")) return "Metal";
            if (part.StartsWith("MAT_Roof")) return "Roof_" + (lot.c % RoofTint.Length);
            if (part.StartsWith("MAT_Awning")) return "Awning_" + (lot.c % AwningTint.Length);
            return "Concrete";
        }

        static void AddBatch(Transform parent, string name, List<CombineInstance> parts, Material material)
        {
            if (parts == null || parts.Count == 0) return;
            var mesh = new Mesh { name = name + "_Mesh", indexFormat = IndexFormat.UInt32 };
            mesh.CombineMeshes(parts.ToArray(), true, true, false);
            mesh.RecalculateBounds();
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            Debug.Log($"URBAN_BATCH {name} vertices={mesh.vertexCount} center={mesh.bounds.center} size={mesh.bounds.size}");
        }

        static void DestroySafe(Object target)
        {
            if (target == null) return;
            if (Application.isPlaying) Object.Destroy(target);
            else Object.DestroyImmediate(target);
        }

        static Bounds LocalBounds(GameObject instance)
        {
            var bounds = new Bounds(); bool first = true;
            foreach (var mf in instance.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.sharedMesh == null) continue;
                var b = mf.sharedMesh.bounds;
                var matrix = instance.transform.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                for (int i = 0; i < 8; i++)
                {
                    var p = matrix.MultiplyPoint3x4(b.center + Vector3.Scale(b.extents,
                        new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    if (first) { bounds = new Bounds(p, Vector3.zero); first = false; } else bounds.Encapsulate(p);
                }
            }
            return bounds;
        }

        static void Append(Dictionary<string, List<CombineInstance>> batches, string key, Mesh mesh, Matrix4x4 matrix, int subMesh = 0)
        {
            if (!batches.TryGetValue(key, out var list)) batches[key] = list = new List<CombineInstance>();
            list.Add(new CombineInstance { mesh = mesh, subMeshIndex = subMesh, transform = matrix });
        }

        public static bool ReplaceVisuals(Transform fallbackRoot, ResortSite site)
        {
            if (fallbackRoot == null || site == null || site.Data == null || !Available) return false;

            var urbanRoot = new GameObject("VilaRealista_F02");
            urbanRoot.transform.SetParent(fallbackRoot, false);

            var batches = new Dictionary<string, List<CombineInstance>>();
            var batchMaterials = new Dictionary<string, Material>();
            var tempRoot = new GameObject("__UrbanBakeTemp");
            tempRoot.transform.SetParent(site.transform, false);
            tempRoot.SetActive(false);

            int replaced = 0;
            for (int index = 0; index < site.Data.lots.Length; index++)
            {
                var lot = site.Data.lots[index];
                var archetype = Pick(lot, index);
                var prefab = Load(archetype.path);
                if (prefab == null) continue;

                var inst = Object.Instantiate(prefab, tempRoot.transform, false);
                inst.name = "Lot_" + index;
                var bounds = LocalBounds(inst);
                float scaleXZ = Mathf.Min(lot.w / bounds.size.x, lot.d / bounds.size.z);
                var scale = new Vector3(scaleXZ, Mathf.Clamp(lot.h / bounds.size.y, 0.85f, 1.12f), scaleXZ);
                var rotation = Quaternion.Euler(0f, lot.rot, 0f);
                float low = float.MaxValue, high = float.MinValue;
                // Sample rotated footprint corners and interior, not unrotated edge midpoints.
                for (int ix = -1; ix <= 1; ix++) for (int iz = -1; iz <= 1; iz++)
                {
                    var offset = rotation * new Vector3(ix * bounds.size.x * scaleXZ / 2, 0, iz * bounds.size.z * scaleXZ / 2);
                    float height = site.HeightAt(lot.x + offset.x, lot.z + offset.z);
                    low = Mathf.Min(low, height); high = Mathf.Max(high, height);
                }
                float floor = high + 0.085f;
                var centreOffset = rotation * Vector3.Scale(new Vector3(bounds.center.x, bounds.min.y, bounds.center.z), scale);
                inst.transform.localPosition = new Vector3(lot.x, floor, lot.z) - centreOffset;
                inst.transform.localRotation = rotation;
                inst.transform.localScale = scale;
                string cell = "Cell_" + Mathf.FloorToInt(lot.x / 90f) + "_" + Mathf.FloorToInt(lot.z / 120f) + "_";
                bool valid = true;

                foreach (var mf in inst.GetComponentsInChildren<MeshFilter>(true))
                {
                    if (mf.sharedMesh == null || !mf.sharedMesh.isReadable) { valid = false; continue; }
                    string key = cell + BatchKey(mf.name, lot);
                    // BuildVila's root is attached to the site after this call: bake in site-local coordinates.
                    for (int sub = 0; sub < mf.sharedMesh.subMeshCount; sub++)
                        Append(batches, key, mf.sharedMesh, site.transform.worldToLocalMatrix * mf.transform.localToWorldMatrix, sub);
                    if (!batchMaterials.ContainsKey(key)) batchMaterials[key] = MaterialFor(mf.name, lot);
                }
                var foundationSize = new Vector3(bounds.size.x * scaleXZ, floor - low + 0.15f, bounds.size.z * scaleXZ);
                string foundationKey = cell + "Foundation";
                Append(batches, foundationKey, ResortSurfaceMaterials.MetreCube(foundationSize),
                    Matrix4x4.TRS(new Vector3(lot.x, floor - foundationSize.y / 2, lot.z), rotation, foundationSize));
                batchMaterials[foundationKey] = Mat("foundation", "urban_concrete", new Color(0.66f, 0.65f, 0.61f));
                if (valid) replaced++;
                DestroySafe(inst);
            }
            DestroySafe(tempRoot);

            if (replaced != site.Data.lots.Length)
            {
                Debug.LogError($"URBAN_BUILD incomplete={replaced}/{site.Data.lots.Length}; collision fallback visuals retained. Check readable mesh import.");
                DestroySafe(urbanRoot); return false;
            }
            Debug.Log($"URBAN_BUILD lots={replaced} batches={batches.Count} spatialBatch=90x120m");
            foreach (var kv in batches)
                AddBatch(urbanRoot.transform, "Urban_" + kv.Key, kv.Value, batchMaterials[kv.Key]);

            // Existing meshes remain authoritative collision geometry but are never rendered
            // when the realistic replacement is complete.
            foreach (var renderer in fallbackRoot.GetComponentsInChildren<MeshRenderer>(true))
                if (!renderer.transform.IsChildOf(urbanRoot.transform))
                    renderer.enabled = false;

            return urbanRoot.transform.childCount > 0;
        }
    }
}
