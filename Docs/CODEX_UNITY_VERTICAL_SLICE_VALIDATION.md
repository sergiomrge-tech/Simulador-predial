# Validação Unity — Cidade Antiga Vertical Slice v0.1

Data: 04/10/2026. Resultado global: **APROVADO no gate físico a pé, com as limitações listadas** (a escada do Horizonte deixou de bloquear; build Windows x64 Development gerado).

Branch: `codex/unity-world-integration-validation`, isolada de `main`, `claude/w1-masterplan` e `gpt/unity-world-integration`. Base: `a5ea6c07cbac6494e94ffae037cc55b694efb85a`. Nenhum merge foi solicitado ou feito. A publicação anterior pelo conector GitHub não chegou a existir no remoto (a branch não estava listada); o push desta versão cria a branch.

Este documento reúne duas etapas: o trabalho do Codex (importação, validadores, streaming, bloqueio da escada) e a correção do bloqueio, feita depois com autorização explícita para alterar a geometria autoral do Horizonte.

## 1. Bloqueio da escada: causas e correção

O NavMesh de referência (construído só dos colliders importados, sem links) devolvia `PathPartial` da rua ao corredor do prólogo. A investigação encontrou **cinco causas independentes**; só resolvendo todas o jogador real (CharacterController, raio 0,28 m, altura 1,8 m) chega ao 4º andar:

| # | Causa | Evidência | Correção (geometria autoral, não colisão artificial) |
| --- | --- | --- | --- |
| 1 | A laje de cada piso era um único bloco da planta inteira: a escada em U batia na laje do andar de cima. | `mb.box(0, 0, za, W - .05, D - .05, .15, …)` em `create_w2_hero_horizonte.py`; as sondas de raio mostravam laje sobre os dois lances. | A laje dos pisos 1+ é montada em torno de uma abertura de caixa de escada (`STAIR_HOLE`), derivada da posição da escada: cobre os dois lances e o patamar de giro. |
| 2 | Faixa de chegada/entrada de só 0,30 m entre a parede do núcleo e o primeiro degrau (a erosão do agente de 0,28 m a eliminava). | Diagnóstico de trechos: cada piso chegava ao topo do lance 2 e parava; “dentro→1º degrau” parcial. | Escada deslocada 0,90 m (`STAIR_Y0 = CORE[1] + 1.4`): 1,2 m de patamar de chegada/entrada em todos os pisos. |
| 3 | Os degraus do lance 1 eram blocos maciços do piso até o topo, então a face inferior do lance de cima ficava plana na cota do piso: sobravam ~1,5 m sobre a metade alta de cada lance dos pisos de 3 m (controlador: 1,8 m). | Geometria (altura livre = pé-direito − cota do degrau); só o térreo (4 m) tinha 2,0 m. Esta causa foi deduzida da geometria e corrigida junto com as demais, sem experimento isolado. | `stair_u(..., hollow=True)` só no Horizonte: degraus vazados com forro escalonado; a altura livre vira o pé-direito menos a espessura do degrau. O padrão `hollow=False` mantém as demais escadas (Lar etc.) idênticas. |
| 4 | As portas da escada eram folhas fechadas (o jogo não tem interação de porta) com vão de 1,0 m e verga a 2,10 m. | NavMesh parcial no vão; depois, em Play Mode, o jogador parava no vão com `OnControllerColliderHit` na verga (y = 29,15 m): a folga de 0,21 m era menor que o `stepOffset` de 0,30 m do controlador. | Vão de **1,20 m × 2,40 m**, folha autoral **aberta a 90°**, articulada no batente oeste e voltada para o corredor. Articulada para dentro da caixa ou no batente leste, a folha obstruía o patamar em um dos pisos (verificado com o NavMesh). |
| 5 | Os pontos de caminhada do QA colavam no batente (o NavMesh não conhece o `skinWidth` de 0,08 m). | Capsule cast e mapa de raios no ponto de travamento: só o raio a +0,35 m tocava o alizar. | O caminhante do Play Mode reamostra a linha a cada 0,5 m e recentraliza (raios laterais, deslocamento ≤ 0,3 m), a 60 Hz fixos. O raio do agente do NavMesh **continua 0,28 m**: um agente de 0,36 m quebrava a rota do painel, que o controlador percorre sem problema. |

