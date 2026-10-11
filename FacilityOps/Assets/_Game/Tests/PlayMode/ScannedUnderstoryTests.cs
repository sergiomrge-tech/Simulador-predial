using NUnit.Framework;
using ResortAurora.Site;
using UnityEngine;

namespace ResortAurora.Tests
{
    public class ScannedUnderstoryTests
    {
        [Test]
        public void CC0VegetationFillsGrassyBlocksWithoutObstructingRoads()
        {
            var root=new GameObject("Understory_QA");
            try
            {
                var site=root.AddComponent<ResortSite>();
                site.Build();
                Assert.IsTrue(site.Ready);
                var vegetation=root.transform.Find("ScannedUnderstory_CC0_FernsShrubs");
                Assert.IsNotNull(vegetation,"Poly Haven plants must be used in the real resort map");
                int total=vegetation.childCount, fern=0, shrub=0, deepInland=0, coastalVerge=0;
                Assert.Greater(total,650,"New vegetation too sparse for visible grassland");
                for(int i=0;i<total;i++)
                {
                    var plant=vegetation.GetChild(i);
                    var p=plant.position;
                    Assert.IsFalse(CoastalUrbanGround.IsRoad(site.Data,p.x,p.z),"Plant inside carriageway");
                    Assert.IsFalse(CoastalUrbanGround.IsSidewalk(site.Data,p.x,p.z),"Plant blocks sidewalk");
                    Assert.IsNull(plant.GetComponentInChildren<Collider>(),"Scanned vegetation should not obstruct gameplay");
                    var renderer=plant.GetComponentInChildren<MeshRenderer>();
                    Assert.IsNotNull(renderer);
                    Assert.IsNotNull(renderer.sharedMaterial);
                    Assert.IsTrue(renderer.sharedMaterial.IsKeywordEnabled("_ALPHATEST_ON"),"Leaf alpha cutout missing");
                    if(plant.position.z>site.Data.avenue.z+site.Data.avenue.width*.5f+150f)deepInland++;
                    if(plant.position.z<site.Data.avenue.z+site.Data.avenue.width*.5f+55f)coastalVerge++;
                    if(plant.name.Contains("fern"))fern++;else shrub++;
                }
                Assert.Greater(fern,35,"No ferns");
                Assert.Greater(shrub,35,"No new shrubs");
                Assert.Greater(deepInland,75,"Plants must fill inland grassland as well");
                Assert.Greater(coastalVerge,40,"Plants must fill grassy avenue verges");
                Debug.Log($"UNDERSTORY_QA_PASS total={total} ferns={fern} shrubs={shrub}");
            }
            finally {Object.DestroyImmediate(root);}
        }
    }
}
