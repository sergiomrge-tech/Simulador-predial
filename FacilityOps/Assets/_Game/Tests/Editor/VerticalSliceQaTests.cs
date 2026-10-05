using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FacilityOps.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.TestTools;

namespace FacilityOps.Tests
{
    public sealed class VerticalSliceQaTests
    {
        [Test]
        public void UnavailableCountersNeverBecomeMeasuredZero()
        {
            var counter = new VerticalSliceCounter(); counter.Observe(false, 0); counter.Observe(true, -1);
            Assert.That(counter.Mean("calls").status, Is.EqualTo("INDISPONÍVEL"));
            Assert.That(counter.Mean("calls").value, Is.Null);
            counter.Observe(true, 0); Assert.That(counter.Mean("bytes").status, Is.EqualTo("MEDIDO"));
            Assert.That(counter.Mean("bytes").value, Is.EqualTo("0.000")); // Genuine zero allocation is valid.
        }
        [Test]
        public void DeliveryRequiresAllEvidenceAndWarningsDoNotBlock()
        {
            var items = VerticalSliceDeliveryGate.Required.Select(id => new VerticalSliceQaItem(id, "PASS", "test")).ToList();
            Assert.That(VerticalSliceDeliveryGate.Ready(items), Is.True);
            items.Add(new VerticalSliceQaItem("performance", "WARNING", "below 60"));
            Assert.That(VerticalSliceDeliveryGate.Ready(items), Is.True);
            items.RemoveAll(i => i.id == "player"); Assert.That(VerticalSliceDeliveryGate.Ready(items), Is.False);
            items.Add(new VerticalSliceQaItem("player", "FAIL", "crash")); Assert.That(VerticalSliceDeliveryGate.Ready(items), Is.False);
        }
        [Test]
        public void ContinuousRouteRejectsMidRouteTeleportAndDisconnectedLegs()
        {
            WorldSliceQaWalker.Step Place() => new WorldSliceQaWalker.Step { kind = "teleport", corners = new[] { new WorldSliceQaWalker.Vec3(Vector3.zero) } };
            var walk = new WorldSliceQaWalker.Step { kind = "walk", corners = new[] { new WorldSliceQaWalker.Vec3(Vector3.zero), new WorldSliceQaWalker.Vec3(Vector3.right * 3) } };
            var route = new WorldSliceQaWalker.Route { version = 1, steps = new[] { Place(), walk } };
            Assert.DoesNotThrow(() => VerticalSlicePlayerQa.ValidateRoute(route));
            route.steps = new[] { Place(), walk, Place() }; Assert.Throws<InvalidDataException>(() => VerticalSlicePlayerQa.ValidateRoute(route));
            route.steps = new[] { Place(), walk, walk }; Assert.Throws<InvalidDataException>(() => VerticalSlicePlayerQa.ValidateRoute(route));
        }
        [Test]
        public void MissingNavMeshReportsExactFailingEndpoint()
        {
            var point = new Vector3(1000000, 1000000, 1000000);
            var leg = VerticalSliceQaRunner.PlanLeg("missing", point, point + Vector3.right, new HashSet<string>());
            Assert.That(leg.status, Is.EqualTo("FAIL")); Assert.That(leg.failurePosition, Is.EqualTo(point));
            Assert.That(leg.failure, Does.Contain("start"));
        }
        [UnityTest, Timeout(1500000)]
        public IEnumerator ContinuousPlayerControllerRouteWithoutMidRouteTeleport()
        {
            if (Environment.GetEnvironmentVariable("VERTICAL_SLICE_CONTINUOUS_QA") != "1") Assert.Ignore("Opt-in current-map continuous physical route. Run VerticalSliceQaRunner first.");
            Assert.That(File.Exists(VerticalSliceQaRunner.RoutePath), Is.True, "Static runner did not produce a valid route");
            EditorSceneManager.OpenScene(WorldSliceBootstrapScaffolder.SliceBootstrap, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            var bridge = UnityEngine.Object.FindAnyObjectByType<WorldSliceRuntimeBridge>();
            float deadline = Time.realtimeSinceStartup + 90f;
            while (!bridge.Active && Time.realtimeSinceStartup < deadline) yield return null;
            Assert.That(bridge.Active, Is.True);
            var nav = AssetDatabase.LoadAssetAtPath<NavMeshData>(WorldSliceWalkabilityQa.NavAsset); Assert.That(nav, Is.Not.Null);
            var instance = NavMesh.AddNavMeshData(nav);
            var harness = new GameObject("Continuous QA harness").AddComponent<VerticalSlicePlayerQa>();
            var route = JsonUtility.FromJson<WorldSliceQaWalker.Route>(File.ReadAllText(VerticalSliceQaRunner.RoutePath));
            var profiler = harness.gameObject.AddComponent<VerticalSliceProfiler>();
            var service = UnityEngine.Object.FindAnyObjectByType<WorldStreamService>(); profiler.Configure(service);
            try
            {
                yield return harness.Run(UnityEngine.Object.FindAnyObjectByType<GameRuntime>(), service,
                    UnityEngine.Object.FindAnyObjectByType<WorldStreamingDebugOverlay>(), route, VerticalSliceQaRunner.EvidenceFolder,
                    WorldSliceBuildGate.Fingerprint(), "EDITOR", null, (file, aim) => { }); // No Player screenshots claimed by an Editor test.
                profiler.Write(Path.Combine(VerticalSliceQaRunner.EvidenceFolder, "EditorMetrics"));
            }
            finally { instance.Remove(); }
            string result = harness.Result.status, failure = harness.Result.failure;
            yield return new ExitPlayMode();
            Assert.That(result, Is.EqualTo("PASS"), failure);
        }
        [UnityTest]
        public IEnumerator ProfilerLifecycleKeepsEditorRenderCountersUnavailable()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            yield return new EnterPlayMode();
            var go = new GameObject("Profiler lifecycle QA — no career");
            var service = go.AddComponent<WorldStreamService>();
            var profiler = go.AddComponent<VerticalSliceProfiler>(); profiler.Configure(service);
            for (int i = 0; i < 10; i++) yield return null;
            var result = profiler.Snapshot();
            Assert.That(result.frames, Is.GreaterThan(0));
            Assert.That(result.drawCalls.status, Is.EqualTo("INDISPONÍVEL"));
            Assert.That(result.memoryBytes.status, Is.EqualTo("MEDIDO"));
            Assert.That(result.maxLoadMs.status, Is.EqualTo("INDISPONÍVEL"));
            UnityEngine.Object.Destroy(go);
            yield return null;
            yield return new ExitPlayMode();
        }
    }
}
