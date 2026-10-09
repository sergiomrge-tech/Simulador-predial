#!/usr/bin/env python3
"""Non-destructive GUID-preserving bridge from visual R12 into a GAME QA checkout.
Staged assets are excluded from Git; never overwrite source game assets or saves.
"""
import argparse, collections, hashlib, json, re, shutil
from pathlib import Path
GUID=re.compile(r"\bguid:\s*([0-9a-f]{32})\b",re.I)
def asset_guid(meta):
    if not meta.is_file():return None
    data=meta.read_text(encoding="utf-8-sig",errors="ignore")
    match=GUID.search(data)
    return match.group(1).lower() if match else None
def index_metas(root):
    index,duplicates={},{}
    for meta in sorted(root.rglob("*.meta")):
        if any(s in meta.parts for s in ("Library","Temp","obj","Logs",".git")):continue
        # Previously staged preview files are intentionally excluded from GAME
        # GUID index, so subsequent reproducible reruns are idempotent.
        if "CopacabanaR12" in meta.parts and "Preview" in meta.parts:continue
        guid=asset_guid(meta)
        if not guid:continue
        asset=Path(str(meta)[:-5])
        if guid in index:duplicates.setdefault(guid,[str(index[guid])]).append(str(asset))
        else:index[guid]=asset
    return index,duplicates
def refs(asset):
    values=set()
    for p in (asset,Path(str(asset)+".meta")):
        if not p.is_file() or p.stat().st_size>10000000:continue
        try:raw=p.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError,OSError):continue
        values|={x.lower() for x in GUID.findall(raw)}
    return values
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def run(source,game,dry_run):
    src=source/"Assets"
    dest=game/"FacilityOps/Assets/_Game/Preview/CopacabanaR12"
    game_assets=game/"FacilityOps/Assets"
    root=src/"Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity"
    if not root.is_file():raise RuntimeError("R12_SOURCE_SCENE_NOT_FOUND")
    sources,duplicates=index_metas(src)
    games,game_duplicates=index_metas(game_assets)
    if duplicates or game_duplicates:raise RuntimeError(f"GUID_DUPLICATES: {len(duplicates)}/{len(game_duplicates)}")
    pending=collections.deque([root]);seen={};external=collections.Counter()
    while pending:
        file=pending.popleft()
        if file in seen:continue
        if not file.is_file():raise RuntimeError("MISSING_R12_ASSET "+str(file))
        guid=asset_guid(Path(str(file)+".meta"))
        if not guid:raise RuntimeError("META_MISSING "+str(file))
        rel=file.relative_to(src).as_posix()
        seen[file]={"path":rel,"guid":guid,"bytes":file.stat().st_size,
                    "sha256":digest(file),"meta_sha256":digest(Path(str(file)+".meta"))}
        for guidref in refs(file):
            if guidref==guid or guidref=="00000000000000000000000000000000":continue
            if guidref in sources:
                if sources[guidref] not in seen:pending.append(sources[guidref])
            elif guidref in games: # game already includes that dependency
                pass
            else:external[guidref]+=1
    coll=set(games)&{d["guid"] for d in seen.values()}
    if coll:raise RuntimeError("GAME_GUID_CONFLICT "+repr(sorted(coll)[:5]))
    m={"status":"R12_GAME_BRIDGE_GUID_AND_HASH_AUDITED",
       "original_scene":"Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity",
       "staged_scene":"Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity",
       "visual_ref":"Resort-Simulator- codex/r12-urban-storefronts afa4dfa",
       "game_ref":"Simulador-predial claude/w1-masterplan bc11f2b",
       "asset_count":len(seen),"asset_bytes":sum(d["bytes"] for d in seen.values()),
       "game_guid_collisions":0,"unknown_external_or_unity_builtin_guids":len(external),
       "assets":sorted(seen.values(),key=lambda x:x["path"])}
    if not dry_run:
        for asset,desc in seen.items():
            target=dest/desc["path"]
            target.parent.mkdir(parents=True,exist_ok=True)
            for a,b,sha in ((asset,target,desc["sha256"]),(Path(str(asset)+".meta"),Path(str(target)+".meta"),desc["meta_sha256"])):
                if b.exists():
                    if digest(b)!=sha:raise RuntimeError("WOULD_OVERWRITE_MODIFIED "+str(b))
                else:shutil.copy2(a,b)
        report=game/"Docs/PROJECT_RESORT_EXECUTION/R12_GAME_BRIDGE_DEPENDENCIES.json"
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("R12_GUID_BRIDGE_"+("DRY_RUN" if dry_run else "STAGED"),json.dumps({k:v for k,v in m.items() if k!="assets"}))
    print("R12_BRIDGE_SAMPLE",json.dumps([x["path"] for x in m["assets"][:12]]))
    return m
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--visual",required=True,type=Path);parser.add_argument("--game",required=True,type=Path)
    parser.add_argument("--dry-run",action="store_true")
    a=parser.parse_args()
    run(a.visual,a.game,a.dry_run)
