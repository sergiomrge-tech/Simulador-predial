# Project Resort — Codex urban visual pass — 2026-10-07

Latest shared-editor continuation: [live MCP corrections and validation](CODEX_URBAN_LIVE_CONTINUATION_2026-10-07.md).
Entrance geometry and lot access paving were refined; a real urban 1/1 pass is recorded.
Final full-suite validation remains unresolved. The earlier isolated evidence below
is historical and does not establish approval of the latest parallel working tree.

**Visual phase: NOT APPROVED. Phase 03 remains blocked.** The safe replacement/integration work using the available approved local urban assets is implemented and tested. Visible placeholders remain in the wider coastal environment and in parts of this scope; an integration test pass is not final art approval.

Repository: `D:\sergi\Documents\Simulador-predial`, branch `claude/w1-masterplan`. Unity: `6000.6.2f1`, URP. No commit, checkout, reset, gameplay progression implementation, or BeachLife AI rewrite was performed.

## Delivered changes

- All 234 existing town lots use the eight approved building archetypes. Imported bounds determine footprint fit; horizontal scaling stays uniform, and vertical scaling is bounded to preserve plausible floor proportions.
- Buildings rest above the highest sampled point of their rotated footprint. Concrete foundation geometry extends below the lowest sampled ground point. The existing hidden collision meshes remain enabled.
- Building meshes are combined by material within 90 × 120 m sectors instead of across the entire town, allowing spatial culling. Final runtime telemetry: 309 building renderers. This is a batching/culling change, not a measured FPS improvement.
- Removed 76 connected cuboid AC/grille components from the eight **project copies** of the building kit. Original library FBXs, editable blends and previews remain intact. Selected scanned condensers now dress rear service facades.
- Closed the 9 m discontinuity between all six north/south streets and the avenue. Streets ending 6 m short of the map edge continue to the boundary as intentional exits.
- Roads form one surface union. Sidewalks occupy the expanded road footprint minus carriageways, so pavement no longer crosses intersections. Added narrow curb caps/risers, interrupted curbs at crossings, pedestrian stripes, and centre lines interrupted at junctions.
- Ground overlays follow the existing heightfield and add no replacement navigation or collision authority. Final meshes: 29,168 road vertices and 15,472 sidewalk vertices, plus curbs and markings.
- Promoted single scan variants rather than whole variant/parts catalogues. The hydrant copy no longer includes the aged duplicate. Gutters/downpipes are individual parts, not a catalogue placed in the world.
- Added street lamps, benches, planters, hydrants, utility cabinets, manhole covers, rear condensers, shutters, shop wall fixtures, chalkboards and selected drainage details. Final telemetry: 78 street/promenade props; additional facade dressing is recorded in the capture TSV.
- Scan material slots retain separate atlases for condenser surfaces, lamp glass/bulbs and chalkboard frame/board. Fourteen material sets have 1K base colour, GL normal and packed metallic/occlusion/smoothness maps, mipmaps and streaming import settings. Shared meshes/materials and distance culling are retained.
- Corrected scan axis placement and front/back orientation. Position/yaw wrappers preserve the imported model hierarchy; the selected scan frame is adapted from Unity -Z vertical to +Y. Shutters receive their own frontage orientation rather than being buried in the wall.
- Replaced the beige cuboid recruitment mural with the scanned standing chalkboard. `JobBoard` keeps its original `PanelStation`, hire panel and collider. The original slab/post renderers are hidden, and the caption sits on the scanned board. Counter, cooler, refrigerator and kiosk look switching remain functional in structural checks.

## Files changed by this pass

Paths below are relative to the repository. Many were already locally modified/untracked when this task began; this report describes only this session's changes.

