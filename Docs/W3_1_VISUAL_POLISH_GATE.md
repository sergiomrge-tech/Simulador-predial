# W3.1 — Cidade Antiga Visual Polish Gate

Data: 2026-10-04 · Branch: `claude/w1-masterplan` · Escopo: o mesmo recorte de 15 subcélulas do W3
(`ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend`). Não foram tocados: Unity, runtime de streaming,
saves, C# de gameplay, branch `gpt/unity-world-integration`. Histórico do W3 preservado em `Docs/W3_HIGH_FIDELITY_VERTICAL_SLICE.md`.

**Classificação: PARTIAL PASS.** Nas vistas de rua, os carros e as fachadas de fundo já não parecem placeholders evidentes. Os
carros, porém, ainda são facetados de perto, e a vista aérea do corredor continua dominada pelas famílias W2 (detalhes abaixo).

## 1. Entregas por item

| Item | Entrega | Onde |
|---|---|---|
| **1. Carros** (prioridade) | 6 famílias autorais sem marca: hatch compacto, sedan, utilitário leve (picape), SUV compacto, van de serviço e hatch antigo. Cada carro tem caixas de roda recortadas no perfil (sem caixa colada), rodas com pneu/aro/cubo, estufa de vidro escuro com colunas B/C, para-choques, grade, faróis e lanternas emissivos, retrovisores, maçanetas, friso de porta e placa fictícia (“SA? 0X00”, gerada por crc32). Pintura nova ou gasta (oxidação/poeira). LOD0 (~5–10 mil tris), LOD1 (sem bevel, 8 segmentos de roda) e proxy de distância por família. Malha única por variante (duplicatas lincadas). | `Tools/Blender/sa_vehicles.py`; `Kit.car` (`sa_detail.py`) agora usa os carros autorais em todos os heróis; recorte: `OT_Vehicle_<subcélula>_NNN`, biblioteca `OT_Lib_Vehicles` + `OT_Lib_Vehicles_LODs` |
| Distribuição | 889 carros estacionados nas ruas do recorte, inclinados conforme a rampa da rua. Ruas locais: estacionamento em um lado só em ~45% dos casos e 45% de carros velhos/gastos. Ruas principais: carros mais novos. Picapes e vans de serviço a até 30 m da Oficina/Horizonte. Frentes de heróis e de arrimos ficam livres. | `create_oldtown_base.py` (bloco “W3.1 parked vehicles”) |
| **2. Prédios de fundo** | Variantes por lote, com tema por quadra (~60 m), para que vizinhos compartilhem uma “época de reforma”: revestimento do térreo (pastilha, cerâmica, azulejo, granito, pintura verde, tijolo), marquise de concreto ou metálica, sacadas com guarda-corpo, escada externa de sobrado, anexo de fundos com telha de fibrocimento, platibanda elevada, portão de aço, rack de condensadoras na cobertura e grades de janela. | peças `ACC_w31_*` instanciadas por GN |
| **3. Grama** | O tufo de 3 cards (“pente”) foi substituído por lâminas curvas e afiladas, de geometria opaca e cor por vértice (raiz mais escura, mistura de lâminas verdes e secas), com altura, largura, inclinação, torção e touceiras irregulares variadas. São 4 tipos: grama curta, grama alta, mato (lâminas + folhas largas) e erva. Os terrenos vagos têm cobertura densa (17.007 tufos) com uma trilha pisada mais rala. Cada tufo tem 74–204 tris. | `sa_vegetation.tuft`, `TUFT_SPECS` |
| **4. Taludes** | 4 arrimos de frente de rua em terrenos vagos em aclive, sem alterar a cota do terreno: o muro acompanha o solo existente ~3 m para dentro do lote. Painéis escalonados (pedra, concreto ou tijolo), capeamento, buzinotes, canaleta no pé do muro, faixa de umidade/contato, escorrimentos, escada recortada com corrimão tubular, mato e arbustos no solo contido, e grafite em parte dos muros. A captura dedicada é feita da calçada oposta, na altura do olho, sem telhados no caminho. | bloco “W3.1 street-front taludes”, `OT_SlopeWorks_W31_*`, câmeras `CAM_W31_Talude(_B)` |
| **5. Interiores** | Volume de irradiância assado por herói (somente cena; equivalente Unity: Adaptive Probe Volume). Isso elimina o vazamento do ambiente azul do céu através das paredes, que era a causa dos interiores frios. Há também preenchimento quente retangular sob o teto: Apto 12 (luz rebatida suave; a lâmpada nua continua sendo a única luminária do estado H0), galpão da Oficina (3 áreas de ~2,2 kW, equivalente high-bay) e salas dos heróis genéricos. Câmera da Mercearia no fim do corredor, olhando ao longo das gôndolas. No galpão, foram adicionados pallets, pneus, tambores, caixotes e manchas de óleo deixados pelo inquilino anterior (estado G0). | `sa_w2.bake_interior_probe`, `sa_w2.area_fill`; `create_w2_hero_{home,garage,generic}.py` |
| **6. Decals autorais** | 26 imagens RGBA geradas pelo próprio Blender (câmera ortográfica, emissão, filme transparente): 8 cartazes lambe-lambe (forró, aulas de violão com canhotos destacáveis, circo, aluga-se, mutirão do córrego, feira de trocas, baile, cachorro perdido), 5 grafites/tags, 5 placas pintadas de comércio, marcas de topografia/água/vala, estêncil “não estacione”, etiquetas de perigo e número, restos de cartaz colado e tinta descascando. Todos os nomes, telefones e textos são inventados, sem marcas nem conteúdo ofensivo. Material com erosão de alfa, desbotamento e sujeira por instância. Regras de colocação por lote (placas nos comércios, grupos de cartazes, grafite em depósitos/abandonados, número da casa, tinta descascando no tecido antigo) e marcas de spray no asfalto junto a bueiros. | `Tools/Blender/bake_decals_w31.py` → `ArtSource/Textures/decals_w31/` (3,5 MB); `Tools/Blender/sa_decals.py` |
| **7. Árvores/calçadas** | 2 indivíduos extras (galhada diferente) por espécie comum (oiti, sibipiruna, mangueira, ipê, jovem), escolhidos por posição, para evitar clones vizinhos. 150 copas podadas (escala ≤ 0,74) sob a fiação. Raízes superficiais e terra transbordando nas covas. Portões de veículos e frentes de heróis livres (raio 3,2 m). A semente das árvores agora é determinística (crc32; o hash de string do Python variava entre processos). | `sa_vegetation.tree(variant=…)`, bloco de árvores de rua |

