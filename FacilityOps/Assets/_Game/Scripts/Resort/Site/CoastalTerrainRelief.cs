using UnityEngine;

namespace ResortAurora.Site
{
    /// <summary>
    /// Mild coastal topography applied to both site heightfields before mesh/collider creation.
    /// No waves or fixed location assumptions: the profile follows the actual shoreline,
    /// keeps the promenade and kiosk access flat, and works for either site size.
    /// </summary>
    public static class CoastalTerrainRelief
    {
        static float BaseHeight(float[] h, SiteData data, float x, float z)
        {
            float fx = Mathf.Clamp(x / data.step, 0f, data.columns - 1f);
            float fz = Mathf.Clamp(z / data.step, 0f, data.rows - 1f);
            int i = Mathf.Min((int)fx, data.columns - 2);
            int j = Mathf.Min((int)fz, data.rows - 2);
            float u = fx - i, v = fz - j;
            int k = j * data.columns + i;
            return Mathf.Lerp(
                Mathf.Lerp(h[k], h[k + 1], u),
                Mathf.Lerp(h[k + data.columns], h[k + data.columns + 1], u), v);
        }

        static float Promenade(SiteData data, float x)
        {
            var p = data.promenade;
            if (p == null || p.Length == 0) return 0f;
            if (x <= p[0].x) return p[0].z;
            for (int i = 1; i < p.Length; i++)
                if (x <= p[i].x)
                    return Mathf.Lerp(p[i - 1].z, p[i].z,
                        (x - p[i - 1].x) / Mathf.Max(0.001f, p[i].x - p[i - 1].x));
            return p[p.Length - 1].z;
        }

        static float FindShore(float[] h, SiteData data, float x, float promenadeZ)
        {
            for (float z = promenadeZ - 10f; z > 5f; z -= Mathf.Max(0.6f, data.step))
                if (BaseHeight(h, data, x, z) <= data.seaLevel + 0.05f)
                    return z;
            return Mathf.Max(5f, promenadeZ - 110f);
        }

        static float Gaussian(float u, float center, float invWidth)
        {
            float a = (u - center) * invWidth;
            return Mathf.Exp(-a * a);
        }

        static float Smooth01(float a, float b, float x)
        {
            float u = Mathf.Clamp01((x - a) / Mathf.Max(0.0001f, b - a));
            return u * u * (3f - 2f * u);
        }

        /// <summary>
        /// Original terrain remains the collision authority. Apply exactly once after loading,
        /// before BuildTerrain, so HeightAt, NPCs, level transitions and colliders stay aligned.
        /// </summary>
        public static void Apply(SiteData data, float[] graded, float[] natural)
        {
            if (data == null || data.promenade == null || data.promenade.Length < 2) return;
            ApplySingle(data, graded);
            if (!ReferenceEquals(graded, natural)) ApplySingle(data, natural);
        }

        static void ApplySingle(SiteData data, float[] heights)
        {
            if (heights == null || heights.Length != data.columns * data.rows) return;
            int count = data.columns;
            float[] shore = new float[count];
            float[] edge = new float[count];

            for (int i = 0; i < count; i++)
            {
                float x = i * data.step;
                float promenade = Promenade(data, x);
                shore[i] = FindShore(heights, data, x, promenade);
                edge[i] = promenade - 8.5f; // promenade slab, paths and adjacent roads untouched
            }

            for (int j = 0; j < data.rows; j++)
            {
                float z = j * data.step;
                for (int i = 0; i < count; i++)
                {
                    int index = j * count + i;
                    float x = i * data.step;
                    float width = edge[i] - shore[i];
                    if (width < 18f || z < shore[i] + 4f || z > edge[i]) continue;
                    if (heights[index] <= data.seaLevel + 0.08f) continue;

                    float u = Mathf.Clamp01((z - shore[i] - 4f) / (width - 4f));
                    float edgeFade = Smooth01(0f, 0.16f, u) * (1f - Smooth01(0.84f, 1f, u));
                    float kioskFade = data.stall == null ? 1f
                        : Smooth01(12f, 48f, Mathf.Abs(x - data.stall.x));
                    float sideFade = Smooth01(0f, 24f, x) *
                        (1f - Smooth01(data.size.x - 24f, data.size.x, x));
                    float variation = 0.70f + 0.30f * Mathf.PerlinNoise(x * 0.027f, z * 0.041f);
                    float rollingDune = Gaussian(u, 0.74f, 4.8f) * 0.95f * variation;
                    float berm = Gaussian(u, 0.37f, 7f) * 0.27f;
                    float smallRidges = (Mathf.PerlinNoise(x * 0.11f, z * 0.072f) - 0.5f)
                        * 0.24f * Gaussian(u, 0.63f, 2.8f);

                    // No changes beneath the promenade, along the kiosk access or at the waterline.
                    heights[index] += Mathf.Max(0f, rollingDune + berm + smallRidges) *
                        edgeFade * kioskFade * sideFade;
                }
            }
        }
    }
}
