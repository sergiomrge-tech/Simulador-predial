# Biblioteca de Skills e Ferramentas — Índice Geral

**Etapa B da fila noturna (W1.5 → B), 2026-10-03.**

Esta é uma biblioteca curada de skills, workflows, MCPs, ferramentas e referências para produzir Facility Ops / Simulador Predial do mundo à Steam. Princípios: **poucos recursos excelentes, automação própria, ferramentas maduras e controle total do pipeline.** Nada foi instalado e nenhum código externo foi executado. Os metadados vieram da API pública do GitHub (`gh api`, só leitura), com licença, último push, release e commit fixado.

Itens no catálogo: ESSENTIAL: 26, RECOMMENDED: 27, OPTIONAL: 41, REJECTED: 8 (total 102).

## Documentos
| Arquivo | Tema |
|---|---|
| `01_CLAUDE_CODE.md` | Claude Code, Agent Skills, MCPs |
| `02_BLENDER_MODELAGEM.md` | Blender, modelagem, kits, salas técnicas |
| `03_BLENDER_PROCEDURAL.md` | Geometry Nodes, cidades procedurais |
| `04_BLENDER_LARGE_WORLD.md` | grandes cenas, bibliotecas, instancing, chunking |
| `05_PBR_TEXTURAS.md` | PBR, UV, trim sheets, decals, fontes CC0, terreno/GIS |
| `06_UNITY_LARGE_WORLD.md` | Addressables, cenas aditivas, LOD/HLOD, URP |
| `07_UNITY_GAMEPLAY.md` | primeira pessoa, interação, trabalhos, inventário, simulação |
| `08_ANIMACAO.md` | rigging, mãos em primeira pessoa, IK |
| `09_VEICULOS.md` | WheelCollider, controlador próprio |
| `10_AI_NPC.md` | NavMesh, rotinas de NPC |
| `11_ECONOMIA_PROGRESSAO.md` | balanceamento, anti-softlock |
| `12_SAVE_DATA.md` | saves versionados, migração, Steam Cloud |
| `13_UI_UX.md` | UI Toolkit, tablet, mapa/GPS |
| `14_AUDIO_VFX.md` | áudio espacial, VFX, clima |
| `15_PERFORMANCE.md` | profiling e orçamentos |
| `16_QA_TESTES.md` | testes, validadores, regressão visual |
| `17_BUILD_GITHUB.md` | build, CI, LFS, documentação/ADR |
| `18_STEAM.md` | Steamworks (preparação; não integrar ainda) |
| `19_LOCALIZACAO_ACESSIBILIDADE.md` | Localization, acessibilidade |
| `20_ASSET_PIPELINE.md` | Blender → Unity, validação de assets |
| `21_LICENCAS.md` | política de licenças e registro de origem |
| `22_RECOMENDACOES.md` | TOP 10, TOP 5, rejeitados, plano de adoção |

## Efetivamente salvos em `Tools/Skills/`
- **Skill própria: santa-aurora-world-pipeline** → `Tools/Skills/claude/santa-aurora-world-pipeline`
- **Skill própria: blender-headless-bpy** → `Tools/Skills/blender/blender-headless-bpy`
- **Skill própria: blender-to-unity-export (plano)** → `Tools/Skills/pipeline/blender-to-unity-export`
- **Skill própria: visual-review** → `Tools/Skills/qa/visual-review`
- **obra/superpowers (subconjunto salvo)** → `Tools/Skills/claude/superpowers-subset`
- **Nice-Wolf-Studio/unity-claude-skills (35 skills)** → `Tools/Skills/unity/nice-wolf-unity-claude-skills`

Tudo o mais fica **por referência** (URL + versão/commit no `catalog.json`).

## Como regenerar
```
python Tools/Skills/build_catalog.py .
```

