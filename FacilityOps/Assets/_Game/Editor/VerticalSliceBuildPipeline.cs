using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using FacilityOps;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class VerticalSliceBuildPipeline
    {
        [Serializable] private sealed class Receipt { public string status, fingerprint; }
        [Serializable] private sealed class EditorReceipt { public string status, fingerprint, scope; public bool continuous, streaming, saveLoad; }
        public static void RecordTests()
        {
            string path = Path.Combine(VerticalSliceQaRunner.EvidenceFolder, "EditMode.xml");
            var result = XDocument.Load(path).Root;
            DateTime newestSource = new[] { "Assets/_Game/Scripts", "Assets/_Game/Editor", "Assets/_Game/Tests" }
                .SelectMany(folder => Directory.GetFiles(folder, "*.cs", SearchOption.AllDirectories)).Select(File.GetLastWriteTimeUtc).Max();
            if (File.GetLastWriteTimeUtc(path) < newestSource) throw new BuildFailedException("NUnit evidence predates the current C# sources; rerun tests.");
            if (result == null || (int?)result.Attribute("failed") != 0 || ((int?)result.Attribute("passed") ?? 0) == 0)
                throw new BuildFailedException("NUnit report missing/failed/empty: " + path);
            File.WriteAllText(Path.Combine(VerticalSliceQaRunner.EvidenceFolder, "tests-receipt.json"), JsonUtility.ToJson(new Receipt { status = "PASS", fingerprint = WorldSliceBuildGate.Fingerprint() }, true));
        }
        public static void BuildCandidate()
        {
            VerticalSliceQaRunner.ValidateStaticBatch();
            string fingerprint = WorldSliceBuildGate.Fingerprint();
            var tests = JsonUtility.FromJson<Receipt>(File.ReadAllText(Path.Combine(VerticalSliceQaRunner.EvidenceFolder, "tests-receipt.json")));
            var walk = JsonUtility.FromJson<EditorReceipt>(File.ReadAllText(Path.Combine(VerticalSliceQaRunner.EvidenceFolder, "editor-runtime.json")));
            if (tests?.status != "PASS" || tests.fingerprint != fingerprint || walk?.status != "PASS" || walk.fingerprint != fingerprint || walk.scope != "EDITOR" || !walk.continuous || !walk.streaming || !walk.saveLoad)
                throw new BuildFailedException("Candidate requires fresh tests and continuous physical Editor route, streaming and save/load PASS.");
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "../.."));
            string output = Path.GetFullPath(Environment.GetEnvironmentVariable("FACILITY_QA_BUILD_STAGE") ?? Path.Combine(root, "Builds/Windows/VerticalSliceQA-stage"));
            string allowed = Path.GetFullPath(Path.Combine(root, "Builds")) + Path.DirectorySeparatorChar;
            if (!output.StartsWith(allowed, StringComparison.OrdinalIgnoreCase)) throw new BuildFailedException("Build output must remain under repository Builds.");
            if (Directory.Exists(output) && Directory.EnumerateFileSystemEntries(output).Any()) throw new BuildFailedException("Candidate output must be empty; existing build was preserved.");
            const string resourceFolder = "Assets/_Game/Resources/QA", resourcePath = resourceFolder + "/VerticalSliceReference.asset";
            bool createdFolder = !AssetDatabase.IsValidFolder(resourceFolder);
            if (AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(resourcePath) != null) throw new BuildFailedException("QA NavMesh resource already exists; it was preserved.");
            try
            {
                if (createdFolder) AssetDatabase.CreateFolder("Assets/_Game/Resources", "QA");
                if (!AssetDatabase.CopyAsset(WorldSliceWalkabilityQa.NavAsset, resourcePath)) throw new BuildFailedException("Cannot package development-only reference NavMesh.");
                Directory.CreateDirectory(output);
                var scenes = new[] { WorldSliceBootstrapScaffolder.SliceBootstrap }.Concat(WorldIntegrationQa.PilotScenePaths()).ToArray();
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = scenes, locationPathName = Path.Combine(output, "FacilityOps_CidadeAntiga_VerticalSlice_v0_1.exe"), target = BuildTarget.StandaloneWindows64, options = BuildOptions.Development });
                if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0) throw new BuildFailedException("Candidate build failed: " + report.summary.result);
                File.WriteAllText(Path.Combine(output, "VERSION.txt"), "Facility Ops — Cidade Antiga Vertical Slice v0.1\nWindows x64 Development\nQA fingerprint: " + fingerprint + "\n");
                File.WriteAllText(Path.Combine(output, "Jogar_CidadeAntiga.bat"), "@echo off\r\ncd /d \"%~dp0\"\r\nstart \"\" \"FacilityOps_CidadeAntiga_VerticalSlice_v0_1.exe\" -worldSlice\r\n");
            }
            finally
            {
                AssetDatabase.DeleteAsset(resourcePath);
                if (createdFolder) AssetDatabase.DeleteAsset(resourceFolder);
            }
        }
    }
}
