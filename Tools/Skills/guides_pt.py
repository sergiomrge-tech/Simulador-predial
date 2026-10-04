"""Textos dos documentos Docs/SKILLS (workflows e orientações). Usado por build_catalog.py."""

GUIDES = {
"00_INDICE_GERAL.md": {"title": "Biblioteca de Skills e Ferramentas — Índice Geral", "body": """\
**Etapa B da fila noturna (W1.5 → B), 2026-10-03.**

Esta é uma biblioteca curada de skills, workflows, MCPs, ferramentas e referências para produzir Facility Ops / Simulador Predial do mundo à Steam. Princípios: **poucos recursos excelentes, automação própria, ferramentas maduras e controle total do pipeline.** Nada foi instalado e nenhum código externo foi executado. Os metadados vieram da API pública do GitHub (`gh api`, só leitura), com licença, último push, release e commit fixado.

Itens no catálogo: {{COUNTS}}.

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
{{SAVED}}

Tudo o mais fica **por referência** (URL + versão/commit no `catalog.json`).

## Como regenerar
```
python Tools/Skills/build_catalog.py .
```
"""},

"01_CLAUDE_CODE.md": {"title": "01 — Claude Code, Agent Skills e MCP", "intro": """\
O Claude Code carrega skills de `.claude/skills/` (projeto), `~/.claude/skills/` (usuário) e de plugins. **Por isso a biblioteca fica em `Tools/Skills/`: guardada, versionada e inerte.** Ativar uma skill é copiá-la para `.claude/skills/`, sempre com aprovação, e revisando o campo `allowed-tools` e qualquer `` !`comando` `` (a documentação oficial alerta que skills podem executar comandos).""", "workflow": """\
1. **Skills próprias primeiro.** Elas descrevem o *nosso* pipeline (validadores, geradores, convenções), exatamente o que skills genéricas não sabem.
2. Skills de terceiros: só markdown, licença permissiva, commit fixado, `PROVENANCE.md` com hash do tarball e varredura de shell injection/allowed-tools. Scripts e hooks ficam de fora.
3. MCPs: o projeto já automatiza Blender (bpy headless versionado) e GitHub (`gh` autenticado). MCPs de controle do Blender ou da Unity aumentam a superfície de execução. Avaliar o `unity-mcp` só na etapa W5, em branch isolada.
4. Toda skill nova passa pela checagem `claude plugin validate` (quando for plugin) e por revisão humana antes de ir para `.claude/skills/`.
"""},

"02_BLENDER_MODELAGEM.md": {"title": "02 — Blender: modelagem, arquitetura, kits e salas técnicas", "intro": """\
A modelagem de produção segue a Art Bible: escala métrica, bordas chanfradas, espessura real, peças separadas onde a câmera chega perto. O W1.5 já criou o construtor paramétrico (`Tools/Blender/sa_arch.py`), o kit modular (`sa_kit.py`) e os heróis (`sa_heroes.py`). A estratégia é **automação própria + autoria manual nos heróis**, não add-ons genéricos.""", "workflow": """\
**Hard-surface e arquitetura (heróis, W2–W4)**
- Bevel com perfil e 2–3 segmentos nas quinas visíveis; *weighted normals* (modificador nativo) para sombreamento limpo; sharp edges por ângulo de 30–35°.
- Kit modular com grade de 0,5 m e alturas de piso de 3,0 m (residencial) e 4–5 m (comercial/técnico); pivôs na face externa inferior; cada peça com LOD0 bevelado e LOD1 simplificado.
- Janelas e portas: batente, folha, vidro e peitoril como peças separadas (já assim no kit); grades com barras de 12–16 mm.
- Telhados com espessura, beiral, calha e rufos; telhas cerâmicas por textura + bump nos LODs distantes e geometria na borda/cumeeira de perto.
- Escadas: espelho de 17–18 cm e piso de 28 cm (regra 2E+P≈63 cm); corrimão a 0,90 m.

**Salas técnicas (diferencial do jogo)**
- Quadros elétricos, bombas, HVAC e geradores: modelar a partir de catálogos genéricos e de fotos *próprias* (nunca de assets de terceiros), com marcas fictícias.
- Tubulação por curvas (Curve → bevel circular de 16–24 lados de perto), flanges e suportes como peças instanciadas.
- Elementos interativos (registros, disjuntores, painéis) com pivô e eixo corretos para animação na Unity.

**Veículos, mobiliário e ferramentas**: hero props com 1024 px/m, desgaste coerente (Art Bible §7) e marcas fictícias.
"""},

"03_BLENDER_PROCEDURAL.md": {"title": "03 — Blender: procedural e Geometry Nodes", "intro": """\
Santa Aurora já é procedural: ruas, calçadas, cruzamentos, lotes, famílias, infraestrutura e vegetação vêm de `Tools/Map/` (Python determinístico) e são instanciados por Geometry Nodes. Add-ons procedurais de terceiros duplicariam essa base.""", "workflow": """\
- **Ruas e calçadas**: grafo → faixas de pista, calçadas elevadas 15 cm com meio-fio, esquinas e faixas de pedestre (já em `create_oldtown_base.py`). Próximo passo: esquinas curvas (filete) e rebaixos de calçada em garagens.
- **Postes, fios e cabos**: pontos já gerados; cabos entre postes por catenária (Curve com 8–12 pontos, flecha de 0,5–1,0 m) num grupo GN *Curve to Mesh*.
- **Muros e cercas**: GN *Resample Curve* + *Instance on Points* com peças do kit (`KIT_Muro_2m`, pilares).
- **Fachadas**: variação por seed (variantes) + quebra de repetição com decals e acessórios (condensadores, toldos, placas) distribuídos por regras, não por acaso.
- **Scattering**: distribuição por máscaras (calçada, praça, terreno vazio) com distância mínima (*Distribute Points on Faces* em modo Poisson).
- **Sinalização e infraestrutura**: regras por tipo de cruzamento (já: semáforo em principal×principal, PARE em local→principal).
- Referência conceitual: Parish & Müller (2001). WFC pode ajudar em interiores repetitivos.
"""},

"04_BLENDER_LARGE_WORLD.md": {"title": "04 — Blender: grandes cenas", "intro": """\
O W1.5 já trabalha em grande escala: 13 mil edificações instanciadas, 181 subcélulas e 8 camadas em um `.blend` de 28 MB que reabre em segundos.""", "workflow": """\
- **Coleções por camada × célula** (`OT_<Camada>_SA_Mxx_yy`) e objetos por subcélula. Facilita exportação, revisão e streaming.
- **Instancing por GN** com bibliotecas ocultas; uma malha por variante. Nunca realizar instâncias em massa no arquivo-fonte.
- **Bibliotecas vinculadas**: quando o kit amadurecer, os arquivos de distrito *vinculam* `SantaAurora_CidadeAntiga_Kit_v1.blend` (Asset Browser) em vez de copiar. Usar caminhos relativos e verificar com BAT antes de empacotar.
- **Proxies e LOD**: LOD1/2 gerados por decimate controlado ou simplificação manual por variante; HLOD por quarteirão (malha única + atlas) para distâncias acima de 750 m.
- **Desempenho do viewport**: exibir instâncias como *bounds* fora do núcleo; *simplify* de subdivisão; cores de objeto no Workbench.
- **Automação**: todo o arquivo é reprodutível por script. Mudanças manuais em heróis devem migrar para o gerador ou para um `.blend` de herói vinculado.
"""},

"05_PBR_TEXTURAS.md": {"title": "05 — PBR, UV, texturas e terreno", "intro": """\
A biblioteca procedural (37 materiais) já tem slots nomeados `SLOT_BaseColor/Normal/Roughness/Metallic/AO` e pasta-alvo `ArtSource/Textures/<material>/`. O W3 preenche esses slots com texturas autorais, de Material Maker ou de fontes CC0 registradas.""", "workflow": """\
**Materiais**
- Tileables 2K (arquitetura 256–512 px/m), trim sheets para molduras, rodapés, frisos e chapas, decals (infiltração, ferrugem, óleo, rachaduras, sinalização) em atlas.
- Camadas: base + sujeira por cavidade (AO/curvatura) + sujeira de rodapé + desgaste de borda; molhado por roughness/darkening (Shader Graph na Unity).
- Concreto, tijolo, asfalto, metal, ferrugem, vidro, madeira, cerâmica e plástico: começar por ambientCG/Poly Haven (CC0), ajustar no Material Maker, registrar origem.

**UV e baking**
- UVs métricos já existem em toda a geometria (projeção de caixa). Heróis ganham *unwrap* manual com texel density uniforme e ilhas alinhadas a trim sheets.
- UDIM só em heróis enormes, se necessário; o padrão é atlas e trim.
- Bake de normal e AO no próprio Blender (Cycles) de high para low; mapas Roughness/Metallic/AO lineares, Normal no padrão OpenGL (Unity espera Y+; o Blender exporta OpenGL).
- Compressão na Unity: BC7 (cor), BC5 (normal), máscaras empacotadas (R=Metallic, G=AO, A=Smoothness no URP Lit).

**Terreno / GIS (apenas técnica)**
- Nosso relevo vem de `sa_terrain.py` (determinístico, dirigível). BlenderGIS e DEM servem para estudar técnica de drenagem e erosão, nunca para importar cidade real. Dados OSM (ODbL) estão proibidos como conteúdo.
"""},

"06_UNITY_LARGE_WORLD.md": {"title": "06 — Unity: mundo grande, streaming e visual URP", "intro": """\
Unity 6000.6.2f1 + URP 17.6. O mundo tem 8×8 km com origem no centro: coordenadas de até cerca de 4 km mantêm precisão sub-milimétrica em float, então floating origin não é necessário agora (reavaliar se surgirem jitter de câmera ou física a grande distância).""", "workflow": """\
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
"""},

"07_UNITY_GAMEPLAY.md": {"title": "07 — Unity: primeira pessoa, sistemas e arquitetura", "intro": """\
O protótipo já tem `Interaction.cs` (primeira pessoa, Input System, raycast), `ServiceSession`, `SaveService`, `ChapterOne` e `TabletUI`. A recomendação é **evoluir o que existe, com arquitetura simples orientada a dados**, e evitar frameworks.""", "workflow": """\
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
"""},

"08_ANIMACAO.md": {"title": "08 — Animação", "intro": """\
O foco é animação em primeira pessoa e de máquinas. Personagens completos ficam para depois.""", "workflow": """\
- **Blender**: rig de braços em primeira pessoa (armature com controles IK/FK); ações por ferramenta (pegar, usar, guardar, inspecionar) exportadas como clips FBX separados; máquinas (portas, bombas, ventiladores, disjuntores) com animação por objeto ou feitas na Unity.
- **Unity**: Animator com camadas (base, mãos, aditivo de respiração); Animation Rigging para ajustar a mão ao alvo (registro, disjuntor, maçaneta); Timeline para eventos narrativos curtos.
- Rigs humanoides de NPC: retarget pelo Avatar Humanoid; biblioteca CC0 ou captura própria (registrar licença).
"""},

"09_VEICULOS.md": {"title": "09 — Veículos", "intro": """\
O W1.5 mostrou que, do Capítulo II em diante, o veículo é necessário: clientes ficam a 4,6–8,9 km, 26–50 min a pé contra 9–18 min de carro. A arquitetura viária já respeita dirigibilidade (rampas ≤ 6% nas arteriais, rotatórias, acessos).""", "workflow": """\
- Controlador próprio sobre WheelCollider: torque e freio, curvas de aderência simples, assistências (ABS e estabilidade) para um modelo híbrido arcade/realista.
- Interiores legíveis (painel, bancos, carga) como cena de herói pequena; entrar/sair com transição de câmera em primeira pessoa.
- Carga e inventário do veículo por slots físicos (caixas, ferramentas grandes) sincronizados com o inventário de dados.
- Estacionamento: vagas já definidas nos heróis (`GP_*__parking__*`); validar raio de giro de utilitário (V2/V3) na oficina.
- Tráfego futuro: grafo viário do manifesto vira grafo de navegação de tráfego; não implementar antes do vertical slice.
"""},

"10_AI_NPC.md": {"title": "10 — NPC e IA", "intro": """\
Os NPCs são clientes, moradores, funcionários (a partir do Capítulo VII) e transeuntes leves. AI Navigation 2.0.12 já está instalado.""", "workflow": """\
- NavMesh por cena de célula + NavMeshLinks entre células; superfícies por camada (calçada, pista, interior).
- Rotinas por agenda (manhã, tarde, noite) com pontos de interesse dos lotes (manifesto `OT_Gameplay_Lots_*`); pooling de pedestres por anel de distância.
- Clientes: máquina de estados simples (aguardando, acompanhando, avaliando, pagando); behavior trees só se o comportamento crescer.
- Funcionários: tarefas da mesma estrutura de chamados com tempo e competência; simulação abstrata fora da tela.
"""},

"11_ECONOMIA_PROGRESSAO.md": {"title": "11 — Economia, progressão e imóveis", "intro": """\
Regra do projeto: **difícil, porém sempre recuperável**. A economia precisa ser provada por simulação antes de ser exposta ao jogador.""", "workflow": """\
- Simulador Python próprio (`Tools/Balance/`, a criar): milhares de carreiras com políticas de jogador (cautelosa, gananciosa, desastrada) medindo caixa, dívida, reputação e tempo até cada desbloqueio.
- Anti-softlock: sempre há chamados baratos acessíveis a pé; o crédito tem limite; ferramentas essenciais nunca saem do mercado; falência leva a recomeço parcial, nunca a beco sem saída.
- Transações seguras para o save: operação atômica (débito + item) registrada no mesmo commit do save.
- Imóveis e lar: estados H0–H4 já têm slots no lar; compras viram objetos físicos; imóveis antigos continuam existindo; garagens com vagas reais.
- Progressão aberta: o mercado livre oferece 3–5 chamados por região desbloqueada; a curva de dificuldade segue reputação, ferramentas e veículo (GDD).
"""},

"12_SAVE_DATA.md": {"title": "12 — Save e dados", "intro": """\
O save atual já é v1 com flags de versão (`servicePresenceVersion`, `chapterOneDataVersion`). A regra é preservar compatibilidade e nunca serializar GameObjects.""", "workflow": """\
- **Versionamento**: `saveVersion` + migrações encadeadas (v1→v2→…) testadas com fixtures de saves reais anonimizados (EditMode).
- **Escrita atômica**: gravar em `slot.tmp`, `Flush(true)`, renomear para `slot.json` (o `File.Replace` mantém backup `slot.bak`); manter 3 backups rotativos.
- **Corrupção**: validar o JSON e o hash ao carregar; se falhar, oferecer o último backup válido.
- **Perfis**: pasta por perfil; nomes de arquivo estáveis (compatível com Steam Auto-Cloud sem código).
- **Dados de conteúdo**: JSON com schema e validador (como no masterplan); IDs estáveis; geradores donos dos arquivos gerados.
"""},

"13_UI_UX.md": {"title": "13 — UI/UX, tablet e mapa", "intro": """\
O `TabletUI.cs` é provisório. A migração planejada é para UI Toolkit antes de polir.""", "workflow": """\
- UI Toolkit (UXML/USS) para tablet, job board, inventário, finanças, imóveis, lojas e configurações; tema único com tokens de cor e escala de fonte.
- **Mapa/GPS**: conversão mundo→mapa linear (8×8 km com origem no centro, já definida); camadas de distritos, POIs, chamados e imóveis; filtros; rota pelo grafo viário (Dijkstra já existe em Python e vira um serviço C# na W5).
- **Minimapa**: render ortográfico pré-gerado por célula (tiles do masterplan) em vez de câmera em tempo real.
- **Acessibilidade**: escala de fonte, alto contraste, indicadores de interação, legendas (doc 19).
"""},

"14_AUDIO_VFX.md": {"title": "14 — Áudio, VFX e clima", "intro": """\
O áudio vende os sistemas técnicos: zumbido elétrico, bombas, HVAC, chuva e trânsito distante.""", "workflow": """\
- Zonas de ambiente por célula e por interior; loops de máquinas com variação; oclusão e transmissão via Steam Audio (avaliar o custo de CPU) ou raycast simples no início.
- Passos por material da superfície (tags nos materiais da biblioteca).
- **VFX**: Particle System para faíscas fictícias, vapor, vazamento, poeira e condensação; VFX Graph só para chuva em larga escala.
- **Clima**: gerenciador com estados (ensolarado, nublado, chuva, tempestade, onda de calor, neblina) que alimenta gameplay (chamados, falhas) e visual (molhado, neblina, iluminação). O orçamento de partículas segue a distância.
"""},

"15_PERFORMANCE.md": {"title": "15 — Performance", "intro": """\
O alvo é PC Windows/Steam. Orçamentos medidos, nunca supostos: sem evidência de execução, não declarar desempenho alvo (CLAUDE.md).""", "workflow": """\
1. Cena de referência por célula do núcleo com câmera em rota fixa (determinística) para medir.
2. Unity Profiler (CPU/GPU), Frame Debugger (draw calls, batching), Memory Profiler (snapshots antes/depois do streaming), Profile Analyzer (comparar builds).
3. RenderDoc para overdraw, tamanho de texturas e custo de shaders; Nsight para gargalos de GPU NVIDIA.
4. Project Auditor (embutido no 6.4+) para problemas estáticos de código, shaders e configurações.
5. Orçamento inicial a validar: até cerca de 2–3k draw calls visíveis com SRP Batcher, texturas em streaming, LOD0 só no anel próximo.
"""},

"16_QA_TESTES.md": {"title": "16 — QA e testes automatizados", "intro": """\
Já existem um smoke test de runtime (`RuntimeSmoke.cs`), `Tools/Test-Windows.ps1`, validadores Python (masterplan, rotas) e auditorias de reabertura no Blender.""", "workflow": """\
- **EditMode**: regras de serviço, economia, migração de saves com fixtures, validação de catálogos e IDs.
- **PlayMode**: cena determinística de smoke (carregar célula, entrar no lar, aceitar chamado, salvar e recarregar).
- **Validadores de assets** (AssetPostprocessor + testes): escala, UV, materiais, colisores, LOD, orçamento de vértices e texturas, nomes.
- **Regressão visual**: capturas por câmera fixa + diff Pillow (skill `visual-review`).
- **Separação de dados**: testes nunca tocam o progresso do jogador (perfil de teste isolado — regra do CLAUDE.md).
"""},

"17_BUILD_GITHUB.md": {"title": "17 — Build, Git/GitHub e documentação", "intro": """\
Build Windows por `Tools/Build.ps1` (batchmode). A branch de trabalho é `claude/w1-masterplan`, sem merge automático no `main`.""", "workflow": """\
- **CI barato e sem segredos**: GitHub Actions rodando `validate_masterplan.py` e `build_catalog.py` a cada push (Python puro). Builds Unity em CI (GameCI) só com decisão do usuário sobre a licença Unity como segredo.
- **Binários**: hoje os `.blend` vão como binários normais (`.gitattributes`). Git LFS (3.7.1 instalado) para texturas e FBX de produção, **sem reescrever o histórico**. Decidir com o usuário considerando a cota do GitHub.
- **Versionamento de build**: `major.minor.patch+commit` injetado pelo `Build.ps1`; smoke launch automático após o build.
- **Documentação**: relatório por marco (padrão W1/W1.5); CHANGELOG no formato Keep a Changelog; ADRs curtos em `Docs/ADR/` para decisões duráveis (relevo, streaming, LFS, Steam).
"""},

"18_STEAM.md": {"title": "18 — Steam (preparar; não integrar ainda)", "intro": """\
A integração Steam fica para depois do vertical slice. Agora só se preparam as escolhas e a compatibilidade.""", "workflow": """\
- Wrapper: Steamworks.NET (MIT, fiel à API) como padrão; Facepunch.Steamworks como alternativa.
- Steam Cloud via Auto-Cloud: saves em pasta fixa por perfil, arquivos pequenos e nomes estáveis (doc 12).
- Conquistas e estatísticas por IDs estáveis definidos em dados; Rich Presence com região e chamado atual.
- Steam Input: mapear as ações do Input System (já em uso) para os *action sets* do Steam.
- SteamPipe: upload de depots via ContentBuilder num script separado, sem credenciais no repositório.
"""},

"19_LOCALIZACAO_ACESSIBILIDADE.md": {"title": "19 — Localização e acessibilidade", "intro": """\
O idioma base é português (pt-BR). A localização deve ser possível desde já, mas sem traduzir agora.""", "workflow": """\
- Unity Localization: string tables por domínio (UI, chamados, narrativa), smart strings para valores e plural, pseudo-localização para testar expansão de texto (+30–40%).
- Fontes com cobertura latina estendida; nada de texto embutido em textura (exceto marcas fictícias decorativas).
- Acessibilidade (Game Accessibility Guidelines/XAG): legendas com indicação de quem fala, remapeamento completo, sensibilidade, modos para daltonismo nos indicadores técnicos (não depender só de cor nos LEDs e quadros), escala de fonte, movimento reduzido (head bob e balanço de câmera), alto contraste e pistas sonoras.
"""},

"20_ASSET_PIPELINE.md": {"title": "20 — Pipeline Blender → Unity e validação de assets", "intro": """\
A skill própria `blender-to-unity-export` registra as convenções planejadas. Elas precisam ser validadas com uma subcélula piloto antes da produção em massa.""", "workflow": """\
1. **Piloto**: exportar 1 subcélula do núcleo + lar + oficina em FBX (escala 1, -Z frente, Y cima) e recriar as instâncias de fundo na Unity a partir do manifesto.
2. **AssetPostprocessor**: remapear materiais por nome, gerar LODGroup por sufixo, colisores por `UCX_`/`_COL`, rótulos Addressables por subcélula.
3. **Validador de importação**: escala, UV ausente, material ausente, colisor ausente, LOD ausente, malha acima do orçamento, textura grande demais, nome fora do padrão. Falha visível no console e em teste EditMode.
4. Exportação em lote por script Blender (subcélula × camada) com relatório JSON comparável entre execuções.
"""},

"21_LICENCAS.md": {"title": "21 — Licenças e registro de origem", "intro": "Política de licenças.", "body": """\
## Política
- **Uso comercial permitido e claro** é pré-requisito: CC0, MIT, Apache-2.0, BSD, zlib e ISC são aceitos. CC-BY só com atribuição registrada nos créditos.
- **GPL/AGPL**: ferramentas GPL (Blender, BAT, add-ons) podem ser *usadas*; o que produzimos com elas é nosso. **Não copiar código GPL/AGPL para o jogo nem para o repositório.** Ex.: AI-SKILL-blender (AGPL) fica só como referência online.
- **Sem licença declarada = não copiar** (ex.: Citronetic/unity-claude-skill).
- **Licenças Unity** (Companion/Package Distribution/Reference-only): usar como pacotes; código reference-only só para leitura.
- **Marketplaces** (Fab/Megascans, Substance, Sketchfab): revisar termos asset a asset antes de qualquer uso; nada de assets cuja licença proíba redistribuição em build.
- **Dados geográficos reais** (OSM/ODbL, DEMs com restrições): proibidos como conteúdo de Santa Aurora.
- **VEIN**: referência de qualidade visual apenas, nenhum asset, textura, layout, mapa ou identidade.

## Registro persistente
Todo recurso externo que entrar no projeto (textura, HDRI, modelo, fonte, som, código) é registrado em `Tools/Skills/asset_license_registry.csv` com: `id, tipo, nome, url, autor, licença, versão/commit/data, onde é usado, atribuição exigida, revisado_por, data`. Skills salvas têm `LICENSE` + `PROVENANCE.md` com commit e SHA-256.

## Segurança de dependências (checklist antes de salvar ou instalar)
1. Repositório oficial, autor identificável, atividade recente, não arquivado (ou anotado).
2. Licença lida no arquivo LICENSE (não só no SPDX do GitHub).
3. Fixar commit ou tag; registrar hash do pacote baixado.
4. Varredura: binários desconhecidos, scripts ofuscados, downloads em tempo de execução, `allowed-tools` amplos, `` !`comando` ``, hooks.
5. Nada de tokens ou credenciais no repositório; MCPs que pedem token ficam DO_NOT_INSTALL sem autorização.
6. Executar só depois de revisão, e em branch isolada.

## Ferramentas de conformidade
{{LIC}}
"""},

"22_RECOMENDACOES.md": {"title": "22 — Recomendações finais", "body": """\
## TOP 10 para todo o projeto
{{TOP10}}

## TOP 5 para usar já no W1.5/W2
{{TOP5}}

**Por que estes:** o W2 é a Cidade Antiga em alta fidelidade. O ganho imediato vem de: (1–2) skills próprias que mantêm o pipeline e os padrões bpy consistentes entre sessões; (3) Material Maker para preencher os slots PBR já criados com texturas autorais; (4) Poly Haven/ambientCG CC0 como base e referência de materiais e HDRIs; (5) revisão visual com regressão por diferença de imagem, para que nada seja aprovado sem olhar.

## Plano de adoção (sem instalar nada agora)
1. **Agora (W2)**: ativar no projeto, com aprovação, as skills próprias `santa-aurora-world-pipeline` e `blender-headless-bpy` (copiar para `.claude/skills/`); usar Material Maker e fontes CC0 fora do repositório, registrando cada asset.
2. **W5 (Unity)**: instalar Addressables, Memory Profiler, Profile Analyzer e Newtonsoft Json; ativar as skills Unity da Nice-Wolf necessárias; avaliar `unity-mcp` em branch isolada.
3. **Pré-lançamento**: Localization, Steamworks.NET, Steam Audio, CI com GameCI (se a licença for decidida), Git LFS para texturas e FBX.

## Rejeitados (com motivo)
{{REJECTED}}

## Não instalar sem revisão/autorização
{{DNI}}

## Riscos gerais
- Skills de comunidade mudam rápido: sempre commit fixado; reavaliar a cada marco.
- Skills Unity baseadas no 6.3 LTS: conferir APIs no 6000.6.
- MCPs de controle de editor ampliam a superfície de execução; preferir scripts versionados.
- Termos de marketplaces mudam (Fab/Megascans em 2024–2025): revisar antes de cada uso.
"""},
}
