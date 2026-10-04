# W3.2 — Cidade Antiga Final Visual Gate

Data: 2026-10-04 · Branch: `claude/w1-masterplan` · Base: W3.1 `ebeff56` · Escopo: o mesmo recorte de 15 subcélulas
(`ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend`). Não foram tocados: Unity, C#, runtime de streaming, saves,
masterplan global, cotas do terreno, branch `gpt/unity-world-integration` e os 9 arquivos de herói.

**Classificação: PARTIAL PASS.** Dos cinco critérios de PASS, três passam (carros, decals, integridade/performance), a vista aérea
melhorou muito mas ainda é de massas repetidas com telhados variados, e dos 4 heróis principais três têm leitura interna convincente da
rua (Oficina, Horizonte, Mercearia). O **Lar não passa**: de dia só uma janela do Apto 12 mostra o interior. Detalhes na seção 6.

## 1. Entregas por item

| Item | Entrega | Onde |
|---|---|---|
| **1. Carros a 3–5 m** | Reescrita do LOD0 das 6 famílias (IDs, famílias, distribuição, instancing e proxy preservados). Carroceria **loftada** (perfil lateral PCHIP de capô, deck e teto; ombro com raio, tumblehome, cantos arredondados em planta; túneis reais de caixa de roda), **estufa** loftada à parte (teto curvo, para-brisa e vidro traseiro inclinados, colunas A/B/C), vidro **translúcido** (Fresnel, sombra transparente) sobre interior mínimo: painel, volante com haste, console, 2 bancos dianteiros e banco traseiro. Rodas com perfil de pneu com ombro, aro com lábio, prato, 5–6 raios, cubo, disco e pinça. Frisos de caixa de roda, soleira, linha de caráter, frisos de porta, maçanetas, retrovisor com haste, grade, faróis e lanternas (carcaça + núcleo emissivo + lente), escapamento e placa fictícia. | `Tools/Blender/sa_vehicles.py` |
| LOD / custo dos carros | LOD0 **11,3–16,2 mil tris** por variante (média 14,1 mil); LOD1 **1,8–2,0 mil** (sem interior, estações grossas, roda simples); proxy de duas caixas. No Blender do recorte, **LOD0 só nos 314 carros a até 70 m das câmeras de altura humana e das frentes de herói; os outros 575 usam o LOD1 compartilhado**. No Unity isso é o LOD Group. | `create_oldtown_base.py` (bloco “W3.2 LOD policy”) |
| **2. Repetição aérea** | Kit de coberturas: telhado colonial parcial (4 larguras), telha fibrocimento, telhado metálico, platibandas alta / curva / em degraus, laje com caixa d’água pequena e com caixa em torre, casa de escada, claraboias, varal, chaminé, exaustores, volume técnico, fileira solar, condensadoras, puxadinho de fundos, e **7 acabamentos de laje** (manta, óxido, verde, branco, azul, fibro, cerâmica) por variante plana. Tudo por seed determinística (lote + hábito de cobertura por quarteirão de ~60 m), com pesos por caráter de bairro (residencial baixo, núcleo, oficinas/depósitos). 1.412 peças + lajes coloridas. | `Tools/Blender/sa_roofs.py`; bloco “W3.2 roof variety” em `create_oldtown_base.py` |
| **3. Máscara de fachada** | `facade_free()`: o gerador agora registra, por variante, as aberturas reais da fachada (portas, janelas, vitrine, porta de enrolar, caixa da persiana — `sa_arch.LAST_FRONT`) e só aceita decal em vão **sem abertura** (margem 0,2 m). Letreiros usam a faixa de letreiro física quando ela existe (394) ou a parede cheia acima da vitrine (62); 442 tentativas sobre vidro foram descartadas. Cartaz “poster” antigo e revestimento de reforma não são mais colocados em lojas. | `create_oldtown_base.py` (`facade_free`, `pick_free`) |
| **4. Interiores vistos da rua** | Causa: os heróis entram por link da coleção `W2_<id>`; preenchimentos, sol e sonda ficam em `W2_<id>__SceneOnly`, que **não** viaja no link. Solução: `dump_hero_fills.py` extrai os preenchimentos (sem sol) para `hero_interior_fills_w32.json`; o slice os recria como luzes de cena com sombra (8 luzes, só os 4 heróis principais por causa do limite de sombras do EEVEE) e **assa 4 volumes de irradiância** (Lar, Oficina, Horizonte, Mercearia), eliminando o vazamento azul do céu. Arquivos de herói intactos. | `Tools/Blender/dump_hero_fills.py`, `ArtSource/Blender/World/OldTown/hero_interior_fills_w32.json`, `create_oldtown_base.py` |
| **5. Rua de proximidade** | Câmeras escolhidas por pontuação sobre os dados gerados: 4 de carro a 4,4–4,9 m; 2 de rua a 1,65 m, de pé na pista, com um carro a 3,4–5,6 m, outro a 9–16 m, fachada com letreiro/decal, árvore e calçada; fachada comercial; 4 de herói e 4 variantes de entardecer. | `create_oldtown_base.py`, `verify_world_v1_5.py --mode w32` |

