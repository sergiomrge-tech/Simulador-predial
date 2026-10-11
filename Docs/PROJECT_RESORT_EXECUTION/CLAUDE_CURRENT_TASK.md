# PROJECT RESORT — Tarefa Atual do Claude

Atualizado em 2026-10-10 (rodada Claude 43, branch `claude/w1-masterplan`).

## Fase atual

**Fase 02 — Vertical Slice do Quiosque** — gate técnico **PASS**; gate visual **ABERTO**; **HUMAN_GATE_PENDING** (jogada humana + olhar do Diretor).

A Fase 03 NÃO está liberada.

## Estado real verificado nesta rodada

- Havia um grande bloco de trabalho do Codex (2026-10-07 a 10-09) só no disco: mapa de **ilha de 2 km²** (2000×1000 m, passo 2 m), relevo costeiro, anel de oceano, vegetação/understory CC0 (Poly Haven), props urbanos CC0, ladrilhos de terreno (PhysX), integração vrbn local, quiosque com assets realistas, sombras mais fortes. HEAD == origin antes da rodada.
- Validação real do Unity 6000.6.2f1 (`Tools/Autonomy/Run-UnityResortTests.ps1 -Graphics`) sobre essa árvore: primeira execução **35/37** — as duas falhas eram testes legados com coordenadas fixas da planta de 900 m (`StagesTests.PiecesLineUpWithTheTerrainAndTheStageFollowsTheLand`, `PousadaInteriorTests.ThePlayerCanEnterTheReceptionAndClimbToTheFirstFloor`); o site migrado desloca o kit em +550 m no X (`ResortStages.LegacyKitOffsetX`). Testes corrigidos para usar o deslocamento.
- Execução final: **37/37 PASS (38 com o diagnóstico opt-in ignorado), UNITY_EXIT=0**, 0 `error CS`, 0 `Shader error`, 0 `NullReferenceException` — `D:\ProjectResort_Autonomy\logs\unity_PlayMode_20261010_211156.xml` (antes da otimização) e `unity_PlayMode_20261010_214359.xml` (final, 37 passed / 1 skipped).
- Nota de ambiente: com `RESORT_TEST_CAPTURE_ROOT` definido, 2 testes de `RealisticHumanPassTests` falham em `-batchmode` (`ScreenCapture.CaptureScreenshot` não grava em 0,15 s). Rode a suíte **sem** essa variável.
- Testes de `RealisticHumanPassTests` e `VRBNIntegrationTests` dependem de pacotes licenciados locais (`Assets/_Game/ThirdParty/`, `Assets/vrbn_studios/`, git-ignorados); em um clone limpo esses testes não passam (o jogo cai nos fallbacks).
- Desempenho (render em lote, sem IMGUI), mapa de 2 km²: a primeira medição mostrou regressão (estágio 1 ao nível do chão 19 ms). **Causa medida** (teste opt-in `PerformanceTests.DiagnosticLeaveOneOutBreakdown`, `RESORT_PERF_DIAG=1`): as árvores Poly Haven tinham LODs de 128k/37k/11k (island_tree_02) e 144k/50k/50k (tree_small_02) triângulos; `RealisticCoastalVegetation` respondia por ~17 ms de 22. Correção: LOD1/LOD2 re-derivados por `Tools/Blender/relod_vegetation.py` (~22k/~8k tris; LOD0 mantido), limiares de LOD mais agressivos (.22/.06/.016) e LOD final vazio (cull < 0,6% da tela) em `CoastalVegetation.Tree`. Folhas escaneadas (quase pretas) clareadas no tom base. Resultado (2 execuções consistentes): praia meio-dia 6,0 ms (p95 6,9), estágio 1 aérea 9,4 / chão 9,2 ms, estágio 7 aérea 7,5 / chão 6,4 / eixo 5,5 ms — todos ≥ 100 fps em lote. As câmeras do `PerformanceTests` agora somam `LegacyKitOffsetX` (antes apontavam para fora do hotel). Backup dos FBX antigos: `D:\ProjectResort_Autonomyackupegetation_lods_20261010`. Medição em lote nesta máquina, sem hardware-alvo.
- Commits desta rodada (push em `origin/claude/w1-masterplan`): ignore de bundles locais; ilha 2 km² + código + testes; assets CC0; docs; otimização de LOD de árvores.
- **Rodada 43**: capturas reais da ilha nova (dia/tarde/pôr do sol/noite, `ArtSource/Blender/World/Reviews/F02/`) conferidas visualmente — o dia está coerente; a noite tinha céu/horizonte/mar quase pretos. Ajuste de apresentação em `DayNightCycle.Apply`: horizonte noturno (0,04,0,07,0,14)→(0,075,0,115,0,22), zênite (0,025,0,05,0,13)→(0,04,0,075,0,185), luz da lua 0,56→0,72. Luminância média noite (kiosque/mar/mesas/calçadão/aérea): 0,086/0,168/0,241/0,080/0,176. Suíte completa 37/37 (1 skip opt-in), UNITY_EXIT=0, 0 `error CS`/`Shader error`/NRE — `unity_PlayMode_20261010_215325.xml`. Melhoria modesta: o céu noturno continua muito escuro olhando para o mar (a lua fica fora do enquadramento); o julgamento de beleza noturna é do olhar humano.
- Fora do commit de propósito: PNGs de `ArtSource/Blender/World/Reviews/` (regenerados a cada run), `ProjectSettings/*` com ruído do Unity (ps4Passcode, TimeManager), `Packages/manifest*.json` (só o plugin MCP), `vrbn_studios/`, `MCPForUnity/`, `FacilityOps/Captures/` (2 GB).

