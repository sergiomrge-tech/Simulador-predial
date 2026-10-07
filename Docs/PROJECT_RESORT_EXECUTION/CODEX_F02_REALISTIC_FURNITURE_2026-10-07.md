# Codex — F02 realistic furniture integration, 2026-10-07

This is a focused visual/assets continuation on `claude/w1-masterplan`, starting at `3935f19`. Phase 03 remains blocked. The visual gate is not approved merely because tests pass.

## Actually integrated

- Poly Haven **Outdoor Table Chair Set 01**: normalized metric table (0.726 m) and chair (0.859 m), original UVs, shared meshes/materials, distance culling. Replaces only the stage-one table/chair renderers; the table collider, six customer anchors, upgrade ownership and stage-two seating remain in the existing architecture. A complete mesh/texture set is required before hiding any procedural fallback.
- Source already downloaded at `D:/ProjectResort_Autonomy/assets/PolyHaven_CC0/OutdoorTableChairSet01_2K`. The preferred `D:/ProjectResort_AssetLibrary/UnityFree/Realistic_PBR_Whitelist` contains a list, not the listed realistic packages.
- Furniture runtime maps: 1K base color, OpenGL normal and metallic/smoothness (alpha = 1 - roughness). Original 2K assets remain intact. URP maps import with mipmaps, streaming and correct data/color spaces.
- Existing project-owned `galvanizado` and `pedra_portuguesa` maps from `ArtSource/Textures/texture_library_w3.json`: applied to the kiosk roof and a single calçadão surface following the existing terrain. No new terrain collider.
- Editable source: `ArtSource/Blender/Resort/CC0_Furniture_Normalized.blend`, with textures packed. This remains local under the existing .gitignore; the FBX exports and runtime maps are distributable project content.
- Preparation scripts reuse the project's Blender FBX export conventions: `Tools/Blender/prepare_resort_furniture.py` and `Tools/Map/prepare_resort_pbr_textures.py`.

Provenance: https://polyhaven.com/a/outdoor_table_chair_set_01 . License checked against https://polyhaven.com/license on 2026-10-07: CC0, commercial use and redistribution permitted. The local license record accompanies the exports. No Asset Store paid content was purchased or promoted.

## Initial assertion and test evidence

The working tree already had the swimmer range ordered with `Mathf.Min`/`Mathf.Max`, with the same ground/water limits and tolerance. It was preserved rather than widened.

- Initial `LivingWorldTests -Graphics`: **10/10**, XML `Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/logs/unity_PlayMode_20261007_085219.xml`.
- Initial full `ResortAurora.Tests -Graphics`: **21/21**, XML alongside, `unity_PlayMode_20261007_085356.xml`.
- First visual living-world pass: **10/11**. The added furniture legitimately removes the prototype tabletop renderer while retaining its filter/collider; the existing wood-only assertion assumed every filter still had a renderer. The current assertion checks surviving timber renderers without removing its stage visibility requirement.
- First new furniture test: **1/2**. Corrected the LOD lookup to include initially inactive upgrade furniture. Added coverage for stage-one/stage-two visibility, metric scale, shared meshes/materials, PBR maps, upgrade/seat counts, navy night horizon and purchase-only parcel overlays.
- A launch at 09:04:48 produced no verdict because another Unity test process was already using this project. It is an infrastructure collision, not a passing test.

Final validation and capture paths will be appended below after execution.

## Preservation and concurrent work

Existing code/test edits and F02/R5 review captures were retained. Additional writes from another active continuation were observed during this run (surface material helper, city façades, compact beach export, signage, masks and tests). They were preserved and are validated as part of the resulting working tree; this report does not claim exclusive authorship of them.

**Preservation incident:** the first full suite included three legacy tests (`StagesTests`, `PousadaInteriorTests`, `PrologueDayTests`) with hardcoded `Reviews/R4` or `Reviews/R2` destinations. They regenerated review images despite the redirected test environment. Fifteen R2/R4 PNGs differ from the preexisting `CODEX_REVIEWS_HASHES_2026-10-07.json` record. No hash-identical backups were located in the existing evidence or desktop capture folders. These test paths now honor `RESORT_TEST_CAPTURE_ROOT`; subsequent executions use separate evidence directories. No reset/checkout/clean/revert was used. Do not claim all original binary review bytes were preserved.

## Remaining visual blockers

- Close NPCs still use HBM mannequins/procedural poses and lack realistic final clothing/skin. HBM is approved for animation, not proof of final human appearance.
- Sand, umbrellas, kiosk equipment, bottles/crates and palms still have prototype elements. Furniture improvement does not make the whole world final.
- City façade dressing still needs visual approval and realistic architecture replacements.
- Sea requires improved shoreline foam, reflections/refraction and material integration; the current sea is still simple.
- Human two-day playtest and audio assessment remain pending. No progression/content phase was advanced.
- Do not use Low Poly Tropical Beach, lowpoly Art Deco, fantasy monsters, Earth Mage or stylized forest content as Resort final art. Earlier recommendations in the asset audit are superseded by this directive and the whitelist.
## Final execution — complete

- Focused LivingWorld + furniture/overlay tests: **13/13** (`CODEX_Visual_20261007_0908/logs/unity_PlayMode_20261007_090753.xml`).
- Full `ResortAurora.Tests`, PlayMode, graphics: **24/24**, **0 failed, 0 skipped**, Unity exit **0**. Exact XML: [unity_PlayMode_20261007_091100.xml](Evidence/CODEX_VISUAL_FINAL_091100/unity_PlayMode_20261007_091100.xml). Full log remains at `D:/ProjectResort_Autonomy/Evidence/CODEX_Visual_20261007_Final/logs/unity_PlayMode_20261007_091100.log`.
- Renderer measurement in this final run: beach average **3.3 ms**, p95 **3.8 ms**, worst **4.8 ms**, **69 NPCs**, LOD `[39,30,0,0]`, **18 registered lamps**. Initial run: average **2.9 ms**, p95 **3.3 ms**, worst **3.6 ms**, **67 NPCs**. These are batch-render/readback measurements, not end-to-end gameplay FPS certification; modest additional measured cost.
- Inspected actual Unity captures: [tables by day](Evidence/CODEX_VISUAL_FINAL_091100/tables_day.png), [tables at night](Evidence/CODEX_VISUAL_FINAL_091100/tables_night.png), [night kiosk](Evidence/CODEX_VISUAL_FINAL_091100/f02_4_noite_kiosque_da_calcada.png). Furniture, navy sky and warm lighting materially improve this representative view; prototype equipment/umbrellas/humans remain visible.
- Reopened the editable blend in Blender 5.2: chair **2052 vertices**, table **1304 vertices**, correct metric dimensions, **16 packed images**. Source remains local and editable.
- Concurrent continuation created `95fa839` (`Improve phase 02 with CC0 PBR beach assets and mode-only parcel overlays`) during final verification. It contains the integrated runtime, assets and tests from the shared working tree. No push was performed in this run. Original code/test edits are present in that shared commit, not discarded.
- Three legacy capture destinations now honor `RESORT_TEST_CAPTURE_ROOT`. The R2/R4 preservation incident above remains explicitly recorded; no unsupported claim of byte-for-byte recovery is made.
- **Gate status: F02 VISUAL_OPEN / HUMAN_GATE_PENDING; F03 BLOCKED.** No new later-phase gameplay/content was implemented.