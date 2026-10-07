using System.Collections.Generic;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Scene body of a kiosk customer. The pure <see cref="Customer"/> object decides what happens; this component only walks to where the state
    /// says the person should be. After being served some customers take a free table on the sand, drink there for a while, then leave.
    /// </summary>
    public sealed class CustomerAgent : MonoBehaviour
    {
        enum Mode { Approach, Queue, Pickup, ToSeat, Seated, Leave }

        ResortGame game; Customer data; Mode mode;
        Vector3 exitPoint; float speed; TextMesh label; PersonRig rig;
        readonly List<Vector3> path = new List<Vector3>();
        Seat seat; float seatTimer; bool decided;

        public void Init(ResortGame g, Customer c, bool fromWest, float variety)
        {
            game = g; data = c;
            var lay = g.Layout;
            float startX = fromWest ? lay.WestX : lay.EastX;
            exitPoint = lay.LanePoint(fromWest ? lay.EastX : lay.WestX);
            speed = 1.1f + variety * 0.7f;
            rig = PersonRig.Create(new System.Random((int)(variety * 100000f) + c.Id * 7919), PersonKind.Casual, "Body");
            rig.transform.SetParent(transform, false);
            transform.position = lay.LanePoint(startX);
            mode = Mode.Approach;
            label = StallBuilder.Label(transform, new Vector3(0f, 2.35f * rig.Scale, 0f), c.Product.Name, 40, 0.05f);
        }

        void OnDestroy() { if (seat != null) seat.Taken = false; }

        void Update()
        {
            if (game == null) return;
            var lay = game.Layout;
            UpdateState(lay);

            if (mode == Mode.Seated)
            {
                seatTimer -= Time.deltaTime;
                transform.SetPositionAndRotation(seat.Pos, Quaternion.Euler(0f, seat.Yaw, 0f));
                rig.Gesture = Gesture.Drink; rig.Animate(Pose.SitChair, 0f, Time.deltaTime);
                if (seatTimer <= 0f || !seat.Enabled) StandUp(lay);
                label.text = "";
                return;
            }

            Vector3 target;
            switch (mode)
            {
                case Mode.Approach: target = lay.LanePoint(lay.Root.position.x); break;
                case Mode.Queue: target = lay.QueueSlot(Mathf.Max(0, game.Service.QueueIndex(data))); break;
                case Mode.Pickup: target = lay.PickupPos; break;
                case Mode.ToSeat: target = path.Count > 0 ? path[0] : seat.Pos; break;
                default: target = path.Count > 0 ? path[0] : exitPoint; break;
            }
            if (mode == Mode.Leave && path.Count == 0) target.y = 0f;
            bool moved = MoveTowards(target, lay);

            if (mode == Mode.Approach && Flat(transform.position, lay.LanePoint(lay.Root.position.x)) < 0.6f) mode = Mode.Queue;
            if ((mode == Mode.ToSeat || mode == Mode.Leave) && path.Count > 0 && Flat(transform.position, path[0]) < 0.35f) path.RemoveAt(0);
            if (mode == Mode.ToSeat && path.Count == 0 && Flat(transform.position, seat.Pos) < 0.15f) { mode = Mode.Seated; seatTimer = 25f + 30f * Random.value; }
            if (mode == Mode.Leave && path.Count == 0 && Flat(transform.position, exitPoint) < 1.2f) { game.ForgetAgent(this); Destroy(gameObject); return; }

            rig.Gesture = Gesture.None;
            rig.Animate(moved ? Pose.Walk : Pose.Stand, speed, Time.deltaTime);
            bool waiting = data.State != CustomerState.Left && data.State != CustomerState.Served;
            label.text = waiting ? Caption() : "";
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
                    if (decided) break;
                    decided = true;
                    float chance = 0.35f + (game.Stall.Has("up.mesas") ? 0.25f : 0f);
                    var s = Random.value < chance ? lay.TakeSeat() : null;
                    if (s != null) { seat = s; BuildSeatPath(lay, s); mode = Mode.ToSeat; }
                    else BeginLeave(lay);
                    break;
                case CustomerState.Left: if (mode != Mode.Leave && mode != Mode.Seated && mode != Mode.ToSeat) BeginLeave(lay); break;
                case CustomerState.Queued: if (mode == Mode.Pickup) mode = Mode.Queue; break;
            }
        }

        /// <summary>The kiosk faces the promenade, the tables are beside and behind it: out past the end of the counter, then along to the chair.</summary>
        void BuildSeatPath(StallLayout lay, Seat s)
        {
            path.Clear();
            path.AddRange(lay.RouteToSeat(s));
        }

        void BeginLeave(StallLayout lay)
        {
            mode = Mode.Leave;
            exitPoint = lay.LanePoint(transform.position.x < lay.Root.position.x ? lay.WestX : lay.EastX);
        }

        void StandUp(StallLayout lay)
        {
            path.Clear();
            var route = lay.RouteToSeat(seat);
            route.Reverse();
            path.AddRange(route);
            seat.Taken = false; seat = null;
            BeginLeave(lay);
        }

        static float Flat(Vector3 a, Vector3 b) { a.y = b.y = 0f; return Vector3.Distance(a, b); }

        bool MoveTowards(Vector3 target, StallLayout lay)
        {
            var p = transform.position;
            var to = target - p; to.y = 0f;
            float d = to.magnitude;
            bool moving = d > 0.05f;
            if (moving)
            {
                p += to / d * Mathf.Min(d, speed * Time.deltaTime);
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(to), 8f * Time.deltaTime);
            }
            p.y = lay.Ground(p).y;
            transform.position = p;
            return moving;
        }
    }

    /// <summary>Scene body of an employee: stays at the station and works (hands busy) while there is work for the role.</summary>
    public sealed class StaffAgent : MonoBehaviour
    {
        ResortGame game; StaffMember member; PersonRig rig;

        public static Color ColorFor(StaffMember s) => s.role == StaffRole.Cozinheiro ? new Color(0.92f, 0.92f, 0.9f) : new Color(0.2f, 0.55f, 0.55f);

        public void Init(ResortGame g, StaffMember m)
        {
            game = g; member = m; rig = GetComponent<PersonRig>();
            StallBuilder.Label(transform, new Vector3(0f, 2.25f, 0f), m.name, 36, 0.04f);
            transform.rotation = Quaternion.LookRotation(Vector3.forward);               // face the promenade
        }

        void Update()
        {
            if (game == null) return;
            bool busy = member.role == StaffRole.Cozinheiro ? game.Service.Tickets.Count > 0 : game.Service.Queue.Count > 0 || game.Service.Ready.Count > 0;
            rig.Gesture = busy ? Gesture.Dig : Gesture.None;
            rig.Animate(Pose.Stand, 0f, Time.deltaTime);
        }
    }
}
