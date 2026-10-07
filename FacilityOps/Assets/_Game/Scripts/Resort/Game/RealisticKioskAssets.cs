using System.Collections.Generic;
using ResortAurora.Site;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Game
{
    /// <summary>Selective CC0 furniture and project-owned PBR dressing. No changes to the service simulation or seat ownership.</summary>
    public static class RealisticKioskAssets
    {
        static readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        const string Textures = "Art/Resort/Textures/";

        static Material MaterialFor(string set)
        {
            if (materials.TryGetValue(set, out var cached) && cached != null) return cached;
            var color = Resources.Load<Texture2D>(Textures + set + "_BaseColor");
            var normal = Resources.Load<Texture2D>(Textures + set + "_Normal");
            var gloss = Resources.Load<Texture2D>(Textures + set + "_MetallicGloss");
            if (color == null || normal == null || gloss == null) return null;
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "PBR_" + set, enableInstancing = true };
            m.SetTexture("_BaseMap", color); m.SetTexture("_BumpMap", normal);
            m.EnableKeyword("_NORMALMAP"); m.SetFloat("_BumpScale", 0.65f);
            m.SetTexture("_MetallicGlossMap", gloss); m.EnableKeyword("_METALLICSPECGLOSSMAP");
            m.SetFloat("_Smoothness", 1f);
            var ao = Resources.Load<Texture2D>(Textures + set + "_AO");
            if (ao != null) { m.SetTexture("_OcclusionMap", ao); m.EnableKeyword("_OCCLUSIONMAP"); m.SetFloat("_OcclusionStrength", 0.65f); }
            materials[set] = m; return m;
        }

        static void Spawn(GameObject prefab, Transform parent, string name, Vector3 position, float yaw, Material material)
        {
            var obj = Object.Instantiate(prefab, parent, false);
            obj.name = name; obj.transform.localPosition = position; obj.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            var renderers = obj.GetComponentsInChildren<MeshRenderer>();
            foreach (var r in renderers) { r.name = name; r.sharedMaterial = material; }
            var lod = obj.AddComponent<LODGroup>();
            lod.SetLODs(new[] { new LOD(0.015f, renderers) }); lod.RecalculateBounds();
        }

        public static void Dress(Transform root)
        {
            var table = Resources.Load<GameObject>("Art/Resort/Furniture/Table");
            var chair = Resources.Load<GameObject>("Art/Resort/Furniture/Chair");
            var tableMat = MaterialFor("furniture_table"); var chairMat = MaterialFor("furniture_chair");
            // A complete set is required before hiding any fallback geometry.
            if (table != null && chair != null && tableMat != null && chairMat != null)
                foreach (var group in root.GetComponentsInChildren<Transform>(true))
                {
                    if (group.name != "S1_Table" && group.name != "S1_TableExtra") continue;
                    foreach (var renderer in group.GetComponentsInChildren<MeshRenderer>(true))
                        if (renderer.name == "S1_TableTop" || renderer.name == "S1_TableLeg" || renderer.name.StartsWith("S1_Chair"))
                            Object.Destroy(renderer); // retain the table's collision and all seat/upgrade data
                    Spawn(table, group, "S1_RealisticTable", Vector3.zero, 0f, tableMat);
                    Spawn(chair, group, "S1_RealisticChair", new Vector3(-0.78f, 0f, 0f), 90f, chairMat);
                    Spawn(chair, group, "S1_RealisticChair", new Vector3(0.78f, 0f, 0f), 270f, chairMat);
                    // Collider follows the smaller real tabletop, without changing customer anchors.
                    var collider = group.Find("S1_TableTop").GetComponent<BoxCollider>();
                    collider.size = new Vector3(0.692f / 0.95f, 1f, 0.692f / 0.95f);
                }
            var zinc = MaterialFor("galvanizado");
            if (zinc == null) return;
            Mesh roofMesh = null;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
                if (filter.name.StartsWith("Awning"))
                {
                    if (roofMesh == null)
                    {
                        roofMesh = Object.Instantiate(filter.sharedMesh); roofMesh.name = "RoofMetreUV";
                        var uv = roofMesh.uv;
                        // KioskDecor may already provide metre-scaled UVs. Scale
                        // only the original unit cube, avoiding a second stretch.
                        if (filter.sharedMesh.name != "SurfaceMetreUV")
                            for (int i = 0; i < uv.Length; i++) uv[i] = Vector2.Scale(uv[i], new Vector2(0.88f, 4.4f));
                        roofMesh.uv = uv; roofMesh.RecalculateTangents();
                    }
                    filter.sharedMesh = roofMesh; filter.GetComponent<MeshRenderer>().sharedMaterial = zinc;
                }
        }

        /// <summary>A single textured surface following the existing ground; the original terrain collider remains authoritative.</summary>
        public static void BuildPromenade(ResortSite site)
        {
            var material = MaterialFor("pedra_portuguesa");
            if (material == null) return;
            const int across = 5;
            int along = Mathf.CeilToInt(site.Data.size.x / 3f) + 1;
            var vertices = new Vector3[along * across]; var uv = new Vector2[vertices.Length];
            for (int i = 0; i < along; i++)
                for (int j = 0; j < across; j++)
                {
                    float x = Mathf.Min(i * 3f, site.Data.size.x), z = site.PromenadeZ(x) - 5.95f + j * (11.9f / (across - 1));
                    int k = i * across + j;
                    vertices[k] = new Vector3(x, site.HeightAt(x, z) + 0.015f, z);
                    uv[k] = new Vector2(x, z) / 2f; // authored tile is two metres
                }
            var triangles = new int[(along - 1) * (across - 1) * 6]; int t = 0;
            for (int i = 0; i < along - 1; i++)
                for (int j = 0; j < across - 1; j++)
                {
                    int a = i * across + j, b = a + across, c = a + 1, d = b + 1;
                    triangles[t++] = a; triangles[t++] = c; triangles[t++] = b;
                    triangles[t++] = b; triangles[t++] = c; triangles[t++] = d;
                }
            var mesh = new Mesh { name = "PromenadePBR", vertices = vertices, uv = uv, triangles = triangles };
            mesh.RecalculateNormals(); mesh.RecalculateTangents(); mesh.RecalculateBounds();
            var go = new GameObject("PromenadePBR"); go.transform.SetParent(site.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>(); r.sharedMaterial = material;
            r.shadowCastingMode = ShadowCastingMode.Off;
        }
    }
}
