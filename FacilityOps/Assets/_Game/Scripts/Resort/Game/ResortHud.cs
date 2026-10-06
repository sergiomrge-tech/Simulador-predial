using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Provisional IMGUI interface: status bar, prompts, market, hiring, end-of-day and help panels. Deliberately thin: all rules live in Sim,
    /// so this can be replaced by UI Toolkit without touching gameplay.
    /// </summary>
    public sealed class ResortHud : MonoBehaviour
    {
        [SerializeField] ResortGame game;
        [SerializeField] PlayerController player;
        GUIStyle label, big, small, button, box, centered;
        Vector2 scroll;
        int lastW, lastH;

        void Styles()
        {
            if (label != null && lastH == Screen.height) return;
            lastH = Screen.height; lastW = Screen.width;
            int s = Mathf.Max(14, Screen.height / 45);
            label = new GUIStyle(GUI.skin.label) { fontSize = s, normal = { textColor = Color.white } };
            big = new GUIStyle(label) { fontSize = Mathf.RoundToInt(s * 1.5f), fontStyle = FontStyle.Bold };
            small = new GUIStyle(label) { fontSize = Mathf.Max(11, Mathf.RoundToInt(s * 0.8f)), normal = { textColor = new Color(0.85f, 0.85f, 0.85f) }, wordWrap = true };
            centered = new GUIStyle(label) { alignment = TextAnchor.MiddleCenter };
            button = new GUIStyle(GUI.skin.button) { fontSize = s };
            box = new GUIStyle(GUI.skin.box) { fontSize = s };
        }

        void OnGUI()
        {
            if (game == null || game.Clock == null) return;
            Styles();
            DrawStatus();
            DrawPrompt();
            DrawTickets();
            switch (game.OpenedPanel)
            {
                case Panel.Market: DrawMarket(); break;
                case Panel.Hire: DrawHire(); break;
                case Panel.Summary: DrawSummary(); break;
                case Panel.Help: DrawHelp(); break;
                case Panel.Parcels: DrawParcels(); break;
                case Panel.Lodging: DrawLodging(); break;
            }
            if (game.ToastActive) GUI.Label(new Rect(0, Screen.height * 0.12f, Screen.width, 40), game.Toast, centered);
        }

        // ---- always-on elements ----

        void DrawStatus()
        {
            float h = lastH / 14f;
            GUI.Box(new Rect(8, 8, Screen.width - 16, h), GUIContent.none);
            var c = game.Clock;
            string s = $"Dia {c.Day}   {GameClock.Format(c.Minutes)}   {WeatherInfo.Label(game.Weather)}      R$ {game.Ledger.Balance}      Reputação {Mathf.RoundToInt(game.Stall.Reputation * 100)}%      Atendidos hoje {game.Service.Served}   Perdidos {game.Service.Lost}";
            GUI.Label(new Rect(20, 8 + h * 0.15f, Screen.width - 40, h), s, label);
        }

        void DrawPrompt()
        {
            var t = player.Target;
            if (t != null && t.CanUse(game) && game.OpenedPanel == Panel.None)
            {
                GUI.Label(new Rect(0, Screen.height * 0.58f, Screen.width, 40), t.Prompt(game), centered);
                if (player.HoldProgress > 0f)
                {
                    float w = Screen.width * 0.2f;
                    GUI.Box(new Rect(Screen.width / 2f - w / 2f, Screen.height * 0.63f, w, 14), GUIContent.none);
                    GUI.DrawTexture(new Rect(Screen.width / 2f - w / 2f + 2, Screen.height * 0.63f + 2, (w - 4) * player.HoldProgress, 10), Texture2D.whiteTexture);
                }
            }
            else if (t != null && game.OpenedPanel == Panel.None) GUI.Label(new Rect(0, Screen.height * 0.58f, Screen.width, 40), t.Prompt(game), centered);
            GUI.Label(new Rect(Screen.width / 2f - 6, Screen.height / 2f - 12, 20, 24), "·", label);
        }

        void DrawTickets()
        {
            var sv = game.Service;
            string txt = $"Fila {sv.Queue.Count}/{StallService.MaxQueue}   Na chapa {sv.Tickets.Count}   Prontos {sv.Ready.Count}      [F1] ajuda";
            GUI.Label(new Rect(20, Screen.height - Screen.height / 14f, Screen.width - 40, 40), txt, label);
        }

        // ---- panels ----

        Rect PanelRect() => new Rect(Screen.width * 0.12f, Screen.height * 0.16f, Screen.width * 0.76f, Screen.height * 0.72f);

        bool Begin(string title)
        {
            var r = PanelRect();
            GUI.Box(r, GUIContent.none); GUI.Box(r, GUIContent.none);
            GUI.Label(new Rect(r.x + 20, r.y + 10, r.width - 40, 50), title, big);
            GUI.Label(new Rect(r.x + r.width - 280, r.y + 14, 260, 40), "R$ " + game.Ledger.Balance, big);
            if (game.OpenedPanel != Panel.Summary && GUI.Button(new Rect(r.xMax - 150, r.yMax - 56, 130, 44), "Fechar (Esc)", button)) { game.ClosePanel(); return false; }
            return true;
        }

        void DrawMarket()
        {
            if (!Begin("Caixa do fornecedor")) return;
            var r = PanelRect(); float y = r.y + 64, row = lastH / 24f;
            GUI.Label(new Rect(r.x + 20, y, 400, row), "Produto", small); GUI.Label(new Rect(r.x + r.width * 0.30f, y, 200, row), "Estoque", small);
            GUI.Label(new Rect(r.x + r.width * 0.42f, y, 200, row), "Custo", small); GUI.Label(new Rect(r.x + r.width * 0.52f, y, 300, row), "Preço de venda", small);
            y += row;
            foreach (var p in Catalog.Products)
            {
                GUI.Label(new Rect(r.x + 20, y, 400, row), p.Name, label);
                GUI.Label(new Rect(r.x + r.width * 0.30f, y, 200, row), game.Stall.Stock(p.Id).ToString(), label);
                GUI.Label(new Rect(r.x + r.width * 0.42f, y, 200, row), "R$ " + p.UnitCost, label);
                if (GUI.Button(new Rect(r.x + r.width * 0.52f, y, row, row), "-", button)) game.Stall.SetPrice(p.Id, game.Stall.Price(p.Id) - 1);
                GUI.Label(new Rect(r.x + r.width * 0.52f + row + 6, y, 100, row), "R$ " + game.Stall.Price(p.Id), label);
                if (GUI.Button(new Rect(r.x + r.width * 0.52f + row + 90, y, row, row), "+", button)) game.Stall.SetPrice(p.Id, game.Stall.Price(p.Id) + 1);
                if (GUI.Button(new Rect(r.x + r.width * 0.72f, y, r.width * 0.12f, row), "+10", button)) Buy(p, 10);
                if (GUI.Button(new Rect(r.x + r.width * 0.85f, y, r.width * 0.12f, row), "+30", button)) Buy(p, 30);
                y += row * 1.08f;
            }
            y += row * 0.3f;
            GUI.Label(new Rect(r.x + 20, y, 600, row * 1.3f), "Melhorias", big); y += row * 1.4f;
            foreach (var u in StallModel.Upgrades)
            {
                bool owned = game.Stall.Has(u.Id);
                GUI.Label(new Rect(r.x + 20, y, r.width * 0.25f, row), u.Name, label);
                GUI.Label(new Rect(r.x + r.width * 0.26f, y, r.width * 0.5f, row * 1.6f), u.Description, small);
                GUI.enabled = !owned;
                if (GUI.Button(new Rect(r.x + r.width * 0.78f, y, r.width * 0.19f, row), owned ? "Comprado" : $"Comprar R$ {u.Cost}", button))
                    game.Say(game.Stall.BuyUpgrade(u.Id, game.Ledger, game.Clock.Day) ? u.Name + " instalado!" : "Dinheiro insuficiente.");
                GUI.enabled = true;
                y += row * 1.18f;
            }
        }

        void Buy(ProductDef p, int qty)
        {
            int got = game.Stall.Buy(p.Id, qty, game.Ledger, game.Clock.Day);
            game.Say(got > 0 ? $"+{got} {p.Name}" : "Sem dinheiro ou estoque cheio.");
        }

        void DrawHire()
        {
            if (!Begin("Mural de vagas")) return;
            var r = PanelRect(); float y = r.y + 70, row = lastH / 14f;
            GUI.Label(new Rect(r.x + 20, y, r.width - 40, row), $"Equipe {game.Roster.Hired.Count}/{game.Roster.Capacity}   Folha por dia: R$ {game.Roster.DailyPayroll()}   (contratar custa uma diária)", label);
            y += row * 1.2f;
            GUI.Label(new Rect(r.x + 20, y, 400, row), "Na equipe", big); y += row * 1.1f;
            if (game.Roster.Hired.Count == 0) { GUI.Label(new Rect(r.x + 20, y, 600, row), "Ninguém ainda. Você está sozinho na barraca.", small); y += row; }
            foreach (var s in new System.Collections.Generic.List<StaffMember>(game.Roster.Hired))
            {
                GUI.Label(new Rect(r.x + 20, y, r.width * 0.6f, row), $"{s.name} — {s.role}  habilidade {Stars(s.skill)}  R$ {s.wage}/dia", label);
                if (GUI.Button(new Rect(r.x + r.width * 0.78f, y, r.width * 0.19f, row), "Dispensar", button)) game.Roster.Fire(s.id);
                y += row * 1.1f;
            }
            y += row * 0.4f;
            GUI.Label(new Rect(r.x + 20, y, 400, row), "Candidatos", big); y += row * 1.1f;
            foreach (var s in new System.Collections.Generic.List<StaffMember>(game.Roster.Candidates))
            {
                GUI.Label(new Rect(r.x + 20, y, r.width * 0.58f, row), $"{s.name} — {s.role}  habilidade {Stars(s.skill)}  R$ {s.wage}/dia", label);
                GUI.Label(new Rect(r.x + 20, y + row * 0.85f, r.width * 0.7f, row), s.bio, small);
                GUI.enabled = !game.Roster.IsFull && game.Ledger.CanAfford(s.wage);
                if (GUI.Button(new Rect(r.x + r.width * 0.78f, y, r.width * 0.19f, row), "Contratar", button))
                {
                    bool ok = game.Roster.Hire(s.id, game.Ledger, game.Clock.Day);
                    game.Say(ok ? s.name + " começou a trabalhar!" : "Não foi possível contratar.");
                }
                GUI.enabled = true;
                y += row * 1.9f;
            }
            if (game.Roster.IsFull) GUI.Label(new Rect(r.x + 20, r.yMax - 100, r.width * 0.6f, row), "A barraca só comporta " + game.Roster.Capacity + " ajudantes. Evolua para um quiosque!", small);
        }

        static string Stars(float skill) { int n = Mathf.Clamp(Mathf.RoundToInt(skill * 5f), 1, 5); return new string('★', n) + new string('☆', 5 - n); }

        void DrawSummary()
        {
            var d = game.LastSummary; if (d == null) return;
            if (!Begin($"Fim do dia {d.day}")) return;
            var r = PanelRect(); float y = r.y + 80, row = lastH / 15f;
            string[] lines =
            {
                $"Clima: {WeatherInfo.Label(d.weather)}",
                $"Clientes atendidos: {d.served}      perdidos: {d.lost}",
                $"Receita do dia: R$ {d.revenue}",
                $"Despesas do dia: R$ {d.expenses}   (equipe R$ {d.payroll})",
                $"Resultado: R$ {d.revenue - d.expenses}",
                d.melted > 0 ? $"Picolés derretidos: {d.melted} (um freezer evitaria isso)" : "Nada estragou.",
                $"Reputação: {Mathf.RoundToInt(d.reputation * 100)}% (barraca vai até {Mathf.RoundToInt(game.Stall.ReputationCap * 100)}%)",
                $"Saldo: R$ {d.balance}",
            };
            if (d.lodging != null && game.Lodging.Unlocked)
                lines = new System.Collections.Generic.List<string>(lines)
                {
                    $"Pousada: {d.lodging.occupied} quartos ocupados, {d.lodging.checkedIn} chegadas, {d.lodging.turnedAway} sem vaga, {d.lodging.checkedOut} saídas, {d.lodging.dirtyLeft} sujos",
                    d.lodging.reviews.Count > 0 ? $"Última avaliação: {d.lodging.reviews[d.lodging.reviews.Count - 1].stars}★ — {d.lodging.reviews[d.lodging.reviews.Count - 1].text}" : "Sem novas avaliações.",
                }.ToArray();
            foreach (var l in lines) { GUI.Label(new Rect(r.x + 30, y, r.width - 60, row), l, label); y += row; }
            if (GUI.Button(new Rect(r.x + 30, r.yMax - 70, r.width * 0.4f, 50), "Salvo. Voltar para casa e dormir", button)) game.GoHome();
        }

        void DrawLodging()
        {
            if (!Begin("Pousada do Seu Tonico")) return;
            var l = game.Lodging;
            var r = PanelRect(); float y = r.y + 70, row = lastH / 17f;
            GUI.Label(new Rect(r.x + 20, y, r.width - 40, row),
                $"Ocupados {l.OccupiedCount()}/{l.Rooms.Count}   Sujos {l.DirtyCount()}   Livres {l.VacantCount()}   Nota média {(l.AverageStars() > 0 ? l.AverageStars().ToString("0.0") + " ★" : "—")}   Hóspedes no total {l.TotalGuests}", label);
            y += row * 1.3f;
            foreach (var room in l.Rooms)
            {
                string st = room.state == RoomState.Occupied ? $"{room.guestName} ({room.nightsLeft}n)" : room.state == RoomState.Dirty ? "SUJO" : "livre";
                GUI.Label(new Rect(r.x + 20, y, r.width * 0.30f, row), $"Quarto {room.id}  {LodgingModel.QualityNames[room.quality]}", label);
                GUI.Label(new Rect(r.x + r.width * 0.30f, y, r.width * 0.18f, row), st, label);
                if (GUI.Button(new Rect(r.x + r.width * 0.49f, y, row, row), "-", button)) l.SetPrice(room.id, room.price - 5);
                GUI.Label(new Rect(r.x + r.width * 0.49f + row + 4, y, 90, row), "R$ " + room.price, label);
                if (GUI.Button(new Rect(r.x + r.width * 0.49f + row + 80, y, row, row), "+", button)) l.SetPrice(room.id, room.price + 5);
                if (room.state == RoomState.Dirty && GUI.Button(new Rect(r.x + r.width * 0.68f, y, r.width * 0.12f, row), "Arrumar", button))
                { l.Clean(room.id); game.Clock.Skip(15f); }
                bool canUp = room.quality < 3 && room.state != RoomState.Occupied;
                GUI.enabled = canUp;
                if (room.quality < 3 && GUI.Button(new Rect(r.x + r.width * 0.81f, y, r.width * 0.17f, row), $"Reformar R$ {LodgingModel.UpgradeCost[room.quality + 1]}", button))
                    game.Say(l.Upgrade(room.id, game.Ledger, game.Clock.Day) ? "Quarto reformado!" : "Dinheiro insuficiente.");
                GUI.enabled = true;
                y += row * 1.2f;
            }
            y += row * 0.5f;
            GUI.Label(new Rect(r.x + 20, y, r.width * 0.9f, row), "Avaliações recentes", big); y += row * 1.4f;
            for (int i = l.Reviews.Count - 1, n = 0; i >= 0 && n < 4; i--, n++)
            {
                var rv = l.Reviews[i];
                GUI.Label(new Rect(r.x + 30, y, r.width * 0.9f, row), $"{new string('★', rv.stars)}{new string('☆', 5 - rv.stars)}  {rv.guest}: {rv.text}", small); y += row;
            }
            GUI.Label(new Rect(r.x + 20, r.yMax - 100, r.width * 0.7f, row * 2f), "Hóspedes chegam ao fechar o dia. Camareiras limpam 3 a 6 quartos por dia; o resto fica com você (cada quarto custa 15 min). Preço justo + qualidade = boas notas.", small);
        }

        void DrawParcels()
        {
            if (!Begin("Terrenos do bairro")) return;
            var r = PanelRect(); float y = r.y + 70, row = lastH / 15f;
            foreach (var info in game.Parcels.All)
            {
                var status = game.Parcels.StatusOf(info.Id, game.Stall.Reputation);
                string tag = status == ParcelStatus.Owned ? "SEU" : status == ParcelStatus.Available ? "À VENDA" : "BLOQUEADO";
                GUI.Label(new Rect(r.x + 20, y, r.width * 0.45f, row), info.Id + "  " + info.Name, label);
                GUI.Label(new Rect(r.x + r.width * 0.46f, y, r.width * 0.15f, row), tag, label);
                GUI.Label(new Rect(r.x + r.width * 0.60f, y, r.width * 0.15f, row), info.Price > 0 ? "R$ " + info.Price : "", label);
                if (status == ParcelStatus.Available)
                {
                    GUI.enabled = game.Ledger.CanAfford(info.Price);
                    if (GUI.Button(new Rect(r.x + r.width * 0.77f, y, r.width * 0.2f, row), "Comprar", button))
                        game.Say(game.Parcels.Buy(info.Id, game.Ledger, game.Clock.Day, game.Stall.Reputation) ? info.Name + " é seu!" : "Não foi possível comprar.");
                    GUI.enabled = true;
                }
                string why = status == ParcelStatus.Locked ? game.Parcels.Requirement(info.Id, game.Stall.Reputation) : info.Note;
                GUI.Label(new Rect(r.x + 40, y + row * 0.8f, r.width * 0.9f, row), why, small);
                y += row * 1.55f;
            }
        }

        void DrawHelp()
        {
            if (!Begin("Como jogar")) return;
            var r = PanelRect();
            GUI.Label(new Rect(r.x + 30, r.y + 80, r.width - 60, r.height - 140),
                "WASD andar   Shift correr   Mouse olhar   E usar   F1 ajuda\n\n" +
                "1. Na caixa do fornecedor, compre estoque e ajuste os preços.\n" +
                "2. Clientes formam fila na frente do balcão. No balcão, [E] anota o pedido.\n" +
                "3. Na chapa, SEGURE [E] até terminar de preparar.\n" +
                "4. De volta ao balcão, [E] entrega e recebe. Rápido = gorjeta e reputação.\n" +
                "5. No mural de vagas você contrata ajudantes: o atendente cuida do balcão, o cozinheiro da chapa.\n" +
                "6. Ao fim do dia o jogo salva. Junte dinheiro para melhorar a barraca e chegar ao quiosque.", label);
        }
    }
}
