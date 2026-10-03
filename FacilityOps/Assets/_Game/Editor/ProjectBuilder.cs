using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class ProjectBuilder
    {
        [MenuItem("Facility Ops/Preparar e compilar Windows")]
        public static void Build()
        {
            RunRules();
            Directory.CreateDirectory("Assets/_Game/Scenes");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            new GameObject("Bootstrap / Facility Ops").AddComponent<GameRuntime>();
            const string scenePath = "Assets/_Game/Scenes/Bootstrap.unity";
            EditorSceneManager.SaveScene(scene, scenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(scenePath, true) };
            PlayerSettings.companyName = "OficinaAurora";
            PlayerSettings.productName = "Facility Ops Prototype";
            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.runInBackground = true;
            PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            AssetDatabase.SaveAssets();
            string output = Path.GetFullPath("../Builds/Windows/FacilityOps.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { scenePath }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.Development
            });
            if (report.summary.result != BuildResult.Succeeded) throw new Exception("Windows build failed: " + report.summary.result);
            Debug.Log("FACILITY BUILD SUCCESS: " + output);
        }
        private static void Require(bool condition, string name)
        {
            if (!condition) throw new Exception("Rules failed: " + name);
            Debug.Log("RULE PASS: " + name);
        }
        public static void RunRules()
        {
            for (int cause = 0; cause < 3; cause++)
            {
                var session = new ServiceSession(new CareerData());
                Require(session.Accept((FailureCause)cause), "Accept " + cause);
                Require(!session.Accept(FailureCause.LightDriver), "Reject second active mission");
                session.Repair((StationId)cause);
                Require(!session.Active.repaired && session.Stock((FailureCause)cause) == 2, "Require diagnosis, preserve inventory");
                session.Verify(StationId.Distribution);
                Require(!session.Settle(out _), "Reject premature settlement");
                session.Diagnose((FailureCause)cause);
                Require(session.Active.diagnosis == -1, "Require evidence");
                session.Measure(StationId.Distribution, ToolMode.Scanner);
                session.Measure(StationId.Distribution, ToolMode.Scanner);
                Require(session.Active.testedNodes.Count == 1, "Deduplicate measurements");
                session.Measure(StationId.Controller, ToolMode.SignalProbe);
                int wrong = (cause + 1) % 3;
                session.Diagnose((FailureCause)wrong);
                session.Repair((StationId)wrong);
                Require(!session.Active.repaired && session.Active.mistakes == 1 && session.Stock((FailureCause)wrong) == 1, "Wrong repair consumes stock and preserves fault");
                session.Diagnose((FailureCause)cause);
                session.Repair((StationId)wrong);
                Require(session.Stock((FailureCause)wrong) == 1, "Wrong target consumes nothing");
                session.Repair((StationId)cause);
                Require(session.Active.repaired && session.Network.LightingHealthy, "Repair propagates network");
                Require(!session.Settle(out _), "Final test required");
                session.Verify(StationId.Controller);
                Require(!session.Active.validated, "Final test must use root node");
                session.Verify(StationId.Distribution);
                Require(session.Settle(out int paid) && paid == 290, "Penalty applied once");
                Require(!session.Settle(out _) && session.Career.money == 690, "Duplicate payment blocked");
            }
            var poor = new CareerData { money = 0, supplyParts = 0, relayParts = 0, driverParts = 0 };
            var credit = new ServiceSession(poor);
            credit.Accept(FailureCause.SupplyModule);
            Require(!credit.Buy(FailureCause.SupplyModule, false), "Buy restricted to hub");
            Require(credit.Buy(FailureCause.SupplyModule) && poor.supplierDebt == 60, "No bankruptcy softlock; supplier credit");
            credit.Measure(StationId.Distribution, ToolMode.Scanner); credit.Measure(StationId.Controller, ToolMode.SignalProbe);
            credit.Diagnose(FailureCause.SupplyModule); credit.Repair(StationId.Distribution); credit.Verify(StationId.Distribution);
            Require(credit.Settle(out int payment) && payment == 340 && poor.supplierDebt == 0, "Debt repaid on delivery");
            string qa = Path.GetFullPath("../Logs/rules-save.json");
            SaveService.Save(poor, qa);
            poor.money += 10;
            SaveService.Save(poor, qa);
            Require(SaveService.Load(qa).money == 350, "Save roundtrip and replacement");
            File.WriteAllText(qa, "broken json");
            Require(SaveService.Load(qa).money == 340, "Recover from backup");
            File.WriteAllText(Path.GetFullPath("../Logs/rules-passed.txt"), "Domain checks passed: all causes, invalid transitions, duplicate payouts, wrong repairs, inventory, debt recovery, save and backup.");
        }
    }
}
