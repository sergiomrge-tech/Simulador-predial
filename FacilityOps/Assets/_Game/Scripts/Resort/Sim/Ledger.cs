using System;
using System.Collections.Generic;
using ResortAurora.Core;

namespace ResortAurora.Sim
{
    [Serializable]
    public sealed class Transaction
    {
        public int day;
        public string category;
        public int amount; // + income, - expense
    }

    /// <summary>Single source of truth for money. Every change is a categorised transaction (feeds the end-of-day report and analytics).</summary>
    public sealed class Ledger
    {
        readonly IEventBus bus;
        readonly List<Transaction> history = new List<Transaction>();
        public int Balance { get; private set; }
        public IReadOnlyList<Transaction> History => history;

        public Ledger(IEventBus bus, int startingBalance = 0) { this.bus = bus; Balance = startingBalance; }

        public void Restore(int balance, IEnumerable<Transaction> past) { Balance = balance; history.Clear(); history.AddRange(past); }

        public bool CanAfford(int cost) => Balance >= cost;

        public void Add(int day, string category, int amount)
        {
            if (amount == 0) return;
            Balance += amount;
            history.Add(new Transaction { day = day, category = category, amount = amount });
            bus.Publish(new MoneyChanged(Balance, amount, category));
        }

        /// <summary>Spends money if affordable. Returns false (and changes nothing) otherwise.</summary>
        public bool TrySpend(int day, string category, int cost)
        {
            if (cost < 0 || Balance < cost) return false;
            Add(day, category, -cost);
            return true;
        }

        public int DayTotal(int day, bool income)
        {
            int sum = 0;
            foreach (var t in history) if (t.day == day && (t.amount > 0) == income) sum += t.amount;
            return income ? sum : -sum;
        }

        public Dictionary<string, int> DayByCategory(int day)
        {
            var d = new Dictionary<string, int>();
            foreach (var t in history) if (t.day == day) d[t.category] = (d.TryGetValue(t.category, out var v) ? v : 0) + t.amount;
            return d;
        }
    }
}
