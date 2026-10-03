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
            if (data.active != null && (data.active.cause < 0 || data.active.cause > 2 || data.active.diagnosis < -1 || data.active.diagnosis > 2 || data.active.evidence == null || data.active.testedNodes == null)) throw new InvalidDataException("Chamado inválido.");
            return data;
        }
    }
}
