using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps.Editor
{
    /// <summary>Non-interactive, fail-closed import of the frozen W3 export contracts.</summary>
    public static class WorldSliceImportPipeline
    {
        public const string HomeCell = "SA_M01_01_S00_02";
        private static readonly string[] Heroes = { "home.starter", "garage", "horizonte", "grocery" };
        [Serializable] private sealed class BoundsRecord { public float[] min; public float[] max; }
        [Serializable] private sealed class LayerRecord
        {
            public string layer; public string status; public string file;
            public long fileBytes; public BoundsRecord blenderBounds;
        }
        [Serializable] private sealed class CellRecord
        {
            public int schemaVersion; public string status; public string cell; public LayerRecord[] layers;
        }
        [Serializable] private sealed class HeroRecord
        {
            public int schemaVersion; public string status; public string hero; public string cell;
            public string fbx; public long fileBytes; public BoundsRecord blenderBounds;
        }
        [Serializable] private sealed class MapRecord { public string path; }
        [Serializable] private sealed class MaterialRecord { public string name; public MapRecord[] maps; }
        [Serializable] private sealed class MaterialContract
        {
            public int schemaVersion; public int materialCount; public MaterialRecord[] materials;
        }
        [Serializable] private sealed class MarkerRecord
        {
            public string name; public string facilityId; public float[] position;
            public float[] forward; public float[] up; public float[] scale;
        }
        [Serializable] private sealed class MarkerContract
        {
            public int schemaVersion; public string status; public int markerCount; public MarkerRecord[] markers;
        }
        [Serializable] private sealed class Preflight { public int schemaVersion; public string status; public string cell; }

        private static string Repository => Path.GetFullPath(Path.Combine(Application.dataPath, "../.."));
        private static string Exports => Path.Combine(Repository, "ArtSource/Blender/World/UnityExport");
        private static string CellManifest(string id) => Path.Combine(Exports, "Cells", id, "cell_export_manifest.json");
        private static string HeroManifest(string id) => Path.Combine(Exports, "Heroes", id, "hero_export_manifest.json");
        private static string MarkerPath(string id) => Path.Combine(Exports, "Markers", id + ".markers.json");

        [MenuItem("Facility Ops/World/Import Frozen W3 Pilot Corridor")]
        public static void ImportPilot()
        {
            // Preflight every artifact before creating any scene, copying a model or changing Build Settings.
            ValidateExports(WorldCellSceneScaffolder.PilotCellIds, Heroes);
            Import(WorldCellSceneScaffolder.PilotCellIds, Heroes);
            WorldCellBuildSettingsUtility.SyncCellScenes();
            WorldCellBuildSettingsUtility.ValidateCellScenesInBuildSettings();
            WorldIntegrationQa.RunPilotGate(false);
            WorldSliceBootstrapScaffolder.CreateNonInteractive();
            var build = EditorBuildSettings.scenes.ToList();
            string bootstrap = WorldSliceBootstrapScaffolder.SliceBootstrap;
            if (!build.Any(s => s.path == bootstrap)) build.Add(new EditorBuildSettingsScene(bootstrap, true));
            EditorBuildSettings.scenes = build.ToArray();
            Debug.Log("WORLD SLICE IMPORT: PASS / 15 cells, 4 heroes. Runtime traversal remains a separate gate.");
        }

        public static void ImportLar()
        {
            ValidateExports(new[] { HomeCell }, new[] { "home.starter" });
            Import(new[] { HomeCell }, new[] { "home.starter" });
            Debug.Log("WORLD SLICE LAR IMPORT: PASS / run the Lar play-mode gate before expanding.");
        }

        public static void ValidateExports(IEnumerable<string> cells, IEnumerable<string> heroes)
        {
            var material = Read<MaterialContract>(Path.Combine(Exports, "w3_materials.json"));
            Require(material.schemaVersion == 1 && material.materials != null &&
                material.materials.Length > 0 && material.materialCount == material.materials.Length,
                "Invalid W3 material contract");
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (var record in material.materials)
            {
                Require(record != null && !string.IsNullOrEmpty(record.name) && names.Add(record.name),
                    "Empty/duplicate W3 material name");
                foreach (var map in record.maps ?? Array.Empty<MapRecord>())
                    RequireFile(Inside(Repository, map.path));
            }
            foreach (string cell in cells)
            {
                var preflight = Read<Preflight>(Path.Combine(Exports, "preflight_" + cell + ".json"));
                Require(preflight.schemaVersion == 1 && preflight.status == "PASS" && preflight.cell == cell,
                    "Cell preflight did not pass: " + cell);
                var record = Read<CellRecord>(CellManifest(cell));
                Require(record.schemaVersion == 1 && record.status == "PASS" && record.cell == cell && record.layers != null,
                    "Invalid cell export: " + cell);
                var layers = new HashSet<string>(StringComparer.Ordinal);
                foreach (var layer in record.layers)
                {
                    Require(layer != null && layers.Add(layer.layer), "Duplicate/null layer: " + cell);
                    Require(new[] { "Terrain", "Roads", "Architecture", "Infrastructure", "Props", "Vegetation" }.Contains(layer.layer),
                        "Unexpected static layer: " + layer.layer);
                    Require(layer.status == "EXPORTED" || layer.status == "SKIPPED", "Failed layer: " + layer.layer);
                    if (layer.status != "EXPORTED") continue;
                    RequireArtifact(Path.GetDirectoryName(CellManifest(cell)), layer.file, layer.fileBytes);
                    ValidateBounds(layer.blenderBounds, cell + "/" + layer.layer);
                }
                foreach (string layer in new[] { "Terrain", "Roads", "Architecture" })
                    Require(record.layers.Any(l => l.layer == layer && l.status == "EXPORTED"), "Missing required layer: " + cell + "/" + layer);
            }
            foreach (string hero in heroes)
            {
                var record = Read<HeroRecord>(HeroManifest(hero));
                Require(record.schemaVersion == 1 && record.status == "PASS" && record.hero == hero &&
                    record.cell == WorldSliceDestinationRegistry.Require(hero).Cell.Name, "Invalid hero export: " + hero);
                RequireArtifact(Path.GetDirectoryName(HeroManifest(hero)), record.fbx, record.fileBytes);
                ValidateBounds(record.blenderBounds, hero);
                var markers = Read<MarkerContract>(MarkerPath(hero));
                Require(markers.schemaVersion == 1 && markers.status == "PASS" && markers.markers != null &&
                    markers.markerCount > 0 && markers.markerCount == markers.markers.Length, "Invalid markers: " + hero);
                var markerNames = new HashSet<string>(StringComparer.Ordinal);
                foreach (var marker in markers.markers)
                {
                    Require(marker != null && !string.IsNullOrEmpty(marker.name) && markerNames.Add(marker.name), "Duplicate/empty marker: " + hero);
                    Require(marker.facilityId == hero, "Marker belongs to another facility: " + marker.name);
                    ValidateVector(marker.position); ValidateVector(marker.forward); ValidateVector(marker.up); ValidateVector(marker.scale);
                    Require(Vector3.Cross(Vec(marker.forward), Vec(marker.up)).sqrMagnitude > 0.0001f, "Invalid marker basis: " + marker.name);
                }
                if (hero == "horizonte")
                    foreach (string suffix in new[] { "GP_prologue_spawn_corridor", "GP_quadro_tecnico" })
                        Require(markers.markers.Any(m => m.name.EndsWith(suffix, StringComparison.Ordinal)), "Missing critical Horizonte marker: " + suffix);
            }
        }

        private static void Import(IEnumerable<string> cells, IEnumerable<string> heroes)
        {
            var heroList = heroes.ToArray();
            WorldStreamingManifestValidator.ValidateOrThrow();
            WorldPbrMaterialBuilder.Build(Path.Combine(Exports, "w3_materials.json"));
            WorldCellSceneScaffolder.CreatePilotScaffoldsNonInteractive();
            foreach (string cell in cells)
            {
                Scene scene = EditorSceneManager.OpenScene(WorldCellSceneScaffolder.ScenePathFor(cell), OpenSceneMode.Single);
                WorldCellFbxImporter.ImportManifest(CellManifest(cell));
                var root = UnityEngine.Object.FindAnyObjectByType<WorldCellRoot>();
                foreach (string hero in heroList.Where(h => WorldSliceDestinationRegistry.Require(h).Cell.Name == cell))
                {
                    GameObject instance = WorldHeroFbxImporter.ImportManifest(HeroManifest(hero));
                    WorldGameplayMarkerImporter.ImportInto(MarkerPath(hero), root.transform.Find("Gameplay"));
                    AssertBounds(instance.transform, Read<HeroRecord>(HeroManifest(hero)).blenderBounds, hero);
                }
                var manifest = Read<CellRecord>(CellManifest(cell));
                foreach (var layer in manifest.layers.Where(l => l.status == "EXPORTED"))
                    AssertBounds(root.transform.Find(layer.layer + "/Imported_" + layer.layer), layer.blenderBounds, cell + "/" + layer.layer);
                foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
                    foreach (var material in renderer.sharedMaterials)
                        Require(material != null && material.shader != null && material.shader.name == "Universal Render Pipeline/Lit",
                            "Missing/non-URP material: " + renderer.name);
                WorldCellCollisionBuilder.BuildActiveCellQaColliders();
                WorldCellContentStamper.StampActiveCell();
                if (!EditorSceneManager.SaveScene(scene)) throw new IOException("Unable to save " + scene.path);
            }
            AssetDatabase.SaveAssets();
        }

        private static void AssertBounds(Transform imported, BoundsRecord expected, string label)
        {
            Require(imported != null, "Missing import: " + label);
            var renderers = imported.GetComponentsInChildren<Renderer>(true);
            Require(renderers.Length > 0, "Import has no renderers: " + label);
            Bounds actual = renderers[0].bounds;
            foreach (var renderer in renderers.Skip(1)) actual.Encapsulate(renderer.bounds);
            Vector3 min = new Vector3(expected.min[0], expected.min[2], expected.min[1]);
            Vector3 max = new Vector3(expected.max[0], expected.max[2], expected.max[1]);
            Require(Vector3.Distance(actual.min, min) < .25f && Vector3.Distance(actual.max, max) < .25f,
                $"Scale/axis/placement mismatch {label}: Unity {actual.min:F3}..{actual.max:F3}, Blender→Unity {min:F3}..{max:F3}");
        }
        private static void ValidateBounds(BoundsRecord record, string label)
        {
            Require(record != null, "Missing export bounds: " + label);
            ValidateVector(record.min); ValidateVector(record.max);
            for (int i = 0; i < 3; i++) Require(record.max[i] >= record.min[i], "Invalid export bounds: " + label);
        }
        private static void ValidateVector(float[] values)
        {
            Require(values != null && values.Length == 3 && values.All(v => !float.IsNaN(v) && !float.IsInfinity(v)), "Invalid transform vector");
        }
        private static Vector3 Vec(float[] v) => new Vector3(v[0], v[1], v[2]);
        private static T Read<T>(string path)
        {
            RequireFile(path);
            var record = JsonUtility.FromJson<T>(File.ReadAllText(path));
            if (record == null) throw new InvalidDataException("Null JSON: " + path);
            return record;
        }
        private static void RequireArtifact(string folder, string file, long bytes)
        {
            string path = Inside(folder, file);
            RequireFile(path);
            Require(bytes > 0 && new FileInfo(path).Length == bytes, "Artifact size mismatch: " + path);
        }
        private static string Inside(string folder, string relative)
        {
            Require(!string.IsNullOrEmpty(relative) && !Path.IsPathRooted(relative), "Expected relative artifact path");
            string root = Path.GetFullPath(folder) + Path.DirectorySeparatorChar;
            string result = Path.GetFullPath(Path.Combine(folder, relative));
            Require(result.StartsWith(root, StringComparison.OrdinalIgnoreCase), "Artifact escapes source folder");
            return result;
        }
        private static void RequireFile(string path)
        {
            if (!File.Exists(path)) throw new FileNotFoundException("Required world export is missing; import aborted.", path);
        }
        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidDataException(message);
        }
    }
}
