# Project Resort — urban continuation through live Unity MCP

**F02 visual gate remains OPEN. No later gameplay/content phase was advanced.**

Continued the existing working tree on `claude/w1-masterplan` in the shared Unity
6000.6.2f1 editor (`FacilityOps@80d9f59950304178`). The existing urban integration
was preserved: 234 lots, eight project-owned building archetypes, 309 sector
building renderers, 78 street/promenade props and original hidden collision.

## Changes in this continuation

- Actual Unity street captures exposed entrance doors intersecting ground-floor
  windows. Corrected **apartamento, residencial_sacadas and sobrado** project FBX
  copies. Each lost one intersecting glass component and its four window-frame
  bars; door lintels, other geometry, UVs/material slots and source-library
  `.blend`/FBX files remain intact. `Tools/Blender/correct_codex_urban_openings.py`
  records before/after hashes and exact removed components. Baseline project FBXs
  were copied to `Evidence/CODEX_2026-10-07/urban_live/original_fbx` before editing.
- Added PBR frontage paving from building thresholds to existing sidewalks and
  small commercial rear maintenance aprons. Reuses the already imported Poly
  Haven CC0 `concrete_pavers_02` and `concrete` materials. No new colliders,
  gameplay routes or parcel geometry. Corner sampling excludes road/sidewalk
  overlap. The original building/terrain collision is still authoritative.
- Expanded the urban PlayMode assertions to check apron existence, original
  collision preservation, and corner-level exclusion of roads and sidewalks.
- Existing `CodexUrbanValidationRunner` now re-registers its callback after
  domain reload and records NUnit XML only when explicitly enabled. This is an
  extension of the existing runner, not a competing automation/editor instance.
- Added `Unity.RenderPipelines.Core.Runtime` and
  `Unity.RenderPipelines.Universal.Runtime` references to the existing Resort
  runtime assembly. The parallel lighting pass introduced Volume/URP types;
  missing references caused CS0234/CS0246 on a fresh test compilation. The
  lighting implementation itself was preserved.

No stylized substitutes or new packages were introduced. The existing approved
CC0 table/chair integration was retained. Sea, lighting code, vegetation design,
human systems and shared scene/settings were not rewritten by this continuation.

## Exact validation and evidence

All scene images below come from actual execution in the shared Unity editor.
No synthetic screenshots or modifications of old review images were used.

- **18:17:27–18:17:31 America/Sao_Paulo: urban PlayMode 1/1 PASS, 0 failures.**
  Verified by NUnit XML, not solely the MCP job status. The MCP initialization
  timeout reported failure before the compilation repair; the Unity runner
  subsequently executed and completed the real test. XML:
  `Evidence/CODEX_2026-10-07/urban_live/urban-playmode-pass.xml`.
- Full PlayMode attempt at **18:05:51–18:10:15: 29/30 PASS**. The urban test's
  assertions/captures completed, but NUnit rejected a compiler error logged from
  a concurrent `CoastalVegetation.cs` edit (CS1628, ref parameter captured by a
  local function). The parallel continuation corrected it before this session's
  attempted patch; the patch did not apply and **this session did not edit that
  vegetation file**. Failed XML is retained as
  `full-suite-interrupted-by-compilation.xml`.
- A second full run was cancelled in the shared editor after seven tests. It is
  not treated as a pass. The original inverted-range living-world test did pass
  in the first full run, together with all other living-world cases.
- Subsequent test requests returned `Passed` with **zero tests**. These are
  explicitly rejected as validation. Read-only discovery still reports 30 real
  PlayMode cases. Invalidating the transient discovery cache (the same operation
  the installed Test Framework uses after script reload) enabled the real 1/1
  urban run, but did not yield a reliable final full-suite rerun. No active Unity
  runner was cleared; orphaned MCP bookkeeping was cleared only after confirming
  Unity's `TestJobDataHolder.TestRuns` was empty.
- Eight urban screenshots from the real 1/1 run are copied into
  `Evidence/CODEX_2026-10-07/urban_live/final_captures/`. Includes frontage,
  avenue/junction, rear/side context, scan bench, condenser, kiosk and service
  shutter. A final positioned MCP street capture is also retained there.
- Live performance probe: **60 valid buffered samples across 360 rendered frames**,
  camera unchanged at `(330, 5.50, 338.50)`, editor Game View `1101x506`.
  CPU total median **3.4726 ms**, p95 **3.8723 ms**; main-thread median
  **2.3169 ms**; render-thread median **1.1540 ms**. Scene/editor counters show
  7,880,580 triangles and median 582 BRG calls. These include editor/scene/shadow
  work and do **not** establish standalone FPS or an optimization comparison.
  Raw samples summary and context: `performance_live.tsv`,
  `performance_context.txt` in the same evidence directory. The probe changed
  neither the camera nor scene objects.
- Console reported zero current errors after the assembly-reference repair.
  Current code/geometry hashes are in `live_delivery_hashes.json`.

## Remaining blockers

Final full-suite execution is blocked by unreliable test selection/lifecycle in
the shared live editor: discovery shows 30 cases but later runs execute zero.
The earlier 29/30 result and the subsequent 1/1 urban pass are separate snapshots,
not a claimed final 30/30 pass. Resolve that lifecycle issue and obtain a real
30-case NUnit report before treating this milestone as fully validated.

The architecture still needs director acceptance for facade/glass/roof detail,
large block interiors and ground context. The local small-lot kit does not solve
lighthouse, hotel ruin, player home or larger resort landmark shells. The
parallel vegetation and human passes have changed since the earlier report;
their latest quality/performance gates require their own review. Global night
lighting and standalone-build performance are also still pending acceptance.
The reviewed final kiosk capture still shows a procedural stacked-body person
in the foreground and angular promenade palms. These visible placeholders are
explicit visual blockers; the preserved CC0 furniture and chalkboard do not
make that view acceptable as final realistic art. Street facades are also very
dark in the latest lighting snapshot and need the lighting owner's contrast review.

No commit or push was created for this continuation because complete regression
validation remains unresolved. Uncommitted parallel work and the index were
preserved; no reset, checkout, clean, revert or deletion was performed.


## Later live continuation ? 18:50 local

The final full suite now has a real **30/30 pass**, including LivingWorld **11/11** and the urban test. The discovery/zero-selection blocker above is historical and resolved for this snapshot. See [promenade lamps, current regression and remaining visual blockers](CODEX_PROMENADE_LAMPS_2026-10-07.md). F02 visual approval remains open.
