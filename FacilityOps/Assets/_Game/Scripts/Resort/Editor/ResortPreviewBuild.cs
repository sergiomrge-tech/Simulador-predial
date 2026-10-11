using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace ResortAurora.EditorTools
{
    /// <summary>Explicit resort-only entry scene; never accidentally packages the Facility Ops bootstrap.</summary>
    public static class ResortPreviewBuild
    {
        public static void Run()
        {
            const string scene = "Assets/_Game/Scenes/ResortPrologue.unity";
            string output = Environment.GetEnvironmentVariable("RESORT_BUILD_OUTPUT");
            if (string.IsNullOrWhiteSpace(output))
                output = Path.Combine(@"D:\ProjectResort_Autonomy\Builds", "Resort_" + DateTime.Now.ToString("yyyyMMdd_HHmmss"), "SimuladorDeResort.exe");
            output = Path.GetFullPath(output);
            if (File.Exists(output)) throw new IOException("Refusing to overwrite an existing playable build: " + output);
            if (!File.Exists(scene))
                throw new InvalidOperationException("Playable ResortPrologue.unity missing.");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var previousName = PlayerSettings.productName;
            var previousWidth = PlayerSettings.defaultScreenWidth;
            var previousHeight = PlayerSettings.defaultScreenHeight;
            try
            {
                PlayerSettings.productName = "Simulador de Resort";
                PlayerSettings.defaultScreenWidth = 1920;
                PlayerSettings.defaultScreenHeight = 1080;
                BuildPlayerOptions options = new BuildPlayerOptions
                {
                    scenes = new[] { scene },
                    locationPathName = output,
                    target = BuildTarget.StandaloneWindows64,
                    options = BuildOptions.None
                };
                Debug.Log("RESORT_ONLY_BUILD_START scene=" + scene + " output=" + output);
                BuildReport report = BuildPipeline.BuildPlayer(options);
                if (report.summary.result != BuildResult.Succeeded)
                    throw new InvalidOperationException(
                        "Resort standalone build failed: " + report.summary.result +
                        " errors=" + report.summary.totalErrors +
                        " warnings=" + report.summary.totalWarnings);
                if (!File.Exists(output))
                    throw new IOException("Unity reported success but Resort EXE not found");
                Debug.Log("RESORT_ONLY_BUILD_SUCCESS path=" + output +
                          " bytes=" + new FileInfo(output).Length +
                          " totalSize=" + report.summary.totalSize +
                          " warnings=" + report.summary.totalWarnings +
                          " firstScene=" + scene);
            }
            finally
            {
                PlayerSettings.productName = previousName;
                PlayerSettings.defaultScreenWidth = previousWidth;
                PlayerSettings.defaultScreenHeight = previousHeight;
            }
        }
    }
}
