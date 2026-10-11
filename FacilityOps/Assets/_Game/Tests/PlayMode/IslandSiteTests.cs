using NUnit.Framework;
using ResortAurora.Site;
using UnityEngine;

namespace ResortAurora.Tests
{
    /// <summary>Real Unity geometry/regression gate for the 2 km² island and home.</summary>
    public class IslandSiteTests
    {
        [Test]
        public void IslandHasFourSeaBordersButHomeAndResortStayDry()
        {
            var root=new GameObject("Island_QA");
            try
            {
                var site=root.AddComponent<ResortSite>();
                site.Build();
                Assert.IsTrue(site.Ready,"Island site did not build");
                Assert.AreEqual(2000f,site.Data.size.x,.01f);
                Assert.AreEqual(1000f,site.Data.size.z,.01f);
                Assert.AreEqual(2000000f,site.Data.size.x*site.Data.size.z,.1f);

                Assert.Greater(site.HomeDoor.y,site.Data.seaLevel+1.5f,
                    "Player home must be above sea level");
                Assert.Greater(site.HeightAt(site.Data.stall.x,site.PromenadeZ(site.Data.stall.x)),
                    site.Data.seaLevel+.1f,"Promenade must be dry");

                foreach(float x in new[]{100f,700f,1100f,1600f,1930f})
                {
                    Assert.Less(site.HeightAt(x,site.Data.size.z-2f),site.Data.seaLevel,
                        "The entire north border must be submerged");
                    Assert.Less(site.HeightAt(x,2f),site.Data.seaLevel,
                        "The entire south border must be submerged");
                }
                foreach(float z in new[]{300f,490f,720f,950f})
                {
                    Assert.Less(site.HeightAt(2f,z),site.Data.seaLevel,"Western shore missing");
                    Assert.Less(site.HeightAt(site.Data.size.x-2f,z),site.Data.seaLevel,"Eastern shore missing");
                }
                var ring=root.transform.Find("CoastalOcean/IslandOceanRing_ThreeNewCoasts");
                Assert.IsNotNull(ring,"No real north/west/east ocean geometry in scene");
                Assert.GreaterOrEqual(ring.childCount,9,"Every new coastline needs water and sand");
                var green=root.transform.Find("ScannedUnderstory_CC0_FernsShrubs");
                Assert.IsNotNull(green,"New CC0 assets not used");
                Assert.Greater(green.childCount,350,"Island greenery insufficient");
                Debug.Log($"ISLAND_NATIVE_QA_PASS km2=2 homeX={site.Data.home.x} " +
                    $"homeZ={site.Data.home.doorZ} homeY={site.HomeDoor.y:F2} " +
                    $"oceanMeshes={ring.childCount} plants={green.childCount}");
            }
            finally {Object.DestroyImmediate(root);}
        }
    }
}
