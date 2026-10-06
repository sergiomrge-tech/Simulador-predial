# Estado da implementação — 03/10/2026

## Entregue nesta etapa

- Unity 6000.6.2f1/URP/C#, Input System, primeira pessoa e personagem com colisão.
- Garagem inicial, tablet, estoque, chamados e retorno à sede.
- Uma rede elétrica abstrata com três causas do mesmo sintoma, duas ferramentas de medição e inspeção visual.
- Prólogo autoral do Horizonte: luminária com isolamento danificado, rearme temporário, desarme ao aquecer, isolamento e confirmação obrigatórios antes da substituição, restauração e teste de estabilidade.
- Diário persistente com mensagens de Guto e Helena; conclusão única do prólogo e indicação do Capítulo I como próxima etapa. Chamados livres continuam disponíveis depois.
- Três serviços autorais iniciais do Capítulo I nos mapas de apartamento, mercearia e restaurante: tomada, relé de iluminação e vedação de torneira. Os ambientes recebem equipamentos interativos e props provisórios distintos.
- Diagnóstico hidráulico abstrato com pressão/vazão fictícias, vazamento visível, fechamento de registro, troca com confirmação, reabertura e validação. Kits hidráulicos têm estoque, preço e crédito próprios.
- Histórico persistente por local atendido, consultável em visitas posteriores; indicação de Helena ao primeiro contrato recorrente exige os três serviços e reputação 25.
- Evidências, escolha de diagnóstico, consumo de peças, penalidade por troca errada, reparo, validação e pagamento único.
- Dinheiro, experiência, reputação, reposição de peças e crédito do fornecedor para recuperar falta de estoque/saldo.
- Save local versionado v1, escrita temporária, backup, recuperação e progresso de chamado ativo.
- Marcador explícito de chamado ativo corrige a serialização de classes inline nulas da Unity, evitando chamados vazios após uma entrega. Carreiras anteriores v1 conservam os dados existentes.
- Três equipamentos autorais do Blender e corredor arquitetônico inicial importados em FBX e preparados para URP.
- Estudo de implantação de Santa Aurora no Blender com os 24 locais da campanha.
- Catálogo com 6 distritos, 24 locais, 182 setores, 30 pavimentos e prólogo + capítulos I–XIV.
- Visitas de prévia aos locais, com portas físicas, mudança de pavimento pelo tablet e registros ambientais. A prévia não concede recompensas nem avança a história.
- Documentos de decisões atuais, plantas, lore original e handoff para Claude.

## Verificações e evidências

- Regras de domínio verificadas pelo editor antes do build: três causas, pré-requisitos, peças, troca errada, teste final obrigatório, pagamento duplicado bloqueado, crédito e backup de save.
- Executável Windows testado com save próprio de QA: interação por raycast, colisão com piso/parede, evidências, três reparos, luzes restauradas, validação, retorno ao hub, economia e save/load.
- Catálogo validado: todos os IDs de locais de capítulos existem e todos os grafos de setores são conectados.
- 30 pavimentos e 213 conexões de portas percorridos pelo CharacterController no executável.
- Equipamentos Blender verificam orientação vertical e escala em metros no runtime. Capturas de câmera mostram corredor, equipamentos e uma planta de Santa Aurora Central.
- Os arquivos `.blend` foram reabertos para conferir geometria, UVs do kit/corredor, textura incorporada do kit e presença dos 24 locais no estudo da cidade.
- Prólogo verificado nas regras e no executável: falha térmica real no loop do jogo, pausa pelo tablet, troca insegura sem consumo de estoque, reparo com circuito isolado, restauração, espera obrigatória, pagamento único, diário e conclusão persistentes. Save/load das etapas isoladas e leitura dos campos antigos de v1 verificados pelo editor.
- Regras do Capítulo I verificam ordem, isolamento, confirmação por componente, consumo separado de peças, crédito hidráulico, pagamentos, registros, save/load e recuperação de reputação por chamados livres. A indicação não é concedida apenas por concluir serviços com reputação baixa.
- Executável confirmou os três locais corretos, raycasts dos equipamentos, 21 passagens preservadas com props instalados, ida à garagem e retomada com isolamento, reparos de tomada/iluminação, vazamento visível antes da intervenção e ausência de vazamento após reparar/reabrir. Economia, memória por prédio e indicação foram conferidas no save de QA. Capturas do restaurante ficam em `Docs/Previews/`.

