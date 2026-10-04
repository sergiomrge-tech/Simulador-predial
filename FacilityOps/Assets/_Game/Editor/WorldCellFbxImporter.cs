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
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);

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

                string sourceFbx = Path.Combine(sourceFolder, layer.file);
                if (!File.Exists(sourceFbx))
                    throw new FileNotFoundException(
                        $"Staging FBX for {layer.layer} is missing.",
                        sourceFbx);

                string assetPath = cellAssetFolder + "/" + layer.file;
                string destination = Path.GetFullPath(
                    Path.Combine(Application.dataPath, "..", assetPath));

                Directory.CreateDirectory(Path.GetDirectoryName(destination));
                File.Copy(sourceFbx, destination, true);
                AssetDatabase.ImportAsset(
                    assetPath,
                    ImportAssetOptions.ForceSynchronousImport |
                    ImportAssetOptions.ForceUpdate);

                GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
                if (model == null)
                    throw new InvalidDataException(
                        "Unity did not import a GameObject from " + assetPath);

                string instanceName = "Imported_" + layer.layer;
                Transform existing = layerRoot.Find(instanceName);
                if (existing != null)
                    Undo.DestroyObjectImmediate(existing.gameObject);

                GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(
                    model,
                    root.gameObject.scene);
                if (instance == null)
                    throw new InvalidOperationException(
                        "Could not instantiate imported FBX: " + assetPath);

                Undo.RegisterCreatedObjectUndo(instance, "Import world cell FBX");
                instance.name = instanceName;
                instance.transform.SetParent(layerRoot, true);
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
