using System;
using System.IO;
using UnityEngine;

namespace FacilityOps
{
    public static class SaveService
    {
        public static string DefaultPath => Path.Combine(Application.persistentDataPath, "career-v1.json");
        public static void Save(CareerData data, string path)
        {
            // Unity serializes null inline classes as default instances. Persist presence explicitly.
            data.servicePresenceVersion = 1;
            data.hasActiveService = data.active != null;
            data.chapterOneDataVersion = 1;
            data.chapterTwoDataVersion = 1;
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
            string temporary = path + ".tmp";
            File.WriteAllText(temporary, JsonUtility.ToJson(data, true));
            if (File.Exists(path)) File.Replace(temporary, path, path + ".bak");
            else File.Move(temporary, path);
        }
        public static CareerData Load(string path)
        {
            if (!File.Exists(path)) return new CareerData();
            try { return Read(path); }
            catch (Exception e) when (e is IOException || e is ArgumentException || e is InvalidDataException)
            {
                Debug.LogWarning("Save principal indisponível: " + e.Message);
                if (File.Exists(path + ".bak")) return Read(path + ".bak");
                throw new InvalidDataException("Save inválido. O arquivo foi preservado para recuperação.", e);
            }
        }
        private static CareerData Read(string path)
        {
            var data = JsonUtility.FromJson<CareerData>(File.ReadAllText(path));
            if (data == null || data.version != 1 || data.money < 0 || data.supplyParts < 0 || data.relayParts < 0 || data.driverParts < 0) throw new InvalidDataException("Versão ou valores inválidos.");
            if (data.servicePresenceVersion < 0 || data.servicePresenceVersion > 1) throw new InvalidDataException("Marcador de chamado incompatível.");
            if (data.servicePresenceVersion == 1 && !data.hasActiveService) data.active = null;
            if (data.chapterOneDataVersion < 0 || data.chapterOneDataVersion > 1) throw new InvalidDataException("Dados do capítulo incompatíveis.");
            if (data.chapterOneDataVersion == 0) data.sealKits = 2;
            if (data.sealKits < 0) throw new InvalidDataException("Estoque hidráulico inválido.");
            if (data.chapterTwoDataVersion < 0 || data.chapterTwoDataVersion > 1) throw new InvalidDataException("Dados do Capítulo II incompatíveis.");
            if (data.chapterTwoDataVersion == 0) data.pumpKits = 1;
            if (data.pumpKits < 0) throw new InvalidDataException("Estoque preventivo de bombas inválido.");
            if (data.firstContractCompleted && !data.recurringContractUnlocked) throw new InvalidDataException("Contrato concluído sem desbloqueio.");
            if (data.completedChapterOneJobs == null) data.completedChapterOneJobs = new System.Collections.Generic.List<string>();
            if (data.buildingHistory == null) data.buildingHistory = new System.Collections.Generic.List<BuildingRecord>();
            var uniqueJobs = new System.Collections.Generic.HashSet<string>();
            foreach (string id in data.completedChapterOneJobs)
                if (ChapterOne.Find(id) == null || !uniqueJobs.Add(id)) throw new InvalidDataException("Progresso do capítulo inválido.");
            if (data.active != null && (data.active.cause < 0 || data.active.cause > 2 || data.active.diagnosis < -1 || data.active.diagnosis > 2 || data.active.evidence == null || data.active.testedNodes == null)) throw new InvalidDataException("Chamado inválido.");
            if (data.campaignJournal == null) data.campaignJournal = new System.Collections.Generic.List<string>();
            var job = ChapterOne.Find(data.active?.missionId);
            if (job != null)
            {
                bool firstContract = job.id == ChapterOne.FirstContractId;
                bool alreadyCompleted = firstContract ? data.firstContractCompleted : data.completedChapterOneJobs.Contains(job.id);
                float maxStability = firstContract ? 4f : 3f;
                if (!data.prologueCompleted || alreadyCompleted || data.active.cause != (int)job.cause || (data.active.isolated && data.active.circuitClosed) || float.IsNaN(data.active.heatSeconds) || float.IsInfinity(data.active.heatSeconds) || data.active.heatSeconds < 0 || data.active.heatSeconds > maxStability) throw new InvalidDataException("Chamado autoral inválido.");
                if (firstContract && (!data.recurringContractUnlocked || data.completedChapterOneJobs.Count != ChapterOne.Jobs.Length)) throw new InvalidDataException("Contrato preventivo aceito antes da indicação.");
            }
            if (data.active != null && data.active.missionId == ServiceSession.PrologueId && (data.active.cause != 2 || float.IsNaN(data.active.heatSeconds) || float.IsInfinity(data.active.heatSeconds) || data.active.heatSeconds < 0 || data.active.heatSeconds > ServiceSession.HeatTestSeconds || (data.active.isolated && data.active.circuitClosed))) throw new InvalidDataException("Estado do prólogo inválido.");
            return data;
        }
    }
}
