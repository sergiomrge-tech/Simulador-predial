#!/usr/bin/env python3
"""Build Tools/Skills/catalog.json and Docs/SKILLS/*.md from the curated entries below.

Usage: python Tools/Skills/build_catalog.py [PROJECT_ROOT]
GitHub facts (license, commit, last push, stars, release) come from Tools/Skills/sources/github_metadata_2026-10-03.json,
collected read-only with `gh api` on 2026-10-03. Nothing listed here is installed or executed by this script.
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
meta = json.loads((root / "Tools" / "Skills" / "sources" / "github_metadata_2026-10-03.json").read_text(encoding="utf-8"))

LICENSE_FIX = {  # NOASSERTION/None resolved by reading the LICENSE files
    "anthropics/skills": "Apache-2.0 (maioria das skills) + source-available (docx/pdf/pptx/xlsx)",
    "anthropics/claude-code": "Proprietário (Anthropic Commercial Terms)",
    "modelcontextprotocol/servers": "MIT -> Apache-2.0 (transição)",
    "franMarz/TexTools-Blender": "GPL-3.0",
    "armory3d/armortools": "zlib (fonte); binários pagos",
    "Unity-Technologies/AutoLOD": "Unity Companion License",
    "Unity-Technologies/ProjectAuditor": "Unity Package Distribution License",
    "Unity-Technologies/Graphics": "Unity Companion License",
    "Unity-Technologies/InputSystem": "Unity Companion License",
    "Unity-Technologies/UnityCsReference": "Unity Reference-Only License",
    "Unity-Technologies/BoatAttack": "Unity Companion License",
    "Unity-Technologies/FPSSample": "Unity Companion License",
    "Unity-Technologies/HLODSystem": "sem arquivo de licença no repositório",
    "Unity-Technologies/game-programming-patterns-demo": "sem SPDX (ver repositório)",
    "git-lfs/git-lfs": "MIT",
    "MessagePack-CSharp/MessagePack-CSharp": "MIT",
    "npryce/adr-tools": "GPL-3.0",
    "mxgmn/WaveFunctionCollapse": "MIT",
    "fsfe/reuse-tool": "GPL-3.0-or-later (ferramenta; dados CC0)",
    "joelparkerhenderson/architecture-decision-record": "sem SPDX (ver repositório)",
    "travisvn/awesome-claude-skills": "sem licença declarada",
    "ComposioHQ/awesome-claude-skills": "sem licença declarada",
    "Citronetic/unity-claude-skill": "sem licença declarada",
}

E = []


def add(id, name, cat, kind, priority, safety, value, risk="", install="", deps="", storage="reference", url=None, gh=None, author=None,
        license=None, version=None, commit=None, updated=None, notes=""):
    item = {"id": id, "name": name, "category": cat, "kind": kind, "priority": priority, "safety": safety, "storage": storage,
            "value": value, "risk": risk, "install": install, "dependencies": deps, "notes": notes}
    if gh:
        m = meta.get(gh, {})
        item.update({"url": m.get("url", f"https://github.com/{gh}"), "author": author or gh.split("/")[0],
                     "license": LICENSE_FIX.get(gh, m.get("license") or "não declarada"), "version": m.get("latest_release") or "(sem release)",
                     "commit": m.get("commit"), "lastUpdate": m.get("pushed_at"), "stars": m.get("stars"), "archived": m.get("archived")})
    else:
        item.update({"url": url, "author": author, "license": license, "version": version, "commit": commit, "lastUpdate": updated})
    if license and gh:
        item["license"] = license
    E.append(item)


# ---------------------------------------------------------------- 01 Claude Code / Agent Skills / MCP
add("own.santa-aurora-world-pipeline", "Skill própria: santa-aurora-world-pipeline", "claude", "skill (própria)", "ESSENTIAL", "SAFE_TO_USE",
    "Codifica o pipeline do mundo (validação, geradores, reabertura, capturas, convenções de IDs/células).",
    storage="saved:Tools/Skills/claude/santa-aurora-world-pipeline", url="Tools/Skills/claude/santa-aurora-world-pipeline/SKILL.md",
    author="Facility Ops (Claude Code, W1.5)", license="Licença do repositório", version="1.0 (2026-10-03)",
    install="Copiar a pasta para .claude/skills/ quando aprovado.")
add("own.blender-headless-bpy", "Skill própria: blender-headless-bpy", "blender_model", "skill (própria)", "ESSENTIAL", "SAFE_TO_USE",
    "Padrões bpy validados no Blender 5.2: malha eficiente, UV métrico, bevel bmesh, GN instancing (correção 5.x), cor, assets, auditoria.",
    storage="saved:Tools/Skills/blender/blender-headless-bpy", url="Tools/Skills/blender/blender-headless-bpy/SKILL.md",
    author="Facility Ops", license="Licença do repositório", version="1.0 (2026-10-03)", install="Copiar para .claude/skills/ quando aprovado.")
add("own.blender-to-unity-export", "Skill própria: blender-to-unity-export (plano)", "pipeline", "skill (própria)", "ESSENTIAL", "SAFE_TO_USE",
    "Convenções FBX/nomes/LOD/colisores/pivôs/manifesto para a integração W5; marcada como plano a validar.",
    storage="saved:Tools/Skills/pipeline/blender-to-unity-export", url="Tools/Skills/pipeline/blender-to-unity-export/SKILL.md",
    author="Facility Ops", license="Licença do repositório", version="0.1 plano (2026-10-03)")
add("own.visual-review", "Skill própria: visual-review", "qa", "skill (própria)", "ESSENTIAL", "SAFE_TO_USE",
    "Capturas reais, review sheets geradas de JSON e regressão visual com Pillow (já instalado).",
    storage="saved:Tools/Skills/qa/visual-review", url="Tools/Skills/qa/visual-review/SKILL.md", author="Facility Ops",
    license="Licença do repositório", version="1.0 (2026-10-03)")
add("anthropics.skills", "Anthropic Agent Skills (oficial)", "claude", "skill marketplace", "RECOMMENDED", "SAFE_TO_USE",
    "Fonte oficial de skills e do padrão SKILL.md; skill-creator, mcp-builder e webapp-testing úteis para criar skills próprias.",
    risk="Skills de documento são source-available (não copiar para redistribuição).",
    install="/plugin marketplace add anthropics/skills (só com aprovação); várias já estão disponíveis na sessão como anthropic-skills:*",
    gh="anthropics/skills", author="Anthropic")
add("anthropics.claude-code-docs", "Documentação Claude Code (skills, hooks, permissões)", "claude", "referência", "ESSENTIAL", "SAFE_TO_USE",
    "Regras de carregamento de skills (.claude/skills), frontmatter, allowed-tools, segurança de skills de terceiros.",
    url="https://code.claude.com/docs/en/skills", author="Anthropic", license="Proprietário (documentação)", version="consultado 2026-10-03")
add("obra.superpowers", "obra/superpowers (subconjunto salvo)", "claude", "skill pack", "RECOMMENDED", "SAFE_TO_USE",
    "Metodologia: systematic-debugging, verification-before-completion, TDD, writing-plans. Reforça gates com evidência.",
    risk="Plugin completo instala hooks e altera fluxo -> não instalar; subconjunto markdown salvo sem scripts.",
    storage="saved:Tools/Skills/claude/superpowers-subset", gh="obra/superpowers", author="Jesse Vincent (obra)")
add("nicewolf.unity-skills", "Nice-Wolf-Studio/unity-claude-skills (35 skills)", "unity_world", "skill pack", "ESSENTIAL", "SAFE_TO_USE",
    "Cobertura ampla de Unity 6 (cenas/assets, performance, testes, save, UI, input, NavMesh, animação, procedural). Base para W5.",
    risk="Baseado em Unity 6.3 LTS (projeto usa 6000.6): conferir APIs novas. unity-ops (hooks/scripts) não copiado.",
    storage="saved:Tools/Skills/unity/nice-wolf-unity-claude-skills", gh="Nice-Wolf-Studio/unity-claude-skills")
add("besty.unity-skills", "Besty0728/Unity-Skills", "unity_world", "skill pack + plugin Unity", "OPTIONAL", "DO_NOT_INSTALL",
    "Automação do Editor Unity por skills + REST; popular (1,8k estrelas).",
    risk="Instala pacote no Editor que executa operações remotamente; 300+ arquivos de código; revisão completa necessária.",
    gh="Besty0728/Unity-Skills")
add("nowsprinting.unity-settings", "nowsprinting/claude-code-settings-for-unity", "qa", "referência", "OPTIONAL", "SAFE_TO_USE",
    "Configurações/skills de um especialista em testes Unity; referência para fluxo de testes com Claude.", risk="Repositório arquivado.",
    gh="nowsprinting/claude-code-settings-for-unity")
add("citronetic.unity-skill", "Citronetic/unity-claude-skill", "unity_world", "skill", "REJECTED", "DO_NOT_INSTALL",
    "Guia Unity 6+ em 16 tópicos.", risk="Sem licença declarada (não pode ser copiado); 0 estrelas; ~32 mil arquivos.", gh="Citronetic/unity-claude-skill")
add("donth77.blender-game-skills", "donth77/blender-game-skills", "blender_model", "skill", "OPTIONAL", "REVIEW_REQUIRED",
    "Concept art -> asset riggado; ideias de fases/gates para assets.", risk="Muito novo (0 estrelas), inclui scripts; fluxo image-to-3D fora da direção autoral.",
    gh="donth77/blender-game-skills")
add("levybytes.ai-skill-blender", "LevyBytes/AI-SKILL-blender", "blender_model", "skill (referência bpy)", "OPTIONAL", "DO_NOT_INSTALL",
    "Referência extensa da API bpy organizada em subskills.", risk="AGPL-3.0: não copiar para o repositório; consultar online apenas.",
    gh="LevyBytes/AI-SKILL-blender")
add("voltagent.awesome", "VoltAgent/awesome-agent-skills", "claude", "lista curada", "OPTIONAL", "SAFE_TO_USE",
    "Descoberta de skills oficiais/comunidade (1000+).", risk="Lista; cada item exige revisão própria.", gh="VoltAgent/awesome-agent-skills")
add("travisvn.awesome", "travisvn/awesome-claude-skills", "claude", "lista curada", "OPTIONAL", "SAFE_TO_USE", "Lista de skills e recursos.",
    gh="travisvn/awesome-claude-skills")
add("composio.awesome", "ComposioHQ/awesome-claude-skills", "claude", "lista curada", "OPTIONAL", "SAFE_TO_USE", "Lista grande por categoria.",
    gh="ComposioHQ/awesome-claude-skills")
add("ahujasid.blender-mcp", "ahujasid/blender-mcp", "claude", "MCP", "OPTIONAL", "DO_NOT_INSTALL",
    "Controle do Blender aberto via MCP (popular, 29,9k estrelas).",
    risk="Socket que executa Python arbitrário dentro do Blender; integrações opcionais com chaves de API. Desnecessário: usamos bpy headless versionado.",
    gh="ahujasid/blender-mcp")
add("coplay.unity-mcp", "CoplayDev/unity-mcp", "claude", "MCP", "OPTIONAL", "REVIEW_REQUIRED",
    "Controle do Editor Unity via MCP (cenas, assets, console); pode acelerar W5.",
    risk="Instala pacote Unity + servidor Python (uv); execução de comandos no Editor. Avaliar em branch isolada.", gh="CoplayDev/unity-mcp")
add("ivanmurzak.unity-mcp", "IvanMurzak/Unity-MCP", "claude", "MCP", "OPTIONAL", "REVIEW_REQUIRED", "Alternativa Apache-2.0 ao unity-mcp.",
    risk="Mesmo perfil de risco (execução no Editor).", gh="IvanMurzak/Unity-MCP")
add("github.mcp", "github/github-mcp-server", "build", "MCP", "REJECTED", "DO_NOT_INSTALL", "Operações GitHub via MCP.",
    risk="Exige token; redundante com o gh CLI já autenticado.", gh="github/github-mcp-server")
add("mcp.servers", "modelcontextprotocol/servers", "claude", "MCP (referência)", "REJECTED", "DO_NOT_INSTALL", "Servidores de referência MCP.",
    risk="Filesystem/git redundantes com ferramentas nativas do Claude Code.", gh="modelcontextprotocol/servers")

# ---------------------------------------------------------------- Blender
add("blender.lts", "Blender 5.2.1 LTS", "blender_model", "ferramenta", "ESSENTIAL", "SAFE_TO_USE",
    "Ferramenta principal de modelagem/geração; já instalada; LTS garante estabilidade da API.", url="https://www.blender.org/download/lts/",
    author="Blender Foundation", license="GPL-2.0-or-later (arquivos gerados são do autor)", version="5.2.1 LTS (build 2026-08-25)",
    install="Já instalado em C:/Program Files/Blender Foundation/Blender 5.2", notes="Fixar a série 5.2 LTS durante W2–W4.")
add("blender.api-docs", "Blender Python API 5.2", "blender_model", "referência", "ESSENTIAL", "SAFE_TO_USE", "Referência oficial bpy/bmesh/GN.",
    url="https://docs.blender.org/api/5.2/", author="Blender Foundation", license="CC-BY-SA (documentação)", version="5.2")
add("blender.gn", "Geometry Nodes (nativo)", "blender_proc", "recurso nativo", "ESSENTIAL", "SAFE_TO_USE",
    "Instancing em massa (já usado para 13k edificações), scattering, cabos, cercas, variação procedural.",
    url="https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html", author="Blender Foundation", license="GPL (parte do Blender)", version="5.2")
add("blender.assetbrowser", "Asset Browser + bibliotecas vinculadas", "blender_large", "recurso nativo", "RECOMMENDED", "SAFE_TO_USE",
    "Kit como biblioteca de assets (já marcado), linking entre .blend por camada/célula.",
    url="https://docs.blender.org/manual/en/latest/editors/asset_browser.html", author="Blender Foundation", license="GPL", version="5.2")
add("blender.bat", "Blender Asset Tracer (BAT v2)", "blender_large", "ferramenta CLI", "OPTIONAL", "REVIEW_REQUIRED",
    "Lista/empacota dependências de .blend (texturas, libs) — útil quando entrarem texturas e links.",
    url="https://projects.blender.org/blender/blender-asset-tracer", author="Blender Foundation (Sybren Stüvel)", license="GPL-2.0-or-later",
    version="v2 (requer Blender 5.1+)", risk="Ferramenta Python externa: revisar antes de executar.")
add("khronos.gltf", "glTF-Blender-IO", "pipeline", "add-on (embutido)", "RECOMMENDED", "SAFE_TO_USE", "Export glTF embutido; útil para revisão/web.",
    gh="KhronosGroup/glTF-Blender-IO", author="Khronos Group")
add("blender.fbx", "Exportador FBX nativo", "pipeline", "recurso nativo", "ESSENTIAL", "SAFE_TO_USE", "Formato padrão Blender -> Unity do projeto.",
    url="https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html", author="Blender Foundation", license="GPL", version="5.2")
add("ranjian0.building-tools", "building_tools", "blender_proc", "add-on", "OPTIONAL", "REVIEW_REQUIRED",
    "Gerador procedural de edifícios (paredes, janelas, portas, escadas); ideias para heróis futuros.",
    risk="Sobrepõe nosso gerador próprio (sa_arch); adicionar dependência sem necessidade.", gh="ranjian0/building_tools")
add("sverchok", "Sverchok", "blender_proc", "add-on", "OPTIONAL", "REVIEW_REQUIRED", "Nós paramétricos avançados.",
    risk="GPL-3; Geometry Nodes nativo cobre o necessário.", gh="nortikin/sverchok")
add("textools", "TexTools-Blender", "pbr", "add-on", "OPTIONAL", "REVIEW_REQUIRED", "Utilitários de UV/texel density/bake.",
    risk="Último push 2024-12 (risco de quebra no 5.2); GPL-3.", gh="franMarz/TexTools-Blender")
add("blendergis", "BlenderGIS", "terrain", "add-on", "OPTIONAL", "REVIEW_REQUIRED", "Técnica de DEM/OSM/georreferência (apenas estudo).",
    risk="Nunca importar cidade real como Santa Aurora; dados OSM são ODbL (share-alike).", gh="domlysz/BlenderGIS")
add("ant.landscape", "A.N.T. Landscape (extensão)", "terrain", "extensão", "OPTIONAL", "SAFE_TO_USE", "Terrenos procedurais simples.",
    url="https://extensions.blender.org/add-ons/antlandscape/", author="Blender community", license="GPL", version="extensão atual",
    notes="Nosso relevo vem de sa_terrain.py (determinístico); usar só para estudos.")
# ---------------------------------------------------------------- PBR / texture sources
add("materialmaker", "Material Maker", "pbr", "ferramenta standalone", "RECOMMENDED", "SAFE_TO_USE",
    "Autoria procedural de texturas PBR (tileables, trim sheets) exportando Base Color/Normal/Roughness/Metallic/AO para os slots já criados.",
    install="Executável standalone fora do repositório; texturas exportadas entram em ArtSource/Textures/<material>/.", gh="RodZill4/material-maker")
add("armortools", "ArmorPaint / ArmorTools", "pbr", "ferramenta", "OPTIONAL", "REVIEW_REQUIRED", "Pintura 3D PBR (fonte zlib; binários pagos).",
    risk="Compilar da fonte ou comprar; avaliar só se pintura 3D for necessária.", gh="armory3d/armortools")
add("polyhaven", "Poly Haven", "pbr", "fonte de assets", "ESSENTIAL", "SAFE_TO_USE",
    "Texturas, HDRIs e modelos CC0 (uso comercial livre) — referência e base de materiais/iluminação.",
    url="https://polyhaven.com/license", author="Poly Haven", license="CC0-1.0", version="por asset",
    notes="Registrar cada asset usado em Tools/Skills/asset_license_registry.csv (nome, URL, data).")
add("ambientcg", "ambientCG", "pbr", "fonte de assets", "ESSENTIAL", "SAFE_TO_USE", "Materiais PBR CC0 (concreto, tijolo, asfalto, metal...).",
    url="https://ambientcg.com/", author="Lennart Demes", license="CC0-1.0", version="por asset", notes="Registrar cada asset usado no registro de licenças.")
add("kenney", "Kenney", "pbr", "fonte de assets", "OPTIONAL", "SAFE_TO_USE", "Assets CC0 para protótipos/UI placeholder.",
    url="https://kenney.nl/support", author="Kenney", license="CC0-1.0", version="por pacote", risk="Estilo low-poly: nunca como arte final.")
add("megascans.fab", "Megascans / Fab", "pbr", "marketplace", "REJECTED", "REVIEW_REQUIRED",
    "Scans fotogramétricos de altíssima qualidade.", url="https://www.fab.com/", author="Epic Games", license="Fab Standard License (qualquer engine; maioria paga desde 2025)",
    version="—", risk="Termos e preços mudaram em 2024–2025; exige revisão jurídica e orçamento antes de qualquer uso.")
add("substance", "Adobe Substance 3D Painter/Designer", "pbr", "ferramenta comercial", "OPTIONAL", "REVIEW_REQUIRED",
    "Padrão da indústria para texturização.", url="https://www.adobe.com/products/substance3d.html", author="Adobe", license="Assinatura comercial",
    version="—", risk="Custo recorrente; preferir open source/CC0 primeiro.")
# ---------------------------------------------------------------- terrain / procedural references
add("osm.data", "OpenStreetMap (dados)", "terrain", "dados", "REJECTED", "DO_NOT_INSTALL", "Dados urbanos reais.",
    url="https://www.openstreetmap.org/copyright", author="OSM contributors", license="ODbL-1.0", version="—",
    risk="Share-alike e cidade real: proibido como conteúdo de Santa Aurora; só estudo de técnica.")
add("parish-muller", "Parish & Müller — Procedural Modeling of Cities (SIGGRAPH 2001)", "blender_proc", "artigo", "RECOMMENDED", "SAFE_TO_USE",
    "Fundamento de redes viárias L-system e lotes; base conceitual do nosso gerador.", url="https://doi.org/10.1145/383259.383292",
    author="Y. Parish, P. Müller", license="Artigo acadêmico (citar)", version="2001")
add("wfc", "WaveFunctionCollapse", "blender_proc", "algoritmo (referência)", "OPTIONAL", "SAFE_TO_USE", "Geração por restrições (fachadas, interiores).",
    gh="mxgmn/WaveFunctionCollapse", author="Maxim Gumin")
add("watabou.town", "TownGeneratorOS", "blender_proc", "referência", "OPTIONAL", "DO_NOT_INSTALL", "Gerador de cidades medievais (ideias de malha).",
    risk="GPL-3: não copiar código; só inspiração.", gh="watabou/TownGeneratorOS")
add("unity.terrain-tools", "Unity Terrain Tools (com.unity.terrain-tools)", "terrain", "pacote Unity", "OPTIONAL", "SAFE_TO_USE",
    "Ferramentas de terreno Unity (se for usado Terrain em vez de malha Blender).", url="https://docs.unity3d.com/Packages/com.unity.terrain-tools@latest",
    author="Unity", license="Unity Companion License", version="via Package Manager", notes="Nosso terreno vem do Blender (malha por subcélula).")
# ---------------------------------------------------------------- Unity large world
add("unity.urp", "Universal Render Pipeline 17.6.0", "unity_visual", "pacote Unity", "ESSENTIAL", "SAFE_TO_USE",
    "Pipeline do projeto: SRP Batcher, decals, reflection/light probes, Shader Graph.", url="https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/manual/index.html",
    author="Unity", license="Unity Companion License", version="17.6.0 (instalado)")
add("unity.addressables", "Addressables (com.unity.addressables)", "unity_world", "pacote Unity", "ESSENTIAL", "SAFE_TO_USE",
    "Carregamento assíncrono por grupos/rótulos — base do streaming por subcélula e cenas aditivas.",
    url="https://docs.unity3d.com/Packages/com.unity.addressables@latest", author="Unity", license="Unity Companion License",
    version="instalar pela versão verificada do Unity 6000.6 e fixar no manifest", install="Package Manager (com aprovação, na etapa W5).")
add("unity.additive-scenes", "Cenas aditivas (SceneManager.LoadSceneAsync Additive)", "unity_world", "técnica nativa", "ESSENTIAL", "SAFE_TO_USE",
    "Uma cena por macrocélula + cenas de heróis; descarregamento por distância.", url="https://docs.unity3d.com/6000.6/Documentation/ScriptReference/SceneManagement.SceneManager.LoadSceneAsync.html",
    author="Unity", license="Unity EULA", version="6000.6")
add("unity.lod", "LODGroup / GPU instancing / SRP Batcher / occlusion culling", "unity_world", "técnica nativa", "ESSENTIAL", "SAFE_TO_USE",
    "LOD por convenção _LODn, instancing das 47 variantes, oclusão bakeada por célula, streaming de texturas (mipmap streaming).",
    url="https://docs.unity3d.com/6000.6/Documentation/Manual/LevelOfDetail.html", author="Unity", license="Unity EULA", version="6000.6",
    notes="8 km com origem no centro: coordenadas máximas de ~4 km mantêm precisão sub-milimétrica; floating origin não é necessário agora.")
add("unity.hlod", "Unity-Technologies/HLODSystem", "unity_world", "pacote experimental", "REJECTED", "DO_NOT_INSTALL", "HLOD experimental.",
    risk="Sem licença no repositório e sem atividade desde 2024; gerar HLOD/proxies no Blender (controle total).", gh="Unity-Technologies/HLODSystem")
add("unity.autolod", "Unity-Technologies/AutoLOD", "unity_world", "pacote experimental", "REJECTED", "DO_NOT_INSTALL", "Geração automática de LOD.",
    risk="Experimental, parado desde 2024; LODs serão autorados/gerados no Blender.", gh="Unity-Technologies/AutoLOD")
add("unity.splines", "Splines (com.unity.splines)", "unity_world", "pacote Unity", "OPTIONAL", "SAFE_TO_USE", "Splines para cabos/ruas/rotas em runtime.",
    url="https://docs.unity3d.com/Packages/com.unity.splines@latest", author="Unity", license="Unity Companion License", version="via Package Manager")
add("unity.cs-reference", "UnityCsReference", "unity_world", "referência de código", "RECOMMENDED", "SAFE_TO_USE",
    "Código C# do Editor/Engine para entender comportamento exato de APIs.", risk="Licença reference-only: ler, nunca copiar para o projeto.",
    gh="Unity-Technologies/UnityCsReference", author="Unity")
add("unity.boatattack", "BoatAttack (amostra URP)", "unity_visual", "projeto de referência", "OPTIONAL", "SAFE_TO_USE", "Técnicas URP (água, iluminação, LOD).",
    gh="Unity-Technologies/BoatAttack", author="Unity")
add("unity.graphics", "Unity Graphics (fonte URP/Shader Graph/VFX)", "unity_visual", "referência de código", "OPTIONAL", "SAFE_TO_USE",
    "Fonte dos pacotes gráficos para depurar URP.", gh="Unity-Technologies/Graphics", author="Unity")
# ---------------------------------------------------------------- Unity gameplay / visual
add("unity.inputsystem", "Input System 1.19.0", "unity_gameplay", "pacote Unity", "ESSENTIAL", "SAFE_TO_USE",
    "Já usado no Interaction.cs; remapeamento, gamepad, sensibilidade, acessibilidade.", gh="Unity-Technologies/InputSystem", author="Unity",
    notes="Instalado: 1.19.0 (repo indica 1.20.0 disponível; atualizar só com teste).")
add("unity.shadergraph", "Shader Graph (URP)", "unity_visual", "pacote Unity", "RECOMMENDED", "SAFE_TO_USE", "Molhado/chuva, decals, materiais em camadas.",
    url="https://docs.unity3d.com/Packages/com.unity.shadergraph@latest", author="Unity", license="Unity Companion License", version="acompanha URP 17.6")
add("unity.vfxgraph", "VFX Graph", "audio_vfx", "pacote Unity", "OPTIONAL", "SAFE_TO_USE", "Chuva/faíscas/vapor em grande escala (GPU).",
    url="https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@latest", author="Unity", license="Unity Companion License",
    version="via Package Manager", notes="Para efeitos pequenos (vazamento, faísca, poeira) o Particle System nativo basta.")
add("unity.animation-rigging", "Animation Rigging", "animation", "pacote Unity", "RECOMMENDED", "SAFE_TO_USE",
    "IK das mãos em primeira pessoa (segurar ferramentas, apertar, inspecionar).", url="https://docs.unity3d.com/Packages/com.unity.animation.rigging@latest",
    author="Unity", license="Unity Companion License", version="via Package Manager")
add("unity.ai-navigation", "AI Navigation 2.0.12", "ai_npc", "pacote Unity", "ESSENTIAL", "SAFE_TO_USE",
    "NavMesh por cena/célula, NavMeshLinks, obstáculos — NPCs clientes/funcionários.", url="https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html",
    author="Unity", license="Unity Companion License", version="2.0.12 (instalado)")
add("unity.navmeshcomponents", "NavMeshComponents (legado)", "ai_npc", "repositório legado", "REJECTED", "DO_NOT_INSTALL",
    "Substituído pelo pacote AI Navigation.", gh="Unity-Technologies/NavMeshComponents")
add("unity.wheelcollider", "WheelCollider (nativo) + controlador próprio", "vehicles", "técnica nativa", "ESSENTIAL", "SAFE_TO_USE",
    "Veículo arcade/realista híbrido leve sem dependências; entrar/sair, carga, estacionamento.",
    url="https://docs.unity3d.com/6000.6/Documentation/Manual/class-WheelCollider.html", author="Unity", license="Unity EULA", version="6000.6",
    notes="Evitar sistemas comerciais pesados (NWH/Edy's) até haver necessidade comprovada.")
add("unity.localization", "Localization (com.unity.localization)", "loc_access", "pacote Unity", "RECOMMENDED", "SAFE_TO_USE",
    "String tables, smart strings, plural, pseudo-localização para QA de expansão de texto.", url="https://docs.unity3d.com/Packages/com.unity.localization@latest",
    author="Unity", license="Unity Companion License", version="via Package Manager")
add("unity.uitoolkit", "UI Toolkit (nativo)", "ui", "recurso nativo", "ESSENTIAL", "SAFE_TO_USE",
    "Migração do tablet provisório (TabletUI.cs) — job board, inventário, finanças, mapa.", url="https://docs.unity3d.com/6000.6/Documentation/Manual/UIElements.html",
    author="Unity", license="Unity EULA", version="6000.6")
add("unity.newtonsoft", "Newtonsoft Json (com.unity.nuget.newtonsoft-json)", "save", "pacote Unity", "RECOMMENDED", "SAFE_TO_USE",
    "Saves versionados com migração (JObject), mais flexível que JsonUtility.", url="https://docs.unity3d.com/Packages/com.unity.nuget.newtonsoft-json@latest",
    author="Unity/James Newton-King", license="MIT", version="via Package Manager")
add("messagepack", "MessagePack-CSharp", "save", "biblioteca", "OPTIONAL", "REVIEW_REQUIRED", "Serialização binária rápida.",
    risk="Saves binários dificultam depuração e migração; JSON primeiro.", gh="MessagePack-CSharp/MessagePack-CSharp")
add("unitask", "UniTask", "unity_gameplay", "biblioteca", "OPTIONAL", "REVIEW_REQUIRED", "Async sem alocação.",
    risk="Unity 6 tem Awaitable nativo; adicionar só se medido necessário.", gh="Cysharp/UniTask")
add("vcontainer", "VContainer", "unity_gameplay", "biblioteca DI", "OPTIONAL", "REVIEW_REQUIRED", "Injeção de dependência leve.",
    risk="Evitar overengineering; serviços simples bastam no escopo atual.", gh="hadashiA/VContainer")
add("unity.gpp-demo", "Game Programming Patterns demo (Unity)", "unity_gameplay", "projeto de referência", "OPTIONAL", "SAFE_TO_USE",
    "Padrões (state, observer, command) aplicados em Unity.", gh="Unity-Technologies/game-programming-patterns-demo", author="Unity")
add("gpp.book", "Game Programming Patterns (livro online)", "unity_gameplay", "referência", "RECOMMENDED", "SAFE_TO_USE",
    "State machines, event queue, service locator, component — base para arquitetura modesta.", url="https://gameprogrammingpatterns.com/",
    author="Robert Nystrom", license="Leitura gratuita online (direitos do autor)", version="web")
add("unity.fpssample", "FPSSample", "unity_gameplay", "projeto de referência", "OPTIONAL", "SAFE_TO_USE", "Referência de controlador FP/arquitetura.",
    risk="Arquivado/antigo (HDRP).", gh="Unity-Technologies/FPSSample", author="Unity")
# ---------------------------------------------------------------- performance
add("unity.profiler", "Unity Profiler + Frame Debugger", "performance", "ferramenta nativa", "ESSENTIAL", "SAFE_TO_USE", "CPU/GPU/memória por frame; draw calls.",
    url="https://docs.unity3d.com/6000.6/Documentation/Manual/Profiler.html", author="Unity", license="Unity EULA", version="6000.6")
add("unity.memoryprofiler", "Memory Profiler (com.unity.memoryprofiler)", "performance", "pacote Unity", "ESSENTIAL", "SAFE_TO_USE",
    "Snapshots e comparação de memória para orçamentos por célula.", url="https://docs.unity3d.com/Packages/com.unity.memoryprofiler@latest",
    author="Unity", license="Unity Companion License", version="via Package Manager")
add("unity.profileanalyzer", "Profile Analyzer", "performance", "pacote Unity", "RECOMMENDED", "SAFE_TO_USE", "Estatística de muitos frames (antes/depois).",
    url="https://docs.unity3d.com/Packages/com.unity.performance.profile-analyzer@latest", author="Unity", license="Unity Companion License", version="via Package Manager")
add("unity.projectauditor", "Project Auditor", "performance", "módulo Unity", "RECOMMENDED", "SAFE_TO_USE",
    "Análise estática de código/assets/shaders/settings; embutido no Unity 6.4+ (Window > Analysis).",
    gh="Unity-Technologies/ProjectAuditor", author="Unity", notes="No 6000.6 é módulo do Editor; instalar só o pacote de regras se necessário.")
add("renderdoc", "RenderDoc", "performance", "ferramenta", "RECOMMENDED", "SAFE_TO_USE", "Captura de frame GPU, overdraw, texturas, draw calls.",
    install="Instalador oficial (renderdoc.org); fora do repositório.", gh="baldurk/renderdoc", author="Baldur Karlsson")
add("nsight", "NVIDIA Nsight Graphics", "performance", "ferramenta", "OPTIONAL", "SAFE_TO_USE", "Profiling GPU NVIDIA aprofundado.",
    url="https://developer.nvidia.com/nsight-graphics", author="NVIDIA", license="Gratuito (proprietário)", version="atual")
# ---------------------------------------------------------------- QA
add("unity.testframework", "Unity Test Framework 1.8.0", "qa", "pacote Unity", "ESSENTIAL", "SAFE_TO_USE",
    "EditMode/PlayMode; smoke tests (RuntimeSmoke já existe), migração de saves, validadores de assets.",
    url="https://docs.unity3d.com/Packages/com.unity.test-framework@1.8/manual/index.html", author="Unity", license="Unity Companion License", version="1.8.0 (instalado)")
add("unity.perftesting", "Performance Testing Extension", "qa", "pacote Unity", "RECOMMENDED", "SAFE_TO_USE", "Medições de desempenho reproduzíveis em testes.",
    url="https://docs.unity3d.com/Packages/com.unity.test-framework.performance@latest", author="Unity", license="Unity Companion License", version="via Package Manager")
add("pillow", "Pillow (já instalado)", "qa", "biblioteca Python", "ESSENTIAL", "SAFE_TO_USE", "Diferença de imagens/contato visual sem nova dependência.",
    url="https://python-pillow.org/", author="Pillow contributors", license="MIT-CMU (HPND)", version="12.3.0 (instalado)")
add("pixelmatch", "pixelmatch", "qa", "biblioteca", "OPTIONAL", "REVIEW_REQUIRED", "Diff perceptual de imagens.", risk="Node; Pillow cobre o necessário.", gh="mapbox/pixelmatch")
add("odiff", "odiff", "qa", "ferramenta", "OPTIONAL", "REVIEW_REQUIRED", "Diff de imagens muito rápido.", risk="Binário nativo; só se o volume exigir.", gh="dmtrKovalenko/odiff")
# ---------------------------------------------------------------- build / git
add("own.build-ps1", "Tools/Build.ps1 + Test-Windows.ps1 (existentes)", "build", "automação própria", "ESSENTIAL", "SAFE_TO_USE",
    "Build Unity em batchmode já funcional; base para smoke launch automatizado.", url="Tools/Build.ps1", author="Facility Ops",
    license="Licença do repositório", version="atual")
add("gh.actions", "GitHub Actions (validadores Python)", "build", "CI", "RECOMMENDED", "SAFE_TO_USE",
    "Rodar validate_masterplan.py e build_catalog.py a cada push (sem licença Unity, sem segredos).",
    url="https://docs.github.com/actions", author="GitHub", license="Serviço GitHub", version="—",
    install="Workflow .github/workflows/ (propor com aprovação; não depende de credenciais).")
add("gameci.builder", "GameCI unity-builder", "build", "GitHub Action", "OPTIONAL", "REVIEW_REQUIRED", "Build Unity em CI.",
    risk="Exige ativação de licença Unity como segredo no GitHub; decidir com o usuário.", gh="game-ci/unity-builder")
add("gameci.testrunner", "GameCI unity-test-runner", "qa", "GitHub Action", "OPTIONAL", "REVIEW_REQUIRED", "Testes Unity em CI.",
    risk="Mesmo requisito de licença/segredos.", gh="game-ci/unity-test-runner")
add("gitlfs", "Git LFS", "build", "ferramenta", "RECOMMENDED", "REVIEW_REQUIRED",
    "Para binários grandes futuros (texturas 4K, FBX, .blend de produção). Instalado (3.7.1), ainda não usado.",
    risk="Não reescrever histórico existente; cota de banda/armazenamento do GitHub; decidir com o usuário antes de ativar.", gh="git-lfs/git-lfs")
add("github.gitignore", "github/gitignore (Unity.gitignore)", "build", "referência", "RECOMMENDED", "SAFE_TO_USE", "Comparar com o .gitignore atual.",
    gh="github/gitignore", author="GitHub")
add("keepachangelog", "Keep a Changelog", "docs", "convenção", "RECOMMENDED", "SAFE_TO_USE", "Formato de CHANGELOG por marco (W1, W1.5...).",
    gh="olivierlacan/keep-a-changelog", author="Olivier Lacan")
add("adr", "Architecture Decision Records (modelos)", "docs", "convenção", "RECOMMENDED", "SAFE_TO_USE",
    "Registrar decisões (terreno, streaming, LFS) em Docs/ADR/NNNN-*.md com um template próprio.",
    gh="joelparkerhenderson/architecture-decision-record", author="Joel Parker Henderson")
add("adr-tools", "adr-tools", "docs", "ferramenta", "OPTIONAL", "REVIEW_REQUIRED", "CLI para ADRs.", risk="GPL-3 e bash; um template markdown basta.",
    gh="npryce/adr-tools", author="Nat Pryce")
add("reuse", "REUSE (FSFE)", "licenses", "ferramenta/convenção", "OPTIONAL", "REVIEW_REQUIRED", "Conformidade de licenças com SPDX.",
    risk="Ferramenta GPL (não é distribuída com o jogo); um registro CSV próprio cobre o necessário agora.", gh="fsfe/reuse-tool")
# ---------------------------------------------------------------- Steam
add("steamworks.sdk", "Steamworks SDK + documentação", "steam", "SDK", "RECOMMENDED", "REVIEW_REQUIRED",
    "Conquistas, stats, Steam Cloud, Rich Presence, Steam Input, SteamPipe (upload de depots).", url="https://partner.steamgames.com/doc/home",
    author="Valve", license="Steamworks SDK Access Agreement (parceiro)", version="—", risk="Exige conta de parceiro; não integrar ainda.")
add("steamworks.net", "Steamworks.NET", "steam", "wrapper C#", "RECOMMENDED", "REVIEW_REQUIRED", "Wrapper fiel da API Steamworks para Unity.",
    risk="Integrar só na etapa Steam; fixar versão compatível com o SDK.", gh="rlabrecque/Steamworks.NET", author="Riley Labrecque")
add("facepunch.steamworks", "Facepunch.Steamworks", "steam", "wrapper C#", "OPTIONAL", "REVIEW_REQUIRED", "Wrapper C# idiomático alternativo.",
    gh="Facepunch/Facepunch.Steamworks")
add("steam.cloud", "Steam Cloud (Auto-Cloud)", "steam", "serviço", "RECOMMENDED", "SAFE_TO_USE",
    "Saves em pasta fixa por perfil, nomes estáveis e arquivos pequenos -> compatível com Auto-Cloud sem código.",
    url="https://partner.steamgames.com/doc/features/cloud", author="Valve", license="Serviço Steam", version="—")
# ---------------------------------------------------------------- audio / vfx
add("steamaudio", "Steam Audio", "audio_vfx", "SDK de áudio", "RECOMMENDED", "REVIEW_REQUIRED",
    "Oclusão/transmissão/reverb físico para interiores técnicos (bombas, HVAC, zumbido elétrico).", risk="Plugin nativo; avaliar custo de CPU.",
    gh="ValveSoftware/steam-audio", author="Valve")
add("fmod", "FMOD Studio", "audio_vfx", "middleware", "OPTIONAL", "REVIEW_REQUIRED", "Áudio adaptativo/zonas de ambiente.",
    url="https://www.fmod.com/licensing", author="Firelight Technologies", license="Proprietária (licença indie gratuita até limite de receita)", version="—",
    risk="Licença por faturamento; o mixer nativo da Unity + Steam Audio cobre o início.")
# ---------------------------------------------------------------- accessibility / design references
add("gag", "Game Accessibility Guidelines", "loc_access", "referência", "ESSENTIAL", "SAFE_TO_USE",
    "Legendas, remapeamento, contraste, movimento reduzido, indicadores de interação.", url="https://gameaccessibilityguidelines.com/",
    author="Game Accessibility Guidelines", license="Leitura livre", version="web")
add("xag", "Xbox Accessibility Guidelines", "loc_access", "referência", "RECOMMENDED", "SAFE_TO_USE", "Checklist detalhado de acessibilidade.",
    url="https://learn.microsoft.com/gaming/accessibility/guidelines", author="Microsoft", license="Documentação", version="web")
add("own.economy-sim", "Simulador de economia próprio (Python, a criar)", "economy", "automação própria", "RECOMMENDED", "SAFE_TO_USE",
    "Rodar milhares de carreiras simuladas (chamados, custos, reputação) para provar 'difícil porém recuperável' e ausência de softlock.",
    url="(a criar em Tools/Balance/)", author="Facility Ops", license="Licença do repositório", version="planejado")
add("machinations", "Machinations", "economy", "SaaS", "OPTIONAL", "REVIEW_REQUIRED", "Modelagem visual de economias de jogos.",
    url="https://machinations.io/", author="Machinations", license="Proprietária (planos)", version="—", risk="Dados do design em serviço externo.")

CATS = {
    "claude": ("01_CLAUDE_CODE.md", "Claude Code, Agent Skills e MCP"),
    "blender_model": ("02_BLENDER_MODELAGEM.md", "Blender: modelagem, arquitetura e kits"),
    "blender_proc": ("03_BLENDER_PROCEDURAL.md", "Blender: procedural e Geometry Nodes"),
    "blender_large": ("04_BLENDER_LARGE_WORLD.md", "Blender: grandes cenas"),
    "pbr": ("05_PBR_TEXTURAS.md", "PBR, UV e texturas"),
    "terrain": ("05_PBR_TEXTURAS.md", "Terreno / GIS (apenas técnica)"),
    "unity_world": ("06_UNITY_LARGE_WORLD.md", "Unity: mundo grande e streaming"),
    "unity_visual": ("06_UNITY_LARGE_WORLD.md", "Unity: URP e visual"),
    "unity_gameplay": ("07_UNITY_GAMEPLAY.md", "Unity: gameplay, arquitetura e sistemas"),
    "animation": ("08_ANIMACAO.md", "Animação"),
    "vehicles": ("09_VEICULOS.md", "Veículos"),
    "ai_npc": ("10_AI_NPC.md", "NPC e IA"),
    "economy": ("11_ECONOMIA_PROGRESSAO.md", "Economia e progressão"),
    "save": ("12_SAVE_DATA.md", "Save e dados"),
    "ui": ("13_UI_UX.md", "UI/UX"),
    "audio_vfx": ("14_AUDIO_VFX.md", "Áudio, VFX e clima"),
    "performance": ("15_PERFORMANCE.md", "Performance"),
    "qa": ("16_QA_TESTES.md", "QA e testes automatizados"),
    "build": ("17_BUILD_GITHUB.md", "Build, Git e GitHub"),
    "docs": ("17_BUILD_GITHUB.md", "Documentação"),
    "steam": ("18_STEAM.md", "Steam"),
    "loc_access": ("19_LOCALIZACAO_ACESSIBILIDADE.md", "Localização e acessibilidade"),
    "pipeline": ("20_ASSET_PIPELINE.md", "Pipeline Blender → Unity"),
    "licenses": ("21_LICENCAS.md", "Licenças"),
}

TOP10 = ["own.santa-aurora-world-pipeline", "own.blender-headless-bpy", "blender.lts", "blender.gn", "polyhaven", "ambientcg", "materialmaker",
         "nicewolf.unity-skills", "unity.addressables", "unity.testframework"]
TOP5 = ["own.santa-aurora-world-pipeline", "own.blender-headless-bpy", "materialmaker", "polyhaven", "own.visual-review"]

catalog = {"schemaVersion": 1, "generated": "2026-10-03", "generator": "Tools/Skills/build_catalog.py",
           "policy": {"install": "Nada instalado; ativação de skills só copiando para .claude/skills/ com aprovação explícita.",
                      "execution": "Nenhum código externo executado; metadados lidos via `gh api` (somente leitura).",
                      "credentials": "Nenhuma credencial armazenada; MCPs que exigem token marcados DO_NOT_INSTALL.",
                      "copying": "Copiado apenas markdown com licença permissiva (MIT), com LICENSE e PROVENANCE.md; o resto por referência."},
           "classification": {"priority": ["ESSENTIAL", "RECOMMENDED", "OPTIONAL", "REJECTED"], "safety": ["SAFE_TO_USE", "REVIEW_REQUIRED", "DO_NOT_INSTALL"]},
           "top10": TOP10, "top5_w15_w2": TOP5, "items": E}
ids = [e["id"] for e in E]
assert len(ids) == len(set(ids)), "duplicate ids"
assert all(t in ids for t in TOP10 + TOP5)
for e in E:
    assert e["priority"] in catalog["classification"]["priority"] and e["safety"] in catalog["classification"]["safety"], e["id"]
    assert e["category"] in CATS, e["id"]
out = root / "Tools" / "Skills" / "catalog.json"
out.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def table(items):
    rows = ["| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |",
            "|---|---|---|---|---|---|---|---|"]
    for e in items:
        link = f"[{e['name']}]({e['url']})" if e.get("url") and str(e["url"]).startswith("http") else f"{e['name']} (`{e.get('url')}`)"
        ver = e.get("version") or "—"
        if e.get("commit"):
            ver += f" / `{e['commit'][:12]}`"
        rows.append(f"| {link} | {e.get('license') or '—'} | {ver} | {e.get('lastUpdate') or '—'} | **{e['priority']}** | {e['safety']} | "
                    f"{e['storage'].replace('saved:', 'salvo: `') + '`' if e['storage'].startswith('saved:') else 'referência'} | {e['value']} |")
    risks = [f"- **{e['name']}**: {e['risk']}" for e in items if e.get("risk")]
    notes = [f"- **{e['name']}**: {e['notes']}" for e in items if e.get("notes")]
    inst = [f"- **{e['name']}**: {e['install']}" for e in items if e.get("install")]
    s = "\n".join(rows)
    if risks:
        s += "\n\n**Riscos**\n\n" + "\n".join(risks)
    if inst:
        s += "\n\n**Instalação (somente com aprovação)**\n\n" + "\n".join(inst)
    if notes:
        s += "\n\n**Notas**\n\n" + "\n".join(notes)
    return s


sys.path.insert(0, str(root / "Tools" / "Skills"))
from guides_pt import GUIDES  # noqa: E402
docs_dir = root / "Docs" / "SKILLS"
docs_dir.mkdir(parents=True, exist_ok=True)
files = {}
for cat, (fname, title) in CATS.items():
    files.setdefault(fname, []).append((cat, title))
for fname, cats in files.items():
    parts = [f"# {GUIDES[fname]['title']}\n", "Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). "
             "Nada aqui foi instalado ou executado.\n", GUIDES[fname]["intro"] + "\n"]
    for cat, title in cats:
        items = [e for e in E if e["category"] == cat]
        parts.append(f"## {title}\n\n{table(items)}\n")
    if GUIDES[fname].get("workflow"):
        parts.append("## Workflow recomendado\n\n" + GUIDES[fname]["workflow"] + "\n")
    (docs_dir / fname).write_text("\n".join(parts), encoding="utf-8")
for fname in ("00_INDICE_GERAL.md", "21_LICENCAS.md", "22_RECOMENDACOES.md"):
    g = GUIDES[fname]
    body = g["body"]
    if fname == "22_RECOMENDACOES.md":
        byid = {e["id"]: e for e in E}
        body = body.replace("{{TOP10}}", "\n".join(f"{k + 1}. **{byid[i]['name']}**: {byid[i]['value']}" for k, i in enumerate(TOP10)))
        body = body.replace("{{TOP5}}", "\n".join(f"{k + 1}. **{byid[i]['name']}**" for k, i in enumerate(TOP5)))
        rej = [e for e in E if e["priority"] == "REJECTED"]
        body = body.replace("{{REJECTED}}", "\n".join(f"- **{e['name']}**: {e.get('risk') or e['value']}" for e in rej))
        dni = [e for e in E if e["safety"] == "DO_NOT_INSTALL"]
        body = body.replace("{{DNI}}", "\n".join(f"- **{e['name']}**: {e.get('risk') or ''}" for e in dni))
    if fname == "00_INDICE_GERAL.md":
        counts = {}
        for e in E:
            counts[e["priority"]] = counts.get(e["priority"], 0) + 1
        saved = [e for e in E if e["storage"].startswith("saved:")]
        body = body.replace("{{COUNTS}}", ", ".join(f"{k}: {v}" for k, v in counts.items()) + f" (total {len(E)})")
        body = body.replace("{{SAVED}}", "\n".join(f"- **{e['name']}** → `{e['storage'][6:]}`" for e in saved))
    if fname == "21_LICENCAS.md":
        body = body.replace("{{LIC}}", table([e for e in E if e["category"] == "licenses"]))
    (docs_dir / fname).write_text(f"# {g['title']}\n\n{body}\n", encoding="utf-8")
print(f"catalog: {len(E)} items; docs: {len(list(docs_dir.glob('*.md')))} files")