Código: `Tools/Blender/create_w2_hero_horizonte.py`, `Tools/Blender/sa_detail.py` (parâmetro `hollow`). O herói `W2_horizonte.blend` foi regenerado, `horizonte.fbx` reexportado e a importação refeita (`WorldSliceImportPipeline.ImportPilot`). A fonte congelada `SantaAurora_W3_VerticalSlice.blend` **não mudou** (SHA256 `EAFE4C1F…F9C7`). Nenhum piso invisível, link de navegação, remoção de colisão ou teleporte foi usado para forçar a aprovação.

**A correção está só nesta branch.** O `W2_horizonte.blend` de `claude/w1-masterplan` tem o mesmo defeito (laje sem abertura, portas fechadas de 1,0 × 2,1 m); a correção precisa ser portada lá por quem mantém a arte.

## 2. Validação em Play Mode (CharacterController real)

Novo gate `WorldSliceStairWalkGateTests` (opt-in `FACILITY_STAIR_QA=1`; relatório `Docs/ValidationEvidence/world-stair-walk-qa.json`, exigido por `WorldSliceBuildGate`): o `FirstPersonController` sai da rua em frente ao Horizonte e segue a linha da rua ao quadro técnico, a 3 m/s, com gravidade, em passos fixos de 1/60 s; o NavMesh só fornece a linha. O prólogo é aceito antes (a mesma pré-condição do gate de runtime), para o painel responder pela lógica original.

| Critério | Resultado |
| --- | --- |
| Trajeto | 185 m (386 pontos reamostrados), 3.599 frames simulados ≈ 60 s |
| Altura vencida | 10,09 m (4º andar), por todos os lances |
| Penetração dos colliders (cápsula de 0,2 m) | **0 frames** |
| Perda de contato com o chão | 5 frames no total, sequência máxima de 4 |
| Maior distância pé–piso | 0,57 m (descida de degraus; limite do gate: 0,70 m) |
| Travamento (sem progresso por 6 s simulados) | **0 ocorrências** |
| Distância final ao ponto de aproximação | 0,30 m |
| Raycast + interação | `TechnicalStation`; a lógica original do prólogo respondeu `QD-01` |

Marcos (tempo simulado): primeiros degraus 52,5 s; patamar do 1º lance 53,7 s; piso 1 54,6 s; 4º andar 58,5 s.

**Observação de acessibilidade (não corrigida):** a rota não usa o portão de pedestres do Horizonte (folha fechada, sem interação com o interfone). Ela entra pelo portão de veículos, sobe a rampa da garagem e dá a volta até o saguão: ~152 m só até a porta da escada. É o que os colliders atuais permitem; o jogo precisa de uma interação de interfone/portão (ou do portão autoral aberto) para o trajeto natural.

## 3. Gates e testes

