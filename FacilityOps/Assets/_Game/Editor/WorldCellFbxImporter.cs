using System;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldCellFbxImporter
    {
        [Serializable]
        private sealed class ExportManifest
        {
            public int schemaVersion;
            public string status;
            public string cell;
            public string sourceBlend;
            public LayerExport[] layers;
        }

        [Serializable]
        private sealed class LayerExport
        {
            public string layer;
            public string status;
            public string file;
            public long fileBytes;
            public string lodFile;
            public int sourceObjects;
            public int exportedObjects;
            public string error;
        }

        private const string ImportedRoot = "Assets/_Game/World/SantaAurora/OldTown/Imported";

        [MenuItem("Facility Ops/World/Import Active Cell FBX Staging...")]
        public static void ImportFromMenu()
        {
            string repository = Path.GetFullPath(
                Path.Combine(Application.dataPath, "..", ".."));
            string initial = Path.Combine(
                repository,
                "ArtSource",
                "Blender",
                "World",
                "UnityExport",
                "Cells");

            string manifestPath = EditorUtility.OpenFilePanel(
                "Select cell_export_manifest.json",
                initial,
                "json");

            if (string.IsNullOrEmpty(manifestPath))
                return;

            ImportManifest(manifestPath);
        }

        public static void ImportManifest(string manifestPath)
        {
            if (!File.Exists(manifestPath))
                throw new FileNotFoundException("Cell export manifest not found.", manifestPath);

            ExportManifest manifest = JsonUtility.FromJson<ExportManifest>(
                File.ReadAllText(manifestPath));

            if (manifest == null || manifest.schemaVersion != 1)
                throw new InvalidDataException("Unsupported cell export manifest: " + manifestPath);
            if (!string.Equals(manifest.status, "PASS", StringComparison.Ordinal))
                throw new InvalidDataException("Cell export manifest is not PASS: " + manifestPath);
            if (!WorldStreamingId.TryParse(manifest.cell, out _))
                throw new InvalidDataException("Invalid cell id in export manifest: " + manifest.cell);

            WorldCellRoot[] roots = UnityEngine.Object.FindObjectsByType<WorldCellRoot>(
                FindObjectsInactive.Include);

            if (roots.Length != 1)
                throw new InvalidOperationException(
                    "Open exactly one generated cell Scene before importing FBX staging.");

            WorldCellRoot root = roots[0];
            if (!string.Equals(root.CellId, manifest.cell, StringComparison.Ordinal))
                throw new InvalidOperationException(
                    $"Open Scene is {root.CellId}, export manifest is {manifest.cell}.");

            string sourceFolder = Path.GetDirectoryName(manifestPath);
            if (string.IsNullOrEmpty(sourceFolder))
                throw new InvalidDataException("Cannot resolve FBX staging folder.");

            EnsureAssetFolder(ImportedRoot);
            string cellAssetFolder = ImportedRoot + "/" + manifest.cell;
            EnsureAssetFolder(cellAssetFolder);

            int importedLayers = 0;
            foreach (LayerExport layer in manifest.layers ?? Array.Empty<LayerExport>())
            {
                if (!string.Equals(layer.status, "EXPORTED", StringComparison.Ordinal) ||
                    string.IsNullOrEmpty(layer.file))
                    continue;

                Transform layerRoot = root.transform.Find(layer.layer);
                if (layerRoot == null)
                    throw new InvalidOperationException(
                        $"Cell Scene is missing layer root {layer.layer}.");

                ImportOne(sourceFolder, cellAssetFolder, layer.file, layerRoot, root.gameObject.scene, "Imported_" + layer.layer);
                if (!string.IsNullOrEmpty(layer.lodFile))
                    StampVehicles(ImportOne(sourceFolder, cellAssetFolder, layer.lodFile, layerRoot, root.gameObject.scene, "Imported_Vehicles"));
                importedLayers++;
            }

            if (importedLayers < 3)
                throw new InvalidOperationException(
                    $"Only {importedLayers} layers imported. Terrain, Roads and Architecture are required.");

            EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
            AssetDatabase.SaveAssets();

            Debug.Log(
                $"WORLD CELL FBX IMPORT COMPLETE: {manifest.cell}, layers={importedLayers}. " +
                "Run collider preparation, marker import and content stamp before QA.");
        }

        private static GameObject ImportOne(string sourceFolder, string cellAssetFolder, string file, Transform layerRoot, UnityEngine.SceneManagement.Scene scene, string instanceName)
        {
            string sourceFbx = Path.Combine(sourceFolder, file);
            if (!File.Exists(sourceFbx))
                throw new FileNotFoundException("Staging FBX is missing.", sourceFbx);

            string assetPath = cellAssetFolder + "/" + file;
            string destination = Path.GetFullPath(Path.Combine(Application.dataPath, "..", assetPath));
            Directory.CreateDirectory(Path.GetDirectoryName(destination));
            File.Copy(sourceFbx, destination, true);
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);

            ModelImporter modelImporter = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (modelImporter != null)
            {
                modelImporter.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                modelImporter.SearchAndRemapMaterials(ModelImporterMaterialName.BasedOnMaterialName, ModelImporterMaterialSearch.Everywhere);
                modelImporter.SaveAndReimport();
            }

            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
            if (model == null)
                throw new InvalidDataException("Unity did not import a GameObject from " + assetPath);

            Transform existing = layerRoot.Find(instanceName);
            if (existing != null)
                Undo.DestroyObjectImmediate(existing.gameObject);

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
            if (instance == null)
                throw new InvalidOperationException("Could not instantiate imported FBX: " + assetPath);

            Undo.RegisterCreatedObjectUndo(instance, "Import world cell FBX");
            instance.name = instanceName;
            instance.transform.SetParent(layerRoot, true);
            // Blender's right-handed -Z/Y FBX arrives with X/Z reversed in Unity 6000.6.2f1.
            // Apply the measured world-origin correction; the pipeline checks source bounds independently after import.
            var axisCorrection = Quaternion.Euler(0f, 180f, 0f);
            instance.transform.position = axisCorrection * instance.transform.position;
            instance.transform.rotation = axisCorrection * instance.transform.rotation;
            return instance;
        }

        // Vehicles arrive as LOD0/LOD1/proxy children under one node (Unity builds the LODGroup); fix the thresholds and give each car a cheap box collider.
        private static readonly float[] VehicleLodHeights = { .06f, .02f, .006f };
        private static void StampVehicles(GameObject cars)
        {
            foreach (var group in cars.GetComponentsInChildren<LODGroup>(true))
            {
                LOD[] lods = group.GetLODs();
                var fitted = new LOD[lods.Length];
                for (int i = 0; i < lods.Length; i++)
                {
                    fitted[i] = lods[i];
                    fitted[i].screenRelativeTransitionHeight = i < VehicleLodHeights.Length ? VehicleLodHeights[i] : VehicleLodHeights[VehicleLodHeights.Length - 1] / 2f;
                }
                group.SetLODs(fitted);
                group.RecalculateBounds();
                if (group.GetComponent<Collider>() == null)
                {
                    // Box in the car's own space from the LOD0 mesh bounds (world-aligned renderer bounds would inflate a turned car).
                    Renderer lod0 = group.GetLODs()[0].renderers.Length > 0 ? group.GetLODs()[0].renderers[0] : null;
                    var filter = lod0 != null ? lod0.GetComponent<MeshFilter>() : null;
                    if (filter == null || filter.sharedMesh == null) continue;
                    Bounds mb = filter.sharedMesh.bounds;
                    Matrix4x4 toGroup = group.transform.worldToLocalMatrix * filter.transform.localToWorldMatrix;
                    Bounds local = new Bounds(toGroup.MultiplyPoint3x4(mb.center), Vector3.zero);
                    for (int c = 0; c < 8; c++)
                    {
                        Vector3 corner = mb.center + Vector3.Scale(mb.extents, new Vector3((c & 1) == 0 ? -1 : 1, (c & 2) == 0 ? -1 : 1, (c & 4) == 0 ? -1 : 1));
                        local.Encapsulate(toGroup.MultiplyPoint3x4(corner));
                    }
                    var box = Undo.AddComponent<BoxCollider>(group.gameObject);
                    box.center = local.center; box.size = local.size;
                }
            }
        }

        private static void EnsureAssetFolder(string path)
        {
            string[] parts = path.Split('/');
            string current = parts[0];

            for (int i = 1; i < parts.Length; i++)
            {
                string next = current + "/" + parts[i];
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, parts[i]);
                current = next;
            }
        }
    }
}
