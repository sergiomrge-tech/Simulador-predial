// Editor-only inspection overlay. NEVER a gameplay position migration.
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using ResortAurora.Site;

namespace ResortAurora.EditorTools
{
    public static class ResortR12GeoCandidatePreview
    {
        const string Source = "Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity";
        const string Output = "Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_GeometricCandidates_Review.unity";
        const string Name = "R12_GEO_CANDIDATES_EDITOR_ONLY";
        const string ReportRelative = "Docs/PROJECT_RESORT_EXECUTION/R12_GEO_CANDIDATE_PREVIEW_NATIVE_QA.json";
        [Serializable] public class XZ { public float x, z; }
        [Serializable] public class Candidate
        {
            public string id, status;
            public bool planar_only;
            public XZ center_world_xz;
            public XZ[] outline_world_xz;
        }
        [Serializable] public class Plan
        {
            public int schemaVersion;
            public string status;
            public bool scene_alignment_verified_natively;
            public bool gameplay_spawn_enabled;
            public bool playmode_navmesh_pass;
            public Candidate[] candidates;
        }
        [Serializable] public class Report
        {
            public string status, unity_version, source_scene_sha256, preview_scene, source_scene;
            public int candidates, outline_segments, visible_labels;
            public bool source_scene_bytes_preserved, game_scene_unmodified,
                        world_y_verified, playable_migration_enabled,
                        native_navmesh_tested, colliders_validated;
        }
        static void Need(bool condition, string reason)
        {
            if (!condition) throw new InvalidOperationException("R12_GEO_REVIEW_BLOCKED:" + reason);
        }
        static string GameRoot() =>
            Path.GetFullPath(Path.Combine(Application.dataPath, "../.."));
        static string PlanPath() =>
            Path.Combine(GameRoot(), "Docs/PROJECT_RESORT_EXECUTION/R12_GEO_UNITY_REVIEW_MARKERS.json");
        static Vector3 Point(XZ v, float editorHeight) => new Vector3(v.x, editorHeight, v.z);
        static void Label(GameObject root, Candidate c)
        {
            var go = new GameObject("CANDIDATE_LABEL_" + c.id);
            go.tag = "EditorOnly";
            go.transform.SetParent(root.transform);
            go.transform.position = Point(c.center_world_xz, 1.4f);
            var text = go.AddComponent<TextMesh>();
            text.text = c.id + " - UNVERIFIED";
            text.fontSize = 18;
            text.characterSize = .5f;
            text.anchor = TextAnchor.MiddleCenter;
            text.color = new Color(1f, .64f, .12f, 1f);
        }
        static void Segment(GameObject root, Candidate candidate, int index, Material mat)
        {
            var a = Point(candidate.outline_world_xz[index], .64f);
            var b = Point(candidate.outline_world_xz[(index + 1) % 4], .64f);
            Vector3 delta = b - a;
            Need(delta.magnitude > 1f && delta.magnitude < 260f, "INVALID_POLYGON_EDGE");
            var line = GameObject.CreatePrimitive(PrimitiveType.Cube);
            line.name = candidate.id + "_OUTLINE_" + index.ToString("D2");
            line.tag = "EditorOnly";
            line.transform.SetParent(root.transform, true);
            line.transform.position = (a + b) * .5f;
            line.transform.rotation = Quaternion.FromToRotation(Vector3.right, delta.normalized);
            line.transform.localScale = new Vector3(delta.magnitude, .14f, .35f);
            var col = line.GetComponent<BoxCollider>();
            if (col != null) UnityEngine.Object.DestroyImmediate(col);
            line.GetComponent<MeshRenderer>().sharedMaterial = mat;
        }
        [MenuItem("Resort/R12 Bridge/Generate Editor-only GIS candidate review")]
        public static void Build()
        {
            Need(File.Exists(PlanPath()), "CANDIDATE_XZ_FILE_MISSING");
            Need(File.Exists(Source), "SOURCE_R12_SCENE_MISSING");
            var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(PlanPath()));
            Need(plan != null && plan.schemaVersion == 1 &&
                 !plan.gameplay_spawn_enabled && !plan.scene_alignment_verified_natively &&
                 !plan.playmode_navmesh_pass && plan.candidates != null &&
                 plan.candidates.Length == 7,"UNVERIFIED_CANDIDATES_MUST_REMAIN_EDITOR_ONLY");
            Need(plan.candidates.All(x => x != null && x.planar_only &&
                 x.outline_world_xz != null && x.outline_world_xz.Length == 4 &&
                 x.center_world_xz != null),"INVALID_CANDIDATE_POLYGONS");
            Need(plan.candidates.Select(x=>x.id).Distinct().Count()==7 &&
                 plan.candidates.All(x=>x.id!="P5"),"DO_NOT_SHOW_UNPLACED_P5");

            string before=R12GameplayWorldGate.Sha256(File.ReadAllBytes(Source));
            var scene=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);
            var overlay = new GameObject(Name);
            overlay.tag = "EditorOnly";
            var shader = Shader.Find("Universal Render Pipeline/Unlit");
            Need(shader != null && shader.isSupported,"URP_SHADER_MISSING");
            var mat=new Material(shader) { name="R12_EditorOnly_Unapproved_GIS_Candidates" };
            mat.SetColor("_BaseColor",new Color(.95f,.56f,.07f));
            mat.enableInstancing=true;
            int count=0;
            foreach (var c in plan.candidates)
            {
                Label(overlay,c);
                for(int i=0;i<4;i++){ Segment(overlay,c,i,mat);count++; }
            }
            Need(count==28,"INCOMPLETE_POLYGON_RENDER");
            Need(overlay.GetComponentsInChildren<Collider>().Length==0,
                 "EDITOR_CANDIDATES_MUST_NOT_ADD_PHYSICS");

            var camera=Camera.main;
            if(camera != null)
            {
                Vector3 center=Vector3.zero;
                foreach(var c in plan.candidates) center+=Point(c.center_world_xz,0f);
                center/=plan.candidates.Length;
                camera.transform.position=center+new Vector3(0,350f,-250f);
                camera.transform.LookAt(center);
            }
            Need(EditorSceneManager.SaveScene(scene,Output,true),"EDITOR_REVIEW_COPY_SAVE_FAILED");
            Need(before == R12GameplayWorldGate.Sha256(File.ReadAllBytes(Source)),
                 "SOURCE_SCENE_MUTATED");
            var report=new Report{
                status="R12_EDITOR_GIS_CANDIDATES_NATIVE_PASS_NOT_GAMEPLAY",
                unity_version=Application.unityVersion,
                source_scene_sha256=before,source_scene=Source,
                preview_scene=Output,candidates=7,
                outline_segments=count,visible_labels=7,
                source_scene_bytes_preserved=true,game_scene_unmodified=true,
                world_y_verified=false,playable_migration_enabled=false,
                native_navmesh_tested=false,colliders_validated=false
            };
            string qa=Path.Combine(GameRoot(),ReportRelative);
            Directory.CreateDirectory(Path.GetDirectoryName(qa));
            File.WriteAllText(qa,JsonUtility.ToJson(report,true)+"\n");
            Debug.Log("R12_GEO_CANDIDATES_UNITY_NATIVE_PASS outlines=28 labels=7 migration=BLOCKED");
        }
    }
}
