using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Site
{
    /// <summary>
    /// Real Poly Haven CC0 scanned low vegetation, not prototype cubes/billboards.
    /// Deterministic landscaping on otherwise empty grassy terrain; authored plots,
    /// roads, sidewalks, hotel construction sites and player paths remain clear.
    /// </summary>
    public static class ScannedUnderstory
    {
        const string Root = "Art/Resort/Vegetation/ScannedUnderstory/";
        sealed class Species
        {
            public string id;
            public float low, high;
            public int cap;
            public float occupy;
            public int placed;
            public Material material;
            public GameObject prefab;
            public Species(string id,float low,float high,int cap,float occupy)
            {this.id=id;this.low=low;this.high=high;this.cap=cap;this.occupy=occupy;}
        }

        static readonly Species[] Flora = {
            new Species("fern_02",.72f,1.12f,360,1.25f),
            new Species("shrub_03",.75f,1.35f,260,1.10f),
            new Species("shrub_04",.90f,1.65f,100,.95f),
            // Larger, denser scans are deliberately used as occasional focal shrubs.
            new Species("shrub_02",.43f,.65f,40,2.25f)
        };

        static readonly Dictionary<string,Material> Materials = new Dictionary<string,Material>();
        static bool Clear(ResortSite site,float x,float z,float radius)
        {
            var d=site.Data;
            if(site.HeightAt(x,z)<=d.seaLevel+.65f) return false;
            if(x<9+radius||x>d.size.x-9-radius||z<d.avenue.z+d.avenue.width*.5f+7f+radius||
                z>d.size.z-10-radius) return false;

            // Clearance for a plant's actual dimensions, including roads and the road-side
            // pedestrian path. No clipping into crossings, kerbs or infrastructure.
            for(int i=0;i<9;i++)
            {
                float a=i*Mathf.PI*.25f;
                float xx=i==0?x:x+Mathf.Cos(a)*radius;
                float zz=i==0?z:z+Mathf.Sin(a)*radius;
                if(CoastalUrbanGround.IsRoad(d,xx,zz)||CoastalUrbanGround.IsSidewalk(d,xx,zz))
                    return false;
            }

            if(d.parcels!=null) foreach(var p in d.parcels)
                if(x>=p.x-radius-2&&x<=p.x+p.width+radius+2&&
                   z>=p.z-radius-2&&z<=p.z+p.depth+radius+2) return false;
            if(d.terraces!=null) foreach(var p in d.terraces)
                if(x>=p.x-radius-2&&x<=p.x+p.width+radius+2&&
                   z>=p.z-radius-2&&z<=p.z+p.depth+radius+2) return false;
            if(d.lots!=null) foreach(var lot in d.lots)
            {
                // Match CoastalVegetation's rotated footprint test.
                float a=-lot.rot*Mathf.Deg2Rad,cos=Mathf.Cos(a),sin=Mathf.Sin(a);
                float dx=x-lot.x,dz=z-lot.z;
                if(Mathf.Abs(cos*dx-sin*dz)<=lot.w*.5f+radius+2 &&
                   Mathf.Abs(sin*dx+cos*dz)<=lot.d*.5f+radius+2) return false;
            }
            if(d.home!=null&&Mathf.Abs(x-d.home.x)<d.home.width*.5f+radius+3 &&
                Mathf.Abs(z-d.home.z)<d.home.depth*.5f+radius+3) return false;
            return true;
        }

        static Material MaterialFor(Species specie)
        {
            if(Materials.TryGetValue(specie.id,out var existing)&&existing!=null) return existing;
            var tex=Resources.Load<Texture2D>(Root+specie.id+"/AlbedoOpacity");
            var shader=Shader.Find("Universal Render Pipeline/Lit");
            if(tex==null||shader==null) return null;
            var m=new Material(shader){name="PolyHavenCC0_"+specie.id,enableInstancing=true};
            m.SetTexture("_BaseMap",tex);
            m.SetColor("_BaseColor",new Color(.92f,.97f,.88f,1f));
            m.SetFloat("_Metallic",0f);
            m.SetFloat("_Smoothness",.06f);
            m.SetFloat("_AlphaClip",1f);
            m.SetFloat("_Cutoff",.38f);
            m.EnableKeyword("_ALPHATEST_ON");
            m.renderQueue=(int)RenderQueue.AlphaTest;
            m.doubleSidedGI=true;
            if(m.HasProperty("_Cull")) m.SetFloat("_Cull",(float)CullMode.Off);
            if(m.HasProperty("_SpecularHighlights")) m.SetFloat("_SpecularHighlights",0f);
            m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            Materials[specie.id]=m;
            return m;
        }

        static int AddModel(Species s,Transform root,ResortSite site,System.Random rng,float x,float z)
        {
            var model=UnityEngine.Object.Instantiate(s.prefab,root,false);
            model.name="CC0_"+s.id+"_"+s.placed;
            model.transform.position=new Vector3(x,site.HeightAt(x,z)+.012f,z);
            model.transform.rotation=Quaternion.Euler(0f,(float)rng.NextDouble()*360f,0f);
            float sc=Mathf.Lerp(s.low,s.high,(float)rng.NextDouble());
            model.transform.localScale=Vector3.one*sc;
            var renderers=model.GetComponentsInChildren<MeshRenderer>(true);
            foreach(var mr in renderers)
            {
                var mats=mr.sharedMaterials;
                for(int i=0;i<mats.Length;i++)mats[i]=s.material;
                mr.sharedMaterials=mats;
                mr.shadowCastingMode=ShadowCastingMode.Off;
                mr.receiveShadows=true;
                mr.gameObject.layer=0;
            }
            if(renderers.Length>0)
            {
                var lod=model.AddComponent<LODGroup>();
                lod.fadeMode=LODFadeMode.CrossFade;
                lod.SetLODs(new[]{new LOD(.007f,renderers)});
                lod.RecalculateBounds();
            }
            s.placed++;
            return renderers.Length;
        }

        public static void Build(ResortSite site)
        {
            if(site==null||site.Data==null) return;
            int available=0;
            foreach(var s in Flora)
            {
                s.placed=0;
                s.prefab=Resources.Load<GameObject>(Root+s.id+"/Model");
                s.material=MaterialFor(s);
                if(s.prefab!=null&&s.material!=null)available++;
                else Debug.LogWarning("CC0_UNDERSTORY_MISSING "+s.id);
            }
            if(available==0)return;
            var root=new GameObject("ScannedUnderstory_CC0_FernsShrubs").transform;
            root.SetParent(site.transform,false);
            var rng=new System.Random(20261008);
            int count=0, renderers=0;
            // Distribute through the ENTIRE grassland rather than exhausting the
            // species caps in the first 100 m inland (the previous row-major grid
            // made distant fields appear empty).
            var occupied=new List<Vector2>();
            float avenueNorth=site.Data.avenue.z+site.Data.avenue.width*.5f;
            foreach(var s in Flora)
            {
                int attempts=0;
                while(s.prefab!=null&&s.material!=null&&s.placed<s.cap&&attempts++<s.cap*140)
                {
                    float px=12f+(float)rng.NextDouble()*(site.Data.size.x-24f);
                    // A planted roadside belt receives about 27% of attempts;
                    // the remaining plants spread across open neighbourhood lawns.
                    float pz=rng.NextDouble()<.27
                        ? avenueNorth+12f+(float)rng.NextDouble()*33f
                        : avenueNorth+12f+(float)rng.NextDouble()*(site.Data.size.z-avenueNorth-24f);
                    float patch=Mathf.PerlinNoise(px*.016f+4.73f,pz*.018f+5.61f);
                    bool verge=pz<avenueNorth+48f;
                    if(patch<(verge?.16f:.28f))continue;
                    if(!Clear(site,px,pz,s.occupy))continue;
                    bool nearOther=false;
                    foreach(var taken in occupied)
                    {
                        if((taken-new Vector2(px,pz)).sqrMagnitude<6.25f)
                        {nearOther=true;break;}
                    }
                    if(nearOther)continue;
                    occupied.Add(new Vector2(px,pz));
                    renderers+=AddModel(s,root,site,rng,px,pz);
                    count++;
                }
            }
            Debug.Log($"CC0_UNDERSTORY_PLANTED total={count} fern={Flora[0].placed} " +
                $"shrub03={Flora[1].placed} shrub04={Flora[2].placed} shrub02={Flora[3].placed} " +
                $"renderers={renderers} alphaPBR=true noColliders=true");
        }
    }
}
