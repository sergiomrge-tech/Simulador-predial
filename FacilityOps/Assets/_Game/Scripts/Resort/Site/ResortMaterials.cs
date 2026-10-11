using System;
using System.Collections.Generic;
using UnityEngine;

namespace ResortAurora.Site
{
    /// <summary>
    /// Builds the URP Lit materials for the exported resort pieces from <c>resort_materials.json</c> (written by export_resort_kit.py):
    /// authored PBR sets (base colour + normal, tiled in metres) where a material maps onto one, plain colour values otherwise.
    /// Pieces arrive from the FBX with placeholder materials; <see cref="Apply"/> swaps them by name.
    /// </summary>
    public static class ResortMaterials
    {
        [Serializable] sealed class Entry
        {
            public string name, set;
            public float[] color, emission;
            public float smoothness, metallic, tile, bump = 0.9f;
        }
        [Serializable] sealed class Table { public Entry[] list; }

        static Dictionary<string, Material> cache;

        public static void Load()
        {
            cache = new Dictionary<string, Material>();
            var ta = Resources.Load<TextAsset>("Art/Resort/resort_materials");
            if (ta == null) return;
            // the exporter writes {"materials": {name: {...}}}; JsonUtility cannot read dictionaries, so parse the object keys by hand
            var json = ta.text;
            int i = json.IndexOf("\"materials\"", StringComparison.Ordinal);
            if (i < 0) return;
            int depth = 0, start = -1;
            string key = null;
            for (int p = json.IndexOf('{', i + 11); p < json.Length; p++)
            {
                char c = json[p];
                if (c == '"' && depth == 1)
                {
                    int q = json.IndexOf('"', p + 1);
                    key = json.Substring(p + 1, q - p - 1);
                    p = q;
                }
                else if (c == '{') { depth++; if (depth == 2) start = p; }
                else if (c == '}')
                {
                    depth--;
                    if (depth == 1 && key != null) { cache[key] = Build(key, JsonUtility.FromJson<Entry>(json.Substring(start, p - start + 1))); key = null; }
                    if (depth == 0) break;
                }
            }
        }

        static Material Build(string name, Entry e)
        {
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = name };
            var c = e.color != null && e.color.Length >= 3 ? new Color(e.color[0], e.color[1], e.color[2], 1f) : Color.gray;
            m.SetColor("_BaseColor", c);
            m.SetFloat("_Smoothness", e.smoothness);
            m.SetFloat("_Metallic", e.metallic);
            if (!string.IsNullOrEmpty(e.set))
            {
                var baseTex = Resources.Load<Texture2D>("Art/Resort/Textures/" + e.set + "_BaseColor");
                var normal = Resources.Load<Texture2D>("Art/Resort/Textures/" + e.set + "_Normal");
                float s = e.tile > 0f ? 1f / e.tile : 1f;
                if (baseTex != null) { m.SetTexture("_BaseMap", baseTex); m.SetTextureScale("_BaseMap", new Vector2(s, s)); }
                if (normal != null && e.bump > 0.01f)
                {
                    m.EnableKeyword("_NORMALMAP");
                    m.SetTexture("_BumpMap", normal);
                    m.SetTextureScale("_BumpMap", new Vector2(s, s));
                    m.SetFloat("_BumpScale", e.bump);
                }
            }
            // Kiosk-specific mask packs metallic/R, AO/G and smoothness/A; preserve existing stage materials.
            if (name.StartsWith("Kiosk_", StringComparison.Ordinal) && !string.IsNullOrEmpty(e.set))
            {
                var mask = Resources.Load<Texture2D>("Art/Resort/Textures/" + e.set + "_Mask");
                if (mask != null)
                {
                    float tile = e.tile > 0f ? 1f / e.tile : 1f;
                    m.SetTexture("_MetallicGlossMap", mask); m.SetTexture("_OcclusionMap", mask);
                    m.SetTextureScale("_MetallicGlossMap", Vector2.one * tile);
                    m.SetTextureScale("_OcclusionMap", Vector2.one * tile);
                    m.SetFloat("_Smoothness", e.smoothness); m.SetFloat("_OcclusionStrength", .65f);
                    m.EnableKeyword("_METALLICSPECGLOSSMAP"); m.EnableKeyword("_OCCLUSIONMAP");
                }
            }
            m.enableInstancing = true;
            if (e.emission != null && e.emission.Length >= 4)
            {
                m.EnableKeyword("_EMISSION");
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                m.SetColor("_EmissionColor", new Color(e.emission[0], e.emission[1], e.emission[2]) * e.emission[3]);
            }
            return m;
        }

