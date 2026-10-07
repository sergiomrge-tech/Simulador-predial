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
        public static void BuildBeach(ResortSite site)
        {
            if (Resources.Load<Texture2D>("Art/Resort/Textures/sand_BaseColor") == null) return;
            const int rows = 17;
            int columns = Mathf.CeilToInt(site.Data.size.x / 1.5f) + 1;
            var vertices = new Vector3[columns * rows];
            var uv = new Vector2[vertices.Length];
            for (int i = 0; i < columns; i++)
            {
                float x = Mathf.Min(i * 1.5f, site.Data.size.x);
                float shore = site.WaterlineZ(x) - 1f, edge = site.PromenadeZ(x) - 6.05f;
                for (int j = 0; j < rows; j++)
                {
                    float z = Mathf.Lerp(shore, edge, j / (float)(rows - 1));
                    int k = i * rows + j;
                    vertices[k] = new Vector3(x, site.HeightAt(x, z) + 0.012f, z);
                    uv[k] = new Vector2(x, z) / 4f;
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
            var mesh = new Mesh { name = "BeachSandPBR", vertices = vertices, uv = uv, triangles = triangles };
            mesh.RecalculateNormals(); mesh.RecalculateTangents(); mesh.RecalculateBounds();
            var surface = new GameObject("BeachSandPBR"); surface.transform.SetParent(site.transform, false);
            surface.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = surface.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = Create("sand", Color.white);
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }
    }
}
