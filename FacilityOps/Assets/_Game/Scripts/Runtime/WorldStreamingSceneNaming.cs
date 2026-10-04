namespace FacilityOps
{
    /// <summary>
    /// Stable scene naming contract for additive world cells.
    /// </summary>
    public static class WorldStreamingSceneNaming
    {
        public const string Prefix = "SA_Cell_";

        public static string SceneName(WorldStreamingId id) => Prefix + id.Name;

        public static bool TryParseSceneName(string sceneName, out WorldStreamingId id)
        {
            id = default;
            if (string.IsNullOrEmpty(sceneName) || !sceneName.StartsWith(Prefix))
                return false;

            return WorldStreamingId.TryParse(sceneName.Substring(Prefix.Length), out id);
        }
    }
}
