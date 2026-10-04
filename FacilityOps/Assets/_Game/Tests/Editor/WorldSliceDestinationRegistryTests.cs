using NUnit.Framework;

namespace FacilityOps.Tests
{
    public sealed class WorldSliceDestinationRegistryTests
    {
        [TestCase("home.starter", "SA_M01_01_S00_02")]
        [TestCase("garage", "SA_M01_01_S01_03")]
        [TestCase("horizonte", "SA_M01_02_S02_00")]
        [TestCase("grocery", "SA_M01_02_S01_02")]
        public void Pilot_Destinations_Map_To_Approved_Cells(
            string facility,
            string expectedCell)
        {
            WorldSliceDestination destination =
                WorldSliceDestinationRegistry.Require(facility);

            Assert.That(destination.Cell.Name, Is.EqualTo(expectedCell));
        }

        [Test]
        public void Horizonte_Prefers_Authoritative_Blender_Spawn_Marker()
        {
            WorldSliceDestination destination =
                WorldSliceDestinationRegistry.Require("horizonte");

            Assert.That(
                destination.PreferredMarkerSuffix,
                Is.EqualTo("GP_prologue_spawn_corridor"));
        }

        [Test]
        public void Unknown_Facility_Is_Not_Silently_Routed()
        {
            Assert.That(
                WorldSliceDestinationRegistry.TryGet(
                    "outside-pilot",
                    out _),
                Is.False);
        }
    }
}
