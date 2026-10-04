# 15 — Performance

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O alvo é PC Windows/Steam. Orçamentos medidos, nunca supostos: sem evidência de execução, não declarar desempenho alvo (CLAUDE.md).

## Performance

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Unity Profiler + Frame Debugger](https://docs.unity3d.com/6000.6/Documentation/Manual/Profiler.html) | Unity EULA | 6000.6 | — | **ESSENTIAL** | SAFE_TO_USE | referência | CPU/GPU/memória por frame; draw calls. |
| [Memory Profiler (com.unity.memoryprofiler)](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@latest) | Unity Companion License | via Package Manager | — | **ESSENTIAL** | SAFE_TO_USE | referência | Snapshots e comparação de memória para orçamentos por célula. |
| [Profile Analyzer](https://docs.unity3d.com/Packages/com.unity.performance.profile-analyzer@latest) | Unity Companion License | via Package Manager | — | **RECOMMENDED** | SAFE_TO_USE | referência | Estatística de muitos frames (antes/depois). |
| [Project Auditor](https://github.com/Unity-Technologies/ProjectAuditor) | Unity Package Distribution License | (sem release) / `eece77260853` | 2025-04-03 | **RECOMMENDED** | SAFE_TO_USE | referência | Análise estática de código/assets/shaders/settings; embutido no Unity 6.4+ (Window > Analysis). |
| [RenderDoc](https://github.com/baldurk/renderdoc) | MIT | v1.46 / `4c0752414779` | 2026-10-02 | **RECOMMENDED** | SAFE_TO_USE | referência | Captura de frame GPU, overdraw, texturas, draw calls. |
| [NVIDIA Nsight Graphics](https://developer.nvidia.com/nsight-graphics) | Gratuito (proprietário) | atual | — | **OPTIONAL** | SAFE_TO_USE | referência | Profiling GPU NVIDIA aprofundado. |

**Instalação (somente com aprovação)**

- **RenderDoc**: Instalador oficial (renderdoc.org); fora do repositório.

**Notas**

- **Project Auditor**: No 6000.6 é módulo do Editor; instalar só o pacote de regras se necessário.

## Workflow recomendado

1. Cena de referência por célula do núcleo com câmera em rota fixa (determinística) para medir.
2. Unity Profiler (CPU/GPU), Frame Debugger (draw calls, batching), Memory Profiler (snapshots antes/depois do streaming), Profile Analyzer (comparar builds).
3. RenderDoc para overdraw, tamanho de texturas e custo de shaders; Nsight para gargalos de GPU NVIDIA.
4. Project Auditor (embutido no 6.4+) para problemas estáticos de código, shaders e configurações.
5. Orçamento inicial a validar: até cerca de 2–3k draw calls visíveis com SRP Batcher, texturas em streaming, LOD0 só no anel próximo.

