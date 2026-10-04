# Facility Ops — Cidade Antiga Vertical Slice v0.1 (build técnico)

Branch `gpt/unity-world-integration` · fonte visual `claude/w1-masterplan @ f3e55ed3a694577be78a502c6929ef500df8ce5f` (W3.2) · Unity 6000.6.2f1 · Windows x64 Development. **Build de teste técnico, não demo final**; a arte continua sendo massing/blockout refinado do W3.2.

## O que foi integrado
- Fonte W3.2 trazida seletivamente (só `W2_horizonte.blend` corrigido e geradores), sem merge da branch Claude. IDs, `GP_`/`SLOT_`/`PROXY_`, `facility_id` e escala 1:1 preservados (`scale-axes-audit.json`: PASS).
- 15 sub-células reexportadas do W3 (por camada) e importadas nas 15 cenas aditivas (`WorldSliceImportPipeline.ImportPilot`: PASS, 15 células, 4 heróis).
- **Carros** exportados como grupos LOD (LOD0/LOD1/proxy, `Props_Vehicles.fbx` por célula; 33–85 carros por célula) com `LODGroup` (0,06 / 0,02 / 0,006) e `BoxCollider` do mesh LOD0 — `Props.fbx` deixou de carregar os carros (menos 40–50 MB por célula). Correção importante: uma caixa derivada de bounds de mundo inflava carros girados e bloqueava a rota (NavMesh `PathPartial`); agora usa os bounds do mesh no espaço do carro.
- **Portão de pedestres do Horizonte**: folha separada na exportação do herói, `WorldDoor` + interfone (`WorldDoorRemote`); evita o desvio de ~152 m.
- **Portas** (`WorldDoor`): fechadas por padrão, `[E]` abre/fecha, folha fechada não é atravessável (MeshCollider da folha, corpo cinemático), nunca fecha sobre o jogador (recusa/reabre), portas da escada fecham sozinhas depois de 20 s com o jogador longe (portão: 30 s).
- Spawn no Lar, destinos Oficina/Horizonte/Mercearia e quadro técnico (QD-01) ligados pelo `WorldSliceRuntimeBridge`.

## Validações (todas executadas)
| Gate | Resultado |
| --- | --- |
| EditMode (26 testes) | 22 aprovados, 0 falhas, 4 opt-in (rodados individualmente abaixo) |
| `WorldIntegrationQa` / manifest / validadores de cena / marcadores | PASS (`ImportPilot` + testes de exportação) |
| Walkability (NavMesh dos colliders importados, raio 0,28 / altura 1,8, sem links sintéticos) | PASS, 5/5 rotas `PathComplete` |
| Runtime gate (streaming 3×3/5×5, Horizonte, quadro) | PASS |
| Escada a pé (CharacterController real) | PASS: subida de 10,09 m, 0 penetrações, 0 travamentos, interação QD-01 |
| Lar / modo normal | PASS / PASS |
| **Caminhada contínua no Player** (Lar → rua → Oficina → rua → Horizonte → interfone/portão → portaria → escada → 4º andar → quadro → saída → Mercearia → retorno ao Lar) | **PASS**: 2802 m, 947 s, 0 penetrações, 0 travamentos, 3 portas abertas por interação real, tablet abre/fecha, save/load verificado 2× (após QD-01 e após o retorno) |

Relatórios brutos em `Docs/ValidationEvidence/UnityVerticalSliceV01/`.

## Desempenho (Player Development, 1920×1080, RTX 4060 Ti)
vsync limita a 60 FPS: **não há afirmação de folga**. Memória é a do runtime Unity (usada / reservada, MiB).

| Trecho | s | FPS médio / mín | frame ms médio / máx | memória | GC B/frame | SetPass |
| --- | --- | --- | --- | --- | --- | --- |
| start | 7 | 60.0 / 57.6 | 16.67 / 17.4 | 318 / 1104 | 10970 | 67 |
| 02 Lar -> rua -> Oficina | 82 | 60.0 / 57.0 | 16.67 / 17.5 | 348 / 1106 | 2793 | 65 |
| 03 Oficina -> rua -> Horizonte | 173 | 60.0 / 57.4 | 16.67 / 17.4 | 363 / 1108 | 2750 | 53 |
| 04 Horizonte: portÃ£o | 50 | 60.0 / 57.5 | 16.67 / 17.4 | 365 / 1112 | 3055 | 63 |
| 05 Horizonte: escada e 4Âº andar | 15 | 60.0 / 57.8 | 16.67 / 17.3 | 365 / 1112 | 3050 | 58 |
| 06 saÃ­da do Horizonte | 59 | 60.0 / 57.8 | 16.67 / 17.3 | 365 / 1114 | 3464 | 66 |
| 07 Horizonte -> Mercearia | 155 | 60.0 / 52.6 | 16.67 / 19.0 | 409 / 1114 | 3358 | 58 |
| 08 Mercearia -> Lar | 404 | 60.0 / 52.3 | 16.67 / 19.1 | 413 / 1114 | 3342 | 56 |

- Células carregadas 23, descarregadas 14, máx. 13 simultâneas; carga máx. 537 ms e descarga máx. 452 ms (assíncronas; nenhum quadro acima de 33 ms nos trechos, pior quadro 19,1 ms).
- **Draw calls / batches: indisponível** (os contadores de ProfilerRecorder retornam 0 no Player; não são registrados como zero). SetPass e triângulos são válidos; a contagem de triângulos inclui passes de sombra (pico ~44 M).
- Nenhuma qualidade visual foi reduzida; sem gargalo identificado a 60 FPS, a otimização (LOD de arquitetura, oclusão, orçamento de triângulos de sombra) fica como próxima etapa.

## Capturas reais (`Docs/Previews/UnityVerticalSliceV01/`)
01-lar, 02-rua, 03-oficina, 04-horizonte-chegada, 05-portao, 06-portaria, 07-escada, 08-patamar, 09-4andar, 10-quadro, 11-saida, 12-mercearia, 13-streaming-overlay, 14-performance, 15-retorno-lar. Geradas pelo Player, em 1920×1080.

## Problemas conhecidos
- Acabamento visual ainda de blockout/massing; interiores com iluminação básica.
- Overlay de debug sobrepõe o HUD nas capturas (modo QA).
- Contadores de draw calls/batches indisponíveis no Player; triângulos de sombra altos.
- A rota de retorno é caminhada em três trechos (o NavMesh recusa uma única consulta de ~800 m como `PathPartial`).
- `Props` de cada célula ainda usa MeshCollider só em Terrain/Roads/Architecture; carros e props usam caixas/sem colisão.

## Reproduzir
`Tools`: ImportPilot → `WorldSliceWalkabilityQa.BuildReference` → `WorldSliceWalkRouteBuilder.Build` → gates (EditMode com `FACILITY_WORLD_QA`/`FACILITY_STAIR_QA`) → `WorldSliceBuilder.Build` → `Builds/Windows/CidadeAntiga_v0_1/Jogar_CidadeAntiga.bat` (ou `-worldSlice -worldSliceQa -worldSliceQaWalk` para o autopiloto). O build (1,28 GB) não é versionado.
