# Project Resort: promenade lamps and live urban regression, 2026-10-07

F02 visual phase remains OPEN. No later gameplay/content phase was started.

## Changes

The 12 promenade fixtures closest to the kiosk now use the approved Poly Haven CC0 `street_lamp_01` scan already imported into `UrbanProps/street_lamp_01_2K`. Metric height is 4.2 m, feet meet the existing terrain, and the original pole collider remains authoritative. Original pole, arm and head objects are retained as asset fallback; only their renderers are hidden after the scan is available. Shared meshes/materials and the existing distance LOD are retained. No additional point light was created: the eight-light pool is unchanged.

The scan has separate metal, glass and bulb slots. Its existing base colour, GL normal and packed metallic/occlusion/smoothness maps remain in use. Glass now uses transparent URP Lit rendering with alpha 0.22, so the lantern's physical bulb is visible. The bulb mesh follows the existing shared dusk/night emissive material. Existing light registration positions are relocated to the actual bulb bounds rather than outside the lantern. Urban street fixtures use the same emitter correction. Source/library originals were not modified. Source: https://polyhaven.com/a/street_lamp_01 ; license: CC0, recorded in the imported LICENSE_SOURCE.txt.

This completes the lamp block on top of the existing assigned urban pass: connected roads/sidewalks/crossings, fitted and sector-batched project-owned buildings, corrected entrance openings, access/service paving, CC0 street/facade props and kiosk chalkboard. The previously integrated Poly Haven outdoor table/chair set remains in the kiosk view. Parallel human, vegetation, deck and global lighting changes remain in the working tree.

## Real Unity validation

- Scoped `UrbanVisualPassTests.ConnectedGroundAndScansPreserveKiosk`: **1/1 passed**, 4.68552 s case duration, XML `test-results-20261007_184342_217.xml`.
- Complete PlayMode suite: **30/30 passed**, zero failed/skipped, 260.6275304 s. MCP job `ef1bb8844a2a47d59629048fbaa62f88`; NUnit XML `test-results-20261007_185039_830.xml`.
- `LivingWorldTests` within that full run: **11/11 passed**, including the previously corrected day/night range assertion.
- First full-run attempt used the incorrect assembly name `ResortAurora.Tests` and selected zero cases; it is discarded as validation. Actual assembly name is `ResortAurora.Tests.PlayMode`. A normal Editor script reload refreshed discovery, then an unfiltered PlayMode run executed all 30 cases successfully.
- Scoped assertions cover the 12 scanned lamps, height, orientation, ground contact, preserved pole collisions, LOD, glass transparency, shared emissive bulb, eight pooled point lights and nearby enabled light at night. Night capture moves the actual main camera to the review view and allows the existing pool update before rendering.
- Capture root was redirected to `FacilityOps/Captures/CodexPromenadeLamps/full_suite` for tests that use shared review folders. Urban captures have their own timestamped folder `FacilityOps/Captures/CodexUrbanPass/20261007_185036`. Temporary capture environment cleared afterward. No baseline review PNG was replaced by this execution.
- Five selected final captures, XML reports, geometry TSV and hashes are archived in [promenade evidence](Evidence/CODEX_2026-10-07/promenade_lamps/). All images are from Unity execution. No generated or edited screenshot is used.
- Live console read after restarting normal Play Mode: **zero current errors**. Unity was left running the existing `ResortPrologue` scene.

## Performance limits and remaining visual blockers

The 12 promenade scan meshes contain **367,320 base triangles** in total (30,610 per fixture), with 12 mesh renderers and shared material slots. This is additional detail, so the existing distance culling must remain. The pool still contains eight point lights; no extra shadowed light was introduced.

A non-mutating 360-rendered-frame Editor probe collected 60 samples at 1101 x 506, camera `(330, 5.50, 338.50)`: median CPU main thread **2.9917 ms**, render thread **1.3835 ms**, total **4.171 ms**, p95 total **5.1403 ms**, 64 SetPass calls, 749 BRG draws, approximately **9.53 million rendered triangles**. These counters include Editor/scene work and the entire current parallel working tree. They are neither standalone FPS nor a controlled before/after performance comparison. Raw TSV/context are in the evidence directory.

URP reported additional-light shadow atlas resolution reduction while fitting 12 cube-face shadow maps into the 2048 atlas. Existing two shadowed pooled point lights explain that pressure; this pass did not increase their count. Standalone GPU/frame-time validation remains required.

The inspected images still show angular/procedural palms, occasional procedural people, large sparse city plots, dark daytime facades and a night view that remains too dark to approve the overall scene. Scan detail and functional tests do not establish final realism. Vegetation/human/global lighting owners' work was preserved. F02 must stay open until those issues and close-up architectural quality are accepted by the Director.

## MCP connection

Installed MCPForUnity is **v10.2.0** and live connector calls succeeded against `FacilityOps@80d9f59950304178` over `http://127.0.0.1:8080/mcp`. No reinstall or config rewrite was necessary. The Codex config SHA256 before/after was identical: `80d4e259c3f9ba738b6beb4d999adcf0536a2d75d70d49d8bc2680f271edf380`. Other MCP entries are unchanged. See [connection proof](UNITY_MCP_CODEX_REVERIFICATION_2026-10-07.json).

The focused urban integration milestone stages only urban assets/scripts and relevant integration lines in shared files. Global lighting, vegetation, human, deck and other parallel modifications are excluded and remain locally intact. Unused original donor texture copies are also excluded from the commit; only runtime PBR derivatives are staged. Shared working-file hashes were checked before/after index staging and remained identical. The 30/30 result validates the complete current working tree, including those parallel changes; it is not a separately executed test of the staged subset.