Relatórios completos locais: `Logs/unity-build.log`, `Logs/rules-passed.txt`, `Logs/windows-smoke.log` e `Builds/Windows/QA/PASSED.txt`. Resultados resumidos portáveis: `Docs/map-validation.json`, `Docs/QA_RESULTADO.txt` e `ArtSource/Blender/*verification.json`.

As capturas foram feitas com render request URP fora da tela. Elas verificam a câmera e o cenário; não representam captura de todos os estados do tablet IMGUI. Interação humana e usabilidade das abas ainda precisam de playtest.

## Limites da entrega

Esta é a fundação e estrutura explorável de um protótipo, não a campanha inteira concluída nem a arte final premium.

Os locais avançados usam uma grade modular de teste. A dimensão e posição dos distritos são uma proposta de level design baseada na lore, não uma geografia fornecida pelo usuário. A arquitetura completa de cada local precisa de curadoria própria. As ligações verticais estão registradas no catálogo e usam viagem pelo tablet; escadas e elevadores físicos ainda não existem.

O primeiro chamado da campanha segue o prólogo da lore; o aquecimento é um temporizador virtual de cinco segundos e os procedimentos são ações abstratas, sem desmontagem física. Os três serviços seguintes adaptam categorias do Capítulo I, com sintomas e preços escritos para o protótipo. Não esgotam todo o conteúdo do capítulo. Hidráulica não utiliza simulação de fluidos: o vazamento e leituras são estados lógicos e um efeito visual simples. Mensagens substituem a apresentação de NPCs. A indicação ao contrato é persistente, mas a execução preventiva/recorrente ainda não existe. Fotografias/laudos, eventos climáticos, auditoria, escolhas, finais, equipes e Cascata continuam pendentes.

UI é provisória em IMGUI. Os ScriptableObjects são definições iniciais ainda sem catálogo de assets conectado; missões de teste estão no código. Ambientes são montados em runtime e precisam migrar para cenas/prefabs editáveis. Não houve validação de 60 FPS em máquinas de referência, gamepad ou acessibilidade final. Steamworks não integrado.

## Ordem recomendada de continuidade

1. Playtest da câmera em primeira pessoa, prompts e tablet.
2. Prefabs/cena do Edifício Horizonte e garagem; mãos, ferramentas e ações táteis.
3. Polimento narrativo/visual dos serviços e apresentação do primeiro contrato recorrente.
4. Inspeção/documentação e memória persistente dos prédios.
5. Bombas e inspeção preventiva com consequências persistentes do Capítulo II.
6. Arte final de um pequeno conjunto de setores antes de expandir acabamento aos 24 locais.
7. Climatização, redundância e equipes; depois campanha avançada e operação Cascata.


## Checkpoint de planejamento e código — expansão de carreira e vida pessoal

### Planejamento oficial adicionado
- GDD completo em `Docs/GDD_PROGRESSAO_VIDA_LIBERDADE_ECONOMIA.md`.
- Liberdade para escolher trabalhos e regiões desbloqueadas.
- Escopo inicial pequeno, expandindo por reputação, ferramentas, dinheiro e transporte.
- Dificuldade planejada como exigente, porém recuperável, sem softlocks.
- Moradia evolutiva: kitnet → apartamentos → casas → residência premium opcional.
- Compra de móveis, eletrodomésticos, ferramentas, veículos, imóveis, oficina e futura sede.
- Lazer opcional: entretenimento, hobbies, atividades urbanas, vida social, viagens curtas e coleções.
- Direção visual de mapa/estruturas/casas inspirada na linguagem visual de VEIN, sem copiar conteúdo.

