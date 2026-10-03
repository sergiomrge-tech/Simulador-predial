using UnityEngine;
using UnityEngine.InputSystem;

namespace FacilityOps
{
    public interface IInteractable
    {
        string GetPrompt(ToolMode tool);
        void Interact(GameRuntime context);
    }
    public sealed class TechnicalStation : MonoBehaviour, IInteractable
    {
        public StationId id;
        public string label;
        public string GetPrompt(ToolMode tool) => "[E] " + GameRuntime.ToolNames[(int)tool] + "  •  " + label;
        public void Interact(GameRuntime context) { context.UseStation(id); }
    }
    public sealed class OfficeTerminal : MonoBehaviour, IInteractable
    {
        public string GetPrompt(ToolMode tool) => "[E] Abrir central de chamados";
        public void Interact(GameRuntime context) { context.SetTablet(true); }
    }
    public sealed class FirstPersonController : MonoBehaviour
    {
        public Camera view;
        public GameRuntime game;
        public float sensitivity = 0.12f;
        private CharacterController controller;
        private float pitch;
        private float vertical;
        public IInteractable Focus { get; private set; }
        public void Initialize(GameRuntime runtime)
        {
            game = runtime;
            controller = gameObject.AddComponent<CharacterController>();
            controller.height = 1.8f;
            controller.radius = 0.28f;
            controller.center = Vector3.up * .9f;
            var cameraObject = new GameObject("Player Camera");
            cameraObject.transform.SetParent(transform, false);
            cameraObject.transform.localPosition = Vector3.up * 1.65f;
            view = cameraObject.AddComponent<Camera>();
            view.nearClipPlane = .05f;
            view.fieldOfView = 75;
            view.tag = "MainCamera";
            cameraObject.AddComponent<AudioListener>();
        }
        private void Update()
        {
            var keyboard = Keyboard.current;
            if (keyboard == null || game == null) return;
            if (keyboard.tabKey.wasPressedThisFrame || keyboard.escapeKey.wasPressedThisFrame) game.SetTablet(!game.TabletOpen);
            if (game.TabletOpen || game.IsSmokeTest) { Focus = null; return; }
            if (Mouse.current != null)
            {
                Vector2 delta = Mouse.current.delta.ReadValue() * sensitivity;
                transform.Rotate(0, delta.x, 0);
                pitch = Mathf.Clamp(pitch - delta.y, -80, 80);
            }
            float x = (keyboard.dKey.isPressed ? 1 : 0) - (keyboard.aKey.isPressed ? 1 : 0);
            float z = (keyboard.wKey.isPressed ? 1 : 0) - (keyboard.sKey.isPressed ? 1 : 0);
            if (controller.isGrounded && vertical < 0) vertical = -2;
            vertical += -20 * Time.deltaTime;
            controller.Move((transform.TransformDirection(new Vector3(x, 0, z).normalized) * (keyboard.leftShiftKey.isPressed ? 5 : 3) + Vector3.up * vertical) * Time.deltaTime);
            UpdateCamera();
            if (keyboard.digit1Key.wasPressedThisFrame) game.Tool = ToolMode.Inspect;
            if (keyboard.digit2Key.wasPressedThisFrame) game.Tool = ToolMode.Scanner;
            if (keyboard.digit3Key.wasPressedThisFrame) game.Tool = ToolMode.SignalProbe;
            if (keyboard.digit4Key.wasPressedThisFrame) game.Tool = ToolMode.Repair;
            if (keyboard.digit5Key.wasPressedThisFrame) game.Tool = ToolMode.Verify;
            if (keyboard.digit6Key.wasPressedThisFrame) game.Tool = ToolMode.Isolate;
            if (keyboard.digit7Key.wasPressedThisFrame) game.Tool = ToolMode.Restore;
            RefreshFocus();
            if (keyboard.eKey.wasPressedThisFrame && Focus != null) Focus.Interact(game);
        }
        public void RefreshFocus()
        {
            Focus = null;
            if (Physics.Raycast(view.transform.position, view.transform.forward, out RaycastHit hit, 3, ~(1 << 2)))
                Focus = hit.collider.GetComponentInParent<IInteractable>();
        }
        public void Teleport(Vector3 position, float yaw = 0)
        {
            controller.enabled = false;
            transform.SetPositionAndRotation(position, Quaternion.Euler(0, yaw, 0));
            controller.enabled = true;
            pitch = 0;
            vertical = 0;
            UpdateCamera();
        }
        public void AimAt(Vector3 position) { view.transform.LookAt(position); }
        private void UpdateCamera()
        {
            view.transform.localPosition = Vector3.up * 1.65f;
            view.transform.localRotation = Quaternion.Euler(pitch,0,0);
        }
    }
}
