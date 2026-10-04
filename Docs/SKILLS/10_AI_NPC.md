# 10 — NPC e IA

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

Os NPCs são clientes, moradores, funcionários (a partir do Capítulo VII) e transeuntes leves. AI Navigation 2.0.12 já está instalado.

## NPC e IA

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [AI Navigation 2.0.12](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html) | Unity Companion License | 2.0.12 (instalado) | — | **ESSENTIAL** | SAFE_TO_USE | referência | NavMesh por cena/célula, NavMeshLinks, obstáculos — NPCs clientes/funcionários. |
| [NavMeshComponents (legado)](https://github.com/Unity-Technologies/NavMeshComponents) | MIT | 2019.4.0f1 / `41d24c4639f3` | 2023-05-17 | **REJECTED** | DO_NOT_INSTALL | referência | Substituído pelo pacote AI Navigation. |

## Workflow recomendado

- NavMesh por cena de célula + NavMeshLinks entre células; superfícies por camada (calçada, pista, interior).
- Rotinas por agenda (manhã, tarde, noite) com pontos de interesse dos lotes (manifesto `OT_Gameplay_Lots_*`); pooling de pedestres por anel de distância.
- Clientes: máquina de estados simples (aguardando, acompanhando, avaliando, pagando); behavior trees só se o comportamento crescer.
- Funcionários: tarefas da mesma estrutura de chamados com tempo e competência; simulação abstrata fora da tela.