### Código novo após o último QA confirmado
- Primeiro contrato preventivo: `campaign.c2.recurringcondo.pump.v1`.
- Local: `recurringcondo`.
- Diagnóstico de entrada → bomba principal → reservatório.
- Estoque independente `pumpKits`.
- Compra de kit preventivo.
- Flags persistentes `firstContractCompleted` e `preventiveRecommendationLogged`.
- Migração aditiva do save v1 via `chapterTwoDataVersion`.
- Blockout específico da casa de bombas, sem reutilizar a torneira.
- Tablet e fluxo de campanha atualizados.
- Runtime smoke test estendido até a preventiva.

**Importante:** esta seção descreve alterações de código já commitadas, mas ainda não substitui o QA anterior. É obrigatório abrir/compilar no Unity 6000.6.2f1 e executar as verificações antes de declarar o contrato preventivo validado.


## Checkpoint — planejamento de mundo grande e direção visual

Documentos oficiais adicionados:
- `Docs/PLANO_MESTRE_MUNDO_SANTA_AURORA.md`: footprint 8×8 km, produção por distritos, grid de streaming, vias, hero locations, pipeline Blender→Unity, LOD/HLOD, performance e ordem de construção.
- `Docs/ART_BIBLE_REALISMO_SANTA_AURORA.md`: regra de realismo, proibição de low-poly final, PBR, decals, desgaste, densidade, interiores técnicos, veículos, ferramentas, clima e gates visuais.

A Cidade Antiga passa a ser o primeiro vertical slice visual. Não escalar acabamento para os demais distritos antes de validar qualidade e performance desse recorte.

A referência VEIN deve ser usada para comparar patamar de realismo, atmosfera, densidade e materialidade. Assets, texturas, prédios e layouts de Santa Aurora devem ser originais.


## Checkpoint — Santa Aurora Foundation W1 preparado

Preparação concluída no GitHub:
- World Bible métrica 8×8 km.
- `masterplan_spec_v1.json` com 6 distritos, 24 locais de campanha, 20 locais de vida/economia e 8 corredores viários.
- Validação estática: PASS, 0 erros e 0 warnings após ajuste.
- Registro estrutural orientado pela história.
- Gerador Blender `create_santa_aurora_masterplan.py`.
- Validador independente `validate_masterplan.py`.
- Checklist de geração, screenshots reais, reabertura e gate W1.

**Ainda pendente:** executar o gerador no Blender real, salvar/reabrir `SantaAurora_Masterplan_v1.blend`, capturar as 10 vistas exigidas e aprovar espacialmente W1. O mapa grande ainda não deve ser descrito como jogável na Unity.

## Checkpoint — W1 executado no Blender (2026-10-03)

- Blender 5.2.1 LTS, geração headless sem exceção; `SantaAurora_Masterplan_v1.blend` com 874 objetos reabre em processo novo sem missing data.
- Layout compartilhado `Tools/Map/masterplan_layout.py` (validador e gerador usam o mesmo código); runner `Tools/Blender/Run-W1Masterplan.ps1`.
- Vias viraram polilinhas para não atravessar garage/vertice/central/datacenter/logistics; canal de drenagem e parque municipal adicionados ao spec; drainage ajustada para (-1130, 3070).
- 10 capturas reais em `ArtSource/Blender/World/Reviews/W1/`.
- Relatório completo e limitações: `Docs/W1_MASTERPLAN_RELATORIO.md`.

**Status:** gate técnico PASS. A aprovação espacial/narrativa depende da revisão das capturas pelo usuário. O protótipo Unity, os saves, os IDs e as coordenadas runtime não foram alterados. O mapa grande continua não jogável.

**Revisão crítica (2026-10-03): W1 NÃO APROVADO.** Há dois bloqueios: falta ligação viária entre Cidade Antiga e Expansão (desvio de rota até 3,4×) e não há ferrovia nem porto seco, contra a lore. Pendente de decisão: relevo × drenagem. Folha de revisão em `ArtSource/Blender/World/Reviews/W1/review_sheet.html`; correções W1.1 na seção 7 de `Docs/W1_MASTERPLAN_RELATORIO.md`.

## Checkpoint — W1.5 Santa Aurora Foundation + Cidade Antiga Base (2026-10-03)

