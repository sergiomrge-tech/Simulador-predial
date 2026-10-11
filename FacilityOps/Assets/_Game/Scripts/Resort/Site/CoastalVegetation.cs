using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Site
{
    public sealed class CoastalVegetationState : MonoBehaviour
    {
        struct ParcelGroup
        {
            public GameObject root;
            public int hideAtStage;
            public ParcelGroup(GameObject root, int hideAtStage) { this.root = root; this.hideAtStage = hideAtStage; }
        }

        readonly List<ParcelGroup> parcelGroups = new List<ParcelGroup>();

        public void Register(GameObject root, int hideAtStage)
        {
            if (root != null) parcelGroups.Add(new ParcelGroup(root, hideAtStage));
        }

        public void SetStage(int stage)
        {
            foreach (var p in parcelGroups)
                if (p.root != null) p.root.SetActive(stage < p.hideAtStage);
        }
    }

    /// <summary>
    /// Deterministic realistic greenery for the open urban blocks.
    /// Keeps roads, sidewalks, authored buildings and reserved resort parcels clear.
    /// Poly Haven CC0 models are optimized offline into explicit LODs before they reach this runtime.
    /// </summary>
    public static class CoastalVegetation
    {
        sealed class TreeDef
        {
            public readonly string folder, stem;
            public readonly int lods;
            public readonly float minScale, maxScale;
            public TreeDef(string folder, string stem, int lods, float minScale, float maxScale)
            { this.folder = folder; this.stem = stem; this.lods = lods; this.minScale = minScale; this.maxScale = maxScale; }
            public string LOD(int i) => "Art/Resort/Vegetation/" + folder + "/" + stem + "_LOD" + i;
        }

        static readonly TreeDef Coastal = new TreeDef("island_tree_02", "island_tree_02", 3, 1.25f, 1.85f);
        static readonly TreeDef Small = new TreeDef("tree_small_02", "tree_small_02", 2, 1.05f, 1.52f);
        static readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        static readonly Dictionary<string, GameObject> prefabs = new Dictionary<string, GameObject>();
        static readonly string GrassRoot = "Art/Resort/Vegetation/grass_medium_01/";
        static readonly string GrassTex = GrassRoot + "textures/grass_medium_01";

        static GameObject Load(string path)
        {
            if (prefabs.TryGetValue(path, out var cached) && cached != null) return cached;
            cached = Resources.Load<GameObject>(path);
            prefabs[path] = cached;
            return cached;
        }

        static Material MaterialFor(string folder, string materialName)
        {
            string stem = materialName.Replace(" (Instance)", "").Split('.')[0];
            string key = folder + "/" + stem;
            if (materials.TryGetValue(key, out var cached) && cached != null) return cached;

            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) return null;
            var m = new Material(shader) { name = "Vegetation_" + stem, enableInstancing = true };
            string p = "Art/Resort/Vegetation/" + folder + "/textures/" + stem;

            bool leaf = stem.Contains("leaves", StringComparison.OrdinalIgnoreCase);
            bool grass = stem.Contains("grass", StringComparison.OrdinalIgnoreCase);
            bool cutout = leaf || grass;

            var baseMap = Resources.Load<Texture2D>(p + "_BaseColor");
            if (baseMap != null) m.SetTexture("_BaseMap", baseMap);
            m.SetColor("_BaseColor", leaf ? new Color(1.55f, 1.75f, 1.30f, 1f) :   // the scanned leaf albedo is very dark; lift it so canopies do not read as black silhouettes
                                    grass ? new Color(0.82f, 0.88f, 0.72f, 1f) : Color.white);
            m.SetFloat("_Metallic", 0f);
            m.SetFloat("_Smoothness", cutout ? 0.025f : 0.20f);

            var normal = Resources.Load<Texture2D>(p + "_Normal");
            if (normal != null)
            {
                m.SetTexture("_BumpMap", normal);
                m.SetFloat("_BumpScale", leaf ? 0.22f : grass ? 0.30f : 0.85f);
                m.EnableKeyword("_NORMALMAP");
            }

            var mask = Resources.Load<Texture2D>(p + "_Mask");
            if (mask != null)
            {
                // Leaves/grass remain matte: their roughness atlas is useful for occlusion, but feeding it
                // through URP's metallic-gloss channel creates silver foliage under a low coastal sun.
                m.SetTexture("_OcclusionMap", mask);
                m.SetFloat("_OcclusionStrength", cutout ? 0.48f : 0.75f);
                m.EnableKeyword("_OCCLUSIONMAP");
                if (!cutout)
                {
                    m.SetTexture("_MetallicGlossMap", mask);
                    m.SetFloat("_Smoothness", 1f);
                    m.EnableKeyword("_METALLICSPECGLOSSMAP");
                }
            }

            if (cutout)
            {
                m.SetFloat("_AlphaClip", 1f);
                m.SetFloat("_Cutoff", grass ? 0.42f : 0.36f);
                m.EnableKeyword("_ALPHATEST_ON");
                m.renderQueue = (int)RenderQueue.AlphaTest;
                m.doubleSidedGI = true;
                if (m.HasProperty("_Cull")) m.SetFloat("_Cull", (float)CullMode.Off);
                if (m.HasProperty("_SpecularHighlights")) m.SetFloat("_SpecularHighlights", 0f);
                m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            }

            Debug.Log("VEG_MATERIAL " + key + " base=" + (baseMap != null) +
                      " normal=" + (normal != null) + " mask=" + (mask != null) +
                      " cutout=" + cutout);

            materials[key] = m;
            return m;
        }

        static void Dress(GameObject model, string folder, bool farLod)
        {
            foreach (var r in model.GetComponentsInChildren<Renderer>(true))
            {
                var src = r.sharedMaterials;
                var dst = new Material[src.Length];
                for (int i = 0; i < src.Length; i++)
                {
                    string n = src[i] != null ? src[i].name : folder;
                    dst[i] = MaterialFor(folder, n);
                }
                r.sharedMaterials = dst;
                r.receiveShadows = true;
                r.shadowCastingMode = farLod ? ShadowCastingMode.Off : ShadowCastingMode.On;
            }
        }

        static bool InRect(Rect2 r, float x, float z, float margin)
        {
            if (r == null) return false;
            return x >= r.x - margin && x <= r.x + r.width + margin &&
                   z >= r.z - margin && z <= r.z + r.depth + margin;
        }

        static bool Reserved(SiteData d, float x, float z, float margin)
        {
            if (d.parcels != null) foreach (var r in d.parcels) if (InRect(r, x, z, margin)) return true;
            if (d.terraces != null) foreach (var r in d.terraces) if (InRect(r, x, z, margin)) return true;
            return false;
        }

        static bool NearLot(SiteData d, float x, float z, float margin)
        {
            if (d.lots != null)
            {
                foreach (var lot in d.lots)
                {
                    float a = -lot.rot * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
                    float dx = x - lot.x, dz = z - lot.z;
                    float lx = c * dx - s * dz, lz = s * dx + c * dz;
                    if (Mathf.Abs(lx) <= lot.w * .5f + margin && Mathf.Abs(lz) <= lot.d * .5f + margin) return true;
                }
            }
            if (d.home != null)
            {
                if (Mathf.Abs(x - d.home.x) <= d.home.width * .5f + margin &&
                    Mathf.Abs(z - d.home.z) <= d.home.depth * .5f + margin) return true;
            }
            return false;
        }

        static bool RoadClear(ResortSite site, float x, float z, float radius)
        {
            if (CoastalUrbanGround.IsRoad(site.Data, x, z) || CoastalUrbanGround.IsSidewalk(site.Data, x, z)) return false;
            for (int i = 0; i < 8; i++)
            {
                float a = i * Mathf.PI * .25f;
                float px = x + Mathf.Cos(a) * radius, pz = z + Mathf.Sin(a) * radius;
                if (CoastalUrbanGround.IsRoad(site.Data, px, pz) || CoastalUrbanGround.IsSidewalk(site.Data, px, pz)) return false;
            }
            return true;
        }

        static bool Free(ResortSite site, float x, float z, float margin)
        {
            var d = site.Data;
            if (x < 12f || x > d.size.x - 12f || z < d.avenue.z + d.avenue.width * .5f + 18f || z > d.size.z - 10f || site.HeightAt(x,z)<d.seaLevel+.65f) return false;
            if (!RoadClear(site, x, z, margin)) return false;
            if (NearLot(d, x, z, margin + 2f)) return false;
            if (Reserved(d, x, z, margin + 4f)) return false;
            return true;
        }

        static readonly Dictionary<TreeDef, Mesh> proxyMeshes = new Dictionary<TreeDef, Mesh>();

        static Material ProxyMaterial()
        {
            const string key = "proxy_canopy";
            if (materials.TryGetValue(key, out var m) && m != null) return m;
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) return null;
            m = new Material(shader) { name = "VegetationProxy_Canopy", enableInstancing = true };
            m.SetColor("_BaseColor", new Color(.27f, .43f, .17f, 1f));
            m.SetFloat("_Metallic", 0f);
            m.SetFloat("_Smoothness", 0f);
            m.SetFloat("_SpecularHighlights", 0f);
            m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            materials[key] = m;
            return m;
        }

        static void AddEllipsoid(List<Vector3> v, List<Vector3> n, List<int> tris, Vector3 center, Vector3 radii, int seg, int rings)
        {
            int start = v.Count;
            for (int r = 0; r <= rings; r++)
            {
                float phi = Mathf.PI * r / rings;
                for (int s = 0; s <= seg; s++)
                {
                    float th = Mathf.PI * 2f * s / seg;
                    var d = new Vector3(Mathf.Sin(phi) * Mathf.Cos(th), Mathf.Cos(phi), Mathf.Sin(phi) * Mathf.Sin(th));
                    v.Add(center + Vector3.Scale(d, radii));
                    n.Add(d);
                }
            }
            for (int r = 0; r < rings; r++)
                for (int s = 0; s < seg; s++)
                {
                    int a = start + r * (seg + 1) + s, b = a + seg + 1;
                    tris.Add(a); tris.Add(b); tris.Add(a + 1);
                    tris.Add(a + 1); tris.Add(b); tris.Add(b + 1);
                }
        }

        /// <summary>Single-draw far-LOD stand-in sized to the authored canopy bounds (root-local): three canopy blobs, no trunk (sub-pixel at that range). ~300 triangles.</summary>
        static Mesh ProxyMesh(TreeDef def, Bounds b)
        {
            if (proxyMeshes.TryGetValue(def, out var cached) && cached != null) return cached;
            float h = Mathf.Max(b.size.y, .5f), sx = Mathf.Max(b.size.x, .5f), sz = Mathf.Max(b.size.z, .5f), y0 = b.min.y;
            var v = new List<Vector3>(); var n = new List<Vector3>(); var tris = new List<int>();
            var cc = b.center;
            // one large central blob and two offset ones for an uneven silhouette
            AddEllipsoid(v, n, tris, new Vector3(cc.x, y0 + h * .68f, cc.z), new Vector3(sx * .41f, h * .27f, sz * .41f), 10, 6);
            AddEllipsoid(v, n, tris, new Vector3(cc.x + sx * .20f, y0 + h * .58f, cc.z - sz * .12f), new Vector3(sx * .27f, h * .20f, sz * .27f), 8, 5);
            AddEllipsoid(v, n, tris, new Vector3(cc.x - sx * .19f, y0 + h * .60f, cc.z + sz * .13f), new Vector3(sx * .26f, h * .20f, sz * .26f), 8, 5);

            var mesh = new Mesh { name = "TreeProxy_" + def.stem };
            mesh.SetVertices(v); mesh.SetNormals(n);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateBounds();
            proxyMeshes[def] = mesh;
            return mesh;
        }

        static GameObject Tree(TreeDef def, Transform parent, Vector3 pos, float yaw, float scale, int index)
        {
            var root = new GameObject("Tree_" + def.stem + "_" + index);
            root.transform.SetParent(parent, false);
            root.transform.position = pos;
            root.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            root.transform.localScale = Vector3.one * scale;

            var lods = new List<LOD>();
            Bounds canopy = default; bool haveBounds = false;
            // The offline-decimated far LODs (collapse on disconnected leaf cards) read as dark thin skeletons from a distance,
            // so the chain is LOD0 (as authored) -> LOD1 (~20k tris) -> a volumetric proxy (trunk + canopy blobs) -> culled.
            int meshLods = Mathf.Min(def.lods, 2);
            for (int i = 0; i < meshLods; i++)
            {
                var prefab = Load(def.LOD(i));
                if (prefab == null) continue;
                var model = UnityEngine.Object.Instantiate(prefab, root.transform, false);
                model.name = "LOD" + i;
                model.transform.localPosition = Vector3.zero;
                model.transform.localRotation = Quaternion.identity;
                model.transform.localScale = Vector3.one;
                Dress(model, def.folder, i == def.lods - 1);   // shadow casting off only on the last authored mesh LOD, as before
                var rs = model.GetComponentsInChildren<Renderer>(true);
                if (i == 0)
                    foreach (var mf in model.GetComponentsInChildren<MeshFilter>(true))
                    {
                        if (mf.sharedMesh == null) continue;
                        var mb = mf.sharedMesh.bounds;   // model space (unscaled, unrotated root): independent of the tree's random yaw/scale
                        for (int c = 0; c < 8; c++)
                        {
                            var corner = model.transform.InverseTransformPoint(mf.transform.TransformPoint(mb.center + Vector3.Scale(mb.extents, new Vector3((c & 1) == 0 ? -1 : 1, (c & 2) == 0 ? -1 : 1, (c & 4) == 0 ? -1 : 1))));
                            if (!haveBounds) { canopy = new Bounds(corner, Vector3.zero); haveBounds = true; } else canopy.Encapsulate(corner);
                        }
                    }
                float threshold = i == 0 ? .22f : .08f;
                lods.Add(new LOD(threshold, rs) { fadeTransitionWidth = .12f });
            }
            if (lods.Count > 0 && haveBounds)
            {
                var proxy = new GameObject("LODProxy");
                proxy.transform.SetParent(root.transform, false);
                proxy.AddComponent<MeshFilter>().sharedMesh = ProxyMesh(def, canopy);
                var pr = proxy.AddComponent<MeshRenderer>();
                pr.sharedMaterial = ProxyMaterial();
                pr.shadowCastingMode = ShadowCastingMode.Off;
                pr.receiveShadows = true;
                lods.Add(new LOD(.03f, new Renderer[] { pr }) { fadeTransitionWidth = .15f });
            }
            if (lods.Count > 0)
            {
                lods.Add(new LOD(.006f, new Renderer[0]));   // culled: a tree under ~0.6% of the screen height is not worth a draw call
                var g = root.AddComponent<LODGroup>();
                g.fadeMode = LODFadeMode.CrossFade;
                g.animateCrossFading = false;
                g.SetLODs(lods.ToArray());
                g.RecalculateBounds();
            }

            var col = root.AddComponent<CapsuleCollider>();
            col.radius = def == Coastal ? .24f : .20f;
            col.height = def == Coastal ? 2.1f : 2.4f;
            col.center = new Vector3(0f, col.height * .5f, 0f);
            return root;
        }

        static Material GrassMaterial()
        {
            const string key = "grass_runtime";
            if (materials.TryGetValue(key, out var m) && m != null) return m;
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) return null;
            m = new Material(shader) { name = "Vegetation_Grass", enableInstancing = true };
            var baseMap = Resources.Load<Texture2D>(GrassTex + "_BaseColor");
            var normal = Resources.Load<Texture2D>(GrassTex + "_Normal");
            var mask = Resources.Load<Texture2D>(GrassTex + "_Mask");
            if (baseMap != null) m.SetTexture("_BaseMap", baseMap);
            if (normal != null) { m.SetTexture("_BumpMap", normal); m.EnableKeyword("_NORMALMAP"); }
            if (mask != null)
            {
                m.SetTexture("_OcclusionMap", mask);
                m.SetFloat("_OcclusionStrength", .5f);
                m.EnableKeyword("_OCCLUSIONMAP");
            }
            m.SetFloat("_Metallic", 0f); m.SetFloat("_Smoothness", .035f);
            m.SetFloat("_AlphaClip", 1f); m.SetFloat("_Cutoff", .42f);
            m.EnableKeyword("_ALPHATEST_ON"); m.renderQueue = (int)RenderQueue.AlphaTest;
            m.doubleSidedGI = true; if (m.HasProperty("_Cull")) m.SetFloat("_Cull", (float)CullMode.Off);
            if (m.HasProperty("_SpecularHighlights")) m.SetFloat("_SpecularHighlights", 0f);
            m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            materials[key] = m; return m;
        }

        static Mesh GrassMesh(int variant)
        {
            var p = Load(GrassRoot + "grass_patch_" + variant);
            var f = p != null ? p.GetComponentInChildren<MeshFilter>(true) : null;
            return f != null ? f.sharedMesh : null;
        }

        static void AddGrass(ResortSite site, Transform parent, System.Random rng)
        {
            var mat = GrassMaterial(); if (mat == null) return;
            var meshes = new[] { GrassMesh(0), GrassMesh(1), GrassMesh(2) };
            int count = 0;
            // Shuffle the whole grid: no front-loaded grass quota on a 2 km island.
            var candidates = new List<Vector2>();
            for(float z=site.Data.avenue.z+34f;z<site.Data.size.z-12f;z+=9.5f)
                for(float x=14f;x<site.Data.size.x-14f;x+=9.5f)
                    candidates.Add(new Vector2(x,z));
            for(int k=candidates.Count-1;k>0;k--)
            {
                int swap=rng.Next(k+1);var temp=candidates[k];
                candidates[k]=candidates[swap];candidates[swap]=temp;
            }
            int maximum=site.Data.size.x>1500?2400:900;
            foreach(var cell in candidates)
            {
                if(count>=maximum) break;
                {
                    float px=cell.x+(float)(rng.NextDouble()*6-3), pz=cell.y+(float)(rng.NextDouble()*6-3);
                    if (!Free(site, px, pz, 2.1f)) continue;
                    float cluster = Mathf.PerlinNoise(px * .018f + 4.7f, pz * .018f + 9.3f);
                    if (cluster < .36f || rng.NextDouble() > .68) continue;
                    var mesh = meshes[rng.Next(meshes.Length)]; if (mesh == null) continue;
                    var go = new GameObject("Grass_" + count++);
                    go.transform.SetParent(parent, false);
                    go.transform.position = new Vector3(px, site.HeightAt(px, pz) + .025f, pz);
                    go.transform.rotation = Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f);
                    float sc = Mathf.Lerp(2.8f, 5.8f, (float)rng.NextDouble());
                    go.transform.localScale = new Vector3(sc, sc * Mathf.Lerp(.85f, 1.1f, (float)rng.NextDouble()), sc);
                    go.AddComponent<MeshFilter>().sharedMesh = mesh;
                    var mr = go.AddComponent<MeshRenderer>(); mr.sharedMaterial = mat;
                    mr.shadowCastingMode = ShadowCastingMode.Off; mr.receiveShadows = true;
                }
            }
            Debug.Log("COASTAL_VEGETATION grass=" + count);
        }

        static bool ParcelFree(ResortSite site, float x, float z, float margin)
        {
            if (!RoadClear(site, x, z, margin)) return false;
            if (NearLot(site.Data, x, z, margin + 1.5f)) return false;
            return true;
        }

        static void AddParcelGrove(
            ResortSite site, CoastalVegetationState state, Transform parent, Rect2 parcel,
            int hideAtStage, int maxTrees, int maxGrass, System.Random rng,
            ref int globalTreeIndex, ref int parcelTreeTotal, ref int parcelGrassTotal)
        {
            if (parcel == null) return;

            var group = new GameObject("TemporaryParcelVegetation_" + parcel.id);
            group.transform.SetParent(parent, false);
            state.Register(group, hideAtStage);

            int treeCount = 0;
            float treeStep = parcel.id == "P5" ? 13.5f : 12.5f;
            for (float z = parcel.z + 7f; z < parcel.z + parcel.depth - 7f && treeCount < maxTrees; z += treeStep)
            {
                for (float x = parcel.x + 7f; x < parcel.x + parcel.width - 7f && treeCount < maxTrees; x += treeStep)
                {
                    float px = x + (float)(rng.NextDouble() * 7 - 3.5);
                    float pz = z + (float)(rng.NextDouble() * 7 - 3.5);
                    if (px < parcel.x + 5f || px > parcel.x + parcel.width - 5f ||
                        pz < parcel.z + 5f || pz > parcel.z + parcel.depth - 5f) continue;
                    if (!ParcelFree(site, px, pz, 4.6f)) continue;

                    float cluster = Mathf.PerlinNoise(px * .021f + hideAtStage * 3.1f, pz * .021f + 19.7f);
                    if (cluster < .34f && rng.NextDouble() > .34) continue;

                    TreeDef def = (globalTreeIndex % 4 == 0 && Load(Small.LOD(0)) != null) ? Small : Coastal;
                    float sc = Mathf.Lerp(def.minScale, def.maxScale, (float)rng.NextDouble());
                    Tree(def, group.transform, new Vector3(px, site.HeightAt(px, pz) + .02f, pz),
                        (float)rng.NextDouble() * 360f, sc, globalTreeIndex++);
                    treeCount++;
                    parcelTreeTotal++;
                }
            }

            var mat = GrassMaterial();
            var meshes = new[] { GrassMesh(0), GrassMesh(1), GrassMesh(2) };
            int grassCount = 0;
            if (mat != null)
            {
                for (float z = parcel.z + 4f; z < parcel.z + parcel.depth - 4f && grassCount < maxGrass; z += 7f)
                {
                    for (float x = parcel.x + 4f; x < parcel.x + parcel.width - 4f && grassCount < maxGrass; x += 7f)
                    {
                        float px = x + (float)(rng.NextDouble() * 5 - 2.5);
                        float pz = z + (float)(rng.NextDouble() * 5 - 2.5);
                        if (!ParcelFree(site, px, pz, 1.6f)) continue;
                        if (Mathf.PerlinNoise(px * .032f + 7.4f, pz * .032f + hideAtStage) < .36f && rng.NextDouble() > .48) continue;
                        var mesh = meshes[rng.Next(meshes.Length)];
                        if (mesh == null) continue;

                        var go = new GameObject("ParcelGrass_" + grassCount++);
                        go.transform.SetParent(group.transform, false);
                        go.transform.position = new Vector3(px, site.HeightAt(px, pz) + .025f, pz);
                        go.transform.rotation = Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f);
                        float sc = Mathf.Lerp(2.8f, 5.2f, (float)rng.NextDouble());
                        go.transform.localScale = new Vector3(sc, sc * Mathf.Lerp(.82f, 1.12f, (float)rng.NextDouble()), sc);
                        go.AddComponent<MeshFilter>().sharedMesh = mesh;
                        var mr = go.AddComponent<MeshRenderer>();
                        mr.sharedMaterial = mat;
                        mr.shadowCastingMode = ShadowCastingMode.Off;
                        mr.receiveShadows = true;
                        parcelGrassTotal++;
                    }
                }
            }

            Debug.Log("COASTAL_VEGETATION parcel=" + parcel.id + " trees=" + treeCount + " grass=" + grassCount + " hideAtStage=" + hideAtStage);
        }

        static void AddTemporaryParcelVegetation(
            ResortSite site, CoastalVegetationState state, Transform parent, System.Random rng,
            ref int globalTreeIndex)
        {
            int treeTotal = 0, grassTotal = 0;
            Rect2 Find(string id) => site.Data.parcels != null ? Array.Find(site.Data.parcels, p => p.id == id) : null;

            AddParcelGrove(site, state, parent, Find("P2"), 3, 8, 28, rng, ref globalTreeIndex, ref treeTotal, ref grassTotal);
            AddParcelGrove(site, state, parent, Find("P3"), 4, 18, 48, rng, ref globalTreeIndex, ref treeTotal, ref grassTotal);
            AddParcelGrove(site, state, parent, Find("P4"), 5, 30, 72, rng, ref globalTreeIndex, ref treeTotal, ref grassTotal);
            AddParcelGrove(site, state, parent, Find("P5"), 6, 108, 240, rng, ref globalTreeIndex, ref treeTotal, ref grassTotal);
            AddParcelGrove(site, state, parent, Find("P6"), 7, 40, 96, rng, ref globalTreeIndex, ref treeTotal, ref grassTotal);

            Debug.Log("COASTAL_VEGETATION temporaryParcelTrees=" + treeTotal + " temporaryParcelGrass=" + grassTotal);
        }

        static void AddStreetTreeLines(ResortSite site, Transform parent, System.Random rng, ref int treeIndex)
        {
            int planted = 0;
            int nextIndex = treeIndex;
            const int maxStreetTrees = 140;

            void TryPlant(float x, float z, float yawBias)
            {
                if (planted >= maxStreetTrees) return;
                if (!Free(site, x, z, 4.8f)) return;
                float sc = Mathf.Lerp(Small.minScale * .94f, Small.maxScale * 1.08f, (float)rng.NextDouble());
                TreeDef def = Load(Small.LOD(0)) != null && ((nextIndex + planted) % 3 != 0) ? Small : Coastal;
                Tree(def, parent, new Vector3(x, site.HeightAt(x, z) + .02f, z),
                    yawBias + (float)rng.NextDouble() * 55f - 27.5f, sc, nextIndex++);
                planted++;
            }

            // A deliberate green promenade behind the waterfront avenue.
            float avenueZ = site.Data.avenue.z + site.Data.avenue.width * .5f + 20f;
            for (float x = 26f; x < site.Data.size.x - 26f && planted < maxStreetTrees; x += 23f)
                TryPlant(x + (float)(rng.NextDouble() * 3f - 1.5f), avenueZ, 90f);

            // Tree-lined neighborhood streets. Only plant on free buildable ground, never on roads,
            // sidewalks, authored lots or reserved resort parcels.
            if (site.Data.streetsEW != null)
            {
                foreach (var ew in site.Data.streetsEW)
                {
                    float north = ew.z + ew.width * .5f + 8.5f;
                    float south = ew.z - ew.width * .5f - 8.5f;
                    for (float x = 34f; x < site.Data.size.x - 34f && planted < maxStreetTrees; x += 31f)
                    {
                        TryPlant(x + (float)(rng.NextDouble() * 3f - 1.5f), north, 90f);
                        TryPlant(x + (float)(rng.NextDouble() * 3f - 1.5f), south, 90f);
                    }
                }
            }

            if (site.Data.streetsNS != null)
            {
                foreach (var ns in site.Data.streetsNS)
                {
                    float east = ns.x + ns.width * .5f + 8.5f;
                    float west = ns.x - ns.width * .5f - 8.5f;
                    for (float z = site.Data.avenue.z + site.Data.avenue.width * .5f + 34f;
                         z < site.Data.size.z - 26f && planted < maxStreetTrees; z += 34f)
                    {
                        TryPlant(east, z + (float)(rng.NextDouble() * 3f - 1.5f), 0f);
                        TryPlant(west, z + (float)(rng.NextDouble() * 3f - 1.5f), 0f);
                    }
                }
            }

            treeIndex = nextIndex;
            Debug.Log("COASTAL_VEGETATION streetTrees=" + planted);
        }

        public static void Build(ResortSite site)
        {
            if (site == null || site.Data == null || Load(Coastal.LOD(0)) == null) return;
            var root = new GameObject("RealisticCoastalVegetation").transform;
            root.SetParent(site.transform, false);
            var state = root.gameObject.AddComponent<CoastalVegetationState>();
            var trees = new GameObject("Trees").transform; trees.SetParent(root, false);
            var grass = new GameObject("GroundCover").transform; grass.SetParent(root, false);
            var rng = new System.Random(20261007);

            int count = 0;
            for (float z = site.Data.avenue.z + 34f; z < site.Data.size.z - 12f && count < 360; z += 13.5f)
            {
                for (float x = 14f; x < site.Data.size.x - 14f && count < 360; x += 13.5f)
                {
                    float px = x + (float)(rng.NextDouble() * 8 - 4), pz = z + (float)(rng.NextDouble() * 8 - 4);
                    if (!Free(site, px, pz, 5.2f)) continue;
                    float cluster = Mathf.PerlinNoise(px * .0125f + 12.4f, pz * .0125f + 28.1f);
                    bool edgeBelt = px < 58f || px > site.Data.size.x - 58f || pz > site.Data.size.z - 68f;
                    if (!edgeBelt && cluster < .34f) continue;
                    if (!edgeBelt && rng.NextDouble() > .82) continue;

                    TreeDef def = (count % 5 == 0 && Load(Small.LOD(0)) != null) ? Small : Coastal;
                    float sc = Mathf.Lerp(def.minScale, def.maxScale, (float)rng.NextDouble());
                    Tree(def, trees, new Vector3(px, site.HeightAt(px, pz) + .02f, pz),
                         (float)rng.NextDouble() * 360f, sc, count++);
                }
            }

            AddStreetTreeLines(site, trees, rng, ref count);
            AddGrass(site, grass, rng);
            AddTemporaryParcelVegetation(site, state, root, rng, ref count);
            Debug.Log("COASTAL_VEGETATION totalTrees=" + count + " source=PolyHaven_CC0 optimizedLODs");
        }
    }
}
