using System;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using ResortAurora.Site;

namespace ResortAurora.EditorTools
{
    /// <summary>Native Unity QA for imported R12 anchor inventory. No gameplay scene mutation.</summary>
    public static class ResortR12GameplayAnchorAudit
    {
        const string SitePath = "Assets/_Game/Resources/Resort/ResortSite.json";
        const string InventoryPath = "Assets/_Game/Resources/Resort/R12GameplayAnchorInventory.json";
        const string PlayablePath = "Assets/_Game/Scenes/ResortPrologue.unity";
        const string R12VisualPath = "Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity";
        [Serializable] public sealed class Report
        {
            public string status, unity, reason, originalGameplaySceneSha256;
            public int anchorCount, verifiedTargetCount, originalParcels;
            public bool legacyGameplayPreserved, migrationEnabled, sourceVisualSceneFound;
        }

        static void Need(bool condition, string reason)
        {
            if (!condition) throw new InvalidOperationException("R12_ANCHOR_NATIVE_BLOCKED:" + reason);
        }

        public static void Run()
        {
            Need(File.Exists(SitePath), "LEGACY_GAMEPLAY_SITE_FILE_MISSING");
            Need(File.Exists(InventoryPath), "ANCHOR_FILE_MISSING");
            Need(File.Exists(PlayablePath), "PLAYABLE_SCENE_MISSING");
            Need(File.Exists(R12VisualPath), "VISUAL_R12_SCENE_MISSING");
            var before=R12GameplayWorldGate.Sha256(File.ReadAllBytes(PlayablePath));
            var siteText=File.ReadAllText(SitePath, Encoding.UTF8);
            var json=File.ReadAllText(InventoryPath, Encoding.UTF8);
            var data=JsonUtility.FromJson<SiteData>(siteText);
            var inv=JsonUtility.FromJson<R12GameplayWorldGate.Inventory>(json);
            Need(data != null && data.parcels != null && data.parcels.Length == 8 &&
                 Mathf.Abs(data.size.x - 900f)<.001f &&
                 Mathf.Abs(data.size.z - 720f)<.001f,
                 "LEGACY_SITE_OR_PARCELS_INCOMPATIBLE");
            Need(inv != null && inv.anchors != null && inv.anchors.Length == 10,
                 "ANCHOR_INVENTORY_NOT_TEN");
            Need(AssetDatabase.LoadAssetAtPath<TextAsset>(InventoryPath) != null,
                 "UNITY_TEXT_ASSET_IMPORT_FAILED");
            // Unity's JsonUtility can deserialize a JSON null class field as a default
            // value-type-like instance. The authoritative provenance remains the
            // checked-in JSON and explicit GEOGRAPHIC_PLACEMENT_UNVERIFIED flags.
            Need(inv.anchors.All(a => a != null &&
                 a.status == "GEOGRAPHIC_PLACEMENT_UNVERIFIED") &&
                 !inv.approved && !inv.migration_enabled &&
                 json.Contains("\"target\": null"),
                 "UNVERIFIED_TARGET_COORDINATES_WERE_ASSIGNED");
            Need(inv.anchors.Any(a => a.id=="HOME_DOOR") &&
                 inv.anchors.Any(a => a.id=="STALL_PROMENADE") &&
                 inv.anchors.Count(a => a.id.StartsWith("PARCEL_"))==8,
                 "ANCHOR_SEMANTIC_IDS_WRONG");
            string reason;
            bool activates=R12GameplayWorldGate.CanActivate(json,siteText,out reason);
            Need(!activates && reason=="MAP_NOT_APPROVED_FOR_PLAYABLE_MIGRATION",
                 "R12_GAMEPLAY_GATE_NOT_CLOSED:"+reason);
            Need(before == R12GameplayWorldGate.Sha256(File.ReadAllBytes(PlayablePath)),
                 "LEGACY_GAMEPLAY_SCENE_CHANGED_DURING_AUDIT");
            var q=new Report {
                status="R12_ANCHORS_UNITY_NATIVE_PASS_MIGRATION_BLOCKED",
                unity=Application.unityVersion,
                reason=reason,
                originalGameplaySceneSha256=before,
                anchorCount=inv.anchors.Length,verifiedTargetCount=0,
                originalParcels=data.parcels.Length,
                legacyGameplayPreserved=true,migrationEnabled=false,
                sourceVisualSceneFound=true
            };
            var projectRoot=Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var report=Path.GetFullPath(Path.Combine(projectRoot,"../Docs/PROJECT_RESORT_EXECUTION/R12_GAMEPLAY_ANCHOR_NATIVE_QA.json"));
            Directory.CreateDirectory(Path.GetDirectoryName(report));
            File.WriteAllText(report,JsonUtility.ToJson(q,true)+"\n",Encoding.UTF8);
            Debug.Log("R12_GAMEPLAY_ANCHORS_NATIVE_PASS anchors=10 target=0 originalSceneSha="+before+" migration=BLOCKED");
        }
    }
}
