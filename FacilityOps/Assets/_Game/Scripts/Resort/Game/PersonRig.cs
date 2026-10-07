using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Game
{
    public enum PersonKind { Casual, Beach, Active, Kid, Staff }
    public enum Pose { Stand, Walk, Run, SitSand, SitChair, LieBack, LieFront, Swim, Bike }
    public enum Gesture { None, Phone, Drink, Chat, Dig, Hit }

    /// <summary>
    /// A procedural person (prototype art, scaled 1.55-1.88 m): torso, head, hair, arms and two-segment legs, with a few palette-driven looks
    /// (skin, hair, clothes) so a crowd does not clone. Poses are driven by joint angles, so walking, running, sitting, lying, swimming and
    /// pedalling cost a handful of rotations. <see cref="SetLod"/> hides parts with distance (arms and shins first), which is what keeps a
    /// beach full of people cheap. The root sits at the feet.
    /// </summary>
    public sealed class PersonRig : MonoBehaviour
    {
        static readonly Color[] Skins =
        {
            new Color(0.96f, 0.80f, 0.69f), new Color(0.90f, 0.70f, 0.55f), new Color(0.78f, 0.57f, 0.42f),
            new Color(0.63f, 0.44f, 0.32f), new Color(0.46f, 0.31f, 0.22f), new Color(0.34f, 0.22f, 0.16f),
        };
        static readonly Color[] Hairs =
        {
            new Color(0.08f, 0.06f, 0.05f), new Color(0.22f, 0.14f, 0.09f), new Color(0.42f, 0.27f, 0.14f), new Color(0.72f, 0.56f, 0.28f), new Color(0.55f, 0.55f, 0.56f),
        };
        static readonly Color[] Shirts =
        {
            new Color(0.95f, 0.95f, 0.93f), new Color(0.12f, 0.12f, 0.14f), new Color(0.85f, 0.25f, 0.22f), new Color(0.95f, 0.78f, 0.20f),
            new Color(0.20f, 0.50f, 0.78f), new Color(0.22f, 0.62f, 0.45f), new Color(0.92f, 0.52f, 0.20f), new Color(0.62f, 0.36f, 0.68f),
            new Color(0.88f, 0.60f, 0.70f), new Color(0.35f, 0.55f, 0.62f), new Color(0.78f, 0.74f, 0.62f), new Color(0.50f, 0.52f, 0.58f),
        };
        static readonly Color[] Bottoms =
        {
            new Color(0.15f, 0.20f, 0.35f), new Color(0.12f, 0.12f, 0.13f), new Color(0.80f, 0.74f, 0.60f), new Color(0.25f, 0.45f, 0.62f),
            new Color(0.78f, 0.28f, 0.25f), new Color(0.20f, 0.55f, 0.40f), new Color(0.95f, 0.85f, 0.30f), new Color(0.90f, 0.90f, 0.88f),
        };

        Transform body, armL, armR, thighL, thighR, shinL, shinR;
        Renderer[] core, extras, limbs, props;
        Vector3 bodyRest;
        int lod = -1;
        float phase, seed;
        HumanVisual.Look look; HumanVisual human; bool humanTried, humanShown; int idleVariant;

        public float Scale { get; private set; } = 1f;
        public int Lod => lod;
        public Gesture Gesture { get; set; }
        public Vector3 BodyOffset { get; set; }
        /// <summary>0..1 strength of the current ball strike for <see cref="Gesture.Hit"/> (driven by the game that owns the ball).</summary>
        public float HitPulse { get; set; }

        static T Pick<T>(T[] a, System.Random r) => a[r.Next(a.Length)];

        static GameObject Part(PrimitiveType type, string name, Transform parent, Vector3 pos, Vector3 scale, Color color)
        {
            var g = GameObject.CreatePrimitive(type);
            g.name = name; g.transform.SetParent(parent, false);
            g.transform.localPosition = pos; g.transform.localScale = scale;
            g.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(color, 0.12f);
            Destroy(g.GetComponent<Collider>());
            return g;
        }

        static Transform Pivot(string name, Transform parent, Vector3 pos)
        {
            var t = new GameObject(name).transform; t.SetParent(parent, false); t.localPosition = pos; return t;
        }

        public static PersonRig Create(System.Random rng, PersonKind kind, string label = "Person", Color? shirtOverride = null)
        {
            var root = new GameObject(label);
            var rig = root.AddComponent<PersonRig>();
            rig.seed = (float)rng.NextDouble() * 50f;
            rig.Build(rng, kind, shirtOverride);
            return rig;
        }

        void Build(System.Random rng, PersonKind kind, Color? shirtOverride)
        {
            bool kid = kind == PersonKind.Kid;
            Scale = kid ? 0.58f + 0.2f * (float)rng.NextDouble() : Mathf.Lerp(0.9f, 1.07f, (float)rng.NextDouble());
            transform.localScale = Vector3.one * Scale;
            float w = kid ? 0.85f : 0.92f + 0.22f * (float)rng.NextDouble();               // build
            var skin = Pick(Skins, rng); var hair = Pick(Hairs, rng);
            var shirt = shirtOverride ?? Pick(Shirts, rng); var bottom = Pick(Bottoms, rng);
            bool beach = kind == PersonKind.Beach || kind == PersonKind.Kid;
            bool shirtless = beach && rng.NextDouble() < 0.45;
            bool bareLegs = beach || kind == PersonKind.Active || rng.NextDouble() < 0.4;
            Color top = shirtless ? skin : shirt;
            Color legColor = bareLegs ? skin : bottom;

            body = Pivot("Body", transform, Vector3.zero); bodyRest = Vector3.zero;
            var core = new List<Renderer>(); var extras = new List<Renderer>(); var limbs = new List<Renderer>();

            core.Add(Part(PrimitiveType.Capsule, "Torso", body, new Vector3(0f, 1.24f, 0f), new Vector3(0.33f * w, 0.29f, 0.21f), top).GetComponent<Renderer>());
            core.Add(Part(PrimitiveType.Sphere, "Head", body, new Vector3(0f, 1.64f, 0f), Vector3.one * 0.22f, skin).GetComponent<Renderer>());
            float hairStyle = (float)rng.NextDouble();
            if (hairStyle < 0.85f)
                extras.Add(Part(PrimitiveType.Sphere, "Hair", body, new Vector3(0f, 1.695f, -0.012f), new Vector3(0.236f, 0.17f, 0.246f), hair).GetComponent<Renderer>());
            if (hairStyle < 0.35f && !kid)
                extras.Add(Part(PrimitiveType.Capsule, "LongHair", body, new Vector3(0f, 1.55f, -0.095f), new Vector3(0.2f, 0.16f, 0.1f), hair).GetComponent<Renderer>());
            // swimwear or shorts
            Color shortsColor = kind == PersonKind.Casual && !bareLegs ? bottom : Pick(Bottoms, rng);
            if (bareLegs) extras.Add(Part(PrimitiveType.Capsule, "Shorts", body, new Vector3(0f, 0.96f, 0f), new Vector3(0.35f * w, 0.10f, 0.23f), shortsColor).GetComponent<Renderer>());
            if (shirtless && rng.NextDouble() < 0.5) extras.Add(Part(PrimitiveType.Capsule, "Top", body, new Vector3(0f, 1.38f, 0.01f), new Vector3(0.335f * w, 0.05f, 0.215f), Pick(Shirts, rng)).GetComponent<Renderer>());

            Transform Leg(float side, out Transform shin)
            {
                var thigh = Pivot("Thigh", body, new Vector3(0.1f * w * side, 0.92f, 0f));
                limbs.Add(Part(PrimitiveType.Capsule, "ThighMesh", thigh, new Vector3(0f, -0.23f, 0f), new Vector3(0.17f, 0.23f, 0.17f), legColor).GetComponent<Renderer>());
                shin = Pivot("Shin", thigh, new Vector3(0f, -0.46f, 0f));
                limbs.Add(Part(PrimitiveType.Capsule, "ShinMesh", shin, new Vector3(0f, -0.22f, 0f), new Vector3(0.135f, 0.22f, 0.135f), legColor).GetComponent<Renderer>());
                limbs.Add(Part(PrimitiveType.Cube, "Foot", shin, new Vector3(0f, -0.45f, 0.05f), new Vector3(0.09f, 0.05f, 0.21f), bareLegs ? skin : new Color(0.15f, 0.15f, 0.16f)).GetComponent<Renderer>());
                return thigh;
            }
            thighL = Leg(-1f, out shinL); thighR = Leg(1f, out shinR);

            Transform Arm(float side)
            {
                var a = Pivot("Arm", body, new Vector3(0.215f * w * side, 1.47f, 0f));
                limbs.Add(Part(PrimitiveType.Capsule, "ArmMesh", a, new Vector3(0f, -0.27f, 0f), new Vector3(0.085f, 0.27f, 0.085f), shirtless || kind == PersonKind.Active ? skin : (rng.NextDouble() < 0.5 ? skin : shirt)).GetComponent<Renderer>());
                return a;
            }
            armL = Arm(-1f); armR = Arm(1f);

            this.core = core.ToArray(); this.extras = extras.ToArray(); this.limbs = limbs.ToArray(); props = new Renderer[0];

            // the same person, described for the optional skinned body (own random stream: the procedural look above is unchanged)
            var lr = new System.Random((int)(seed * 977f) + 11);
            bool longHair = hairStyle < 0.35f && !kid;
            look = new HumanVisual.Look
            {
                skin = skin, hair = hair, shirt = shirt, bottom = bareLegs ? shortsColor : bottom, shoes = new Color(0.15f, 0.15f, 0.16f),
                shirtless = shirtless, bareLegs = bareLegs, longSleeves = !shirtless && kind != PersonKind.Active && lr.NextDouble() < 0.35,
                longHair = longHair, hasHair = hairStyle < 0.85f, female = lr.NextDouble() < (longHair ? 0.8 : 0.3), scale = Scale,
            };
            idleVariant = lr.Next(2);
            SetLod(0);
        }

        /// <summary>Adds a bicycle under the rider (wheels, frame, handlebar). Parts hide at far LOD with the other props.</summary>
        public void AddBike(Color frame)
        {
            var bike = Pivot("Bike", transform, Vector3.zero);
            var list = new List<Renderer>(props);
            foreach (var z in new[] { -0.55f, 0.55f })
            {
                var wheel = Part(PrimitiveType.Cylinder, "Wheel", bike, new Vector3(0f, 0.34f, z), new Vector3(0.68f, 0.03f, 0.68f), new Color(0.1f, 0.1f, 0.1f));
                wheel.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);
                list.Add(wheel.GetComponent<Renderer>());
            }
            list.Add(Part(PrimitiveType.Cube, "Frame", bike, new Vector3(0f, 0.62f, 0f), new Vector3(0.05f, 0.05f, 1.05f), frame).GetComponent<Renderer>());
            list.Add(Part(PrimitiveType.Cube, "Seat", bike, new Vector3(0f, 0.8f, -0.25f), new Vector3(0.1f, 0.06f, 0.2f), new Color(0.1f, 0.1f, 0.1f)).GetComponent<Renderer>());
            list.Add(Part(PrimitiveType.Cube, "Bars", bike, new Vector3(0f, 0.95f, 0.5f), new Vector3(0.5f, 0.04f, 0.04f), new Color(0.15f, 0.15f, 0.15f)).GetComponent<Renderer>());
            props = list.ToArray();
            ApplyLod(true);
        }

        /// <summary>Removes the bicycle (when a pooled rider is released) so the rig can be reused on foot.</summary>
        public void ClearProps()
        {
            var bike = transform.Find("Bike");
            if (bike != null) Destroy(bike.gameObject);
            props = new Renderer[0];
        }

        // ---------------------------------------------------------------- level of detail

        /// <summary>0: full (shadows), 1: full without shadows, 2: torso, head and hair only, 3: hidden.</summary>
        public void SetLod(int level)
        {
            level = Mathf.Clamp(level, 0, 3);
            if (level == lod) return;
            lod = level; ApplyLod(false);
        }

        void ApplyLod(bool force)
        {
            if (lod >= 2 && humanShown) { humanShown = false; human.Show(false); }     // the skinned body is for near and medium people only
            bool near = lod <= 1, visible = lod < 3, proc = !humanShown;
            var shadow = lod == 0 ? ShadowCastingMode.On : ShadowCastingMode.Off;
            if (humanShown) human.SetShadows(lod == 0);
            foreach (var r in core) { r.enabled = visible && proc; r.shadowCastingMode = shadow; }
            foreach (var r in extras) { r.enabled = visible && proc; r.shadowCastingMode = shadow; }
            foreach (var r in limbs) { r.enabled = near && proc; r.shadowCastingMode = shadow; }
            foreach (var r in props) { r.enabled = near; r.shadowCastingMode = shadow; }
        }

        // ---------------------------------------------------------------- poses

        static void Rot(Transform t, float x, float z = 0f) => t.localRotation = Quaternion.Euler(x, 0f, z);

        public bool HumanShown => humanShown;

        void SetHumanShown(bool on)
        {
            if (humanShown == on) return;
            humanShown = on; human.Show(on); ApplyLod(true);
        }

        /// <summary>Upright locomotion and talking use the skinned body when the optional pack is present; everything else stays procedural.</summary>
        bool TryHuman(Pose pose, float speed, float dt)
        {
            bool wants = lod <= 1 && HumanVisual.Available && (pose == Pose.Walk || pose == Pose.Run || pose == Pose.Stand)
                         && (Gesture == Gesture.None || Gesture == Gesture.Chat) && props.Length == 0;
            if (wants && human == null && !humanTried) { humanTried = true; human = HumanVisual.Create(transform, look, new System.Random((int)(seed * 31f) + 5)); }
            if (wants && human != null && !humanShown && HumanVisual.ActiveCount >= HumanVisual.MaxActive) wants = false;
            if (!wants || human == null) { if (humanShown) SetHumanShown(false); return false; }
            SetHumanShown(true);
            var clip = pose == Pose.Run ? HumanVisual.Clip.Run : pose == Pose.Walk ? HumanVisual.Clip.Walk
                     : Gesture == Gesture.Chat ? HumanVisual.Clip.Talk : (idleVariant == 0 ? HumanVisual.Clip.Idle1 : HumanVisual.Clip.Idle2);
            human.Drive(clip, speed, dt, Mathf.Repeat(seed, 1f));
            return true;
        }

        /// <summary>Poses the joints for this instant. <paramref name="speed"/> is the ground speed (m/s) and drives the stride.</summary>
        public void Animate(Pose pose, float speed, float dt)
        {
            if (lod >= 2) return;                                                       // limbs are hidden: nothing to move
            if (TryHuman(pose, speed, dt)) return;                                      // skinned body animates itself
            phase += dt * Mathf.Max(0.4f, speed) * (pose == Pose.Run ? 3.4f : pose == Pose.Bike ? 2.2f : 4.2f);
            float s = Mathf.Sin(phase), idle = Mathf.Sin(Time.time * 1.1f + seed);
            Vector3 off = bodyRest;
            Quaternion bodyRot = Quaternion.identity;
            switch (pose)
            {
                case Pose.Walk:
                case Pose.Run:
                {
                    bool run = pose == Pose.Run;
                    float amp = run ? 52f : 26f, knee = run ? 85f : 40f, arm = run ? 55f : 22f;
                    Rot(thighL, s * amp); Rot(thighR, -s * amp);
                    Rot(shinL, Mathf.Max(0f, Mathf.Sin(phase + 1.3f)) * knee); Rot(shinR, Mathf.Max(0f, Mathf.Sin(phase + 1.3f + Mathf.PI)) * knee);
                    Rot(armL, -s * arm); Rot(armR, s * arm);
                    if (run) bodyRot = Quaternion.Euler(9f, 0f, 0f);
                    off.y = Mathf.Abs(Mathf.Cos(phase)) * (run ? 0.06f : 0.03f);
                    break;
                }
                case Pose.Stand:
                    Rot(thighL, 0f); Rot(thighR, 0f); Rot(shinL, 0f); Rot(shinR, 0f);
                    Rot(armL, 2f + idle * 2f); Rot(armR, 2f - idle * 2f);
                    break;
                case Pose.SitSand:
                    Rot(thighL, -88f); Rot(thighR, -80f); Rot(shinL, 4f); Rot(shinR, 14f);
                    Rot(armL, -25f); Rot(armR, -25f);
                    off.y = -0.82f; bodyRot = Quaternion.Euler(-4f, 0f, 0f);
                    break;
                case Pose.SitChair:
                    Rot(thighL, -90f); Rot(thighR, -90f); Rot(shinL, 90f); Rot(shinR, 90f);
                    Rot(armL, -40f); Rot(armR, -40f);
                    off.y = -0.46f;
                    break;
                case Pose.LieBack:
                    Rot(thighL, 0f); Rot(thighR, 4f, 6f); Rot(shinL, 0f); Rot(shinR, 0f);
                    Rot(armL, 8f); Rot(armR, 8f);
                    bodyRot = Quaternion.Euler(-90f, 0f, 0f); off.y = 0.11f;
                    break;
                case Pose.LieFront:
                    Rot(thighL, 0f); Rot(thighR, 0f); Rot(shinL, 0f); Rot(shinR, 0f);
                    Rot(armL, -150f); Rot(armR, -150f);
                    bodyRot = Quaternion.Euler(90f, 0f, 0f); off.y = 0.12f;
                    break;
                case Pose.Swim:
                    Rot(thighL, s * 14f); Rot(thighR, -s * 14f); Rot(shinL, 8f); Rot(shinR, 8f);
                    Rot(armL, -90f - Mathf.Repeat(phase * 0.6f, 6.283f) * Mathf.Rad2Deg); Rot(armR, -90f - Mathf.Repeat(phase * 0.6f + Mathf.PI, 6.283f) * Mathf.Rad2Deg);
                    bodyRot = Quaternion.Euler(78f, 0f, 0f); off.y = 0.05f;
                    break;
                case Pose.Bike:
                    Rot(thighL, -60f + s * 24f); Rot(thighR, -60f - s * 24f); Rot(shinL, 62f - s * 22f); Rot(shinR, 62f + s * 22f);
                    Rot(armL, -58f); Rot(armR, -58f);
                    bodyRot = Quaternion.Euler(14f, 0f, 0f); off = new Vector3(0f, 0.07f, -0.2f);
                    break;
            }
            ApplyGesture(pose);
            body.localRotation = bodyRot; body.localPosition = off + BodyOffset;
        }

        void ApplyGesture(Pose pose)
        {
            if (Gesture == Gesture.None || pose == Pose.Walk || pose == Pose.Run || pose == Pose.Swim || pose == Pose.Bike) return;
            float t = Time.time + seed;
            switch (Gesture)
            {
                case Gesture.Phone: Rot(armR, -78f, 18f); break;                                            // phone held up in front of the face
                case Gesture.Drink: Rot(armR, -40f - 90f * Mathf.SmoothStep(0f, 1f, Mathf.PingPong(t * 0.35f, 1f)), 8f); break;
                case Gesture.Chat: Rot(armR, -35f - 25f * Mathf.Sin(t * 3.1f), 6f); Rot(armL, -15f - 10f * Mathf.Sin(t * 2.3f + 1f)); break;
                case Gesture.Dig: Rot(armR, -50f + 30f * Mathf.Sin(t * 5f)); Rot(armL, -50f - 30f * Mathf.Sin(t * 5f)); break;
                case Gesture.Hit: Rot(armR, -35f - 125f * HitPulse, 4f); Rot(armL, -20f - 30f * HitPulse, -6f); break;   // racket arm swings up through the strike
            }
        }

        /// <summary>The head turns with the body only; looking at the sea is done by yawing the whole rig.</summary>
        public static float YawTowards(Vector3 from, Vector3 to) => Mathf.Atan2(to.x - from.x, to.z - from.z) * Mathf.Rad2Deg;
    }
}