| Verificação | Resultado | Evidência |
| --- | --- | --- |
| Preflight e FBX de 15 células, quatro heróis, materiais e markers | PASS | `ArtSource/Blender/World/UnityExport` |
| Importação do corredor (15 células, 4 heróis) com o Horizonte corrigido | PASS (~76 s em batch) | `WorldSliceImportPipeline.ImportPilot` |
| NavMesh de referência (505 fontes, 18,7 s de bake, raio 0,28 / altura 1,8) | **PASS — 5/5 rotas `PathComplete`**, inclusive rua→prólogo e spawn→quadro | `world-walkability-qa.json` |
| Suíte EditMode completa (`-worldSlice -worldSliceQa`) | 26 casos: **24 PASS, 0 FAIL, 2 IGNORE** (os dois opt-ins abaixo) | `EditMode-final.xml` |
| Gate de runtime (streaming, cargas/descargas, markers, spawn→quadro, QD-01) | PASS | `world-runtime-qa.json` |
| Gate da escada (Play Mode, CharacterController) | PASS | `world-stair-walk-qa.json`, `Stair-Walk.xml` |
| Modo normal sem `-worldSlice` | PASS 1/1 | `Normal-Mode.xml` |
| Lar: aterrissagem e 7,2 m de caminhada | PASS 1/1 | `Lar-PlayMode.xml`, `lar-playmode-gate.txt` |
| Manifesto, cenas, Build Settings, regras antigas do `ProjectBuilder` (runtime antigo e save), `WorldIntegrationQa` | PASS (repetidos no comando de build) | `world-integration-qa.json` |
| `WorldSliceBuilder.Build` | gates exigidos e satisfeitos; build gerado | `build-summary.txt` |

Os dois IGNORE são os gates opt-in do Lar e do modo normal, executados e aprovados em rodadas próprias. O aviso “Save principal indisponível: JSON parse error” no log do build vem da regra do `ProjectBuilder` que corrompe de propósito um save temporário para provar a recuperação por `.bak`; nenhum save do jogador foi lido ou alterado.

## 4. Métricas

**Player: Windows x64 Development, 1280×720, Direct3D 11, NVIDIA GeForce RTX 4060 Ti, Unity 6000.6.2f1** (`player-tour-qa.json`; `-worldSlice -worldSliceQa -worldSliceQaTour`). Escopo: o jogador **parado** após cada teleporte e carga de células, 8 s por amostra; **não é caminhada contínua nem ensaio longo**.

| Amostra | Células | FPS médio | p99 do frame (ms) | Maior frame (ms) | Maior frame na carga (ms) | Memória usada / reservada (MiB) | GC por frame (B) | SetPass | Tris visíveis |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Lar | 4 | 60,0 | 16,7 | 16,8 | **75,8** | 206,9 / 815,7 | 2.879 | 43 | 3,14 M |
| Oficina | 9 | 60,0 | 16,7 | 16,9 | 16,9 | 265,9 / 1.091,7 | 2.333 | 45 | 8,22 M |
| Horizonte | 11 | 60,0 | 16,8 | 17,3 | 16,9 | 285,0 / 1.091,7 | 2.343 | 42 | 5,13 M |
| Mercearia | 9 | 60,0 | 16,7 | 16,8 | 17,0 | 319,9 / 1.091,7 | 2.326 | 45 | 8,20 M |
| Lar (retorno) | 7 | 60,0 | 16,7 | 17,5 | 16,8 | 321,6 / 1.091,7 | 2.342 | 43 | 3,14 M |

- Operações de streaming no Player: **carga máxima 409 ms**, **descarga máxima 252 ms**; 19 cargas e 12 descargas, sem cena duplicada.
- O FPS de 60,0 é o teto do V-Sync: **não indica folga**. Sem teste com V-Sync desligado ou em máquina-alvo, não há afirmação de desempenho além de “não caiu abaixo de 60 nesta cena com o jogador parado”.
- **Draw calls e batches: indisponíveis.** Os contadores `Draw Calls Count` e `Batches Count` do `ProfilerRecorder` devolveram 0 neste Player (provável efeito do SRP Batcher/URP); isso **não** é ausência de geometria. Os valores válidos são **SetPass Calls (42–45)** e **triângulos (3,1–8,2 M)**.
- O maior hitch do Player (75,8 ms) foi a carga inicial a frio do Lar. O Editor teve um hitch de ~21 s no primeiro ensaio com shaders frios e não é referência de Player.

