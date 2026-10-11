# Project Resort — realistic humans pass — 2026-10-07

Three realistic adult visual variants are integrated and proven in Unity 6000.6.2f1 / URP: **Eric, Carla and Claudia**. They use the existing BeachLife/PersonRig selection and HBM animation graph. The targeted upright adult validation passes; **the overall visual phase remains OPEN** because beachwear, children, special poses and distant procedural fallback coverage remain incomplete. Phase 03 was not advanced.

## Promoted assets and provenance

Runtime folder: `FacilityOps/Assets/_Game/ThirdParty/Resources/RealisticHumans/` (already excluded from Git by the existing ThirdParty rule).

| Variant | Approved local source under `D:/ProjectResort_AssetLibrary/Renderpeople_Free_Rigged/Source/` | Runtime mesh | Vertices | Triangles | Weighted bones |
| --- | --- | --- | ---: | ---: | ---: |
| Eric | `rp_eric_rigged_001_FBX/rp_eric_rigged_001_u3d.fbx` | `Eric.fbx` | 11,437 | 20,539 | 69 |
| Carla | `rp_carla_rigged_001_FBX/rp_carla_rigged_001_u3d.fbx` | `Carla.fbx` | 11,588 | 19,984 | 69 |
| Claudia | `rp_claudia_rigged_002_FBX/rp_claudia_rigged_002_u3d.fbx` | `Claudia.fbx` | 12,149 | 21,489 | 69 |

Carla and Eric's FBXs and reduced maps were already present on arrival. This pass promoted Claudia's existing extracted Unity FBX and generated `Claudia_BaseColor.png`, `Claudia_Normal.png` and `Claudia_MetallicGloss.png` from the downloaded originals. Each scan has one skinned renderer and one submesh. Original meshes, UV atlases and skin weights are shared without palette repainting or geometry replacement. The source archives and original texture files were preserved.

`Tools/Map/prepare_realistic_humans.py` is reproducible and does not overwrite existing runtime FBXs/maps. `PROMOTION_LOCAL_ONLY.json` stores exact source paths and SHA256 values. All maps are 2048px. Metallic RGB is zero; alpha carries source gloss. Base color is sRGB; normal and gloss are linear. Mipmaps and texture streaming are enabled.

The local provenance record is `D:/ProjectResort_AssetLibrary/Licenses/Renderpeople_Free_Rigged/README.md`, with archived `source.html`, `terms.html` and `download.json`. It records the Renderpeople free license, source `https://renderpeople.com/free-3d-people/`, and terms archived as version 13.12.2024. These assets are **not CC0 or project-owned**; keep raw models/maps local and do not redistribute them in a public repository. No new assets were downloaded or purchased. HBM remains the existing Kevin Iglesias Human Basic Motions FREE integration, under its separate Unity Asset Store license.

Other approved sources were inventoried without promoting unverified locomotion models:

- Animated collection: Sophia idling, Manuel dancing and Nathan walking, supplied as nested FBX ZIPs. They are unnecessary for the three verified rigged variants and were not substituted into the runtime graph.
- Posed collection: `rp_posed_00178_29.fbx` and its base color/normal/roughness/specular maps. A fixed posed scan is not a verified locomotion avatar and was not presented as an animated person.
- HBM models and all ten male/female clips remain at `Assets/_Game/ThirdParty/Resources/HBM`. No HBM source import metadata was edited.

## Rig, retargeting and material decisions

All three Unity imports were inspected and have `avatar.isValid == true`, `avatar.isHuman == true` and Humanoid import type. The imported centimetre file scale is 0.01; Unity's effective models are metric. Model animation, imported cameras/lights and source material import are disabled. Bone hierarchy remains available for inspection; meshes are not CPU-readable during normal gameplay.

The human mapping includes hips, spine/chest, neck/head, shoulders/arms/hands, upper/lower legs, feet/toes and fingers. The complete mapping, geometry counts, texture settings and HBM clip flags are captured in `avatar-import-audit.txt`. HBM's gender-specific Idle01, Idle02, Walk01_Forward, Run01_Forward and Talk01 clips all report Humanoid motion and are retargeted through each scan's own avatar. Root motion remains disabled, so BeachLife owns world movement and paths.

The scan material uses `Universal Render Pipeline/Lit`, with base color, normal and metallic/smoothness maps. A single cached material is shared by every instance of each scan. No per-person scan materials or textures are created. Shader support and required maps are checked before selecting a scan.

