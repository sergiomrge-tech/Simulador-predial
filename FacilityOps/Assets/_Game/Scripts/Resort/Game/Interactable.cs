using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>Something the first-person player can use with E. Set <see cref="holdSeconds"/> above 0 for hold-to-work actions (grill).</summary>
    public abstract class Interactable : MonoBehaviour
    {
        public float holdSeconds;
        public abstract string Prompt(ResortGame game);
        public abstract bool CanUse(ResortGame game);
        /// <summary>Fires once for tap actions, or when the hold completes.</summary>
        public abstract void Use(ResortGame game);
        /// <summary>Hold actions: called when the hold starts. Return false to refuse.</summary>
        public virtual bool BeginHold(ResortGame game) => true;
        public virtual void CancelHold(ResortGame game) { }
        /// <summary>Real seconds the hold needs right now (skill and upgrades change it).</summary>
        public virtual float HoldDuration(ResortGame game) => holdSeconds;
    }

    public sealed class CounterStation : Interactable
    {
        public override bool CanUse(ResortGame g) => g.Service.CanHandOver || g.Service.CanTakeOrder;
        public override string Prompt(ResortGame g)
        {
            if (g.Service.CanHandOver) return "[E] Entregar pedido";
            if (g.Service.CanTakeOrder) return "[E] Anotar pedido: " + g.Service.FrontOfQueue.Product.Name;
            return "Balcão (sem clientes)";
        }
        public override void Use(ResortGame g)
        {
            if (g.Service.CanHandOver) g.Service.HandOver();
            else g.Service.TakeOrder();
        }
    }

    public sealed class GrillStation : Interactable
    {
        Sim.Customer working;
        public override bool CanUse(ResortGame g) => g.Service.NextTicket() != null;
        public override string Prompt(ResortGame g)
        {
            var t = g.Service.NextTicket();
            return t == null ? "Chapa (sem pedidos)" : "[segure E] Preparar: " + t.Product.Name;
        }
        public override bool BeginHold(ResortGame g)
        {
            var t = g.Service.NextTicket();
            if (t == null || !g.Service.BeginPrepare(t)) return false;
            working = t;
            return true;
        }
        public override float HoldDuration(ResortGame g) => working != null ? g.Service.PrepareDuration(working, 0.5f) : holdSeconds;
        public override void Use(ResortGame g) { g.Service.FinishPrepare(working); working = null; }
        public override void CancelHold(ResortGame g)
        {
            // Walking away from the grill puts the ticket back; the stock already used is lost, like a burnt pastel.
            if (working != null) working.BeingCooked = false;
            working = null;
        }
    }

    public sealed class ActionStation : Interactable
    {
        public System.Func<ResortGame, string> prompt; public System.Func<ResortGame, bool> canUse; public System.Action<ResortGame> action;
        public override bool CanUse(ResortGame g) => canUse == null || canUse(g);
        public override string Prompt(ResortGame g) => prompt(g);
        public override void Use(ResortGame g) => action(g);
    }

    public enum Panel { None, Market, Hire, Summary, Help, Parcels, Lodging }

    public sealed class PanelStation : Interactable
    {
        public Panel panel; public string label;
        public override bool CanUse(ResortGame g) => true;
        public override string Prompt(ResortGame g) => "[E] " + label;
        public override void Use(ResortGame g) => g.OpenPanel(panel);
    }
}
