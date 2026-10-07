using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
using UnityEngine.Rendering;

namespace ResortAurora.Game
{
    /// <summary>
    /// Optional skinned look for near and medium people: the free "Human Basic Motions" mannequins (Kevin Iglesias, Unity Asset Store) driven by a runtime
    /// playable graph (idle, walk, run, talk, cross-faded) and "dressed" by painting: each model gets one UV-remapped copy of its mesh in which every
    /// triangle belongs to a body region (torso, sleeves, shorts, legs, shoes, hair...), and every person gets a tiny palette texture that colours those
    /// regions, so the crowd keeps its variety at the cost of one material and no extra renderers.
    /// The licensed files live locally in <c>Assets/_Game/ThirdParty/Resources/HBM</c> and are not in the public repository: when they are missing
    /// <see cref="Available"/> is false and <see cref="PersonRig"/> keeps its procedural body, so a fresh clone still builds and runs.
    /// Sitting, lying, swimming and cycling stay procedural (the pack has no such clips).
    /// </summary>
    public sealed class HumanVisual : MonoBehaviour
    {
        public enum Clip { Idle1, Idle2, Walk, Run, Talk }

        // palette cells (one pixel each); a region is a part of the body that can be coloured on its own
        const int Skin = 0, Torso = 1, SleeveShort = 2, SleeveLong = 3, Forearm = 4, ShortsZone = 5, ThighLower = 6, Shin = 7, Foot = 8, HairTop = 9, HairBack = 10, Cells = 12;

        const string Folder = "HBM/";
        const float RefWalk = 1.45f, RefRun = 3.9f;       // ground speed (m/s) at which the clips play at 1x
        public const int MaxActive = 40;

        static bool probed, available;
        static readonly GameObject[] models = new GameObject[2];
        static readonly AnimationClip[][] clips = new AnimationClip[2][];
        static readonly Mesh[] painted = new Mesh[2];
        static int active;
        static Shader litShader;

        public static bool Available { get { Probe(); return available; } }
        public static int ActiveCount => active;

        static AnimationClip LoadClip(string name)
        {
            foreach (var c in Resources.LoadAll<AnimationClip>(Folder + name)) if (!c.name.StartsWith("__preview__")) return c;
            return null;
        }

        static void Probe()
        {
            if (probed) return;
            probed = true;
            string[] names = { "Idle01", "Idle02", "Walk01_Forward", "Run01_Forward", "Talk01" };
            for (int g = 0; g < 2; g++)
            {
                char c = g == 0 ? 'M' : 'F';
                models[g] = Resources.Load<GameObject>(Folder + "Human" + c + "_Model");
                clips[g] = new AnimationClip[names.Length];
                for (int i = 0; i < names.Length; i++) clips[g][i] = LoadClip("Human" + c + "@" + names[i]);
                if (models[g] == null) return;
                foreach (var cl in clips[g]) if (cl == null) return;
            }
            available = true;
        }

        public struct Look
        {
            public Color skin, hair, shirt, bottom, shoes;
            public bool shirtless, bareLegs, longSleeves, longHair, hasHair, female;
            public float scale;
        }

        Animator animator;
        SkinnedMeshRenderer[] skinned;
        PlayableGraph graph;
        AnimationMixerPlayable mixer;
        AnimationClipPlayable[] players;
        float[] weights;
        Clip target = Clip.Idle1;
        bool counted, built;

        public Clip Current => target;
        public bool Shown => gameObject.activeSelf;
        public Animator Animator => animator;
        public float ClipTime => players != null ? (float)players[(int)target].GetTime() : -1f;

        /// <summary>Instantiates the mannequin under <paramref name="rig"/> and paints it. The root of the rig stands at the feet.</summary>
        public static HumanVisual Create(Transform rig, Look look, System.Random rng)
        {
            if (!Available) return null;
            int g = look.female ? 1 : 0;
            var root = new GameObject("HumanVisual"); root.transform.SetParent(rig, false);
            var hv = root.AddComponent<HumanVisual>();
            var model = Instantiate(models[g], root.transform);
            model.name = "Mannequin"; model.transform.localPosition = Vector3.zero; model.transform.localRotation = Quaternion.identity;
            hv.animator = model.GetComponent<Animator>();
            if (hv.animator == null) hv.animator = model.GetComponentInChildren<Animator>();
            if (hv.animator == null || !hv.animator.isHuman) { Destroy(root); return null; }
            hv.animator.applyRootMotion = false;
            hv.animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;            // culled animators freeze their playable graph; the LOD already hides far people
            hv.animator.runtimeAnimatorController = null;
            hv.skinned = hv.animator.GetComponentsInChildren<SkinnedMeshRenderer>();
            hv.Paint(look, g);
            hv.BuildGraph(g, rng);
            hv.built = true;
            root.SetActive(false);
            return hv;
        }

