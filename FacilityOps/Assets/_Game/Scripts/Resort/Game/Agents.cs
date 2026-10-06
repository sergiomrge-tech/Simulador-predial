using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Scene body of a customer (or of a cosmetic passer-by when <c>data == null</c>). The pure <see cref="Customer"/> object decides what
    /// happens; this component only walks to where the state says the person should be.
    /// </summary>
    public sealed class CustomerAgent : MonoBehaviour
    {
        enum Mode { Approach, Queue, Pickup, Leave, Pass }

        ResortGame game; Customer data; Mode mode;
        Vector3 exitPoint; float speed; TextMesh label; Transform body;
        float bob;

        public void Init(ResortGame g, Customer c, bool fromWest, float variety)
        {
            game = g; data = c;
            var lay = g.Layout;
            float startX = fromWest ? lay.WestX : lay.EastX;
            exitPoint = lay.LanePoint(fromWest ? lay.EastX : lay.WestX);
            speed = 1.1f + variety * 0.7f;
            var shirt = Color.HSVToRGB(variety, 0.45f + 0.3f * (variety * 7f % 1f), 0.8f);
            var vis = StallBuilder.Person("Body", shirt, Vector3.zero);
            vis.transform.SetParent(transform, false);
            body = vis.transform;
            body.localScale = Vector3.one * (0.92f + 0.14f * (variety * 13f % 1f));
            transform.position = lay.LanePoint(startX);
            mode = c != null ? Mode.Approach : Mode.Pass;
            if (c != null) label = StallBuilder.Label(transform, new Vector3(0f, 2.35f, 0f), c.Product.Name, 40, 0.05f);
        }

        void Update()
        {
            if (game == null) return;
            var lay = game.Layout;
            if (data != null) UpdateState(lay);

            Vector3 target = mode switch
            {
                Mode.Approach => lay.LanePoint(lay.Root.position.x + 0.0f),
                Mode.Queue => lay.QueueSlot(Mathf.Max(0, game.Service.QueueIndex(data))),
                Mode.Pickup => lay.PickupPos,
                _ => exitPoint,
            };
            if (mode == Mode.Leave || mode == Mode.Pass) target.y = 0f;
            MoveTowards(target, lay);

            if (mode == Mode.Approach && Flat(transform.position, lay.LanePoint(lay.Root.position.x)) < 0.6f) mode = Mode.Queue;
            if ((mode == Mode.Leave || mode == Mode.Pass) && Flat(transform.position, exitPoint) < 1.2f) { game.ForgetAgent(this); Destroy(gameObject); }
            if (label != null) label.text = data != null && data.State != CustomerState.Left && data.State != CustomerState.Served ? Caption() : "";
        }

        string Caption()
        {
            string bar = new string('|', Mathf.CeilToInt(data.Satisfaction * 8f));
            return data.Product.Name + "\n" + bar;
        }

        void UpdateState(StallLayout lay)
        {
            switch (data.State)
            {
                case CustomerState.WaitingFood:
                case CustomerState.Ready: mode = Mode.Pickup; break;
                case CustomerState.Served:
                case CustomerState.Left: if (mode != Mode.Leave) { mode = Mode.Leave; exitPoint = lay.LanePoint(transform.position.x < lay.Root.position.x ? lay.WestX : lay.EastX); } break;
                case CustomerState.Queued: if (mode == Mode.Pickup) mode = Mode.Queue; break;
            }
        }

        static float Flat(Vector3 a, Vector3 b) { a.y = b.y = 0f; return Vector3.Distance(a, b); }

        void MoveTowards(Vector3 target, StallLayout lay)
        {
            var p = transform.position;
            var to = target - p; to.y = 0f;
            float d = to.magnitude;
            if (d > 0.05f)
            {
                var step = to / d * Mathf.Min(d, speed * Time.deltaTime);
                p += step;
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(to), 8f * Time.deltaTime);
                bob += Time.deltaTime * speed * 6f;
            }
            p.y = lay.Site.HeightAt(p.x, p.z);
            transform.position = p;
            if (body != null) body.localPosition = new Vector3(0f, d > 0.1f ? Mathf.Abs(Mathf.Sin(bob)) * 0.05f : 0f, 0f);
        }
    }

    /// <summary>Scene body of an employee: stays at the station and bobs while there is work for the role.</summary>
    public sealed class StaffAgent : MonoBehaviour
    {
        ResortGame game; StaffMember member; Vector3 basePos; TextMesh tag;

        public static Color ColorFor(StaffMember s) => s.role == StaffRole.Cozinheiro ? new Color(0.92f, 0.92f, 0.9f) : new Color(0.2f, 0.55f, 0.55f);

        public void Init(ResortGame g, StaffMember m)
        {
            game = g; member = m; basePos = transform.position;
            tag = StallBuilder.Label(transform, new Vector3(0f, 2.25f, 0f), m.name, 36, 0.04f);
            // face the promenade
            transform.rotation = Quaternion.LookRotation(Vector3.forward);
        }

        void Update()
        {
            if (game == null) return;
            bool busy = member.role == StaffRole.Cozinheiro ? game.Service.Tickets.Count > 0 : game.Service.Queue.Count > 0 || game.Service.Ready.Count > 0;
            transform.position = basePos + (busy ? Vector3.up * Mathf.Abs(Mathf.Sin(Time.time * 7f)) * 0.04f : Vector3.zero);
        }
    }
}
