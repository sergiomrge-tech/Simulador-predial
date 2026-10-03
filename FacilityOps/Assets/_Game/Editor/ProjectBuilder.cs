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
            RunPrologueRules();
            RunChapterOneRules();
            File.WriteAllText(Path.GetFullPath("../Logs/rules-passed.txt"), "Domain checks passed: all causes, invalid transitions, duplicate payouts, wrong repairs, inventory, debt recovery, save and backup. Authored prologue: thermal recurrence, isolation, safety confirmation, restoration, stable final test, persistent journal and legacy-save compatibility. Chapter I: order, isolation, separate hydraulic stock/credit, faucet diagnosis, component confirmation, authored rewards, building history, persistence and reputation-gated recommendation.");
        }
        private static void RunPrologueRules()
        {
            var s = new ServiceSession(new CareerData());
            Require(s.AcceptPrologue() && s.IsPrologue && !s.Network.LightingHealthy, "Prologue starts with tripped breaker");
            Require(!s.AcceptPrologue(), "Single active prologue");
            s.Restore(StationId.Distribution);
            Require(s.Network.LightingHealthy, "Rearm briefly clears the symptom");
            s.Tick(4f); s.Restore(StationId.Distribution); s.Tick(1f);
            Require(!s.Network.LightingHealthy && !s.Active.repaired, "Heat reproduces short; repeated restore cannot reset test");
            s.Measure(StationId.Distribution, ToolMode.Scanner); s.Measure(StationId.Luminaire, ToolMode.SignalProbe);
            s.Diagnose(FailureCause.LightDriver);
            Require(s.Active.diagnosis == -1, "Authored defect must be inspected");
            s.Inspect(StationId.Luminaire); s.Diagnose(FailureCause.LightDriver);
            s.Repair(StationId.Luminaire);
            Require(!s.Active.repaired && s.Career.driverParts == 2, "Tripped protection is not confirmed isolation");
            s.Isolate(StationId.Controller);
            Require(!s.Active.isolated, "Isolation requires QD-01");
            s.Isolate(StationId.Distribution); s.Repair(StationId.Luminaire);
            Require(!s.Active.repaired && s.Career.driverParts == 2, "Isolation alone does not permit repair");
            s.Verify(StationId.Luminaire);
            string path = Path.GetFullPath("../Logs/prologue-save.json");
            SaveService.Save(s.Career,path);
            s = new ServiceSession(SaveService.Load(path));
            Require(s.Active.isolated && s.Active.insulationTested && s.Active.diagnosis == 2, "Resume isolated service without losing safety confirmation");
            s.Repair(StationId.Luminaire);
            Require(s.Active.repaired && !s.Network.LightingHealthy && s.Career.driverParts == 1, "Repair consumes one module but keeps circuit isolated");
            s.Verify(StationId.Distribution);
            Require(!s.Active.validated && !s.Settle(out _), "Cannot deliver with circuit isolated");
            s.Restore(StationId.Distribution); s.Verify(StationId.Distribution);
            Require(!s.Active.validated, "Restoration requires thermal soak");
            s.Tick(5f); s.Verify(StationId.Distribution);
            Require(s.Active.validated, "Repaired circuit survives thermal test");
            s.Isolate(StationId.Distribution);
            Require(!s.Active.validated && !s.Settle(out _), "New isolation invalidates final verification");
            s.Restore(StationId.Distribution); s.Tick(5f); s.Verify(StationId.Distribution);
            Require(s.Settle(out int paid) && paid == 400 && s.Career.prologueCompleted, "Prologue paid once and chapter frontier persisted");
            Require(!s.AcceptPrologue() && !s.Settle(out _), "Cannot replay prologue or duplicate reward");
            SaveService.Save(s.Career,path);
            var saved = SaveService.Load(path);
            Require(saved.prologueCompleted && saved.campaignJournal.Count == 5 && saved.active == null, "Mentor/client journal and completion survive load");
            File.WriteAllText(path,"{\"version\":1,\"money\":200,\"completed\":2,\"supplyParts\":1,\"relayParts\":1,\"driverParts\":1}");
            var legacy = SaveService.Load(path);
            Require(legacy.money == 200 && legacy.completed == 2 && !legacy.prologueCompleted && legacy.campaignJournal != null, "Old v1 careers retain rewards and can start authored prologue");
        }
        private static void CompleteChapterJob(ServiceSession s,ServiceDefinition job)
        {
            Require(s.AcceptChapterOne(job.id),"Accept authored job " + job.id);
            foreach (StationId node in Enum.GetValues(typeof(StationId))) s.Inspect(node);
            s.Measure(StationId.Distribution,ToolMode.Scanner); s.Measure(StationId.Luminaire,ToolMode.SignalProbe);
            s.Diagnose(job.cause); s.Repair((StationId)job.cause);
            Require(!s.Active.repaired,"Chapter repair requires isolation");
            s.Isolate(StationId.Distribution); s.Verify((StationId)job.cause); s.Repair((StationId)job.cause);
            Require(s.Active.repaired && !s.Network.LightingHealthy,"Chapter replacement preserves isolation");
            s.Restore(StationId.Distribution); s.Verify(StationId.Distribution);
            Require(!s.Active.validated,"Chapter final test needs stable restored state");
            s.Tick(3f); s.Verify(StationId.Distribution);
            Require(s.Settle(out int paid) && paid==job.basePay+job.cleanBonus,"Authored payment and result recorded");
        }
        private static void RunChapterOneRules()
        {
            var locked = new ServiceSession(new CareerData());
            Require(!locked.AcceptChapterOne(ChapterOne.Jobs[0].id),"Chapter I requires prologue");
            var s = new ServiceSession(new CareerData { prologueCompleted=true, reputation=0 });
            Require(!s.AcceptChapterOne(ChapterOne.Jobs[1].id),"Authored services preserve order");
            foreach(var job in ChapterOne.Jobs)CompleteChapterJob(s,job);
            Require(s.NextJob==null && s.Career.buildingHistory.Count==3 && !s.Career.recurringContractUnlocked,"Three records persist; low reputation delays recommendation");
            Require(s.Career.supplyParts==1 && s.Career.relayParts==1 && s.Career.driverParts==2 && s.Career.sealKits==1,"Hydraulic kit is independent of electrical stock");
            Require(!s.AcceptChapterOne(ChapterOne.Jobs[0].id) && !s.Settle(out _),"Authored rewards cannot be repeated");
            string path=Path.GetFullPath("../Logs/chapter-one-save.json");
            SaveService.Save(s.Career,path); s=new ServiceSession(SaveService.Load(path));
            Require(s.Career.completedChapterOneJobs.Count==3 && s.Career.buildingHistory.Count==3,"Chapter progress and building memory roundtrip");
            for(int i=0;i<2;i++)
            {
                s.Accept(FailureCause.LightDriver);
                s.Measure(StationId.Distribution,ToolMode.Scanner);s.Measure(StationId.Luminaire,ToolMode.SignalProbe);
                s.Diagnose(FailureCause.LightDriver);s.Repair(StationId.Luminaire);s.Verify(StationId.Distribution);s.Settle(out _);
            }
            Require(s.Career.recurringContractUnlocked && s.Career.completedChapterOneJobs.Count==3,"Free services recover reputation without faking chapter progress");
            var water=new ServiceSession(new CareerData { prologueCompleted=true, money=0, sealKits=0, completedChapterOneJobs=new System.Collections.Generic.List<string>{ChapterOne.Jobs[0].id,ChapterOne.Jobs[1].id} });
            water.AcceptChapterOne(ChapterOne.Jobs[2].id);
            Require(water.Network.Read(StationId.Luminaire,ToolMode.SignalProbe).Contains("12 UF"),"Residual flow identifies faucet seal");
            Require(!water.BuySealKit(false) && water.BuySealKit(true) && water.Career.supplierDebt==50,"Hydraulic credit avoids stock softlock and stays at hub");
            water.Inspect(StationId.Luminaire);water.Measure(StationId.Distribution,ToolMode.Scanner);water.Measure(StationId.Luminaire,ToolMode.SignalProbe);
            water.Diagnose(FailureCause.LightDriver);water.Isolate(StationId.Distribution);water.Verify(StationId.Luminaire);
            SaveService.Save(water.Career,path);water=new ServiceSession(SaveService.Load(path));
            Require(water.Active.isolated && water.Active.insulationTested && water.Career.sealKits==1,"Hydraulic isolated visit resumes safely");
            water.Diagnose(FailureCause.ControlRelay);water.Repair(StationId.Controller);
            Require(!water.Active.repaired && water.Career.sealKits==1,"Changing hydraulic diagnosis invalidates component confirmation");
            water.Diagnose(FailureCause.LightDriver);water.Verify(StationId.Luminaire);water.Repair(StationId.Luminaire);water.Restore(StationId.Distribution);water.Tick(3);water.Verify(StationId.Distribution);
            Require(water.Settle(out int paid) && paid==290 && water.Career.supplierDebt==0,"Hydraulic credit repaid on delivery");
        }
    }
}
