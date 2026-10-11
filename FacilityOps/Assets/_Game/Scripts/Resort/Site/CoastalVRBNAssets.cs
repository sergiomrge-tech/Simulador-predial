using System.Collections.Generic;
using UnityEngine;
using Object = UnityEngine.Object;

namespace ResortAurora.Site
{
    /// <summary>Licensed vrbn visuals on compatible existing lots; original gameplay collision stays authoritative.</summary>
    public static class CoastalVRBNAssets
    {
        static readonly string[] Models = { "B00004", "B00274", "B00275", "B00276" };
        const string ResourceRoot = "Art/Resort/Urban/VRBN/";
        const float MinimumUniformScale = .85f;
        static GameObject prefab;
        static Bounds bounds;
        static bool measured;
        static readonly Dictionary<string, GameObject> prefabs = new Dictionary<string, GameObject>();
        static readonly Dictionary<string, Bounds> measuredBounds = new Dictionary<string, Bounds>();

        static bool TrySelect(LotData lot, out float scale)
        {
            scale = 1;
            string resource = ResourceRoot + Models[Mathf.Abs(lot.c) % Models.Length];
            if (!prefabs.TryGetValue(resource, out prefab)) prefabs[resource] = prefab = Resources.Load<GameObject>(resource);
            measured = measuredBounds.TryGetValue(resource, out bounds);
            if (prefab == null) return false;
            if (!measured)
            {
                var lod = prefab.GetComponentInChildren<LODGroup>(true);
                if (lod == null || lod.GetLODs().Length == 0) return false;
                bool first = true;
                foreach (var renderer in lod.GetLODs()[0].renderers)
                {
                    if (renderer == null) return false;
                    var filter = renderer.GetComponent<MeshFilter>();
                    if (filter == null || filter.sharedMesh == null) return false;
                    foreach (var material in renderer.sharedMaterials)
                        if (material == null || material.shader == null || !material.shader.isSupported) return false;
                    var b = filter.sharedMesh.bounds;
                    var matrix = prefab.transform.worldToLocalMatrix * filter.transform.localToWorldMatrix;
                    for (int corner = 0; corner < 8; corner++)
                    {
                        var p = matrix.MultiplyPoint3x4(b.center + Vector3.Scale(b.extents,
                            new Vector3((corner & 1) == 0 ? -1 : 1, (corner & 2) == 0 ? -1 : 1, (corner & 4) == 0 ? -1 : 1)));
                        if (first) { bounds = new Bounds(p, Vector3.zero); first = false; } else bounds.Encapsulate(p);
                    }
                }
                if (first || bounds.size.x <= 0 || bounds.size.z <= 0) return false;
                measured = true;
                measuredBounds[resource] = bounds;
            }
            // Restrict to generous residential lots. No horizontal/vertical independent deformation.
            scale = Mathf.Min(1, (lot.w - .10f) / bounds.size.x, (lot.d - .10f) / bounds.size.z);
            return lot.h >= 7f && scale >= MinimumUniformScale && bounds.max.y * scale <= lot.h + .25f;
        }

        public static bool IsCompatible(LotData lot) => TrySelect(lot, out _);

        public static bool TryDescribe(ResortSite site, LotData lot, out CoastalUrbanAssets.LotFrame frame)
        {
            frame = default;
            if (!TrySelect(lot, out float scale)) return false;
            frame.rotation = Quaternion.Euler(0, lot.rot, 0);
            frame.width = bounds.size.x * scale; frame.depth = bounds.size.z * scale;
            // vrbn ground datum is y=0; the authored basement reaches below it.
            frame.height = bounds.max.y * scale;
            frame.front = frame.depth / 2; frame.back = -frame.depth / 2; frame.wallX = frame.width / 2;
            frame.floor = float.MinValue;
            for (int x = -1; x <= 1; x++) for (int z = -1; z <= 1; z++)
            {
                var offset = frame.rotation * new Vector3(x * frame.width / 2, 0, z * frame.depth / 2);
                frame.floor = Mathf.Max(frame.floor, site.HeightAt(lot.x + offset.x, lot.z + offset.z) + .085f);
            }
            frame.pitchedRoof = true;
            return true;
        }

        public static bool TryPlace(Transform parent, ResortSite site, LotData lot, int index)
        {
            if (!TryDescribe(site, lot, out var frame) || !TrySelect(lot, out float scale)) return false;
            var root = new GameObject("VRBN_Lot_" + index).transform;
            root.SetParent(parent, false);
            var instance = Object.Instantiate(prefab, root, false);
            instance.name = prefab.name;
            instance.transform.localRotation = frame.rotation;
            instance.transform.localScale = Vector3.one * scale;
            var offset = frame.rotation * new Vector3(bounds.center.x * scale, 0, bounds.center.z * scale);
            instance.transform.localPosition = new Vector3(lot.x, frame.floor, lot.z) - offset;
            // Disable vendor animation/dirt controllers before Start; preserve original shared PBR materials and LODs.
            foreach (var behaviour in instance.GetComponentsInChildren<MonoBehaviour>(true)) behaviour.enabled = false;
            foreach (var collider in instance.GetComponentsInChildren<Collider>(true)) collider.enabled = false;
            foreach (var body in instance.GetComponentsInChildren<Rigidbody>(true)) { body.isKinematic = true; body.detectCollisions = false; }
            Debug.Log($"VRBN_APPLIED lot={index} model={prefab.name} scale={scale:F4} footprint={frame.width:F3}x{frame.depth:F3} ground={frame.floor:F3} originalCollision=retained");
            return true;
        }
    }
}
