using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace ResortAurora.Site
{
    /// <summary>
    /// Fail-closed gate for future R12 gameplay migration.
    /// Does not alter ResortSite.Build(), existing saves, player or terrain.
    /// A geometric anchor inventory is NOT proof that the new scene is playable.
    /// </summary>
    public static class R12GameplayWorldGate
    {
        [Serializable] public sealed class Position { public float x, z; }
        [Serializable] public sealed class Anchor
        {
            public string id, status, role;
            public Position legacy, target;
        }
        [Serializable] public sealed class Inventory
        {
            public int schemaVersion;
            public string status, source_site_sha256, source_frame_sha256;
            public string transform_policy, target_scene;
            public bool approved, migration_enabled;
            public Position legacy_size_m;
            public Anchor[] anchors;
        }

        public static string Sha256(byte[] data)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(data)).Replace("-", "").ToLowerInvariant();
        }

        static bool Finite(float v) => !float.IsNaN(v) && !float.IsInfinity(v);

        /// <summary>Only a verified future plan may enable gameplay on the OSM map.</summary>
        public static bool CanActivate(string json, string originalSiteJson, out string why)
        {
            why = "BLOCKED";
            if (string.IsNullOrWhiteSpace(json) || string.IsNullOrWhiteSpace(originalSiteJson))
            {
                why = "MISSING_INVENTORY_OR_SITE";
                return false;
            }

            Inventory plan;
            try { plan = JsonUtility.FromJson<Inventory>(json); }
            catch (Exception e) { why = "INVALID_JSON_" + e.GetType().Name; return false; }
            if (plan == null || plan.schemaVersion != 1)
            {
                why = "INVALID_ANCHOR_SCHEMA";
                return false;
            }
            if (!string.Equals(plan.source_site_sha256,
                    Sha256(Encoding.UTF8.GetBytes(originalSiteJson)), StringComparison.OrdinalIgnoreCase))
            {
                why = "LEGACY_SITE_HASH_CHANGED";
                return false;
            }
            if (plan.legacy_size_m == null ||
                Mathf.Abs(plan.legacy_size_m.x - 900f) > .001f ||
                Mathf.Abs(plan.legacy_size_m.z - 720f) > .001f)
            {
                why = "LEGACY_MAP_SIZE_CHANGED";
                return false;
            }
            if (plan.transform_policy != "ONE_TO_ONE_METRES_RIGID_ROTATION_TRANSLATION_ONLY_NO_RESIZE")
            {
                why = "NO_RIGID_WORLD_MAPPING";
                return false;
            }
            if (!plan.approved || !plan.migration_enabled ||
                plan.status != "NATIVE_GAMEPLAY_QA_APPROVED")
            {
                why = "MAP_NOT_APPROVED_FOR_PLAYABLE_MIGRATION";
                return false;
            }
            if (plan.anchors == null || plan.anchors.Length != 10)
            {
                why = "REQUIRED_GAMEPLAY_ANCHORS_MISSING";
                return false;
            }
            var names = new HashSet<string>();
            foreach (var a in plan.anchors)
            {
                if (a == null || string.IsNullOrEmpty(a.id) ||
                    !names.Add(a.id) || a.legacy == null || a.target == null ||
                    !Finite(a.legacy.x) || !Finite(a.legacy.z) ||
                    !Finite(a.target.x) || !Finite(a.target.z) ||
                    a.status != "NATIVE_COLLISION_NAVIGATION_QA_APPROVED")
                {
                    why = "UNVERIFIED_GEOGRAPHIC_ANCHOR";
                    return false;
                }
            }
            // Never launch R12 automatically: this checks only anchor bookkeeping.
            // Integration also needs physics, pathfinding, gameplay and save gates.
            why = "ANCHOR_BOOKKEEPING_VALID_RUNTIME_INTEGRATION_NOT_IMPLEMENTED";
            return false;
        }
    }
}
