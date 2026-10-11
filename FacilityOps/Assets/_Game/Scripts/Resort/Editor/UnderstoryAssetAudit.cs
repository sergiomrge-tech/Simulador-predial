using UnityEditor;
using UnityEngine;
using System.Text;
namespace ResortAurora.EditorTools
{
    public static class UnderstoryAssetAudit
    {
        public static void Run()
        {
            foreach (var name in new [] { "fern_02","shrub_02","shrub_03","shrub_04" })
            {
                string prefix = "Art/Resort/Vegetation/ScannedUnderstory/"+name+"/";
                var prefab=Resources.Load<GameObject>(prefix+"Model");
                var albedo=Resources.Load<Texture2D>(prefix+"AlbedoOpacity");
                if(prefab==null||albedo==null) throw new System.InvalidOperationException("Missing imported CC0 model/texture for "+name);
                Bounds b = new Bounds(Vector3.zero, Vector3.zero);
                bool has=false; int tris=0, submeshes=0;
                foreach(var f in prefab.GetComponentsInChildren<MeshFilter>(true))
                {
                    if(f.sharedMesh==null) continue;
                    var mesh=f.sharedMesh;
                    var bounds=mesh.bounds;
                    var mn=f.transform.localToWorldMatrix.MultiplyPoint3x4(bounds.min);
                    var mx=f.transform.localToWorldMatrix.MultiplyPoint3x4(bounds.max);
                    if(!has){b=new Bounds((mn+mx)*.5f,Vector3.zero); has=true;}
                    b.Encapsulate(mn);b.Encapsulate(mx);
                    tris+=mesh.triangles.Length/3;submeshes+=mesh.subMeshCount;
                }
                Debug.Log($"CC0_UNDERSTORY_AUDIT asset={name} tris={tris} submeshes={submeshes} bounds={b.size} center={b.center} " +
                    $"albedoAlpha={albedo.format} prefab={prefab.name}");
                if(!has||tris==0) throw new System.InvalidOperationException("Empty mesh "+name);
            }
        }
    }
}