- Pipeline: `Tools/Blender/Run-W15World.ps1` (validação, rotas, 3 geradores, 3 reaberturas com capturas).
- Masterplan v1.5 com:
  - relevo drenando para o canal;
  - Cidade Antiga orgânica (9 bairros, 13.872 lotes);
  - 8 zonas de transição e nenhuma célula vazia;
  - Industrial denso (ocupação de 28%);
  - R09/R10, rotatórias e ferrovia histórica;
  - skyline diferenciado por distrito.
- Cidade Antiga, base de produção:
  - ruas, calçadas e meio-fio;
  - infraestrutura provisória em escala;
  - 13.050 edificações instanciadas a partir de 47 variantes;
  - 9 heróis + lar com arquitetura base, cortes e slots H0–H4/G0–G4;
  - 8 camadas × 181 subcélulas com manifesto.
- Kit modular com bevel (40 peças + 15 de infraestrutura) e biblioteca PBR procedural (37 materiais com slots de textura).
- Validação PASS; reaberturas 3/3 PASS; 25 capturas em `ArtSource/Blender/World/Reviews/W1_5/`.
- Relatório: `Docs/W1_5_WORLD_FOUNDATION_RELATORIO.md`.

**Ainda não é arte final.** Faltam texturas autorais, decals, clutter, LOD0 final, vegetação autoral e integração na Unity. O protótipo Unity, os saves, os IDs e as coordenadas runtime não foram alterados.

## Checkpoint — Etapa B: biblioteca de skills e ferramentas (2026-10-03)

- `Docs/SKILLS/00…22` + `Tools/Skills/catalog.json` (102 itens com URL, licença, versão/commit, prioridade e segurança), gerados por `Tools/Skills/build_catalog.py`.
- Salvos (inertes, só markdown com LICENSE + PROVENANCE): 35 skills Unity da Nice-Wolf (MIT), 4 skills de metodologia da superpowers (MIT) e 4 skills próprias (pipeline do mundo, bpy headless, exportação Blender→Unity, revisão visual).
- Nada instalado, nenhum código externo executado, nenhuma credencial armazenada. MCPs de Blender/GitHub marcados DO_NOT_INSTALL; unity-mcp REVIEW_REQUIRED para a W5.
- TOP 10 e TOP 5 em `Docs/SKILLS/22_RECOMENDACOES.md`.

## Checkpoint — Etapa C: revisão visual e gates W1.5 (2026-10-03)

- Revisão crítica em `Docs/W1_5_REVISAO_GATES.md`: 10 critérios PASS, **nenhum BLOCKED**, 7 NEEDS_FIX subjetivos registrados para W2/W3.
- Corrigido: lotes de fundo que tapavam a fachada dos heróis (recuos frontais reservados e pavimentados, com nova checagem no validador), câmera da fachada do Horizonte e câmera do lar. Pipeline completo rerodado (3/3 reaberturas PASS, 26 capturas).
- Próximo: Etapa D — W2 Cidade Antiga Base.


## Checkpoint — Etapa D: W2 Cidade Antiga Base, parcial (2026-10-04)

- Heróis A/B/C em `.blend` próprios (`ArtSource/Blender/World/OldTown/Heroes/`), cada um com raiz posicionada no mundo:
  - Lar (Apto 12 completo com H0 e slots H0–H4) — 111 mil tris;
  - Oficina Aurora G0 (galpão de pórticos, cômodos, serviços, slots G0–G4) — 59 mil tris;
  - Horizonte (12 pavimentos, térreo técnico, corredor do 4º andar com quadro técnico, cobertura) — 171 mil tris.
- Kit detalhado `sa_detail.py` (30+ componentes) e +16 materiais procedurais.
- Cidade Antiga:
  - N3: 2.223 esquinas curvas, 983 rebaixos;
  - N1: 29.381 acessórios por regra (+4,9% de tris instanciados);
  - N4: recuos com piso intertravado, floreiras e balizadores.
