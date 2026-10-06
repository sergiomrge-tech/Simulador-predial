using System;

namespace ResortAurora.Sim
{
    public enum DayPhase { Amanhecer, Manha, MeioDia, Tarde, PorDoSol, Noite }

    /// <summary>
    /// Light of the world clock (pure C#, so the cycle can be unit-tested and the population model can read it). October on a tropical
    /// coast: sunrise a little before 06:00, sunset around 18:00, about 45 minutes of twilight on each side.
    /// </summary>
    public static class Daylight
    {
        public const float Sunrise = 5.8f, Sunset = 18.0f;
        /// <summary>Street and kiosk lamps come on above this night factor.</summary>
        public const float LampsOnAbove = 0.30f;

        static float Smooth(float a, float b, float x) { float t = Math.Max(0f, Math.Min(1f, (x - a) / (b - a))); return t * t * (3f - 2f * t); }

        /// <summary>0 = full daylight, 1 = full night. Twilight starts before sunset and ends an hour after it; dawn mirrors it.</summary>
        public static float Night(float hours)
        {
            hours = hours % 24f; if (hours < 0f) hours += 24f;
            return hours < 12f ? 1f - Smooth(Sunrise - 0.6f, Sunrise + 0.45f, hours) : Smooth(Sunset - 0.35f, Sunset + 1.0f, hours);
        }

        /// <summary>Sun height above the horizon in degrees (negative below it). Peaks at 78 degrees at solar noon.</summary>
        public static float SunElevation(float hours)
        {
            float t = (hours - Sunrise) / (Sunset - Sunrise);
            return Math.Max(-35f, (float)(78.0 * Math.Sin(Math.PI * t)));
        }

        /// <summary>How low and golden the light is (0 at midday, 1 with the sun on the horizon).</summary>
        public static float Golden(float hours) => 1f - Math.Min(1f, Math.Max(0f, SunElevation(hours)) / 28f);

        public static bool LampsOn(float hours) => Night(hours) > LampsOnAbove;

        public static DayPhase PhaseOf(float hours) =>
            hours < 6.75f ? DayPhase.Amanhecer : hours < 11.5f ? DayPhase.Manha : hours < 14.5f ? DayPhase.MeioDia :
            hours < 17.25f ? DayPhase.Tarde : hours < 19.0f ? DayPhase.PorDoSol : DayPhase.Noite;

        public static string Label(DayPhase p) => p switch
        {
            DayPhase.Amanhecer => "Amanhecer", DayPhase.Manha => "Manhã", DayPhase.MeioDia => "Meio-dia",
            DayPhase.Tarde => "Tarde", DayPhase.PorDoSol => "Pôr do sol", _ => "Noite",
        };
    }

    /// <summary>
    /// How full the beach and promenade are, by hour, weather, reputation and stage of the business. Pure numbers: the scene layer turns them into
    /// pooled people. Mornings are joggers and locals, midday is the beach, the late afternoon is the stroll, nights are quieter but never empty.
    /// </summary>
    public static class PopulationModel
    {
        // 0..23h, people on the beach and promenade relative to a full midday
        static readonly float[] hourCurve =
        {
            0.04f, 0.03f, 0.02f, 0.02f, 0.05f, 0.14f,   0.22f, 0.32f, 0.46f, 0.66f, 0.86f, 1.00f,
            1.00f, 1.00f, 0.95f, 0.86f, 0.80f, 0.74f,   0.60f, 0.42f, 0.32f, 0.24f, 0.14f, 0.08f,
        };

        public struct Mix { public int Strollers, Joggers, Cyclists, Beach, Swimmers, Kids; public int Total => Strollers + Joggers + Cyclists + Beach + Swimmers + Kids; }

        public static float Density(float hours, Weather w, float reputation, int stage)
        {
            hours = hours % 24f; if (hours < 0f) hours += 24f;
            int a = (int)hours, b = (a + 1) % 24; float f = hours - a;
            float curve = hourCurve[a] * (1f - f) + hourCurve[b] * f;
            float weather = w == Weather.Hot ? 1.15f : w == Weather.Sunny ? 1f : w == Weather.Cloudy ? 0.7f : 0.6f;
            float rep = 0.9f + 0.4f * Math.Max(0f, Math.Min(1f, reputation));
            return curve * weather * rep * (1f + 0.08f * Math.Max(0, stage - 1));
        }

        /// <summary>Target head counts for each kind of ambient person (before the kiosk's own customers).</summary>
        public static Mix MixFor(float hours, Weather w, float reputation, int stage)
        {
            float d = Density(hours, w, reputation, stage), night = Daylight.Night(hours);
            float sunny = (1f - night) * (1f - night);                                  // nobody sunbathes after dark
            float dawnDusk = Math.Max(0f, 1f - Math.Abs(hours - 7f) / 2f) + Math.Max(0f, 1f - Math.Abs(hours - 17.5f) / 2f);
            return new Mix
            {
                Strollers = (int)Math.Round(14f * d * (1f - 0.35f * night)),            // groups, 1-4 people each
                Joggers = (int)Math.Round(5f * Math.Min(1f, dawnDusk) * (w == Weather.Hot ? 0.5f : 1f) * (night > 0.8f ? 0f : 1f)),
                Cyclists = (int)Math.Round(3f * d * (1f - night)),
                Beach = (int)Math.Round(24f * d * sunny),
                Swimmers = (int)Math.Round(8f * d * sunny * (w == Weather.Cloudy || w == Weather.Windy ? 0.5f : 1f)),
                Kids = (int)Math.Round(6f * d * sunny),
            };
        }
    }
}
