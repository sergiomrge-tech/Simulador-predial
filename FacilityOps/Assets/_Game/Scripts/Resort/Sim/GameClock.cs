using ResortAurora.Core;

namespace ResortAurora.Sim
{
    /// <summary>
    /// In-game clock. One day runs 06:00 to 22:00 of play (night is skipped by the end-of-day flow). Pure C#: ticked by the runtime,
    /// so it can be unit-tested and run headless faster than real time.
    /// </summary>
    public sealed class GameClock
    {
        public const float DayStart = 6f * 60f, DayEnd = 22f * 60f;

        readonly IEventBus bus;
        public int Day { get; private set; } = 1;
        /// <summary>Minutes since midnight.</summary>
        public float Minutes { get; private set; } = DayStart;
        /// <summary>Real seconds per in-game minute.</summary>
        public float SecondsPerMinute { get; set; } = 0.75f;
        public bool Paused { get; set; }
        public bool DayOver => Minutes >= DayEnd;
        public int Hour => (int)(Minutes / 60f);
        public float Hours => Minutes / 60f;

        public GameClock(IEventBus bus) { this.bus = bus; }

        public void Restore(int day, float minutes) { Day = day; Minutes = minutes; }

        public void Tick(float dt)
        {
            if (Paused || DayOver) return;
            int before = Hour;
            Minutes = System.Math.Min(DayEnd, Minutes + dt / SecondsPerMinute);
            if (Hour != before) bus.Publish(new HourChanged(Day, Hour));
            if (DayOver) bus.Publish(new DayEnded(Day));
        }

        public void StartNextDay() { Day++; Minutes = DayStart; bus.Publish(new HourChanged(Day, Hour)); }

        public static string Format(float minutes) => $"{(int)(minutes / 60f):00}:{(int)(minutes % 60f):00}";
    }
}
