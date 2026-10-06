using System;
using System.Collections.Generic;

namespace ResortAurora.Sim
{
    [Serializable]
    public sealed class StockEntry { public string productId; public int count; public int price; }

    [Serializable]
    public sealed class UpgradeEntry { public string id; }

    public sealed class UpgradeDef
    {
        public string Id, Name, Description; public int Cost;
    }

    /// <summary>State of the beach stall: stock, prices, upgrades, reputation. No Unity types, so it is saved and tested as data.</summary>
    public sealed class StallModel
    {
        public static readonly UpgradeDef[] Upgrades =
        {
            new UpgradeDef { Id = "up.toldo",   Name = "Toldo novo",       Cost = 140, Description = "Sombra: clientes aguentam esperar mais e o calor pesa menos." },
            new UpgradeDef { Id = "up.freezer", Name = "Freezer",          Cost = 220, Description = "Picolé e água de coco gelados vendem mais no calor." },
            new UpgradeDef { Id = "up.fogao",   Name = "Fogão de 2 bocas", Cost = 300, Description = "Pastéis e milho saem 30% mais rápido." },
            new UpgradeDef { Id = "up.mesas",   Name = "Mesas de plástico", Cost = 180, Description = "Mais clientes sentam e voltam. Reputação sobe mais rápido." },
        };

        public const int MaxStockPerProduct = 60;
        readonly Dictionary<string, int> stock = new Dictionary<string, int>();
        readonly Dictionary<string, int> price = new Dictionary<string, int>();
        readonly HashSet<string> upgrades = new HashSet<string>();
        public float Reputation { get; set; } = 0.3f; // 0..1
        /// <summary>A beach stall cannot become famous: reputation above this needs the next stage (set by the progression system).</summary>
        public float ReputationCap { get; set; } = 0.6f;

        public StallModel()
        {
            foreach (var p in Catalog.Products) { stock[p.Id] = 0; price[p.Id] = p.BasePrice; }
        }

        public int Stock(string id) => stock[id];
        public int Price(string id) => price[id];
        public void SetPrice(string id, int value) => price[id] = Math.Max(1, Math.Min(value, Catalog.Get(id).BasePrice * 3));
        public bool Has(string upgradeId) => upgrades.Contains(upgradeId);
        public void Grant(string upgradeId) => upgrades.Add(upgradeId);
        public IEnumerable<string> OwnedUpgrades => upgrades;

        public int Buy(string id, int qty, Ledger ledger, int day)
        {
            qty = Math.Max(0, Math.Min(qty, MaxStockPerProduct - stock[id]));
            if (qty == 0) return 0;
            int cost = Catalog.Get(id).UnitCost * qty;
            if (!ledger.TrySpend(day, "estoque", cost))
            {
                qty = ledger.Balance / Catalog.Get(id).UnitCost;
                if (qty <= 0) return 0;
                ledger.TrySpend(day, "estoque", Catalog.Get(id).UnitCost * qty);
            }
            stock[id] += qty;
            return qty;
        }

        public bool TryConsume(string id) { if (stock[id] <= 0) return false; stock[id]--; return true; }

        public bool BuyUpgrade(string id, Ledger ledger, int day)
        {
            if (upgrades.Contains(id)) return false;
            var u = Array.Find(Upgrades, x => x.Id == id);
            if (u == null || !ledger.TrySpend(day, "melhoria", u.Cost)) return false;
            upgrades.Add(id);
            return true;
        }

        /// <summary>End of day: unsold ice cream melts unless there is a freezer.</summary>
        public int MeltStock()
        {
            if (Has("up.freezer")) return 0;
            int lost = stock["sweet.picole"];
            stock["sweet.picole"] = 0;
            return lost;
        }

        public float PrepSpeed => Has("up.fogao") ? 1.3f : 1f;
        public float PatienceBonus => Has("up.toldo") ? 1.25f : 1f;

        public List<StockEntry> ExportStock()
        {
            var l = new List<StockEntry>();
            foreach (var p in Catalog.Products) l.Add(new StockEntry { productId = p.Id, count = stock[p.Id], price = price[p.Id] });
            return l;
        }

        public void ImportStock(IEnumerable<StockEntry> entries)
        {
            foreach (var e in entries) if (stock.ContainsKey(e.productId)) { stock[e.productId] = e.count; price[e.productId] = Math.Max(1, e.price); }
        }
    }
}