Normalization measures the body in its own frame rather than world-scaled renderer height, preserving PersonRig's existing height variation. The original sole offset is removed at initialization, and Humanoid foot IK is enabled for scans. Walk/run speed references and blend rates stay unchanged. Ground contact is validated using baked, animated vertices transformed into world space, not only renderer bounds.

Validation exposed a pre-existing visual issue: HBM Talk01 is not looping. Mixed-out clip inputs had already advanced beyond its end, causing a static conversation pose. HumanVisual now resets a non-looping selected clip on entry and repeats it while selected. The source clip and its import settings are unchanged.

## Runtime scope and performance

Clothed adult `Casual` and `Staff` looks are eligible. Male looks select Eric; female looks select Carla or Claudia using an independent deterministic seed derived from the existing person seed. The population RNG is not consumed by this choice. Existing randomized clip phases, idle variants, playback rates and state selection remain in use.

BeachLife.cs was not edited by this pass. Spawning, roles, paths, pooling, population rules, props and supported pose decisions remain in the existing code. LOD 0/1 use the skinned body where eligible; LOD 2 releases it to the existing distant representation; LOD 3 culls it. The active skinned limit remains **40**. Renderer offscreen updates remain disabled; the graph stops when the visual is hidden. Existing near/medium per-person shadow behavior was preserved.

The final natural-crowd sample recorded 77 active people, 33 skinned bodies, 11 realistic scan instances and all three variants. LOD counts were `[44,29,4,0]`. The test verifies that each variant's instances share one material. That scene sample reported 958 total draw calls and 9,444,726 triangles for the entire existing world, not just humans. These are editor snapshots, not an FPS benchmark or a measured performance improvement. The pass does not claim that the whole scene meets a performance budget. Each scan remains one renderer/submesh; no accessory renderers or extra material slots were added.

## Validation and real Unity evidence

Capture root:

`FacilityOps/Captures/CodexHumanPass/20261007_152206/`

- `realistic-human-tests.xml`: **2 passed, 0 failed, 0 skipped**, 40.93 seconds. All three scans were verified across Idle1, Idle2, Walk, Run and Talk, with animated mesh motion, valid avatars, original shared meshes, supported URP shader/maps, metric scale, ground contact, no idle T-pose and disabled root motion. The natural BeachLife test verifies all three variants and the active budget.
- `existing-tests-results.json`: initial **5 passed, 0 failed, 0 skipped** for HumanVisualTests and AssetGateF02Tests, including locomotion, special-pose fallback, far LOD, crowd budget and existing kiosk/furniture behavior.
- `retarget-ground-metrics.csv`: final measurements for all 15 model/clip combinations, using invariant decimal formatting.
- `avatar-import-audit.txt`: complete import/rig/clip audit.
- `natural-crowd-metrics.txt`: runtime population and renderer snapshot.

Test-runner recovery: one temporary test compilation error (`UnityStats.batches` is unavailable in this editor) was corrected by retaining supported draw-call/triangle counters. Several repeated MCP runs returned zero tests after interrupted compilation and were explicitly excluded. A direct domain-reload attempt was aborted by the Unity Test Framework (`PlayModeRunTask` null reference, accompanied by ResortGame.Update during transition). A fresh compilation and clean Edit Mode context restored proper native test execution. Those harness attempts are not presented as passing tests or visual evidence, and no unrelated gameplay fix was added to conceal them.

The final expanded eight-test regression attempt was **incomplete**: the runner reached six completed entries, then reported `Cancelled by user` on `HumanVisualTests.TheBeachCrowdUsesSkinnedBodiesNearTheCameraWithinTheBudget`; native execution ended while the MCP job remained stuck. The cause of that cancellation was not established. Its diagnostic snapshot is `expanded-regression-incomplete.json`. The pending job was cleared after native execution ended, and editor options were restored. This attempt is not counted as an eight-test pass. The earlier completed five-test run and final completed two-test human run remain the verified results. The final fresh compilation and console read returned zero errors; the wider repeat regression remains unproven.

| Model | Walk left-foot lift | Run left-foot lift | Minimum sole height over sampled clips | Talk mesh motion |
| --- | ---: | ---: | ---: | ---: |
| Eric | 0.1616 m | 0.3802 m | -0.0005 m | 0.2985 m |
| Carla | 0.1260 m | 0.3202 m | 0.0045 m | 0.2994 m |
| Claudia | 0.1395 m | 0.3538 m | 0.0007 m | 0.2717 m |

Run legitimately includes airborne frames. At contact, the tested soles are within millimetres of the ground. These measurements are for the tested flat promenade positions and do not assert terrain-adaptive foot placement on every slope.

The primary images are real **Unity Game-view captures**, obtained with `ScreenCapture.CaptureScreenshot` in Play Mode and including the runtime HUD:

- `Eric_{Idle1,Idle2,Walk,Run,Talk}_game.png`
- `Carla_{Idle1,Idle2,Walk,Run,Talk}_game.png`
- `Claudia_{Idle1,Idle2,Walk,Run,Talk}_game.png`
- `natural_beachlife_promenade_game.png`
- `unity-editor-gameview-proof.png`: desktop evidence of the open Unity editor, active Play Mode, Game tab, runtime hierarchy and Eric's animated visual.

The captures were visually inspected: scan faces, hair and clothing are textured, no magenta scan materials are visible, upright animations are active and the feet are at the surface. `AssetGateF02/` also contains Unity camera renders at close/medium distances. Those camera renders are supplemental; the `_game.png` images provide the actual Game-view evidence. Existing regression capture files are redirected into this new root; ArtSource review PNGs are not overwritten.

## Files changed by this pass

- `FacilityOps/Assets/_Game/Scripts/Resort/Game/HumanVisual.cs`: three-model selection/cache, safe material guard, variant identification, scale/sole correction, scan foot IK and non-looping clip replay.
- `FacilityOps/Assets/_Game/Scripts/Resort/Game/PersonRig.cs`: only realistic eligibility and deterministic variant seed assignment.
- `FacilityOps/Assets/_Game/Scripts/Resort/Editor/RealisticHumanImport.cs` and `.meta`: narrowly scoped Humanoid/texture import policy for the local scan folder.
- `FacilityOps/Assets/_Game/Tests/PlayMode/RealisticHumanPassTests.cs` and `.meta`: runtime/retargeting/ground/material/selection validation and real Game-view capture.
- `FacilityOps/Assets/_Game/Tests/PlayMode/AssetGateF02Tests.cs`: existing source-mesh assertion now follows the actual selected variant rather than assuming every female scan is Carla.
- `Tools/Map/prepare_realistic_humans.py`: local promotion and provenance manifest generation.
- Ignored local `ThirdParty/Resources/RealisticHumans/`: Claudia FBX, three maps and their generated import metadata; promotion manifest. Unity refreshed scan import metadata as required by the import policy.
- New capture/evidence directory and this report.

The repository already had extensive uncommitted work on arrival, including these human source files. Changes above are measured against the incoming working files, not assumed to be the full Git diff. Incoming copies of HumanVisual.cs/PersonRig.cs and protected-file hashes were kept in `FacilityOps/Logs/HumanPassBaseline`. No reset, checkout, clean, revert or stash was used.

Final preservation check: **53 protected files match their incoming SHA256 values**, including all 46 ArtSource review PNGs and the seven explicitly reserved files. During editor/test serialization Unity normalized QualitySettings.asset from CRLF to LF without changing property values; its exact incoming bytes were restored only after verifying the CRLF reconstruction matched the recorded incoming hash. No lighting/shadow/quality values were edited. `protected-files-verification.json` records the final hashes. `capture-manifest.json` hashes the 29 newly captured PNGs. A temporary scene left by the aborted native runner was moved out of Assets into `Logs/HumanPassBaseline/RunnerArtifacts`; it was created during this pass and was absent on arrival. The Unity editor is left in Edit Mode with ResortPrologue open and its original play-mode options restored. `final-console.json` records zero final console errors.

## Remaining blockers and phase status

The three rigged adults have no remaining avatar/retargeting blocker for the tested upright clips. The broader human visual gate remains **OPEN**:

- Existing beach, active/sports and child looks still use earlier HBM/procedural visuals because these three approved scans have adult business/casual clothing. No new stylized or low-poly human asset was introduced or promoted.
- Sitting, lying, swimming, cycling and prop-specific gestures retain the existing procedural behavior. The approved HBM subset lacks the necessary matching clips. They were not faked with inappropriate scan poses.
- Far LOD and bodies beyond the existing active skinned cap retain the previous fallback representation. More extensive realistic crowd coverage and a measured whole-scene performance gate remain future visual work.
- Animated/posed Renderpeople archives remain local and unpromoted for runtime locomotion. Any later use requires its own avatar/clip validation.
- Only three identities are available in this approved rigged set; deterministic model choice and varied phases/states reduce synchronized clones but cannot provide a large identity roster.
- The expanded eight-test repeat regression was interrupted by a runner cancellation. Re-run it in a clean test-runner context before claiming a broader regression pass; the existing completed five-test and targeted two-test results are archived.

No global lighting, shadow pipeline, sky or water implementation was authored by this pass. Runtime tests exercised existing daylight behavior. Phase 03 remains untouched.
