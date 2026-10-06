using System.Collections.Generic;
using ResortAurora.Core;

namespace ResortAurora.Sim
{
    public enum ParcelStatus { Owned, Available, Locked }

    /// <summary>Static facts about a parcel (from the exported site data).</summary>
    public sealed class ParcelInfo
    {
        public string Id, Name, Note, LockTag;
        public int Price;
    }

    public readonly struct ParcelBought : IGameEvent
    {
        public readonly string Id;
        public ParcelBought(string id) { Id = id; }
    }

    /// <summary>
    /// Land ownership: the progression gate of the whole game. A parcel is Available when its requirements are met and Locked otherwise
    /// (the reason is always shown to the player, never a silent wall). Pure data, no Unity types.
    /// </summary>
    public sealed class ParcelBook
    {
        readonly IEventBus bus;
        readonly List<ParcelInfo> infos = new List<ParcelInfo>();
        readonly HashSet<string> owned = new HashSet<string>();
        /// <summary>Story/stage flags that unlock parcels ("story" = the deed, "stage" = a later stage). Set by progression systems.</summary>
        public readonly HashSet<string> Flags = new HashSet<string>();

        public ParcelBook(IEventBus bus) { this.bus = bus; }
        public IReadOnlyList<ParcelInfo> All => infos;
        public IEnumerable<string> Owned => owned;

        public void Add(ParcelInfo info, bool startsOwned) { infos.Add(info); if (startsOwned) owned.Add(info.Id); }
        public void Restore(IEnumerable<string> ownedIds) { foreach (var id in ownedIds) owned.Add(id); }
        public bool Owns(string id) => owned.Contains(id);

        /// <summary>Why a parcel cannot be bought yet (empty when it can).</summary>
        public string Requirement(string id, float reputation)
        {
            var info = infos.Find(p => p.Id == id);
            if (info == null) return "Terreno desconhecido.";
            if (!string.IsNullOrEmpty(info.LockTag) && !Flags.Contains(info.LockTag))
                return info.LockTag == "story" ? "Exige a escritura histórica (história)." : "Disponível em uma etapa futura.";
            switch (id)
            {
                case "P1": if (reputation < 0.45f) return "Reputação mínima de 45% para a concessão."; break;
                case "P2": if (!owned.Contains("P1")) return "Antes, obtenha a faixa do quiosque."; break;
                case "P3": if (!owned.Contains("P2")) return "Antes, compre o sobrado do Seu Tonico."; break;
                case "P5": if (!owned.Contains("P3")) return "Antes, expanda para o quarteirão vizinho."; break;
            }
            return "";
        }

        public ParcelStatus StatusOf(string id, float reputation) =>
            owned.Contains(id) ? ParcelStatus.Owned : Requirement(id, reputation).Length == 0 ? ParcelStatus.Available : ParcelStatus.Locked;

        public bool Buy(string id, Ledger ledger, int day, float reputation)
        {
            var info = infos.Find(p => p.Id == id);
            if (info == null || owned.Contains(id) || Requirement(id, reputation).Length > 0) return false;
            if (!ledger.TrySpend(day, "terreno", info.Price)) return false;
            owned.Add(id);
            bus.Publish(new ParcelBought(id));
            return true;
        }
    }
}
