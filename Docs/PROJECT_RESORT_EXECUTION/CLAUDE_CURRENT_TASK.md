# PROJECT RESORT — Tarefa Atual do Claude

Atualizado em 2026-10-10 (rodada Claude 42, branch `claude/w1-masterplan`).

## Fase atual

**Fase 02 — Vertical Slice do Quiosque** — gate técnico **PASS**; gate visual **ABERTO**; **HUMAN_GATE_PENDING** (jogada humana + olhar do Diretor).

A Fase 03 NÃO está liberada.

## Estado real verificado nesta rodada

- Havia um grande bloco de trabalho do Codex (2026-10-07 a 10-09) só no disco: mapa de **ilha de 2 km²** (2000×1000 m, passo 2 m), relevo costeiro, anel de oceano, vegetação/understory CC0 (Poly Haven), props urbanos CC0, ladrilhos de terreno (PhysX), integração vrbn local, quiosque com assets realistas, sombras mais fortes. HEAD == origin antes da rodada.
- Validação real do Unity 6000.6.2f1 (`Tools/Autonomy/Run-UnityResortTests.ps1 -Graphics`) sobre essa árvore: primeira execução **35/37** — as duas falhas eram testes legados com coordenadas fixas da planta de 900 m (`StagesTests.PiecesLineUpWithTheTerrainAndTheStageFollowsTheLand`, `PousadaInteriorTests.ThePlayerCanEnterTheReceptionAndClimbToTheFirstFloor`); o site migrado desloca o kit em +550 m no X (`ResortStages.LegacyKitOffsetX`). Testes corrigidos para usar o deslocamento.
- Execução final: **37/37 PASS, UNITY_EXIT=0**, 0 `error CS`, 0 `Shader error`, 0 `NullReferenceException` — `D:\ProjectResort_Autonomy\logs\unity_PlayMode_20261010_211156.xml`.
- Nota de ambiente: com `RESORT_TEST_CAPTURE_ROOT` definido, 2 testes de `RealisticHumanPassTests` falham em `-batchmode` (`ScreenCapture.CaptureScreenshot` não grava em 0,15 s). Rode a suíte **sem** essa variável.
- Testes de `RealisticHumanPassTests` e `VRBNIntegrationTests` dependem de pacotes licenciados locais (`Assets/_Game/ThirdParty/`, `Assets/vrbn_studios/`, git-ignorados); em um clone limpo esses testes não passam (o jogo cai nos fallbacks).
- Desempenho (render em lote, sem IMGUI), mapa de 2 km²: praia ao meio-dia 5,7 ms média / 6,7 p95 / 7,1 pior (76 pessoas, 102 lâmpadas) — antes 2,8 ms; estágio 7 ao nível do chão 17,3 ms (58 fps) / p95 18,0; estágio 1 ao nível do chão 15,5 ms. **Regressão de ~2× em relação ao mapa de 900 m**; ainda dentro de 60 fps nessa máquina, mas é o item de otimização mais importante antes da Fase 16 (e para o gate de "performance" da Fase 02).
- Commits desta rodada (push em `origin/claude/w1-masterplan`): ignore de bundles locais; ilha 2 km² + código + testes; assets CC0.
- Fora do commit de propósito: PNGs de `ArtSource/Blender/World/Reviews/` (regenerados a cada run), `ProjectSettings/*` com ruído do Unity (ps4Passcode, TimeManager), `Packages/manifest*.json` (só o plugin MCP), `vrbn_studios/`, `MCPForUnity/`, `FacilityOps/Captures/` (2 GB).

## Pendente

1. **HUMAN_GATE_PENDING**: uma pessoa precisa jogar dois dias (`ROTEIRO_PLAYTEST_HUMANO_FASE_02.md`) e avaliar ritmo, HUD, diversão, áudio e as capturas reais.
2. Gate visual aberto (ver `CODEX_PROMENADE_LAMPS_2026-10-07.md`): palmeiras/pessoas visíveis, lotes esparsos, contraste de fachada/noite, manequins/guarda-sóis ainda blockout, desempenho standalone.
3. Gate de coerência visual (`RESORT_VISUAL_COHESION_GATE_20261007.md`): todos os assets devem ter o mesmo estilo; vrbn é banco de candidatos (status `CANDIDATE/HOLD/APPROVED_ON_SCENE`).

## Trabalho seguro dentro da Fase 02 (próxima rodada)

- Perfilar e reduzir o custo de render do mapa de 2 km² (culling por célula da vegetação/understory, instancing, LOD de props urbanos, sombra a 120 m) e remedir com `PerformanceTests`; meta: voltar a ≤ 4 ms na praia ao meio-dia e ≤ 10 ms no estágio 7 ao nível do chão.
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
