"""Static GitHub-only gate for the cross-repository R12 Unity asset bridge.
Does NOT claim to run native Unity or reproduce the 121MB imported FBX bundle.
"""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/"Docs/PROJECT_RESORT_EXECUTION"
def validate():
    m=json.loads((DOC/"R12_GAME_BRIDGE_DEPENDENCIES.json").read_text(encoding="utf-8-sig"))
    q=json.loads((DOC/"R12_GAME_BRIDGE_UNITY_QA.json").read_text(encoding="utf-8-sig"))
    assert m["status"]=="R12_GAME_BRIDGE_GUID_AND_HASH_AUDITED"
    assert m["asset_count"]==len(m["assets"])==622
    assert m["asset_bytes"]==121093212
    assert m["game_guid_collisions"]==0
    assert m["unknown_external_or_unity_builtin_guids"]==9
    assert m["original_scene"]=="Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity"
    paths=set();guids=set();total=0
    for item in m["assets"]:
        name=item["path"]
        path=Path(name)
        assert not path.is_absolute() and ".." not in path.parts,name
        assert name not in paths,name
        assert item["guid"] not in guids,item["guid"]
        for field in ("sha256","meta_sha256"):
            assert re.fullmatch("[a-f0-9]{64}",item[field]),(name,field)
        assert re.fullmatch("[a-f0-9]{32}",item["guid"]),name
        assert item["bytes"]>=0
        total+=item["bytes"]
        paths.add(name);guids.add(item["guid"])
    assert total==m["asset_bytes"]
    assert q["status"]=="R12_GAME_PROJECT_ASSET_COMPATIBILITY_PASS_GAMEPLAY_ALIGNMENT_PENDING"
    assert q["unityVersion"]=="6000.6.2f1"
    assert q["runtimeRenderer"]=="Direct3D11"
    assert q["buildingsCount"]==1468
    assert q["roadTriangles"]==3731
    assert q["trees"]==48
    assert (q["r8Renderers"],q["r11DetailRenderers"],q["r12StorefrontRenderers"],q["r10CoastalRenderers"])==(350,210,19,9)
    assert q["missingUV0"]==q["missingShaders"]==q["missingMaterials"]==q["missingMonoScripts"]==0
    assert q["r9TreesMissingUV0"]==48
    assert (q["originalDataWidth"],q["originalDataDepth"])==(900,720)
    assert not q["gameplayMapSameAsR12"] and not q["gameplayIntegrationApproved"]
    assert re.fullmatch("[a-f0-9]{64}",q["gameplaySceneSha256"])
    assert q["originalGameplaySceneLeftUnchanged"]
    print("R12_GAME_BRIDGE_CONTRACT_PASS",{"visual_assets":len(paths),
       "bytes":total,"uvless_trees":48,"scene":q["importedScene"],
       "playable_geo_aligned":False},flush=True)
if __name__=="__main__":validate()
