using System.Collections.Generic;

namespace FacilityOps
{
    /// <summary>
    /// Pure streaming neighborhood rules. No scene I/O.
    /// The initial production target is 3x3 loaded, 5x5 retained for hysteresis.
    /// </summary>
    public static class WorldStreamingPolicy
    {
        public const int LoadRadius = 1;
        public const int KeepRadius = 2;

        public static HashSet<WorldStreamingId> BuildSquare(WorldStreamingId center, int radius)
        {
            var result = new HashSet<WorldStreamingId>();
            int centerX = center.MacroX * WorldStreamingId.SubcellsPerMacroAxis + center.SubX;
            int centerZ = center.MacroZ * WorldStreamingId.SubcellsPerMacroAxis + center.SubZ;
            int max = WorldStreamingId.MacroCellCountPerAxis * WorldStreamingId.SubcellsPerMacroAxis;

            for (int dz = -radius; dz <= radius; dz++)
            for (int dx = -radius; dx <= radius; dx++)
            {
                int gx = centerX + dx;
                int gz = centerZ + dz;
                if (gx < 0 || gz < 0 || gx >= max || gz >= max)
                    continue;

                int macroX = gx / WorldStreamingId.SubcellsPerMacroAxis;
                int macroZ = gz / WorldStreamingId.SubcellsPerMacroAxis;
                int subX = gx % WorldStreamingId.SubcellsPerMacroAxis;
                int subZ = gz % WorldStreamingId.SubcellsPerMacroAxis;
                result.Add(new WorldStreamingId(macroX, macroZ, subX, subZ));
            }

            return result;
        }

        public static HashSet<WorldStreamingId> BuildLoadSet(WorldStreamingId center) =>
            BuildSquare(center, LoadRadius);

        public static HashSet<WorldStreamingId> BuildKeepSet(WorldStreamingId center) =>
            BuildSquare(center, KeepRadius);
    }
}
