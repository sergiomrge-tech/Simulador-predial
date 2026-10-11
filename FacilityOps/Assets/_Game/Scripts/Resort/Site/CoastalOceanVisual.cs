using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace ResortAurora.Site
{
    /// <summary>GPU animated ocean tiles. Dense only in the breaking zone, shared
    /// material, conservative displacement bounds, no opaque SeaBase or collider.</summary>
    public sealed class CoastalOceanVisual : MonoBehaviour
    {
        readonly List<Mesh> meshes = new List<Mesh>();
        Material material;
        public static GameObject Build(ResortSite site)
        {
            var root = new GameObject("CoastalOcean");
            var owner = root.AddComponent<CoastalOceanVisual>();
            var shader = Resources.Load<Shader>("Coastal/CoastalOcean");
            if (shader == null) throw new System.InvalidOperationException("CoastalOcean shader missing.");
            owner.material = new Material(shader) { name = "CoastalOceanURP" };
            owner.material.SetTexture("_NormalA", Resources.Load<Texture2D>("Coastal/OceanNormalA"));
            owner.material.SetTexture("_NormalB", Resources.Load<Texture2D>("Coastal/OceanNormalB"));
            // Contract: use supported public URP settings; no renderer feature or package edits.
            var pipeline = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (pipeline != null) { pipeline.supportsCameraDepthTexture = true; pipeline.supportsCameraOpaqueTexture = true; }
            float x0 = -512, x1 = site.Data.size.x + 512;
            for (float x = x0; x < x1; x += 64)
                owner.Tile(site, x, Mathf.Min(x + 64, x1), -6, 64, 1.5f, 1.25f);
            // Offshore patches retain enough geometry for low amplitude swell and cull individually.
            for (float x = x0; x < x1; x += 128)
                owner.Tile(site, x, Mathf.Min(x + 128, x1), 64, 256, 8, 8);
            for (float x = x0; x < x1; x += 256)
                owner.Tile(site, x, Mathf.Min(x + 256, x1), 256, 1800, 16, 24);
            IslandOceanRing.Build(site, owner.material, root.transform);
            return root;
        }
        void Tile(ResortSite site, float x0, float x1, float d0, float d1, float dx, float dz)
        {
            int nx = Mathf.CeilToInt((x1 - x0) / dx) + 1, nz = Mathf.CeilToInt((d1 - d0) / dz) + 1;
            var v = new Vector3[nx * nz]; var uv = new Vector2[v.Length]; var shoreUV = new Vector2[v.Length];
            var t = new int[(nx - 1) * (nz - 1) * 6]; int k = 0;
            for (int i = 0; i < nx; i++)
            {
                float x = Mathf.Lerp(x0, x1, i / (float)(nx - 1));
                float shore = site.WaterlineZ(Mathf.Clamp(x, 0, site.Data.size.x));
                for (int j = 0; j < nz; j++)
                {
                    float distance = Mathf.Lerp(d0, d1, j / (float)(nz - 1)); int a = i * nz + j;
                    v[a] = new Vector3(x, site.Data.seaLevel, shore - distance);
                    uv[a] = new Vector2(x, shore - distance); shoreUV[a] = new Vector2(distance, shore);
                    if (i == nx - 1 || j == nz - 1) continue;
                    int b = a + nz; t[k++] = a; t[k++] = b; t[k++] = a + 1;
                    t[k++] = b; t[k++] = b + 1; t[k++] = a + 1;
                }
            }
            var mesh = new Mesh { name = "Ocean_" + x0 + "_" + d0, vertices = v, uv = uv, uv2 = shoreUV, triangles = t };
            mesh.RecalculateBounds(); var bounds = mesh.bounds; bounds.Expand(new Vector3(0, 1.2f, 0)); mesh.bounds = bounds; meshes.Add(mesh);
            var go = new GameObject(mesh.name); go.transform.SetParent(transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>(); renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = true;
        }
        void OnDestroy() { foreach (var mesh in meshes) if (mesh != null) Destroy(mesh); if (material != null) Destroy(material); }
    }
}
