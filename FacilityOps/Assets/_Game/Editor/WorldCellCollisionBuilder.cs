using System;
using System.Collections.Generic;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    /// <summary>
    /// Temporary QA collider preparation for the first streamed-world slice.
    /// It adds static MeshColliders to imported Terrain/Roads/Architecture meshes.
    /// This is intentionally a validation bridge, not the final collision solution.
    /// </summary>
    public static class WorldCellCollisionBuilder
    {
        private static readonly string[] CollisionLayers =
        {
            "Terrain",
            "Roads",
            "Architecture"
        };

        [MenuItem("Facility Ops/World/Build Active Cell QA Colliders")]
        public static void BuildActiveCellQaColliders()
        {
            WorldCellRoot[] roots = UnityEngine.Object.FindObjectsByType<WorldCellRoot>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);

            if (roots.Length != 1)
                throw new InvalidOperationException(
                    "Open exactly one generated cell Scene before building QA colliders.");

            WorldCellRoot root = roots[0];
            int added = 0;
            int existing = 0;
            long colliderTriangles = 0;
            var warnings = new List<string>();

            foreach (string layerName in CollisionLayers)
            {
                Transform layer = root.transform.Find(layerName);
                if (layer == null)
                    throw new MissingReferenceException(
                        $"Cell {root.CellId} is missing layer root {layerName}.");

                MeshFilter[] filters = layer.GetComponentsInChildren<MeshFilter>(true);
                foreach (MeshFilter filter in filters)
                {
                    if (filter.sharedMesh == null)
                        continue;

                    Collider collider = filter.GetComponent<Collider>();
                    if (collider != null)
                    {
                        existing++;
                        continue;
                    }

                    var meshCollider = Undo.AddComponent<MeshCollider>(filter.gameObject);
                    meshCollider.sharedMesh = filter.sharedMesh;
                    meshCollider.convex = false;
                    filter.gameObject.isStatic = true;
                    added++;

                    long tris = 0;
                    for (int sub = 0; sub < filter.sharedMesh.subMeshCount; sub++)
                        tris += (long)filter.sharedMesh.GetIndexCount(sub) / 3L;
                    colliderTriangles += tris;

                    if (tris > 250000)
                        warnings.Add(
                            $"{layerName}/{filter.name}: QA MeshCollider is heavy ({tris:N0} tris). " +
                            "Replace with authored/simplified collider before production.");
                }
            }

            EditorSceneManager.MarkSceneDirty(root.gameObject.scene);

            foreach (string warning in warnings)
                Debug.LogWarning(warning);

            Debug.Log(
                $"WORLD CELL QA COLLIDERS: {root.CellId}, added={added}, existing={existing}, colliderTris~={colliderTriangles:N0}, warnings={warnings.Count}. " +
                "This collider pass is temporary and must be profiled/replaced before production.");
        }
    }
}
