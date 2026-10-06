using System;
using System.Collections.Generic;
using ResortAurora.Core;

namespace ResortAurora.Sim
{
    public enum RoomState { Vacant, Occupied, Dirty }

    [Serializable]
    public sealed class Room
    {
        public int id;
        public int quality;          // 0 Simples, 1 Conforto, 2 Superior, 3 Suite
        public int price;            // per night
        public RoomState state;
        public string guestName, guestProfile;
        public int nightsLeft;
        public float guestSatisfaction;
    }

    [Serializable]
    public sealed class Review
    {
        public int day, stars;
        public string guest, text;
    }

    public sealed class GuestProfile
    {
        public string Id, Name; public int Budget, Expect, MinNights, MaxNights;
        public string[] Names;
    }

    public readonly struct GuestCheckedIn : IGameEvent
    {
        public readonly int RoomId; public readonly string Guest;
        public GuestCheckedIn(int roomId, string guest) { RoomId = roomId; Guest = guest; }
    }

    public readonly struct ReviewPosted : IGameEvent
    {
        public readonly int Stars; public readonly string Guest;
        public ReviewPosted(int stars, string guest) { Stars = stars; Guest = guest; }
    }

    public sealed class NightReport
    {
        public int arrivals, checkedIn, turnedAway, checkedOut, revenue, laundry, cleanedByStaff, dirtyLeft, occupied;
        public readonly List<Review> reviews = new List<Review>();
    }

    /// <summary>
    /// The pousada's lodging business (stage 3): rooms with quality and price, nightly arrivals by profile, check-out reviews, housekeeping.
    /// Runs once per day at close of business. Pure data and rules, no Unity types, deterministic for a given Random.
    /// </summary>
    public sealed class LodgingModel
    {
        public static readonly string[] QualityNames = { "Simples", "Conforto", "Superior", "Suíte" };
        public static readonly int[] SuggestedPrice = { 55, 90, 140, 220 };
        public static readonly int[] UpgradeCost = { 0, 450, 900, 1700 };    // cost to reach quality i
        public const int RoomsPerPousada = 6;

        public static readonly GuestProfile[] Profiles =
        {
            new GuestProfile { Id = "mochileiro", Name = "Mochileiro", Budget = 70, Expect = 0, MinNights = 1, MaxNights = 3,
                Names = new[] { "Caio", "Bia", "Theo", "Lia", "Davi", "Nina" } },
            new GuestProfile { Id = "casal", Name = "Casal", Budget = 130, Expect = 1, MinNights = 2, MaxNights = 3,
                Names = new[] { "Ana e Rui", "Lara e Beto", "Clara e Nuno", "Rita e Gil" } },
            new GuestProfile { Id = "familia", Name = "Família", Budget = 190, Expect = 2, MinNights = 3, MaxNights = 4,
                Names = new[] { "Família Souza", "Família Lima", "Família Prado", "Família Reis" } },
        };

        readonly IEventBus bus;
        readonly List<Room> rooms = new List<Room>();
        readonly List<Review> reviews = new List<Review>();
        public IReadOnlyList<Room> Rooms => rooms;
        public IReadOnlyList<Review> Reviews => reviews;
        public bool Unlocked => rooms.Count > 0;
        public int TotalGuests { get; set; }

        public LodgingModel(IEventBus bus) { this.bus = bus; }

        public void Unlock()
        {
            if (Unlocked) return;
            for (int i = 0; i < RoomsPerPousada; i++)
                rooms.Add(new Room { id = i + 1, quality = 0, price = SuggestedPrice[0], state = RoomState.Vacant });
        }

        public void Restore(IEnumerable<Room> r, IEnumerable<Review> rv, int totalGuests)
        {
            rooms.Clear(); rooms.AddRange(r);
            reviews.Clear(); reviews.AddRange(rv);
            TotalGuests = totalGuests;
        }

        public void SetPrice(int roomId, int price)
        {
            var r = rooms.Find(x => x.id == roomId);
            if (r != null) r.price = Math.Max(10, Math.Min(price, 500));
        }

        public bool Upgrade(int roomId, Ledger ledger, int day)
        {
            var r = rooms.Find(x => x.id == roomId);
            if (r == null || r.state == RoomState.Occupied || r.quality >= 3) return false;
            int cost = UpgradeCost[r.quality + 1];
            if (!ledger.TrySpend(day, "reforma de quarto", cost)) return false;
            r.quality++;
            if (r.price < SuggestedPrice[r.quality] * 0.8f) r.price = SuggestedPrice[r.quality];
            return true;
        }

        /// <summary>The player makes the bed: a dirty room becomes vacant. Free, but it uses the player's time (the panel closes the clock for it).</summary>
        public bool Clean(int roomId)
        {
            var r = rooms.Find(x => x.id == roomId);
            if (r == null || r.state != RoomState.Dirty) return false;
            r.state = RoomState.Vacant;
            return true;
        }

        public int VacantCount() => rooms.FindAll(r => r.state == RoomState.Vacant).Count;
        public int OccupiedCount() => rooms.FindAll(r => r.state == RoomState.Occupied).Count;
        public int DirtyCount() => rooms.FindAll(r => r.state == RoomState.Dirty).Count;
        public float AverageStars(int lastN = 20)
        {
            if (reviews.Count == 0) return 0f;
            int n = Math.Min(lastN, reviews.Count); float sum = 0f;
            for (int i = reviews.Count - n; i < reviews.Count; i++) sum += reviews[i].stars;
            return sum / n;
        }

