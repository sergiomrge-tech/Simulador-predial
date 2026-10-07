using System.Collections.Generic;
using ResortAurora.Site;
using ResortAurora.Sim;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Game
{
    /// <summary>
    /// Scene side of the world clock's light: sun (east to west across the northern sky), moon and stars, procedural sky, haze, ambient and
    /// reflections, and the lamps of the promenade, kiosk and home. Lamps are cheap emissive heads that share one material; only the few
    /// nearest to the camera carry a real point light (a small pool that is re-aimed as the player walks), so night costs a handful of lights.
    /// </summary>
    public sealed class DayNightCycle : MonoBehaviour
    {
        const int PoolSize = 8;

        struct Lamp { public Vector3 pos; public float range, intensity; public Color color; }

        ResortGame game;
        Light sun, moon;
        Material sky, lampMat, starMat, moonMat;
        bool customSky;
        Transform dome;
        readonly List<Lamp> lamps = new List<Lamp>();
        Light[] pool;
        float poolTimer;

        public float NightFactor { get; private set; }
        public float Hours { get; private set; } = 12f;
        public bool LampsOn => Daylight.LampsOn(Hours);
        public int LampCount => lamps.Count;
        public int LightsActive { get; private set; }

        static readonly Color Warm = new Color(1f, 0.74f, 0.42f);

        public void Init(ResortGame g, Light sunLight)
        {
            game = g; sun = sunLight;
            var moonGo = new GameObject("Moon"); moonGo.transform.SetParent(transform, false);
            moon = moonGo.AddComponent<Light>();
            moon.type = LightType.Directional; moon.color = new Color(0.55f, 0.66f, 1f); moon.intensity = 0f; moon.shadows = LightShadows.None;

            var skyShader = Shader.Find("ResortAurora/Sky");
            customSky = skyShader != null;
            if (!customSky) skyShader = Shader.Find("Skybox/Procedural");                // stock fallback if the shader was stripped
            if (skyShader != null) { sky = new Material(skyShader) { name = "DaySky" }; RenderSettings.skybox = sky; }
            RenderSettings.sun = sun;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Exponential;

            lampMat = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "LampHead" };
            lampMat.SetColor("_BaseColor", new Color(0.96f, 0.9f, 0.78f)); lampMat.EnableKeyword("_EMISSION");
            lampMat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;

            pool = new Light[PoolSize];
            for (int i = 0; i < PoolSize; i++)
            {
                var go = new GameObject("LampLight" + i); go.transform.SetParent(transform, false);
                var l = go.AddComponent<Light>(); l.type = LightType.Point; l.shadows = LightShadows.None; l.enabled = false;
                pool[i] = l;
            }
            BuildSkyDome();
        }

        // ---------------------------------------------------------------- lamps

        /// <summary>Registers a lamp (its emissive head is made by <see cref="LampHead"/>). The light itself is borrowed from the pool when the player is near.</summary>
        public void AddLamp(Vector3 pos, float range = 14f, float intensity = 2.2f, Color? color = null) =>
            lamps.Add(new Lamp { pos = pos, range = range, intensity = intensity, color = color ?? Warm });

        public bool RelocateLamp(Vector3 from, Vector3 to)
        {
            for(int i=0;i<lamps.Count;i++)
                if((lamps[i].pos-from).sqrMagnitude<.0001f)
                { var lamp=lamps[i]; lamp.pos=to; lamps[i]=lamp; return true; }
            return false;
        }

        /// <summary>A small emissive globe that glows at night with every other lamp head (shared material).</summary>
        public GameObject LampHead(Transform parent, Vector3 localPos, float diameter)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            g.name = "LampHead"; g.transform.SetParent(parent, false);
            g.transform.localPosition = localPos; g.transform.localScale = Vector3.one * diameter;
            g.GetComponent<MeshRenderer>().sharedMaterial = lampMat;
            Destroy(g.GetComponent<Collider>());
            return g;
        }

        static Bounds RendererBounds(Transform root)
        {
            var rs = root.GetComponentsInChildren<Renderer>(true);
            if (rs.Length == 0) return new Bounds(root.position, Vector3.zero);
            var b = rs[0].bounds;
            for (int i = 1; i < rs.Length; i++) b.Encapsulate(rs[i].bounds);
            return b;
        }

        /// <summary>
        /// Connects the realistic scanned urban lamp meshes generated by CoastalUrbanProps to the
        /// pooled night-light system. The scan remains the visible fixture; only a tiny shared
        /// emissive bulb is added, plus a pooled real light when the camera/player is nearby.
        /// </summary>
        public void RegisterUrbanLamps(ResortSite site)
        {
            if (site == null) return;
            var root = site.transform.Find("UrbanPropsRealistic_F02");
            if (root == null) return;

            int street = 0, wall = 0;
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                bool isStreet = t.name.StartsWith("AvenueLamp_") || t.name.StartsWith("NeighbourhoodLamp_");
                bool isWall = t.name.StartsWith("ShopWallLamp_");
                if (!isStreet && !isWall) continue;

                var b = RendererBounds(t);
                if (b.size.sqrMagnitude < 0.001f) continue;
                var p = isStreet
                    ? new Vector3(b.center.x, b.max.y - Mathf.Min(0.22f, b.size.y * 0.04f), b.center.z)
                    : new Vector3(b.center.x, b.center.y + b.extents.y * 0.35f, b.center.z);
                if(CoastalUrbanProps.TryLampEmitter(t,out var emitter)) p=emitter;

                AddLamp(p, isStreet ? 19f : 10f, isStreet ? 6.0f : 3.0f,
                    isStreet ? new Color(1f, 0.73f, 0.40f) : new Color(1f, 0.68f, 0.36f));

                var bulb = LampHead(t, t.InverseTransformPoint(p), isStreet ? 0.10f : 0.075f);
                bulb.name = "NightBulb";
                if(CoastalUrbanProps.BindLampBulb(t,bulb.GetComponent<Renderer>().sharedMaterial))
                    bulb.GetComponent<Renderer>().enabled=false;
                if (isStreet) street++; else wall++;
            }
            Debug.Log($"URBAN_NIGHT_LIGHTS street={street} wall={wall} totalRegistered={lamps.Count}");
        }

        /// <summary>Street lights along the beach edge of the promenade around the kiosk, as in REF 01. The first and last stay outside the stall's footprint.</summary>
        public void BuildPromenadeLamps(ResortSite site, float centerX)
        {
            var root = new GameObject("PromenadeLamps").transform; root.SetParent(transform, false);
            var metal = new Color(0.16f, 0.17f, 0.18f);
            for (float x = centerX - 126f; x <= centerX + 126f; x += 21f)
            {
                if (Mathf.Abs(x - centerX) < 14f) continue;                               // the stall (and its stage 2 deck) brings its own lights
                float z = site.PromenadeZ(x) - 5.6f, y = site.HeightAt(x, z);
                var post = new GameObject("LampPost"); post.transform.SetParent(root, false); post.transform.position = new Vector3(x, y, z);
                var pole = StallBuilder.Box("Pole", post.transform, new Vector3(0f, 2.1f, 0f), new Vector3(0.11f, 4.2f, 0.11f), metal);
                pole.GetComponent<BoxCollider>().size = Vector3.one;
                StallBuilder.Box("Arm", post.transform, new Vector3(0.35f, 4.15f, 0f), new Vector3(0.8f, 0.07f, 0.07f), metal, collider: false);
                LampHead(post.transform, new Vector3(0.7f, 4.05f, 0f), 0.34f);
                AddLamp(post.transform.position + new Vector3(0.7f, 4.0f, 0f), 15f, 2.6f);
            }
        }

        // ---------------------------------------------------------------- sky

        /// <summary>Stars (a cloud of points) and a moon disc on a dome that follows the camera, so they sit at infinity.</summary>
        void BuildSkyDome()
        {
            dome = new GameObject("SkyDome").transform; dome.SetParent(transform, false);
            var rng = new System.Random(4242);
            const int n = 700;
            var verts = new Vector3[n]; var cols = new Color[n]; var idx = new int[n];
            for (int i = 0; i < n; i++)
            {
                double u = rng.NextDouble(), v = rng.NextDouble() * 0.92 + 0.04;                  // keep above the horizon
                double th = u * Mathf.PI * 2, ph = v * Mathf.PI * 0.5;
                verts[i] = new Vector3((float)(System.Math.Cos(th) * System.Math.Cos(ph)), (float)System.Math.Sin(ph), (float)(System.Math.Sin(th) * System.Math.Cos(ph))) * 850f;
                float b = 0.45f + 0.55f * (float)rng.NextDouble();
                cols[i] = new Color(b, b, Mathf.Min(1f, b + 0.08f), 1f); idx[i] = i;
            }
            var mesh = new Mesh { name = "Stars" };
            mesh.vertices = verts; mesh.colors = cols; mesh.SetIndices(idx, MeshTopology.Points, 0);
            mesh.bounds = new Bounds(Vector3.zero, Vector3.one * 2000f);
            starMat = new Material(Shader.Find("Sprites/Default")) { name = "Stars" };
            var stars = new GameObject("Stars"); stars.transform.SetParent(dome, false);
            stars.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = stars.AddComponent<MeshRenderer>(); mr.sharedMaterial = starMat; mr.shadowCastingMode = ShadowCastingMode.Off; mr.receiveShadows = false;

            var disc = GameObject.CreatePrimitive(PrimitiveType.Sphere); disc.name = "MoonDisc";
            disc.transform.SetParent(dome, false); disc.transform.localScale = Vector3.one * 26f;
            Destroy(disc.GetComponent<Collider>());
            moonMat = new Material(Shader.Find("Sprites/Default")) { name = "MoonDisc", color = new Color(0.93f, 0.95f, 1f, 1f) };
            var dr = disc.GetComponent<MeshRenderer>(); dr.sharedMaterial = moonMat; dr.shadowCastingMode = ShadowCastingMode.Off; dr.receiveShadows = false;
        }

        // ---------------------------------------------------------------- per frame

        void Update()
        {
            if (game == null || game.Clock == null) return;
            Apply(game.Clock.Hours);
            poolTimer -= Time.deltaTime;
            if (poolTimer <= 0f) { poolTimer = 0.3f; AssignLights(); }
            if (dome != null && Camera.main != null) dome.position = Camera.main.transform.position;
        }

        /// <summary>Puts the whole scene in the light of <paramref name="hours"/> (also called by tests and captures).</summary>
        public void Apply(float hours)
        {
            Hours = hours;
            float night = Daylight.Night(hours); NightFactor = night;
            float elev = Daylight.SunElevation(hours), golden = Daylight.Golden(hours);
            float t = Mathf.Clamp01((hours - Daylight.Sunrise) / (Daylight.Sunset - Daylight.Sunrise));

            // sun: rises in the east, crosses the northern sky, sets in the west; the light points the other way
            float az = 90f - 180f * t;
            if (sun != null)
            {
                // below the horizon the light is already off (vis), and the procedural sky needs the real direction or it keeps a yellow dusk glow all night
                sun.transform.rotation = Quaternion.Euler(elev, az + 180f, 0f);
                sun.color = Color.Lerp(new Color(1f, 0.96f, 0.88f), new Color(1f, 0.58f, 0.32f), golden * golden);
                float vis = Mathf.Clamp01((elev + 3f) / 10f);
                sun.intensity = Mathf.Lerp(1.2f, 0.55f, golden) * vis;
                sun.shadows = night < 0.85f && elev > 1f ? LightShadows.Soft : LightShadows.None;
                sun.enabled = vis > 0.001f;
            }
            // moon: rises in the east after sunset and climbs
            float moonUp = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.25f, 0.9f, night));
            float moonElev = 24f + Mathf.Max(0f, hours - 18f) * 7f, moonAz = 105f - Mathf.Max(0f, hours - 18f) * 9f;
            moon.transform.rotation = Quaternion.Euler(moonElev, moonAz + 180f, 0f);
            moon.intensity = 0.42f * moonUp;
            moon.shadows = night > 0.85f ? LightShadows.Soft : LightShadows.None;
            moon.enabled = moonUp > 0.001f;

            // ambient: day sky-blue, dusk violet, night deep blue that never goes black
            var dayA = new Color(0.60f, 0.72f, 0.90f); var duskA = new Color(0.42f, 0.34f, 0.48f); var nightA = new Color(0.10f, 0.14f, 0.27f);
            Color Amb(Color d, Color k, Color nn) => Color.Lerp(Color.Lerp(d, k, golden * 0.8f), nn, night);
            RenderSettings.ambientSkyColor = Amb(dayA, duskA, nightA);
            RenderSettings.ambientEquatorColor = Amb(new Color(0.62f, 0.60f, 0.56f), new Color(0.40f, 0.30f, 0.30f), new Color(0.09f, 0.11f, 0.19f));
            RenderSettings.ambientGroundColor = Amb(new Color(0.40f, 0.34f, 0.26f), new Color(0.22f, 0.16f, 0.14f), new Color(0.05f, 0.05f, 0.08f));
            RenderSettings.reflectionIntensity = Mathf.Lerp(1f, 0.12f, night);
            // horizon (also the fog and the sea's far colour): blue day, orange sunset, violet dusk, deep blue night; the dusk only shows while night rises
            float dusk = Mathf.Sin(Mathf.Clamp01(night) * Mathf.PI) * (elev < 4f ? 1f : 0f);
            var horizon = Color.Lerp(Color.Lerp(new Color(0.72f, 0.82f, 0.92f), new Color(0.95f, 0.55f, 0.40f), golden), new Color(0.04f, 0.06f, 0.13f), night);
            horizon = Color.Lerp(horizon, new Color(0.40f, 0.26f, 0.44f), dusk * 0.55f);
            RenderSettings.fogColor = horizon;
            RenderSettings.fogDensity = Mathf.Lerp(0.00035f, 0.0007f, Mathf.Max(golden * 0.6f, night));

            if (sky != null && customSky)
            {
                var zenith = Color.Lerp(new Color(0.14f, 0.36f, 0.78f), new Color(0.22f, 0.27f, 0.54f), golden);
                zenith = Color.Lerp(zenith, new Color(0.02f, 0.035f, 0.10f), night);
                zenith = Color.Lerp(zenith, new Color(0.14f, 0.12f, 0.30f), dusk * 0.5f);
                float glowK = golden * golden * (1f - night) * Mathf.Clamp01((elev + 22f) / 24f);     // the sky keeps its afterglow while the sun is a little below the horizon
                sky.SetColor("_Zenith", zenith);
                sky.SetColor("_Horizon", horizon);
                sky.SetColor("_Ground", horizon * 0.55f);
                sky.SetVector("_SunDir", sun != null ? -sun.transform.forward : Vector3.up);
                sky.SetColor("_SunColor", (sun != null ? sun.color : Color.white) * Mathf.Clamp01((elev + 2f) / 6f));
                sky.SetColor("_Glow", new Color(1f, 0.52f, 0.26f) * (0.55f * glowK));
                sky.SetFloat("_SunDisc", 1f);
                var cloud = Color.Lerp(new Color(0.96f, 0.97f, 0.99f), new Color(1f, 0.74f, 0.58f), golden * 0.8f);
                cloud = Color.Lerp(cloud, new Color(0.055f, 0.075f, 0.15f), night);
                cloud = Color.Lerp(cloud, new Color(0.30f, 0.22f, 0.38f), dusk * 0.5f);
                sky.SetColor("_CloudColor", cloud);
                sky.SetFloat("_CloudCover", game.Weather == Weather.Cloudy ? 0.78f : 0.4f);
            }
            else if (sky != null)
            {
                sky.SetFloat("_SunSize", 0.04f);
                sky.SetFloat("_AtmosphereThickness", Mathf.Lerp(1.0f, 1.6f, golden));
                sky.SetFloat("_Exposure", Mathf.Lerp(1.25f, 0.18f, night));
                sky.SetColor("_SkyTint", Color.Lerp(new Color(0.5f, 0.5f, 0.5f), new Color(0.62f, 0.48f, 0.55f), golden));
                sky.SetColor("_GroundColor", Color.Lerp(new Color(0.37f, 0.35f, 0.33f), new Color(0.05f, 0.06f, 0.1f), night));
            }
            else { var cam = Camera.main; if (cam != null) { cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = horizon; } }

            float stars = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.5f, 1f, night)) * (game.Weather == Weather.Cloudy ? 0.35f : 1f);
            if (starMat != null) starMat.color = new Color(1f, 1f, 1f, stars);
            if (dome != null)
            {
                var disc = dome.Find("MoonDisc");
                if (disc != null)
                {
                    disc.localPosition = Quaternion.Euler(-moonElev, moonAz, 0f) * Vector3.forward * 800f;
                    disc.gameObject.SetActive(moonUp > 0.05f);
                    moonMat.color = new Color(0.93f, 0.95f, 1f, 1f) * Mathf.Lerp(0.2f, 1f, moonUp);
                }
                dome.Find("Stars").gameObject.SetActive(stars > 0.02f);
            }

            float lampFade = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(Daylight.LampsOnAbove, 0.65f, night));
            lampMat.SetColor("_EmissionColor", Warm * (lampFade * 3.2f));
        }

        void AssignLights()
        {
            float fade = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(Daylight.LampsOnAbove, 0.65f, NightFactor));
            var cam = Camera.main;
            if (fade <= 0.001f || cam == null || lamps.Count == 0) { foreach (var l in pool) l.enabled = false; LightsActive = 0; return; }
            var cp = cam.transform.position;
            var chosen = new List<int>(PoolSize);
            for (int k = 0; k < PoolSize && k < lamps.Count; k++)
            {
                int best = -1; float bd = float.MaxValue;
                for (int i = 0; i < lamps.Count; i++)
                {
                    if (chosen.Contains(i)) continue;
                    float d = (lamps[i].pos - cp).sqrMagnitude;
                    if (d < bd) { bd = d; best = i; }
                }
                if (best < 0) break;
                chosen.Add(best);
            }
            LightsActive = chosen.Count;
            for (int i = 0; i < PoolSize; i++)
            {
                bool on = i < chosen.Count;
                pool[i].enabled = on;
                if (!on) continue;
                var lamp = lamps[chosen[i]];
                pool[i].transform.position = lamp.pos; pool[i].color = lamp.color;
                pool[i].range = lamp.range; pool[i].intensity = lamp.intensity * fade;
            }
        }
    }
}
