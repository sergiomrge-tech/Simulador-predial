using UnityEngine;

namespace FacilityOps
{
    public abstract class ContentDefinition : ScriptableObject
    {
        public string persistentId;
        public string displayName;
    }
    public sealed class ToolDefinition : ContentDefinition { public ToolMode capability; }
    public sealed class PartDefinition : ContentDefinition { public FailureCause compatibleCause; public int cost = 60; }
    public sealed class FailureDefinition : ContentDefinition { public FailureCause cause; public StationId node; public PartDefinition part; }
    public sealed class MissionDefinition : ContentDefinition
    {
        public string symptom;
        public string locationId;
        public FailureDefinition[] allowedFailures;
    }
}
