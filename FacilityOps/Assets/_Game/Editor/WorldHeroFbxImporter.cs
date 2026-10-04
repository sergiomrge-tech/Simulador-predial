using System;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldHeroFbxImporter
    {
        [Serializable]
        private sealed class HeroExportManifest
        {
            public int schemaVersion;
            public string status;
            public string hero;
            public string sourceBlend;
            public string rootObject;
            public string cell;
            public string[] unityWorldPosition;
            public string fbx;
            public long fileBytes;
            public int exportedObjects;
            public string gameplayMarkers;
            public string error;
        }

        private const string HeroAssetRoot =
            "Assets/_Game/World/SantaAurora/OldTown/Heroes";

        [MenuItem("Facility Ops/World/Import Hero FBX Into Active Cell...")]
        public static void ImportFromMenu()
        {
            string repo = Path.GetFullPath(
                Path.Combine(Application.dataPath, "..", ".."));
            string initial = Path.Combine(
                repo,
                "ArtSource",
                "Blender",
                "World",
                "UnityExport",
                "Heroes");

            string manifestPath = EditorUtility.OpenFilePanel(
                "Select hero_export_manifest.json",
                initial,
                "json");

            if (string.IsNullOrEmpty(manifestPath))
                return;

            ImportManifest(manifestPath);
        }

        public static GameObject ImportManifest(string manifestPath)
        {
            if (!File.Exists(manifestPath))
                throw new FileNotFoundException(
                    "Hero export manifest not found.",
                    manifestPath);

            HeroExportManifest manifest =
                JsonUtility.FromJson<HeroExportManifest>(
                    File.ReadAllText(manifestPath));

            if (manifest == null || manifest.schemaVersion != 1)
                throw new InvalidDataException(
                    "Unsupported hero export manifest.");

            if (!string.Equals(
                    manifest.status,
                    "PASS",
                    StringComparison.Ordinal))
                throw new InvalidDataException(
                    "Hero export manifest is not PASS: " +
                    manifestPath);

            if (string.IsNullOrEmpty(manifest.hero) ||
                string.IsNullOrEmpty(manifest.cell) ||
                string.IsNullOrEmpty(manifest.fbx))
                throw new InvalidDataException(
                    "Hero export manifest is incomplete.");

            if (!WorldStreamingId.TryParse(
                    manifest.cell,
                    out _))
                throw new InvalidDataException(
                    "Hero manifest contains invalid cell id: " +
                    manifest.cell);

            WorldCellRoot[] roots =
                UnityEngine.Object.FindObjectsByType<WorldCellRoot>(
                    FindObjectsInactive.Include,
                    FindObjectsSortMode.None);

            if (roots.Length != 1)
                throw new InvalidOperationException(
                    "Open exactly one generated cell Scene before importing a hero.");

            WorldCellRoot root = roots[0];
            if (!string.Equals(
                    root.CellId,
                    manifest.cell,
                    StringComparison.Ordinal))
                throw new InvalidOperationException(
                    $"Open Scene is {root.CellId}, but hero {manifest.hero} belongs to {manifest.cell}.");

            Transform architecture =
                root.transform.Find("Architecture");
            if (architecture == null)
                throw new MissingReferenceException(
                    "Cell Scene is missing Architecture layer.");

            string sourceFolder =
                Path.GetDirectoryName(manifestPath);
            string sourceFbx =
                Path.Combine(sourceFolder, manifest.fbx);

            if (!File.Exists(sourceFbx))
                throw new FileNotFoundException(
                    "Hero FBX is missing.",
                    sourceFbx);

            string heroFolder =
                HeroAssetRoot +
                "/" +
                SafeFile(manifest.hero);
            EnsureAssetFolder(heroFolder);

            string assetPath =
                heroFolder +
                "/" +
                Path.GetFileName(sourceFbx);

            string destination =
                Path.GetFullPath(
                    Path.Combine(
                        Application.dataPath,
                        "..",
                        assetPath));

            Directory.CreateDirectory(
                Path.GetDirectoryName(destination));
            File.Copy(sourceFbx, destination, true);

            AssetDatabase.ImportAsset(
                assetPath,
                ImportAssetOptions.ForceSynchronousImport |
                ImportAssetOptions.ForceUpdate);

            ModelImporter importer =
                AssetImporter.GetAtPath(assetPath)
                as ModelImporter;

            if (importer != null)
            {
                importer.materialImportMode =
                    ModelImporterMaterialImportMode.ImportStandard;
                importer.SearchAndRemapMaterials(
                    ModelImporterMaterialName.BasedOnMaterialName,
                    ModelImporterMaterialSearch.Everywhere);
                importer.SaveAndReimport();
            }

            GameObject model =
                AssetDatabase.LoadAssetAtPath<GameObject>(
                    assetPath);

            if (model == null)
                throw new InvalidDataException(
                    "Unity did not import a GameObject from " +
                    assetPath);

            string instanceName =
                "Hero_" + manifest.hero;

            Transform existing =
                architecture.Find(instanceName);
            if (existing != null)
                Undo.DestroyObjectImmediate(
                    existing.gameObject);

            GameObject instance =
                (GameObject)PrefabUtility.InstantiatePrefab(
                    model,
                    root.gameObject.scene);

            if (instance == null)
                throw new InvalidOperationException(
                    "Could not instantiate hero FBX.");

            Undo.RegisterCreatedObjectUndo(
                instance,
                "Import Facility Ops hero");

            instance.name = instanceName;
            instance.transform.SetParent(
                architecture,
                true);

            var tag =
                instance.GetComponent<WorldHeroInstance>();
            if (tag == null)
                tag = Undo.AddComponent<WorldHeroInstance>(
                    instance);

            tag.Configure(
                manifest.hero,
                manifest.cell,
                Path.GetFileName(manifestPath),
                manifest.sourceBlend);

            EditorUtility.SetDirty(tag);
            EditorSceneManager.MarkSceneDirty(
                root.gameObject.scene);

            Debug.Log(
                $"WORLD HERO IMPORTED: {manifest.hero} -> {manifest.cell}, objects={manifest.exportedObjects}");

            return instance;
        }

        private static string SafeFile(string value)
        {
            foreach (char invalid in Path.GetInvalidFileNameChars())
                value = value.Replace(invalid, '_');

            return value.Replace('.', '_')
                .Replace('/', '_')
                .Replace('\\', '_');
        }

        private static void EnsureAssetFolder(string path)
        {
            string[] parts = path.Split('/');
            string current = parts[0];

            for (int i = 1; i < parts.Length; i++)
            {
                string next =
                    current +
                    "/" +
                    parts[i];

                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(
                        current,
                        parts[i]);

                current = next;
            }
        }
    }
}
