using System.Collections.Generic;
using ResortAurora.Core;
using ResortAurora.Grid;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;

namespace ResortAurora.Placement
{
    /// <summary>
    /// Build mode: a ghost follows the mouse, snaps to grid cells and turns red when the footprint is blocked.
    /// Left click places, R rotates, Esc / right click cancels, B toggles build mode, 1..9 picks a definition.
    /// Depends on <see cref="IGridService"/> and <see cref="IEventBus"/>; inject them with <see cref="Inject"/>.
    /// </summary>
    public sealed class PlacementSystem : MonoBehaviour
    {
        [SerializeField] GridManager gridManager;
        [SerializeField] UnityEngine.Camera worldCamera;
        [SerializeField] List<BuildingDefinition> definitions = new List<BuildingDefinition>();
        [SerializeField] Transform buildingsRoot;

        static readonly int BaseColor = Shader.PropertyToID("_BaseColor"); // URP Lit
        static readonly int LegacyColor = Shader.PropertyToID("_Color");   // built-in fallback

        IGridService grid;
        IEventBus bus;
        BuildingDefinition current;
        GameObject ghost;
        Renderer[] ghostRenderers;
        MaterialPropertyBlock block;
        Vector2Int ghostOrigin;
        int rotation; // quarter turns, 0..3
        int nextOwnerId = 1;
        bool lastValid;

        public bool IsActive => current != null;

        /// <summary>Composition-root hook. Optional: when never called, Awake wires the serialized grid and a private bus.</summary>
        public void Inject(IGridService gridService, IEventBus eventBus) { grid = gridService; bus = eventBus; }

        void Awake()
        {
            grid ??= gridManager;
            bus ??= new EventBus();
            if (worldCamera == null) worldCamera = UnityEngine.Camera.main;
            block = new MaterialPropertyBlock();
            if (buildingsRoot == null) buildingsRoot = new GameObject("Buildings").transform;
            if (definitions.Count == 0) // zero-setup prototype: one 2x2 cube so the scene works with nothing assigned
            {
                var d = ScriptableObject.CreateInstance<BuildingDefinition>();
                d.name = "RuntimeCube";
                definitions.Add(d);
            }
        }

        void Update()
        {
            var kb = Keyboard.current;
            var mouse = Mouse.current;
            if (kb == null || mouse == null || grid == null) return;

            if (kb.bKey.wasPressedThisFrame) { if (IsActive) Cancel(); else Select(definitions[0]); }
            for (int i = 0; i < Mathf.Min(9, definitions.Count); i++)
                if (kb[Key.Digit1 + i].wasPressedThisFrame) Select(definitions[i]);

            if (!IsActive) return;
            if (kb.escapeKey.wasPressedThisFrame || mouse.rightButton.wasPressedThisFrame) { Cancel(); return; }
            if (kb.rKey.wasPressedThisFrame) rotation = (rotation + 1) & 3;

            UpdateGhost(mouse.position.ReadValue());
            if (mouse.leftButton.wasPressedThisFrame && lastValid && !PointerOverUi()) Commit();
        }

        public void Select(BuildingDefinition def)
        {
            Cancel(silent: true);
            current = def;
            rotation = 0;
            ghost = BuildVisual(def, asGhost: true);
            ghostRenderers = ghost.GetComponentsInChildren<Renderer>();
            ghost.SetActive(false);
            bus.Publish(new PlacementModeChanged(true, def.id));
        }

        public void Cancel() => Cancel(false);

        void Cancel(bool silent)
        {
            if (ghost != null) Destroy(ghost);
            ghost = null;
            ghostRenderers = null;
            bool was = current != null;
            current = null;
            if (was && !silent) bus.Publish(new PlacementModeChanged(false, null));
        }

        Vector2Int Footprint => (rotation & 1) == 0 ? current.footprint : new Vector2Int(current.footprint.y, current.footprint.x);

        void UpdateGhost(Vector2 screen)
        {
            if (worldCamera == null || !grid.TryRaycast(worldCamera.ScreenPointToRay(screen), out var hit))
            {
                ghost.SetActive(false);
                lastValid = false;
                return;
            }
            var fp = Footprint;
            // Centre the footprint under the cursor, then snap its min corner to a cell.
            ghostOrigin = grid.WorldToCell(hit) - new Vector2Int(fp.x / 2, fp.y / 2);
            lastValid = grid.CanPlace(ghostOrigin, fp);
            ghost.SetActive(true);
            ghost.transform.SetPositionAndRotation(grid.FootprintCenter(ghostOrigin, fp), Quaternion.Euler(0f, rotation * 90f, 0f));
            Tint(ghostRenderers, lastValid ? new Color(0.3f, 1f, 0.4f, 1f) : new Color(1f, 0.25f, 0.25f, 1f));
        }

        void Commit()
        {
            var fp = Footprint;
            int owner = nextOwnerId++;
            if (!grid.Occupy(ghostOrigin, fp, owner)) return;
            var go = BuildVisual(current, asGhost: false);
            go.transform.SetParent(buildingsRoot, true);
            go.transform.SetPositionAndRotation(grid.FootprintCenter(ghostOrigin, fp), Quaternion.Euler(0f, rotation * 90f, 0f));
            go.name = $"{current.id}#{owner}";
            bus.Publish(new BuildingPlaced(current.id, ghostOrigin, rotation));
        }

        GameObject BuildVisual(BuildingDefinition def, bool asGhost)
        {
            GameObject root;
            if (def.prefab != null) root = Instantiate(def.prefab);
            else
            {
                // Pivot object so the origin sits on the ground at the footprint centre; the cube is its child.
                root = new GameObject(def.id);
                var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
                cube.transform.SetParent(root.transform, false);
                cube.transform.localScale = new Vector3(def.footprint.x * grid.CellSize, def.height, def.footprint.y * grid.CellSize);
                cube.transform.localPosition = new Vector3(0f, def.height * 0.5f, 0f);
                if (!asGhost) Tint(root.GetComponentsInChildren<Renderer>(), def.color);
            }
            // The ghost must never block the placement raycast or any physics.
            if (asGhost) foreach (var c in root.GetComponentsInChildren<Collider>()) Destroy(c);
            return root;
        }

        void Tint(Renderer[] renderers, Color c)
        {
            foreach (var r in renderers)
            {
                r.GetPropertyBlock(block);
                block.SetColor(BaseColor, c);
                block.SetColor(LegacyColor, c);
                r.SetPropertyBlock(block);
            }
        }

        static bool PointerOverUi() => EventSystem.current != null && EventSystem.current.IsPointerOverGameObject();
    }
}