Outros itens:
- registro de licença: `veh.santaaurora.w31` e `decal.santaaurora.w31` em `Tools/Skills/asset_license_registry.csv`;
- modo `w31` em `verify_world_v1_5.py`;
- montagem das comparações em `Tools/Map/compose_w3_w31_comparison.py` (Pillow, já instalado; nada novo foi instalado).

## 2. Capturas (`ArtSource/Blender/World/Reviews/W3_1/`)

| # | Pedido | Arquivo |
|---|---|---|
| 1 | Rua com carros novos | `w31_01_rua_carros.jpg` |
| 2 | Outra rua com variedade | `w31_02_rua_carros_variedade.jpg`, `w2_grocery_01_rua.jpg` |
| 3 | Quadra com variantes | `w31_03_quadra_variantes.jpg` |
| 4 | Fachada de perto | `w31_04_fachada_closeup.jpg` |
| 5 | Grama | `w31_05_grama.jpg` |
| 6 | Talude/arrimo | `w31_06_talude_arrimo.jpg`, `w31_06b_talude_arrimo.jpg` |
| 7 | Apto 12 | `w2_home_03_apto12_interior.jpg`, `w2_home_04_apto12_cozinha_banheiro.jpg` |
| 8 | Oficina (galpão) | `w2_garage_03_galpao.jpg`, `w2_garage_06_bancada.jpg` |
| 9 | Mercearia | `w2_grocery_03_interior.jpg` |
| 10 | Decals | `w31_10_decals.jpg`, `w31_04_fachada_closeup.jpg` |
| 11 | Rua arborizada | `w31_11_rua_arborizada.jpg` |
| 12 | Visão geral do corredor | `w31_12_corredor_visao_geral.jpg`, `w31_12b_relevo_aereo.jpg` |
| 13 | W3 × W3.1 | `w31_13_comparacao_w3_w31_1.jpg`, `w31_13_comparacao_w3_w31_2.jpg` |

Também há: `w31_14_rua_relevo`, `w31_15_mercearia_exterior`, `w31_16_clutter`, `w31_17_oficina_exterior`,
`w31_18_horizonte_exterior` e as capturas completas dos 9 heróis (`w2_*`).

**Observação de honestidade sobre as capturas:**
- Todas as capturas acima são renders reais do Blender.
- As capturas do recorte (`w31_*`), do Lar, da Oficina e do Horizonte são da execução final.
- As de Imperial, apartments, grocery, restaurant, workshop e smalloffice vêm da execução anterior do mesmo dia (09:37). A única
  diferença de código para a versão final é a redução do bevel dos carros (2 → 1 segmento) e das rodas (18 → 14 segmentos).
- Na execução final, o render por GPU desta máquina passou a falhar ao criar o contexto OpenGL
  (`EXCEPTION_ACCESS_VIOLATION` em `DRW_gpu_context_create`, reproduzido com uma cena vazia de 64×64). Isso aconteceu depois que o
  sistema encerrou o processo por falta de memória. Os 6 heróis foram então reabertos e validados sem render (PASS).

## 3. Validações

