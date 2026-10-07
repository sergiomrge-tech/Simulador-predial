using UnityEditor;

namespace ResortAurora.EditorTools
{
    /// <summary>Import settings for the resort PBR textures: *_Normal.jpg become normal maps; everything gets mipmaps and anisotropic filtering.</summary>
    public sealed class ResortTextureImport : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if (!assetPath.Contains("/Art/Resort/Textures/")) return;
            var ti = (TextureImporter)assetImporter;
            ti.mipmapEnabled = true;
            ti.anisoLevel = 8;
            if (assetPath.EndsWith("_Normal.jpg") || assetPath.EndsWith("_Normal.png"))
                ti.textureType = TextureImporterType.NormalMap;
            ti.sRGBTexture = assetPath.Contains("_BaseColor.");
            ti.streamingMipmaps = true;
            ti.maxTextureSize = 1024;
            if (assetPath.EndsWith("_Mask.png"))
            {
                ti.sRGBTexture = false;
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
                ti.alphaIsTransparency = false;
            }
        }
    }
}