- Validação PASS; 5/5 reaberturas PASS sem dados faltando; 33 capturas em `ArtSource/Blender/World/Reviews/W2/`.
- Relatório: `Docs/W2_CIDADE_ANTIGA_BASE_RELATORIO.md` (Gate D parcial PASS).
- Atualização (2026-10-04):
  - Teatro Imperial W2 (123 mil tris: fachada clássica, pórtico, plateia com 2,4 mil poltronas, palco e urdimento, quadro antigo + retrofit inacabado);
  - cinco heróis restantes pelo gerador genérico (`create_w2_hero_generic.py`);
  - os **nove** heróis W2 vinculados à base como instâncias de coleção (LOD0), com o massing W1.5 oculto como LOD1;
  - 73 capturas.
- **Falta:**
  - revisão visual do usuário (gate da Cidade Antiga);
  - refino autoral dos 5 heróis genéricos;
  - decals e desgaste;
  - estados G1–G4/H1–H4 modelados;
  - subsolo do Horizonte.
- Ainda não é arte final. Protótipo Unity, saves e IDs intactos.

## Checkpoint — W2.5 Cidade Antiga: relevo + wear pass + heróis secundários (2026-10-04)

- **Relevo urbano** em `sa_terrain`:
  - Alto da Aurora +20 m;
  - vale da Av. do Trabalho (R02) com córrego canalizado de 2,4 km;
  - ondulação entre quarteirões;
  - platôs dos heróis.
- **Rampas:** locais até ≈15%, arteriais ≤3,8%; validação PASS.
- **Implantação em desnível:** 1.511 embasamentos, 1.356 muros de arrimo, 19 escadarias.
- **Wear pass:**
  - nó `SA_WEAR` em 29 materiais (escorrimento, umidade, remendos, sujeira de piso, ferrugem);
  - decals de umidade, sujeira, óleo e pneu nas vias e nos 9 heróis.
- **Bairro:**
  - fiação aérea (2.192 vãos);
  - calçadas variadas;
  - muros e portões, lixeiras, caçambas, puxadinhos, lonas, arbustos, entulho;
  - carros-proxy.
- **Heróis:** os 5 secundários ganharam identidade (fachada, letreiros, volumes de apoio, vida de rua); os 4 principais foram reassentados no relevo, com desgaste.
- **Integridade:** IDs, marcadores, lotes e heróis vinculados idênticos ao commit anterior (auditoria). Reaberturas PASS sem dados faltando. 77 capturas em `Reviews/W2_5/`.
- **Complexidade:** +4,2% de tris instanciados; +0,51 M de tris em meshes simples.
- **Gate visual da Cidade Antiga: PARTIAL PASS.** Relevo pouco legível em vistas aéreas; vegetação e carros proxy; iluminação de revisão; texturas autorais pendentes. Detalhes em `Docs/W2_5_VISUAL_FIDELITY_GATE.md`.
- **Complemento W2.5, vegetação de calçada:**
  - 4.773 árvores irregulares por caráter de bairro, mais densas longe do miolo e raras em áreas industriais;
  - covas e canteiros na calçada;
  - 175 pracinhas;
  - 1.434 arbustos sobre arrimos;
  - 7 espécies-proxy (oiti, sibipiruna, mangueira, ipê amarelo e rosa, muda, palmeira) mais arbusto;
  - +4,7% de tris instanciados;
  - IDs re-auditados idênticos.

## Checkpoint — W3 Cidade Antiga High Fidelity Vertical Slice (2026-10-04)

- **Recorte de 15 subcélulas** (Lar → Oficina → Horizonte → Mercearia, cliente I.2) em `ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend`. O contexto vizinho é vinculado da base do distrito, pelos mesmos nomes de streaming.
- **21 texturas PBR autorais e tileáveis** em `ArtSource/Textures/`, aplicadas em toda a Cidade Antiga, nos heróis, no kit e no masterplan.
- **Visual:**
  - terreno blend por declividade;
  - vegetação de produção (galhos + folhas alpha, LOD0/LOD1, grama e ervas);
  - vidro funcional;
  - look Khronos PBR Neutral com AO/GI;
  - fachadas LOD0 no recorte;
  - clutter por regra de uso;
  - Mercearia com interior abastecido.
- **Validações:** reaberturas PASS sem dados faltando; masterplan e rotas PASS; IDs, marcadores, lotes, heróis e streaming idênticos (auditoria); 82 capturas em `Reviews/W3/`.
- **Gate W3: PARTIAL PASS.** Faltam: carros-proxy, edificações de fundo simples, tufos em "pente", câmera de talude, luz e câmera de alguns interiores, decals pintados. Ver `Docs/W3_HIGH_FIDELITY_VERTICAL_SLICE.md`.

