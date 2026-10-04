using System.IO;
using FacilityOps.Editor;
using NUnit.Framework;
using UnityEngine;

namespace FacilityOps.Tests
{
    public sealed class WorldMarkerImportValidationTests
    {
        [Test]
        public void Duplicate_Marker_Catalog_Is_Rejected_Before_Mutating_Gameplay()
        {
            string path = Path.GetTempFileName();
            var parent = new GameObject("Gameplay");
            string record = "{\"name\":\"GP_duplicate\",\"facilityId\":\"horizonte\",\"position\":[1,2,3],\"forward\":[0,0,1],\"up\":[0,1,0],\"scale\":[1,1,1]}";
            try
            {
                File.WriteAllText(path, "{\"schemaVersion\":1,\"status\":\"PASS\",\"markerCount\":2,\"markers\":[" + record + "," + record + "]}");
                Assert.Throws<InvalidDataException>(() => WorldGameplayMarkerImporter.ImportInto(path, parent.transform));
                Assert.That(parent.transform.childCount, Is.Zero);
            }
            finally { File.Delete(path); Object.DestroyImmediate(parent); }
        }
    }
}
