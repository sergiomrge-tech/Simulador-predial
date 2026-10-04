using NUnit.Framework;

namespace FacilityOps.Tests
{
    public sealed class WorldStreamingPolicyTests
    {
        [Test]
        public void Interior_Load_Set_Is_Three_By_Three()
        {
            var center = new WorldStreamingId(3, 3, 2, 2);
            var cells = WorldStreamingPolicy.BuildLoadSet(center);
            Assert.That(cells.Count, Is.EqualTo(9));
            Assert.That(cells.Contains(center), Is.True);
        }

        [Test]
        public void Interior_Keep_Set_Is_Five_By_Five()
        {
            var center = new WorldStreamingId(3, 3, 2, 2);
            var cells = WorldStreamingPolicy.BuildKeepSet(center);
            Assert.That(cells.Count, Is.EqualTo(25));
            Assert.That(cells.Contains(center), Is.True);
        }

        [Test]
        public void World_Corner_Clips_Neighborhood_To_Bounds()
        {
            var corner = new WorldStreamingId(0, 0, 0, 0);
            Assert.That(WorldStreamingPolicy.BuildLoadSet(corner).Count, Is.EqualTo(4));
            Assert.That(WorldStreamingPolicy.BuildKeepSet(corner).Count, Is.EqualTo(9));
        }

        [Test]
        public void Scene_Name_RoundTrips()
        {
            var id = new WorldStreamingId(1, 2, 2, 0);
            string scene = WorldStreamingSceneNaming.SceneName(id);
            Assert.That(scene, Is.EqualTo("SA_Cell_SA_M01_02_S02_00"));
            Assert.That(WorldStreamingSceneNaming.TryParseSceneName(scene, out var parsed), Is.True);
            Assert.That(parsed, Is.EqualTo(id));
        }
    }
}