## Checkpoint — W3.1 Cidade Antiga Visual Polish Gate (2026-10-04)

- Mesmo recorte de 15 subcélulas; Unity, saves, C# de gameplay e `gpt/unity-world-integration` não foram tocados.
- **Carros autorais** (`sa_vehicles.py`): 6 famílias sem marca, com caixas de roda, rodas, vidro, faróis/lanternas e placas fictícias; LOD0/LOD1/proxy. Substituem os proxies em todos os heróis; 889 estacionados no recorte (velhos nas ruas locais, serviço junto à Oficina/Horizonte).
- **Fundo:** variantes por lote com tema por quadra (revestimentos de reforma, marquises, sacadas, escadas externas, anexos, platibandas, portões, condensadoras, grades).
- **Grama** de lâminas curvas (sem o efeito “pente”), terrenos vagos densos.
- **4 arrimos** de frente de rua com drenagem e escada, sem alterar cotas, e câmera dedicada.
- **Interiores** com volume de irradiância assado (fim do vazamento azul) e preenchimento quente. Mercearia enquadrada nas gôndolas; galpão com escala.
- **26 decals autorais** (`bake_decals_w31.py`).
- **Árvores:** variantes anti-clone, poda sob a fiação, raízes, portões livres.
- **Validações:** recorte e 9 heróis reabertos PASS (6 heróis sem render por falha de GPU do ambiente); masterplan e rotas PASS; IDs/GP_/SLOT_/PROXY_ idênticos; 13.003 lotes, 181 subcélulas.
- **Desempenho:** meshTris do recorte 2,70 M → 8,53 M (carros LOD0 como duplicatas); a mitigação via LOD Group fica para a integração Unity.
- **Gate W3.1: PARTIAL PASS.** Os carros ainda são facetados de perto, a vista aérea segue repetitiva e os taludes são baixos (≤ 1,18 m pelo relevo validado). Ver `Docs/W3_1_VISUAL_POLISH_GATE.md`.

## Checkpoint — W3.2 Cidade Antiga Final Visual Gate (2026-10-04)

- Mesmo recorte de 15 subcélulas; Unity, C#, saves, masterplan, cotas, os 9 arquivos de herói e `gpt/unity-world-integration` não foram tocados.
- **Carros:** LOD0 reescrito (carroceria e estufa loftadas, vidro translúcido com interior mínimo, rodas com raios, lâmpadas com volume): 11–16 mil tris; LOD1 ~1,9 mil; LOD0 só perto das câmeras de altura humana no Blender (314 de 889). Famílias, IDs, distribuição e proxies preservados.
- **Telhados/volumes:** kit `sa_roofs.py` + 7 acabamentos de laje; 1.412 peças e 440 lajes coloridas por seed de lote/quarteirão e caráter de bairro.
- **Decals:** máscara de fachada a partir das aberturas reais; nenhum decal sobre vitrine, janela ou porta.
- **Interiores:** preenchimentos dos heróis recriados no slice (`hero_interior_fills_w32.json`) e 4 volumes de irradiância assados.
- **Capturas:** 21 arquivos em `ArtSource/Blender/World/Reviews/W3_2/` (inclui comparações W3.1 × W3.2). Relatório: `Docs/W3_2_FINAL_VISUAL_GATE.md`.
- **Validações:** slice reaberto PASS; masterplan e rotas PASS; IDs/`GP_`/`SLOT_`/`PROXY_`/âncoras/instâncias idênticos aos do W3.1; 13.003 lotes, 15 subcélulas, 9 heróis. meshTris 8,45 M, instancedTris 32,5 M, `.blend` 24,7 MB.
- **Gate W3.2: PARTIAL PASS.** O Lar (Apto 12 vazio) não lê como ocupado por fora; a aérea melhorou mas as massas das famílias W2 ainda se repetem.

## Checkpoint — W3.2 congelado: correção da escada do Horizonte (2026-10-04)

