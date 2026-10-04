using NUnit.Framework;
using UnityEngine;

namespace FacilityOps.Tests
{
    public sealed class WorldStreamingIdTests
    {
        [Test]
        public void Parse_RoundTrips_All_1024_Subcells()
        {
            for (int mx = 0; mx < WorldStreamingId.MacroCellCountPerAxis; mx++)
            for (int mz = 0; mz < WorldStreamingId.MacroCellCountPerAxis; mz++)
            for (int sx = 0; sx < WorldStreamingId.SubcellsPerMacroAxis; sx++)
            for (int sz = 0; sz < WorldStreamingId.SubcellsPerMacroAxis; sz++)
            {
                var expected = new WorldStreamingId(mx, mz, sx, sz);
                Assert.That(WorldStreamingId.TryParse(expected.Name, out var parsed), Is.True, expected.Name);
                Assert.That(parsed, Is.EqualTo(expected), expected.Name);
            }
        }

        [TestCase("SA_M08_00_S00_00")]
        [TestCase("SA_M00_08_S00_00")]
        [TestCase("SA_M00_00_S04_00")]
        [TestCase("SA_M00_00_S00_04")]
        [TestCase("SA_M1_00_S00_00")]
        [TestCase("not-a-cell")]
        public void Parse_Rejects_Invalid_Cell_Ids(string value)
        {
            Assert.That(WorldStreamingId.TryParse(value, out _), Is.False);
        }

        [Test]
        public void World_Position_Maps_To_Expected_Hero_Cells()
        {
            Assert.That(
                WorldStreamingId.FromWorldPosition(-2860f, -2280f).Name,
                Is.EqualTo("SA_M01_01_S00_02"));

            Assert.That(
                WorldStreamingId.FromWorldPosition(-2700f, -2150f).Name,
                Is.EqualTo("SA_M01_01_S01_03"));

            Assert.That(
                WorldStreamingId.FromWorldPosition(-2350f, -1800f).Name,
                Is.EqualTo("SA_M01_02_S02_00"));

            Assert.That(
                WorldStreamingId.FromWorldPosition(-2580f, -1480f).Name,
                Is.EqualTo("SA_M01_02_S01_02"));
        }

        [Test]
        public void Cell_Center_RoundTrips_Through_Position()
        {
            var id = new WorldStreamingId(1, 2, 2, 0);
            Vector2 center = id.WorldCenterXZ;
            Assert.That(WorldStreamingId.FromWorldPosition(center.x, center.y), Is.EqualTo(id));
        }
    }
}
