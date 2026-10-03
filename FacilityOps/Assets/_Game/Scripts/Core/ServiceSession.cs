using System;
using System.Collections.Generic;

namespace FacilityOps
{
    public enum FailureCause { SupplyModule, ControlRelay, LightDriver }
    public enum StationId { Distribution, Controller, Luminaire }
    public enum ToolMode { Inspect, Scanner, SignalProbe, Repair, Verify }

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
        public List<string> evidence = new List<string>();
        public List<string> testedNodes = new List<string>();
    }

    // This graph is deliberately abstract: readings are fictional diagnostic units.
    public sealed class ElectricalNetwork
    {
        private readonly ServiceData state;
        public ElectricalNetwork(ServiceData state) { this.state = state; }
        public bool SupplyHealthy => state.repaired || state.cause != (int)FailureCause.SupplyModule;
        public bool CommandHealthy => SupplyHealthy && (state.repaired || state.cause != (int)FailureCause.ControlRelay);
        public bool LightingHealthy => CommandHealthy && (state.repaired || state.cause != (int)FailureCause.LightDriver);
        public string Read(StationId node, ToolMode tool)
        {
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
        public CareerData Career { get; }
        public ServiceData Active => Career.active;
        public ElectricalNetwork Network => Active == null ? null : new ElectricalNetwork(Active);
        public ServiceSession(CareerData career) { Career = career; }
        public bool Accept(FailureCause cause)
        {
            if (Active != null) return false;
            Career.active = new ServiceData { cause = (int)cause };
            return true;
        }
        public string Inspect(StationId node)
        {
            if (Active == null) return "Aceite um chamado na sede.";
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
            return "Componente substituído. Iluminação restaurada! Falta testar a rede no QD-01.";
        }
        public string Verify(StationId node)
        {
            if (Active == null) return "Nenhum chamado ativo.";
            if (node != StationId.Distribution) return "O teste integrado está disponível no QD-01.";
            if (!Active.repaired || !Network.LightingHealthy) return "Teste reprovado: a iluminação continua indisponível.";
            Active.validated = true;
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
            Career.active = null;
            return true;
        }
    }
}
