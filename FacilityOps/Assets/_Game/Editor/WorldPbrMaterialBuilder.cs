using System;
using System.Collections.Generic;
using System.IO;
using FacilityOps;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace FacilityOps.Editor
{
    public static class WorldPbrMaterialBuilder
    {
        [Serializable]
        private sealed class Contract
        {
            public int schemaVersion;
            public string stage;
            public string sourceBlend;
            public int materialCount;
            public MaterialRecord[] materials;
        }

        [Serializable]
        private sealed class MaterialRecord
        {
            public string name;
            public string baseName;
            public string family;
            public string textureSet;
            public string textureMode;
            public float tileMeters = 1f;
            public float[] tint;
            public float[] diffuseColor;
            public float metallic;
            public float roughness = .5f;
            public float alpha = 1f;
            public float ior = 1.5f;
            public bool isGlass;
            public MapRecord[] maps;
            public string normalConvention;
            public string status;
        }

        [Serializable]
        private sealed class MapRecord
        {
            public string channel;
            public string path;
        }

        private const string TextureAssetRoot =
            "Assets/_Game/World/SantaAurora/Shared/Textures/W3";
        private const string MaterialAssetRoot =
            "Assets/_Game/World/SantaAurora/Shared/Materials/W3";

        [MenuItem("Facility Ops/World/Build W3 URP Materials...")]
        public static void BuildFromMenu()
        {
            string repo = RepositoryRoot();
            string defaultFolder = Path.Combine(
                repo,
                "ArtSource",
                "Blender",
                "World",
                "UnityExport");

            string contractPath = EditorUtility.OpenFilePanel(
                "Select w3_materials.json",
                defaultFolder,
                "json");

            if (string.IsNullOrEmpty(contractPath))
                return;

            Build(contractPath);
        }

        public static void Build(string contractPath)
        {
            if (!File.Exists(contractPath))
                throw new FileNotFoundException(
                    "W3 material contract not found.",
                    contractPath);

            Contract contract = JsonUtility.FromJson<Contract>(
                File.ReadAllText(contractPath));

            if (contract == null ||
                contract.schemaVersion != 1 ||
                contract.materials == null)
                throw new InvalidDataException(
                    "Unsupported or malformed W3 material contract: " +
                    contractPath);

            EnsureAssetFolder(TextureAssetRoot);
            EnsureAssetFolder(MaterialAssetRoot);

            var copied = new Dictionary<string, string>(
                StringComparer.OrdinalIgnoreCase);
            var packedBySet = new Dictionary<string, string>(
                StringComparer.Ordinal);

            int created = 0;
            int updated = 0;
            foreach (MaterialRecord record in contract.materials)
            {
                if (string.IsNullOrEmpty(record.name))
                    continue;

                var channels = new Dictionary<string, string>(
                    StringComparer.OrdinalIgnoreCase);

                foreach (MapRecord map in record.maps ?? Array.Empty<MapRecord>())
                {
                    if (map == null ||
                        string.IsNullOrEmpty(map.channel) ||
                        string.IsNullOrEmpty(map.path))
                        continue;

                    string assetPath = SyncTexture(
                        map.path,
                        record.textureSet,
                        map.channel,
                        copied);

                    channels[map.channel] = assetPath;
                }

                string metallicSmoothness = null;
                if (!record.isGlass &&
                    (channels.ContainsKey("Roughness") ||
                     channels.ContainsKey("Metallic")))
                {
                    string key = string.IsNullOrEmpty(record.textureSet)
                        ? record.name
                        : record.textureSet;

                    if (!packedBySet.TryGetValue(
                            key,
                            out metallicSmoothness))
                    {
                        metallicSmoothness = BuildMetallicSmoothness(
                            record,
                            channels);
                        packedBySet[key] = metallicSmoothness;
                    }
                }

                string materialPath =
                    MaterialAssetRoot +
                    "/" +
                    SafeFile(record.name) +
                    ".mat";

                Material material =
                    AssetDatabase.LoadAssetAtPath<Material>(materialPath);

                bool isNew = material == null;
                if (isNew)
                {
                    Shader shader = Shader.Find(
                        "Universal Render Pipeline/Lit");
                    if (shader == null)
                        throw new InvalidOperationException(
                            "URP Lit shader was not found.");

                    material = new Material(shader)
                    {
                        name = record.name
                    };
                    AssetDatabase.CreateAsset(material, materialPath);
                    created++;
                }
                else
                {
                    updated++;
                }

                ApplyRecord(
                    material,
                    record,
                    channels,
                    metallicSmoothness);

                EditorUtility.SetDirty(material);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log(
                $"W3 URP MATERIALS: PASS materials={contract.materials.Length}, " +
                $"created={created}, updated={updated}, copiedTextures={copied.Count}, " +
                $"packedSets={packedBySet.Count}");
        }

        private static void ApplyRecord(
            Material material,
            MaterialRecord record,
            Dictionary<string, string> channels,
            string metallicSmoothnessPath)
        {
            float tile = record.tileMeters > .001f
                ? 1f / record.tileMeters
                : 1f;

            Color tint = Color.white;
            if (record.tint != null && record.tint.Length >= 3)
            {
                tint = new Color(
                    record.tint[0],
                    record.tint[1],
                    record.tint[2],
                    record.tint.Length > 3 ? record.tint[3] : 1f);
            }

            if (channels.TryGetValue(
                    "BaseColor",
                    out string basePath))
            {
                Texture2D tex =
                    AssetDatabase.LoadAssetAtPath<Texture2D>(basePath);
                material.SetTexture("_BaseMap", tex);
                material.SetTextureScale(
                    "_BaseMap",
                    new Vector2(tile, tile));
            }

            if (channels.TryGetValue(
                    "Normal",
                    out string normalPath))
            {
                Texture2D tex =
                    AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath);
                material.SetTexture("_BumpMap", tex);
                material.SetTextureScale(
                    "_BumpMap",
                    new Vector2(tile, tile));
                material.SetFloat(
                    "_BumpScale",
                    IsGroundFamily(record.family) ? .7f : .9f);
                material.EnableKeyword("_NORMALMAP");
            }
            else
            {
                material.SetTexture("_BumpMap", null);
                material.DisableKeyword("_NORMALMAP");
            }

            if (channels.TryGetValue(
                    "AO",
                    out string aoPath))
            {
                Texture2D tex =
                    AssetDatabase.LoadAssetAtPath<Texture2D>(aoPath);
                material.SetTexture("_OcclusionMap", tex);
                material.SetTextureScale(
                    "_OcclusionMap",
                    new Vector2(tile, tile));
                material.SetFloat("_OcclusionStrength", .85f);
            }
            else
            {
                material.SetTexture("_OcclusionMap", null);
            }

            if (!record.isGlass &&
                !string.IsNullOrEmpty(metallicSmoothnessPath))
            {
                Texture2D packed =
                    AssetDatabase.LoadAssetAtPath<Texture2D>(
                        metallicSmoothnessPath);
                material.SetTexture("_MetallicGlossMap", packed);
                material.SetTextureScale(
                    "_MetallicGlossMap",
                    new Vector2(tile, tile));
                material.SetFloat("_Metallic", 1f);
                material.SetFloat("_Smoothness", 1f);
                material.EnableKeyword("_METALLICSPECGLOSSMAP");
            }
            else
            {
                material.SetTexture("_MetallicGlossMap", null);
                material.SetFloat("_Metallic", Mathf.Clamp01(record.metallic));
                material.SetFloat(
                    "_Smoothness",
                    Mathf.Clamp01(1f - record.roughness));
                material.DisableKeyword("_METALLICSPECGLOSSMAP");
            }

            if (record.isGlass)
                ConfigureGlass(material, record, tint);
            else
                ConfigureOpaque(material, tint);
        }

        private static void ConfigureOpaque(
            Material material,
            Color tint)
        {
            tint.a = 1f;
            material.SetColor("_BaseColor", tint);
            material.SetFloat("_Surface", 0f);
            material.SetFloat("_ZWrite", 1f);
            material.SetOverrideTag("RenderType", "Opaque");
            material.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.renderQueue = (int)RenderQueue.Geometry;
        }

        private static void ConfigureGlass(
            Material material,
            MaterialRecord record,
            Color tint)
        {
            if (record.diffuseColor != null &&
                record.diffuseColor.Length >= 3)
            {
                tint.r = record.diffuseColor[0];
                tint.g = record.diffuseColor[1];
                tint.b = record.diffuseColor[2];
            }

            tint.a = Mathf.Clamp01(record.alpha);
            material.SetColor("_BaseColor", tint);
            material.SetFloat("_Surface", 1f);
            material.SetFloat("_Blend", 0f);
            material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            material.SetFloat(
                "_DstBlend",
                (float)BlendMode.OneMinusSrcAlpha);
            material.SetFloat("_ZWrite", 0f);
            material.SetFloat("_Metallic", 0f);
            material.SetFloat(
                "_Smoothness",
                Mathf.Clamp01(1f - record.roughness));
            material.SetOverrideTag("RenderType", "Transparent");
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.renderQueue = (int)RenderQueue.Transparent;
        }

        private static string SyncTexture(
            string repositoryRelativePath,
            string textureSet,
            string channel,
            Dictionary<string, string> copied)
        {
            string source = Path.GetFullPath(
                Path.Combine(
                    RepositoryRoot(),
                    repositoryRelativePath.Replace(
                        '/',
                        Path.DirectorySeparatorChar)));

            if (!File.Exists(source))
                throw new FileNotFoundException(
                    $"W3 texture missing for {channel}.",
                    source);

            if (copied.TryGetValue(source, out string existing))
                return existing;

            string folder = TextureAssetRoot;
            if (!string.IsNullOrEmpty(textureSet))
                folder += "/" + SafeFile(textureSet);
            EnsureAssetFolder(folder);

            string assetPath =
                folder + "/" + Path.GetFileName(source);
            string destination = AssetPathToAbsolute(assetPath);

            Directory.CreateDirectory(
                Path.GetDirectoryName(destination));
            File.Copy(source, destination, true);
            AssetDatabase.ImportAsset(
                assetPath,
                ImportAssetOptions.ForceSynchronousImport |
                ImportAssetOptions.ForceUpdate);

            TextureImporter importer =
                AssetImporter.GetAtPath(assetPath)
                as TextureImporter;

            if (importer != null)
            {
                bool normal = string.Equals(
                    channel,
                    "Normal",
                    StringComparison.OrdinalIgnoreCase);

                importer.textureType = normal
                    ? TextureImporterType.NormalMap
                    : TextureImporterType.Default;
                importer.sRGBTexture = string.Equals(
                    channel,
                    "BaseColor",
                    StringComparison.OrdinalIgnoreCase);
                importer.mipmapEnabled = true;
                importer.wrapMode = TextureWrapMode.Repeat;
                importer.filterMode = FilterMode.Trilinear;
                importer.anisoLevel = 4;
                importer.SaveAndReimport();
            }

            copied[source] = assetPath;
            return assetPath;
        }

        private static string BuildMetallicSmoothness(
            MaterialRecord record,
            Dictionary<string, string> channels)
        {
            Texture2D rough = LoadSourceImage(
                FindChannel(record, "Roughness"));
            Texture2D metallic = LoadSourceImage(
                FindChannel(record, "Metallic"));

            int width = rough != null
                ? rough.width
                : metallic != null ? metallic.width : 4;
            int height = rough != null
                ? rough.height
                : metallic != null ? metallic.height : 4;

            var packed = new Texture2D(
                width,
                height,
                TextureFormat.RGBA32,
                true,
                true);

            Color32[] pixels = new Color32[width * height];
            Color[] roughPixels =
                rough != null ? rough.GetPixels() : null;
            Color[] metallicPixels =
                metallic != null ? metallic.GetPixels() : null;

            for (int i = 0; i < pixels.Length; i++)
            {
                float m = metallicPixels != null
                    ? metallicPixels[i].r
                    : record.metallic;
                float r = roughPixels != null
                    ? roughPixels[i].r
                    : record.roughness;
                float smooth = Mathf.Clamp01(1f - r);

                pixels[i] = new Color(
                    Mathf.Clamp01(m),
                    0f,
                    0f,
                    smooth);
            }

            packed.SetPixels32(pixels);
            packed.Apply(true, false);

            string set = string.IsNullOrEmpty(record.textureSet)
                ? SafeFile(record.name)
                : SafeFile(record.textureSet);
            string folder = TextureAssetRoot + "/" + set;
            EnsureAssetFolder(folder);

            string assetPath =
                folder +
                "/" +
                set +
                "_MetallicSmoothness.png";
            File.WriteAllBytes(
                AssetPathToAbsolute(assetPath),
                packed.EncodeToPNG());

            UnityEngine.Object.DestroyImmediate(packed);
            if (rough != null)
                UnityEngine.Object.DestroyImmediate(rough);
            if (metallic != null)
                UnityEngine.Object.DestroyImmediate(metallic);

            AssetDatabase.ImportAsset(
                assetPath,
                ImportAssetOptions.ForceSynchronousImport |
                ImportAssetOptions.ForceUpdate);

            TextureImporter importer =
                AssetImporter.GetAtPath(assetPath)
                as TextureImporter;
            if (importer != null)
            {
                importer.textureType = TextureImporterType.Default;
                importer.sRGBTexture = false;
                importer.mipmapEnabled = true;
                importer.wrapMode = TextureWrapMode.Repeat;
                importer.SaveAndReimport();
            }

            return assetPath;
        }

        private static string FindChannel(
            MaterialRecord record,
            string channel)
        {
            foreach (MapRecord map in record.maps ?? Array.Empty<MapRecord>())
            {
                if (map != null &&
                    string.Equals(
                        map.channel,
                        channel,
                        StringComparison.OrdinalIgnoreCase))
                    return map.path;
            }

            return null;
        }

        private static Texture2D LoadSourceImage(
            string repositoryRelativePath)
        {
            if (string.IsNullOrEmpty(repositoryRelativePath))
                return null;

            string path = Path.GetFullPath(
                Path.Combine(
                    RepositoryRoot(),
                    repositoryRelativePath.Replace(
                        '/',
                        Path.DirectorySeparatorChar)));

            if (!File.Exists(path))
                throw new FileNotFoundException(
                    "Material channel source image missing.",
                    path);

            var texture = new Texture2D(
                2,
                2,
                TextureFormat.RGBA32,
                false,
                true);

            if (!texture.LoadImage(File.ReadAllBytes(path), false))
            {
                UnityEngine.Object.DestroyImmediate(texture);
                throw new InvalidDataException(
                    "Unity could not decode " + path);
            }

            return texture;
        }

        private static bool IsGroundFamily(string family)
        {
            return string.Equals(
                       family,
                       "terreno",
                       StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(
                       family,
                       "asfalto",
                       StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(
                       family,
                       "pavimento",
                       StringComparison.OrdinalIgnoreCase);
        }

        private static string RepositoryRoot()
        {
            return Path.GetFullPath(
                Path.Combine(Application.dataPath, "..", ".."));
        }

        private static string AssetPathToAbsolute(string assetPath)
        {
            return Path.GetFullPath(
                Path.Combine(
                    Application.dataPath,
                    "..",
                    assetPath));
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

        private static string SafeFile(string value)
        {
            foreach (char invalid in Path.GetInvalidFileNameChars())
                value = value.Replace(invalid, '_');
            return value.Replace('/', '_').Replace('\\', '_');
        }
    }
}
