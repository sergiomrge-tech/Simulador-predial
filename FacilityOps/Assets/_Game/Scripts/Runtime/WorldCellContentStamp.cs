using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Written by the cell import pipeline after real Blender content is attached.
    /// It distinguishes a generated empty scaffold from an import-ready runtime cell.
    /// </summary>
    public sealed class WorldCellContentStamp : MonoBehaviour
    {
        [SerializeField] private string cellId;
        [SerializeField] private string sourceRevision;
        [SerializeField] private string sourceBlend;
        [SerializeField] private int importedObjectCount;
        [SerializeField] private int importedRendererCount;
        [SerializeField] private int importedColliderCount;
        [SerializeField] private int gameplayMarkerCount;
        [SerializeField] private long estimatedTriangles;
        [SerializeField] private bool terrainPresent;
        [SerializeField] private bool roadsPresent;
        [SerializeField] private bool architecturePresent;
        [SerializeField] private bool importValidated;

        public string CellId => cellId;
        public string SourceRevision => sourceRevision;
        public string SourceBlend => sourceBlend;
        public int ImportedObjectCount => importedObjectCount;
        public int ImportedRendererCount => importedRendererCount;
        public int ImportedColliderCount => importedColliderCount;
        public int GameplayMarkerCount => gameplayMarkerCount;
        public long EstimatedTriangles => estimatedTriangles;
        public bool TerrainPresent => terrainPresent;
        public bool RoadsPresent => roadsPresent;
        public bool ArchitecturePresent => architecturePresent;
        public bool ImportValidated => importValidated;

        public void Configure(
            string id,
            string revision,
            string blend,
            int objects,
            int renderers,
            int colliders,
            int markers,
            long triangles,
            bool hasTerrain,
            bool hasRoads,
            bool hasArchitecture,
            bool validated)
        {
            cellId = id;
            sourceRevision = revision;
            sourceBlend = blend;
            importedObjectCount = objects;
            importedRendererCount = renderers;
            importedColliderCount = colliders;
            gameplayMarkerCount = markers;
            estimatedTriangles = triangles;
            terrainPresent = hasTerrain;
            roadsPresent = hasRoads;
            architecturePresent = hasArchitecture;
            importValidated = validated;
        }
    }
}