| Verificação | Resultado |
|---|---|
| Recorte reaberto em processo novo (`--mode w31`) | **PASS**, sem dados faltando (os decals usam caminhos relativos `//`) |
| 9 heróis reabertos (`verify_w2_hero.py`) | **9 PASS** (3 com render, 6 sem render; ver observação acima) |
| Base da Cidade Antiga, masterplan e kit reabertos | **PASS** (arquivos inalterados no W3.1) |
| `validate_masterplan.py` | **PASS** (`errors: []`; `Docs/masterplan-validation-v1.json` inalterado) |
| `masterplan_routes.py` | **PASS** (`unreachable: []`) |
| Auditoria de IDs/marcadores (base) vs. linha de base pré-W2.5 | markers, heroAnchors, facilityIds, linkedInstances e libraries **idênticos** |
| Auditoria do recorte vs. recorte W3 (HEAD) | markers (GP_/SLOT_/PROXY_), heroAnchors e facilityIds **idênticos**. A diferença em `libraries` vem da cópia do HEAD extraída para outra pasta, que não resolvia os links relativos dos heróis. |
| Heróis / lotes / subcélulas | 9 instâncias de herói, 13.003 lotes, 181 subcélulas no manifesto (15 no recorte), 38 slots de estado no recorte |
| Saves, `.meta`, Unity, C# | não tocados |

## 4. Impacto de desempenho (recorte, `reopen_w31.json` vs. `reopen_w3.json`)

| Métrica | W3 | W3.1 | Observação |
|---|---|---|---|
| meshTris | 2,70 M | 8,53 M | ~5,8 M vêm dos 889 carros em LOD0, que no Blender são duplicatas lincadas de 19 malhas |
| instancedTris | 24,12 M | 31,78 M | grama densa, variantes, decals, árvores extras |
| instâncias GN | 93.643 | 116.713 | |
| materiais | 456 | 535 | 26 decals + pinturas de carro + lâminas |
| texturas (imagens) | 629 | 655 | +26 decals (3,5 MB em disco) |
| memória de textura (estimativa do Blender) | 3.346 MB | 3.380 MB | a estimativa conta cada biblioteca lincada em dobro |
| luzes | 66 | 66 | os preenchimentos e as sondas ficam nos arquivos dos heróis (somente cena) |
| objetos | 2.198 | 3.219 | carros como objetos individuais |

Os carros pesam mais do que deveriam. No Unity, eles devem entrar como instâncias GPU com LOD Group:
- LOD0 até ~25 m;
- LOD1 (~0,4–0,9 mil tris) até ~80 m;
- proxy a partir daí.

Com isso, o custo visível fica perto de 1 M tris. LOD1 e proxy já estão em `OT_Lib_Vehicles_LODs`, mas a integração não foi feita
(fora do escopo: não tocar na Unity).

## 5. Comparação W3 × W3.1

| Tema | W3 | W3.1 |
|---|---|---|
| Carros | caixas coloridas (proxy) | 6 famílias com rodas visíveis, vidro escuro, faróis, placas fictícias e estado de pintura |
| Fundo | famílias repetidas | revestimentos de reforma por quadra, marquises, sacadas, escadas externas, condensadoras, grades |
| Grama | 3 cards cruzados (“pente”) | lâminas curvas variadas, terrenos vagos densos, trilha pisada |
| Talude | câmera sobre telhados | arrimo de frente de rua com drenagem, escada e mato, visto da calçada |
| Interiores | azul/frio (vazamento do céu), Mercearia sem gôndolas | luz quente e ocluída, gôndolas enquadradas, galpão com escala |
| Decals | manchas procedurais e 4 cartazes de texto | 26 decals autorais desgastados, colocados por regra |
| Árvores | clones vizinhos, sem poda | 3 indivíduos por espécie comum, poda sob fiação, raízes e terra |

## 6. Limitações (por que não PASS)

1. **Carros de perto:** a silhueta e as rodas convencem a 10–40 m, mas a 3–5 m o volume ainda é facetado (perfil de ~7 pontos, sem
   curvatura de capô/teto), os aros são discos lisos e não há interior visível pelo vidro. Próximo passo: perfil com mais pontos e
   painéis curvos, aro com raios e banco/painel simples atrás do vidro.
2. **Vista aérea:** as variantes são de fachada (térreo/cobertura) e quase não aparecem do alto; a massa das famílias W2 continua
   repetitiva vista de cima.
3. **Taludes baixos:** o relevo validado do recorte só permite muros de até 1,18 m em frente de rua sem mexer na cota. Taludes mais
   altos dependem de um novo passe de relevo (decisão do coordenador).
4. **Fachadas de vidro:** muitas fachadas comerciais LOD0 têm vitrine contínua, então cartazes e placas às vezes caem sobre o vidro.
   Falta uma máscara de “parede cheia” por família.
5. **Iluminação de interiores:** preenchimentos e sondas só existem nos arquivos dos heróis. No recorte (onde os heróis entram por
   link), os interiores vistos de fora não têm sonda.
6. Sem LOD/imposters no Unity (fora do escopo, herdado do W3).
7. 6 capturas de herói não foram re-renderizadas após a última alteração dos carros (falha de GPU do ambiente; ver seção 2).
