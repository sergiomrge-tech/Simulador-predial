using System.Collections.Generic;

namespace ResortAurora.Sim
{
    /// <summary>A product the stall can sell. Ids are stable: saves and analytics reference them.</summary>
    public sealed class ProductDef
    {
        public string Id, Name;
        public int BasePrice;        // suggested sell price
        public int UnitCost;         // supplier price per unit
        public float PrepSeconds;    // hands-on preparation time at skill 0.5
        public float HeatSensitivity; // how much hot weather boosts demand (cold drinks > fried food)
        public float Appeal;         // relative pick probability
    }

    public static class Catalog
    {
        public static readonly ProductDef[] Products =
        {
            new ProductDef { Id = "food.pastel",   Name = "Salgado",         BasePrice = 9, UnitCost = 3, PrepSeconds = 5.0f, HeatSensitivity = -0.2f, Appeal = 1.0f },
            new ProductDef { Id = "food.milho",    Name = "Milho cozido",   BasePrice = 6, UnitCost = 2, PrepSeconds = 2.5f, HeatSensitivity = -0.1f, Appeal = 0.8f },
            new ProductDef { Id = "drink.agua",    Name = "Água",           BasePrice = 4, UnitCost = 1, PrepSeconds = 0.8f, HeatSensitivity = 1.0f,  Appeal = 1.0f },
            new ProductDef { Id = "drink.refri",   Name = "Refrigerante",   BasePrice = 7, UnitCost = 3, PrepSeconds = 0.8f, HeatSensitivity = 0.7f,  Appeal = 1.0f },
            new ProductDef { Id = "drink.cerveja", Name = "Cerveja",        BasePrice = 10, UnitCost = 5, PrepSeconds = 0.9f, HeatSensitivity = 0.5f, Appeal = 0.9f },
            new ProductDef { Id = "food.lanche",   Name = "Lanche",         BasePrice = 14, UnitCost = 6, PrepSeconds = 6.0f, HeatSensitivity = -0.1f, Appeal = 0.8f },
            new ProductDef { Id = "drink.coco",    Name = "Suco / água de coco",   BasePrice = 7, UnitCost = 3, PrepSeconds = 2.0f, HeatSensitivity = 0.8f,  Appeal = 1.1f },
            new ProductDef { Id = "sweet.picole",  Name = "Picolé",         BasePrice = 5, UnitCost = 2, PrepSeconds = 1.2f, HeatSensitivity = 1.0f,  Appeal = 0.7f },
        };

        static readonly Dictionary<string, ProductDef> byId = Build();
        static Dictionary<string, ProductDef> Build() { var d = new Dictionary<string, ProductDef>(); foreach (var p in Products) d[p.Id] = p; return d; }
        public static ProductDef Get(string id) => byId[id];
        public static bool TryGet(string id, out ProductDef p) => byId.TryGetValue(id, out p);
    }

    public enum Weather { Sunny, Hot, Cloudy, Windy }

    public static class WeatherInfo
    {
        public static string Label(Weather w) => w switch { Weather.Sunny => "Sol", Weather.Hot => "Calor forte", Weather.Cloudy => "Nublado", _ => "Vento" };
        public static float Traffic(Weather w) => w switch { Weather.Sunny => 1.0f, Weather.Hot => 1.2f, Weather.Cloudy => 0.65f, _ => 0.8f };
        public static float Heat(Weather w) => w switch { Weather.Hot => 1f, Weather.Sunny => 0.5f, _ => 0f };
    }
}