        public static bool TryGet(string name, out Material m)
        {
            if (cache == null) Load();
            if (cache.TryGetValue(name, out m) && m != null) return true;

            // With Enter Play Mode Options/domain reload disabled, static references can
            // survive after Unity has destroyed runtime-created Material objects.
            // Reload the authored table instead of reusing a fake-null destroyed material.
            Load();
            return cache.TryGetValue(name, out m) && m != null;
        }

        /// <summary>Replaces the placeholder materials of every renderer under <paramref name="root"/> with the authored ones (by name).</summary>
        static Material SafeFallback(string materialName, string rendererName)
        {
            string n = ((materialName ?? "") + " " + (rendererName ?? "")).ToLowerInvariant();
            Color c = new Color(0.72f, 0.70f, 0.64f);
            float smooth = 0.26f, metal = 0f;

            if (n.Contains("folha") || n.Contains("leaf") || n.Contains("verde") || n.Contains("palm") || n.Contains("palmeira") || n.Contains("bugan") || n.Contains("arbusto"))
            {
                c = new Color(0.14f, 0.30f, 0.09f); smooth = 0.10f;
            }
            else if (n.Contains("tronco") || n.Contains("wood") || n.Contains("madeira") || n.Contains("porta"))
            {
                c = new Color(0.34f, 0.22f, 0.12f); smooth = 0.22f;
            }
            else if (n.Contains("glass") || n.Contains("vidro") || n.Contains("janela"))
            {
                c = new Color(0.10f, 0.22f, 0.28f); smooth = 0.78f;
            }
            else if (n.Contains("telha") || n.Contains("roof") || n.Contains("cobertura"))
            {
                c = new Color(0.48f, 0.25f, 0.17f); smooth = 0.18f;
            }
            else if (n.Contains("metal") || n.Contains("aco") || n.Contains("steel") || n.Contains("alumin"))
            {
                c = new Color(0.46f, 0.48f, 0.50f); smooth = 0.48f; metal = 0.75f;
            }
            else if (n.Contains("parede") || n.Contains("wall") || n.Contains("reboco") || n.Contains("plaster") || n.Contains("pousada") || n.Contains("hotel"))
            {
                c = new Color(0.82f, 0.78f, 0.69f); smooth = 0.16f;
            }

            var sh = Shader.Find("Universal Render Pipeline/Lit");
            var m = new Material(sh) { name = "FallbackURP_" + (materialName ?? "material") };
            m.SetColor("_BaseColor", c);
            m.SetFloat("_Smoothness", smooth);
            m.SetFloat("_Metallic", metal);
            return m;
        }

        static bool NeedsFallback(Material m)
        {
            if (m == null || m.shader == null) return true;
            string sn = m.shader.name ?? "";
            return !m.shader.isSupported || sn.Contains("InternalErrorShader") || sn == "Standard" || sn.StartsWith("Legacy Shaders/");
        }

        public static void Apply(GameObject root)
        {
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials;
                for (int k = 0; k < mats.Length; k++)
                {
                    var original = mats[k];
                    if (original == null)
                    {
                        mats[k] = SafeFallback("null", r.name);
                        continue;
                    }
                    var n = System.Text.RegularExpressions.Regex.Replace(original.name.Replace(" (Instance)", ""), @"\.\d{3}$", "");
                    if (TryGet(n, out var built))
                    {
                        mats[k] = built;
                        continue;
                    }
                    if (NeedsFallback(original))
                    {
                        mats[k] = SafeFallback(n, r.name);
                        Debug.Log($"MATERIAL_FALLBACK root={root.name} renderer={r.name} material={n} shader={(original.shader != null ? original.shader.name : "null")}");
                    }
                }
                r.sharedMaterials = mats;
            }
        }
    }
}