## Pendente

1. **HUMAN_GATE_PENDING**: uma pessoa precisa jogar dois dias (`ROTEIRO_PLAYTEST_HUMANO_FASE_02.md`) e avaliar ritmo, HUD, diversão, áudio e as capturas reais.
2. Gate visual aberto (ver `CODEX_PROMENADE_LAMPS_2026-10-07.md`): palmeiras/pessoas visíveis, lotes esparsos, contraste de fachada/noite, manequins/guarda-sóis ainda blockout, desempenho standalone.
3. Gate de coerência visual (`RESORT_VISUAL_COHESION_GATE_20261007.md`): todos os assets devem ter o mesmo estilo; vrbn é banco de candidatos (status `CANDIDATE/HOLD/APPROVED_ON_SCENE`).

## Trabalho seguro dentro da Fase 02 (próxima rodada)

- Restam 2400 `GroundCover` + 3040 understory como renderers individuais (~1–2 ms): combinar por célula/instancing se a Fase 16 pedir mais folga.
- Capturas reais de dia/pôr do sol/noite da ilha nova (rodar com a variável de capturas somente nos testes de captura da cena, nunca em `RealisticHumanPassTests`).

## O que NÃO fazer

- não iniciar a Fase 03;
- não construir pousada/hotel/resort novos;
- não chamar blockout de arte final;
- não marcar o gate visual/humano como PASS sem uma pessoa jogar;
- não commitar `vrbn_studios/`, `ThirdParty/`, `Captures/` nem pacotes brutos da Asset Store.

## Histórico resumido

- Rodadas 1–21 (2026-10-06): loop completo, praia viva com LOD/pooling, dia/noite, mar/céu/nuvens com shader próprio, atividades ambientes, HUD de próximo passo — ver `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md` (adendos 1–11).
- Rodadas 22–41: reconfirmações sem trabalho novo (HUMAN_GATE_PENDING).
- Codex 2026-10-07/10-09: passe PBR, móveis CC0, calçadão, lâmpadas, vegetação, ilha 2 km² — ver `CODEX_F02_CONTINUATION_2026-10-07.md`, `CODEX_F02_REALISTIC_FURNITURE_2026-10-07.md`, `CODEX_PROMENADE_LAMPS_2026-10-07.md`, `CODEX_URBAN_*`.
