using UnityEngine;

namespace ResortAurora.Core
{
    /// <summary>A building was committed to the grid. The stable definition id is what gets saved, never the GameObject.</summary>
    public readonly struct BuildingPlaced : IGameEvent
    {
        public readonly string DefinitionId;
        public readonly Vector2Int Origin;
        public readonly int Rotation;
        public BuildingPlaced(string definitionId, Vector2Int origin, int rotation)
        { DefinitionId = definitionId; Origin = origin; Rotation = rotation; }
    }

    public readonly struct PlacementModeChanged : IGameEvent
    {
        public readonly bool Active;
        public readonly string DefinitionId;
        public PlacementModeChanged(bool active, string definitionId) { Active = active; DefinitionId = definitionId; }
    }
}
