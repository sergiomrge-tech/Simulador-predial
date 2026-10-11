using System.Linq;
using System.Collections.Generic;
using ResortAurora.Site;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortAurora.Game
{
    /// <summary>Selective CC0 furniture and project-owned PBR dressing. No changes to the service simulation or seat ownership.</summary>
    public static class RealisticKioskAssets
    {
        static readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        const string Textures = "Art/Resort/Textures/";
        static readonly Dictionary<Color, Material> canopyMaterials = new Dictionary<Color, Material>();

        public static Material CanopyMaterial(Color color)
        {
            if (canopyMaterials.TryGetValue(color, out var cached) && cached != null) return cached;
            var baseMap = Resources.Load<Texture2D>("Art/Resort/Props/fabric_BaseColor");
            var normal = Resources.Load<Texture2D>("Art/Resort/Props/fabric_Normal");
            var mask = Resources.Load<Texture2D>("Art/Resort/Props/fabric_MetallicGloss");
            if (baseMap == null || normal == null || mask == null) return StallBuilder.Mat(color, 0.1f);
            var material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "WovenCanopyPBR", enableInstancing = true };
            material.SetColor("_BaseColor", color); material.SetTexture("_BaseMap", baseMap);
            material.SetTexture("_BumpMap", normal); material.SetFloat("_BumpScale", 0.3f); material.EnableKeyword("_NORMALMAP");
            material.SetTexture("_MetallicGlossMap", mask); material.SetFloat("_Smoothness", 1f); material.EnableKeyword("_METALLICSPECGLOSSMAP");
            material.SetTextureScale("_BaseMap", Vector2.one * 24f);
            material.SetTextureScale("_BumpMap", Vector2.one * 24f);
            canopyMaterials[color] = material; return material;
        }

        static Material MaterialFor(string set)
        {
            if (materials.TryGetValue(set, out var cached) && cached != null) return cached;
            var color = Resources.Load<Texture2D>(Textures + set + "_BaseColor");
            var normal = Resources.Load<Texture2D>(Textures + set + "_Normal");
            var gloss = Resources.Load<Texture2D>(Textures + set + "_MetallicGloss");
            if (color == null || normal == null || gloss == null) return null;
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "PBR_" + set, enableInstancing = true };
            m.SetTexture("_BaseMap", color); m.SetTexture("_BumpMap", normal);
            m.EnableKeyword("_NORMALMAP"); m.SetFloat("_BumpScale", 0.65f);
            m.SetTexture("_MetallicGlossMap", gloss); m.EnableKeyword("_METALLICSPECGLOSSMAP");
            m.SetFloat("_Smoothness", 1f);
            var ao = Resources.Load<Texture2D>(Textures + set + "_AO");
            if (ao != null) { m.SetTexture("_OcclusionMap", ao); m.EnableKeyword("_OCCLUSIONMAP"); m.SetFloat("_OcclusionStrength", 0.65f); }
            materials[set] = m; return m;
        }

        /// <summary>The shared Portuguese-pavement material of the promenade, or null while its scanned maps are missing.</summary>
        public static Material PromenadeStoneMaterial() => MaterialFor("pedra_portuguesa");

        static void Spawn(GameObject prefab, Transform parent, string name, Vector3 position, float yaw, Material material)
        {
            var obj = Object.Instantiate(prefab, parent, false);
            obj.name = name; obj.transform.localPosition = position; obj.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            var renderers = obj.GetComponentsInChildren<MeshRenderer>();
            foreach (var r in renderers) { r.name = name; r.sharedMaterial = material; }
            var lod = obj.AddComponent<LODGroup>();
            lod.SetLODs(new[] { new LOD(0.015f, renderers) }); lod.RecalculateBounds();
        }

        public static bool DeckAssetsAvailable => Resources.Load<GameObject>("Art/Resort/Props/KioskShellF02") != null
            && Resources.Load<GameObject>("Art/Resort/Furniture/Table") != null
            && Resources.Load<GameObject>("Art/Resort/Furniture/Chair") != null
            && Resources.Load<GameObject>("Art/Resort/Props/UmbrellaCanopy") != null
            && MaterialFor("furniture_table") != null && MaterialFor("furniture_chair") != null;

        public static void DressDeck(GameObject shell, Vector3 origin)
        {
            var structure = shell.GetComponentsInChildren<MeshRenderer>();
            var stationRoot = Object.FindAnyObjectByType<ResortGame>().Layout.Root;
            foreach(var renderer in structure)
                if(renderer.GetComponent<MeshCollider>() != null)
                    renderer.gameObject.AddComponent<KioskSurfaceInteractions>().Init(stationRoot);
            var distant = Resources.Load<GameObject>("Art/Resort/Props/KioskShellF02_LOD1");
            if (distant != null)
            {
                var low = Object.Instantiate(distant, shell.transform, false); low.name = "Kiosk_ArchitectureLOD1";
                ResortMaterials.Apply(low);
                var lod = shell.AddComponent<LODGroup>(); lod.fadeMode = LODFadeMode.CrossFade;
                lod.SetLODs(new[] { new LOD(.08f, structure), new LOD(.012f, low.GetComponentsInChildren<MeshRenderer>()) });
                lod.RecalculateBounds();
            }
            DressPremiumInterior(shell, origin);
            var table = Resources.Load<GameObject>("Art/Resort/Furniture/Table");
            var chair = Resources.Load<GameObject>("Art/Resort/Furniture/Chair");
            var canopy = Resources.Load<GameObject>("Art/Resort/Props/UmbrellaCanopy");
            foreach (float side in new[] { -1f, 1f })
                for (int k = 0; k < 3; k++)
                {
                    if (side < 0f && k == 2) continue;
                    var center = origin + new Vector3(side * 7f, StallLayout.DeckLift, -(1f + 3f * k));
                    SpawnDeck(table, shell.transform, "F02_DeckTable", center, 0f, MaterialFor("furniture_table"), new Vector3(.692f, .726f, .692f));
                    foreach (float dx in new[] { -.9f, .9f })
                        SpawnDeck(chair, shell.transform, "F02_DeckChair", center + Vector3.right * dx, dx < 0f ? 90f : 270f,
                            MaterialFor("furniture_chair"), new Vector3(.45f, .45f, .45f));
                    SpawnDeck(canopy, shell.transform, "F02_DeckCanopy", center + Vector3.up * 2.55f, 0f,
                        CanopyMaterial(new Color(.87f, .78f, .51f)), Vector3.zero);
                    StallBuilder.Box("F02_UmbrellaPole", shell.transform, shell.transform.InverseTransformPoint(center + Vector3.up * 1.25f),
                        new Vector3(.04f, 2.5f, .04f), new Color(.3f, .32f, .33f), false);
                }
        }

        static void DressPremiumInterior(GameObject shell, Vector3 origin)
        {
            // Keep the same station/stock simulation. Dressing lives with the stage-two shell.
            Vector3 Local(Vector3 p) => shell.transform.InverseTransformPoint(origin + p);
            var register = Resources.Load<GameObject>("Art/Resort/Props/ModernKioskPOS");
            if(register != null)
            {
                var obj=Object.Instantiate(register,shell.transform,false);obj.name="Kiosk_ModernPOS";
                obj.transform.localPosition=Local(new Vector3(.9f,1.18f,1.1f));obj.transform.localRotation=Quaternion.identity;
                ResortMaterials.Apply(obj);
                var text=StallBuilder.Label(shell.transform,Local(new Vector3(.9f,1.415f,1.026f)),"LANCHES DO MAR",40,.0022f);
                text.name="Kiosk_POSDisplay";text.GetComponent<Billboard>().enabled=false;text.transform.rotation=Quaternion.identity;
                text.color=new Color(.65f,.92f,.97f);
                text.transform.SetParent(obj.transform,true);
                obj.AddComponent<KioskTerminalDisplay>().display=text;
                var collision=obj.AddComponent<BoxCollider>();collision.size=new Vector3(.45f,.36f,.36f);collision.center=Vector3.up*.18f;
                obj.AddComponent<CounterStation>();
                var terminalLOD=obj.AddComponent<LODGroup>();terminalLOD.SetLODs(new[]{new LOD(.01f,obj.GetComponentsInChildren<Renderer>())});terminalLOD.RecalculateBounds();
            }
            var bottle = Resources.Load<GameObject>("Art/Resort/Props/WineBottle");
            // Stage-one dressing already validates and caches this CC0 bottle material.
            if (bottle != null && materials.TryGetValue("shelf_bottle", out var bottleMaterial) && bottleMaterial != null)
                foreach (float y in new[] { 1.675f, 2.225f })
                    for (int i = 0; i < 12; i++)
                    {
                        Spawn(bottle, shell.transform, "Kiosk_ShelfBottle", Local(new Vector3(-3.55f + i * .46f, y, -5.2f)), 0f, bottleMaterial);
                        shell.transform.GetChild(shell.transform.childCount - 1).localScale = Vector3.one * .87f;
                    }
            var crate = Resources.Load<GameObject>("Art/Resort/Props/PlasticCrate"); var crateMaterial = PropMaterial("PlasticCrate0", true);
            if (crate != null && crateMaterial != null)
                for (int i = 0; i < 3; i++)
                    Spawn(crate, shell.transform, "Kiosk_StockCrate", Local(new Vector3(3.6f, .14f + i * .275f, -3.1f)), 0f, crateMaterial);
            var fern = Resources.Load<GameObject>("Art/Resort/Vegetation/ScannedUnderstory/fern_02/Model");
            var fernMaterial = Object.FindAnyObjectByType<ResortSite>().GetComponentsInChildren<MeshRenderer>(true)
                .SelectMany(r => r.sharedMaterials).FirstOrDefault(m => m != null && m.name == "PolyHavenCC0_fern_02");
            if (fern != null && fernMaterial != null)
                foreach (float x in new[] { -8.65f, 8.65f })
                {
                    Spawn(fern, shell.transform, "Kiosk_PlantedFern", Local(new Vector3(x, .62f, 2.5f)), 0f, fernMaterial);
                    shell.transform.GetChild(shell.transform.childCount - 1).localScale = Vector3.one * .43f;
                }
            BuildWashroomDoor(shell.transform, origin);
            var sign = StallBuilder.Label(shell.transform, Local(new Vector3(0f, 3.54f, 2.525f)), "LANCHES DO MAR", 60, .026f);
            sign.name = "Kiosk_FasciaSign"; sign.GetComponent<Billboard>().enabled = false;
            sign.transform.rotation = Quaternion.Euler(0f, 180f, 0f);
            var game = Object.FindAnyObjectByType<ResortGame>();
            if (game != null && game.DayNight != null)
                foreach (float x in new[] { -3f, 0f, 3f })
                    foreach (float z in new[] { 1f, -4.2f })
                    {
                        var at = new Vector3(x, 3.265f, z);
                        var emitter = game.DayNight.LampHead(shell.transform, Local(at), .15f);
                        emitter.name = "Kiosk_NightEmitter";
                        game.DayNight.AddLamp(origin + at, 8f, 2.4f);
                    }
        }

        static void BuildWashroomDoor(Transform shell, Vector3 origin)
        {
            var pivot = new GameObject("Kiosk_WashroomDoorPivot").transform;
            pivot.SetParent(shell, false); pivot.position = origin + new Vector3(-8.31f, .14f, -5.88f);
            pivot.rotation = Quaternion.Euler(0f, -95f, 0f);
            var door = StallBuilder.Box("Kiosk_WashroomDoor", pivot, new Vector3(.405f, 1.075f, 0f),
                new Vector3(.81f, 2.15f, .045f), new Color(.78f,.72f,.61f));
            door.GetComponent<MeshFilter>().sharedMesh = ResortSurfaceMaterials.MetreCube(door.transform.localScale);
            door.GetComponent<MeshRenderer>().sharedMaterial = ResortSurfaceMaterials.Create("madeira", new Color(.78f,.72f,.61f));
            foreach (float z in new[] { -.055f, .055f })
            {
                var handle = StallBuilder.Box("Kiosk_DoorHandle", pivot, new Vector3(.70f, 1f, z),
                    new Vector3(.11f, .025f, .025f), new Color(.22f,.25f,.25f), false);
                handle.GetComponent<MeshRenderer>().sharedMaterial = ResortSurfaceMaterials.Create("galvanizado", new Color(.22f,.25f,.25f));
            }
            bool open = true;
            var station = door.AddComponent<ActionStation>();
            station.prompt = g => open ? "[E] Fechar a porta do sanitário" : "[E] Abrir a porta do sanitário";
            station.action = g =>
            {
                // Keep the player's capsule clear when the door is closed.
                if (open && Physics.OverlapBox(origin + new Vector3(-7.905f, 1.215f, -5.88f),
                    new Vector3(.43f, 1.08f, .08f), Quaternion.identity, ~0, QueryTriggerInteraction.Ignore)
                    .Any(c => c.GetComponentInParent<PlayerController>() != null))
                { g.Say("Afaste-se da porta para fechá-la.", 3f); return; }
                open = !open; pivot.rotation = Quaternion.Euler(0f, open ? -95f : 0f, 0f);
            };
        }

        static void SpawnDeck(GameObject prefab, Transform parent, string name, Vector3 position, float yaw, Material material, Vector3 collision)
        {
            Spawn(prefab, parent, name, parent.InverseTransformPoint(position), yaw - parent.eulerAngles.y, material);
            var obj = parent.GetChild(parent.childCount - 1);
            if (collision == Vector3.zero) return;
            var box = obj.gameObject.AddComponent<BoxCollider>(); box.size = collision; box.center = Vector3.up * collision.y * .5f;
        }

        public static void Dress(Transform root)
        {
            foreach (var name in new[] { "SupplierCrate", "CrateSign", "OpenSign", "HelpBoard" })
            {
                var part = root.Find(name); if (part == null) continue;
                var material = ResortSurfaceMaterials.Create(name == "SupplierCrate" ? "madeira" : "galvanizado",
                    name == "SupplierCrate" ? new Color(.78f,.72f,.61f) : new Color(.22f,.25f,.25f));
                part.GetComponent<MeshRenderer>().sharedMaterial = material;
                part.GetComponent<MeshFilter>().sharedMesh = ResortSurfaceMaterials.MetreCube(part.localScale);
            }
            DressShelfBottles(root);
            DressCounterProps(root);
            var table = Resources.Load<GameObject>("Art/Resort/Furniture/Table");
            var chair = Resources.Load<GameObject>("Art/Resort/Furniture/Chair");
            var tableMat = MaterialFor("furniture_table"); var chairMat = MaterialFor("furniture_chair");
            // A complete set is required before hiding any fallback geometry.
            if (table != null && chair != null && tableMat != null && chairMat != null)
                foreach (var group in root.GetComponentsInChildren<Transform>(true))
                {
                    if (group.name != "S1_Table" && group.name != "S1_TableExtra") continue;
                    foreach (var renderer in group.GetComponentsInChildren<MeshRenderer>(true))
                        if (renderer.name == "S1_TableTop" || renderer.name == "S1_TableLeg" || renderer.name.StartsWith("S1_Chair"))
                            Object.Destroy(renderer); // retain the table's collision and all seat/upgrade data
                    Spawn(table, group, "S1_RealisticTable", Vector3.zero, 0f, tableMat);
                    Spawn(chair, group, "S1_RealisticChair", new Vector3(-0.78f, 0f, 0f), 90f, chairMat);
                    Spawn(chair, group, "S1_RealisticChair", new Vector3(0.78f, 0f, 0f), 270f, chairMat);
                    // Collider follows the smaller real tabletop, without changing customer anchors.
                    var collider = group.Find("S1_TableTop").GetComponent<BoxCollider>();
                    collider.size = new Vector3(0.692f / 0.95f, 1f, 0.692f / 0.95f);
                }
            var zinc = MaterialFor("galvanizado");
            if (zinc == null) return;
            Mesh roofMesh = null;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
                if (filter.name.StartsWith("Awning"))
                {
                    if (roofMesh == null)
                    {
                        roofMesh = Object.Instantiate(filter.sharedMesh); roofMesh.name = "RoofMetreUV";
                        var uv = roofMesh.uv;
                        // KioskDecor may already provide metre-scaled UVs. Scale
                        // only the original unit cube, avoiding a second stretch.
                        if (filter.sharedMesh.name != "SurfaceMetreUV")
                            for (int i = 0; i < uv.Length; i++) uv[i] = Vector2.Scale(uv[i], new Vector2(0.88f, 4.4f));
                        roofMesh.uv = uv; roofMesh.RecalculateTangents();
                    }
                    filter.sharedMesh = roofMesh; filter.GetComponent<MeshRenderer>().sharedMaterial = zinc;
                }
        }

        static void DressShelfBottles(Transform root)
        {
            var prefab = Resources.Load<GameObject>("Art/Resort/Props/WineBottle");
            var color = Resources.Load<Texture2D>("Art/Resort/Props/bottle_BaseColor");
            var gloss = Resources.Load<Texture2D>("Art/Resort/Props/bottle_MetallicGloss");
            if (prefab == null || color == null || gloss == null) return;
            if (!materials.TryGetValue("shelf_bottle", out var material) || material == null)
            {
                material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "CC0_ShelfBottlePBR", enableInstancing = true };
                material.SetTexture("_BaseMap", color); material.SetColor("_BaseColor", Color.white);
                material.SetTexture("_MetallicGlossMap", gloss); material.SetFloat("_Smoothness", 1f);
                material.EnableKeyword("_METALLICSPECGLOSSMAP");
                materials["shelf_bottle"] = material;
            }
            // Replace only shelf decoration, not fridge merchandise/stations.
            // Keep the original filters/renderers as disabled fallback geometry.
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.name != "S1_Bottle" || filter.transform.parent != root || filter.GetComponent<MeshRenderer>() == null) continue;
                var bottle = Object.Instantiate(prefab, root, false);
                bottle.name = "S1_CC0ShelfBottle";
                bottle.transform.localPosition = filter.transform.localPosition - Vector3.up * 0.13f;
                bottle.transform.localScale = Vector3.one * (0.26f / 0.2980393f);
                var renderers = bottle.GetComponentsInChildren<MeshRenderer>();
                foreach (var r in renderers) r.sharedMaterial = material;
                var lod = bottle.AddComponent<LODGroup>();
                lod.SetLODs(new[] { new LOD(0.009f, renderers) }); lod.RecalculateBounds();
                filter.name = "S1_BottleFallback";
                filter.GetComponent<MeshRenderer>().enabled = false;
            }
        }

        static Material PropMaterial(string set, bool clip = false)
        {
            if (materials.TryGetValue(set, out var cached) && cached != null) return cached;
            var color = Resources.Load<Texture2D>("Art/Resort/Props/" + set + "_BaseColor");
            var normal = Resources.Load<Texture2D>("Art/Resort/Props/" + set + "_Normal");
            var gloss = Resources.Load<Texture2D>("Art/Resort/Props/" + set + "_MetallicGloss");
            if (color == null || normal == null || gloss == null) return null;
            var material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "CC0_" + set, enableInstancing = true };
            material.SetTexture("_BaseMap", color); material.SetTexture("_BumpMap", normal);
            material.SetFloat("_BumpScale", .65f); material.EnableKeyword("_NORMALMAP");
            material.SetTexture("_MetallicGlossMap", gloss); material.SetFloat("_Smoothness", 1f); material.EnableKeyword("_METALLICSPECGLOSSMAP");
            if (clip)
            {
                material.SetFloat("_AlphaClip", 1f); material.SetFloat("_Cutoff", .5f);
                material.EnableKeyword("_ALPHATEST_ON"); material.renderQueue = 2450; material.SetOverrideTag("RenderType", "TransparentCutout");
            }
            materials[set] = material; return material;
        }

        static void DressCounterProps(Transform root)
        {
            var register = Resources.Load<GameObject>("Art/Resort/Props/CashRegister");
            var main = PropMaterial("CashRegister0"); var glass = PropMaterial("CashRegister1");
            if (register != null && main != null && glass != null)
            {
                var obj = Object.Instantiate(register, root, false); obj.name = "S1_CC0Register";
                obj.transform.localPosition = new Vector3(.9f, 1.15f, 1.1f); obj.transform.localScale = Vector3.one * .65f;
                var renderers = obj.GetComponentsInChildren<MeshRenderer>();
                foreach (var r in renderers)
                {
                    var slots = r.sharedMaterials;
                    for (int i = 0; i < slots.Length; i++) slots[i] = slots[i] != null && slots[i].name.Contains("glass") ? glass : main;
                    r.sharedMaterials = slots; r.name = "S1_CC0Register";
                }
                var lod = obj.AddComponent<LODGroup>(); lod.SetLODs(new[] { new LOD(.012f, renderers) }); lod.RecalculateBounds();
                foreach (var name in new[] { "S1_Register", "S1_RegisterScreen" })
                {
                    var original = root.Find(name); original.name += "Fallback"; original.GetComponent<MeshRenderer>().enabled = false;
                }
            }
            var crate = Resources.Load<GameObject>("Art/Resort/Props/PlasticCrate"); var plastic = PropMaterial("PlasticCrate0", true);
            if (crate == null || plastic == null) return;
            foreach (var original in root.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (original.name != "S1_Crate") continue;
                Spawn(crate, root, "S1_CC0Crate", original.transform.localPosition - Vector3.up * .135f, 0f, plastic);
                original.name = "S1_CrateFallback"; original.enabled = false;
            }
        }

        /// <summary>A single textured surface following the existing ground; the original terrain collider remains authoritative.</summary>
        public static void BuildPromenade(ResortSite site)
        {
            var material = MaterialFor("pedra_portuguesa");
            if (material == null) return;
            const int across = 5;
            int along = Mathf.CeilToInt(site.Data.size.x / 3f) + 1;
            var vertices = new Vector3[along * across]; var uv = new Vector2[vertices.Length];
            for (int i = 0; i < along; i++)
                for (int j = 0; j < across; j++)
                {
                    float x = Mathf.Min(i * 3f, site.Data.size.x), z = site.PromenadeZ(x) - 5.95f + j * (11.9f / (across - 1));
                    int k = i * across + j;
                    vertices[k] = new Vector3(x, site.HeightAt(x, z) + 0.015f, z);
                    uv[k] = new Vector2(x, z) / 2f; // authored tile is two metres
                }
            var triangles = new int[(along - 1) * (across - 1) * 6]; int t = 0;
            for (int i = 0; i < along - 1; i++)
                for (int j = 0; j < across - 1; j++)
                {
                    int a = i * across + j, b = a + across, c = a + 1, d = b + 1;
                    triangles[t++] = a; triangles[t++] = c; triangles[t++] = b;
                    triangles[t++] = b; triangles[t++] = c; triangles[t++] = d;
                }
            var mesh = new Mesh { name = "PromenadePBR", vertices = vertices, uv = uv, triangles = triangles };
            mesh.RecalculateNormals(); mesh.RecalculateTangents(); mesh.RecalculateBounds();
            var go = new GameObject("PromenadePBR"); go.transform.SetParent(site.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>(); r.sharedMaterial = material;
            r.shadowCastingMode = ShadowCastingMode.Off;
        }
    }
}
