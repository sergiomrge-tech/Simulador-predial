using System;
using System.Linq;
using NUnit.Framework;
using ResortAurora.Site;
using UnityEngine;

namespace ResortAurora.Tests
{
    /// <summary>Checks the terrain used for both beach rendering and collision, without starting play mode.</summary>
    public class CoastalTerrainReliefTests
    {
        [Test]
        public void CoastlineGetsActualElevationWhilePromenadeAndAccessRemainUntouched()
        {
            var data = JsonUtility.FromJson<SiteData>(Resources.Load<TextAsset>("Resort/ResortSite").text);
            var source = Resources.Load<TextAsset>("Resort/ResortSiteHeights_natural").bytes;
            var unchanged = new float[data.columns * data.rows];
            Buffer.BlockCopy(source, 0, unchanged, 0, source.Length);
            var altered = (float[])unchanged.Clone();
            CoastalTerrainRelief.Apply(data, altered, altered);
            Assert.AreEqual(unchanged.Length, altered.Length);

            int raised = 0, unsafeLowered = 0, promenadeChanged = 0, kioskChanged = 0;
            float maxRise = 0f;
            for (int j = 0; j < data.rows; j++)
            {
                float z = j * data.step;
                for (int i = 0; i < data.columns; i++)
                {
                    int k = j * data.columns + i;
                    float x = i * data.step, difference = altered[k] - unchanged[k];
                    if (difference > 0.12f) raised++;
                    if (difference < -0.0001f) unsafeLowered++;
                    maxRise = Mathf.Max(maxRise, difference);

                    if (Mathf.Abs(x - data.stall.x) < 12f && Mathf.Abs(difference) > 0.0001f) kioskChanged++;
                    if (z > PromenadeZ(data, x) - 8f && Mathf.Abs(difference) > 0.0001f) promenadeChanged++;
                    if (unchanged[k] <= data.seaLevel + 0.08f)
                        Assert.That(Mathf.Abs(difference), Is.LessThan(.0001f), "Waterline moved");
                }
            }
            Assert.That(raised, Is.GreaterThan(150), "Dunes not present in mesh/collider heightfield");
            Assert.That(maxRise, Is.InRange(.18f, 1.5f), "Relief outside gentle coastal range");
            Assert.AreEqual(0, unsafeLowered, "Must not excavate existing infrastructure");
            Assert.AreEqual(0, kioskChanged, "Kiosk access must stay at the original height");
            Assert.AreEqual(0, promenadeChanged, "Promenade must stay at the original height");
        }

        static float PromenadeZ(SiteData site, float x)
        {
            var p = site.promenade;
            if (x <= p[0].x) return p[0].z;
            for (int i = 1; i < p.Length; i++)
                if (x <= p[i].x)
                    return Mathf.Lerp(p[i - 1].z, p[i].z, (x - p[i - 1].x) / Mathf.Max(.001f, p[i].x - p[i - 1].x));
            return p[p.Length - 1].z;
        }
    }
}
