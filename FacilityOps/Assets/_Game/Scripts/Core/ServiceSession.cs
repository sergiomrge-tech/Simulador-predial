using System;
using System.Collections.Generic;

namespace FacilityOps
{
    public enum FailureCause { SupplyModule, ControlRelay, LightDriver }
    public enum StationId { Distribution, Controller, Luminaire }
    public enum ToolMode { Inspect, Scanner, SignalProbe, Repair, Verify, Isolate, Restore }

    [Serializable]
    public sealed class CareerData
    {
        public int version = 1;
        public int money = 400;
        public int reputation = 10;
        public int experience;
        public int completed;
        public int supplierDebt;
        public int supplyParts = 2;
        public int relayParts = 2;
        public int driverParts = 2;
        public bool prologueCompleted;
        public List<string> campaignJournal = new List<string>();
        public int servicePresenceVersion;
        public bool hasActiveService;
        public ServiceData active;
    }

    [Serializable]
    public sealed class ServiceData
    {
        public string missionId = "office.lighting.v1";
        public int cause;
        public int diagnosis = -1;
        public bool repaired;
        public bool validated;
        public bool settled;
        public int mistakes;
        public float elapsed;
        public bool circuitClosed;
        public bool isolated;
        public bool insulationTested;
        public bool defectFound;
        public float heatSeconds;
        public List<string> evidence = new List<string>();
        public List<string> testedNodes = new List<string>();
    }

    // This graph is deliberately abstract: readings are fictional diagnostic units.
    public sealed class ElectricalNetwork
    {
        private readonly ServiceData state;
        public ElectricalNetwork(ServiceData state) { this.state = state; }
        private bool Prologue => state.missionId == ServiceSession.PrologueId;
        public bool SupplyHealthy => Prologue ? state.circuitClosed : state.repaired || state.cause != (int)FailureCause.SupplyModule;
        public bool CommandHealthy => SupplyHealthy && (Prologue || state.repaired || state.cause != (int)FailureCause.ControlRelay);
        public bool LightingHealthy => CommandHealthy && (Prologue || state.repaired || state.cause != (int)FailureCause.LightDriver);
        public string Read(StationId node, ToolMode tool)
        {
            if (Prologue)
            {
                if (tool == ToolMode.Scanner) return state.circuitClosed ? "Circuito: 100 U fictícias. A luz acendeu; observe o comportamento ao aquecer." : "Circuito: 0 U fictícias. Distinguir disjuntor desarmado de isolamento confirmado.";
                if (node == StationId.Luminaire) return state.repaired ? "Módulo de luminária substituído. Isolamento virtual íntegro." : "LM-01: resposta de isolamento irregular. O defeito aparece com aquecimento.";
                return node == StationId.Distribution ? (state.circuitClosed ? "Proteção virtual fechada; acompanhe a estabilidade do circuito." : "Proteção virtual aberta. Investigue a falha no circuito a jusante.") : "Comando íntegro. A causa não está no relé CT-01.";
            }
            if (tool == ToolMode.Scanner)
            {
                if (node == StationId.Distribution) return SupplyHealthy ? "Entrada 100 U / saída 100 U. Alimentação estável." : "Entrada 100 U / saída 0 U. Módulo sem resposta.";
                if (node == StationId.Controller) return SupplyHealthy ? "Entrada do controlador: 100 U. Alimentação disponível." : "Entrada do controlador: 0 U. Investigue a origem a montante.";
                return CommandHealthy ? "Entrada da luminária: 100 U. Energia virtual disponível." : "Entrada da luminária: 0 U. A falha pode estar a montante.";
            }
            if (node == StationId.Distribution) return SupplyHealthy ? "Pulso de saída presente. O módulo transmite o sinal." : "Pulso de saída ausente. Entrada presente, saída interrompida.";
            if (node == StationId.Controller) return !SupplyHealthy ? "Sem pulso de entrada. Não é possível avaliar o comando sem alimentação." : CommandHealthy ? "Pulso de entrada e saída presentes. Comando responde." : "Pulso de entrada presente / saída ausente. Comando não responde.";
            return !CommandHealthy ? "Sem sinal recebido. Verifique distribuição e comando antes de trocar a peça." : LightingHealthy ? "Driver responde; emissão luminosa confirmada." : "Sinal recebido / driver sem resposta. Emissão ausente.";
        }
    }

