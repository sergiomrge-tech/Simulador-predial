using System;
using System.Globalization;
using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Stable identifier for Santa Aurora's 250 m streaming subcells.
    /// Naming is shared with the Blender world pipeline:
    /// SA_Mxx_yy_Sxx_yy = 1 km macro cell + 250 m subcell.
    ///
    /// Coordinate convention:
    /// Blender X -> Unity X
    /// Blender Y -> Unity Z
    /// Blender Z -> Unity Y
    ///
    /// This type does not load scenes. It only centralizes parsing and coordinate math
    /// so future streaming code does not duplicate naming rules.
    /// </summary>
    public readonly struct WorldStreamingId : IEquatable<WorldStreamingId>
    {
        public const float WorldHalfExtent = 4000f;
        public const float MacroCellSize = 1000f;
        public const float SubcellSize = 250f;
        public const int MacroCellCountPerAxis = 8;
        public const int SubcellsPerMacroAxis = 4;

        public readonly int MacroX;
        public readonly int MacroZ;
        public readonly int SubX;
        public readonly int SubZ;

        public WorldStreamingId(int macroX, int macroZ, int subX, int subZ)
        {
            MacroX = macroX;
            MacroZ = macroZ;
            SubX = subX;
            SubZ = subZ;
        }

        public string MacroName => $"SA_M{MacroX:00}_{MacroZ:00}";
        public string Name => $"{MacroName}_S{SubX:00}_{SubZ:00}";

        public Vector2 WorldCenterXZ => new Vector2(
            -WorldHalfExtent + MacroX * MacroCellSize + SubX * SubcellSize + SubcellSize * 0.5f,
            -WorldHalfExtent + MacroZ * MacroCellSize + SubZ * SubcellSize + SubcellSize * 0.5f);

        public bool IsInWorldBounds =>
            MacroX >= 0 && MacroX < MacroCellCountPerAxis &&
            MacroZ >= 0 && MacroZ < MacroCellCountPerAxis &&
            SubX >= 0 && SubX < SubcellsPerMacroAxis &&
            SubZ >= 0 && SubZ < SubcellsPerMacroAxis;

        public static bool TryParse(string value, out WorldStreamingId id)
        {
            id = default;
            if (string.IsNullOrEmpty(value) || value.Length != 16)
                return false;

            // SA_M00_00_S00_00
            if (!value.StartsWith("SA_M", StringComparison.Ordinal) ||
                value[6] != '_' || value[9] != '_' || value[10] != 'S' || value[13] != '_')
                return false;

            if (!TryTwoDigits(value, 4, out int macroX) ||
                !TryTwoDigits(value, 7, out int macroZ) ||
                !TryTwoDigits(value, 11, out int subX) ||
                !TryTwoDigits(value, 14, out int subZ))
                return false;

            var candidate = new WorldStreamingId(macroX, macroZ, subX, subZ);
            if (!candidate.IsInWorldBounds)
                return false;

            id = candidate;
            return true;
        }

        public static WorldStreamingId FromWorldPosition(float x, float z)
        {
            float clampedX = Mathf.Clamp(x, -WorldHalfExtent, WorldHalfExtent - 0.001f);
            float clampedZ = Mathf.Clamp(z, -WorldHalfExtent, WorldHalfExtent - 0.001f);
            float localX = clampedX + WorldHalfExtent;
            float localZ = clampedZ + WorldHalfExtent;

            int macroX = Mathf.FloorToInt(localX / MacroCellSize);
            int macroZ = Mathf.FloorToInt(localZ / MacroCellSize);
            int subX = Mathf.FloorToInt((localX % MacroCellSize) / SubcellSize);
            int subZ = Mathf.FloorToInt((localZ % MacroCellSize) / SubcellSize);
            return new WorldStreamingId(macroX, macroZ, subX, subZ);
        }

        private static bool TryTwoDigits(string value, int start, out int parsed)
        {
            parsed = 0;
            if (start < 0 || start + 1 >= value.Length)
                return false;

            char a = value[start];
            char b = value[start + 1];
            if (a < '0' || a > '9' || b < '0' || b > '9')
                return false;

            parsed = (a - '0') * 10 + (b - '0');
            return true;
        }

        public bool Equals(WorldStreamingId other) =>
            MacroX == other.MacroX && MacroZ == other.MacroZ &&
            SubX == other.SubX && SubZ == other.SubZ;

        public override bool Equals(object obj) => obj is WorldStreamingId other && Equals(other);
        public override int GetHashCode() => HashCode.Combine(MacroX, MacroZ, SubX, SubZ);
        public override string ToString() => Name;

        public static bool operator ==(WorldStreamingId left, WorldStreamingId right) => left.Equals(right);
        public static bool operator !=(WorldStreamingId left, WorldStreamingId right) => !left.Equals(right);
    }
}
