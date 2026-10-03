using UnityEngine;

namespace FacilityOps
{
    public sealed class TabletUI : MonoBehaviour
    {
        public GameRuntime game;
        private GUIStyle heading, body, small, button, tab, title;
        private Texture2D pixel;
        private int page;
        private Vector2 scroll;
        private int selectedLocation;
        private int selectedDistrict;
        private readonly Color ink = new Color(.055f, .08f, .1f);
        private readonly Color panel = new Color(.10f, .14f, .17f);
        private readonly Color accent = new Color(1, .67f, .25f);
        private void Styles()
        {
            if (pixel != null) return;
            pixel = new Texture2D(1, 1); pixel.SetPixel(0, 0, Color.white); pixel.Apply();
            body = new GUIStyle(GUI.skin.label) { fontSize = 16, wordWrap = true, richText = false, normal = { textColor = new Color(.85f, .90f, .91f) } };
            small = new GUIStyle(body) { fontSize = 13 };
            heading = new GUIStyle(body) { fontSize = 24, fontStyle = FontStyle.Bold };
            title = new GUIStyle(heading) { fontSize = 36 };
            button = new GUIStyle(GUI.skin.button) { fontSize = 16, padding = new RectOffset(16, 16, 10, 10), normal = { textColor = Color.white } };
            tab = new GUIStyle(button) { fontSize = 14 };
        }
        private void Fill(Rect rect, Color color) { Color previous = GUI.color; GUI.color = color; GUI.DrawTexture(rect, pixel); GUI.color = previous; }
        private void Text(float x, float y, float w, float h, string text, GUIStyle style = null) { GUI.Label(new Rect(x, y, w, h), text, style ?? body); }
        private bool Button(float x, float y, float w, string text, bool enabled = true)
        {
            bool previous = GUI.enabled; GUI.enabled = enabled;
            bool clicked = GUI.Button(new Rect(x, y, w, 42), text, button); GUI.enabled = previous; return clicked;
        }
        private void OnGUI()
        {
            if (game == null || game.Session == null) return;
            Styles();
            GUI.matrix = Matrix4x4.TRS(Vector3.zero, Quaternion.identity, new Vector3(Screen.width / 1280f, Screen.height / 720f, 1));
            if (game.TabletOpen) Tablet(); else HUD();
            if (!string.IsNullOrEmpty(game.SaveError))
            {
                Fill(new Rect(20, 660, 1240, 42), new Color(.5f, .12f, .1f));
                Text(30, 665, 1220, 38, game.SaveError, small);
            }
        }
        private void HUD()
        {
            Fill(new Rect(24, 24, 450, 79), ink);
            Text(40, 34, 430, 27, game.PreviewLocation != null ? "PRÉVIA / " + game.PreviewLocation.name : game.AtOffice ? "OFICINA AURORA" : game.ServiceLocationName, body);
            Text(40, 69, 430, 27, game.PreviewLocation != null ? "Leia registros [E] • [TAB] Cidade / pavimentos" : game.AtOffice ? "Central de chamados na mesa • [TAB] tablet" : game.Session.IsAuthored ? "Inspecione, isole e confirme antes de substituir." : "As luzes do corredor do 4º andar apagaram.", small);
            Fill(new Rect(625, 359, 30, 2), Color.white); Fill(new Rect(639, 345, 2, 30), Color.white);
            string focus = game.Player.Focus?.GetPrompt(game.Tool);
            if (focus != null)
            {
                Fill(new Rect(340, 435, 600, 46), ink); Text(359, 445, 566, 32, focus);
            }
            Fill(new Rect(24, 622, 650, 72), ink);
            Text(40, 632, 620, 25, ((int)game.Tool + 1) + "  /  " + game.ToolName);
            Text(40, 667, 620, 24, "WASD mover  •  E usar  •  1–5 ferramentas  •  6 isolar  •  7 restaurar  •  TAB", small);
            if (game.ShowNotice)
            {
                Fill(new Rect(340, 506, 600, 96), panel); Text(358, 520, 566, 76, game.Notice);
            }
        }
        private void Tablet()
        {
            Fill(new Rect(0, 0, 1280, 720), new Color(.02f, .035f, .045f, .85f));
            Fill(new Rect(80, 45, 1120, 630), ink);
            Fill(new Rect(80, 45, 7, 630), accent);
            Text(112, 69, 500, 49, "FACILITY / OPS", title);
            Text(114, 117, 500, 30, "OFICINA AURORA   /   CENTRAL OPERACIONAL", small);
            Text(755, 78, 410, 30, "R$ " + game.Session.Career.money + "    •    REP " + game.Session.Career.reputation + "/100", heading);
            Text(757, 116, 400, 25, game.Session.Career.completed + " serviços entregues   /   " + game.Session.Career.experience + " XP", small);
            string[] tabs = { "CHAMADO", "EVIDÊNCIAS", "DIAGNÓSTICO", "ESTOQUE", "CIDADE", "GUIA", "MENSAGENS" };
            for (int i = 0; i < tabs.Length; i++)
            {
                GUI.backgroundColor = page == i ? accent : Color.gray;
                if (GUI.Button(new Rect(112 + i * 151, 160, 145, 37), tabs[i], tab)) { page = i; scroll = Vector2.zero; }
            }
            GUI.backgroundColor = Color.white;
            Fill(new Rect(112, 218, 1055, 342), panel);
            if (page == 0) Mission();
            if (page == 1) Evidence();
            if (page == 2) Diagnosis();
            if (page == 3) Stock();
            if (page == 4) City();
            if (page == 5) Guide();
            if (page == 6) Messages();
            Text(115, 575, 1020, 48, game.Notice, small);
            if (Button(112, 624, 220, "Voltar ao ambiente [TAB]")) game.SetTablet(false);
            Text(355, 634, 580, 25, "PROTÓTIPO 0.3  •  Sistemas e medições fictícios", small);
            if (Button(963, 624, 204, "Salvar e sair")) { game.Save(); Application.Quit(); }
        }
        private void Mission()
        {
            bool prologue = game.Session.IsPrologue || (game.Session.Active == null && !game.Session.Career.prologueCompleted);
            var job=game.DisplayJob;
            bool authored=prologue || job!=null;
            Text(136, 239, 700, 35, game.MissionTitle, heading);
            string clientText=job==null ? "Cliente: Helena Prado / Edifício Horizonte\n“As luzes do corredor do 4º andar apagaram. Ontem estavam piscando.”\n" + (prologue ? "Guto: investigue a causa antes de religar a proteção." : "Chamado livre • Elétrica abstrata • 3 causas possíveis") : "Cliente: "+job.client+" / "+game.DisplayLocationName+"\n"+job.symptom+"\nCapítulo I • "+(job.hydraulic ? "Hidráulica abstrata • kit de vedação" : "Elétrica abstrata");
            Text(136, 288, 660, 80,clientText);
            Text(136, 382, 660, 86, "Pagamento base: R$ "+(job?.basePay??320)+"  •  Bônus sem desperdício: R$ "+(job?.cleanBonus??80)+"\n" + (authored ? "Inspecione e meça. Registre a hipótese. Isole [6] na origem, confirme [5] no componente e troque [4]. Restaure [7], aguarde "+(prologue ? "5" : "3")+"s em campo e teste [5] na origem." : "Investigue a rede, registre uma hipótese, repare e faça o teste integrado."));
            var active = game.Session.Active;
            if (active == null)
            {
                if (Button(136, 483, 300, "Aceitar chamado e viajar")) { game.Accept(); page = 1; }
                if (game.Session.Career.prologueCompleted && job!=null && Button(452,483,280,"Atender chamado livre")) { game.AcceptFree(); page=1; }
                if (game.LastReport != null) Text(840, 239, 295, 280, game.LastReport, small);
            }
            else
            {
                string checklist = "CHECKLIST\n\n" + (active.testedNodes.Count >= 2 ? "✓" : "○") + " Coletar medições\n" + (active.diagnosis >= 0 ? "✓" : "○") + " Registrar hipótese\n";
                if (authored) checklist += ((active.isolated && active.insulationTested) || active.repaired ? "✓" : "○") + " Isolar e confirmar\n";
                checklist += (active.repaired ? "✓" : "○") + " Reparar o componente\n" + (active.validated ? "✓" : "○") + " Validar na origem";
                if (authored) checklist += "\nSistema: " + (active.isolated ? "isolado" : active.circuitClosed ? "restaurado" : "desarmado") + "\nEnsaio: " + active.heatSeconds.ToString("0.0") + " / "+game.Session.StabilitySeconds+" s";
                Text(840, 241, 285, 237, checklist, small);
                if (Button(136, 483, 280, "Entregar serviço", active.validated)) { game.Deliver(); page = 0; }
                if (Button(432, 483, 280, game.AtOffice || game.PreviewLocation != null ? "Retomar visita" : "Voltar à sede / comprar")) { if (game.AtOffice || game.PreviewLocation != null) game.Resume(); else { game.ReturnToOffice(); page = 3; } }
            }
        }
        private void Evidence()
        {
            Text(136, 239, 900, 38, "Registro de campo", heading);
            var active = game.Session.Active;
            string log = active == null || active.evidence.Count == 0 ? "Nenhuma evidência registrada.\n\nNo ambiente, aproxime-se de um painel e pressione E.\n[1] Inspeção  •  [2] Scanner de energia  •  [3] Sonda de sinal\n\nCompare entrada e saída ao longo da rede. O sintoma sozinho não identifica a causa." : string.Join("\n\n", active.evidence);
            scroll = GUI.BeginScrollView(new Rect(136, 288, 999, 246), scroll, new Rect(0, 0, 970, Mathf.Max(246, body.CalcHeight(new GUIContent(log), 950) + 20)));
            GUI.Label(new Rect(0, 0, 950, Mathf.Max(246, body.CalcHeight(new GUIContent(log), 950))), log, body); GUI.EndScrollView();
        }
        private void Diagnosis()
        {
            Text(136, 239, 950, 35, "Qual hipótese explica as suas medições?", heading);
            var job=game.Session.ActiveJob;
            Text(136, 286, 950, 58, job==null ? "Rede lógica: QD-01 (alimentação) → CT-01 (comando) → LM-01 (driver).\nA energia pode faltar no final por uma falha anterior. Compare scanner e sonda." : "Rede: "+string.Join(" → ",job.stationNames)+"\n"+(job.hydraulic ? "Compare pressão, vazão e inspeção da vedação. Registro fechado interrompe o fluxo." : "Compare entrada e resposta em cada etapa antes de trocar o componente."));
            for (int i = 0; i < 3; i++)
            {
                if (Button(136 + i * 335, 363, 315, game.CauseName(i), game.Session.Active != null)) game.Diagnose((FailureCause)i);
                Text(145 + i * 335, 420, 295, 57, job?.hydraulic==true ? (i==0 ? "A alimentação chega ao registro?" : i==1 ? "Existe perda antes da torneira?" : "A torneira deixa passar água com comando fechado?") : i == 0 ? "A entrada existe, mas o módulo não alimenta a rede?" : i == 1 ? "A alimentação chega ao comando, mas o sinal não sai?" : game.Session.IsPrologue ? "O isolamento danificado explica o desarme ao aquecer?" : "Energia e sinal chegam, mas o componente não responde?", small);
            }
            Text(136, 497, 960, 42, game.Session.Active?.diagnosis >= 0 ? "Hipótese atual: " + game.CauseName(game.Session.Active.diagnosis) + "  •  [4] Kit de reparo + [E] no componente" : "Colete ao menos duas medições e registre uma hipótese. Uma troca errada consome peça.");
        }
        private void Stock()
        {
            Text(136, 239, 960, 37, "Peças / fornecedor local", heading);
            Text(136, 287, 960, 67, "Cada troca consome uma peça. Compras na sede, inclusive durante um chamado.\nSem saldo? O fornecedor oferece crédito, descontado no próximo pagamento.\nDívida atual: R$ " + game.Session.Career.supplierDebt);
            for (int i = 0; i < 3; i++)
            {
                Text(144 + i * 250, 367, 235, 60, GameRuntime.CauseNames[i] + "\nEm estoque: " + game.Session.Stock((FailureCause)i));
                if (Button(136 + i * 250, 453, 235, "+1 / R$ 60", game.AtOffice)) game.Buy((FailureCause)i);
            }
            Text(894,367,225,60,"Kit hidráulico / vedação\nEm estoque: "+game.Session.Career.sealKits);
            if (Button(886,453,235,"+1 / R$ 50",game.AtOffice))game.BuySealKit();
        }
        private void Guide()
        {
            Text(136, 239, 960, 35, "Seu primeiro atendimento", heading);
            Text(136, 285, 960, 248, "1. Aceite o próximo chamado da campanha. WASD move, mouse olha, E usa.\n2. [1] inspeciona, [2] mede energia/pressão fictícia, [3] compara resposta/vazão.\n3. Inspecione os componentes, colete duas medições e escolha a hipótese no tablet.\n4. [6] na origem isola; [5] no componente da hipótese confirma; [4] substitui.\n5. [7] na origem restaura. Aguarde 5s no prólogo ou 3s no Capítulo I e teste [5] na origem.\n6. Entregue, reponha peças e confira MENSAGENS. Hidráulica usa kit de vedação separado.\n\nNo prólogo, religar sem reparar provoca novo desarme. O tablet pausa o ensaio.\nChamados livres usam [1–5] e não avançam a lista autoral do capítulo.\nTrês serviços do bairro + reputação 25 permitem a indicação ao contrato recorrente.
7. No primeiro contrato, compare RG-01, BP-01 e RS-01. A preventiva usa kit de bomba próprio e abre o Capítulo II.");
        }
        private void Messages()
        {
            Text(136,239,960,35,game.Session.Career.prologueCompleted ? "Campanha / Capítulo I — Pequenos problemas" : "Campanha / Prólogo — O primeiro chamado",heading);
            string log = game.Session.Career.campaignJournal.Count == 0 ? "A maleta de Guto está pronta. Aceite o primeiro chamado de Helena para iniciar a campanha." : string.Join("\n\n",game.Session.Career.campaignJournal);
            if (game.Session.Career.prologueCompleted) log += "\n\nServiços iniciais: "+game.Session.Career.completedChapterOneJobs.Count+" / "+ChapterOne.Jobs.Length+". Reputação para indicação: "+game.Session.Career.reputation+" / "+ChapterOne.ContractReputation+".\n"+(game.Session.Career.recurringContractUnlocked ? "Indicação ao contrato recorrente conquistada. Manutenção preventiva e rotina do contrato serão a próxima etapa." : "Atenda os chamados autorais na aba CHAMADO. Chamados livres também podem recuperar reputação.");
            float height = Mathf.Max(246,body.CalcHeight(new GUIContent(log),950)+20);
            scroll=GUI.BeginScrollView(new Rect(136,288,999,246),scroll,new Rect(0,0,970,height));
            GUI.Label(new Rect(0,0,950,height),log,body);GUI.EndScrollView();
        }
        private void City()
        {
            var catalog = game.Campaign;
            if (catalog == null) { Text(136,239,960,80,"Catálogo de campanha não encontrado."); return; }
            Text(136,235,960,37,"SANTA AURORA / estrutura da campanha",heading);
            for (int i = 0; i < catalog.districts.Length; i++)
                if (GUI.Button(new Rect(136+i*167,279,158,29),catalog.districts[i].name,small)) { selectedDistrict=i; scroll=Vector2.zero; }
            var district = catalog.districts[selectedDistrict];
            int[] indices = System.Array.FindAll(System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Range(0,catalog.locations.Length)),i=>catalog.locations[i].districtId==district.id);
            if (!System.Array.Exists(indices,i=>i==selectedLocation))selectedLocation=indices[0];
            scroll=GUI.BeginScrollView(new Rect(136,320,390,210),scroll,new Rect(0,0,365,indices.Length*42));
            for(int j=0;j<indices.Length;j++)
                if(GUI.Button(new Rect(0,j*42,360,36),catalog.locations[indices[j]].name,tab))selectedLocation=indices[j];
            GUI.EndScrollView();
            var location=catalog.locations[selectedLocation];
            Text(552,322,579,30,location.name,heading);
            Text(552,361,579,110,"Etapa: "+catalog.chapters[location.unlockChapter].name+"\nPersonagem: "+location.npc+"\nSistemas: "+string.Join(", ",location.systems)+"\n"+location.lore,small);
            for(int f=0;f<location.floors.Length;f++)
                if(Button(552+f*190,487,180,"Visitar / nível "+f)) game.VisitPreview(location,f);
            if(Button(850,576,285,"Voltar à garagem"))game.ReturnToOffice();
        }
    }
}
