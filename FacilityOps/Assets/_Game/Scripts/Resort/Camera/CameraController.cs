using UnityEngine;
using UnityEngine.InputSystem;

namespace ResortAurora.CameraSystem
{
    /// <summary>
    /// RTS / tycoon camera. Attach to an empty "CameraRig" and make the Main Camera its child.
    /// The rig moves on the ground plane (WASD / arrows / screen edge), rotates around Y (Q/E or middle-mouse drag),
    /// and the camera child is dollied along a pitched arm for zoom (scroll wheel).
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class CameraController : MonoBehaviour
    {
        [Header("Target")]
        [SerializeField] Transform cameraTransform;

        [Header("Pan")]
        [SerializeField] float panSpeed = 25f;
        [SerializeField, Tooltip("Pan speed multiplier at max zoom-out.")] float zoomPanBoost = 2.5f;
        [SerializeField] bool edgePan = true;
        [SerializeField, Min(1)] int edgeSizePixels = 12;
        [SerializeField] float shiftMultiplier = 2f;

        [Header("Rotation")]
        [SerializeField] float keyRotateSpeed = 90f;
        [SerializeField] float dragRotateSpeed = 0.25f;

        [Header("Zoom")]
        [SerializeField] float minDistance = 8f;
        [SerializeField] float maxDistance = 70f;
        [SerializeField] float zoomStep = 4f;
        [SerializeField, Range(15f, 85f)] float pitch = 55f;

        [Header("Feel / Limits")]
        [SerializeField] float smoothTime = 0.12f;
        [SerializeField, Tooltip("Rig X limits (min, max). Match the grid extents.")] Vector2 boundsX = new Vector2(-10f, 74f);
        [SerializeField, Tooltip("Rig Z limits (min, max). Match the grid extents.")] Vector2 boundsZ = new Vector2(-10f, 74f);

        Vector3 targetPos;
        float targetYaw, yaw;
        float targetDistance, distance;
        Vector3 velocity;
        float yawVelocity, distVelocity;

        void Awake()
        {
            if (cameraTransform == null && UnityEngine.Camera.main != null) cameraTransform = UnityEngine.Camera.main.transform;
            targetPos = transform.position;
            targetYaw = yaw = transform.eulerAngles.y;
            targetDistance = distance = Mathf.Clamp((minDistance + maxDistance) * 0.5f, minDistance, maxDistance);
            ApplyCameraArm();
        }

        void Update()
        {
            var kb = Keyboard.current;
            var mouse = Mouse.current;
            if (kb == null || mouse == null) return;
            float dt = Time.unscaledDeltaTime; // stays responsive while the simulation is paused

            // Rotation
            if (kb.qKey.isPressed) targetYaw -= keyRotateSpeed * dt;
            if (kb.eKey.isPressed) targetYaw += keyRotateSpeed * dt;
            if (mouse.middleButton.isPressed) targetYaw += mouse.delta.ReadValue().x * dragRotateSpeed;

            // Zoom
            float scroll = mouse.scroll.ReadValue().y;
            if (Mathf.Abs(scroll) > 0.01f) targetDistance = Mathf.Clamp(targetDistance - Mathf.Sign(scroll) * zoomStep, minDistance, maxDistance);

            // Pan, relative to the current yaw
            var move = Vector2.zero;
            if (kb.wKey.isPressed || kb.upArrowKey.isPressed) move.y += 1;
            if (kb.sKey.isPressed || kb.downArrowKey.isPressed) move.y -= 1;
            if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) move.x += 1;
            if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) move.x -= 1;
            if (edgePan && Application.isFocused) move += EdgeDirection(mouse.position.ReadValue());
            if (move.sqrMagnitude > 1f) move.Normalize();

            float zoomT = Mathf.InverseLerp(minDistance, maxDistance, targetDistance);
            float speed = panSpeed * Mathf.Lerp(1f, zoomPanBoost, zoomT) * (kb.leftShiftKey.isPressed ? shiftMultiplier : 1f);
            targetPos += Quaternion.Euler(0f, targetYaw, 0f) * new Vector3(move.x, 0f, move.y) * (speed * dt);
            targetPos.x = Mathf.Clamp(targetPos.x, boundsX.x, boundsX.y);
            targetPos.z = Mathf.Clamp(targetPos.z, boundsZ.x, boundsZ.y);

            // Smooth towards the targets
            transform.position = Vector3.SmoothDamp(transform.position, targetPos, ref velocity, smoothTime, Mathf.Infinity, dt);
            yaw = Mathf.SmoothDampAngle(yaw, targetYaw, ref yawVelocity, smoothTime, Mathf.Infinity, dt);
            distance = Mathf.SmoothDamp(distance, targetDistance, ref distVelocity, smoothTime, Mathf.Infinity, dt);
            transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            ApplyCameraArm();
        }

        Vector2 EdgeDirection(Vector2 p)
        {
            if (p.x < 0 || p.y < 0 || p.x > Screen.width || p.y > Screen.height) return Vector2.zero; // cursor outside the window
            var d = Vector2.zero;
            if (p.x <= edgeSizePixels) d.x -= 1; else if (p.x >= Screen.width - edgeSizePixels) d.x += 1;
            if (p.y <= edgeSizePixels) d.y -= 1; else if (p.y >= Screen.height - edgeSizePixels) d.y += 1;
            return d;
        }

        void ApplyCameraArm()
        {
            if (cameraTransform == null) return;
            // The camera sits behind the rig along the pitched arm, looking at the rig.
            var pitchRot = Quaternion.Euler(pitch, 0f, 0f);
            cameraTransform.localPosition = pitchRot * Vector3.back * distance;
            cameraTransform.localRotation = pitchRot;
        }

        /// <summary>Focus helper for future systems (click a guest, jump to a building).</summary>
        public void FocusOn(Vector3 world) => targetPos = new Vector3(world.x, transform.position.y, world.z);
    }
}
