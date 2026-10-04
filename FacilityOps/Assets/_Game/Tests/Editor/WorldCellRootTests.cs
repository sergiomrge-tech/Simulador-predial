using NUnit.Framework;
using UnityEngine;

namespace FacilityOps.Tests
{
    public sealed class WorldCellRootTests
    {
        [Test]
        public void Configure_Preserves_Stable_Cell_Metadata()
        {
            var go = new GameObject("cell-test");
            try
            {
                var root = go.AddComponent<WorldCellRoot>();
                root.Configure("SA_M01_02_S02_00", true, true);

                Assert.That(root.CellId, Is.EqualTo("SA_M01_02_S02_00"));
                Assert.That(root.ContainsGameplayMarkers, Is.True);
                Assert.That(root.HighFidelityPilotCell, Is.True);
                Assert.That(root.TryGetStreamingId(out var id), Is.True);
                Assert.That(id.Name, Is.EqualTo("SA_M01_02_S02_00"));
            }
            finally
            {
                Object.DestroyImmediate(go);
            }
        }
    }
}