        // ---------------------------------------------------------------- painting

        /// <summary>Body region of a vertex from its dominant bone and where it sits along that bone (bind pose, world space).</summary>
        static int RegionOf(HumanBodyBones bone, Vector3 p, Animator an, Vector3 headCenter, Vector3 headSize, Vector3 fwd)
        {
            float Along(HumanBodyBones a, HumanBodyBones b)
            {
                var ta = an.GetBoneTransform(a); var tb = an.GetBoneTransform(b); if (ta == null || tb == null) return 0f;
                var d = tb.position - ta.position; float len = d.magnitude; return len < 1e-4f ? 0f : Vector3.Dot(p - ta.position, d) / (len * len);
            }
            switch (bone)
            {
                case HumanBodyBones.Hips: return ShortsZone;
                case HumanBodyBones.Spine: case HumanBodyBones.Chest: case HumanBodyBones.UpperChest:
                case HumanBodyBones.LeftShoulder: case HumanBodyBones.RightShoulder: return Torso;
                case HumanBodyBones.Neck: return Skin;
                case HumanBodyBones.Head:
                {
                    float top = headCenter.y + headSize.y * 0.5f;
                    if (p.y > top - headSize.y * 0.40f) return HairTop;
                    if (p.y > headCenter.y - headSize.y * 0.25f && Vector3.Dot(p - headCenter, fwd) < -headSize.z * 0.18f) return HairBack;
                    return Skin;
                }
                case HumanBodyBones.LeftUpperArm: return Along(HumanBodyBones.LeftUpperArm, HumanBodyBones.LeftLowerArm) < 0.5f ? SleeveShort : SleeveLong;
                case HumanBodyBones.RightUpperArm: return Along(HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm) < 0.5f ? SleeveShort : SleeveLong;
                case HumanBodyBones.LeftLowerArm: case HumanBodyBones.RightLowerArm: return Forearm;
                case HumanBodyBones.LeftUpperLeg: return Along(HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg) < 0.5f ? ShortsZone : ThighLower;
                case HumanBodyBones.RightUpperLeg: return Along(HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg) < 0.5f ? ShortsZone : ThighLower;
                case HumanBodyBones.LeftLowerLeg: case HumanBodyBones.RightLowerLeg: return Shin;
                case HumanBodyBones.LeftFoot: case HumanBodyBones.RightFoot: case HumanBodyBones.LeftToes: case HumanBodyBones.RightToes: return Foot;
                default: return Skin;
            }
        }

