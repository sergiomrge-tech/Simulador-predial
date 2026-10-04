using System.Text;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FacilityOps
{
    /// <summary>
    /// Optional development-only overlay for the first playable world slice.
    /// Attach manually to a QA rig; it renders nothing in non-development player builds.
    /// </summary>
    public sealed class WorldStreamingDebugOverlay : MonoBehaviour
    {
        [SerializeField] private WorldStreamService streamService;
        [SerializeField] private bool visible = true;

        private GUIStyle style;
        private readonly StringBuilder buffer = new StringBuilder(256);

        public WorldStreamService StreamService
        {
            get => streamService;
            set => streamService = value;
        }

        private void OnGUI()
        {
            if (!visible || streamService == null)
                return;

            if (!Application.isEditor && !Debug.isDebugBuild)
                return;

            if (style == null)
            {
                style = new GUIStyle(GUI.skin.box)
                {
                    alignment = TextAnchor.UpperLeft,
                    fontSize = 14,
                    richText = false,
                    wordWrap = false
                };
                style.padding = new RectOffset(10, 10, 8, 8);
            }

            buffer.Clear();
            buffer.AppendLine("SANTA AURORA / STREAMING QA");
            buffer.Append("Cell: ").AppendLine(streamService.HasCurrentCell ? streamService.CurrentCell.Name : "n/a");
            buffer.Append("Loaded index: ").Append(streamService.LoadedCells.Count).AppendLine();
            buffer.Append("Pending load: ").Append(streamService.PendingLoadCount).AppendLine();
            buffer.Append("Pending unload: ").Append(streamService.PendingUnloadCount).AppendLine();
            buffer.Append("Unity scenes loaded: ").Append(SceneManager.sceneCount).AppendLine();

            GUI.Box(new Rect(12, 12, 320, 125), buffer.ToString(), style);
        }
    }
}