| File/path | Change |
| --- | --- |
| `FacilityOps/Assets/_Game/Scripts/Resort/Site/CoastalUrbanAssets.cs` | Complete-kit guard, measured fit, rotated ground sampling, foundations, local-coordinate bake and spatial batches |
| `FacilityOps/Assets/_Game/Scripts/Resort/Site/CoastalUrbanGround.cs` | Connected road union, non-overlapping sidewalks, curb geometry and crossings |
| `FacilityOps/Assets/_Game/Scripts/Resort/Site/CoastalUrbanProps.cs` | Multi-slot PBR scans, metric placement/axis adapter, facade dressing, street furniture and visual-only kiosk board integration |
| `FacilityOps/Assets/_Game/Scripts/Resort/Game/StallBuilder.cs` | One integration call after existing realistic kiosk dressing; prior local changes preserved |
| `FacilityOps/Assets/_Game/Scripts/Resort/Editor/ResortTextureImport.cs` | Extend existing normal/mask/mipmap rules to urban prop maps |
| `FacilityOps/Assets/_Game/Resources/Art/Resort/Urban/*.fbx` | Eight derived project-owned building copies with embedded AC blockouts removed |
| `FacilityOps/Assets/_Game/Resources/Art/Resort/UrbanProps/` | Thirteen selected FBX exports, fourteen map sets and import metadata |
| `FacilityOps/Assets/_Game/Tests/PlayMode/UrbanVisualPassTests.cs` | Connectivity, sidewalk exclusion, metric scan bounds, grounding, shaders/PBR, kiosk stations/look switching and eight graphics captures |
| `FacilityOps/Assets/_Game/Tests/Editor/ResortAurora.Tests.Editor.asmdef` | Editor test-runner assembly |
| `FacilityOps/Assets/_Game/Tests/Editor/CodexUrbanValidationRunner.cs` | Menu and explicit one-shot file request for running the scoped test when MCP is unavailable |
| `Tools/Blender/audit_codex_urban_sources.py` | Read-only FBX geometry/material/UV inventory |
| `Tools/Blender/promote_codex_urban_props.py` | Reproducible scan selection, canonical origin, 1K PBR packing and provenance hashes |
| `Tools/Blender/refine_codex_urban_buildings.py` | Reproducible AC component removal from in-memory source blends; only project FBXs are exported |
| This report and `Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_pass/` | Provenance, hashes, geometry audit and delivery verification |

New scripts, folders and assets have Unity metadata. The exhaustive list of 71 validated code/geometry/map inputs and their hashes is in [delivery_verification.json](Evidence/CODEX_2026-10-07/urban_pass/delivery_verification.json).

## Assets and source paths

The building kit was already staged before this task. Its integration was refined, and the project FBXs were re-exported from the original editable blends without saving those source blends.

Source directory: `D:\ProjectResort_AssetLibrary\ProjectOwned\CoastalUrbanKit`.

Building sources: `casa_terrea.blend`, `sobrado.blend`, `loja.blend`, `misto.blend`, `apartamento.blend`, `hotel.blend`, `townhouse.blend`, `residencial_sacadas.blend`. Their corresponding original FBXs remain in that directory. Derived FBXs retain their existing project GUIDs. See [building_refinement.json](Evidence/CODEX_2026-10-07/urban_pass/building_refinement.json) for component counts and source hashes.

The following folders are under `D:\ProjectResort_AssetLibrary\PolyHaven_CC0\UrbanKit`. Destination folders have the same names under `FacilityOps/Assets/_Game/Resources/Art/Resort/UrbanProps`.

| Source folder | Project export / selection |
| --- | --- |
| `exterior_aircon_unit_2K` | `exterior_aircon_unit_2k.fbx`; clean condenser only; two material slots |
| `fire_hydrant_2K` | `fire_hydrant_2k.fbx`; one hydrant with its caps and chain |
| `painted_wooden_bench_2K` | `painted_wooden_bench_2k.fbx` |
| `planter_box_01_2K` | `planter_box_01_2k.fbx` |
| `rollershutter_door_2K` | `rollershutter_door_2k.fbx`; one clean door |
| `rollershutter_window_01_2K` | `rollershutter_window_01_2k.fbx`; one clean window shutter |
| `standing_chalkboard_01_2K` | `standing_chalkboard_01_2k.fbx`; frame and board atlases |
| `street_lamp_01_2K` | `street_lamp_01_2k.fbx`; metal, glass and bulb slots |
| `street_lamp_02_2K` | `street_lamp_02_2k.fbx`; wall fixture |
| `utility_box_01_2K` | `utility_box_01_2k.fbx` |
| `water_manhole_cover_2K` | `water_manhole_cover_2k.fbx`; cover and frame |
| `modular_metal_gutter_2K` | `gutter_section.fbx` and `downpipe.fbx`; individual horizontal/vertical modules |

