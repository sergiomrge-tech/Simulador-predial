using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
namespace ResortAurora.EditorTools
{
    public static class ResortAssetAudit
    {
        [Serializable] public sealed class Row
        {
            public string path, guid, kind, status, licenseEvidence;
            public long bytes, vertices, triangles;
            public int meshes, lodGroups, lodLevels, colliders, animationClips;
            public string[] shaders, materialNames;
        }
        [Serializable] public sealed class Report { public Row[] assets; public int files, modelFiles, prefabs, materials, textures, animations; }
        public static void Run()
        {
            var rows=new List<Row>();
            foreach(var path in AssetDatabase.GetAllAssetPaths().Where(p=>p.StartsWith("Assets/") && File.Exists(p)))
            {
                var extension=Path.GetExtension(path).ToLowerInvariant();
                if(!new[]{".fbx",".prefab",".mat",".anim",".png",".jpg",".jpeg",".tga",".exr",".hdr"}.Contains(extension))continue;
                var row=new Row { path=path, guid=AssetDatabase.AssetPathToGUID(path), kind=extension, bytes=new FileInfo(path).Length,
                    status="IMPORTED_TECHNICAL_ONLY_VISUAL_REVIEW_REQUIRED",licenseEvidence="VERIFY_PROJECT_OR_LIBRARY_SOURCE_RECORD" };
                var loaded=AssetDatabase.LoadAllAssetsAtPath(path);
                foreach(var mesh in loaded.OfType<Mesh>())
                {
                    row.meshes++;row.vertices+=mesh.vertexCount;
                    for(int i=0;i<mesh.subMeshCount;i++) if(mesh.GetTopology(i)==MeshTopology.Triangles)row.triangles+=(long)mesh.GetIndexCount(i)/3;
                }
                row.animationClips=loaded.OfType<AnimationClip>().Count();
                var go=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var mats=go!=null?go.GetComponentsInChildren<Renderer>(true).SelectMany(r=>r.sharedMaterials).Where(m=>m!=null).Distinct().ToArray():loaded.OfType<Material>().ToArray();
                row.shaders=mats.Select(m=>m.shader!=null?m.shader.name:"MISSING").Distinct().ToArray();row.materialNames=mats.Select(m=>m.name).ToArray();
                if(go!=null)
                {
                    var lods=go.GetComponentsInChildren<LODGroup>(true);row.lodGroups=lods.Length;row.lodLevels=lods.Sum(l=>l.GetLODs().Length);
                    row.colliders=go.GetComponentsInChildren<Collider>(true).Length;
                }
                var folder=Path.GetDirectoryName(path);
                row.licenseEvidence=string.Join(";",Directory.GetFiles(folder).Where(p=>Path.GetFileName(p).IndexOf("license",StringComparison.OrdinalIgnoreCase)>=0 || Path.GetFileName(p).IndexOf("source",StringComparison.OrdinalIgnoreCase)>=0).Where(p=>!p.EndsWith(".meta")));
                if(path.EndsWith("Props/KioskShellF02.fbx"))row.licenseEvidence="D:/ProjectResort_AssetLibrary/ProjectOwned/KioskPremium_20261008/SOURCE.json";
                rows.Add(row);
            }
            var report=new Report{assets=rows.ToArray(),files=rows.Count,modelFiles=rows.Count(r=>r.kind==".fbx"),prefabs=rows.Count(r=>r.kind==".prefab"),materials=rows.Count(r=>r.kind==".mat"),textures=rows.Count(r=>new[]{".png",".jpg",".jpeg",".tga",".exr",".hdr"}.Contains(r.kind)),animations=rows.Count(r=>r.kind==".anim")};
            var root="D:/ProjectResort_Autonomy/CodexResortFinalAssets";Directory.CreateDirectory(root);
            File.WriteAllText(Path.Combine(root,"unity-imported-inventory.json"),JsonUtility.ToJson(report,true));
            Debug.Log("RESORT_ASSET_AUDIT files="+report.files+" models="+report.modelFiles+" prefabs="+report.prefabs+" materials="+report.materials+" textures="+report.textures);
        }
        public static void AuditAndBuild(){Run();ResortPreviewBuild.Run();}
    }
}
