using UnityEngine;

namespace ResortAurora.Placement
{
    /// <summary>Data for one placeable building (Assets > Create > Resort Aurora > Building Definition). The id must stay stable: saves reference it.</summary>
    [CreateAssetMenu(menuName = "Resort Aurora/Building Definition", fileName = "Building_")]
    public sealed class BuildingDefinition : ScriptableObject
    {
        public string id = "building.cube";
        public string displayName = "Cubo de teste";
        [Tooltip("Footprint in cells (X, Z) at rotation 0.")]
        public Vector2Int footprint = new Vector2Int(2, 2);
        [Min(0.1f)] public float height = 2f;
        [Tooltip("Optional. When empty the placement system builds a cube sized to the footprint.")]
        public GameObject prefab;
        public Color color = new Color(0.85f, 0.75f, 0.55f);
        [Min(0)] public int cost = 1000;
    }
}
