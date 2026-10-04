# W3.2 — Correção da escada do Edifício Horizonte

Data: 2026-10-04 · Branch: `claude/w1-masterplan` · Escopo: **só** `W2_horizonte.blend` (gerador `create_w2_hero_horizonte.py` + um parâmetro opcional em `sa_detail.Kit.stair_u`). O polimento visual está congelado: nenhum bairro, prédio ou melhoria geral novos. Unity, saves, código de gameplay e `gpt/unity-world-integration` não foram tocados.

## Defeito

Foi detectado na validação real na Unity (`Docs/CODEX_UNITY_VERTICAL_SLICE_VALIDATION.md`, branch `codex/unity-world-integration-validation`): o NavMesh dos colliders importados não ligava a rua ao corredor do prólogo (4º andar) e, depois, o `CharacterController` do jogo travava na escada. A causa estava na geometria autoral do herói, em cinco pontos:

| # | Defeito no `W2_horizonte.blend` | Efeito |
| --- | --- | --- |
| 1 | A laje de cada piso era um único bloco da planta inteira, sem abertura de caixa de escada. | A escada em U batia na laje do andar de cima: altura livre de 0,14 m sobre os degraus (medido, seção “Verificação”). |
| 2 | Só 0,30 m de patamar entre a parede do núcleo e o primeiro degrau. | Sem espaço para entrar/chegar na escada com uma cápsula de 0,28 m de raio. |
| 3 | Degraus do lance 1 maciços do piso ao topo, com a face inferior plana na cota do piso. | Nos pisos de 3 m, só ~1,5 m de altura livre sobre a metade alta do lance (controlador: 1,8 m). |
| 4 | Portas da escada com folha fechada, vão de 1,0 m e verga a 2,10 m. | O jogo não tem interação de porta (a folha fechada bloqueia a única rota); com a verga a 2,10 m, a folga de 0,21 m sobre o controlador ficava abaixo do `stepOffset` de 0,30 m e ele travava no vão. |
| 5 | (Só QA) trajetos colados no batente. | Resolvido no caminhante da Unity, sem mudança de arte. |

## Correção

- **Laje:** os pisos 1+ são montados em torno de `STAIR_HOLE`, a abertura derivada da posição da escada (os dois lances e o patamar de giro). A planta, a espessura (0,15 m) e o material da laje não mudam.
- **Patamar:** a escada foi deslocada 0,90 m para o interior do núcleo (`STAIR_Y0 = CORE[1] + 1.4`): 1,20 m de patamar de chegada/entrada em todos os pisos.
- **Degraus:** `stair_u(..., hollow=True)` só no Horizonte (forro escalonado). O padrão continua `hollow=False`: o Lar e as demais escadas não mudam.
- **Portas da escada (térreo e piso do prólogo):** vão de 1,20 m × 2,40 m; a folha é autoral, aberta a 90°, articulada no batente oeste e voltada para o corredor (articulada para dentro do núcleo, ou no batente leste, a folha obstruía o patamar em um dos pisos). É um calço fixo, não uma interação.

Preservado: identidade visual (mesmos materiais, fachada e interiores), escala 1:1, nomes de objetos, `facility_id`, `sa_kind`, `sa_layer`, coleções, marcadores (`GP_prologue_spawn_corridor`, `GP_quadro_tecnico`), âncoras, posições do mundo (só a escada deslocou 0,90 m e as folhas das portas giraram), quadro técnico do 4º andar e o corredor Lar → Oficina → Horizonte → Mercearia.

## Verificação

`Tools/Blender/verify_horizonte_stair.py` (novo, abre o `.blend` em processo novo, não salva, sai com status ≠ 0 se falhar): altura livre sobre os pontos andáveis dos dois lances e do patamar (exige ≥ 1,9 m, para o controlador de 1,8 m) e passagem livre nas portas (raios de largura × altura, abertura ≥ 2,4 m no eixo).

| Arquivo | Resultado |
| --- | --- |
| `W2_horizonte.blend` anterior (commit `9e4d740`) | **FALHA**: altura livre 0,14 m em 51–62 de 80 pontos por escada; 42/42 raios bloqueados em cada porta; abertura 1,95 m |
| `W2_horizonte.blend` corrigido | **PASSA**: altura livre mínima 2,82–2,97 m (0 pontos abaixo de 1,9 m nas 11 escadas); 0/42 raios bloqueados nas duas portas; abertura 2,42 m |

Relatório: `ArtSource/Blender/World/Reviews/W3_2_horizonte/stair_validation.json`.

O mesmo gerador (com este patch) foi usado na branch Unity: o herói reexportado foi caminhado a pé, pelo `CharacterController` real, da rua ao quadro técnico do 4º andar (0 penetrações, 0 travamentos, interação `QD-01`) e as cinco rotas do NavMesh de referência ficaram `PathComplete`. Esse teste vive em `codex/unity-world-integration-validation`.

## Reabertura e regressão (processo novo do Blender)

| Verificação | Resultado |
| --- | --- |
| `verify_w2_hero.py` no `W2_horizonte.blend` corrigido (capturas em `Reviews/W3_2_horizonte/`) | **PASS**, sem dados faltando, 12 luzes, 17 interativos, 147 malhas |
| Comparação de objetos com o herói anterior | nenhum objeto removido ou adicionado; `facility_id`, `sa_kind`, `sa_layer` e coleções idênticos; só mudaram a escada, as folhas das portas e a malha das lajes |
| Comparação visual (corredor do 4º andar, cortes de térreo e 4º andar, portaria) | equivalentes; a porta da escada agora aparece aberta |
| Slice W3.2 reaberto (`verify_world_v1_5.py --mode w32`) | **PASS**, sem dados faltando; a fachada do Horizonte renderizada difere da anterior só por ruído de render (diferença média 0,09/255) |
| IDs / `GP_` / `SLOT_` / `PROXY_` / âncoras / `facility_id` / instâncias do slice (`audit_ids_markers.py`) | **idênticos** ao W3.2 anterior (70 / 4 / 6 / 9) |
| `validate_masterplan.py` / `masterplan_routes.py` | **PASS** (`errors: []`, `unreachable: []`) |

Efeito colateral aceito: ao regenerar, três dos quatro carros da garagem do Horizonte passam a usar os carros W3.2 (de ~5–8 mil para ~13–16 mil tris cada, +22 mil no herói; os demais heróis não foram regenerados e seguem com os carros W3.1). Triângulos do herói: 189 mil → 211 mil.

## Arquivos

`Tools/Blender/create_w2_hero_horizonte.py`, `Tools/Blender/sa_detail.py`, `Tools/Blender/verify_horizonte_stair.py` (novo), `ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend`, `ArtSource/Blender/World/Reviews/W3_2_horizonte/` (capturas, `reopen_horizonte.json`, `reopen_w32.json`, `stair_validation.json`), este documento e `Docs/STATUS_IMPLEMENTACAO.md`.

## Pendências fora desta correção

Portão de pedestres do Horizonte (folha fechada, sem interação), interação de porta no jogo (a porta da escada é um estado autoral aberto), iluminação interior da escada e do corredor, e o port desta correção para a branch Unity: tudo isso é da etapa de integração.