        /// <summary>One copy of the model's mesh per gender with every triangle's UVs pointing at its region's palette cell (vertices are split where regions meet).</summary>
        Mesh BuildPainted(int g, SkinnedMeshRenderer smr)
        {
            var src = smr.sharedMesh;
            if (!src.isReadable) { Debug.LogWarning("HumanVisual: mannequin mesh is not readable; people keep the plain mannequin colour"); return null; }
            var byBone = new Dictionary<Transform, HumanBodyBones>();
            for (int i = 0; i < (int)HumanBodyBones.LastBone; i++) { var t = animator.GetBoneTransform((HumanBodyBones)i); if (t != null && !byBone.ContainsKey(t)) byBone[t] = (HumanBodyBones)i; }
            var baked = new Mesh(); smr.BakeMesh(baked, false);
            var world = baked.vertices; for (int i = 0; i < world.Length; i++) world[i] = smr.transform.TransformPoint(world[i]);
            Destroy(baked);
            var bws = src.boneWeights; var bones = smr.bones; int vc = src.vertexCount;
            var boneOf = new HumanBodyBones[vc];
            for (int i = 0; i < vc; i++) boneOf[i] = byBone.TryGetValue(bones[bws[i].boneIndex0], out var hb) ? hb : HumanBodyBones.LastBone;

            // head box from the head-owned vertices (for the hair cap and the back of the head)
            var headBox = new Bounds(animator.GetBoneTransform(HumanBodyBones.Head).position, new Vector3(0.18f, 0.24f, 0.2f)); bool any = false;
            for (int i = 0; i < vc; i++)
                if (boneOf[i] == HumanBodyBones.Head) { if (!any) { headBox = new Bounds(world[i], Vector3.zero); any = true; } else headBox.Encapsulate(world[i]); }
            var fwd = transform.forward;

            var vertRegion = new int[vc];
            for (int i = 0; i < vc; i++) vertRegion[i] = RegionOf(boneOf[i], world[i], animator, headBox.center, headBox.size, fwd);

            // split vertices per (original vertex, region)
            var map = new Dictionary<long, int>(); var verts = new List<Vector3>(vc); var norms = new List<Vector3>(vc); var tans = new List<Vector4>(vc);
            var bw = new List<BoneWeight>(vc); var uvs = new List<Vector2>(vc);
            var vv = src.vertices; var nn = src.normals; var tt = src.tangents; bool hasN = nn.Length == vc, hasT = tt.Length == vc;
            int Remap(int vi, int region)
            {
                long key = ((long)vi << 8) | (uint)region;
                if (map.TryGetValue(key, out int ni)) return ni;
                ni = verts.Count; map[key] = ni;
                verts.Add(vv[vi]); if (hasN) norms.Add(nn[vi]); if (hasT) tans.Add(tt[vi]); bw.Add(bws[vi]);
                uvs.Add(new Vector2((region + 0.5f) / Cells, 0.5f));
                return ni;
            }
            var mesh = new Mesh { name = src.name + "_painted" + (g == 0 ? "M" : "F"), indexFormat = IndexFormat.UInt32 };
            var subTris = new List<int[]>();
            for (int sm = 0; sm < src.subMeshCount; sm++)
            {
                var tri = src.GetTriangles(sm); var outTris = new List<int>(tri.Length);
                for (int t = 0; t + 2 < tri.Length; t += 3)
                {
                    int r0 = vertRegion[tri[t]], r1 = vertRegion[tri[t + 1]], r2 = vertRegion[tri[t + 2]];
                    int region = r0 == r1 || r0 == r2 ? r0 : r1 == r2 ? r1 : r0;      // majority of the corners
                    outTris.Add(Remap(tri[t], region)); outTris.Add(Remap(tri[t + 1], region)); outTris.Add(Remap(tri[t + 2], region));
                }
                subTris.Add(outTris.ToArray());
            }
            mesh.SetVertices(verts); if (hasN) mesh.SetNormals(norms); if (hasT) mesh.SetTangents(tans); mesh.SetUVs(0, uvs);
            mesh.subMeshCount = subTris.Count;
            for (int sm = 0; sm < subTris.Count; sm++) mesh.SetTriangles(subTris[sm], sm);
            mesh.boneWeights = bw.ToArray(); mesh.bindposes = src.bindposes; mesh.bounds = src.bounds;
            var count = new int[Cells]; foreach (var r in vertRegion) count[r]++;
            Debug.Log($"HumanVisual painted mesh {mesh.name}: {vc} -> {verts.Count} vertices, {src.subMeshCount} submesh(es), {smr.bones.Length} bones, head {headBox.size}, region vertex counts [{string.Join(",", count)}]");
            return mesh;
        }

        static Texture2D Palette(Look l)
        {
            var c = new Color[Cells];
            for (int i = 0; i < Cells; i++) c[i] = l.skin;
            c[Torso] = l.shirtless ? l.skin : l.shirt;
            c[SleeveShort] = l.shirtless ? l.skin : l.shirt;
            c[SleeveLong] = l.shirtless || !l.longSleeves ? l.skin : l.shirt;
            c[Forearm] = l.shirtless || !l.longSleeves ? l.skin : l.shirt;
            c[ShortsZone] = l.bottom;
            c[ThighLower] = l.bareLegs ? l.skin : l.bottom;
            c[Shin] = l.bareLegs ? l.skin : l.bottom;
            c[Foot] = l.bareLegs ? l.skin : l.shoes;
            c[HairTop] = l.hasHair ? l.hair : l.skin;
            c[HairBack] = l.longHair || l.hasHair ? l.hair : l.skin;
            var tex = new Texture2D(Cells, 1, TextureFormat.RGBA32, false, false) { filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp, name = "HumanPalette" };
            tex.SetPixels(c); tex.Apply(false, true);
            return tex;
        }

