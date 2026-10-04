using System.Collections.Generic;
using UnityEngine;

namespace FacilityOps
{
    /// <summary>
    /// Minimal door/gate for the vertical slice: [E] opens or closes the leaf around its authored hinge (the leaf's own pivot).
    /// A closed leaf keeps its detailed MeshCollider, so it cannot be crossed; the leaf never closes on the player (the close is refused while the
    /// player's capsule overlaps the leaf's swing volume, and a closing leaf that meets the player reopens). Doors flagged <c>autoClose</c> shut again
    /// after a while once the player has moved away, so a stair door is never left open for good.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class WorldDoor : MonoBehaviour, IInteractable
    {
        public static readonly List<WorldDoor> All = new List<WorldDoor>();

        [SerializeField] private string openPrompt = "[E] Abrir porta";
        [SerializeField] private string closePrompt = "[E] Fechar porta";
        [SerializeField] private Quaternion closedLocalRotation = Quaternion.identity;
        [SerializeField] private Quaternion openLocalRotation = Quaternion.identity;
        [SerializeField] private float degreesPerSecond = 150f;
        [SerializeField] private float autoCloseSeconds = 0f;
        [SerializeField] private bool startsOpen;
        [SerializeField] private string doorId = "";

        private float openAmount;          // 0 closed .. 1 open
        private float target;
        private float openedAt;
        private Collider leafCollider;
        private FirstPersonController player;
        private CharacterController playerBody;

        public string DoorId => string.IsNullOrEmpty(doorId) ? name : doorId;
        public bool IsOpen => target > .5f;
        public bool IsMoving => !Mathf.Approximately(openAmount, target);
        public bool IsFullyOpen => openAmount >= .999f;
        public bool IsFullyClosed => openAmount <= .001f;
        public float AutoCloseSeconds => autoCloseSeconds;
        public Quaternion ClosedLocalRotation => closedLocalRotation;
        public Quaternion OpenLocalRotation => openLocalRotation;

        /// <summary>Editor/stamping setup: the leaf is authored in <paramref name="authoredOpen"/> pose and the other pose is supplied.</summary>
        public void Configure(string id, string openText, string closeText, Quaternion closed, Quaternion open, bool authoredOpen, float autoClose)
        {
            doorId = id; openPrompt = openText; closePrompt = closeText;
            closedLocalRotation = closed; openLocalRotation = open;
            startsOpen = false; autoCloseSeconds = autoClose;
            // The authored pose is whichever the artist modelled; the slice default is always "closed".
            transform.localRotation = closed;
        }

        private void OnEnable()
        {
            if (!All.Contains(this)) All.Add(this);
            leafCollider = GetComponent<Collider>();
            openAmount = target = startsOpen ? 1f : 0f;
            transform.localRotation = Quaternion.Slerp(closedLocalRotation, openLocalRotation, openAmount);
        }
        private void OnDisable() { All.Remove(this); }

        public string GetPrompt(ToolMode tool)
        {
            if (IsMoving) return "";
            return IsOpen ? closePrompt : openPrompt;
        }

        public void Interact(GameRuntime context)
        {
            if (IsMoving) return;
            if (IsOpen)
            {
                if (PlayerInSwing()) { context.Notify("Há alguém no caminho: a porta não fecha."); return; }
                target = 0f;
            }
            else { target = 1f; openedAt = Time.time; }
        }

        /// <summary>Open/close without animation (NavMesh reference bake, tests).</summary>
        public void SetOpenImmediate(bool open)
        {
            target = openAmount = open ? 1f : 0f;
            transform.localRotation = Quaternion.Slerp(closedLocalRotation, openLocalRotation, openAmount);
            if (open) openedAt = Time.time;
        }
        public void Request(bool open)
        {
            if (open == IsOpen || IsMoving) return;
            if (!open && PlayerInSwing()) return;
            target = open ? 1f : 0f;
            if (open) openedAt = Time.time;
        }

        private void Update()
        {
            if (IsMoving)
            {
                float angle = Quaternion.Angle(closedLocalRotation, openLocalRotation);
                float step = angle < .01f ? 1f : degreesPerSecond * Time.deltaTime / angle;
                float previous = openAmount;
                openAmount = Mathf.MoveTowards(openAmount, target, step);
                transform.localRotation = Quaternion.Slerp(closedLocalRotation, openLocalRotation, openAmount);
                if (target < previous && PlayerInSwing())
                {
                    target = 1f; openAmount = previous;                           // a closing leaf never pushes into the player
                    transform.localRotation = Quaternion.Slerp(closedLocalRotation, openLocalRotation, openAmount);
                }
                return;
            }
            if (autoCloseSeconds > 0f && IsOpen && Time.time - openedAt > autoCloseSeconds && !PlayerNear(5f) && !PlayerInSwing())
                target = 0f;
        }

        private bool EnsurePlayer()
        {
            if (player == null) { player = FindAnyObjectByType<FirstPersonController>(); playerBody = player != null ? player.GetComponent<CharacterController>() : null; }
            return playerBody != null;
        }
        private bool PlayerNear(float meters)
        {
            if (!EnsurePlayer()) return false;
            return Vector3.Distance(playerBody.transform.position, leafCollider != null ? leafCollider.bounds.center : transform.position) < meters;
        }
        private bool PlayerInSwing()
        {
            if (!EnsurePlayer() || leafCollider == null) return false;
            // Swept region of the leaf between its two poses (bounds of both poses + a margin) tested against the player's capsule.
            Bounds swing = leafCollider.bounds;
            Quaternion keep = transform.localRotation;
            transform.localRotation = closedLocalRotation; swing.Encapsulate(leafCollider.bounds);
            transform.localRotation = openLocalRotation; swing.Encapsulate(leafCollider.bounds);
            transform.localRotation = keep;
            swing.Expand(new Vector3(.2f, 0f, .2f));
            return playerBody.bounds.Intersects(swing);
        }
    }

    /// <summary>[E] on a remote (the Horizonte intercom) toggles a linked door/gate.</summary>
    public sealed class WorldDoorRemote : MonoBehaviour, IInteractable
    {
        [SerializeField] private WorldDoor door;
        [SerializeField] private string prompt = "[E] Interfone: abrir o portão";
        public void Configure(WorldDoor target, string text) { door = target; prompt = text; }
        public string GetPrompt(ToolMode tool) => door != null && door.IsOpen ? "[E] Interfone: fechar o portão" : prompt;
        public void Interact(GameRuntime context) { if (door != null) door.Interact(context); }
    }
}
