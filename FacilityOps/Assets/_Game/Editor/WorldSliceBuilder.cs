using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class WorldSliceBuilder
    {
        private const string BootstrapScene = WorldSliceBootstrapScaffolder.SliceBootstrap;

        [MenuItem("Facility Ops/Build Cidade Antiga Vertical Slice v0.1")]
        public static void Build()
        {
            WorldIntegrationQa.RunPilotGate(false);

            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(BootstrapScene) == null)
                throw new BuildFailedException("Bootstrap scene missing: " + BootstrapScene);

            string[] cells = WorldIntegrationQa.PilotScenePaths();
            var scenes = new List<string>(1 + cells.Length) { BootstrapScene };
            scenes.AddRange(cells);

            string outputDirectory = Path.GetFullPath(
                Path.Combine(Application.dataPath, "..", "..", "Builds", "Windows", "CidadeAntiga_v0_1"));
            Directory.CreateDirectory(outputDirectory);
            string executable = Path.Combine(outputDirectory, "FacilityOps_CidadeAntiga_v0_1.exe");

            var options = new BuildPlayerOptions
            {
                scenes = scenes.ToArray(),
                locationPathName = executable,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.Development
            };

            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException(
                    $"Cidade Antiga vertical slice build failed: {report.summary.result}");

            string launcherPath = Path.Combine(outputDirectory, "Jogar_CidadeAntiga.bat");
            File.WriteAllText(
                launcherPath,
                "@echo off\r\n" +
                "cd /d \"%~dp0\"\r\n" +
                "start \"\" \"FacilityOps_CidadeAntiga_v0_1.exe\" -worldSlice\r\n");

            string summaryPath = Path.Combine(outputDirectory, "BUILD_SUMMARY.txt");
            File.WriteAllText(
                summaryPath,
                "Facility Ops — Cidade Antiga Vertical Slice v0.1\n" +
                $"Unity: {Application.unityVersion}\n" +
                $"Scenes: {scenes.Count}\n" +
                $"Size bytes: {report.summary.totalSize}\n" +
                $"Build time: {report.summary.totalTime}\n" +
                $"Warnings: {report.summary.totalWarnings}\n" +
                $"Errors: {report.summary.totalErrors}\n" +
                "Runtime mode: -worldSlice\n" +
                "Launcher: Jogar_CidadeAntiga.bat\n");

            Debug.Log(
                "CIDADE ANTIGA VERTICAL SLICE BUILD SUCCESS: " + executable);
        }
    }
}
