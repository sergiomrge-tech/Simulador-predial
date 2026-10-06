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
            public float smoothness, metallic, tile;
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
                if (normal != null)
                {
                    m.EnableKeyword("_NORMALMAP");
                    m.SetTexture("_BumpMap", normal);
                    m.SetTextureScale("_BumpMap", new Vector2(s, s));
                    m.SetFloat("_BumpScale", 0.9f);
                }
            }
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
            return cache.TryGetValue(name, out m);
        }

        /// <summary>Replaces the placeholder materials of every renderer under <paramref name="root"/> with the authored ones (by name).</summary>
        public static void Apply(GameObject root)
        {
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials;
                for (int k = 0; k < mats.Length; k++)
                {
                    if (mats[k] == null) continue;
                    var n = System.Text.RegularExpressions.Regex.Replace(mats[k].name.Replace(" (Instance)", ""), @"\.\d{3}$", "");
                    if (TryGet(n, out var built)) mats[k] = built;
                }
                r.sharedMaterials = mats;
            }
        }
    }
}
