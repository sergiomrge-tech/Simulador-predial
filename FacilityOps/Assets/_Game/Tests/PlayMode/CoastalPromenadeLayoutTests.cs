using NUnit.Framework;
using ResortAurora.Site;
using UnityEngine;

namespace ResortAurora.Tests
{
    public class CoastalPromenadeLayoutTests
    {
        [Test]
        public void CoastalAvenueBufferIsOneMetreAndBeachUsesDenseDryWetPBR()
        {
            var sceneRoot = new GameObject("CoastalPromenade_QA");
            try
            {
                var site = sceneRoot.AddComponent<ResortSite>();
                site.Build();
                Assert.IsTrue(site.Ready, "Site must initialize");
                Assert.AreEqual(1f, CoastalPromenadeAvenueLink.RoadEdge(site.Data)
                    - CoastalPromenadeAvenueLink.LinkEnd(site.Data), 0.001f);
                var walkway = sceneRoot.transform.Find("PromenadeAvenueLink_1mBuffer");
                Assert.IsNotNull(walkway, "Missing continuous link to avenue");
                var linkMesh = walkway.GetComponent<MeshFilter>().sharedMesh;
                Assert.Greater(linkMesh.vertexCount, 12000, "The esplanade must conform to terrain, not span it with giant triangles");
                var buffer = sceneRoot.transform.Find("CoastalAvenueBuffer_Exactly1m");
                Assert.IsNotNull(buffer, "Missing continuous metre buffer");
                var stripMesh = buffer.GetComponent<MeshFilter>().sharedMesh;
                for (int i = 0; i < stripMesh.vertexCount; i += 2)
                    Assert.AreEqual(1f, stripMesh.vertices[i + 1].z - stripMesh.vertices[i].z, .001f);

                var beach = sceneRoot.transform.Find("BeachSandPBR");
                Assert.IsNotNull(beach);
                var beachMesh = beach.GetComponent<MeshFilter>().sharedMesh;
                Assert.Greater(beachMesh.vertexCount, 18000, "Old 17-row beach mesh intersects terrain");
                var material = beach.GetComponent<MeshRenderer>().sharedMaterial;
                Assert.IsTrue(material != null && material.shader != null && material.shader.isSupported);
                Assert.AreEqual("ResortAurora/CoastalSand", material.shader.name);
                Assert.IsNotNull(material.GetTexture("_DryColor"));
                Assert.IsNotNull(material.GetTexture("_WetColor"));
            }
            finally { Object.DestroyImmediate(sceneRoot); }
        }
    }
}
