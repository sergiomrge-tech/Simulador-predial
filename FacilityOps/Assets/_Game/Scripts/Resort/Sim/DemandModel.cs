using System;

namespace ResortAurora.Sim
{
    /// <summary>
    /// How many potential customers pass the stall each hour and what they pick. Deterministic given (seed, day, hour), so the same day
    /// replays identically and the model can be balanced offline.
    /// </summary>
    public static class DemandModel
    {
        // Foot traffic on the promenade by hour of day (people per hour that pass in front of the stall at neutral conditions).
        static readonly float[] hourCurve =
        {
            // 0..5 (closed)           6     7     8     9     10    11    12    13    14    15    16    17    18    19    20    21
            0,0,0,0,0,0,              2,    4,    8,    12,   18,   26,   32,   30,   26,   22,   18,   14,   8,    4,    2,    0,
        };

        public static Weather WeatherFor(int seed, int day)
        {
            var r = new Random(seed * 7919 + day * 104729);
            double v = r.NextDouble();
            return v < 0.45 ? Weather.Sunny : v < 0.65 ? Weather.Hot : v < 0.88 ? Weather.Cloudy : Weather.Windy;
        }

        /// <summary>Expected people stopping to consider the stall this hour (before price and reputation effects).</summary>
        public static float Passersby(int hour, Weather w) => (hour >= 0 && hour < hourCurve.Length ? hourCurve[hour] : 0f) * WeatherInfo.Traffic(w) * TrafficScale;

        /// <summary>Balance knob for the stall stage (a beach stall is not the busiest place in town).</summary>
        public const float TrafficScale = 0.6f;

        /// <summary>Probability that a passer-by stops, from reputation (0..1) and how expensive the menu feels.</summary>
        public static float StopChance(StallModel stall)
        {
            float priceFeel = 0f; int n = 0;
            foreach (var p in Catalog.Products) { if (stall.Stock(p.Id) <= 0) continue; priceFeel += (float)stall.Price(p.Id) / p.BasePrice; n++; }
            priceFeel = n == 0 ? 1f : priceFeel / n;
            float priceFactor = Math.Max(0.15f, 1.6f - priceFeel * 0.6f);            // 1.0 at base price, falling when pricier
            float rep = 0.35f + 0.9f * stall.Reputation;                              // 0.35..1.25
            float comfort = stall.Has("up.mesas") ? 1.15f : 1f;
            return Math.Min(0.95f, 0.45f * priceFactor * rep * comfort);
        }

        /// <summary>Picks what a customer wants among products in stock; null if everything is sold out.</summary>
        public static ProductDef Pick(StallModel stall, Weather w, Random rng)
        {
            float total = 0f; var weights = new float[Catalog.Products.Length];
            for (int i = 0; i < weights.Length; i++)
            {
                var p = Catalog.Products[i];
                if (stall.Stock(p.Id) <= 0) continue;
                float heat = WeatherInfo.Heat(w) * (stall.Has("up.freezer") && (p.Id == "sweet.picole" || p.Id == "drink.coco") ? 1.4f : 1f);
                float priceFeel = Math.Max(0.3f, 1.4f - 0.4f * stall.Price(p.Id) / p.BasePrice);
                weights[i] = Math.Max(0.05f, p.Appeal * (1f + p.HeatSensitivity * heat) * priceFeel);
                total += weights[i];
            }
            if (total <= 0f) return null;
            float roll = (float)rng.NextDouble() * total;
            for (int i = 0; i < weights.Length; i++) { roll -= weights[i]; if (roll <= 0f && weights[i] > 0f) return Catalog.Products[i]; }
            return Catalog.Products[weights.Length - 1];
        }
    }
}
