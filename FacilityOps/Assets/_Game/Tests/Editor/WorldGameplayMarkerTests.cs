using NUnit.Framework;
using UnityEngine;

namespace FacilityOps.Tests
{
    public sealed class WorldGameplayMarkerTests
    {
        [Test]
        public void Configure_Preserves_Blender_Marker_Contract()
        {
            var go = new GameObject("GP_test");
            try
            {
                var marker = go.AddComponent<WorldGameplayMarker>();
                marker.Configure(
                    "GP_quadro_tecnico",
                    "horizonte",
                    "interaction",
                    null,
                    null,
                    "quadro técnico",
                    "horizonte.markers.json");

                Assert.That(marker.MarkerName, Is.EqualTo("GP_quadro_tecnico"));
                Assert.That(marker.FacilityId, Is.EqualTo("horizonte"));
                Assert.That(marker.Kind, Is.EqualTo("interaction"));
                Assert.That(marker.Note, Is.EqualTo("quadro técnico"));
                Assert.That(marker.SourceCatalog, Is.EqualTo("horizonte.markers.json"));
            }
            finally
            {
                Object.DestroyImmediate(go);
            }
        }
    }
}
