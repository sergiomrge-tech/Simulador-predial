"""Scale / axes / pivot audit of the W3 vertical slice before the Blender -> Unity export (read-only, never saves).

blender -b ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend --python Tools/Blender/audit_unity_scale_axes.py -- --root . --out report.json

Hard errors: scene units not metric 1:1; NaN/inf transforms; negative or non-uniform scale on exported static meshes (Unity would mirror/skew them);
objects tagged with a sub-cell whose world origin is more than 1 m outside that sub-cell for plain meshes (pivot would break per-cell offsets);
hero instances not at scale 1 / rotation 0; missing hero roots of the corridor. Observations (not errors): Geometry Nodes instancers and
libraries, which carry their positions in the point data.
"""
import json
import math
import re
import sys
from pathlib import Path

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
root = Path(argv[argv.index("--root") + 1]).resolve()
out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
corridor = json.loads((root / "Docs" / "unity-vertical-slice-corridor-v1.json").read_text(encoding="utf-8"))
cells = set(corridor["cells"])
scene = bpy.context.scene
errors, obs = [], {}


def rect(sub):
    m = re.match(r"SA_M(\d{2})_(\d{2})_S(\d{2})_(\d{2})", sub)
    ix, iz, sx, sz = (int(g) for g in m.groups())
    x0, y0 = -4000 + ix * 1000 + sx * 250, -4000 + iz * 1000 + sz * 250
    return x0, y0, x0 + 250, y0 + 250


if scene.unit_settings.system != "METRIC" or abs(scene.unit_settings.scale_length - 1.0) > 1e-9:
    errors.append("scene units are not metric 1:1")
bad_scale = bad_nan = pivot_out = checked = gn = 0
sub_seen = set()
for o in bpy.data.objects:
    if o.library is not None:
        continue
    if any(not math.isfinite(v) for v in list(o.location) + list(o.rotation_euler) + list(o.scale)):
        bad_nan += 1
    sub = o.get("sa_subcell")
    if not sub or o.type != "MESH":
        continue
    sub_seen.add(sub)
    if any(m.type == "NODES" for m in o.modifiers):
        gn += 1
        continue
    checked += 1
    if min(o.scale) <= 0 or max(o.scale) - min(o.scale) > 1e-4:
        bad_scale += 1
    x0, y0, x1, y1 = rect(sub)
    p = o.matrix_world.translation
    if not (x0 - 1 <= p.x <= x1 + 1 and y0 - 1 <= p.y <= y1 + 1) and not (abs(p.x) < 1e-3 and abs(p.y) < 1e-3):
        pivot_out += 1
if bad_nan:
    errors.append(f"{bad_nan} objects with NaN/inf transforms")
if bad_scale:
    errors.append(f"{bad_scale} static meshes with negative/non-uniform scale")
if pivot_out:
    errors.append(f"{pivot_out} sub-cell meshes whose origin lies outside their sub-cell")
unknown = sorted(sub_seen - cells)
heroes = {o.name: o for o in bpy.data.objects if o.name.startswith("W2I_")}
for h in corridor["heroIds"]:
    o = heroes.get("W2I_" + h)
    if o is None:
        errors.append("missing hero instance W2I_" + h)
    elif o.instance_collection is None or any(abs(s - 1) > 1e-6 for s in o.scale) or any(abs(r) > 1e-6 for r in o.rotation_euler):
        errors.append(f"hero instance W2I_{h} is not an identity-scale/rotation collection instance")
obs.update({"meshesChecked": checked, "geometryNodesInstancers": gn, "subcellsInFile": len(sub_seen), "subcellsOutsideCorridor": unknown[:6],
            "unitSystem": scene.unit_settings.system, "unitScale": scene.unit_settings.scale_length})
report = {"passed": not errors, "errors": errors, "observations": obs, "blenderUp": "Z", "unityUp": "Y (FBX exporter converts; manifests carry Blender bounds)"}
if out:
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("UNITY SCALE/AXES AUDIT", "PASS" if not errors else "FAIL", json.dumps({"errors": errors, "obs": obs}))
sys.exit(1 if errors else 0)