    public sealed class ServiceSession
    {
        public const string PrologueId = "campaign.prologue.horizonte.v1";
        public const float HeatTestSeconds = 5f;
        public CareerData Career { get; }
        public ServiceData Active => Career.active;
        public ElectricalNetwork Network => Active == null ? null : new ElectricalNetwork(Active);
        public bool IsPrologue => Active?.missionId == PrologueId;
        public ServiceSession(CareerData career) { Career = career; if (Career.campaignJournal == null) Career.campaignJournal = new List<string>(); }
        public bool AcceptPrologue()
        {
            if (Active != null || Career.prologueCompleted) return false;
            Career.active = new ServiceData { missionId = PrologueId, cause = (int)FailureCause.LightDriver };
            Journal("Guto / A maleta agora é sua. Máquina sempre avisa antes de parar. Primeiro entenda, depois confirme, só então repare.");
            Journal("Helena / Edifício Horizonte: o corredor do quarto andar ficou sem energia. O disjuntor desarmou depois que as luzes piscaram.");
            return true;
        }
        private void Journal(string message) { if (!Career.campaignJournal.Contains(message)) Career.campaignJournal.Add(message); }
        public string Tick(float seconds)
        {
            if (!IsPrologue || !Active.circuitClosed || seconds <= 0) return null;
            Active.heatSeconds = Math.Min(HeatTestSeconds, Active.heatSeconds + seconds);
            if (!Active.repaired && Active.heatSeconds >= HeatTestSeconds)
            {
                Active.circuitClosed = false;
                AddEvidence("Falha reproduzida: ao aquecer, LM-01 provoca curto virtual e a proteção desarma novamente.");
                Journal("Guto / Disjuntor não desarma por vontade própria. Religar remove o sintoma por alguns segundos; investigue a luminária.");
                return "O circuito desarmou novamente ao aquecer. Guto: sintoma não é causa. Inspecione LM-01.";
            }
            return null;
        }
        public string Isolate(StationId node)
        {
            if (!IsPrologue) return "Isolamento disponível no prólogo autoral do Horizonte.";
            if (node != StationId.Distribution) return "Isole o circuito no QD-01 usando [6].";
            if (Active.isolated) return "Circuito já isolado. Use [5] na LM-01 para confirmar antes da troca.";
            Active.circuitClosed = false; Active.isolated = true; Active.insulationTested = false;
            Active.validated = false; Active.heatSeconds = 0;
            AddEvidence("QD-01: circuito isolado e bloqueado no sistema fictício.");
            return "Circuito isolado. Confirme na LM-01 com [5]; só então use o kit de reparo.";
        }
        public string Restore(StationId node)
        {
            if (!IsPrologue) return "Restauração manual disponível no prólogo do Horizonte.";
            if (node != StationId.Distribution) return "Restaure no QD-01 usando [7].";
            if (Active.circuitClosed) return "Circuito já restaurado. Aguarde o ensaio de aquecimento e teste no QD-01.";
            Active.circuitClosed = true; Active.isolated = false; Active.insulationTested = false;
            Active.validated = false; Active.heatSeconds = 0;
            return Active.repaired ? "Circuito restaurado. Aguarde 5 segundos em campo e use [5] no QD-01 para verificar estabilidade." : "Proteção rearmada. A causa permanece: observe se o circuito sustenta a iluminação ao aquecer.";
        }
        public bool Accept(FailureCause cause)
        {
            if (Active != null) return false;
            Career.active = new ServiceData { cause = (int)cause };
            return true;
        }
        public string Inspect(StationId node)
        {
            if (Active == null) return "Aceite um chamado na sede.";
            if (IsPrologue)
            {
                string observation;
                if (node == StationId.Distribution) observation = Active.circuitClosed ? "QD-01: circuito energizado. O rearme ainda não comprova a correção da causa." : Active.isolated ? "QD-01: circuito isolado e bloqueado." : "QD-01: disjuntor desarmado. Guto: disjuntor não desarma por vontade própria.";
                else if (node == StationId.Controller) observation = "CT-01: comando íntegro. Siga o circuito até a luminária antiga.";
                else { Active.defectFound = true; observation = Active.repaired ? "LM-01: módulo novo instalado." : "LM-01: isolamento danificado na luminária antiga. Marcas de aquecimento explicam a falha intermitente."; }
                AddEvidence(node + ": " + observation); return observation;
            }
            string note = node == StationId.Distribution ? "QD-01 alimenta CT-01, que comanda LM-01. Etiquetas legíveis; carcaça intacta." : node == StationId.Controller ? "CT-01: comando do corredor. O histórico registra iluminação intermitente." : "LM-01: corredor sem iluminação. Sem dano externo visível.";
            AddEvidence(node + ": " + note);
            return note;
        }
        public string Measure(StationId node, ToolMode tool)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (tool != ToolMode.Scanner && tool != ToolMode.SignalProbe) return "Selecione uma ferramenta de diagnóstico.";
            string key = node + "." + tool;
            if (!Active.testedNodes.Contains(key)) Active.testedNodes.Add(key);
            string reading = Network.Read(node, tool);
            AddEvidence(node + " / " + tool + ": " + reading);
            return reading;
        }
        private void AddEvidence(string note) { if (!Active.evidence.Contains(note)) Active.evidence.Add(note); }
        public string Diagnose(FailureCause cause)
        {
            if (Active == null) return "Aceite um chamado primeiro.";
            if (Active.repaired) return "O reparo já foi executado. Faça a validação.";
            if (Active.testedNodes.Count < 2) return "Colete ao menos duas medições antes de registrar uma hipótese.";
            if (IsPrologue && !Active.defectFound) return "Inspecione a luminária LM-01 antes de concluir a causa.";
            Active.diagnosis = (int)cause;
            return "Hipótese registrada. Use o kit de reparo no componente escolhido.";
        }
        public int Stock(FailureCause cause) => cause == FailureCause.SupplyModule ? Career.supplyParts : cause == FailureCause.ControlRelay ? Career.relayParts : Career.driverParts;
        public bool Buy(FailureCause cause, bool atOffice = true)
        {
            const int cost = 60;
            if (!atOffice) return false;
            if (Career.money < cost)
            {
                Career.supplierDebt += cost - Career.money;
                Career.money = 0;
            }
            else Career.money -= cost;
            ChangeStock(cause, 1);
            return true;
        }
        private void ChangeStock(FailureCause cause, int delta)
        {
            if (cause == FailureCause.SupplyModule) Career.supplyParts += delta;
            else if (cause == FailureCause.ControlRelay) Career.relayParts += delta;
            else Career.driverParts += delta;
        }
        public string Repair(StationId node)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (Active.repaired) return "Componente reparado. Valide a rede no QD-01.";
            if (Active.diagnosis < 0) return "Registre seu diagnóstico no tablet [TAB] antes de reparar.";
            if ((int)node != Active.diagnosis) return "Este componente não corresponde à hipótese registrada.";
            if (IsPrologue && (!Active.isolated || Active.circuitClosed || !Active.insulationTested)) return "Troca bloqueada: isole no QD-01 [6] e confirme na LM-01 [5]. Nenhuma peça foi consumida.";
            FailureCause chosen = (FailureCause)Active.diagnosis;
            if (Stock(chosen) < 1) return "Sem peça compatível. Volte à sede e reponha o estoque.";
            ChangeStock(chosen, -1);
            if (Active.diagnosis != Active.cause)
            {
                Active.mistakes++;
                Active.diagnosis = -1;
                return "Peça substituída, mas o sintoma continua. Reavalie suas evidências.";
            }
            Active.repaired = true;
            Active.validated = false;
            if (IsPrologue) return "Luminária substituída com circuito isolado. Restaure no QD-01 [7] e confirme estabilidade após aquecer.";
            return "Componente substituído. Iluminação restaurada! Falta testar a rede no QD-01.";
        }
        public string Verify(StationId node)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (IsPrologue && node == StationId.Luminaire)
            {
                if (!Active.isolated || Active.circuitClosed) return "Confirmação recusada: isole primeiro no QD-01 [6].";
                Active.insulationTested = true;
                AddEvidence("LM-01: ausência de energia fictícia confirmada antes da intervenção.");
                return "Teste de isolamento confirmado. Registre a hipótese e substitua o módulo de luminária com [4].";
            }
            if (node != StationId.Distribution) return "O teste integrado está disponível no QD-01.";
            if (!Active.repaired || !Network.LightingHealthy) return "Teste reprovado: a iluminação continua indisponível.";
            if (IsPrologue && Active.heatSeconds < HeatTestSeconds) return "Ensaio ainda em andamento. Aguarde 5 segundos com circuito restaurado, fora do tablet, e repita.";
            Active.validated = true;
            if (IsPrologue) AddEvidence("Ensaio térmico virtual aprovado: a iluminação permanece estável após aquecimento.");
            return "Teste aprovado: distribuição, comando e iluminação operacionais. Entregue pelo tablet.";
        }
        public int Reward => Active == null ? 0 : Math.Max(180, 320 + (Active.mistakes == 0 ? 80 : 0) - Active.mistakes * 30);
        public bool Settle(out int payment)
        {
            payment = 0;
            if (Active == null || !Active.validated || Active.settled) return false;
            payment = Reward;
            int repayment = Math.Min(payment, Career.supplierDebt);
            Career.supplierDebt -= repayment;
            payment -= repayment;
            Active.settled = true;
            Career.money += payment;
            Career.reputation = Math.Max(0, Math.Min(100, Career.reputation + (Active.mistakes == 0 ? 5 : 1)));
            Career.experience += 100;
            Career.completed++;
            if (IsPrologue)
            {
                Career.prologueCompleted = true;
                Journal("Guto / Você encontrou a causa, isolou, confirmou e testou antes de entregar. Guarde esse método para cada chamado.");
                Journal("Helena / Pagamento enviado. A iluminação permaneceu estável; vou indicar sua empresa quando precisarem de manutenção.");
            }
            Career.active = null;
            return true;
        }
    }
}