See [promoted_assets.json](Evidence/CODEX_2026-10-07/urban_pass/promoted_assets.json) for exact donor FBX paths, selected objects, polygon counts and hashes. The modular street seating catalogue was not instantiated as assembled furniture; the approved wooden bench provides the safe seating replacement.

The previously staged PBR surfaces remain sourced from `D:\ProjectResort_AssetLibrary\PolyHaven_CC0\UrbanSurfaces`: `asphalt_01`, `concrete`, `concrete_pavers_02`, `white_stucco_02`, `clay_roof_tiles_02` and `brick_wall_04`. This pass uses the existing `urban_*` map sets; it does not claim them as newly downloaded assets.

Previously integrated outdoor furniture, cash register, crates, bottles and Renderpeople/HBM assets were retained. No new human retargeting or AI changes were required for this urban integration.

## Before / after issues resolved

| Before | After |
| --- | --- |
| Six streets stopped before the avenue | Continuous asphalt connection through the avenue junctions |
| Sidewalk strips ran across roads | Sidewalk quads excluded from the road union; crossings interrupt curbs |
| Whole-city material batches | Material batches per spatial sector |
| Lowest-ground placement and nominal dimensions could expose unsupported buildings | Measured footprints with high-ground support and concrete foundations |
| Missing optional archetype could silently leave a visual gap | All eight required; partial bake reports an error and retains fallback visuals |
| Props received one diffuse material across unrelated UV slots | Separate scan atlases with normals and packed PBR maps |
| Hydrant included multiple variants; kit could appear as a parts catalogue | Selected single variants and individual drainage modules |
| Scan axes could produce horizontal giant lamps or overturned furniture | Axis adapter, metric width/depth assertions and actual screenshot inspection |
| Cuboid AC units embedded in building meshes | 76 source components removed; scanned condenser dressing |
| Flat beige recruitment board | Scanned A-frame chalkboard; original station/collider retained |

## Validation and evidence

The MCP HTTP server returned an empty instance list. The original Editor and its UPM service were left running. Validation used an isolated copy under `FacilityOps/Captures/CodexUrbanPass/ValidationProject`, a private UPM pipe and the same installed Unity version. All owned inputs matched the validated copy byte-for-byte. Final evidence was copied out of the temporary validation project; the shared project was not replaced by this copy. The temporary project remains because the execution policy rejected the cleanup command with `blocked by policy`. No alternative deletion was attempted. The private `Unity-Upm-CodexUrban` helper (PID 10300 at creation) was in the same rejected cleanup command and is also retained; the batch validation Editor exited normally.

Final command used `-batchmode -runTests -testPlatform PlayMode -testFilter ResortAurora.Tests.UrbanVisualPassTests`, with graphics enabled. Test saves were temporary and separate from the user's save.

Final run: **2026-10-07 14:55:59–14:56:03 America/Sao_Paulo**. **1 targeted PlayMode test passed, 0 failed; Unity exit code 0; 0 C# compilation errors in the final log.** This single test exercises the entire urban integration and contains multiple assertions; it is not a full gameplay regression suite.

Checks performed:

- All eight building Resources resolve; replacement renderers exist and the collision fallback remains enabled but visually hidden.
- Each north/south centreline stays inside the road union from the avenue to its existing extent; all east/west intersections are road, not sidewalk.
- Every generated sidewalk quad centre lies outside the carriageway union.
- Street/promenade scan feet match the sampled ground lift; lamp/hydrant heights and lamp horizontal bounds are metric. Facade shutter/downpipe dimensions are checked and recorded separately.
- Enabled site materials have supported shaders and no `Hidden/InternalErrorShader`; mapped urban props have normal and metallic/smoothness maps. Captures were inspected and show no magenta materials in the reviewed urban/kiosk views.
- Counter, cooler, refrigerator and recruitment station components persist. Recruitment collider and hire panel remain intact, including kiosk look switching; the old board renderer stays hidden.
- Eight final screenshots inspected: connected town roads, avenue junction, street frontages, rear/side elevations, scanned bench, condenser detail, kiosk/mural, service shutter.
- 46 baseline `ArtSource/Blender/World/Reviews` PNG hashes are unchanged. Original donor FBXs and editable building sources remain intact. Existing local modifications were preserved.

