using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Metadata anchor for one additive Santa Aurora cell scene.
    /// The scene root remains data-only until the real exported content is attached.
    /// </summary>
    public sealed class WorldCellRoot : MonoBehaviour
    {
        [SerializeField] private string cellId;
        [SerializeField] private string sourceManifest = "oldtown_streaming_manifest_v1.json";
        [SerializeField] private bool containsGameplayMarkers;
        [SerializeField] private bool highFidelityPilotCell;

        public string CellId => cellId;
        public string SourceManifest => sourceManifest;
        public bool ContainsGameplayMarkers => containsGameplayMarkers;
        public bool HighFidelityPilotCell => highFidelityPilotCell;

        public bool TryGetStreamingId(out WorldStreamingId id) =>
            WorldStreamingId.TryParse(cellId, out id);

        public void Configure(
            string id,
            bool gameplayMarkers,
            bool pilotCell,
            string manifest = "oldtown_streaming_manifest_v1.json")
        {
            cellId = id;
            containsGameplayMarkers = gameplayMarkers;
            highFidelityPilotCell = pilotCell;
            sourceManifest = string.IsNullOrEmpty(manifest)
                ? "oldtown_streaming_manifest_v1.json"
                : manifest;
        }
    }
}
