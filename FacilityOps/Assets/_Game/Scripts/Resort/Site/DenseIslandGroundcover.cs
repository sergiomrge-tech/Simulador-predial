using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Site
{
    /// <summary>
    /// GPU-instanced Poly Haven CC0 grasses on the complete 1km2 island.
    /// Exclusion mask is generated from REAL ResortSite heightfield/roads/parcel
    /// geometry. No GameObject per tuft, no collision on vegetation and no
    /// CPU triangle soup. Only camera-visible 48m cells render.
    /// </summary>
    public sealed class DenseIslandGroundcover : MonoBehaviour
    {
        public const int CellMeters = 5;
        public const int MaskColumns = 250;
        public const int MaskRows = 160;
        public const float ChunkMetres = 48f;

        sealed class Chunk
        {
            public Vector3 center;
            public Bounds bounds;
            public readonly List<Matrix4x4>[] pending = {
                new List<Matrix4x4>(120), new List<Matrix4x4>(120), new List<Matrix4x4>(120)
            };
            public readonly Matrix4x4[][] matrices = new Matrix4x4[3][];
            public void Seal()
            {
                for(int i=0;i<matrices.Length;i++) {
                    matrices[i]=pending[i].ToArray();
                    pending[i].Clear();
                }
            }
        }
        readonly Dictionary<int,Chunk> chunksById = new Dictionary<int,Chunk>();
        readonly List<Chunk> chunks = new List<Chunk>();
        readonly Mesh[] meshes = new Mesh[3];
        Material material;
        Camera lastCam;
        Plane[] planes;
        int generated;
        public int GeneratedCount => generated;
        public int ChunkCount => chunks.Count;
        public bool Ready { get; private set; }

        public static DenseIslandGroundcover Attach(ResortSite site)
        {
            if(site==null||!site.Ready||site.Data==null||site.Data.size.x!=1250f||
               site.Data.size.z!=800f) return null;
            var old=site.GetComponentInChildren<DenseIslandGroundcover>();
            if(old!=null) return old;
            var go=new GameObject("DenseIslandGroundcover_CC0_Instanced");
            go.transform.SetParent(site.transform,false);
            var component=go.AddComponent<DenseIslandGroundcover>();
            if(!component.Generate(site)) {
                Destroy(go);
                return null;
            }
            return component;
        }

        Mesh LoadMesh(int variant)
        {
            var prefab=Resources.Load<GameObject>(
                "Art/Resort/Vegetation/grass_medium_01/grass_patch_"+variant);
            var mf=prefab==null?null:prefab.GetComponentInChildren<MeshFilter>(true);
            return mf!=null?mf.sharedMesh:null;
        }

        static Texture2D Texture(string suffix)
        {
            return Resources.Load<Texture2D>(
                "Art/Resort/Vegetation/grass_medium_01/textures/grass_medium_01_"+suffix);
        }

        Material CreateMaterial()
        {
            var shader=Shader.Find("Universal Render Pipeline/Lit");
            if(shader==null) return null;
            var m=new Material(shader) { name="CC0_Grass_Groundcover_1km2", enableInstancing=true };
            m.SetTexture("_BaseMap",Texture("BaseColor"));
            m.SetTexture("_BumpMap",Texture("Normal"));
            m.SetTexture("_OcclusionMap",Texture("Mask"));
            m.SetColor("_BaseColor",new Color(.86f,.95f,.78f,1f));
            m.SetFloat("_Metallic",0f);
            m.SetFloat("_Smoothness",.02f);
            m.SetFloat("_Cutoff",.42f);
            m.SetFloat("_AlphaClip",1f);
            m.EnableKeyword("_ALPHATEST_ON");
            m.EnableKeyword("_NORMALMAP");
            m.EnableKeyword("_OCCLUSIONMAP");
            m.renderQueue=(int)RenderQueue.AlphaTest;
            m.doubleSidedGI=true;
            if(m.HasProperty("_Cull"))m.SetFloat("_Cull",(float)CullMode.Off);
            return m;
        }

        bool Generate(ResortSite site)
        {
            var src=Resources.Load<TextAsset>("Resort/PlantingMask_1km2");
            if(src==null || src.bytes.Length!=MaskColumns*MaskRows) {
                Debug.LogError("GROUND_COVER_MASK missing or invalid; no grasses planted");
                return false;
            }
            var mask=src.bytes;
            material=CreateMaterial();
            for(int i=0;i<3;i++)meshes[i]=LoadMesh(i);
            if(material==null || Array.Exists(meshes,m=>m==null)) {
                Debug.LogError("GROUND_COVER_GRASS_CC0 meshes or URP shader missing");
                return false;
            }

            var rng=new System.Random(20261008);
            for(int j=0;j<MaskRows;j++)for(int i=0;i<MaskColumns;i++)
            {
                byte kind=mask[j*MaskColumns+i];
                // 6 wild grass, 7 urban lawn, 8 semi-dry coastal planting.
                if(kind!=6 && kind!=7 && kind!=8)continue;
                int number=kind==7?2:1;
                if(rng.NextDouble()<(kind==7?.55:kind==8?.6:.45))number++;
                for(int n=0;n<number;n++)
                {
                    float x=(i+.13f+(float)rng.NextDouble()*.74f)*CellMeters;
                    float z=(j+.13f+(float)rng.NextDouble()*.74f)*CellMeters;
                    float height=site.HeightAt(x,z);
                    if(height<site.Data.seaLevel+.76f) continue;
                    // Explicitly keep every path, beach, road and resort plot usable.
                    if(CoastalUrbanGround.IsRoad(site.Data,x,z) ||
                       CoastalUrbanGround.IsSidewalk(site.Data,x,z))continue;
                    int variant=rng.Next(3);
                    float sc=kind==7?Mathf.Lerp(2.3f,3.9f,(float)rng.NextDouble()):
                        kind==8?Mathf.Lerp(1.55f,2.65f,(float)rng.NextDouble()):
                        Mathf.Lerp(2.2f,3.8f,(float)rng.NextDouble());
                    var m=Matrix4x4.TRS(new Vector3(x,height+.035f,z),
                        Quaternion.Euler(0f,(float)rng.NextDouble()*360f,0f),
                        new Vector3(sc,sc*.75f,sc));
                    int gx=Mathf.FloorToInt(x/ChunkMetres);
                    int gz=Mathf.FloorToInt(z/ChunkMetres);
                    int id=gx+10000*gz;
                    if(!chunksById.TryGetValue(id,out var chunk))
                    {
                        var center=new Vector3((gx+.5f)*ChunkMetres,site.Data.seaLevel+10f,
                            (gz+.5f)*ChunkMetres);
                        chunk=new Chunk {
                            center=center,
                            bounds=new Bounds(center,new Vector3(ChunkMetres+25f,62f,ChunkMetres+25f))
                        };
                        chunksById[id]=chunk;
                        chunks.Add(chunk);
                    }
                    chunk.pending[variant].Add(m);
                    generated++;
                }
            }
            foreach(var ch in chunks)ch.Seal();
            chunksById.Clear();
            Ready=generated>0;
            Debug.Log($"ISLAND_GROUNDCOVER_1KM2 count={generated} cells={chunks.Count} gpuInstanced=true " +
                $"source=PolyHaven_CC0 noRoadCollisions=true");
            return Ready;
        }

        void OnEnable()
        {
            RenderPipelineManager.beginCameraRendering+=OnBeginCameraRendering;
        }
        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering-=OnBeginCameraRendering;
        }
        void OnBeginCameraRendering(ScriptableRenderContext context,Camera cam)
        {
            if(!Ready||cam==null || (cam.cameraType!=CameraType.Game && cam.cameraType!=CameraType.SceneView))
                return;
            float altitude=cam.transform.position.y;
            float drawDistance=altitude>100f?Mathf.Min(500f,altitude+60f):170f;
            float sq=drawDistance*drawDistance;
            var frustum=GeometryUtility.CalculateFrustumPlanes(cam);
            foreach(var chunk in chunks)
            {
                // Camera-height aware radius; keep GPU-work bounded in the real FPS view.
                Vector3 point=cam.transform.position;
                point.y=chunk.center.y;
                if((chunk.center-point).sqrMagnitude>sq)continue;
                if(!GeometryUtility.TestPlanesAABB(frustum,chunk.bounds))continue;
                for(int i=0;i<3;i++)
                {
                    var batch=chunk.matrices[i];
                    if(batch==null||batch.Length==0)continue;
                    // Unity GPU-instanced, 1023-instance batches by 48m culling tile.
                    // Every matrix is authored in true island-local metres.
                    for(int from=0;from<batch.Length;from+=1023)
                    {
                        int count=Math.Min(1023,batch.Length-from);
                        if(from==0 && count==batch.Length)
                            Graphics.DrawMeshInstanced(meshes[i],0,material,batch,count,
                                null,ShadowCastingMode.Off,true,0,cam,LightProbeUsage.Off);
                        else
                        {
                            var subset=new Matrix4x4[count];
                            Array.Copy(batch,from,subset,0,count);
                            Graphics.DrawMeshInstanced(meshes[i],0,material,subset,count,
                                null,ShadowCastingMode.Off,true,0,cam,LightProbeUsage.Off);
                        }
                    }
                }
            }
        }
        void OnDestroy()
        {
            if(material!=null) Destroy(material);
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void StartOnPlayableResortScene()
        {
            if(!Application.isPlaying)return;
            var boot=new GameObject("DenseIslandGroundcover_AutoLoader");
            boot.AddComponent<IslandGroundcoverAutoLoader>();
        }
    }

    /// <summary>Safe integration without racing other agents' ResortSite.cs edits.</summary>
    public sealed class IslandGroundcoverAutoLoader : MonoBehaviour
    {
        IEnumerator Start()
        {
            int frames=0;
            ResortSite site=null;
            while(frames++<600)
            {
                site=UnityEngine.Object.FindAnyObjectByType<ResortSite>();
                if(site!=null && site.Ready)break;
                yield return null;
            }
            if(site!=null && site.Ready &&
               Mathf.Approximately(site.Data.size.x,1250f) &&
               Mathf.Approximately(site.Data.size.z,800f))
            {
                DenseIslandGroundcover.Attach(site);
            }
            Destroy(gameObject);
        }
    }
}