**Editor (Play Mode, gate de runtime, `world-runtime-qa.json`)**: 4–11 células carregadas, memória usada 680–1.318 MiB, reservada até 2.264 MiB, GC 98–865 KB/frame (inclui test runner e capturas), carga máxima 678 ms, descarga 369 ms, maior frame 633,8 ms; draw calls/tris do `ProfilerRecorder` do Editor retornaram 0. Esses números incluem test runner, Editor e capturas e **não substituem os do Player**.

Pendente para o gate físico: perfil em máquina-alvo, V-Sync desligado, caminhada contínua pela cidade, ensaio longo de memória/vazamento e draw calls/batches válidos (Frame Debugger ou profiler do Player).

## 5. Capturas reais (Unity, Play Mode)

PNG 1280×720 via `RenderPipeline.SubmitRenderRequest`/URP da câmera do jogador, com o overlay de streaming visível. Nada renderizado no Blender foi usado como evidência de runtime. Em `Docs/Previews/UnityValidation/`:

- Lar: `home-starter-runtime.png`, `Lar-runtime.png`
- Rua: `street-runtime.png`, `Lar-street-runtime.png`
- Oficina: `garage-runtime.png`
- Horizonte exterior: `horizonte-runtime.png`, `horizonte-exterior-walk-runtime.png` (início da caminhada)
- Escada do Horizonte: `horizonte-escada-base-runtime.png`, `horizonte-escada-meio-runtime.png`, `horizonte-escada-1andar-runtime.png`, `horizonte-escada-topo-runtime.png` (chegada ao 4º andar, com a porta autoral aberta)
- Horizonte, área técnica: `horizonte-corridor-runtime.png`, `horizonte-panel-runtime.png`, `horizonte-panel-stair-walk-runtime.png`
- Mercearia: `grocery-runtime.png`
- Overlay de streaming: visível nas capturas do Editor (o overlay do Player foi medido pelo relatório, não por imagem).

As capturas mostram a taxa de quadros do Editor em batch (≈12,6 FPS durante a captura), que não representa o Player.

## 6. Build

`Facility Ops — Cidade Antiga Vertical Slice v0.1`, **Windows x64 Development**, 16 cenas (bootstrap + 15 células), 0 erros, 3 avisos, `-worldSlice`. Gerado em `Builds/Windows/CidadeAntiga_v0_1/FacilityOps_CidadeAntiga_v0_1.exe` (pasta ignorada pelo git; ~681 MB). `Jogar_CidadeAntiga.bat` inicia com `-worldSlice`. O build foi executado e a medição da seção 4 foi feita nele.

## 7. Fonte congelada, ferramentas e correções anteriores do Codex

- Unity **6000.6.2f1**; Blender **5.2.1 LTS**; Unity CLI **1.0.0-beta.12** (`run` e `test`).
- Fonte: `ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend`; SHA256 inalterado `EAFE4C1F12E597365CCE3F77345FC9107B4DA5825621912C2F4908840781F9C7`. Os heróis vêm das referências W2 ligadas ao W3; o único `.blend` alterado é `W2_horizonte.blend` (seção 1).
- Já feito pelo Codex: string multilinha inválida em `TabletUI.cs` (`CS1010`); exportação FBX compatível com o Blender 5.2; manifests com bounds de origem; materiais PBR com recorte alpha das folhas; exportação filtrável de markers, com rejeição de duplicatas antes de criar objetos; `WorldSliceImportPipeline` atômico e sem diálogos; Build Settings validados; streaming com prioridade da célula central e reconciliação de pedidos fora de ordem; bridge que preserva o runtime original até a célula carregar; painel autoral do Horizonte ligado a `TechnicalStation/Distribution`; sol global no bootstrap; overlay uGUI capturável; `-worldSliceQa` com carreira e save exclusivos (`FacilityOps/QA/world-slice-career.json`).
- `WorldSliceBuilder.Build` exige os gates de runtime, caminhabilidade e **escada** com o fingerprint dos assets e scripts; relatório ausente, falho ou desatualizado interrompe o comando antes do `BuildPipeline.BuildPlayer`.
- Novo nesta etapa: `WorldSliceQaTour` (medição opt-in no Player Development, `-worldSliceQaTour`), contadores de batches e SetPass no overlay, e `WorldSliceWalkabilityQa.DiagnoseHorizonteStair` (trechos da rota e sondas de colisão).

