using UnityEditor;

public sealed class VegetationImportSettings : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        if (!assetPath.Replace('\\','/').Contains("/Art/Resort/Vegetation/")) return;
        var t = (TextureImporter)assetImporter;
        t.maxTextureSize = 1024;
        t.textureCompression = TextureImporterCompression.CompressedHQ;

        if (assetPath.EndsWith("_Normal.png"))
        {
            t.textureType = TextureImporterType.NormalMap;
            t.sRGBTexture = false;
        }
        else if (assetPath.EndsWith("_Mask.png"))
        {
            t.textureType = TextureImporterType.Default;
            t.sRGBTexture = false;
            t.alphaSource = TextureImporterAlphaSource.FromInput;
        }
        else if (assetPath.EndsWith("_BaseColor.png"))
        {
            t.textureType = TextureImporterType.Default;
            t.sRGBTexture = true;
            t.alphaSource = TextureImporterAlphaSource.FromInput;
            string p = assetPath.ToLowerInvariant();
            t.alphaIsTransparency = p.Contains("leaves") || p.Contains("grass");
        }
    }

    void OnPreprocessModel()
    {
        if (!assetPath.Replace('\\','/').Contains("/Art/Resort/Vegetation/")) return;
        var m = (ModelImporter)assetImporter;
        m.importAnimation = false;
        m.importCameras = false;
        m.importLights = false;
        m.meshCompression = ModelImporterMeshCompression.Medium;
        m.isReadable = false;
        m.optimizeMeshPolygons = true;
        m.optimizeMeshVertices = true;
    }
}
