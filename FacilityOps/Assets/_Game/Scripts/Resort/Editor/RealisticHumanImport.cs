using UnityEditor;

namespace ResortAurora.EditorTools
{
    /// <summary>Local licensed scan imports only; never changes global URP settings.</summary>
    public sealed class RealisticHumanImport : AssetPostprocessor
    {
        const string Folder = "Assets/_Game/ThirdParty/Resources/RealisticHumans/";

        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(Folder)) return;
            var model = (ModelImporter)assetImporter;
            model.animationType = ModelImporterAnimationType.Human;
            model.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            model.importAnimation = false;
            model.materialImportMode = ModelImporterMaterialImportMode.None;
            model.importCameras = false;
            model.importLights = false;
            model.isReadable = false;
            model.optimizeGameObjects = false; // retain bones for validation and retargeting
        }

        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Folder)) return;
            var texture = (TextureImporter)assetImporter;
            texture.textureType = assetPath.Contains("_Normal.") ? TextureImporterType.NormalMap : TextureImporterType.Default;
            texture.sRGBTexture = assetPath.Contains("_BaseColor.");
            texture.maxTextureSize = 2048;
            texture.mipmapEnabled = true;
            texture.streamingMipmaps = true;
            texture.anisoLevel = 4;
            texture.isReadable = false;
            texture.alphaSource = TextureImporterAlphaSource.FromInput;
            texture.alphaIsTransparency = false;
        }
    }
}
