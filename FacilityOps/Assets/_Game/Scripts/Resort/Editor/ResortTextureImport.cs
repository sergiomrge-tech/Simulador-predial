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
            if (assetPath.EndsWith("_Normal.jpg")) ti.textureType = TextureImporterType.NormalMap;
        }
    }
}
