using System;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldCellContentStamper
    {
        [MenuItem("Facility Ops/World/Stamp Active Cell Imported Content")]
        public static void StampActiveCell()
        {
            WorldCellRoot[] roots = UnityEngine.Object.FindObjectsByType<WorldCellRoot>(
                FindObjectsInactive.Include);

            if (roots.Length != 1)
                throw new InvalidOperationException(
                    "Active Scene must contain exactly one WorldCellRoot.");

            WorldCellRoot root = roots[0];
            if (!root.TryGetStreamingId(out _))
                throw new InvalidOperationException("WorldCellRoot has invalid cell id.");

            Transform terrain = root.transform.Find("Terrain");
            Transform roads = root.transform.Find("Roads");
            Transform architecture = root.transform.Find("Architecture");
            Transform gameplay = root.transform.Find("Gameplay");

            bool hasTerrain = HasImportedContent(terrain);
            bool hasRoads = HasImportedContent(roads);
            bool hasArchitecture = HasImportedContent(architecture);

            if (!hasTerrain || !hasRoads || !hasArchitecture)
                throw new InvalidOperationException(
                    "Cannot stamp an empty/incomplete cell. Terrain, Roads and Architecture must contain imported content.");

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            Collider[] colliders = root.GetComponentsInChildren<Collider>(true);
            WorldGameplayMarker[] markers = gameplay == null
                ? Array.Empty<WorldGameplayMarker>()
                : gameplay.GetComponentsInChildren<WorldGameplayMarker>(true);

            long triangles = EstimateTriangles(root);

            WorldCellContentStamp stamp = root.GetComponent<WorldCellContentStamp>();
            if (stamp == null)
                stamp = Undo.AddComponent<WorldCellContentStamp>(root.gameObject);

            Undo.RecordObject(stamp, "Stamp imported world cell content");
            stamp.Configure(
                root.CellId,
                Environment.GetEnvironmentVariable("FACILITY_SOURCE_REVISION") ?? "local",
                "ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend",
                CountImportedObjects(root),
                renderers.Length,
                colliders.Length,
                markers.Length,
                triangles,
                hasTerrain,
                hasRoads,
                hasArchitecture,
                true);

            EditorUtility.SetDirty(stamp);
            EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
            Debug.Log(
                $"WORLD CELL CONTENT STAMPED: {root.CellId} objects={stamp.ImportedObjectCount} renderers={renderers.Length} colliders={colliders.Length} markers={markers.Length} tris~={triangles}");
        }

        private static bool HasImportedContent(Transform layer)
        {
            return layer != null && layer.childCount > 0;
        }

        private static int CountImportedObjects(WorldCellRoot root)
        {
            int count = 0;
            foreach (Transform child in root.GetComponentsInChildren<Transform>(true))
            {
                if (child == root.transform)
                    continue;
                if (child.parent == root.transform &&
                    IsLayerRoot(child.name))
                    continue;
                count++;
            }
            return count;
        }

        private static bool IsLayerRoot(string name)
        {
            switch (name)
            {
                case "Terrain":
                case "Roads":
                case "Architecture":
                case "Infrastructure":
                case "Props":
                case "Vegetation":
                case "Lighting":
                case "Gameplay":
                    return true;
                default:
                    return false;
            }
        }

        private static long EstimateTriangles(WorldCellRoot root)
        {
            long total = 0;
            MeshFilter[] filters = root.GetComponentsInChildren<MeshFilter>(true);
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                if (mesh == null)
                    continue;
                for (int sub = 0; sub < mesh.subMeshCount; sub++)
                    total += (long)mesh.GetIndexCount(sub) / 3L;
            }
            return total;
        }
    }
}
