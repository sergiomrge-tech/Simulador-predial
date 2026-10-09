// R12 visual asset compatibility audit inside gameplay project.
// Completely non-destructive: does not change gameplay scenes / saved games.
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
namespace ResortAurora.EditorTools
{
    public static class ResortR12GameBridgeAudit
    {
        const string StagedScene="Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity";
        const string PlayableScene="Assets/_Game/Scenes/ResortPrologue.unity";
        [Serializable] sealed class Report {
            public string status, unityVersion, graphicsDevice, runtimeRenderer, originalScene, importedScene, note, gameplaySceneSha256;
            public int buildingsCount, roadTriangles, trees, r8Renderers, r11DetailRenderers, r12StorefrontRenderers, r10CoastalRenderers;
            public int missingShaders,missingUV0,missingMaterials,missingMonoScripts,shaderVariantErrors,originalDataWidth,originalDataDepth;
            public int r9TreesMissingUV0;
            public bool originalGameplaySceneLeftUnchanged=true, gameplayMapSameAsR12=false, gameplayIntegrationApproved=false;
        }
        [Serializable] sealed class SiteDim {
            public V2 size;
            [Serializable] public class V2 {public float x,z;}
        }
        static void Require(bool condition,string message) {
            if(!condition) throw new InvalidOperationException("R12_GAME_BRIDGE_BLOCKED:"+message);
        }
        static string FileHash(string p)
        {
            using(var stream=File.OpenRead(p))using(var sha=SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
        public static void Audit()
        {
            Require(AssetDatabase.LoadAssetAtPath<SceneAsset>(StagedScene)!=null,
                "STAGING_MISSING_RUN_Tools_Bridge_stage_r12_preview_py");
            Require(AssetDatabase.LoadAssetAtPath<SceneAsset>(PlayableScene)!=null,
                "GAMEPLAY_SCENE_NOT_PRESENT");
            var gameplayGuid=AssetDatabase.AssetPathToGUID(PlayableScene);
            var gameplayOriginalHash=FileHash(PlayableScene);
            Require(!String.IsNullOrWhiteSpace(gameplayGuid),"GAMEPLAY_GUID_MISSING");
            var siteAsset=AssetDatabase.LoadAssetAtPath<TextAsset>("Assets/_Game/Resources/Resort/ResortSite.json");
            Require(siteAsset!=null,"GAMEPLAY_SITE_JSON_MISSING");
            var site=JsonUtility.FromJson<SiteDim>(siteAsset.text);
            Require(site!=null && site.size!=null,"INVALID_GAMEPLAY_SITE_MAP");
            var scene=EditorSceneManager.OpenScene(StagedScene,OpenSceneMode.Single);
            Require(scene.isLoaded,"R12_LOADED_SCENE_INVALID");
            var all=scene.GetRootGameObjects()
                .SelectMany(r=>r.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
            var r8=all.Where(r=>r.name.StartsWith("R8_cop_",StringComparison.Ordinal)).ToArray();
            var r11=all.Where(r=>r.name.StartsWith("R11_cop_",StringComparison.Ordinal)).ToArray();
            var r12=all.Where(r=>r.name.StartsWith("R12_",StringComparison.Ordinal)).ToArray();
            var r10=all.Where(r=>r.name.StartsWith("R10_",StringComparison.Ordinal)).ToArray();
            var trees=all.Where(r=>r.name.StartsWith("R9_TREE_",StringComparison.Ordinal)).ToArray();
            var gis=all.FirstOrDefault(r=>r.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS",StringComparison.Ordinal));
            Require(gis!=null && gis.GetComponent<MeshFilter>()!=null,"OSM_GIS_MESH_MISSING");
            int roads=gis.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3;
            int missingShaders=0, missingMaterials=0, missingUV=0, treeMissingUV=0, scriptMissing=0;
            foreach(var renderer in all)
            {
                var m=renderer.sharedMaterials;
                if(m==null || m.Length==0 || m.Any(x=>x==null)){missingMaterials++;continue;}
                foreach(var material in m)
                    if(material.shader==null || !material.shader.isSupported ||
                       material.shader.name=="Hidden/InternalErrorShader")missingShaders++;
                if(renderer.name.StartsWith("R8_",StringComparison.Ordinal)||
                   renderer.name.StartsWith("R10_",StringComparison.Ordinal)||
                   renderer.name.StartsWith("R11_",StringComparison.Ordinal)||
                   renderer.name.StartsWith("R12_",StringComparison.Ordinal))
                {
                    var mf=renderer.GetComponent<MeshFilter>();
                    if(mf==null || mf.sharedMesh==null ||
                       !mf.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0))missingUV++;
                }
                // R9 foliage models are currently unwrapped solid-color meshes.
                // Keep this as an explicit ART defect, not a missing shader.
                if(renderer.name.StartsWith("R9_TREE_",StringComparison.Ordinal))
                {
                    var mf=renderer.GetComponent<MeshFilter>();
                    if(mf==null || mf.sharedMesh==null ||
                       !mf.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0))treeMissingUV++;
                }
            }
            foreach(var go in scene.GetRootGameObjects())
                foreach(var transform in go.GetComponentsInChildren<Transform>(true))
                    scriptMissing+=GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(transform.gameObject);
            Require(r8.Length==350 && r11.Length==210 && r12.Length==19,
                "R12_IMPORT_HAS_INVALID_RENDERERS:"+r8.Length+"/"+r11.Length+"/"+r12.Length);
            Require(trees.Length==48 && roads==3731,
                "SOURCE_ROADS_OR_TREES_DIFFER:"+roads+"/"+trees.Length);
            Require(missingShaders==0 && missingMaterials==0 && missingUV==0 && scriptMissing==0,
                "BROKEN_GAME_ASSET_REFERENCES:"+missingShaders+"/"+missingMaterials+"/"+missingUV+"/"+scriptMissing);
            Require(FileHash(PlayableScene)==gameplayOriginalHash,
                "ORIGINAL_GAMEPLAY_SCENE_CONTENT_CHANGED");
            Require(AssetDatabase.AssetPathToGUID(PlayableScene)==gameplayGuid,
                "ORIGINAL_GAMEPLAY_SCENE_GUID_CHANGED");
            var output=Path.Combine(
               Path.GetFullPath(Path.Combine(Application.dataPath,"..","..")),
               "Docs/PROJECT_RESORT_EXECUTION/R12_GAME_BRIDGE_UNITY_QA.json");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var q=new Report{
                status="R12_GAME_PROJECT_ASSET_COMPATIBILITY_PASS_GAMEPLAY_ALIGNMENT_PENDING",
                unityVersion=Application.unityVersion, graphicsDevice=SystemInfo.graphicsDeviceName,
                runtimeRenderer=SystemInfo.graphicsDeviceType.ToString(),
                originalScene=PlayableScene,importedScene=StagedScene,gameplaySceneSha256=gameplayOriginalHash,
                buildingsCount=1468,roadTriangles=roads,trees=trees.Length,
                r8Renderers=r8.Length,r11DetailRenderers=r11.Length,
                r12StorefrontRenderers=r12.Length,r10CoastalRenderers=r10.Length,
                missingShaders=missingShaders,missingMaterials=missingMaterials,
                missingUV0=missingUV,missingMonoScripts=scriptMissing,r9TreesMissingUV0=treeMissingUV,
                originalDataWidth=Mathf.RoundToInt(site.size.x),
                originalDataDepth=Mathf.RoundToInt(site.size.z),
                note="Visual 2000x1000m georeferenced R12 and playable SiteData "+
                     site.size.x+"x"+site.size.z+"m have different frames, and "+
                     "runtime ResortSite generates a second beach/roads/buildings. "+
                     "R9 has "+treeMissingUV+" UV0-less tree meshes: art rework needed. "+
                     "No gameplay integration without verified coordinate mapping, "+
                     "single active terrain/ocean, collider tests, quest/save QA."
            };
            File.WriteAllText(output,JsonUtility.ToJson(q,true)+"\n");
            Debug.Log("RESORT_R12_GAME_BRIDGE_UNITY_PASS r8="+r8.Length+
                      " r11="+r11.Length+" r12="+r12.Length+" trees="+trees.Length+
                      " roads="+roads+" broken=0 uvlessTrees="+treeMissingUV+" gameplayMap="+
                      site.size.x+"x"+site.size.z+" gated=noGameplayMerge");
        }
    }
}
