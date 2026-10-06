using System.Collections.Generic;
using UnityEngine;

namespace ResortAurora.Grid
{
    /// <summary>
    /// Invisible logical grid on a horizontal plane. Owns occupancy only; it knows nothing about prefabs, UI or money.
    /// Cell (0,0) has its min corner at <c>transform.position</c>; the grid extends along +X and +Z.
    /// </summary>
    public sealed class GridManager : MonoBehaviour, IGridService
    {
        [SerializeField, Min(0.25f)] float cellSize = 1f;
        [SerializeField] Vector2Int size = new Vector2Int(64, 64);
        [Header("Debug")]
        [SerializeField] bool drawGizmos = true;
        [SerializeField] Color gizmoColor = new Color(1f, 1f, 1f, 0.25f);

        readonly Dictionary<Vector2Int, int> occupied = new Dictionary<Vector2Int, int>();

        public float CellSize => cellSize;
        public Vector2Int Size => size;

        void OnValidate()
        {
            cellSize = Mathf.Max(0.25f, cellSize);
            size = Vector2Int.Max(size, Vector2Int.one);
        }

        /// <summary>Runtime setup (site loader). Clears occupancy.</summary>
        public void Configure(Vector2Int newSize, float newCellSize)
        {
            size = Vector2Int.Max(newSize, Vector2Int.one);
            cellSize = Mathf.Max(0.25f, newCellSize);
            occupied.Clear();
        }

        public bool InBounds(Vector2Int c) => c.x >= 0 && c.y >= 0 && c.x < size.x && c.y < size.y;

        public Vector2Int WorldToCell(Vector3 w)
        {
            var l = w - transform.position;
            return new Vector2Int(Mathf.FloorToInt(l.x / cellSize), Mathf.FloorToInt(l.z / cellSize));
        }

        public Vector3 CellToWorld(Vector2Int c) =>
            transform.position + new Vector3((c.x + 0.5f) * cellSize, 0f, (c.y + 0.5f) * cellSize);

        public Vector3 FootprintCenter(Vector2Int origin, Vector2Int fp) =>
            transform.position + new Vector3((origin.x + fp.x * 0.5f) * cellSize, 0f, (origin.y + fp.y * 0.5f) * cellSize);

        public bool CanPlace(Vector2Int origin, Vector2Int fp)
        {
            if (fp.x <= 0 || fp.y <= 0) return false;
            for (int x = 0; x < fp.x; x++)
                for (int y = 0; y < fp.y; y++)
                {
                    var c = new Vector2Int(origin.x + x, origin.y + y);
                    if (!InBounds(c) || occupied.ContainsKey(c)) return false;
                }
            return true;
        }

        public bool Occupy(Vector2Int origin, Vector2Int fp, int ownerId)
        {
            if (!CanPlace(origin, fp)) return false;
            for (int x = 0; x < fp.x; x++)
                for (int y = 0; y < fp.y; y++)
                    occupied[new Vector2Int(origin.x + x, origin.y + y)] = ownerId;
            return true;
        }

        public void Release(Vector2Int origin, Vector2Int fp)
        {
            for (int x = 0; x < fp.x; x++)
                for (int y = 0; y < fp.y; y++)
                    occupied.Remove(new Vector2Int(origin.x + x, origin.y + y));
        }

        public bool TryRaycast(Ray ray, out Vector3 point)
        {
            var plane = new Plane(Vector3.up, transform.position); // built per call so moving the grid object always works
            if (plane.Raycast(ray, out float t)) { point = ray.GetPoint(t); return true; }
            point = default;
            return false;
        }

        void OnDrawGizmos()
        {
            if (!drawGizmos) return;
            Gizmos.color = gizmoColor;
            var o = transform.position;
            float w = size.x * cellSize, d = size.y * cellSize;
            for (int x = 0; x <= size.x; x++) Gizmos.DrawLine(o + new Vector3(x * cellSize, 0, 0), o + new Vector3(x * cellSize, 0, d));
            for (int y = 0; y <= size.y; y++) Gizmos.DrawLine(o + new Vector3(0, 0, y * cellSize), o + new Vector3(w, 0, y * cellSize));
        }
    }
}