        void Paint(Look l, int g)
        {
            // normalise the mannequin to a 1.74 m body (the rig's own scale then gives each person their height)
            float modelHeight = 0f;
            foreach (var r in skinned) modelHeight = Mathf.Max(modelHeight, r.bounds.size.y);
            if (modelHeight < 0.5f) modelHeight = 1.8f;
            transform.localScale = Vector3.one * Mathf.Clamp(1.74f / Mathf.Max(0.5f, modelHeight), 0.3f, 3f);

            if (painted[g] == null && skinned.Length > 0) painted[g] = BuildPainted(g, skinned[0]);
            if (litShader == null) litShader = Shader.Find("Universal Render Pipeline/Lit");
            var mat = new Material(litShader) { name = "HumanPainted" };
            mat.SetTexture("_BaseMap", Palette(l)); mat.SetColor("_BaseColor", Color.white); mat.SetFloat("_Smoothness", 0.18f);
            for (int i = 0; i < skinned.Length; i++)
            {
                if (painted[g] != null && i == 0) skinned[i].sharedMesh = painted[g];
                skinned[i].sharedMaterial = mat; skinned[i].updateWhenOffscreen = false;
            }
        }

        // ---------------------------------------------------------------- animation

        void BuildGraph(int g, System.Random rng)
        {
            graph = PlayableGraph.Create("Human");
            graph.SetTimeUpdateMode(DirectorUpdateMode.GameTime);
            var output = AnimationPlayableOutput.Create(graph, "Anim", animator);
            var cl = clips[g];
            mixer = AnimationMixerPlayable.Create(graph, cl.Length);
            players = new AnimationClipPlayable[cl.Length]; weights = new float[cl.Length];
            for (int i = 0; i < cl.Length; i++)
            {
                players[i] = AnimationClipPlayable.Create(graph, cl[i]);
                players[i].SetApplyFootIK(false);
                players[i].SetTime(rng.NextDouble() * cl[i].length);                       // out of step with the neighbours
                graph.Connect(players[i], 0, mixer, i);
                mixer.SetInputWeight(i, 0f);
            }
            weights[(int)Clip.Idle1] = 1f; mixer.SetInputWeight((int)Clip.Idle1, 1f);
            output.SetSourcePlayable(mixer);
            graph.Play();
        }

        /// <summary>Chooses the clip for this instant and eases the others out. <paramref name="speed"/> (m/s) sets the playback rate of walk and run.</summary>
        public void Drive(Clip clip, float speed, float dt, float variety)
        {
            if (!built) return;
            target = clip;
            for (int i = 0; i < weights.Length; i++)
            {
                float goal = i == (int)clip ? 1f : 0f;
                weights[i] = Mathf.MoveTowards(weights[i], goal, dt * 4f);
                mixer.SetInputWeight(i, weights[i]);
            }
            players[(int)Clip.Walk].SetSpeed(Mathf.Clamp(speed / RefWalk, 0.6f, 1.6f));
            players[(int)Clip.Run].SetSpeed(Mathf.Clamp(speed / RefRun, 0.7f, 1.5f));
            players[(int)Clip.Idle1].SetSpeed(0.9f + variety * 0.2f); players[(int)Clip.Idle2].SetSpeed(0.9f + variety * 0.2f);
        }

        public void SetShadows(bool on)
        {
            var mode = on ? ShadowCastingMode.On : ShadowCastingMode.Off;
            foreach (var r in skinned) r.shadowCastingMode = mode;
        }

        public void Show(bool on)
        {
            if (!built || gameObject.activeSelf == on) return;
            gameObject.SetActive(on);
            if (on) { graph.Play(); if (!counted) { counted = true; active++; } }
            else { graph.Stop(); if (counted) { counted = false; active--; } }
        }

        void OnDestroy()
        {
            if (counted) { counted = false; active--; }
            if (graph.IsValid()) graph.Destroy();
        }
    }
}
