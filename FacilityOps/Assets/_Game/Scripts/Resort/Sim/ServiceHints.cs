using System.Collections.Generic;
using System.Text;

namespace ResortAurora.Sim
{
    /// <summary>Where the stall is in its day, as far as the player's next move is concerned (inputs of <see cref="ServiceHints.NextStep"/>).</summary>
    public struct ServiceSnapshot
    {
        public bool AwaitingSleep, Closing, Open, DayOver;
        public int TotalStock, Queue, TicketsToCook, Ready;
    }

    /// <summary>Plain-language hints for the HUD: what to do next and what is running low. Pure functions, no Unity types.</summary>
    public static class ServiceHints
    {
        public const int LowStockAt = 3;

        public static string NextStep(ServiceSnapshot s)
        {
            if (s.AwaitingSleep) return "Dia encerrado. Volte para casa (Apto 12) e durma na cama.";
            if (s.Closing) return s.Queue + s.TicketsToCook + s.Ready > 0 ? "Atenda os últimos clientes para fechar o caixa." : "Fechando o caixa...";
            if (!s.Open)
            {
                if (s.DayOver) return "O dia acabou. Fechando o caixa...";
                return s.TotalStock <= 0
                    ? "Sem estoque: compre na caixa do fornecedor e depois abra o quiosque na placa."
                    : "Abra o quiosque na placa verde do balcão.";
            }
            if (s.Ready > 0) return "Pedido pronto: entregue no balcão [E].";
            if (s.TicketsToCook > 0) return "Pedido na chapa: segure [E] na grelha para preparar.";
            if (s.Queue > 0) return "Cliente na fila: anote o pedido no balcão [E].";
            return s.TotalStock <= 0
                ? "Sem estoque! Reponha na caixa do fornecedor."
                : "Aguardando clientes. Confira geladeira, freezer e prateleira.";
        }

        /// <summary>"Água 2, Cerveja 0" for the products at or below <paramref name="threshold"/>, or an empty string when everything is stocked.</summary>
        public static string LowStock(StallModel stall, int threshold = LowStockAt)
        {
            var sb = new StringBuilder(); bool any = false;
            foreach (var p in Catalog.Products)
            {
                int n = stall.Stock(p.Id);
                if (n > threshold) continue;
                if (any) sb.Append(", ");
                sb.Append(p.Name).Append(' ').Append(n); any = true;
            }
            return sb.ToString();
        }

        public static int TotalStock(StallModel stall)
        {
            int total = 0;
            foreach (var p in Catalog.Products) total += stall.Stock(p.Id);
            return total;
        }

        /// <summary>Tickets nobody is cooking yet (the grill has work for the player).</summary>
        public static int TicketsToCook(IReadOnlyList<Customer> tickets)
        {
            int n = 0;
            foreach (var t in tickets) if (!t.BeingCooked) n++;
            return n;
        }
    }
}
