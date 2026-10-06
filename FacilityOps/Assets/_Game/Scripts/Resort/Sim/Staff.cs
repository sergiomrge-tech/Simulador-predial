using System;
using System.Collections.Generic;
using ResortAurora.Core;

namespace ResortAurora.Sim
{
    public enum StaffRole { Atendente, Cozinheiro }

    [Serializable]
    public sealed class StaffMember
    {
        public string id, name, bio;
        public StaffRole role;
        public float skill;       // 0..1, speeds up work and lowers mistakes
        public int wage;          // per day
        public float morale = 0.8f;
    }

    /// <summary>People who can be hired and the ones already working. The candidate pool is deterministic per game so reloads show the same people.</summary>
    public sealed class StaffRoster
    {
        readonly IEventBus bus;
        readonly List<StaffMember> hired = new List<StaffMember>();
        readonly List<StaffMember> pool = new List<StaffMember>();
        public IReadOnlyList<StaffMember> Hired => hired;
        public IReadOnlyList<StaffMember> Candidates => pool;
        /// <summary>The stall only has room for this many helpers (grows with each stage).</summary>
        public int Capacity { get; set; } = 2;

        public StaffRoster(IEventBus bus)
        {
            this.bus = bus;
            // Marisa is the lore's first employee (LORE_RESORT_AURORA.md): great on the grill, asks for a fair wage.
            pool.Add(new StaffMember { id = "staff.marisa", name = "Marisa Campos", role = StaffRole.Cozinheiro, skill = 0.75f, wage = 70,
                bio = "Jovem da vila, ótima na chapa. Sonha em ser chef." });
            pool.Add(new StaffMember { id = "staff.dudu", name = "Dudu Ferraz", role = StaffRole.Atendente, skill = 0.55f, wage = 45,
                bio = "Salva-vidas nas horas vagas. Simpático e rápido no troco." });
            pool.Add(new StaffMember { id = "staff.nina", name = "Nina Prado", role = StaffRole.Atendente, skill = 0.8f, wage = 75,
                bio = "Ex-caixa de supermercado. Não erra uma conta." });
            pool.Add(new StaffMember { id = "staff.beto", name = "Beto Lima", role = StaffRole.Cozinheiro, skill = 0.4f, wage = 35,
                bio = "Aprendiz animado, ainda queima uns pastéis." });
            pool.Add(new StaffMember { id = "staff.vera", name = "Dona Vera", role = StaffRole.Cozinheiro, skill = 0.9f, wage = 95,
                bio = "Quarenta anos de fogão. Cara, mas faz milagre." });
        }

        public bool IsFull => hired.Count >= Capacity;
        public bool Has(StaffRole role) => hired.Exists(s => s.role == role);
        public StaffMember Best(StaffRole role)
        {
            StaffMember best = null;
            foreach (var s in hired) if (s.role == role && (best == null || s.skill > best.skill)) best = s;
            return best;
        }

        public bool Hire(string id, Ledger ledger, int day)
        {
            if (IsFull) return false;
            var c = pool.Find(p => p.id == id);
            if (c == null) return false;
            // Hiring fee equals one day of wages; there is no free labour.
            if (!ledger.TrySpend(day, "contratacao", c.wage)) return false;
            pool.Remove(c);
            hired.Add(c);
            bus.Publish(new StaffChanged());
            return true;
        }

        public void Fire(string id)
        {
            var s = hired.Find(h => h.id == id);
            if (s == null) return;
            hired.Remove(s);
            pool.Add(s);
            bus.Publish(new StaffChanged());
        }

        public int DailyPayroll() { int sum = 0; foreach (var s in hired) sum += s.wage; return sum; }

        public void Restore(IEnumerable<StaffMember> hiredList)
        {
            foreach (var h in hiredList)
            {
                pool.RemoveAll(p => p.id == h.id);
                hired.Add(h);
            }
        }
    }
}
