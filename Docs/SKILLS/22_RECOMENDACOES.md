# 22 — Recomendações finais

## TOP 10 para todo o projeto
1. **Skill própria: santa-aurora-world-pipeline**: Codifica o pipeline do mundo (validação, geradores, reabertura, capturas, convenções de IDs/células).
2. **Skill própria: blender-headless-bpy**: Padrões bpy validados no Blender 5.2: malha eficiente, UV métrico, bevel bmesh, GN instancing (correção 5.x), cor, assets, auditoria.
3. **Blender 5.2.1 LTS**: Ferramenta principal de modelagem/geração; já instalada; LTS garante estabilidade da API.
4. **Geometry Nodes (nativo)**: Instancing em massa (já usado para 13k edificações), scattering, cabos, cercas, variação procedural.
5. **Poly Haven**: Texturas, HDRIs e modelos CC0 (uso comercial livre) — referência e base de materiais/iluminação.
6. **ambientCG**: Materiais PBR CC0 (concreto, tijolo, asfalto, metal...).
7. **Material Maker**: Autoria procedural de texturas PBR (tileables, trim sheets) exportando Base Color/Normal/Roughness/Metallic/AO para os slots já criados.
8. **Nice-Wolf-Studio/unity-claude-skills (35 skills)**: Cobertura ampla de Unity 6 (cenas/assets, performance, testes, save, UI, input, NavMesh, animação, procedural). Base para W5.
9. **Addressables (com.unity.addressables)**: Carregamento assíncrono por grupos/rótulos — base do streaming por subcélula e cenas aditivas.
10. **Unity Test Framework 1.8.0**: EditMode/PlayMode; smoke tests (RuntimeSmoke já existe), migração de saves, validadores de assets.

## TOP 5 para usar já no W1.5/W2
1. **Skill própria: santa-aurora-world-pipeline**
2. **Skill própria: blender-headless-bpy**
3. **Material Maker**
4. **Poly Haven**
5. **Skill própria: visual-review**

**Por que estes:** o W2 é a Cidade Antiga em alta fidelidade. O ganho imediato vem de: (1–2) skills próprias que mantêm o pipeline e os padrões bpy consistentes entre sessões; (3) Material Maker para preencher os slots PBR já criados com texturas autorais; (4) Poly Haven/ambientCG CC0 como base e referência de materiais e HDRIs; (5) revisão visual com regressão por diferença de imagem, para que nada seja aprovado sem olhar.

## Plano de adoção (sem instalar nada agora)
1. **Agora (W2)**: ativar no projeto, com aprovação, as skills próprias `santa-aurora-world-pipeline` e `blender-headless-bpy` (copiar para `.claude/skills/`); usar Material Maker e fontes CC0 fora do repositório, registrando cada asset.
2. **W5 (Unity)**: instalar Addressables, Memory Profiler, Profile Analyzer e Newtonsoft Json; ativar as skills Unity da Nice-Wolf necessárias; avaliar `unity-mcp` em branch isolada.
3. **Pré-lançamento**: Localization, Steamworks.NET, Steam Audio, CI com GameCI (se a licença for decidida), Git LFS para texturas e FBX.

## Rejeitados (com motivo)
- **Citronetic/unity-claude-skill**: Sem licença declarada (não pode ser copiado); 0 estrelas; ~32 mil arquivos.
- **github/github-mcp-server**: Exige token; redundante com o gh CLI já autenticado.
- **modelcontextprotocol/servers**: Filesystem/git redundantes com ferramentas nativas do Claude Code.
- **Megascans / Fab**: Termos e preços mudaram em 2024–2025; exige revisão jurídica e orçamento antes de qualquer uso.
- **OpenStreetMap (dados)**: Share-alike e cidade real: proibido como conteúdo de Santa Aurora; só estudo de técnica.
- **Unity-Technologies/HLODSystem**: Sem licença no repositório e sem atividade desde 2024; gerar HLOD/proxies no Blender (controle total).
- **Unity-Technologies/AutoLOD**: Experimental, parado desde 2024; LODs serão autorados/gerados no Blender.
- **NavMeshComponents (legado)**: Substituído pelo pacote AI Navigation.

## Não instalar sem revisão/autorização
- **Besty0728/Unity-Skills**: Instala pacote no Editor que executa operações remotamente; 300+ arquivos de código; revisão completa necessária.
- **Citronetic/unity-claude-skill**: Sem licença declarada (não pode ser copiado); 0 estrelas; ~32 mil arquivos.
- **LevyBytes/AI-SKILL-blender**: AGPL-3.0: não copiar para o repositório; consultar online apenas.
- **ahujasid/blender-mcp**: Socket que executa Python arbitrário dentro do Blender; integrações opcionais com chaves de API. Desnecessário: usamos bpy headless versionado.
- **github/github-mcp-server**: Exige token; redundante com o gh CLI já autenticado.
- **modelcontextprotocol/servers**: Filesystem/git redundantes com ferramentas nativas do Claude Code.
- **OpenStreetMap (dados)**: Share-alike e cidade real: proibido como conteúdo de Santa Aurora; só estudo de técnica.
- **TownGeneratorOS**: GPL-3: não copiar código; só inspiração.
- **Unity-Technologies/HLODSystem**: Sem licença no repositório e sem atividade desde 2024; gerar HLOD/proxies no Blender (controle total).
- **Unity-Technologies/AutoLOD**: Experimental, parado desde 2024; LODs serão autorados/gerados no Blender.
- **NavMeshComponents (legado)**: 

## Riscos gerais
- Skills de comunidade mudam rápido: sempre commit fixado; reavaliar a cada marco.
- Skills Unity baseadas no 6.3 LTS: conferir APIs no 6000.6.
- MCPs de controle de editor ampliam a superfície de execução; preferir scripts versionados.
- Termos de marketplaces mudam (Fab/Megascans em 2024–2025): revisar antes de cada uso.