## 2. Capturas (`ArtSource/Blender/World/Reviews/W3_2/`)

| # | Pedido | Arquivo |
|---|---|---|
| 1 | hatch a 3–5 m | `w32_01_carro_hatch_3m.jpg` |
| 2 | sedan / SUV a 3–5 m | `w32_02_carro_sedan_3m.jpg`, `w32_02b_carro_suv_3m.jpg` |
| 3 | picape de serviço | `w32_03_van_picape_servico.jpg` (a van só aparece 2 vezes no recorte; não há câmera de van) |
| 4 | rua em primeira pessoa | `w32_04_rua_primeira_pessoa_A.jpg` |
| 5 | segunda rua | `w32_05_rua_primeira_pessoa_B.jpg` |
| 6 | aérea com telhados | `w32_06_aerea_telhados.jpg` |
| 7 | quarteirão oblíquo | `w32_07_quadra_obliqua.jpg` |
| 8 | fachada comercial sem decal sobre vidro | `w32_08_fachada_comercial.jpg` |
| 9–12 | Lar, Oficina, Horizonte, Mercearia | `w32_09_…`, `w32_10_…`, `w32_11_…`, `w32_12_…` (+ variantes `…b_entardecer`) |
| 13 | comparação carros W3.1 × W3.2 | `w32_13_comparacao_carros_w31_w32.jpg` |
| 14 | comparação aérea W3.1 × W3.2 | `w32_14_comparacao_aerea_w31_w32.jpg` |
| 15 | corredor | `w32_15_corredor_visao_geral.jpg`, `w32_15b_aereo_corredor.jpg` |

Todas são renders reais do Blender, na GPU (a falha de contexto OpenGL do W3.1 não se repetiu). As referências W3.1 das comparações foram
renderizadas de um checkout do commit `ebeff56` com as mesmas câmeras (`Tools/Map/compose_w32_comparison.py`). As capturas vêm de duas
execuções em processos novos no mesmo `.blend` final: a lista completa e `--only w32_15`, refeita porque as variantes de entardecer
(sobrescrevem o sol) vinham antes e vazavam para as vistas do corredor; elas agora vêm por último.

## 3. Validações

| Verificação | Resultado |
|---|---|
| Slice reaberto em processo novo (`--mode w32`) | **PASS**, sem dados faltando |
| Heróis | os 9 `W2I_*` presentes; os 9 arquivos de herói **não foram alterados** (nenhuma reabertura extra necessária) |
| `validate_masterplan.py` / `masterplan_routes.py` | **PASS** (`errors: []`, `unreachable: []`; `Docs/masterplan-validation-v1.json` inalterado) |
| IDs / `GP_` / `SLOT_` / `PROXY_` / âncoras / `facility_id` / instâncias vinculadas (`audit_ids_markers.py`, W3.2 × W3.1) | **idênticos** (70 marcadores, 4 âncoras, 6 facility ids, 9 instâncias). A lista de bibliotecas só difere no caminho absoluto do checkout de referência |
| Lotes / subcélulas | 13.003 instâncias de edifício, 15 subcélulas no recorte, 38 slots de estado, 181 subcélulas no manifesto (não regenerado) |
| Base, kit e masterplan | não regenerados; arquivos inalterados |
| Saves, `.meta`, Unity, C# | não tocados |
| Licença / proveniência | `veh.santaaurora.w32` e `roofs.santaaurora.w32` em `Tools/Skills/asset_license_registry.csv` |
| Aviso do Blender | `Shadow buffer full (≈4300 / 4096)` ainda aparece em algumas capturas (muitas luzes locais com sombra no recorte, já presentes no W3.1); pode causar sombras faltando em luzes distantes. Não foi mascarado |

