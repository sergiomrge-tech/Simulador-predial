# Vertical Slice QA

FAIL

READY_FOR_USER_TEST = FALSE

| Item | Result | Detail |
| --- | --- | --- |
| compilation | PASS | Validated @ (0.00, 0.00, 0.00) |
| manifest | PASS | Validated @ (0.00, 0.00, 0.00) |
| references | PASS | Validated @ (0.00, 0.00, 0.00) |
| build_settings | PASS | Validated @ (0.00, 0.00, 0.00) |
| save_load | PASS | Validated @ (0.00, 0.00, 0.00) |
| legacy_rules | PASS | Validated @ (0.00, 0.00, 0.00) |
| navmesh | PASS | Validated @ (0.00, 0.00, 0.00) |
| colliders | PASS | 0 render meshes without colliders in physical layers @ (0.00, 0.00, 0.00) |
| markers | PASS | 150 unique marker names inspected @ (0.00, 0.00, 0.00) |
| portal_portão | FAIL | Capsule overlaps EXPORT_W2_horizonte__site @ (-2350.00, 27.03, -1827.50) |
| portal_portaria | FAIL | Capsule overlaps EXPORT_W2_horizonte__F00_lobby @ (-2350.00, 26.97, -1816.00) |
| spawn_Lar | PASS | Floor and clear capsule @ (-2860.00, 16.75, -2266.00) |
| spawn_Oficina | PASS | Floor and clear capsule @ (-2710.00, 20.67, -2150.00) |
| spawn_Horizonte | PASS | Floor and clear capsule @ (-2350.00, 27.03, -1831.00) |
| spawn_Mercearia | PASS | Floor and clear capsule @ (-2598.00, 24.68, -1480.00) |
| spawn_Prólogo | PASS | Floor and clear capsule @ (-2361.00, 37.12, -1800.00) |
| spawn | PASS | ID/marker-based physical floor and capsule probes @ (0.00, 0.00, 0.00) |
| route:Lar→Oficina | PASS | 242,5 m; cells: SA_M01_01_S00_02,SA_M01_01_S00_03,SA_M01_01_S01_03 @ (0.00, 0.00, 0.00) |
| route:Oficina→Horizonte | PASS | 516,7 m; cells: SA_M01_01_S01_03,SA_M01_02_S01_00,SA_M01_02_S02_00 @ (0.00, 0.00, 0.00) |
| route:Horizonte→portão | PASS | 3,2 m; cells: SA_M01_02_S02_00 @ (0.00, 0.00, 0.00) |
| route:portão→portaria | PASS | 137,4 m; cells: SA_M01_02_S02_00 @ (0.00, 0.00, 0.00) |
| route:portaria→4º andar | FAIL | NavMesh crosses physical wall: EXPORT_W2_horizonte__stair_F01 @ (-2347.10, 31.72, -1796.27) |
| route:4º andar→área técnica | PASS | 15,5 m; cells: SA_M01_02_S02_00 @ (0.00, 0.00, 0.00) |
| route:área técnica→portaria | FAIL | No physical floor with NavMesh coverage (gap or missing collision) @ (-2347.70, 35.73, -1794.60) |
| route:portaria→portão | PASS | 137,4 m; cells: SA_M01_02_S02_00 @ (0.00, 0.00, 0.00) |
| route:portão→Mercearia | PASS | 463,1 m; cells: SA_M01_02_S01_01,SA_M01_02_S01_02,SA_M01_02_S02_00,SA_M01_02_S02_01 @ (0.00, 0.00, 0.00) |
| route:Mercearia→Lar | FAIL | PathPartial @ (-2778.10, 19.53, -2163.90) |
| route_plan | FAIL | Continuous NavMesh legs; doors opened in reference pose, no links/proxy floors added @ (0.00, 0.00, 0.00) |
| cells | PASS | Validated @ (0.00, 0.00, 0.00) |
| editor_route | PENDING | Run continuous Play Mode test @ (0.00, 0.00, 0.00) |
| player | PENDING | Run Development Player @ (0.00, 0.00, 0.00) |

Route distance: 1545,0 m. NavMesh is a planning reference; only the continuous controller run proves physical traversal.
Fingerprint: `26E6096E2091917031D68DFB5522D848DA1112E7A66E4C560FC8732D0566D3C7`
