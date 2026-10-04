# 07 — Unity: primeira pessoa, sistemas e arquitetura

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O protótipo já tem `Interaction.cs` (primeira pessoa, Input System, raycast), `ServiceSession`, `SaveService`, `ChapterOne` e `TabletUI`. A recomendação é **evoluir o que existe, com arquitetura simples orientada a dados**, e evitar frameworks.

## Unity: gameplay, arquitetura e sistemas

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Input System 1.19.0](https://github.com/Unity-Technologies/InputSystem) | Unity Companion License | 1.20.0 / `bed688c78414` | 2026-10-02 | **ESSENTIAL** | SAFE_TO_USE | referência | Já usado no Interaction.cs; remapeamento, gamepad, sensibilidade, acessibilidade. |
| [UniTask](https://github.com/Cysharp/UniTask) | MIT | 2.5.11 / `f74aace058f4` | 2026-09-29 | **OPTIONAL** | REVIEW_REQUIRED | referência | Async sem alocação. |
| [VContainer](https://github.com/hadashiA/VContainer) | MIT | 1.19.0 / `4fc1ed47dff1` | 2026-09-05 | **OPTIONAL** | REVIEW_REQUIRED | referência | Injeção de dependência leve. |
| [Game Programming Patterns demo (Unity)](https://github.com/Unity-Technologies/game-programming-patterns-demo) | sem SPDX (ver repositório) | (sem release) / `edbd64fd5635` | 2025-10-23 | **OPTIONAL** | SAFE_TO_USE | referência | Padrões (state, observer, command) aplicados em Unity. |
| [Game Programming Patterns (livro online)](https://gameprogrammingpatterns.com/) | Leitura gratuita online (direitos do autor) | web | — | **RECOMMENDED** | SAFE_TO_USE | referência | State machines, event queue, service locator, component — base para arquitetura modesta. |
| [FPSSample](https://github.com/Unity-Technologies/FPSSample) | Unity Companion License | v0.0.0 / `c8375e7cf29c` | 2025-10-23 | **OPTIONAL** | SAFE_TO_USE | referência | Referência de controlador FP/arquitetura. |

**Riscos**

- **UniTask**: Unity 6 tem Awaitable nativo; adicionar só se medido necessário.
- **VContainer**: Evitar overengineering; serviços simples bastam no escopo atual.
- **FPSSample**: Arquivado/antigo (HDRP).

**Notas**

- **Input System 1.19.0**: Instalado: 1.19.0 (repo indica 1.20.0 disponível; atualizar só com teste).

## Workflow recomendado

**Primeira pessoa e interação**
- Manter o alcance do raycast igual à distância do personagem (regra do CLAUDE.md). *Head bob* moderado e opcional (acessibilidade).
- Mãos: rig humanoide de braços + Animation Rigging (Two Bone IK) para segurar e acionar; ferramentas como prefabs com pontos de pega (grip/aim).
- Interações: portas (dobradiça com limite), pegar/colocar (snap points), inspeção (zoom + rotação), prompts contextuais via UI Toolkit, troca de equipamento numa roda ou hotbar.

**Trabalhos, contratos e consequências**
- Chamados = dados (`ScriptableObject` ou JSON) com ID estável, local (ID do mapa), sintomas, causas ponderadas, peças e preço.
- Geração com seed por dia e região; tabelas de falha ponderadas por tipo e idade do equipamento; validação de cada chamado gerado (causa alcançável, peças à venda, região desbloqueada).
- Histórico persistente por edifício e equipamento (estado, últimas intervenções, recomendações ignoradas), alimentando consequências e contratos recorrentes.

**Simulação abstrata de sistemas prediais**
- Grafo de componentes (fonte → proteção → circuito → carga; bomba → recalque → reservatório) com estados simples (ok, degradado, falha) e sinais de diagnóstico.
- Nunca reproduzir procedimentos perigosos reais: valores e procedimentos são fictícios e simplificados (a classe `ElectricalNetwork` já segue esse princípio).

**Inventário e catálogos**
- Itens por ID (`ScriptableObject` catálogo + ID string estável); empilháveis e ferramentas únicas; inventário de veículo e de depósito como contêineres; o save guarda só IDs e quantidades.

**Arquitetura**
- Serviços simples com interfaces onde há teste; eventos C# ou um barramento mínimo; máquinas de estado explícitas para fluxos de serviço. Sem DI framework até haver dor real.

