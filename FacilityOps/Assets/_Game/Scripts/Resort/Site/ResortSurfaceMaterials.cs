using System.Collections.Generic;
using UnityEngine;

namespace ResortAurora.Site
{
    /// <summary>Project-owned surface maps, shared materials and metre-scaled cube UVs.</summary>
    public static class ResortSurfaceMaterials
    {
        static readonly Dictionary<Vector3, Mesh> cubes = new Dictionary<Vector3, Mesh>();

        public static void ApplyMaps(Material material, string set, float tile = 1f, float bump = 0.35f)
        {
            string path = "Art/Resort/Textures/" + set;
            var baseMap = Resources.Load<Texture2D>(path + "_BaseColor");
            var normal = Resources.Load<Texture2D>(path + "_Normal");
            var mask = Resources.Load<Texture2D>(path + "_Mask");
            if (baseMap != null) material.SetTexture("_BaseMap", baseMap);
            if (normal != null)
            {
                material.SetTexture("_BumpMap", normal);
                material.SetFloat("_BumpScale", bump);
                material.EnableKeyword("_NORMALMAP");
            }
            if (mask != null)
            {
                material.SetTexture("_MetallicGlossMap", mask);
                material.SetTexture("_OcclusionMap", mask);
                material.SetFloat("_Smoothness", 1f);
                material.SetFloat("_SmoothnessTextureChannel", 0f);
                material.SetFloat("_OcclusionStrength", 0.65f);
                material.EnableKeyword("_METALLICSPECGLOSSMAP");
                material.EnableKeyword("_OCCLUSIONMAP");
            }
            var scale = Vector2.one / tile;
            material.SetTextureScale("_BaseMap", scale);
            material.SetTextureScale("_BumpMap", scale);
            material.SetTextureScale("_MetallicGlossMap", scale);
            material.SetTextureScale("_OcclusionMap", scale);
        }

        public static Material Create(string set, Color tint, float tile = 1f)
        {
            var material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "ResortPBR_" + set };
            material.SetColor("_BaseColor", tint);
            material.SetFloat("_Smoothness", 0.15f);
            ApplyMaps(material, set, tile);
            return material;
        }

        public static Mesh MetreCube(Vector3 size)
        {
            if (cubes.TryGetValue(size, out var cached) && cached != null) return cached;
            var mesh = Object.Instantiate(Resources.GetBuiltinResource<Mesh>("Cube.fbx"));
            mesh.name = "SurfaceMetreUV";
            var vertices = mesh.vertices; var normals = mesh.normals;
            var uv = new Vector2[vertices.Length];
            for (int i = 0; i < vertices.Length; i++)
            {
                var p = Vector3.Scale(vertices[i], size); var n = normals[i];
                uv[i] = Mathf.Abs(n.y) > 0.5f ? new Vector2(p.x, p.z) :
                    Mathf.Abs(n.x) > 0.5f ? new Vector2(p.z * Mathf.Sign(n.x), p.y) : new Vector2(-p.x * Mathf.Sign(n.z), p.y);
            }
            mesh.uv = uv; mesh.RecalculateTangents();
            cubes[size] = mesh;
            return mesh;
        }

        /// <summary>One PBR sand surface follows the same heightfield/collider.
        /// The local CC0 scan adds close detail without changing terrain physics.</summary>
        // Paving spans PromenadeZ +/- 5.95 and sits .015 m over the ground.
        const float SandEdgeOffset = 5.95f, SandLift = .10f, SandEdgeLift = .005f, SandTaper = 1f;

        public static void BuildBeach(ResortSite site)
        {
            if (Resources.Load<Texture2D>("Art/Resort/Textures/sand_BaseColor") == null) return;
            // Sample the actual heightfield no more than 0.75 m apart. The old 17
            // longitudinal bands bridged dunes and intersected the terrain,
            // producing black patches and bright sand streaks.
            int columns = Mathf.CeilToInt(site.Data.size.x / 1.5f) + 1;
            float widestBeach = 0f;
            for (int probe = 0; probe <= columns; probe++)
            {
                float x = Mathf.Min(probe * 1.5f, site.Data.size.x);
                widestBeach = Mathf.Max(widestBeach, site.PromenadeZ(x) - SandEdgeOffset - (site.WaterlineZ(x) - .40f));
            }
            int rows = Mathf.Max(20, Mathf.CeilToInt(widestBeach / .75f) + 1);
            var vertices = new Vector3[columns * rows];
            var uv = new Vector2[vertices.Length];
            var shoreDistance = new Vector2[vertices.Length];
            for (int i = 0; i < columns; i++)
            {
                float x = Mathf.Min(i * 1.5f, site.Data.size.x);
                float shore = site.WaterlineZ(x) - .40f, edge = site.PromenadeZ(x) - SandEdgeOffset;
                for (int j = 0; j < rows; j++)
                {
                    float z = Mathf.Lerp(shore, edge, j / (float)(rows - 1));
                    int k = i * rows + j;
                    // The sand runs right up to the paving (no bare-terrain gap) and settles
                    // from its .10 m lift to just under the paving over the last metre, so
                    // the seam has neither a lip nor a strip of the terrain tint.
                    float lift = Mathf.Lerp(SandEdgeLift, SandLift, Mathf.SmoothStep(0f, 1f, (edge - z) / SandTaper));
                    vertices[k] = new Vector3(x, site.HeightAt(x, z) + lift, z);
                    // World-space metres; the shader controls physical scan tiling.
                    uv[k] = new Vector2(x, z);
                    shoreDistance[k] = new Vector2(z - site.WaterlineZ(x), 0f);
                }
            }
            var triangles = new int[(columns - 1) * (rows - 1) * 6]; int t = 0;
            for (int i = 0; i < columns - 1; i++)
                for (int j = 0; j < rows - 1; j++)
                {
                    int a = i * rows + j, b = a + rows, c = a + 1, d = b + 1;
                    triangles[t++] = a; triangles[t++] = c; triangles[t++] = b;
                    triangles[t++] = b; triangles[t++] = c; triangles[t++] = d;
                }
            var mesh = new Mesh { name = "BeachSandPBR", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32, vertices = vertices, uv = uv, uv2 = shoreDistance, triangles = triangles };
            mesh.RecalculateNormals(); mesh.RecalculateTangents(); mesh.RecalculateBounds();
            var surface = new GameObject("BeachSandPBR"); surface.transform.SetParent(site.transform, false);
            surface.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = surface.AddComponent<MeshRenderer>();
            // Prefer the coherent Poly Haven CC0 wet/dry scanned sand; keep an explicit
            // stable PBR fallback if any import is incomplete.
            var coastalShader = Resources.Load<Shader>("Coastal/CoastalSand");
            Material coastalMaterial = null;
            if (coastalShader != null && coastalShader.isSupported)
            {
                var candidate = new Material(coastalShader) { name = "CoastalSand_DryWet_CC0" };
                bool allMaps = true;
                foreach (var layer in new[] { "Dry", "Wet" })
                    foreach (var channel in new[] { "Color", "Normal", "Rough", "AO" })
                    {
                        var map = Resources.Load<Texture2D>("Coastal/" + layer + channel);
                        if (map == null) { allMaps = false; break; }
                        candidate.SetTexture("_" + layer + channel, map);
                    }
                if (allMaps)
                {
                    candidate.SetFloat("_DryMetres", 2f);
                    candidate.SetFloat("_WetMetres", 2f);
                    coastalMaterial = candidate;
                }
                else Object.Destroy(candidate);
            }
            renderer.sharedMaterial = coastalMaterial != null ? coastalMaterial : Create("sand", Color.white);
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }
    }
}
