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
        public int chapterOneDataVersion;
        public int sealKits = 2;
        public bool recurringContractUnlocked;
        public List<string> completedChapterOneJobs = new List<string>();
        public List<BuildingRecord> buildingHistory = new List<BuildingRecord>();
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
        private ServiceDefinition Job => ChapterOne.Find(state.missionId);
        public bool SupplyHealthy => Prologue ? state.circuitClosed : (Job == null || state.circuitClosed) && (state.repaired || state.cause != (int)FailureCause.SupplyModule);
        public bool CommandHealthy => SupplyHealthy && (Prologue || state.repaired || state.cause != (int)FailureCause.ControlRelay);
        public bool LightingHealthy => CommandHealthy && (Prologue || state.repaired || state.cause != (int)FailureCause.LightDriver);
        public string Read(StationId node, ToolMode tool)
        {
            if (Job != null && Job.hydraulic)
            {
                if (tool == ToolMode.Scanner) return SupplyHealthy ? "Pressão virtual: 100 UP fictícias. Alimentação disponível." : "Pressão virtual: 0 UP. Registro fechado ou alimentação interrompida.";
                if (!SupplyHealthy) return "Vazão virtual: 0 UF. O sistema está isolado; confirme antes de abrir o componente.";
                if (node == StationId.Luminaire) return state.repaired ? "Comando fechar: 0 UF / comando abrir: 20 UF. Vedação responde." : "Comando fechar: 12 UF residuais. A torneira não veda.";
                return "Trecho de alimentação responde; sem perda virtual antes da torneira.";
            }
            if (Job != null)
            {
                if (tool == ToolMode.Scanner)
                {
                    if (node == StationId.Distribution) return "Entrada 100 U / saída " + (SupplyHealthy ? "100" : "0") + " U fictícias.";
                    return "Entrada virtual: " + ((node == StationId.Controller ? SupplyHealthy : CommandHealthy) ? "100" : "0") + " U. Compare a etapa anterior.";
                }
                bool responds = node == StationId.Distribution ? SupplyHealthy : node == StationId.Controller ? CommandHealthy : LightingHealthy;
                return Job.stationNames[(int)node] + (responds ? ": entrada e resposta presentes." : ": resposta ausente; diferencie falha local de falta de entrada.");
            }
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
        public ServiceDefinition ActiveJob => ChapterOne.Find(Active?.missionId);
        public bool IsAuthored => IsPrologue || ActiveJob != null;
        public ServiceDefinition NextJob => Array.Find(ChapterOne.Jobs, job => !Career.completedChapterOneJobs.Contains(job.id));
        public float StabilitySeconds => IsPrologue ? HeatTestSeconds : 3f;
        public ServiceSession(CareerData career)
        {
            Career = career;
            if (Career.campaignJournal == null) Career.campaignJournal = new List<string>();
            if (Career.completedChapterOneJobs == null) Career.completedChapterOneJobs = new List<string>();
            if (Career.buildingHistory == null) Career.buildingHistory = new List<BuildingRecord>();
        }
        public bool AcceptChapterOne(string id)
        {
            if (Active != null || !Career.prologueCompleted || NextJob == null || NextJob.id != id) return false;
            var job = NextJob;
            Career.active = new ServiceData { missionId=job.id, cause=(int)job.cause, circuitClosed=true };
            Journal(job.client + " / " + job.title + ": " + job.symptom);
            return true;
        }
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
            if (!IsAuthored || !Active.circuitClosed || seconds <= 0) return null;
            Active.heatSeconds = Math.Min(StabilitySeconds, Active.heatSeconds + seconds);
            if (IsPrologue && !Active.repaired && Active.heatSeconds >= HeatTestSeconds)
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
            if (!IsAuthored) return "Isolamento disponível nos chamados autorais da campanha.";
            if (node != StationId.Distribution) return "Isole no primeiro equipamento da rede usando [6].";
            if (Active.isolated) return "Sistema já isolado. Use [5] no componente da hipótese para confirmar antes da troca.";
            Active.circuitClosed = false; Active.isolated = true; Active.insulationTested = false;
            Active.validated = false; Active.heatSeconds = 0;
            AddEvidence((ActiveJob?.stationNames[0]??"QD-01") + ": sistema isolado e bloqueado no modelo fictício.");
            return "Sistema isolado. Confirme com [5] no componente da hipótese; só então use o kit de reparo.";
        }
        public string Restore(StationId node)
        {
            if (!IsAuthored) return "Restauração manual disponível nos chamados autorais da campanha.";
            if (node != StationId.Distribution) return "Restaure no primeiro equipamento da rede usando [7].";
            if (Active.circuitClosed) return "Sistema já restaurado. Aguarde o ensaio de estabilidade e teste na origem da rede.";
            Active.circuitClosed = true; Active.isolated = false; Active.insulationTested = false;
            Active.validated = false; Active.heatSeconds = 0;
            return Active.repaired ? "Sistema restaurado. Aguarde " + StabilitySeconds + " segundos em campo e use [5] no primeiro equipamento para verificar estabilidade." : "Sistema reaberto. A causa permanece; investigue antes de entregar.";
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
            if (ActiveJob != null)
            {
                if ((int)node == Active.cause) Active.defectFound = true;
                string observation = Active.repaired ? ActiveJob.stationNames[(int)node] + ": reparo registrado. Confirme o funcionamento após restaurar." : ActiveJob.observations[(int)node];
                AddEvidence(observation); return observation;
            }
            if (IsPrologue)
            {
                string observation;
                if (node == StationId.Distribution) observation = Active.circuitClosed ? "QD-01: circuito energizado. O rearme ainda não comprova a correção da causa." : Active.isolated ? "QD-01: circuito isolado e bloqueado." : "QD-01: disjuntor desarmado. Guto: disjuntor não desarma por vontade própria.";
                else if (node == StationId.Controller) observation = "CT-01: comando íntegro. Siga o circuito até a luminária antiga.";
                else { Active.defectFound = true; observation = Active.repaired ? "LM-01: módulo novo instalado." : "LM-01: isolamento danificado na luminária antiga. Marcas de aquecimento explicam a falha intermitente."; }
                AddEvidence(StationName(node) + ": " + observation); return observation;
            }
            string note = node == StationId.Distribution ? "QD-01 alimenta CT-01, que comanda LM-01. Etiquetas legíveis; carcaça intacta." : node == StationId.Controller ? "CT-01: comando do corredor. O histórico registra iluminação intermitente." : "LM-01: corredor sem iluminação. Sem dano externo visível.";
            AddEvidence(StationName(node) + ": " + note);
            return note;
        }
        public string Measure(StationId node, ToolMode tool)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (tool != ToolMode.Scanner && tool != ToolMode.SignalProbe) return "Selecione uma ferramenta de diagnóstico.";
            string key = node + "." + tool;
            if (!Active.testedNodes.Contains(key)) Active.testedNodes.Add(key);
            string reading = Network.Read(node, tool);
            string instrument=tool==ToolMode.Scanner ? (ActiveJob?.hydraulic==true ? "pressão" : "energia") : (ActiveJob?.hydraulic==true ? "vazão" : "resposta");
            AddEvidence(StationName(node) + " / " + instrument + ": " + reading);
            return reading;
        }
        private string StationName(StationId node) => ActiveJob?.stationNames[(int)node] ?? (node==StationId.Distribution ? "QD-01" : node==StationId.Controller ? "CT-01" : "LM-01");
        private void AddEvidence(string note) { if (!Active.evidence.Contains(note)) Active.evidence.Add(note); }
        public string Diagnose(FailureCause cause)
        {
            if (Active == null) return "Aceite um chamado primeiro.";
            if (Active.repaired) return "O reparo já foi executado. Faça a validação.";
            if (Active.testedNodes.Count < 2) return "Colete ao menos duas medições antes de registrar uma hipótese.";
            if (IsPrologue && !Active.defectFound) return "Inspecione a luminária LM-01 antes de concluir a causa.";
            if (ActiveJob != null && !Active.defectFound) return "Inspecione os componentes para confirmar a causa antes de registrar a hipótese.";
            if (ActiveJob != null && Active.diagnosis != (int)cause) Active.insulationTested = false;
            Active.diagnosis = (int)cause;
            return "Hipótese registrada. Use o kit de reparo no componente escolhido.";
        }
        public int Stock(FailureCause cause) => cause == FailureCause.SupplyModule ? Career.supplyParts : cause == FailureCause.ControlRelay ? Career.relayParts : Career.driverParts;
        public bool Buy(FailureCause cause, bool atOffice = true)
        {
            const int cost = 60;
            if (!atOffice) return false;
            PayForPart(cost);
            ChangeStock(cause, 1);
            return true;
        }
        public bool BuySealKit(bool atOffice)
        {
            if (!atOffice) return false;
            PayForPart(50); Career.sealKits++; return true;
        }
        private void PayForPart(int cost)
        {
            if (Career.money < cost)
            {
                Career.supplierDebt += cost - Career.money;
                Career.money = 0;
            }
            else Career.money -= cost;
        }
        public int RepairStock(FailureCause cause) => ActiveJob?.hydraulic == true ? Career.sealKits : Stock(cause);
        private void ChangeStock(FailureCause cause, int delta)
        {
            if (cause == FailureCause.SupplyModule) Career.supplyParts += delta;
            else if (cause == FailureCause.ControlRelay) Career.relayParts += delta;
            else Career.driverParts += delta;
        }
        public string Repair(StationId node)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (Active.repaired) return "Componente reparado. Restaure e valide a rede na origem.";
            if (Active.diagnosis < 0) return "Registre seu diagnóstico no tablet [TAB] antes de reparar.";
            if ((int)node != Active.diagnosis) return "Este componente não corresponde à hipótese registrada.";
            if (IsAuthored && (!Active.isolated || Active.circuitClosed || !Active.insulationTested)) return "Troca bloqueada: isole o sistema [6] e confirme no componente [5]. Nenhuma peça foi consumida.";
            FailureCause chosen = (FailureCause)Active.diagnosis;
            if (RepairStock(chosen) < 1) return "Sem peça compatível. Volte à sede e reponha o estoque.";
            if (ActiveJob?.hydraulic == true) Career.sealKits--; else ChangeStock(chosen, -1);
            if (Active.diagnosis != Active.cause)
            {
                Active.mistakes++;
                Active.diagnosis = -1;
                return "Peça substituída, mas o sintoma continua. Reavalie suas evidências.";
            }
            Active.repaired = true;
            Active.validated = false;
            Active.heatSeconds = 0;
            if (IsPrologue) return "Luminária substituída com circuito isolado. Restaure no QD-01 [7] e confirme estabilidade após aquecer.";
            if (ActiveJob != null) return "Componente substituído com sistema isolado. Restaure [7] e valide a rede [5].";
            return "Componente substituído. Iluminação restaurada! Falta testar a rede no QD-01.";
        }
        public string Verify(StationId node)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (IsAuthored && ((IsPrologue && node == StationId.Luminaire) || (ActiveJob != null && Active.diagnosis == (int)node && Active.isolated)))
            {
                if (!Active.isolated || Active.circuitClosed) return "Confirmação recusada: isole primeiro no QD-01 [6].";
                Active.insulationTested = true;
                AddEvidence((ActiveJob == null ? "LM-01" : ActiveJob.stationNames[(int)node]) + ": isolamento fictício confirmado antes da intervenção.");
                return "Teste de isolamento confirmado. Substitua o componente da hipótese com [4].";
            }
            if (node != StationId.Distribution) return "O teste integrado está disponível na origem da rede.";
            if (!Active.repaired || !Network.LightingHealthy) return "Teste reprovado: a rede ainda não foi reparada e restaurada.";
            if (IsAuthored && Active.heatSeconds < StabilitySeconds) return "Ensaio ainda em andamento. Aguarde " + StabilitySeconds + " segundos com sistema restaurado, fora do tablet, e repita.";
            Active.validated = true;
            if (IsPrologue) AddEvidence("Ensaio térmico virtual aprovado: a iluminação permanece estável após aquecimento.");
            return "Teste aprovado: sistema restaurado e resposta final confirmada. Entregue pelo tablet.";
        }
        public int Reward => Active == null ? 0 : Math.Max(ActiveJob == null ? 180 : 100, (ActiveJob?.basePay ?? 320) + (Active.mistakes == 0 ? (ActiveJob?.cleanBonus ?? 80) : 0) - Active.mistakes * 30);
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
            if (ActiveJob != null)
            {
                var job = ActiveJob;
                Career.completedChapterOneJobs.Add(job.id);
                Career.buildingHistory.Add(new BuildingRecord { locationId=job.locationId, missionId=job.id, mistakes=Active.mistakes, summary=job.title + " / sistema restaurado e validado / trocas incorretas: " + Active.mistakes });
                Journal(job.client + " / Serviço entregue: " + job.title + ". Pagamento líquido: R$ " + payment + ".");
            }
            if (!Career.recurringContractUnlocked && Career.completedChapterOneJobs.Count == ChapterOne.Jobs.Length && Career.reputation >= ChapterOne.ContractReputation)
            {
                Career.recurringContractUnlocked = true;
                Journal("Helena / Vi a qualidade dos seus atendimentos no bairro. Indiquei sua empresa para o primeiro contrato recorrente de um condomínio. A próxima fase será manutenção preventiva.");
            }
            Career.active = null;
            return true;
        }
    }
}
