using System;
using System.Collections;
using FacilityOps.Editor;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace FacilityOps.Tests
{
    public sealed class WorldSliceNormalModeTests
    {
        [UnityTest]
        public IEnumerator Without_WorldSlice_Procedural_Runtime_Remains_Active()
        {
            if (Environment.GetEnvironmentVariable("FACILITY_NORMAL_QA") != "1") Assert.Ignore("Opt-in normal-mode Play Mode regression gate.");
            Assert.That(Environment.GetCommandLineArgs(), Does.Not.Contain("-worldSlice"));
            EditorSceneManager.OpenScene(WorldSliceBootstrapScaffolder.SliceBootstrap, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            for (int i = 0; i < 20; i++) yield return null;
            var game = UnityEngine.Object.FindAnyObjectByType<GameRuntime>();
            var bridge = UnityEngine.Object.FindAnyObjectByType<WorldSliceRuntimeBridge>();
            var service = UnityEngine.Object.FindAnyObjectByType<WorldStreamService>();
            Assert.That(game.Player, Is.Not.Null);
            Assert.That(game.World.Root.activeSelf, Is.True);
            Assert.That(game.Player.transform.position.magnitude, Is.LessThan(20f));
            Assert.That(bridge.Active, Is.False);
            Assert.That(service.StreamingEnabled, Is.False);
            Assert.That(SceneManager.sceneCount, Is.EqualTo(1));
            Assert.That(UnityEngine.Object.FindObjectsByType<OfficeTerminal>(FindObjectsSortMode.None).Length, Is.GreaterThan(0));
            yield return new ExitPlayMode();
        }
    }
}
