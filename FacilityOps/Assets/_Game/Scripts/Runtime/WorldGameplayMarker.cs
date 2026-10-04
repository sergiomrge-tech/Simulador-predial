using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Stable metadata attached to a marker imported from Blender.
    /// It intentionally contains no gameplay behavior; runtime systems decide how
    /// to interpret spawn, interaction and progression markers.
    /// </summary>
    public sealed class WorldGameplayMarker : MonoBehaviour
    {
        [SerializeField] private string markerName;
        [SerializeField] private string facilityId;
        [SerializeField] private string kind;
        [SerializeField] private string state;
        [SerializeField] private string item;
        [SerializeField] private string note;
        [SerializeField] private string sourceCatalog;

        public string MarkerName => markerName;
        public string FacilityId => facilityId;
        public string Kind => kind;
        public string State => state;
        public string Item => item;
        public string Note => note;
        public string SourceCatalog => sourceCatalog;

        public void Configure(
            string name,
            string facility,
            string markerKind,
            string markerState,
            string markerItem,
            string markerNote,
            string source)
        {
            markerName = name;
            facilityId = facility;
            kind = markerKind;
            state = markerState;
            item = markerItem;
            note = markerNote;
            sourceCatalog = source;
        }
    }
}
