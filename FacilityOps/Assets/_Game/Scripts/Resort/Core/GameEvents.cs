using UnityEngine;

namespace ResortAurora.Core
{
    /// <summary>A building was committed to the grid. The stable definition id is what gets saved, never the GameObject.</summary>
    public readonly struct BuildingPlaced : IGameEvent
    {
        public readonly string DefinitionId;
        public readonly Vector2Int Origin;
        public readonly int Rotation;
        public BuildingPlaced(string definitionId, Vector2Int origin, int rotation)
        { DefinitionId = definitionId; Origin = origin; Rotation = rotation; }
    }

    public readonly struct PlacementModeChanged : IGameEvent
    {
        public readonly bool Active;
        public readonly string DefinitionId;
        public PlacementModeChanged(bool active, string definitionId) { Active = active; DefinitionId = definitionId; }
    }
}

namespace ResortAurora.Core
{
    public readonly struct MoneyChanged : IGameEvent
    {
        public readonly int Balance, Delta; public readonly string Reason;
        public MoneyChanged(int balance, int delta, string reason) { Balance = balance; Delta = delta; Reason = reason; }
    }
    public readonly struct HourChanged : IGameEvent
    {
        public readonly int Day, Hour;
        public HourChanged(int day, int hour) { Day = day; Hour = hour; }
    }
    public readonly struct DayEnded : IGameEvent
    {
        public readonly int Day;
        public DayEnded(int day) { Day = day; }
    }
    public readonly struct StaffChanged : IGameEvent { }
    public readonly struct CustomerServed : IGameEvent
    {
        public readonly string ProductId; public readonly int Paid, Tip;
        public CustomerServed(string productId, int paid, int tip) { ProductId = productId; Paid = paid; Tip = tip; }
    }
    public readonly struct CustomerLost : IGameEvent
    {
        public readonly string Reason;
        public CustomerLost(string reason) { Reason = reason; }
    }
}