- Polimento visual congelado; só `W2_horizonte.blend` foi corrigido (gerador `create_w2_hero_horizonte.py` + `hollow` opcional em `stair_u`). Unity, saves, código de gameplay e `gpt/unity-world-integration` intocados.
- Defeito (achado na validação Unity): laje sem abertura de escada, patamar de 0,30 m, degraus maciços com pouca altura livre e portas da escada fechadas de 1,0 × 2,1 m. Correção: abertura na laje, patamar de 1,20 m, degraus vazados, portas 1,2 × 2,4 m abertas a 90° para o corredor. Detalhes e verificação em `Docs/W3_2_HORIZONTE_STAIR_FIX.md`.
- Validação: `verify_horizonte_stair.py` (herói anterior falha; corrigido passa: altura livre ≥ 2,82 m, 0 raios bloqueados nas portas), herói e slice reabertos em processo novo sem dados faltando, IDs/marcadores/âncoras/instâncias idênticos, masterplan e rotas PASS.
- Estado: **W3.2 congelado e pronto para integração Unity.** Pendências na integração: portão de pedestres do Horizonte, interação de porta, iluminação interior da escada.

## W4 — Orla das Palmeiras (costa sul)

- Terreno: `Tools/Map/sa_terrain.py` (`shore_z`, perfil de praia). Areia 1,6%, calçadão a +3 m, a cidade desce ~930 m até a orla; greide máximo das vias continua ≤ 4% na costa (R03.0 4,02%).
- Spec: bloco `coast` em `masterplan_spec_v1.json`; R03 (Av. das Palmeiras) estendida até a Avenida da Orla (z ≈ −3664). IDs preservados.
- Gerador: `Tools/Blender/create_coast.py` → `ArtSource/Blender/World/Coast/SantaAurora_Orla_v1.blend` (terreno de 5 m, mar, espuma, calçadão de pedra portuguesa, ciclovia, avenida, 2 píeres, farol, torres de salva-vidas, quiosques, ~2,2 mil palmeiras, guarda-sóis, rochas, barcos, ~240 prédios de orla em massing com faixas de pavimento).
- Masterplan v1.5 regenerado com mar e cores de areia; pipeline `Run-W15World.ps1 -NoRender` passou (masterplan, Cidade Antiga, kit).
- Capturas: `ArtSource/Blender/World/Reviews/W4/`.
- Vida: ~1,4 mil carros (LOD1, famílias genéricas originais), ~1,9 mil pedestres, ~2,4 mil banhistas, ~680 nadadores (figuras autorais, instâncias GN).
- Hora do dia: `Tools/Blender/render_orla_time_of_day.py` (dia / dusk / night). A noite liga a coleção `09_Night_Lights` (~700 spots nos postes + luar) e acende as vitrines; a coleção fica oculta no render diurno.
- Pendente: a Cidade Antiga base ainda não foi refeita em alta fidelidade ao sul de z = −3400 (terreno novo vale, arte antiga); prédios da orla são massing; figuras e palmeiras são de baixa/média complexidade (não final); sem integração Unity.

## Resort R1 — terreno jogável da Orla (2026-10-06)

- `Tools/Map/export_resort_site.py` exporta o terreno real da Praia das Palmeiras (320 × 520 m, passo 2 m) como heightfield + JSON em `FacilityOps/Assets/_Game/Resources/Resort/`, com um **lote plano de 256 × 160 m (cota 4,53 m)** atrás da Avenida da Orla para o grid de construção.
- Unity: `ResortSite` monta malha, colisão, mar e alinha `GridManager` e limites da câmera. Menu **Resort Aurora > Create Site Scene** gera `Assets/_Game/Scenes/ResortSite.unity` pronta para Play (B constrói, R gira, WASD/borda/scroll/Q-E câmera).
- Compilação em batch sem erros; capturas de revisão em `ArtSource/Blender/World/Reviews/R1/`. Não testado em Play interativo. Visual provisório (cores por altura, sem PBR).
- Próximo: economia/tempo (`GameManager`, `TimeManager`, `EconomyManager`), hóspedes e kit modular. O recorte Blender `W5S` fica como cenário de contexto.
