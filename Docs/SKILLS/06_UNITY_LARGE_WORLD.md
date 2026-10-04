# 06 — Unity: mundo grande, streaming e visual URP

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

Unity 6000.6.2f1 + URP 17.6. O mundo tem 8×8 km com origem no centro: coordenadas de até cerca de 4 km mantêm precisão sub-milimétrica em float, então floating origin não é necessário agora (reavaliar se surgirem jitter de câmera ou física a grande distância).

## Unity: mundo grande e streaming

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Nice-Wolf-Studio/unity-claude-skills (35 skills)](https://github.com/Nice-Wolf-Studio/unity-claude-skills) | MIT | (sem release) / `a149d3e99542` | 2026-09-15 | **ESSENTIAL** | SAFE_TO_USE | salvo: `Tools/Skills/unity/nice-wolf-unity-claude-skills` | Cobertura ampla de Unity 6 (cenas/assets, performance, testes, save, UI, input, NavMesh, animação, procedural). Base para W5. |
| [Besty0728/Unity-Skills](https://github.com/Besty0728/Unity-Skills) | MIT | v2.9.0 / `c7d0dfc85aec` | 2026-10-03 | **OPTIONAL** | DO_NOT_INSTALL | referência | Automação do Editor Unity por skills + REST; popular (1,8k estrelas). |
| [Citronetic/unity-claude-skill](https://github.com/Citronetic/unity-claude-skill) | sem licença declarada | (sem release) / `7a8aa0348f9c` | 2026-10-01 | **REJECTED** | DO_NOT_INSTALL | referência | Guia Unity 6+ em 16 tópicos. |
| [Addressables (com.unity.addressables)](https://docs.unity3d.com/Packages/com.unity.addressables@latest) | Unity Companion License | instalar pela versão verificada do Unity 6000.6 e fixar no manifest | — | **ESSENTIAL** | SAFE_TO_USE | referência | Carregamento assíncrono por grupos/rótulos — base do streaming por subcélula e cenas aditivas. |
| [Cenas aditivas (SceneManager.LoadSceneAsync Additive)](https://docs.unity3d.com/6000.6/Documentation/ScriptReference/SceneManagement.SceneManager.LoadSceneAsync.html) | Unity EULA | 6000.6 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Uma cena por macrocélula + cenas de heróis; descarregamento por distância. |
| [LODGroup / GPU instancing / SRP Batcher / occlusion culling](https://docs.unity3d.com/6000.6/Documentation/Manual/LevelOfDetail.html) | Unity EULA | 6000.6 | — | **ESSENTIAL** | SAFE_TO_USE | referência | LOD por convenção _LODn, instancing das 47 variantes, oclusão bakeada por célula, streaming de texturas (mipmap streaming). |
| [Unity-Technologies/HLODSystem](https://github.com/Unity-Technologies/HLODSystem) | sem arquivo de licença no repositório | (sem release) / `04be7e86357c` | 2024-03-30 | **REJECTED** | DO_NOT_INSTALL | referência | HLOD experimental. |
| [Unity-Technologies/AutoLOD](https://github.com/Unity-Technologies/AutoLOD) | Unity Companion License | (sem release) / `9492bc0620ea` | 2024-02-29 | **REJECTED** | DO_NOT_INSTALL | referência | Geração automática de LOD. |
| [Splines (com.unity.splines)](https://docs.unity3d.com/Packages/com.unity.splines@latest) | Unity Companion License | via Package Manager | — | **OPTIONAL** | SAFE_TO_USE | referência | Splines para cabos/ruas/rotas em runtime. |
| [UnityCsReference](https://github.com/Unity-Technologies/UnityCsReference) | Unity Reference-Only License | (sem release) / `88ce7b60434b` | 2026-10-02 | **RECOMMENDED** | SAFE_TO_USE | referência | Código C# do Editor/Engine para entender comportamento exato de APIs. |

**Riscos**

- **Nice-Wolf-Studio/unity-claude-skills (35 skills)**: Baseado em Unity 6.3 LTS (projeto usa 6000.6): conferir APIs novas. unity-ops (hooks/scripts) não copiado.
- **Besty0728/Unity-Skills**: Instala pacote no Editor que executa operações remotamente; 300+ arquivos de código; revisão completa necessária.
- **Citronetic/unity-claude-skill**: Sem licença declarada (não pode ser copiado); 0 estrelas; ~32 mil arquivos.
- **Unity-Technologies/HLODSystem**: Sem licença no repositório e sem atividade desde 2024; gerar HLOD/proxies no Blender (controle total).
- **Unity-Technologies/AutoLOD**: Experimental, parado desde 2024; LODs serão autorados/gerados no Blender.
- **UnityCsReference**: Licença reference-only: ler, nunca copiar para o projeto.

**Instalação (somente com aprovação)**

- **Addressables (com.unity.addressables)**: Package Manager (com aprovação, na etapa W5).

**Notas**

- **LODGroup / GPU instancing / SRP Batcher / occlusion culling**: 8 km com origem no centro: coordenadas máximas de ~4 km mantêm precisão sub-milimétrica; floating origin não é necessário agora.

## Unity: URP e visual

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Universal Render Pipeline 17.6.0](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/manual/index.html) | Unity Companion License | 17.6.0 (instalado) | — | **ESSENTIAL** | SAFE_TO_USE | referência | Pipeline do projeto: SRP Batcher, decals, reflection/light probes, Shader Graph. |
| [BoatAttack (amostra URP)](https://github.com/Unity-Technologies/BoatAttack) | Unity Companion License | (sem release) / `6acf5f773a44` | 2025-12-05 | **OPTIONAL** | SAFE_TO_USE | referência | Técnicas URP (água, iluminação, LOD). |
| [Unity Graphics (fonte URP/Shader Graph/VFX)](https://github.com/Unity-Technologies/Graphics) | Unity Companion License | (sem release) / `a7e4c051d256` | 2026-09-29 | **OPTIONAL** | SAFE_TO_USE | referência | Fonte dos pacotes gráficos para depurar URP. |
| [Shader Graph (URP)](https://docs.unity3d.com/Packages/com.unity.shadergraph@latest) | Unity Companion License | acompanha URP 17.6 | — | **RECOMMENDED** | SAFE_TO_USE | referência | Molhado/chuva, decals, materiais em camadas. |

## Workflow recomendado

**Streaming (W5)**
1. Uma cena aditiva por macrocélula `SA_Mxx_yy` + cenas de heróis (interiores) carregadas por proximidade ou portal.
2. Conteúdo por subcélula como grupos/rótulos Addressables; carregamento assíncrono em anel (completo até 500–750 m, HLOD até 1,8 km, proxies de skyline até 4 km — World Bible §12).
3. Orçamentos por célula: memória, draw calls, tris (medidos com Memory Profiler e Frame Debugger).
4. Transições sem tela de carregamento: pré-carregar a vizinhança na direção do movimento; `Application.backgroundLoadingPriority` ajustado.

**Renderização**
- SRP Batcher + GPU instancing das variantes; LODGroup pelos sufixos `_LODn`; occlusion culling bakeado por cena de célula; mipmap streaming de texturas.
- Iluminação: luz direcional + céu; Adaptive Probe Volumes/light probes nos exteriores; reflection probes por quarteirão; baking seletivo nos interiores de heróis; decals URP.
- Clima e noite: Shader Graph para molhado; neblina leve nativa; ciclo dia/noite controlado por script com perfis Volume.

**Não usar**: HLODSystem e AutoLOD experimentais (parados e sem licença clara). HLOD e LOD são gerados no Blender, com controle total.