        // ------------------------------------------------------------------------------------------ the night

        /// <summary>Close of business: guests check out (reviews), rooms are cleaned by housekeeping, new guests arrive and pay for the night.</summary>
        public NightReport RunNight(int day, StallModel stall, StaffRoster roster, Ledger ledger, Weather weather, Random rng)
        {
            var rep = new NightReport();
            if (!Unlocked) return rep;

            // 1. check-out: guests whose stay ends leave a review
            foreach (var r in rooms)
            {
                if (r.state != RoomState.Occupied) continue;
                if (--r.nightsLeft > 0) continue;
                var review = MakeReview(day, r, rng);
                reviews.Add(review); rep.reviews.Add(review);
                if (reviews.Count > 60) reviews.RemoveAt(0);
                stall.Reputation = Math.Max(0f, Math.Min(stall.ReputationCap, stall.Reputation + (review.stars - 3) * 0.006f));
                r.state = RoomState.Dirty; r.guestName = null; r.guestProfile = null;
                rep.checkedOut++;
                rep.laundry += 6;
                bus.Publish(new ReviewPosted(review.stars, review.guest));
            }
            if (rep.laundry > 0) ledger.Add(day, "lavanderia", -rep.laundry);

            // 2. housekeeping: each maid cleans up to 4 rooms a day (skill raises it); the rest stays dirty until the player cleans them
            int capacity = 0;
            foreach (var s in roster.Hired) if (s.role == StaffRole.Camareira) capacity += 3 + (int)Math.Round(s.skill * 3f);
            foreach (var r in rooms)
            {
                if (r.state != RoomState.Dirty) continue;
                if (capacity > 0) { r.state = RoomState.Vacant; capacity--; rep.cleanedByStaff++; }
            }

            // 3. arrivals: demand grows with reputation, good weather and a decent average price
            float rating = AverageStars() <= 0f ? 3.2f : AverageStars();
            float weatherF = weather == Weather.Cloudy ? 0.7f : weather == Weather.Windy ? 0.85f : 1.1f;
            float receptionBonus = roster.Has(StaffRole.Recepcionista) ? 1.15f : 1f;
            float expected = (1.2f + 4.5f * stall.Reputation) * (0.7f + 0.15f * rating) * weatherF * receptionBonus;
            int arrivals = (int)Math.Floor(expected + rng.NextDouble());
            rep.arrivals = arrivals;
            for (int a = 0; a < arrivals; a++)
            {
                var p = Profiles[PickProfile(rng, stall.Reputation)];
                // best fit: the cheapest vacant room that meets the guest's expectation and budget
                Room pick = null;
                foreach (var r in rooms)
                {
                    if (r.state != RoomState.Vacant || r.quality < p.Expect || r.price > p.Budget) continue;
                    if (pick == null || r.price < pick.price) pick = r;
                }
                if (pick == null)
                {                                                                  // second chance: any room within budget, even below expectation
                    foreach (var r in rooms)
                        if (r.state == RoomState.Vacant && r.price <= p.Budget && (pick == null || r.quality > pick.quality)) pick = r;
                }
                if (pick == null) { rep.turnedAway++; continue; }
                pick.state = RoomState.Occupied;
                pick.guestName = p.Names[rng.Next(p.Names.Length)];
                pick.guestProfile = p.Id;
                pick.nightsLeft = p.MinNights + rng.Next(p.MaxNights - p.MinNights + 1);
                rep.checkedIn++;
                TotalGuests++;
                bus.Publish(new GuestCheckedIn(pick.id, pick.guestName));
            }

            // 4. the night is paid: every occupied room (including those who just arrived) brings its price
            foreach (var r in rooms)
                if (r.state == RoomState.Occupied) { rep.revenue += r.price; rep.occupied++; }
            if (rep.revenue > 0) ledger.Add(day, "hospedagem", rep.revenue);
            rep.dirtyLeft = DirtyCount();
            return rep;
        }

        static int PickProfile(Random rng, float reputation)
        {
            // better reputation attracts couples and families
            double v = rng.NextDouble();
            double families = 0.05 + 0.35 * reputation, couples = 0.25 + 0.3 * reputation;
            return v < families ? 2 : v < families + couples ? 1 : 0;
        }

        Review MakeReview(int day, Room r, Random rng)
        {
            var p = Array.Find(Profiles, x => x.Id == r.guestProfile) ?? Profiles[0];
            // value for money: price against what the guest expected to pay for the quality it got
            float fair = SuggestedPrice[Math.Min(3, r.quality)];
            float valueScore = Math.Max(-1.2f, Math.Min(1.0f, (fair - r.price) / (fair * 0.4f)));
            float qualityScore = (r.quality - p.Expect) * 0.7f;
            float noise = (float)(rng.NextDouble() - 0.5) * 0.8f;
            int stars = (int)Math.Round(Math.Max(1.0, Math.Min(5.0, 3.6 + qualityScore + valueScore * 0.7 + noise)));
            string text = stars >= 5 ? "Perfeito! Voltaremos." : stars == 4 ? "Muito bom, quarto agradável." : stars == 3 ? "Ok, nada de especial."
                : stars == 2 ? (valueScore < -0.4f ? "Achamos caro para o que oferece." : "Quarto abaixo do esperado.") : "Decepcionante. Não recomendo.";
            return new Review { day = day, stars = stars, guest = r.guestName ?? "Hóspede", text = text };
        }
    }
}