## 4. Impacto de desempenho (`reopen_w32.json` × `reopen_w31.json`)

| Métrica | W3.1 | W3.2 | Observação |
|---|---|---|---|
| meshTris | 8,53 M | 8,45 M | carros LOD0 só perto das câmeras; 314 LOD0 (≈4,4 M) + 575 LOD1 (≈1,1 M). Com os 889 em LOD0 seriam ≈ 12,5 M só de carros |
| instancedTris | 31,78 M | 32,52 M | +0,74 M pelas peças de cobertura |
| instâncias GN | 116.713 | 116.436 | |
| objetos | 3.219 | 3.416 | +luzes de preenchimento, sondas, peças de telhado, câmeras |
| materiais | 535 | 544 | +vidro translúcido, lentes, aro, interior, bancos, liner |
| imagens | 655 | 655 | nenhuma textura nova |
| luzes | 66 | 74 | +8 preenchimentos de herói |
| tamanho do `.blend` | 18,4 MB | 24,7 MB | +6 MB: 4 volumes de irradiância assados e peças de telhado |
| geração do slice | ~1,5 min | ~2,6 min | inclui o bake das 4 sondas (~30 s cada) |

Custo adicional dos carros LOD0: de 5–10 mil tris (W3.1) para 11–16 mil; do telhado/volumes: +0,74 M tris instanciados e +1.412 instâncias
(mais 440 lajes coloridas).

## 5. Comparação W3.1 × W3.2

| Tema | W3.1 | W3.2 |
|---|---|---|
| Carro a 4 m | perfil de ~7 pontos, facetado, aros lisos, vidro preto opaco, sem interior | superfícies suaves, caixas de roda reais, rodas com raios, vidro translúcido com interior, lâmpadas com volume |
| Aérea | lajes cinza quase idênticas | lajes em 7 acabamentos, telhados parciais, platibandas de 3 perfis, caixas, claraboias, volumes técnicos |
| Decals | cartazes e placas sobre vitrine | só em parede cheia, letreiros na faixa física |
| Interiores | Oficina/Mercearia/Horizonte escuros por fora | Oficina, Horizonte e Mercearia legíveis pela abertura; Lar ainda fraco |

## 6. Limitações (por que não PASS)

1. **Lar (Edifício Santa Clara, Apto 12):** o estado H0 é uma unidade vazia com uma lâmpada nua; de dia a janela do Apto 12 mostra um interior
   quente e as demais ficam escuras. Não parece “ocupado”. Resolver exige acender outras unidades (luzes de ocupação nos andares, decisão de
   arte/narrativa) ou uma janela de entardecer como padrão de captura. As variantes `…b_entardecer` mostram o efeito, sem substituir o gate.
2. **Vitrine da Mercearia:** o vidro grande continua escuro; só a porta e a vitrine lateral mostram as gôndolas.
3. **Vista aérea:** a variação vem de coberturas e lajes; as massas (famílias W2, cores de fachada) ainda se repetem. As telhas cerâmicas
   das famílias com telhado inclinado são todas da mesma cor (trocá-las mudaria `libraryIndex`/mesh das famílias).
4. **Carros:** estilizados (sem texturas de vidro/marca e com pintura procedural). A 3–5 m deixam de parecer placeholder, mas o capô e a
   frente têm pequenas ondulações de sombreamento na região dos arcos de roda, e as lanternas ficam nas faces de ponta, não nos cantos.
5. **Sombras:** estouro do buffer de sombras do EEVEE em algumas capturas (seção 3).
6. **LOD no Unity** continua fora de escopo; o LOD0/LOD1/proxy do Blender é referência para o LOD Group.
7. Taludes altos (≥ 1,2 m) dependem de um novo passe de relevo (herdado do W3.1).
