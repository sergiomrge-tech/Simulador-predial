using System.Collections.Generic;
using ResortAurora.Site;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>Draws every parcel's boundary on the ground (green owned, yellow for sale, red locked) and a sign you can use to open the land panel.</summary>
    public sealed class ParcelMarkers : MonoBehaviour
    {
        sealed class Entry { public Rect2 data; public LineRenderer line; public TextMesh label; public string lastKey; }
        readonly List<Entry> entries = new List<Entry>();
        ResortGame game;

        public void Init(ResortGame g)
        {
            game = g;
            foreach (var p in g.Site.Data.parcels)
            {
                if (p.id == "P0") continue;                         // the stall spot is drawn by the stall itself
                var go = new GameObject("Parcel " + p.id);
                go.transform.SetParent(transform, false);
                var lr = go.AddComponent<LineRenderer>();
                lr.sharedMaterial = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
                lr.loop = true; lr.widthMultiplier = 0.18f; lr.positionCount = 4; lr.useWorldSpace = true;
                lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                var corners = new[] { new Vector2(p.x, p.z), new Vector2(p.x + p.width, p.z), new Vector2(p.x + p.width, p.z + p.depth), new Vector2(p.x, p.z + p.depth) };
                for (int i = 0; i < 4; i++) lr.SetPosition(i, new Vector3(corners[i].x, g.Site.HeightAt(corners[i].x, corners[i].y) + 0.35f, corners[i].y));

                // sign on the south edge, readable from the avenue side
                float sx = p.x + Mathf.Min(3f, p.width * 0.5f), sz = p.z - 0.5f;
                float gy = g.Site.HeightAt(sx, sz);
                var sign = StallBuilder.Box("Sign", go.transform, new Vector3(sx, gy + 1.2f, sz), new Vector3(1.6f, 1.1f, 0.12f), new Color(0.95f, 0.9f, 0.7f));
                StallBuilder.Box("Post", go.transform, new Vector3(sx, gy + 0.5f, sz), new Vector3(0.12f, 1.0f, 0.12f), new Color(0.4f, 0.28f, 0.18f), collider: false);
                var st = sign.AddComponent<PanelStation>(); st.panel = Panel.Parcels; st.label = "Terrenos: " + p.name;
                var label = StallBuilder.Label(go.transform, new Vector3(sx, gy + 2.4f, sz), p.name, 40, 0.1f);
                entries.Add(new Entry { data = p, line = lr, label = label });
            }
        }

        const float ShowRange = 22f;                           // boundary and label only appear when you are close to the land (a beach full of red lines is not a beach)

        const float LockedRange = 6f;

        void Update()
        {
            if (game == null || game.Parcels == null) return;
            var cam = Camera.main; var cp = cam != null ? cam.transform.position : Vector3.zero;
            foreach (var e in entries)
            {
                float dx = Mathf.Max(e.data.x - cp.x, 0f, cp.x - (e.data.x + e.data.width)), dz = Mathf.Max(e.data.z - cp.z, 0f, cp.z - (e.data.z + e.data.depth));
                var status = game.Parcels.StatusOf(e.data.id, game.Stall.Reputation);
                float range = status == ParcelStatus.Locked ? LockedRange : ShowRange;   // land you cannot buy yet stays out of the way
                bool near = cam == null || dx * dx + dz * dz < range * range;
                if (e.line.enabled != near) { e.line.enabled = near; e.label.gameObject.SetActive(near); }
                string key = status.ToString();
                if (key == e.lastKey) continue;
                e.lastKey = key;
                Color c = status == ParcelStatus.Owned ? new Color(0.25f, 0.9f, 0.35f) : status == ParcelStatus.Available ? new Color(1f, 0.85f, 0.2f) : new Color(0.9f, 0.3f, 0.25f);
                e.line.startColor = e.line.endColor = c;
                e.line.sharedMaterial.color = c;
                e.label.text = status == ParcelStatus.Owned ? e.data.name + "\nSEU" : status == ParcelStatus.Available ? e.data.name + "\nÀ VENDA R$ " + e.data.price : e.data.name + "\nINDISPONÍVEL";
                e.label.color = c;
            }
        }
    }
}