Final evidence:

- Captures: `FacilityOps/Captures/CodexUrbanPass/20261007_145559/` — eight PNGs, `facade_dimensions.tsv`, `validation.txt`.
- NUnit results: `FacilityOps/Captures/CodexUrbanPass/batch-playmode-results.xml`.
- Final Unity log: `FacilityOps/Captures/CodexUrbanPass/batch-editor-final-review.log`.
- Source/UV/material audit, promotion/refinement logs, baseline hashes and delivery checks: `Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_pass/`.
- Earlier diagnostic screenshots and results are retained separately under `FacilityOps/Captures/CodexUrbanPass/diagnostic_20261007_144441/` and diagnostic XML/log files. They must not be mistaken for final evidence.

Validation failures were resolved before delivery: the first isolated launch with `-noUpm` lacked package references and was restarted with a private UPM service; the first graphics audit exposed scan axis/orientation faults; the expanded lamp proportion check failed before the adapter was corrected. Close review also caught shutters facing into the wall, which were corrected and recaptured. No package versions or settings in the shared project were changed to resolve those temporary validation issues.

## Remaining blockers and limits

1. **Vegetation remains visibly prototypical.** No approved realistic coastal palm/shrub donor exists in the available local library. The extracted Supercyan forest sample is not an acceptable coastal replacement. Angular palms in the kiosk capture remain a blocker.
2. **The town still has large bare green blocks and a sparse masterplan.** Road connectivity is fixed, but the untextured inland terrain, empty block interiors and limited planting still read as unfinished. Parcel footprints and gameplay routes were preserved. Realistic landscaping/ground assets and a coherent block-interior art pass are required.
3. **Bespoke staged landmarks remain outside the small-lot kit replacement:** lighthouse, hotel ruin, player home and later resort shells. The local small hotel/apartment donors do not match those structures' footprints, interiors or collision/routes. They need compatible detailed replacements, rather than stretching a lot archetype over the existing gameplay shell. Later phase progression was not implemented or used as a completion criterion.
4. **Some kiosk/beach objects still lack suitable approved local donors**, including sphere-like coconuts, some refrigeration/cooler forms and other small prototype equipment. Existing realistic furniture/register/crates/bottles were preserved, and the matching chalkboard replacement was completed. Seated/procedural human placeholders also remain; core BeachLife AI was not rewritten.
5. The approved modular building kit now integrates correctly but still needs final art-director acceptance for facade variety, glass response, flat-roof detail, frontage paving and service-yard context. No claim of photoreal final architecture is made solely from polygon counts or PBR maps.
6. No FPS/frame-time benchmark, full-hour lighting review, player build or complete gameplay suite was run. Sector batching, shared assets and culling are present, but performance must be measured in the shared playable project. The tested isolated copy contains a lighting snapshot; final shared-editor review should follow the parallel lighting pass.

Reserved lighting/shadow files, sea/sky/shore shaders, global post-processing and `ResortMaterials.cs` were not edited by this session. A concurrent change to `DayNightCycle.cs` was observed through hashes and was preserved; it is not attributed to this pass. `ResortSite.cs` and `ResortStages.cs` also remain byte-identical to this session's baseline.

**The visual phase is NOT approved unless every visible placeholder in this scope is gone and the shared playable result passes visual review. The remaining blockers above keep that approval closed.**


## Later live continuation ? 18:50 local

The final full suite now has a real **30/30 pass**, including LivingWorld **11/11** and the urban test. The discovery/zero-selection blocker above is historical and resolved for this snapshot. See [promenade lamps, current regression and remaining visual blockers](CODEX_PROMENADE_LAMPS_2026-10-07.md). F02 visual approval remains open.
