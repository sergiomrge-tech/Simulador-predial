using System;
using System.Collections.Generic;
using ResortAurora.Core;

namespace ResortAurora.Sim
{
    public enum CustomerState { Queued, WaitingFood, Ready, Served, Left }

    /// <summary>A customer as pure data. The scene agent that walks around only mirrors this object.</summary>
    public sealed class Customer
    {
        public int Id;
        public ProductDef Product;
        public CustomerState State;
        public float Patience, MaxPatience;
        public bool BeingCooked;
        public int Paid, Tip;
        public float Satisfaction => MaxPatience <= 0f ? 0f : Math.Max(0f, Patience / MaxPatience);
    }

    /// <summary>
    /// The stall's order flow: queue -> take order (counter) -> prepare (grill) -> hand over (counter). Player and staff use the same
    /// verbs, so hiring only automates what the player would do by hand. No Unity dependencies.
    /// </summary>
    public sealed class StallService
    {
        public const int MaxQueue = 6;
        const float BasePatience = 75f;

        readonly IEventBus bus;
        readonly StallModel stall;
        readonly Ledger ledger;
        readonly StaffRoster roster;
        readonly Func<int> day;
        readonly List<Customer> queue = new List<Customer>();
        readonly List<Customer> cooking = new List<Customer>();   // tickets waiting for the grill
        readonly List<Customer> ready = new List<Customer>();
        int nextId = 1;
        float attendantTimer;
        Customer cookCurrent; float cookProgress, cookTotal;

        public int Served { get; private set; }
        public int Lost { get; private set; }
        public int DayRevenue { get; private set; }

        public IReadOnlyList<Customer> Queue => queue;
        public IReadOnlyList<Customer> Tickets => cooking;
        public IReadOnlyList<Customer> Ready => ready;
        public int QueueIndex(Customer c) => queue.IndexOf(c);
        public bool QueueFull => queue.Count >= MaxQueue;
        public Customer FrontOfQueue => queue.Count > 0 ? queue[0] : null;

        public StallService(IEventBus bus, StallModel stall, Ledger ledger, StaffRoster roster, Func<int> day)
        { this.bus = bus; this.stall = stall; this.ledger = ledger; this.roster = roster; this.day = day; }

        public void ResetDay() { Served = 0; Lost = 0; DayRevenue = 0; queue.Clear(); cooking.Clear(); ready.Clear(); cookCurrent = null; }

        /// <summary>A customer decided to buy and joins the queue. Returns null when the queue is full or nothing is in stock.</summary>
        public Customer Arrive(ProductDef product)
        {
            if (product == null) { Fail("esgotado"); return null; }
            if (QueueFull) { Fail("fila cheia"); return null; }
            float patience = BasePatience * stall.PatienceBonus;
            var c = new Customer { Id = nextId++, Product = product, State = CustomerState.Queued, Patience = patience, MaxPatience = patience };
            queue.Add(c);
            return c;
        }

        // ---- Verbs shared by the player and the staff ----

        public bool CanTakeOrder => queue.Count > 0;
        public bool TakeOrder()
        {
            if (queue.Count == 0) return false;
            var c = queue[0]; queue.RemoveAt(0);
            c.State = CustomerState.WaitingFood;
            cooking.Add(c);
            return true;
        }

        public bool CanHandOver => ready.Count > 0;
        public Customer HandOver()
        {
            if (ready.Count == 0) return null;
            var c = ready[0]; ready.RemoveAt(0);
            int price = stall.Price(c.Product.Id);
            int tip = c.Satisfaction > 0.6f ? (int)Math.Round(price * 0.15f * (c.Satisfaction - 0.4f) / 0.6f) : 0;
            c.Paid = price; c.Tip = tip; c.State = CustomerState.Served;
            ledger.Add(day(), "vendas", price + tip);
            DayRevenue += price + tip;
            Served++;
            stall.Reputation = Math.Min(stall.ReputationCap, stall.Reputation + (0.0008f + 0.0025f * (c.Satisfaction - 0.4f)) * (stall.Has("up.mesas") ? 1.5f : 1f));
            bus.Publish(new CustomerServed(c.Product.Id, price, tip));
            return c;
        }

        /// <summary>Grill side: the next ticket nobody is cooking, or null.</summary>
        public Customer NextTicket()
        {
            foreach (var t in cooking) if (!t.BeingCooked) return t;
            return null;
        }

        public float PrepareDuration(Customer c, float skill) => c.Product.PrepSeconds / (0.5f + skill) / stall.PrepSpeed;

        /// <summary>Marks a ticket as being cooked. Returns false when the product ran out meanwhile (the customer leaves).</summary>
        public bool BeginPrepare(Customer c)
        {
            if (c == null || c.BeingCooked || c.State != CustomerState.WaitingFood) return false;
            if (!stall.TryConsume(c.Product.Id)) { cooking.Remove(c); Leave(c, "esgotado"); return false; }
            c.BeingCooked = true;
            return true;
        }

        public void FinishPrepare(Customer c)
        {
            if (c == null || !cooking.Remove(c)) return;
            c.BeingCooked = false;
            c.State = CustomerState.Ready;
            ready.Add(c);
        }

        // ---- Simulation tick: patience and staff automation ----

        public void Tick(float dt)
        {
            Drain(queue, dt); Drain(cooking, dt); Drain(ready, dt);
            if (cookCurrent != null && cookCurrent.State == CustomerState.Left) cookCurrent = null;
            RunAttendant(dt);
            RunCook(dt);
        }

        void Drain(List<Customer> list, float dt)
        {
            for (int i = list.Count - 1; i >= 0; i--)
            {
                var c = list[i];
                c.Patience -= dt;
                if (c.Patience <= 0f) { list.RemoveAt(i); Leave(c, "demora"); }
            }
        }

        void Leave(Customer c, string reason)
        {
            c.State = CustomerState.Left;
            Fail(reason);
            stall.Reputation = Math.Max(0f, stall.Reputation - (reason == "demora" ? 0.004f : 0.0015f));
        }

        void Fail(string reason) { Lost++; bus.Publish(new CustomerLost(reason)); }

        void RunAttendant(float dt)
        {
            var a = roster.Best(StaffRole.Atendente);
            if (a == null) return;
            attendantTimer -= dt;
            if (attendantTimer > 0f) return;
            if (ready.Count > 0) { HandOver(); attendantTimer = 2.2f / (0.5f + a.skill); }
            else if (queue.Count > 0) { TakeOrder(); attendantTimer = 2.8f / (0.5f + a.skill); }
        }

        void RunCook(float dt)
        {
            var cook = roster.Best(StaffRole.Cozinheiro);
            if (cook == null) return;
            if (cookCurrent == null)
            {
                var t = NextTicket();
                if (t == null || !BeginPrepare(t)) return;
                cookCurrent = t; cookProgress = 0f; cookTotal = PrepareDuration(t, cook.skill);
            }
            cookProgress += dt;
            if (cookProgress >= cookTotal) { FinishPrepare(cookCurrent); cookCurrent = null; }
        }
    }
}
