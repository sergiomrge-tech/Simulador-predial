# CLAUDE NEXT TASK — ETAPA A

## Pesquisa e curadoria de skills/ferramentas para toda a produção

Antes de continuar pesado no W1.5, faça uma pesquisa ampla na web para montar uma biblioteca técnica curada para o projeto Facility Ops.

### Objetivo

Encontrar skills públicas de Claude Code, workflows, MCPs, add-ons, extensões, ferramentas e referências técnicas que aumentem a capacidade de produção em:

- Blender / bpy / Python;
- Geometry Nodes;
- hard-surface e arquitetura;
- procedural cities / roads / façades / scattering;
- large scenes / Asset Browser / linked libraries / instancing;
- PBR / UV / trim sheets / decals / texturização;
- terrain / GIS / OSM / DEM apenas como técnica, nunca para copiar uma cidade real;
- Blender→Unity export pipeline;
- Unity C# / URP / Shader Graph / VFX Graph;
- additive scenes / Addressables / world streaming;
- LOD / HLOD / occlusion / GPU instancing / profiling;
- first-person tools / IK / Animation Rigging;
- vehicles / WheelCollider / enter-exit / cargo;
- NavMesh / pedestrians / NPC schedules;
- job boards / authored jobs / procedural jobs;
- economy / progression / anti-softlock;
- properties / homes / furniture persistence;
- inventories / ScriptableObjects / stable IDs;
- versioned saves / migrations / backups / Steam Cloud readiness;
- UI Toolkit / maps / tablet / shops / settings / accessibility;
- audio / spatial audio / ambience;
- weather / day-night / rain / wetness / storms;
- automated QA / Unity Test Framework / screenshot tests / validation;
- build automation / PowerShell / GitHub Actions;
- Git LFS / Unity+Blender binary workflow;
- Steamworks / Steamworks.NET / Steam Input / achievements / cloud / depots;
- localization / accessibility;
- ADR/GDD/docs/changelog;
- simulator game balancing / replayability;
- data-driven content;
- asset validation;
- visual regression / render review.

### Agent Skills

Procure especificamente skills públicas confiáveis para Claude Code relacionadas a:
- Blender;
- Blender Python;
- Geometry Nodes;
- Unity;
- C#;
- game development;
- 3D environment art;
- procedural modeling;
- large-world optimization;
- QA/testing;
- Git/GitHub;
- Steam.

Para cada skill, registrar:
- nome;
- URL;
- autor;
- licença;
- última atualização;
- função;
- dependências;
- se exige MCP;
- se exige credenciais;
- risco;
- valor concreto para este projeto;
- instalação;
- classificação.

### Classificação

Use:
- ESSENTIAL
- RECOMMENDED
- OPTIONAL
- REJECTED

E:
- SAFE_TO_USE
- REVIEW_REQUIRED
- DO_NOT_INSTALL

### Segurança/licença

Priorizar:
- open source;
- licença comercial clara;
- projetos mantidos;
- fontes oficiais/confiáveis.

Sempre verificar:
- licença;
- uso comercial;
- redistribuição;
- necessidade de atribuição;
- issues recentes;
- scripts suspeitos;
- dependências.

Não instalar nada ainda.

### Estrutura de saída

Criar:

`Docs/SKILLS/00_INDICE_GERAL.md`  
`Docs/SKILLS/01_CLAUDE_CODE.md`  
`Docs/SKILLS/02_BLENDER_MODELAGEM.md`  
`Docs/SKILLS/03_BLENDER_PROCEDURAL.md`  
`Docs/SKILLS/04_BLENDER_LARGE_WORLD.md`  
`Docs/SKILLS/05_PBR_TEXTURAS.md`  
`Docs/SKILLS/06_UNITY_LARGE_WORLD.md`  
`Docs/SKILLS/07_UNITY_GAMEPLAY.md`  
`Docs/SKILLS/08_ANIMACAO.md`  
`Docs/SKILLS/09_VEICULOS.md`  
`Docs/SKILLS/10_AI_NPC.md`  
`Docs/SKILLS/11_ECONOMIA_PROGRESSAO.md`  
`Docs/SKILLS/12_SAVE_DATA.md`  
`Docs/SKILLS/13_UI_UX.md`  
`Docs/SKILLS/14_AUDIO_VFX.md`  
`Docs/SKILLS/15_PERFORMANCE.md`  
`Docs/SKILLS/16_QA_TESTES.md`  
`Docs/SKILLS/17_BUILD_GITHUB.md`  
`Docs/SKILLS/18_STEAM.md`  
`Docs/SKILLS/19_LOCALIZACAO_ACESSIBILIDADE.md`  
`Docs/SKILLS/20_ASSET_PIPELINE.md`  
`Docs/SKILLS/21_LICENCAS.md`  
`Docs/SKILLS/22_RECOMENDACOES.md`

Criar também:
- `Tools/Skills/README.md`
- `Tools/Skills/catalog.json`
- diretórios lógicos `claude/`, `blender/`, `unity/`, `pipeline/`, `qa/`, `steam/` somente se necessários.

Se uma skill deve ser mantida apenas por referência, não copie seu código: registre URL + tag/commit no catálogo.

### Resultado final obrigatório

Selecionar:
- TOP 10 recursos essenciais para o projeto;
- TOP 5 para W1.5/W2;
- quais poderiam ser instalados depois;
- quais foram rejeitados e por quê.

Depois:
1. atualizar `Docs/STATUS_IMPLEMENTACAO.md`;
2. commit organizado;
3. push para `claude/w1-masterplan`;
4. working tree limpa;
5. reler `Docs/CLAUDE_NEXT_TASK.md` conforme `Docs/CLAUDE_AUTONOMOUS_PROTOCOL.md`.

Não fazer merge no main.
