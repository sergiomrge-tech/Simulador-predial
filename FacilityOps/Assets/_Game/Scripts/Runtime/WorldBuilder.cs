using System.Collections.Generic;
using UnityEngine;

namespace FacilityOps
{
    // Original procedural blockout; replace these meshes with authored assets later.
    public sealed class WorldBuilder
    {
        public GameObject Root { get; private set; }
        public readonly List<Light> WorkLights = new List<Light>();
        public readonly List<Renderer> LightFaces = new List<Renderer>();
        public readonly List<TechnicalStation> Stations = new List<TechnicalStation>();
        private Material concrete, dark, metal, amber, white, timber, blue, lit, unlit;
        private Material labelMaterial;
        private Material Material(string name, Color color, float smooth = .2f)
        {
            var material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = name };
            material.color = color;
            material.SetFloat("_Smoothness", smooth);
            return material;
        }
        public void Create(bool office)
        {
            if (Root != null) { Root.SetActive(false); Object.Destroy(Root); }
            WorkLights.Clear(); LightFaces.Clear(); Stations.Clear();
            Root = new GameObject(office ? "Hub · Garagem original" : "Local · Edifício Horizonte");
            if (concrete == null)
            {
            concrete = Material("Concreto quente", new Color(.52f, .56f, .56f));
            dark = Material("Grafite", new Color(.055f, .085f, .10f));
            metal = Material("Aço pintado", new Color(.26f, .34f, .38f), .65f);
            amber = Material("Amarelo de sinalização", new Color(.95f, .57f, .15f));
            white = Material("Gesso", new Color(.78f, .81f, .78f));
            timber = Material("Bancada", new Color(.34f, .23f, .15f));
            blue = Material("Azul industrial", new Color(.12f, .31f, .39f));
            lit = Material("Difusor ligado", new Color(.9f, 1, .93f));
            lit.EnableKeyword("_EMISSION"); lit.SetColor("_EmissionColor", new Color(.8f, 1, .9f) * 2);
            unlit = Material("Difusor desligado", new Color(.22f, .25f, .23f));
            var paint = Resources.Load<Texture2D>("Art/AuroraPaint_Albedo");
            if (paint != null) { metal.SetTexture("_BaseMap", paint); metal.color = Color.white; }
            }
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(.39f, .43f, .48f);
            RenderSettings.fog = false;
            var sun = new GameObject("Luz ambiente direcional"); sun.transform.SetParent(Root.transform);
            sun.transform.rotation = Quaternion.Euler(48, -25, 0);
            var sunlight = sun.AddComponent<Light>(); sunlight.type = LightType.Directional; sunlight.intensity = .7f;
            sunlight.shadows = LightShadows.Soft;
            Shell(office ? 8 : 7, office ? 10 : 14);
            if (!office) InstallCorridorArt();
            if (office) Office(); else ServiceRoom();
        }
        private GameObject Box(string name, Vector3 position, Vector3 scale, Material material)
        {
            var box = GameObject.CreatePrimitive(PrimitiveType.Cube);
            box.name = name; box.transform.SetParent(Root.transform);
            box.transform.position = position; box.transform.localScale = scale;
            box.GetComponent<Renderer>().sharedMaterial = material;
            return box;
        }
        private void Shell(float width, float length)
        {
            Box("Piso", new Vector3(0, -.15f, length / 2), new Vector3(width, .3f, length), concrete);
            Box("Parede esquerda", new Vector3(-width / 2, 1.6f, length / 2), new Vector3(.2f, 3.2f, length), white);
            Box("Parede direita", new Vector3(width / 2, 1.6f, length / 2), new Vector3(.2f, 3.2f, length), white);
            Box("Parede de fundo", new Vector3(0, 1.6f, length), new Vector3(width, 3.2f, .2f), white);
            Box("Parede de entrada", new Vector3(0, 1.6f, 0), new Vector3(width, 3.2f, .2f), white);
            Box("Teto", new Vector3(0, 3.3f, length / 2), new Vector3(width, .2f, length), concrete);
            for (int side = -1; side <= 1; side += 2)
            {
                Box("Rodapé", new Vector3(side * (width / 2 - .13f), .14f, length / 2), new Vector3(.08f, .28f, length), dark);
                Box("Faixa técnica", new Vector3(side * (width / 2 - .13f), 1.12f, length / 2), new Vector3(.035f, .09f, length), blue);
            }
            for (int z = 1; z < length; z++)
                Box("Junta piso", new Vector3(0, .003f, z), new Vector3(width, .006f, .012f), metal);
        }
        public void CreatePreview(LocationData location, int floorIndex)
        {
            Create(true);
            foreach (Transform child in Root.transform) { child.gameObject.SetActive(false); Object.Destroy(child.gameObject); }
            Root.name = "Prévia de campanha / " + location.id;
            var directional = new GameObject("Luz de estudo"); directional.transform.SetParent(Root.transform); directional.transform.rotation = Quaternion.Euler(55,-35,0);
            var light = directional.AddComponent<Light>(); light.type = LightType.Directional; light.intensity = .9f;
            FloorData floor = location.floors[floorIndex];
            var borders = new HashSet<string>();
            foreach (var room in floor.rooms)
            {
                Box(room.id + " / piso", new Vector3(room.x,-.15f,room.z), new Vector3(room.width,.3f,room.depth), concrete);
                Box(room.id + " / teto", new Vector3(room.x,3.35f,room.z), new Vector3(room.width,.15f,room.depth), white);
                Vector3[] directions = { Vector3.left,Vector3.right,Vector3.back,Vector3.forward };
                foreach (var direction in directions)
                {
                    Vector3 center = new Vector3(room.x,1.65f,room.z) + direction * 4;
                    string key = center.x + ":" + center.z;
                    if (!borders.Add(key)) continue;
                    RoomData neighbor = System.Array.Find(floor.rooms, r => Mathf.Abs(r.x-(room.x+direction.x*8))<.01f && Mathf.Abs(r.z-(room.z+direction.z*8))<.01f);
                    bool door = neighbor != null && System.Array.Exists(floor.connections, c => c.from == room.id && c.to == neighbor.id || c.to == room.id && c.from == neighbor.id);
                    Vector3 along = new Vector3(direction.z,0,direction.x);
                    if (door)
                    {
                        for (int side = -1; side <= 1; side += 2)
                            Box("Parede / passagem", center + along * side * 2.5f, direction.x != 0 ? new Vector3(.16f,3.3f,3) : new Vector3(3,3.3f,.16f), white);
                        Box("Verga / passagem", center + Vector3.up*1.3f, direction.x != 0 ? new Vector3(.16f,.7f,2) : new Vector3(2,.7f,.16f), blue);
                    }
                    else Box("Parede / perímetro",center,direction.x != 0 ? new Vector3(.16f,3.3f,8) : new Vector3(8,3.3f,.16f),white);
                }
                var plinth = Box("Registro / " + room.name, new Vector3(room.x+2.3f,.65f,room.z+2.8f), new Vector3(1.4f,1.3f,.65f),blue);
                var hotspot = plinth.AddComponent<LoreHotspot>(); hotspot.caption = room.name; hotspot.note = room.hotspot;
                Label(room.name + "\n" + location.name, new Vector3(room.x,2.96f,room.z+3.8f),0,.045f,new Color(.08f,.17f,.2f));
                Label("REGISTRO\n" + room.name, new Vector3(room.x+2.3f,1.4f,room.z+2.44f),0,.025f,new Color(.1f,.2f,.24f));
                CeilingLight(room.x,room.z,false);
            }
        }
        private void InstallCorridorArt()
        {
            var source = Resources.Load<GameObject>("Art/AuroraCorridor");
            if (source == null) return;
            foreach (Transform child in Root.transform)
                if (child.name == "Piso" || child.name.StartsWith("Parede") || child.name == "Teto" || child.name == "Rodapé" || child.name == "Faixa técnica" || child.name == "Junta piso")
                    child.GetComponent<Renderer>().enabled = false;
            var art = Object.Instantiate(source, Root.transform); art.name = "Blender / Aurora Corridor";
            Bounds bounds = new Bounds(); bool first = true;
            foreach (var renderer in art.GetComponentsInChildren<Renderer>())
            {
                if (first) { bounds = renderer.bounds; first = false; } else bounds.Encapsulate(renderer.bounds);
                var imported = renderer.sharedMaterials;
                for (int i = 0; i < imported.Length; i++)
                {
                    string name = imported[i] != null ? imported[i].name : "";
                    imported[i] = name.Contains("Plaster") ? white : name.Contains("FloorA") ? concrete : name.Contains("FloorB") ? concrete : name.Contains("Blue") ? blue : name.Contains("Metal") ? metal : dark;
                }
                renderer.sharedMaterials = imported;
            }
            if (bounds.center.z < 0) art.transform.rotation = Quaternion.Euler(0,180,0);
        }
        private void Label(string text, Vector3 position, float yaw, float size = .12f, Color? color = null)
        {
            var label = new GameObject("Placa · " + text); label.transform.SetParent(Root.transform);
            label.transform.SetPositionAndRotation(position, Quaternion.Euler(0, yaw, 0));
            var mesh = label.AddComponent<TextMesh>(); mesh.text = text; mesh.fontSize = 64;
            mesh.characterSize = size * .45f; mesh.anchor = TextAnchor.MiddleCenter; mesh.alignment = TextAlignment.Center;
            mesh.color = color ?? new Color(.85f, .91f, .9f);
            var renderer = label.GetComponent<Renderer>();
            if (labelMaterial == null)
            {
                labelMaterial = new Material(Resources.Load<Shader>("WorldLabel"));
                labelMaterial.mainTexture = renderer.sharedMaterial.mainTexture;
            }
            renderer.sharedMaterial = labelMaterial;
        }
        private void CeilingLight(float x, float z, bool affected)
        {
            Box("Armadura luminária", new Vector3(x, 3.07f, z), new Vector3(1.6f, .16f, .44f), dark);
            var face = Box("Difusor", new Vector3(x, 2.97f, z), new Vector3(1.45f, .06f, .35f), lit);
            var lightObject = new GameObject("Iluminação de área"); lightObject.transform.SetParent(Root.transform);
            lightObject.transform.position = new Vector3(x, 2.78f, z);
            var lamp = lightObject.AddComponent<Light>(); lamp.type = LightType.Point; lamp.range = 7;
            lamp.intensity = 1.8f; lamp.color = new Color(.88f, .96f, 1);
            if (affected) { WorkLights.Add(lamp); LightFaces.Add(face.GetComponent<Renderer>()); }
        }
        public void Reflect(bool working)
        {
            foreach (var light in WorkLights) light.enabled = working;
            foreach (var face in LightFaces) face.sharedMaterial = working ? lit : unlit;
        }
        private void Office()
        {
            CeilingLight(0, 3, false); CeilingLight(0, 7, false);
            Box("Mesa", new Vector3(0, .79f, 7.4f), new Vector3(3, .14f, 1.2f), timber);
            for (int x = -1; x <= 1; x += 2) Box("Pé da mesa", new Vector3(x * 1.25f, .38f, 7.4f), new Vector3(.1f, .76f, .9f), dark);
            Box("Monitor", new Vector3(0, 1.3f, 7.7f), new Vector3(1.25f, .75f, .1f), dark).AddComponent<OfficeTerminal>();
            Box("Tela", new Vector3(0, 1.31f, 7.63f), new Vector3(1.12f, .62f, .015f), blue);
            Label("FACILITY OPS\nCENTRAL DE CHAMADOS", new Vector3(0, 1.32f, 7.61f), 0, .05f);
            Box("Teclado", new Vector3(0, .9f, 7), new Vector3(.75f, .04f, .23f), dark);
            Box("Mural", new Vector3(0, 2.25f, 9.85f), new Vector3(3.4f, 1.1f, .05f), dark);
            Label("OFICINA AURORA\nMANUTENÇÃO & FACILITIES", new Vector3(0, 2.25f, 9.8f), 0, .12f);
            for (int shelf = 0; shelf < 3; shelf++)
            {
                Box("Estoque prateleira", new Vector3(-2.8f, .5f + shelf * .6f, 5.5f), new Vector3(1, .07f, 2.5f), metal);
                for (int item = 0; item < 3; item++) Box("Caixa de peças", new Vector3(-2.8f, .72f + shelf * .6f, 4.7f + item * .75f), new Vector3(.7f, .35f, .55f), shelf == 1 ? amber : timber);
            }
            Label("PEÇAS / ESTOQUE", new Vector3(-2.23f, 2.4f, 5.5f), 90, .09f);
            Box("Mala de ferramentas", new Vector3(1.1f, 1, 7.3f), new Vector3(.6f, .35f, .4f), amber);
            Box("Bancada de trabalho", new Vector3(2.8f, .7f, 4.7f), new Vector3(1, 1.4f, 2.5f), blue);
            Box("Tampo", new Vector3(2.8f, 1.43f, 4.7f), new Vector3(1.12f, .09f, 2.6f), timber);
            Box("Tapete", new Vector3(0, .014f, 1.8f), new Vector3(2.5f, .02f, 1.7f), dark);
        }
        private void ServiceRoom()
        {
            CeilingLight(0, 2, false); CeilingLight(0, 6, true); CeilingLight(0, 10, true);
            Box("Portal sala técnica esquerda", new Vector3(-2.65f, 1.55f, 4), new Vector3(1.5f, 3.1f, .18f), blue);
            Box("Portal sala técnica direita", new Vector3(2.65f, 1.55f, 4), new Vector3(1.5f, 3.1f, .18f), blue);
            Box("Portal superior", new Vector3(0, 2.95f, 4), new Vector3(3.8f, .3f, .18f), blue);
            Label("ACESSO TÉCNICO  /  CORREDOR 04", new Vector3(0, 2.94f, 3.87f), 0, .065f);
            Station(StationId.Distribution, "QD-01 / DISTRIBUIÇÃO", new Vector3(-3.19f, 1.6f, 6), new Vector3(.45f, 1.35f, 1.15f), -90);
            Station(StationId.Controller, "CT-01 / COMANDO", new Vector3(3.19f, 1.55f, 9), new Vector3(.45f, .85f, .9f), 90);
            Station(StationId.Luminaire, "LM-01 / DRIVER", new Vector3(0, 1.55f, 13.73f), new Vector3(1.1f, .8f, .35f), 0);
            for (int z = 5; z < 14; z++)
            {
                Box("Conduíte", new Vector3(-3.28f, 2.58f, z), new Vector3(.07f, .07f, 1), metal);
                Box("Abraçadeira", new Vector3(-3.25f, 2.58f, z), new Vector3(.12f, .16f, .08f), dark);
            }
            Box("Caixote", new Vector3(2.8f, .3f, 5.1f), new Vector3(.7f, .6f, .7f), timber);
            Box("Caixote menor", new Vector3(2.8f, .85f, 5.1f), new Vector3(.55f, .5f, .6f), timber);
            for (int z = 6; z < 13; z += 3)
            {
                Box("Porta escritório", new Vector3(3.36f, 1.15f, z), new Vector3(.05f, 2.3f, 1.1f), timber);
                Box("Maçaneta", new Vector3(3.28f, 1.03f, z - .3f), new Vector3(.1f, .06f, .15f), metal);
            }
            Label("EDIFÍCIO HORIZONTE\nCORREDOR RESIDENCIAL", new Vector3(0, 2.45f, 13.84f), 0, .10f, new Color(.12f, .23f, .26f));
        }
        private void Station(StationId id, string title, Vector3 position, Vector3 size, float yaw)
        {
            var body = Box(title, position, size, metal);
            var station = body.AddComponent<TechnicalStation>(); station.id = id; station.label = title; Stations.Add(station);
            string assetId = id == StationId.Distribution ? "QD01" : id == StationId.Controller ? "CT01" : "LM01";
            var source = Resources.Load<GameObject>("Art/" + assetId);
            if (source != null)
            {
                body.GetComponent<Renderer>().enabled = false;
                var art = Object.Instantiate(source, Root.transform);
                art.name = "Blender / " + assetId;
                art.transform.SetPositionAndRotation(position, Quaternion.Euler(0, yaw + 180, 0) * source.transform.localRotation);
                foreach (Renderer renderer in art.GetComponentsInChildren<Renderer>())
                {
                    Material[] materials = renderer.sharedMaterials;
                    for (int index = 0; index < materials.Length; index++)
                    {
                        string name = materials[index] != null ? materials[index].name : "";
                        materials[index] = name.Contains("Graphite") ? dark : name.Contains("Amber") ? amber : name.Contains("Ivory") ? white : name.Contains("Blue") ? blue : metal;
                    }
                    renderer.sharedMaterials = materials;
                }
                return;
            }
            Vector3 front = Quaternion.Euler(0, yaw, 0) * Vector3.back;
            float offset = yaw == 0 ? size.z / 2 : size.x / 2;
            Vector3 panel = position + front * (offset + .016f);
            var plate = Box("Placa de identificação", panel + Vector3.up * .16f, new Vector3(.7f, .25f, .025f), dark);
            plate.transform.rotation = Quaternion.Euler(0, yaw, 0);
            Label(title.Replace(" / ", "\n"), panel + front * .025f + Vector3.up * .16f, yaw, .052f);
            for (int i = -1; i <= 1; i++)
            {
                Vector3 side = Quaternion.Euler(0, yaw, 0) * Vector3.right;
                var indicator = Box("Indicador virtual", panel - Vector3.up * .17f + side * i * .18f, new Vector3(.07f, .09f, .035f), i == 0 ? amber : dark);
                indicator.transform.rotation = Quaternion.Euler(0, yaw, 0);
            }
        }
    }
}
