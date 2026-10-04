using System;
using UnityEngine;

namespace FacilityOps
{
    public readonly struct WorldSliceDestination
    {
        public readonly string FacilityId;
        public readonly Vector3 FallbackPosition;
        public readonly float FallbackYaw;
        public readonly string PreferredMarkerSuffix;

        public WorldSliceDestination(
            string facilityId,
            Vector3 fallbackPosition,
            float fallbackYaw,
            string preferredMarkerSuffix = null)
        {
            FacilityId = facilityId;
            FallbackPosition = fallbackPosition;
            FallbackYaw = fallbackYaw;
            PreferredMarkerSuffix = preferredMarkerSuffix;
        }

        public WorldStreamingId Cell =>
            WorldStreamingId.FromWorldPosition(
                FallbackPosition.x,
                FallbackPosition.z);
    }

    /// <summary>
    /// Stable pilot destinations used only by the first world-slice compatibility bridge.
    /// These are fallback entry points, not mission-authoritative coordinates.
    /// Real Blender gameplay markers take priority when present.
    /// </summary>
    public static class WorldSliceDestinationRegistry
    {
        private static readonly WorldSliceDestination[] Destinations =
        {
            new WorldSliceDestination(
                "home.starter",
                new Vector3(-2860f, 17.65f, -2266f),
                180f),

            new WorldSliceDestination(
                "garage",
                new Vector3(-2710f, 21.7f, -2150f),
                90f),

            new WorldSliceDestination(
                "horizonte",
                new Vector3(-2350f, 28.0f, -1831f),
                0f,
                "GP_prologue_spawn_corridor"),

            new WorldSliceDestination(
                "grocery",
                new Vector3(-2598f, 25.9f, -1480f),
                90f)
        };

        public static bool TryGet(string facilityId, out WorldSliceDestination destination)
        {
            foreach (WorldSliceDestination candidate in Destinations)
            {
                if (!string.Equals(
                        candidate.FacilityId,
                        facilityId,
                        StringComparison.Ordinal))
                    continue;

                destination = candidate;
                return true;
            }

            destination = default;
            return false;
        }

        public static WorldSliceDestination Require(string facilityId)
        {
            if (TryGet(facilityId, out WorldSliceDestination destination))
                return destination;

            throw new ArgumentOutOfRangeException(
                nameof(facilityId),
                facilityId,
                "Facility is not part of the first playable world-slice registry.");
        }
    }
}
