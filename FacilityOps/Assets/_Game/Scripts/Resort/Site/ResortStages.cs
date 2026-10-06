using System;
using System.Collections.Generic;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Site
{
    /// <summary>
    /// Shows the physical stage of the resort (1 stall ... 7 Grand Aurora) from the exported FBX pieces (Tools/Blender/export_resort_kit.py).
    /// Every piece keeps its site-local coordinates, so it is instantiated at the origin and lines up with the terrain.
    /// The stage follows land ownership (<see cref="StageFor"/>); the graded platô terrain switches on at stage 6.
    /// </summary>
    public sealed class ResortStages : MonoBehaviour
    {
        [Serializable] sealed class Piece { public string asset, name; public int from, to, polygons; }
        [Serializable] sealed class Manifest { public Piece[] pieces; }

        readonly List<(GameObject go, int from, int to, string name)> instances = new List<(GameObject, int, int, string)>();
        ResortSite site;

        public int Stage { get; private set; }
        public int PieceCount => instances.Count;
        public IEnumerable<GameObject> Instances { get { foreach (var i in instances) yield return i.go; } }

        public void Init(ResortSite s)
        {
            site = s;
            // Blender's FBX axis conversion lands pieces rotated 180 degrees about the up axis (x -> -x, z -> -z); the root undoes that so
            // every piece keeps its site-local position (east = +x, north = +z) with the correct handedness.
            transform.localPosition = Vector3.zero;
            transform.localRotation = Quaternion.Euler(0f, 180f, 0f);
            var mf = Resources.Load<TextAsset>("Art/Resort/resort_stages");
            if (mf == null) { Debug.LogWarning("ResortStages: manifest not found (run Tools/Blender/export_resort_kit.py)."); return; }
            foreach (var p in JsonUtility.FromJson<Manifest>(mf.text).pieces)
            {
                var prefab = Resources.Load<GameObject>("Art/Resort/" + p.asset);
                if (prefab == null) { Debug.LogWarning("ResortStages: missing asset " + p.asset); continue; }
                var go = Instantiate(prefab, transform);
                go.name = p.asset;
                go.transform.localPosition = Vector3.zero;
                go.transform.localRotation = Quaternion.identity;
                ResortMaterials.Apply(go);
                if (SolidName(p.name)) foreach (var mf2 in go.GetComponentsInChildren<MeshFilter>()) mf2.gameObject.AddComponent<MeshCollider>();
                go.SetActive(false);
                instances.Add((go, p.from, p.to, p.name));
            }
        }

        /// <summary>Buildings and terraces block the player; vegetation, water, the crane and other thin things do not.</summary>
        static bool SolidName(string n)
        {
            n = n.ToLowerInvariant();
            return !(n.Contains("palmeira") || n.Contains("arbusto") || n.Contains("bugan") || n.Contains("arvore") || n.Contains("agua") || n.Contains("grua"));
        }

        public void SetStage(int stage)
        {
            Stage = stage;
            foreach (var i in instances) i.go.SetActive(i.from <= stage && stage <= i.to);
            if (site != null) site.SetGraded(stage >= 6);
        }

        /// <summary>Stage from owned land: P1 kiosk strip (2), P2 pousada (3), P3 hotel (4), P4 Grande Hotel (5), P5 platô (6), P6 headland (7).</summary>
        public static int StageFor(ParcelBook parcels)
        {
            if (parcels == null) return 1;
            int stage = 1;
            if (parcels.Owns("P1")) stage = 2;
            if (stage >= 2 && parcels.Owns("P2")) stage = 3;
            if (stage >= 3 && parcels.Owns("P3")) stage = 4;
            if (stage >= 4 && parcels.Owns("P4")) stage = 5;
            if (stage >= 5 && parcels.Owns("P5")) stage = 6;
            if (stage >= 6 && parcels.Owns("P6")) stage = 7;
            return stage;
        }
    }
}
