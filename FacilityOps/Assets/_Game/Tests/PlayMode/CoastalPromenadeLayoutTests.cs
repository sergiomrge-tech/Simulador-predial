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
                // The sand must run right up to the paving and settle under it: no strip of bare terrain, no lip.
                var sandVerts = beachMesh.vertices; float worstGap = 0f, worstLip = 0f; int onEdge = 0;
                for (int i = 0; i < sandVerts.Length; i++)
                {
                    var v = sandVerts[i];
                    float edge = site.PromenadeZ(v.x) - 5.95f;
                    if (v.z < edge - 0.05f) continue;
                    onEdge++;
                    worstGap = Mathf.Max(worstGap, Mathf.Abs(edge - v.z));
                    worstLip = Mathf.Max(worstLip, v.y - site.HeightAt(v.x, v.z));
                }
                Assert.Greater(onEdge, 100, "sand mesh has a vertex row on the paving edge");
                Assert.Less(worstGap, 0.05f, "sand reaches the paving edge");
                Assert.Less(worstLip, 0.02f, "sand is flush with the ground where it meets the paving");
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
