using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace ResortAurora.Sim
{
    /// <summary>Serializable snapshot. Plain data only: never GameObjects. Bump <see cref="CurrentVersion"/> and migrate when fields change.</summary>
    [Serializable]
    public sealed class ResortSave
    {
        public const int CurrentVersion = 1;
        public int version = CurrentVersion;
        public int seed;
        public int day = 1;
        public int balance;
        public float reputation = 0.3f;
        public List<StockEntry> stock = new List<StockEntry>();
        public List<string> upgrades = new List<string>();
        public List<StaffMember> staff = new List<StaffMember>();
        public List<Transaction> transactions = new List<Transaction>();
        public List<string> parcels = new List<string>();   // owned parcel ids (older saves: empty -> defaults apply)
        public int stage = 1;
        public int totalServed;
    }

    /// <summary>JSON persistence in its own file (never touches the old FacilityOps save). Override the path with RESORT_SAVE_PATH for tests.</summary>
    public static class SaveStore
    {
        public static string Path
        {
            get
            {
                var overridePath = Environment.GetEnvironmentVariable("RESORT_SAVE_PATH");
                if (!string.IsNullOrEmpty(overridePath)) return overridePath;
                return System.IO.Path.Combine(Application.persistentDataPath, "ResortAurora", "save_v1.json");
            }
        }

        public static bool Exists() => File.Exists(Path);

        public static void Write(ResortSave save)
        {
            var dir = System.IO.Path.GetDirectoryName(Path);
            Directory.CreateDirectory(dir);
            var tmp = Path + ".tmp";
            File.WriteAllText(tmp, JsonUtility.ToJson(save, true));
            if (File.Exists(Path)) File.Replace(tmp, Path, Path + ".bak"); else File.Move(tmp, Path); // atomic: no half-written saves
        }

        public static ResortSave Read()
        {
            try
            {
                var s = JsonUtility.FromJson<ResortSave>(File.ReadAllText(Path));
                return s != null && s.version <= ResortSave.CurrentVersion ? s : null;
            }
            catch (Exception e) { Debug.LogWarning("ResortAurora: save unreadable, starting fresh. " + e.Message); return null; }
        }
    }
}
