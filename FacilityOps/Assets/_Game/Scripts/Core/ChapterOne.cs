using System;

namespace FacilityOps
{
    // Authored opening services. IDs are save keys; descriptions adapt Chapter I, not direct lore quotes.
    public sealed class ServiceDefinition
    {
        public readonly string id, title, locationId, client, symptom;
        public readonly FailureCause cause;
        public readonly bool hydraulic;
        public readonly int basePay, cleanBonus;
        public readonly string[] stationNames, causes, observations;
        public readonly int[] stationRooms;
        public ServiceDefinition(string id, string title, string locationId, string client, string symptom,
            FailureCause cause, bool hydraulic, int basePay, int cleanBonus, string[] stationNames,
            string[] causes, string[] observations, int[] stationRooms)
        {
            this.id=id; this.title=title; this.locationId=locationId; this.client=client; this.symptom=symptom;
            this.cause=cause; this.hydraulic=hydraulic; this.basePay=basePay; this.cleanBonus=cleanBonus;
            this.stationNames=stationNames; this.causes=causes; this.observations=observations; this.stationRooms=stationRooms;
        }
    }
    [Serializable] public sealed class BuildingRecord
    {
        public string locationId, missionId, summary;
        public int mistakes;
    }
    public static class ChapterOne
    {
        public const int ContractReputation = 25;
        public const string FirstContractId = "campaign.c2.recurringcondo.pump.v1";
        public static readonly ServiceDefinition FirstContract = new ServiceDefinition(
            FirstContractId, "II.1 / Primeira preventiva — bomba de recalque", "recurringcondo", "Síndico / Helena",
            "A pressão oscila nos horários de pico. O sistema ainda funciona, mas a bomba principal apresenta sinais de desgaste.",
            FailureCause.ControlRelay, true, 520, 100,
            new[]{"RG-01 / ISOLAMENTO", "BP-01 / BOMBA PRINCIPAL", "RS-01 / RESERVATÓRIO"},
            new[]{"Alimentação / registro", "Bomba de recalque", "Reservatório / controle"},
            new[]{
                "RG-01: alimentação hidráulica disponível e registro operacional. O problema não nasce na entrada.",
                "BP-01: vibração e resposta irregulares no modelo preventivo. A bomba ainda opera, mas o conjunto pede intervenção antes da falha.",
                "RS-01: nível e controle respondem. A oscilação chega ao reservatório vinda da etapa de recalque."
            },
            new[]{4,3,5});

        public static readonly ServiceDefinition[] Jobs =
        {
            new ServiceDefinition("campaign.c1.apartment.socket.v1", "I.1 / Tomada sem energia", "apartments", "Moradores",
                "A tomada da sala parou de funcionar. Trocar o aparelho não resolveu.", FailureCause.SupplyModule, false, 240, 40,
                new[]{"QD-01 / ALIMENTAÇÃO", "CX-01 / CONEXÃO", "TM-01 / TOMADA"},
                new[]{"Módulo de alimentação", "Conexão intermediária", "Módulo da tomada"},
                new[]{"QD-01: módulo de alimentação sem saída. O circuito da sala é separado dos demais.", "CX-01: conexão íntegra; verifique a alimentação a montante.", "TM-01: tomada sem resposta, sem dano externo. O aparelho funciona em outro circuito."},
                new[]{5,2,1}),
            new ServiceDefinition("campaign.c1.grocery.lighting.v1", "I.2 / Luzes da mercearia", "grocery", "Comerciante",
                "As luzes da área de vendas não respondem ao comando, mas o estoque continua iluminado.", FailureCause.ControlRelay, false, 300, 60,
                new[]{"QD-01 / ALIMENTAÇÃO", "CT-01 / COMANDO", "LM-01 / ILUMINAÇÃO"},
                new[]{"Módulo de alimentação", "Relé de comando", "Driver de iluminação"},
                new[]{"QD-01: alimentação disponível para o circuito da loja.", "CT-01: relé não transmite o comando, mesmo com entrada presente.", "LM-01: o conjunto da área de vendas não recebe o comando. Não conclua que todas as lâmpadas falharam."},
                new[]{4,1,0}),
            new ServiceDefinition("campaign.c1.restaurant.tap.v1", "I.3 / Torneira não fecha", "restaurant", "Proprietário",
                "A torneira da copa continua vazando depois de fechar. A cozinha precisa voltar a funcionar.", FailureCause.LightDriver, true, 280, 60,
                new[]{"RG-01 / REGISTRO", "TB-01 / TUBULAÇÃO", "TR-01 / TORNEIRA"},
                new[]{"Registro de alimentação", "Trecho de tubulação", "Vedação da torneira"},
                new[]{"RG-01: registro responde e a alimentação de água está disponível.", "TB-01: trecho seco; não há vazamento visível na tubulação.", "TR-01: gotejamento com comando fechado. A vedação está desgastada."},
                new[]{4,2,3})
        };
        public static ServiceDefinition Find(string id)
        {
            if (id == FirstContractId) return FirstContract;
            return Array.Find(Jobs, job => job.id==id);
        }
    }
}
