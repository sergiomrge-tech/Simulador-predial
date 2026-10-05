using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor.Build;
using UnityEngine;

namespace FacilityOps.Editor
{
    // A successful import is insufficient evidence for shipping the playable slice.
    public static class WorldSliceBuildGate
    {
        [Serializable] private sealed class Verdict { public string status; public string fingerprint; }
        public static string Fingerprint()
        {
            using var hash = SHA256.Create();
            string[] folders = { "Assets/_Game/World", "Assets/_Game/Scripts/Runtime", "Assets/_Game/Editor", "Assets/_Game/Tests", "Assets/_Game/Scenes", "Assets/_Game/Resources" };
            foreach (string path in folders.Where(Directory.Exists).SelectMany(f => Directory.GetFiles(f, "*", SearchOption.AllDirectories))
                .Where(p => !p.Replace('\\', '/').Contains("/QA/") && !p.Replace('\\', '/').EndsWith("/QA.meta", StringComparison.Ordinal)).OrderBy(p => p, StringComparer.Ordinal))
            {
                byte[] name = Encoding.UTF8.GetBytes(path.Replace('\\', '/'));
                hash.TransformBlock(name, 0, name.Length, name, 0);
                byte[] data = File.ReadAllBytes(path);
                hash.TransformBlock(data, 0, data.Length, data, 0);
            }
            const string route = "../Docs/ValidationEvidence/VerticalSliceQA/route.json";
            if (File.Exists(route))
            {
                byte[] name = Encoding.UTF8.GetBytes("QA/route.json"), data = File.ReadAllBytes(route);
                hash.TransformBlock(name, 0, name.Length, name, 0);
                hash.TransformBlock(data, 0, data.Length, data, 0);
            }
            hash.TransformFinalBlock(Array.Empty<byte>(), 0, 0);
            return BitConverter.ToString(hash.Hash).Replace("-", "");
        }
        public static void RequirePassed()
        {
            string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../Logs"));
            string fingerprint = Fingerprint();
            foreach (string file in new[] { "world-runtime-qa.json", "world-walkability-qa.json", "world-stair-walk-qa.json" })
            {
                string path = Path.Combine(folder, file);
                if (!File.Exists(path)) throw new BuildFailedException("Playable slice gate missing: " + path);
                var verdict = JsonUtility.FromJson<Verdict>(File.ReadAllText(path));
                if (verdict == null || verdict.status != "PASS" || verdict.fingerprint != fingerprint)
                    throw new BuildFailedException("Playable slice gate failed or stale: " + path + ". Resolve critical issues and rerun Play Mode/walkability QA before building.");
            }
        }
    }
}
