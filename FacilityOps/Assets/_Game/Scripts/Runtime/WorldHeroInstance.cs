using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Stable metadata for a hero location instantiated into a streamed cell.
    /// </summary>
    public sealed class WorldHeroInstance : MonoBehaviour
    {
        [SerializeField] private string facilityId;
        [SerializeField] private string cellId;
        [SerializeField] private string sourceManifest;
        [SerializeField] private string sourceBlend;

        public string FacilityId => facilityId;
        public string CellId => cellId;
        public string SourceManifest => sourceManifest;
        public string SourceBlend => sourceBlend;

        public void Configure(
            string facility,
            string cell,
            string manifest,
            string blend)
        {
            facilityId = facility;
            cellId = cell;
            sourceManifest = manifest;
            sourceBlend = blend;
        }
    }
}
