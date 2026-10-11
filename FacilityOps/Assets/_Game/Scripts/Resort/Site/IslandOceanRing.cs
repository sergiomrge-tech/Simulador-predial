using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Site
{
    /// <summary>Water and natural sandy shores on the other three coasts of the 2km² island.
    /// Builds true geometry in the real Unity scene, using the same animated URP/PBR
    /// materials as the main beach. No synthetic background or fake captures.</summary>
    public sealed class IslandOceanRing : MonoBehaviour
    {
        readonly List<Mesh> generated = new List<Mesh>();
        readonly List<Material> ownedMaterials = new List<Material>();
        enum Side { North, West, East }
        const float SeaOffset = 0.025f;

        public static GameObject Build(ResortSite site, Material animatedOcean, Transform parent)
        {
            if(site == null || site.Data == null || site.Data.size.x < 1800f) return null;
            var go=new GameObject("IslandOceanRing_ThreeNewCoasts");
            go.transform.SetParent(parent,false);
            var ring=go.AddComponent<IslandOceanRing>();
            var sandShader=Resources.Load<Shader>("Coastal/CoastalSand");
            Material sand=null;
            if(sandShader!=null && sandShader.isSupported)
            {
                sand=new Material(sandShader){name="IslandBeaches_PolyHaven_PBR"};
                bool maps=true;
                foreach(var layer in new[]{"Dry","Wet"})
                    foreach(var channel in new[]{"Color","Normal","Rough","AO"})
                    {
                        var tx=Resources.Load<Texture2D>("Coastal/"+layer+channel);
                        if(tx==null) maps=false; else sand.SetTexture("_"+layer+channel,tx);
                    }
                sand.SetFloat("_DryMetres",2f);sand.SetFloat("_WetMetres",2f);
                if(!maps) { Destroy(sand);sand=null; }
                else ring.ownedMaterials.Add(sand);
            }
            foreach(Side side in Enum.GetValues(typeof(Side)))
            {
                // The coast mesh is explicit rather than a rectangle that covers land.
                ring.Strip(site, side, -2f, 126f, 8f, 3.2f, animatedOcean, false);
                ring.Strip(site, side, 126f, 1500f, 36f, 52f, animatedOcean, false);
                if(sand!=null) ring.Strip(site, side, -0.5f, -32f, 5f, 1.5f, sand, true);
            }
            Debug.Log("ISLAND_OCEAN_RING active=true coasts=North,West,East beachPBR="+(sand!=null));
            return go;
        }

        static float FindShore(ResortSite s,Side side,float along)
        {
            var d=s.Data;
            if(side==Side.North)
            {
                float x=Mathf.Clamp(along,0,d.size.x);
                for(float z=d.size.z-2f;z>=d.size.z-180f;z-=2f)
                    if(s.HeightAt(x,z)>d.seaLevel+0.12f) return z+1f;
                return d.size.z-80f;
            }
            float zz=Mathf.Clamp(along,0,d.size.z-1f);
            if(side==Side.West)
            {
                for(float x=2;x<220;x+=2)
                    if(s.HeightAt(x,zz)>d.seaLevel+.12f) return x-1f;
                return 65f;
            }
            for(float x=d.size.x-2f;x>d.size.x-220f;x-=2f)
                if(s.HeightAt(x,zz)>d.seaLevel+.12f) return x+1f;
            return d.size.x-65f;
        }

        void Strip(ResortSite s,Side side,float offset0,float offset1,
            float alongStep,float perpendicularStep,Material mat,bool beach)
        {
            float beginning = side==Side.North ? -18f : 275f;
            float ending = side==Side.North ? s.Data.size.x+18f : s.Data.size.z+18f;
            int na=Mathf.CeilToInt((ending-beginning)/alongStep)+1;
            int np=Mathf.CeilToInt(Mathf.Abs(offset1-offset0)/perpendicularStep)+1;
            var v=new Vector3[na*np];
            var u=new Vector2[v.Length];var depthUV=new Vector2[v.Length];
            for(int i=0;i<na;i++)
            {
                float along=Mathf.Lerp(beginning,ending,i/(float)(na-1));
                float shore=FindShore(s,side,along);
                for(int j=0;j<np;j++)
                {
                    float offset=Mathf.Lerp(offset0,offset1,j/(float)(np-1));
                    float x=side==Side.North?along:shore+(side==Side.East?offset:-offset);
                    float z=side==Side.North?shore+offset:along;
                    float y=beach?s.HeightAt(x,z)+.092f:s.Data.seaLevel+SeaOffset;
                    int k=i*np+j;v[k]=new Vector3(x,y,z);
                    u[k]=new Vector2(x,z);
                    depthUV[k]=new Vector2(beach?-offset:offset,shore);
                }
            }
            var triangles=new int[(na-1)*(np-1)*6];int t=0;
            for(int i=0;i<na-1;i++)for(int j=0;j<np-1;j++)
            {
                int a=i*np+j,b=a+np,c=a+1,e=b+1;
                triangles[t++]=a;triangles[t++]=c;triangles[t++]=b;
                triangles[t++]=b;triangles[t++]=c;triangles[t++]=e;
            }
            var mesh=new Mesh {
                name=(beach?"Sand_":"Water_")+side+"_"+offset0,
                indexFormat=IndexFormat.UInt32,vertices=v,uv=u,uv2=depthUV,triangles=triangles
            };
            mesh.RecalculateBounds();
            if(beach) {mesh.RecalculateNormals();mesh.RecalculateTangents();}
            else {var b=mesh.bounds;b.Expand(new Vector3(0f,1.3f,0f));mesh.bounds=b;}
            generated.Add(mesh);
            var go=new GameObject(mesh.name);go.transform.SetParent(transform,false);
            go.AddComponent<MeshFilter>().sharedMesh=mesh;
            var renderer=go.AddComponent<MeshRenderer>();renderer.sharedMaterial=mat;
            renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;
        }
        void OnDestroy()
        {
            foreach(var m in generated)if(m!=null)Destroy(m);
            foreach(var m in ownedMaterials)if(m!=null)Destroy(m);
        }
    }
}
