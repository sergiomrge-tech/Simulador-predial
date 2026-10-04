using System;
using System.Collections.Generic;
using System.Linq;
using FacilityOps;
using UnityEditor;
using UnityEngine;

namespace FacilityOps.Editor
{
    /// <summary>
    /// Turns the imported Horizonte door leaves and the pedestrian-gate leaf into <see cref="WorldDoor"/>s (kinematic body so the detailed leaf
    /// collider can swing, not static so it can move, closed by default). The stair-door leaves are authored propped open in the hero
    /// (W3.2 stair fix); their closed pose is the +-90 degree turn about the hinge that brings the leaf back into the frame, found geometrically
    /// so no axis convention is assumed. Runs inside the import pipeline, so a reimport keeps the interaction.
    /// </summary>
    public static class WorldDoorStamper
    {
        public static int StampActiveCell()
        {
            int count = 0;
            foreach (var root in UnityEngine.Object.FindObjectsByType<WorldCellRoot>(FindObjectsInactive.Include))
            {
                Transform architecture = root.transform.Find("Architecture");
                Transform hero = architecture != null ? architecture.Find("Hero_horizonte") : null;
                if (hero == null) continue;
                count += StampHorizonte(hero);
            }
            return count;
        }

        private static int StampHorizonte(Transform hero)
        {
            int count = 0;
            var filters = hero.GetComponentsInChildren<MeshFilter>(true);
            foreach (var f in filters.Where(m => m.name.EndsWith("_stair_door__leaf", StringComparison.Ordinal)))
            {
                string floor = f.name.Contains("__F03_") ? "F03" : "F00";
                Transform frame = f.transform.parent != null
                    ? f.transform.parent.GetComponentsInChildren<MeshFilter>(true).FirstOrDefault(m => m.name == f.name.Replace("__leaf", "__frame"))?.transform
                    : null;
                if (frame == null) throw new InvalidOperationException("Missing door frame for " + f.name);
                Quaternion authoredOpen = f.transform.localRotation;
                Quaternion closed = TurnTowards(f.transform, frame, new[] { 90f, -90f }, FrameDistance);
                Prepare(f.gameObject);
                var door = Ensure<WorldDoor>(f.gameObject);
                door.Configure("horizonte.stair." + floor, "[E] Abrir a porta da escada", "[E] Fechar a porta da escada", closed, authoredOpen, true, 20f);
                EditorUtility.SetDirty(door);
                count++;
            }
            MeshFilter gate = filters.FirstOrDefault(m => m.name.EndsWith("__ped_gate__leaf", StringComparison.Ordinal));
            if (gate != null)
            {
                Quaternion closed = gate.transform.localRotation;
                Quaternion open = TurnTowards(gate.transform, null, new[] { 100f, -100f }, NorthScore);   // swings into the forecourt (toward the building, +z)
                Prepare(gate.gameObject);
                var door = Ensure<WorldDoor>(gate.gameObject);
                door.Configure("horizonte.pedestrian_gate", "[E] Abrir o portão de pedestres", "[E] Fechar o portão de pedestres", closed, open, false, 30f);
                EditorUtility.SetDirty(door);
                count++;
                MeshFilter intercom = filters.FirstOrDefault(m => m.name.EndsWith("__intercom", StringComparison.Ordinal));
                if (intercom != null)
                {
                    var remote = Ensure<WorldDoorRemote>(intercom.gameObject);
                    remote.Configure(door, "[E] Interfone: abrir o portão");
                    EnsureCollider(intercom.gameObject);
                    EditorUtility.SetDirty(remote);
                    count++;
                }
            }
            else Debug.LogWarning("WORLD DOORS: pedestrian gate leaf not found in Hero_horizonte (old hero export?)");
            return count;
        }

        // Rotates the leaf about its own pivot (its hinge) around world up and returns the local rotation that scores best; the leaf is left in that pose.
        private static Quaternion TurnTowards(Transform leaf, Transform frame, float[] degrees, Func<Transform, Transform, float> score)
        {
            Vector3 pivot = leaf.position;
            Quaternion original = leaf.localRotation;
            Quaternion best = original; float bestScore = float.MaxValue;
            foreach (float d in degrees)
            {
                leaf.localRotation = original;
                leaf.RotateAround(pivot, Vector3.up, d);
                float s = score(leaf, frame);
                if (s < bestScore) { bestScore = s; best = leaf.localRotation; }
            }
            leaf.localRotation = original;
            return best;
        }
        private static float FrameDistance(Transform leaf, Transform frame) => Vector3.Distance(Center(leaf), Center(frame));
        private static float NorthScore(Transform leaf, Transform unused) => -Center(leaf).z;      // lower is better: the larger z (north), the better
        private static Vector3 Center(Transform t)
        {
            var renderers = t.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0) return t.position;
            Bounds b = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++) b.Encapsulate(renderers[i].bounds);
            return b.center;
        }

        private static void Prepare(GameObject go)
        {
            GameObjectUtility.SetStaticEditorFlags(go, 0);
            EnsureCollider(go);
            var body = Ensure<Rigidbody>(go);
            body.isKinematic = true; body.useGravity = false;
        }
        private static void EnsureCollider(GameObject go)
        {
            if (go.GetComponent<Collider>() != null) return;
            var filter = go.GetComponent<MeshFilter>();
            if (filter == null || filter.sharedMesh == null) return;
            var collider = Undo.AddComponent<MeshCollider>(go);
            collider.sharedMesh = filter.sharedMesh; collider.convex = false;
        }
        private static T Ensure<T>(GameObject go) where T : Component { var c = go.GetComponent<T>(); return c != null ? c : Undo.AddComponent<T>(go); }
    }
}
