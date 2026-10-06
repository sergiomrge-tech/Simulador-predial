using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Basic ambient soundscape, synthesised at start so the project needs no audio assets yet: surf (follows the player along the waterline),
    /// sea breeze, the murmur of the promenade crowd (scaled by how many people are about), evening insects, and the odd gull call.
    /// Placeholder until authored audio replaces it in the polish phase; the layering and the rules (day/night, crowd, weather) stay.
    /// </summary>
    public sealed class AmbientAudio : MonoBehaviour
    {
        const int Rate = 22050;

        ResortGame game; AmbientLife life;
        AudioSource surf, wind, murmur, insects, gullCall;
        AudioClip[] gullClips;
        float callTimer = 8f;
        System.Random rng;

        public bool SurfPlaying => surf != null && surf.isPlaying;
        public float SurfVolume => surf != null ? surf.volume : 0f;
        public float MurmurVolume => murmur != null ? murmur.volume : 0f;
        public float InsectVolume => insects != null ? insects.volume : 0f;
        public float WindVolume => wind != null ? wind.volume : 0f;
        public int GullCalls { get; private set; }
        public AudioClip SurfClip => surf != null ? surf.clip : null;
        public AudioClip MurmurClip => murmur != null ? murmur.clip : null;

        public void Init(ResortGame g, AmbientLife l)
        {
            game = g; life = l; rng = new System.Random(g.Seed + 99);
            surf = Source("Surf", Surf(), 1f, 0.6f);
            wind = Source("Wind", Wind(), 0f, 0.0f);
            murmur = Source("Murmur", Murmur(), 0f, 0.0f);
            insects = Source("Insects", Insects(), 0f, 0.0f);
            gullClips = new[] { Gull(0, 1900f, 1150f), Gull(1, 2200f, 1400f), Gull(2, 1700f, 1000f) };
            var go = new GameObject("GullCall"); go.transform.SetParent(transform, false);
            gullCall = go.AddComponent<AudioSource>(); gullCall.spatialBlend = 1f; gullCall.rolloffMode = AudioRolloffMode.Linear; gullCall.minDistance = 20f; gullCall.maxDistance = 220f; gullCall.playOnAwake = false;
        }

        AudioSource Source(string name, AudioClip clip, float blend, float volume)
        {
            var go = new GameObject(name); go.transform.SetParent(transform, false);
            var s = go.AddComponent<AudioSource>();
            s.clip = clip; s.loop = true; s.playOnAwake = false; s.volume = volume; s.spatialBlend = blend;
            if (blend > 0f) { s.rolloffMode = AudioRolloffMode.Linear; s.minDistance = 25f; s.maxDistance = 260f; }
            s.Play();
            return s;
        }

        // ---------------------------------------------------------------- per frame

        void Update()
        {
            if (game == null || game.Clock == null) return;
            var cam = Camera.main;
            float night = game.DayNight != null ? game.DayNight.NightFactor : 0f;
            if (cam != null && game.Site != null && game.Site.Ready)
            {
                var p = cam.transform.position;
                surf.transform.position = new Vector3(p.x, 0f, game.Site.WaterlineZ(p.x) - 4f);       // the nearest bit of shore is the sound's source
            }
            // volumes ease toward their targets (also keeps hour jumps from clicking)
            float k = 1f - Mathf.Exp(-Time.deltaTime * 1.5f);
            float crowd = game.Life != null ? Mathf.Clamp01(game.Life.ActiveCount / 60f) : 0f;
            float wnd = life != null ? life.Wind : 0.4f;
            surf.volume = Mathf.Lerp(surf.volume, Mathf.Lerp(0.85f, 0.6f, night), k);
            wind.volume = Mathf.Lerp(wind.volume, 0.07f + wnd * 0.28f, k);
            murmur.volume = Mathf.Lerp(murmur.volume, crowd * 0.2f * (1f - 0.5f * night), k);
            insects.volume = Mathf.Lerp(insects.volume, Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.5f, 0.95f, night)) * 0.09f + 0.0f, k);

            callTimer -= Time.deltaTime;
            if (callTimer <= 0f && night < 0.5f)
            {
                var pos = life != null ? life.AnyGullPosition() : null;
                if (pos.HasValue)
                {
                    gullCall.transform.position = pos.Value;
                    gullCall.PlayOneShot(gullClips[rng.Next(gullClips.Length)], 0.5f);
                    GullCalls++;
                }
                callTimer = 7f + (float)rng.NextDouble() * 16f;
            }
        }

        // ---------------------------------------------------------------- synthesis

        static float Noise(System.Random r) => (float)(r.NextDouble() * 2.0 - 1.0);

        static AudioClip Make(string name, float[] data)
        {
            float peak = 0f; foreach (var v in data) peak = Mathf.Max(peak, Mathf.Abs(v));
            if (peak > 0.0001f) { float k = 0.85f / peak; for (int i = 0; i < data.Length; i++) data[i] *= k; }   // normalised: loudness is set by the source volumes
            var clip = AudioClip.Create(name, data.Length, 1, Rate, false);
            clip.SetData(data, 0);
            return clip;
        }

        /// <summary>Makes the clip loop seamlessly by cross-fading its tail into its head.</summary>
        static float[] Loopable(float[] d, int fade)
        {
            int n = d.Length - fade;
            var o = new float[n];
            for (int i = 0; i < n; i++) o[i] = d[i];
            for (int i = 0; i < fade; i++) { float t = i / (float)fade; o[i] = o[i] * t + d[n + i] * (1f - t); }
            return o;
        }

        /// <summary>Two swells per 12 s: low rumble that swells with a hissing crest, then drains back over the sand.</summary>
        static AudioClip Surf()
        {
            var r = new System.Random(12);
            int n = Rate * 14, fade = Rate * 2; var d = new float[n];
            float lo1 = 0f, lo2 = 0f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate, white = Noise(r);
                lo1 += (white - lo1) * 0.03f; lo2 += (lo1 - lo2) * 0.05f;                       // rumble
                float ph = Mathf.Repeat(t / 6f, 1f);
                float swell = Mathf.Pow(Mathf.Sin(Mathf.PI * ph), 2f);
                float crest = Mathf.Pow(Mathf.Max(0f, Mathf.Sin(Mathf.PI * Mathf.Clamp01(ph * 1.25f - 0.12f))), 6f);
                float hiss = white * 0.5f - lo1 * 0.5f;                                          // high-passed noise
                d[i] = (lo2 * 9f * (0.3f + 0.7f * swell) + hiss * crest * 0.55f) * 0.45f;
            }
            return Make("SurfLoop", Loopable(d, fade));
        }

        static AudioClip Wind()
        {
            var r = new System.Random(34);
            int n = Rate * 12, fade = Rate * 2; var d = new float[n];
            float a = 0f, b = 0f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                float cut = 0.012f + 0.01f * Mathf.Sin(t * 0.9f) + 0.006f * Mathf.Sin(t * 0.37f + 1f);
                a += (Noise(r) - a) * cut; b += (a - b) * 0.08f;
                float gust = 0.55f + 0.45f * Mathf.Sin(t * 0.52f + Mathf.Sin(t * 0.21f) * 2f);
                d[i] = b * 14f * gust * 0.5f;
            }
            return Make("WindLoop", Loopable(d, fade));
        }

        /// <summary>Distant voices: band-limited noise shaped by syllable-rate pulses (no intelligible words, just the warmth of a crowd).</summary>
        static AudioClip Murmur()
        {
            var r = new System.Random(56);
            int n = Rate * 10, fade = Rate * 2; var d = new float[n];
            float a = 0f, b = 0f, c = 0f;
            float f1 = 0f, f2 = 0f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate, w = Noise(r);
                a += (w - a) * 0.22f; b += (a - b) * 0.22f; c += (w - c) * 0.025f;                  // crude band-pass: lp(0.22)-lp(0.025)
                float band = (b - c) * 4f;
                f1 = 0.5f + 0.5f * Mathf.Sin(t * 2.1f * 6.283f + Mathf.Sin(t * 0.7f) * 2f);
                f2 = 0.5f + 0.5f * Mathf.Sin(t * 3.4f * 6.283f + 1.7f + Mathf.Sin(t * 0.3f) * 3f);
                d[i] = band * (0.25f + 0.75f * Mathf.Pow(f1 * 0.6f + f2 * 0.4f, 1.5f)) * 0.8f;
            }
            return Make("MurmurLoop", Loopable(d, fade));
        }

        /// <summary>Evening chorus: 4.4 kHz chirps in tight bursts, two overlapping "singers".</summary>
        static AudioClip Insects()
        {
            int n = Rate * 6, fade = Rate; var d = new float[n];
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                float burstA = Mathf.Repeat(t * 3.1f, 1f) < 0.45f ? 1f : 0f, burstB = Mathf.Repeat(t * 2.3f + 0.4f, 1f) < 0.5f ? 1f : 0f;
                float pulseA = Mathf.Max(0f, Mathf.Sin(t * 46f * 6.283f)), pulseB = Mathf.Max(0f, Mathf.Sin(t * 38f * 6.283f + 1f));
                d[i] = (Mathf.Sin(t * 4400f * 6.283f) * pulseA * burstA * 0.5f + Mathf.Sin(t * 5100f * 6.283f) * pulseB * burstB * 0.35f) * 0.6f;
            }
            return Make("InsectLoop", Loopable(d, fade));
        }

        /// <summary>A gull's cry: descending whistle with vibrato, 0.45 s.</summary>
        static AudioClip Gull(int seed, float f0, float f1)
        {
            int n = (int)(Rate * 0.45f); var d = new float[n]; float phase = 0f;
            var r = new System.Random(seed + 400);
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)n;
                float f = Mathf.Lerp(f0, f1, t) * (1f + 0.04f * Mathf.Sin(t * 60f)) + Noise(r) * 30f;
                phase += f / Rate * 6.283f;
                float env = Mathf.Sin(Mathf.PI * Mathf.Pow(t, 0.7f));
                d[i] = (Mathf.Sin(phase) + 0.45f * Mathf.Sin(phase * 2f) + 0.2f * Mathf.Sin(phase * 3f)) * env * 0.35f;
            }
            return Make("Gull" + seed, d);
        }
    }
}
