using System.Collections.Generic;
using ResortAurora.Site;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Non-human life of the coast (Phase 02): surf (foam lines that roll in and wash out along the waterline), gulls circling over the water by day,
    /// and palm crowns that sway in the sea breeze. The exported palm foliage is one welded mesh per stage, so the crowns are split into
    /// separate pivoting meshes the first time a stage shows them. Everything is cheap: a few small ribbons, nine gulls, and only the palms near the camera move.
    /// </summary>
    public sealed class AmbientLife : MonoBehaviour
    {
        const int WaveCount = 5, WaveSegments = 100;
        const float WaveSpan = 260f, WavePeriod = 9.5f, SwayRange = 170f;

        sealed class Wave { public Mesh mesh; public Material mat; public Vector3[] verts; public float offset; }
        sealed class Gull { public Transform root, left, right; public Vector3 center; public float radius, height, speed, phase, flap, glide; }
        sealed class Palm { public Transform t; public Quaternion rest; public float phase, amp; public Vector3 pos; }

        ResortGame game; ResortSite site;
        float sx;
        Material gullMat;
        readonly List<Wave> waves = new List<Wave>();
        readonly List<Gull> gulls = new List<Gull>();
        readonly List<Palm> palms = new List<Palm>();
        readonly HashSet<GameObject> split = new HashSet<GameObject>();
        float checkTimer, gullCallTimer = 6f;
        Transform folder;
        AmbientAudio audioLayer;

        public int Waves => waves.Count;
        public int GullsFlying { get { int n = 0; foreach (var g in gulls) if (g.root.gameObject.activeSelf) n++; return n; } }
        public int PalmCrowns => palms.Count;
        public float WaveAlphaMax { get; private set; }
        public AmbientAudio Audio => audioLayer;
        /// <summary>Wind strength 0..1 (breezier on windy days, calm at night).</summary>
        public float Wind { get; private set; } = 0.5f;

        public void Init(ResortGame g)
        {
            game = g; site = g.Site; sx = g.Layout.Root.position.x;
            folder = new GameObject("AmbientLifeObjects").transform; folder.SetParent(transform, false);
            BuildWaves();
            BuildGulls();
            audioLayer = new GameObject("AmbientAudio").AddComponent<AmbientAudio>();
            audioLayer.transform.SetParent(transform, false);
            audioLayer.Init(g, this);
            SplitPalms();
        }

        // ---------------------------------------------------------------- surf

        void BuildWaves()
        {
            var shader = Shader.Find("Sprites/Default");
            for (int k = 0; k < WaveCount; k++)
            {
                var w = new Wave { offset = k / (float)WaveCount * WavePeriod, verts = new Vector3[(WaveSegments + 1) * 2] };
                var uv = new Vector2[w.verts.Length]; var cols = new Color[w.verts.Length]; var tris = new int[WaveSegments * 6];
                for (int i = 0; i <= WaveSegments; i++)
                {
                    uv[i * 2] = new Vector2(i * 0.5f, 0f); uv[i * 2 + 1] = new Vector2(i * 0.5f, 1f);
                    cols[i * 2] = cols[i * 2 + 1] = Color.white;
                }
                for (int i = 0; i < WaveSegments; i++)
                {
                    int a = i * 2, b = a + 1, c = a + 2, d = a + 3;
                    tris[i * 6] = a; tris[i * 6 + 1] = b; tris[i * 6 + 2] = c; tris[i * 6 + 3] = c; tris[i * 6 + 4] = b; tris[i * 6 + 5] = d;
                }
                w.mesh = new Mesh { name = "SurfFoam" + k }; w.mesh.MarkDynamic();
                w.mesh.vertices = w.verts; w.mesh.uv = uv; w.mesh.colors = cols; w.mesh.triangles = tris;
                w.mesh.bounds = new Bounds(new Vector3(sx, 0f, site.WaterlineZ(sx)), new Vector3(WaveSpan * 2f, 20f, 120f));
                w.mat = new Material(shader) { name = "SurfFoam", color = new Color(1f, 1f, 1f, 0f), renderQueue = 3000 };
                var go = new GameObject("Surf" + k); go.transform.SetParent(folder, false);
                go.AddComponent<MeshFilter>().sharedMesh = w.mesh;
                var mr = go.AddComponent<MeshRenderer>(); mr.sharedMaterial = w.mat;
                mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; mr.receiveShadows = false;
                waves.Add(w);
            }
        }

        void UpdateWaves()
        {
            float night = game.DayNight != null ? game.DayNight.NightFactor : 0f;
            float swell = game.Weather == Weather.Windy ? 1.25f : 1f;
            float tint = Mathf.Lerp(1f, 0.32f, night);
            float peakAlpha = 0f;
            foreach (var w in waves)
            {
                float t = Mathf.Repeat((Time.time + w.offset) / WavePeriod, 1f);
                float dist = Mathf.Lerp(30f * swell, 0.4f, Mathf.Pow(t, 0.75f));          // the crest approaches the beach and decelerates
                float width = Mathf.Lerp(0.5f, 2.6f, t) * swell;
                float alpha = Mathf.Pow(Mathf.Sin(Mathf.PI * Mathf.Clamp01(t * 1.05f)), 1.4f) * 0.8f;
                peakAlpha = Mathf.Max(peakAlpha, alpha);
                w.mat.color = new Color(tint, tint, tint, alpha);
                for (int i = 0; i <= WaveSegments; i++)
                {
                    float x = sx - WaveSpan + i * (WaveSpan * 2f / WaveSegments);
                    float shore = site.WaterlineZ(x);
                    // crests bend a little along their length so the line is not ruler-straight
                    float z = shore - dist + Mathf.Sin(x * 0.045f + w.offset) * 0.9f * Mathf.Clamp01(dist / 8f);
                    float gap = Mathf.Clamp01(dist / 2f);                                    // the last metre merges into the wet sand
                    float y = site.Data.seaLevel + 0.07f;
                    w.verts[i * 2] = new Vector3(x, y, z);
                    w.verts[i * 2 + 1] = new Vector3(x, y, z + width * Mathf.Lerp(0.4f, 1f, gap));
                }
                w.mesh.vertices = w.verts;
            }
            WaveAlphaMax = peakAlpha;
        }

        // ---------------------------------------------------------------- gulls

        void BuildGulls()
        {
            gullMat = StallBuilder.Mat(new Color(0.93f, 0.94f, 0.95f), 0.2f);
            var rng = new System.Random(game.Seed * 17 + 3);
            for (int i = 0; i < 9; i++)
            {
                var root = new GameObject("Gull" + i).transform; root.SetParent(folder, false);
                Part(root, "Body", Vector3.zero, new Vector3(0.18f, 0.16f, 0.52f), PrimitiveType.Sphere);
                Part(root, "Head", new Vector3(0f, 0.05f, 0.3f), new Vector3(0.11f, 0.11f, 0.13f), PrimitiveType.Sphere);
                var beak = Part(root, "Beak", new Vector3(0f, 0.03f, 0.39f), new Vector3(0.03f, 0.03f, 0.08f), PrimitiveType.Cube);
                beak.GetComponent<MeshRenderer>().sharedMaterial = StallBuilder.Mat(new Color(0.95f, 0.72f, 0.1f), 0.2f);
                var left = new GameObject("WingL").transform; left.SetParent(root, false); left.localPosition = new Vector3(-0.07f, 0.04f, 0.06f);
                var right = new GameObject("WingR").transform; right.SetParent(root, false); right.localPosition = new Vector3(0.07f, 0.04f, 0.06f);
                Part(left, "Wing", new Vector3(-0.38f, 0f, 0f), new Vector3(0.76f, 0.025f, 0.2f), PrimitiveType.Cube);
                Part(right, "Wing", new Vector3(0.38f, 0f, 0f), new Vector3(0.76f, 0.025f, 0.2f), PrimitiveType.Cube);
                var tipMat = StallBuilder.Mat(new Color(0.22f, 0.23f, 0.25f), 0.2f);
                Part(left, "Tip", new Vector3(-0.72f, 0f, 0f), new Vector3(0.16f, 0.027f, 0.19f), PrimitiveType.Cube).GetComponent<MeshRenderer>().sharedMaterial = tipMat;
                Part(right, "Tip", new Vector3(0.72f, 0f, 0f), new Vector3(0.16f, 0.027f, 0.19f), PrimitiveType.Cube).GetComponent<MeshRenderer>().sharedMaterial = tipMat;
                float cx = sx + ((float)rng.NextDouble() - 0.5f) * 280f;
                var gl = new Gull
                {
                    root = root, left = left, right = right,
                    center = new Vector3(cx, 0f, site.WaterlineZ(cx) + (float)rng.NextDouble() * 20f - 25f),
                    radius = 22f + (float)rng.NextDouble() * 40f, height = 11f + (float)rng.NextDouble() * 24f,
                    speed = (0.16f + (float)rng.NextDouble() * 0.12f) * (rng.NextDouble() < 0.5 ? 1f : -1f),
                    phase = (float)rng.NextDouble() * 6.28f, flap = 5.5f + (float)rng.NextDouble() * 2f, glide = (float)rng.NextDouble() * 10f,
                };
                gulls.Add(gl);
            }
        }

        GameObject Part(Transform parent, string name, Vector3 pos, Vector3 scale, PrimitiveType type)
        {
            var g = GameObject.CreatePrimitive(type);
            g.name = name; g.transform.SetParent(parent, false); g.transform.localPosition = pos; g.transform.localScale = scale;
            g.GetComponent<MeshRenderer>().sharedMaterial = gullMat;
            g.GetComponent<MeshRenderer>().shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            Destroy(g.GetComponent<Collider>());
            return g;
        }

        void UpdateGulls()
        {
            float night = game.DayNight != null ? game.DayNight.NightFactor : 0f;
            bool day = night < 0.55f;
            foreach (var g in gulls)
            {
                if (g.root.gameObject.activeSelf != day) g.root.gameObject.SetActive(day);
                if (!day) continue;
                float a = g.phase + Time.time * g.speed;
                var p = g.center + new Vector3(Mathf.Cos(a) * g.radius, g.height + Mathf.Sin(Time.time * 0.7f + g.phase) * 1.4f, Mathf.Sin(a) * g.radius * 0.6f);
                var tangent = new Vector3(-Mathf.Sin(a), 0f, Mathf.Cos(a) * 0.6f) * Mathf.Sign(g.speed);
                g.root.position = p;
                g.root.rotation = Quaternion.LookRotation(tangent.normalized, Vector3.up) * Quaternion.Euler(0f, 0f, -Mathf.Sign(g.speed) * 14f);
                // flap in bursts, glide in between
                bool flapping = Mathf.Sin(Time.time * 0.35f + g.glide) > -0.35f;
                float ang = flapping ? Mathf.Sin(Time.time * g.flap + g.phase) * 32f : 6f + Mathf.Sin(Time.time * 1.1f + g.phase) * 3f;
                g.left.localRotation = Quaternion.Euler(0f, 0f, -ang); g.right.localRotation = Quaternion.Euler(0f, 0f, ang);
            }
        }

        /// <summary>Largest tilt (degrees) any palm crown currently has from its rest pose (proves the wind moves them).</summary>
        public float MaxSwayAngle()
        {
            float m = 0f;
            foreach (var p in palms) m = Mathf.Max(m, Quaternion.Angle(p.rest, p.t.localRotation));
            return m;
        }

        /// <summary>World position of a flying gull (for the sound of its call), or null when none are up.</summary>
        public Vector3? AnyGullPosition()
        {
            foreach (var g in gulls) if (g.root.gameObject.activeSelf) return g.root.position;
            return null;
        }

        // ---------------------------------------------------------------- palms

        void ScanPalmPieces()
        {
            if (game.Stages == null) return;
            foreach (var go in game.Stages.Instances)
            {
                if (go == null || !go.activeInHierarchy || split.Contains(go)) continue;
                string n = go.name.ToLowerInvariant();
                if (!n.Contains("palmeiras_folha")) continue;
                split.Add(go);
                SplitCrowns(go);
            }
        }

        void SplitPalms() => ScanPalmPieces();

        /// <summary>Palm trunk tops (world space) from the matching trunk piece: trunk vertices within 0.8 m horizontally belong to one palm, the highest is its crown base.</summary>
        static List<Vector3> TrunkTops(GameObject trunkPiece)
        {
            var pts = new List<Vector3>();
            foreach (var mf in trunkPiece.GetComponentsInChildren<MeshFilter>())
            {
                var mesh = mf.sharedMesh; if (mesh == null || !mesh.isReadable) continue;
                foreach (var v in mesh.vertices) pts.Add(mf.transform.TransformPoint(v));
            }
            var tops = new List<Vector3>(); var cell = new Dictionary<long, List<int>>();
            long Key(int x, int z) => ((long)x << 32) ^ (uint)z;
            foreach (var p in pts)
            {
                int cx = Mathf.FloorToInt(p.x / 0.8f), cz = Mathf.FloorToInt(p.z / 0.8f); int hit = -1;
                for (int dx = -1; dx <= 1 && hit < 0; dx++)
                    for (int dz = -1; dz <= 1 && hit < 0; dz++)
                        if (cell.TryGetValue(Key(cx + dx, cz + dz), out var lst))
                            foreach (var i in lst) { var t = tops[i]; if ((t.x - p.x) * (t.x - p.x) + (t.z - p.z) * (t.z - p.z) < 0.64f) { hit = i; break; } }
                if (hit >= 0) { if (p.y > tops[hit].y) tops[hit] = p; continue; }
                tops.Add(p);
                var k = Key(cx, cz); if (!cell.TryGetValue(k, out var l0)) cell[k] = l0 = new List<int>(); l0.Add(tops.Count - 1);
            }
            return tops;
        }

        /// <summary>
        /// Cuts the welded foliage mesh into one mesh per palm crown: every frond triangle goes to the nearest trunk top (horizontally) and the crown pivots
        /// at that trunk top, so the trunks stay put while the fronds sway.
        /// </summary>
        void SplitCrowns(GameObject piece)
        {
            string wanted = piece.name.ToLowerInvariant().Replace("folha", "tronco"); GameObject trunk = null;
            foreach (var go in game.Stages.Instances) if (go != null && go.name.ToLowerInvariant() == wanted) { trunk = go; break; }
            if (trunk == null) { Debug.LogWarning($"AmbientLife: no trunk piece '{wanted}' for {piece.name}; palms stay still"); return; }
            var tops = TrunkTops(trunk);
            if (tops.Count < 2) { Debug.LogWarning($"AmbientLife: {trunk.name} gave {tops.Count} trunks (mesh unreadable?); palms stay still"); return; }

            int made = 0;
            foreach (var mf in piece.GetComponentsInChildren<MeshFilter>())
            {
                var mr = mf.GetComponent<MeshRenderer>(); var mesh = mf.sharedMesh;
                if (mr == null || mesh == null) continue;
                if (!mesh.isReadable) { Debug.LogWarning($"AmbientLife: mesh {mesh.name} of {piece.name} is not readable; palms stay still"); continue; }
                var verts = mesh.vertices; var normals = mesh.normals; var uvs = mesh.uv; var cols = mesh.colors;
                int vc = verts.Length, nc = tops.Count, subs = mesh.subMeshCount;
                bool hasN = normals != null && normals.Length == vc, hasUv = uvs != null && uvs.Length == vc, hasC = cols != null && cols.Length == vc;
                var tf = mf.transform;
                var pivotsLocal = new Vector3[nc];
                for (int c = 0; c < nc; c++) pivotsLocal[c] = tf.InverseTransformPoint(tops[c] - Vector3.up * 0.3f);

                // nearest trunk for any point (grid over trunk tops would be faster; the trunk count is small enough for a linear scan per triangle)
                int Nearest(Vector3 local)
                {
                    int best = 0; float bd = float.MaxValue;
                    for (int c = 0; c < nc; c++) { float dx = pivotsLocal[c].x - local.x, dz = pivotsLocal[c].z - local.z; float d = dx * dx + dz * dz; if (d < bd) { bd = d; best = c; } }
                    return best;
                }
                var maps = new Dictionary<int, int>[nc];
                var lists = new List<int>[nc];                       // source vertex per local vertex
                var tris = new List<int>[nc][];
                for (int s = 0; s < subs; s++)
                {
                    var t = mesh.GetTriangles(s);
                    for (int i = 0; i + 2 < t.Length; i += 3)
                    {
                        var cen = (verts[t[i]] + verts[t[i + 1]] + verts[t[i + 2]]) / 3f;
                        int c = Nearest(cen);
                        if (maps[c] == null) { maps[c] = new Dictionary<int, int>(); lists[c] = new List<int>(); tris[c] = new List<int>[subs]; for (int q = 0; q < subs; q++) tris[c][q] = new List<int>(); }
                        for (int k = 0; k < 3; k++)
                        {
                            int src = t[i + k];
                            if (!maps[c].TryGetValue(src, out int li)) { li = lists[c].Count; maps[c][src] = li; lists[c].Add(src); }
                            tris[c][s].Add(li);
                        }
                    }
                }
                for (int c = 0; c < nc; c++)
                {
                    if (maps[c] == null) continue;
                    int n = lists[c].Count; var pivot = pivotsLocal[c];
                    var cv = new Vector3[n]; var cn = hasN ? new Vector3[n] : null; var cu = hasUv ? new Vector2[n] : null; var cc = hasC ? new Color[n] : null;
                    for (int j = 0; j < n; j++)
                    {
                        int src = lists[c][j];
                        cv[j] = verts[src] - pivot; if (hasN) cn[j] = normals[src]; if (hasUv) cu[j] = uvs[src]; if (hasC) cc[j] = cols[src];
                    }
                    var m = new Mesh { name = mesh.name + "_crown" + c, subMeshCount = subs };
                    m.vertices = cv; if (hasN) m.normals = cn; if (hasUv) m.uv = cu; if (hasC) m.colors = cc;
                    for (int s = 0; s < subs; s++) m.SetTriangles(tris[c][s], s);
                    m.RecalculateBounds();
                    var go = new GameObject("Crown" + c); go.transform.SetParent(tf, false);
                    go.transform.localPosition = pivot;
                    go.AddComponent<MeshFilter>().sharedMesh = m;
                    var cr = go.AddComponent<MeshRenderer>(); cr.sharedMaterials = mr.sharedMaterials; cr.shadowCastingMode = mr.shadowCastingMode; cr.receiveShadows = mr.receiveShadows;
                    var rnd = new System.Random(c * 7919 + 13);
                    palms.Add(new Palm { t = go.transform, rest = go.transform.localRotation, phase = (float)rnd.NextDouble() * 6.28f, amp = 0.7f + (float)rnd.NextDouble() * 0.7f, pos = go.transform.position });
                    made++;
                }
                mr.enabled = false;                                                            // the welded original is replaced by its crowns
            }
            Debug.Log($"AmbientLife: {made} palm crowns split from {piece.name} ({tops.Count} trunks)");
        }

        void UpdatePalms()
        {
            var cam = Camera.main; if (cam == null || palms.Count == 0) return;
            var cp = cam.transform.position;
            float strength = Wind * (game.Weather == Weather.Windy ? 1.6f : 1f);
            float t = Time.time;
            foreach (var p in palms)
            {
                if ((p.pos - cp).sqrMagnitude > SwayRange * SwayRange) continue;
                float gust = Mathf.Sin(t * 0.55f + p.pos.x * 0.04f) * 0.5f + 0.5f;                          // a gust wave rolling along the shore
                float a = (Mathf.Sin(t * 1.3f + p.phase) * 0.6f + Mathf.Sin(t * 2.9f + p.phase * 1.7f) * 0.25f) * p.amp * (1.5f + 3.5f * gust) * strength;
                p.t.localRotation = p.rest * Quaternion.Euler(a * 0.8f + strength * 1.2f, 0f, a * 0.5f);
            }
        }

        // ---------------------------------------------------------------- frame

        void Update()
        {
            if (game == null || site == null || !site.Ready) return;
            Wind = Mathf.Lerp(Wind, (game.Weather == Weather.Windy ? 0.85f : 0.45f) * Mathf.Lerp(1f, 0.55f, game.DayNight != null ? game.DayNight.NightFactor : 0f), Time.deltaTime * 0.5f);
            UpdateWaves();
            UpdateGulls();
            UpdatePalms();
            checkTimer -= Time.deltaTime;
            if (checkTimer <= 0f) { checkTimer = 1f; ScanPalmPieces(); }
        }
    }
}
