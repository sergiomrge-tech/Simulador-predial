using UnityEngine;
using UnityEngine.InputSystem;

namespace ResortAurora.Game
{
    /// <summary>First-person walker with a use-ray. Interaction reach is fixed (2.6 m) and independent of camera tweaks.</summary>
    [RequireComponent(typeof(CharacterController))]
    public sealed class PlayerController : MonoBehaviour
    {
        public const float Reach = 2.6f;
        [SerializeField] Transform head;
        [SerializeField] float walkSpeed = 3.4f, runSpeed = 5.6f, lookSpeed = 0.12f;

        CharacterController cc;
        ResortGame game;
        float pitch, vy;
        Interactable target, holding;
        float holdTime;

        public Interactable Target => target;
        public float HoldProgress => holding == null ? 0f : Mathf.Clamp01(holdTime / Mathf.Max(0.01f, holding.HoldDuration(game)));
        public bool Frozen { get; set; }

        public void Bind(ResortGame g) => game = g;

        void Awake()
        {
            cc = GetComponent<CharacterController>();
            if (head == null) head = GetComponentInChildren<Camera>().transform;
        }

        void Update()
        {
            var kb = Keyboard.current; var mouse = Mouse.current;
            if (kb == null || mouse == null || game == null) return;
            if (Frozen) { CancelHold(); target = null; return; }

            var look = mouse.delta.ReadValue() * lookSpeed;
            transform.Rotate(0f, look.x, 0f);
            pitch = Mathf.Clamp(pitch - look.y, -80f, 80f);
            head.localRotation = Quaternion.Euler(pitch, 0f, 0f);

            var m = Vector2.zero;
            if (kb.wKey.isPressed) m.y += 1; if (kb.sKey.isPressed) m.y -= 1;
            if (kb.dKey.isPressed) m.x += 1; if (kb.aKey.isPressed) m.x -= 1;
            if (m.sqrMagnitude > 1f) m.Normalize();
            float speed = kb.leftShiftKey.isPressed ? runSpeed : walkSpeed;
            vy = cc.isGrounded ? -1f : vy - 20f * Time.deltaTime;
            var vel = transform.TransformDirection(new Vector3(m.x, 0f, m.y)) * speed + Vector3.up * vy;
            cc.Move(vel * Time.deltaTime);

            UpdateTarget(kb);
        }

        void UpdateTarget(Keyboard kb)
        {
            Interactable found = null;
            if (Physics.Raycast(head.position, head.forward, out var hit, Reach, ~0, QueryTriggerInteraction.Collide))
                found = hit.collider.GetComponentInParent<Interactable>();
            if (holding != null && found != holding) CancelHold();
            target = found;
            if (target == null || !target.CanUse(game)) { if (holding != null) CancelHold(); return; }

            if (target.holdSeconds > 0f)
            {
                if (kb.eKey.wasPressedThisFrame && holding == null && target.BeginHold(game)) { holding = target; holdTime = 0f; }
                if (holding != null)
                {
                    if (!kb.eKey.isPressed) { CancelHold(); return; }
                    holdTime += Time.deltaTime;
                    if (holdTime >= holding.HoldDuration(game)) { var h = holding; holding = null; h.Use(game); }
                }
            }
            else if (kb.eKey.wasPressedThisFrame) target.Use(game);
        }

        void CancelHold() { if (holding != null) { holding.CancelHold(game); holding = null; } }
    }
}