## 8. Limitações restantes

1. **Portão de pedestres do Horizonte** fechado, sem interação (seção 2): a rota a pé entra pelo portão de veículos.
2. A porta da escada é um estado **autoral aberto** (calço); o jogo ainda não tem interação de porta. A mesma correção precisa ser portada ao `W2_horizonte.blend` de `claude/w1-masterplan`.
3. A medição do Player é de jogador parado, com V-Sync a 60 Hz e sem draw calls/batches válidos; falta perfil na máquina-alvo e ensaio longo.
4. Colliders são MeshColliders detalhados de QA (o gate da escada depende deles) e precisam de simplificação autoral/perfil antes de produção.
5. O shader procedural de terreno e certos efeitos de desgaste do Blender continuam simplificados no URP; não há equivalência visual completa com o Blender.
6. O bridge integra só o quadro QD-01; a migração dos demais equipamentos e feedbacks da campanha ao cenário autoral continua pendente. O runtime antigo permanece intacto.
7. A escada e o corredor aparecem escuros nas capturas: não há iluminação interior no URP (só o sol global); é pendência de arte/iluminação, não de colisão.
8. IDs dos markers críticos inalterados: `W2_horizonte__GP_prologue_spawn_corridor` em `(-2361, 37.951012, -1800)` e `W2_horizonte__GP_quadro_tecnico` em `(-2345.5, 38.451012, -1799.300049)`.

## 9. Reprodução

Com Blender e a versão Unity instalada, no root do repositório (PowerShell):

```powershell
# Horizonte (herói) após alterar a geometria autoral
blender -b --factory-startup --python Tools/Blender/create_w2_hero_horizonte.py -- --root <repo>
blender -b ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend --python Tools/Blender/export_unity_hero_fbx.py -- --root <repo> --hero horizonte
unity run ./FacilityOps -- -executeMethod FacilityOps.Editor.WorldSliceImportPipeline.ImportPilot
unity run ./FacilityOps -- -executeMethod FacilityOps.Editor.WorldSliceWalkabilityQa.BuildReference
$env:FACILITY_WORLD_QA='1'; $env:FACILITY_STAIR_QA='1'
unity test ./FacilityOps --mode EditMode --output ./Logs/EditMode-final.xml -- -worldSlice -worldSliceQa
Remove-Item Env:FACILITY_WORLD_QA, Env:FACILITY_STAIR_QA
$env:FACILITY_NORMAL_QA='1'; unity test ./FacilityOps --mode EditMode --filter WorldSliceNormalModeTests --output ./Logs/Normal-Mode.xml -- -worldSliceQa; Remove-Item Env:FACILITY_NORMAL_QA
$env:FACILITY_LAR_QA='1'; unity test ./FacilityOps --mode EditMode --filter WorldSliceLarGateTests --output ./Logs/Lar-PlayMode.xml; Remove-Item Env:FACILITY_LAR_QA
unity run ./FacilityOps -- -executeMethod FacilityOps.Editor.WorldSliceBuilder.Build
# Medição no Player (Development)
.\Builds\Windows\CidadeAntiga_v0_1\FacilityOps_CidadeAntiga_v0_1.exe -worldSlice -worldSliceQa -worldSliceQaTour -screen-width 1280 -screen-height 720 -screen-fullscreen 0
```

O NavMesh de referência e os saves de QA são descartáveis e ignorados. `Library`, caches, logs completos e builds não são publicados; evidências selecionadas ficam em `Docs/ValidationEvidence`.
