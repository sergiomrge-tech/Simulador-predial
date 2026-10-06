using UnityEngine;

namespace ResortAurora.Grid
{
    /// <summary>Contract the placement code depends on. Lets tests and future systems (pathfinding, zoning) use a fake grid.</summary>
    public interface IGridService
    {
        float CellSize { get; }
        Vector2Int Size { get; }
        bool InBounds(Vector2Int cell);
        Vector2Int WorldToCell(Vector3 world);
        /// <summary>World position of the cell's centre, on the grid plane.</summary>
        Vector3 CellToWorld(Vector2Int cell);
        /// <summary>World centre of a footprint of <paramref name="size"/> cells whose min corner is <paramref name="origin"/>.</summary>
        Vector3 FootprintCenter(Vector2Int origin, Vector2Int size);
        bool CanPlace(Vector2Int origin, Vector2Int size);
        bool Occupy(Vector2Int origin, Vector2Int size, int ownerId);
        void Release(Vector2Int origin, Vector2Int size);
        /// <summary>Intersects a ray with the grid plane.</summary>
        bool TryRaycast(Ray ray, out Vector3 point);
    }
}
