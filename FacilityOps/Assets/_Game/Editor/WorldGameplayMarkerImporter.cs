using System;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldGameplayMarkerImporter
    {
        [Serializable]
        private sealed class MarkerCatalog
        {
            public int schemaVersion;
            public string name;
            public string sourceBlend;
            public int markerCount;
            public string status;
            public MarkerRecord[] markers;
        }

        [Serializable]
        private sealed class MarkerRecord
        {
            public string name;
            public string type;
            public string facilityId;
            public string kind;
            public string layer;
            public string state;
            public string item;
            public string note;
            public float[] position;
            public float[] forward;
            public float[] up;
            public float[] scale;
        }

        [MenuItem("Facility Ops/World/Import Gameplay Marker Catalog...")]
        public static void ImportFromMenu()
        {
            string path = EditorUtility.OpenFilePanel(
                "Import Blender gameplay marker catalog",
                RepositoryMarkerFolder(),
                "json");

            if (string.IsNullOrEmpty(path))
                return;

            Transform parent = ResolveGameplayParent();
            if (parent == null)
            {
                EditorUtility.DisplayDialog(
                    "Facility Ops",
                    "Open a generated world cell Scene containing a WorldCellRoot and Gameplay child first.",
                    "OK");
                return;
            }

            ImportInto(path, parent);
        }

        public static int ImportInto(string path, Transform parent)
        {
            if (parent == null)
                throw new ArgumentNullException(nameof(parent));
            if (!File.Exists(path))
                throw new FileNotFoundException("Marker catalog not found.", path);

            MarkerCatalog catalog = JsonUtility.FromJson<MarkerCatalog>(File.ReadAllText(path));
            if (catalog == null || catalog.schemaVersion != 1 || catalog.markers == null)
                throw new InvalidDataException("Unsupported or malformed gameplay marker catalog: " + path);
            if (!string.Equals(catalog.status, "PASS", StringComparison.Ordinal))
                throw new InvalidDataException("Marker catalog is not PASS: " + path);
            if (catalog.markerCount != catalog.markers.Length)
                throw new InvalidDataException(
                    $"Marker count mismatch in {path}: header={catalog.markerCount}, records={catalog.markers.Length}");

            int created = 0;
            Undo.IncrementCurrentGroup();
            int undoGroup = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Import Facility Ops Gameplay Markers");

            try
            {
                foreach (MarkerRecord record in catalog.markers)
                {
                    ValidateRecord(record, path);

                    Transform existing = parent.Find(record.name);
                    GameObject go;
                    WorldGameplayMarker marker;

                    if (existing != null)
                    {
                        go = existing.gameObject;
                        marker = go.GetComponent<WorldGameplayMarker>();
                        if (marker == null)
                            marker = Undo.AddComponent<WorldGameplayMarker>(go);
                    }
                    else
                    {
                        go = new GameObject(record.name);
                        Undo.RegisterCreatedObjectUndo(go, "Create gameplay marker");
                        go.transform.SetParent(parent, false);
                        marker = Undo.AddComponent<WorldGameplayMarker>(go);
                        created++;
                    }

                    Undo.RecordObject(go.transform, "Update gameplay marker transform");
                    go.transform.position = Vec(record.position);
                    go.transform.rotation = Rotation(record.forward, record.up);
                    go.transform.localScale = Vec(record.scale);

                    Undo.RecordObject(marker, "Update gameplay marker metadata");
                    marker.Configure(
                        record.name,
                        record.facilityId,
                        record.kind,
                        record.state,
                        record.item,
                        record.note,
                        Path.GetFileName(path));

                    EditorUtility.SetDirty(marker);
                }
            }
            finally
            {
                Undo.CollapseUndoOperations(undoGroup);
            }

            EditorSceneManager.MarkSceneDirty(parent.gameObject.scene);
            Debug.Log(
                $"Gameplay markers imported: catalog={catalog.name}, records={catalog.markers.Length}, new={created}, parent={parent.name}");
            return created;
        }

        private static Transform ResolveGameplayParent()
        {
            WorldCellRoot[] roots = UnityEngine.Object.FindObjectsByType<WorldCellRoot>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);

            if (roots.Length != 1)
                return null;

            return roots[0].transform.Find("Gameplay");
        }

        private static void ValidateRecord(MarkerRecord record, string path)
        {
            if (record == null || string.IsNullOrEmpty(record.name))
                throw new InvalidDataException("Marker without name in " + path);
            if (!ValidVec(record.position) || !ValidVec(record.forward) || !ValidVec(record.up) || !ValidVec(record.scale))
                throw new InvalidDataException("Marker has invalid transform arrays: " + record.name);
        }

        private static bool ValidVec(float[] value) => value != null && value.Length == 3;

        private static Vector3 Vec(float[] value) => new Vector3(value[0], value[1], value[2]);

        private static Quaternion Rotation(float[] forward, float[] up)
        {
            Vector3 f = Vec(forward);
            Vector3 u = Vec(up);
            if (f.sqrMagnitude < 0.0001f)
                f = Vector3.forward;
            if (u.sqrMagnitude < 0.0001f)
                u = Vector3.up;
            return Quaternion.LookRotation(f.normalized, u.normalized);
        }

        private static string RepositoryMarkerFolder()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string repository = Path.GetFullPath(Path.Combine(project, ".."));
            return Path.Combine(repository, "ArtSource", "Blender", "World", "UnityExport", "Markers");
        }
    }
}
