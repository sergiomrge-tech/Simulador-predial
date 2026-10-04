# W2.5 — Cidade Antiga: relevo visual, wear pass e refino dos heróis (gate de fidelidade visual)

**Data:** 2026-10-04 · **Branch:** `claude/w1-masterplan` · **Blender:** 5.2.1 LTS headless
**Capturas:** `ArtSource/Blender/World/Reviews/W2_5/` (77 imagens) · **Estágio:** base de produção, **não é arte final**.
O layout aprovado (vias, lotes, IDs, heróis), os saves e o protótipo Unity não foram alterados. Os blockouts W1.5 continuam no arquivo como LOD1 oculto.

---

## 1. Relevo urbano (Parte 1)

### Como foi implementado
O relevo vive em um termo próprio em `Tools/Map/sa_terrain.py`, `Terrain.relief()`:
- usado pelo validador, pelas rotas, pelo masterplan, pela base e pelos heróis;
- aplicado só na região da Cidade Antiga, com borda suave de 250 m;
- calculado sobre uma grade de 10 m com interpolação bilinear.

| Feature | Parâmetros | Efeito |
|---|---|---|
| `alto_aurora` | gaussiana em (−2250, −850), σ 280 m, +20 m | o Alto da Aurora vira o ponto mais alto do bairro |
| `vale_corrego` | fundo de vale ao longo da Av. do Trabalho (R02), σ 130 m, −9 m, some ao norte de z −250 | vale urbano com córrego canalizado no canteiro central, seguindo em galeria até o canal |
| `ondulacao_urbana` | λ 360 m, ±5,2 m, zerada perto das arteriais e coletoras (25–140 m) | diferenças suaves entre quarteirões; os corredores principais continuam nivelados |
| `hero_pads` | platô plano em cada lote de herói (cota média), transição de 10 m | heróis assentados; os taludes ficam fora do lote |

Diferença Alto da Aurora → fundo do vale: cerca de 27 m.

**Rampas resultantes (vias da Cidade Antiga):**
- locais: máx. ≈15%, 90% abaixo de ≈7%;
- principais: máx. ≈11%;
- arteriais: máx. 3,8%, dentro do limite de 6% do validador;
- câmeras escolhem automaticamente uma rua de 10,5% (`w25_02`) e uma rua descendo ao vale com 8,7% (`w25_05`).

Validação do masterplan **PASS**; rotas **sem pontos inalcançáveis**.

### Como o relevo aparece na base (`create_oldtown_base.py`)
- **Implantação dos edifícios:** a entrada fica no nível da rua (cota do ponto frontal do lote). No lado que desce aparece o embasamento: **1.511 pódios** de pedra/concreto. No lado que sobe, **1.356 muros de arrimo** com rufo.
- **Escadarias:** passagens e becos íngremes viram escadarias reais, com degraus de cerca de 17 cm, patamares e corrimãos (**19 escadarias, 362 degraus**).
- **Córrego canalizado:**
  - **2,44 km** de canal de concreto com 2 m de profundidade no canteiro da R02;
  - parapeitos, guarda-corpo, lâmina d'água e bueiros sob os cruzamentos;
  - o terreno é aberto sob o canal, e tampas/bocas de lobo foram retiradas de cima dele.
- **Vias, calçadas e meio-fio** seguem o terreno (já amostravam a superfície). O masterplan de 8×8 km foi regenerado com o mesmo relevo.

---

## 2. Wear pass (Parte 2)

### Shader (todos os materiais procedurais, `sa_materials._wear`)
Controlado por um nó `SA_WEAR` em cada material (0 = sem desgaste) e por um fator aleatório por objeto (0,55–1,35×):
- **alvenaria** (reboco, concreto, tijolo, pedra, pintura): escorrimento vertical de chuva, umidade ascendente na base com borda irregular, remendos de reboco com tom diferente;
- **pisos** (asfalto, pavimento, concreto, cerâmica): sujeira de circulação em superfícies horizontais;
- **aço pintado e metal:** ferrugem que escorre e se concentra na parte de baixo.

29 materiais carregam o nó. Novos: `pedra_portuguesa`, `cimentado`.

### Decals (alpha dithered)
- Tipos: `decal_umidade`, `decal_sujeira`, `decal_oleo`, `decal_pneu`, `decal_ferrugem`.
- **Nas vias:**
  - 2.766 trechos de marcas de pneu;
  - 1.316 remendos de asfalto;
  - 891 manchas de óleo.
- **Nos 9 heróis** (`sa_w2.wear_pass`):
  - umidade na base das fachadas e escorrimento sob janelas;
  - sujeira nas soleiras;
  - óleo em vagas, docas e pátios;
  - marcas de pneu em acessos (portão da Oficina, rampa do Horizonte, doca do Teatro).

**Comparação antes/depois:** `w25_06_rua_antes_wear.jpg` × `w25_07_rua_depois_wear.jpg`. É a mesma câmera, com `SA_WEAR` 0 e 1. Remendos e marcas de pneu são geometria e aparecem nas duas.

---

## 3. Heróis secundários refinados (Parte 3)

Gerados por `create_w2_hero_generic.py`, agora com um passe de caráter por herói. Todos são ficcionais.

- **Residencial Vila Antiga:**
  - varandas alternadas com guarda-corpo, varal e vasos;
  - faixa de cobogó sobre a entrada (núcleo da escada);
  - marquise com letreiro, portão gradeado na passagem de veículos;
  - pátio com árvores, varais e carros.
- **Mercearia São Jorge:**
  - letreiro pintado sobre o toldo listrado (com sanefa) e “DESDE 1978”;
  - faixa “HORTIFRUTI - FRIOS - BEBIDAS”;
  - caixotes, freezer de sorvete, cavalete de ofertas, abrigo de gás;
  - floreiras na residência de cima;
  - pátio de carga com paletes, van e tambores;
  - vagas na rua ocupadas.
- **Restaurante Dona Cida:**
  - “COMIDA CASEIRA”;
  - mesas e cadeiras sob o toldo, cavalete de cardápio, floreiras;
  - duto de exaustão da cozinha subindo pela fachada lateral;
  - abrigo de gás, caixotes e lixeiras no pátio de serviço;
  - estacionamento ocupado.
- **Auto Elétrica Ferreira:**
  - faixa pintada amarela e “BATERIAS - ALTERNADORES - INJEÇÃO”;
  - pilhas de pneus, tambores de óleo;
  - carro no elevador e outro no box 2, estante de baterias;
  - pátio com carros.
- **Escritório Contábil Paiva:**
  - brises verticais de alumínio nos pavimentos superiores;
  - marquise de entrada, placa “PAIVA CONTABILIDADE”, floreiras;
  - estacionamento dos fundos ocupado.

Todos receberam também o wear pass. Câmeras de rua foram afastadas para mostrar a relação com a rua.

**Tris:**

| Herói | W2 | W2.5 |
|---|---|---|
| apartments | 74k | 106k |
| grocery | 28k | 50k |
| restaurant | 45k | 74k |
| workshop | 23k | 39k |
| smalloffice | 44k | 52k |

## 4. Heróis principais (Parte 4)

- Lar, Oficina, Horizonte e Teatro foram regenerados sobre os platôs do relevo, com o wear pass de decals e o novo shader.
- Extras:
  - varal nos fundos do Lar;
  - marcas de pneu e óleo no acesso e no box da Oficina;
  - carros na garagem térrea e marcas de pneu na rampa do Horizonte;
  - pneu e óleo na doca do Teatro.
- Câmeras dentro da cidade: `w25_08…11`.

## 5. Bairro (Parte 5)

- **Fiação aérea:** 2.192 vãos com catenária (2 fases + telecom) entre postes vizinhos.
- **Calçadas variadas por testada:**
  - calçada: 2.246;
  - cimentado: 1.288;
  - intertravado: 1.062;
  - pedra portuguesa: 1.078.
- **Novos acessórios por regra** (agora 39.848 no total):
  - muros com portão nas casas com recuo (2.455);
  - lixeiras (3.633);
  - caçambas em oficinas e armazéns (601);
  - puxadinhos na laje (425);
  - coberturas de lona improvisadas (242);
  - arbustos (2.784);
  - entulho em terrenos vazios (327).
- **Mantidos do W2:** postes, transformadores, caixas técnicas, hidrômetros, bocas de lobo, hidrantes, placas, recuos com piso, floreiras e balizadores.

## 5b. Vegetação urbana de calçada (complemento W2.5)

**Distribuição** (`oldtown_layout._street_trees`, determinística):
- A densidade segue o caráter do bairro:
  - residencial baixo: 0,88;
  - misto baixo: 0,62;
  - núcleo nobre e transição: 0,42;
  - núcleo ferroviário/misto: 0,14–0,22;
  - oficinas: 0,12;
  - pátios/depósitos: 0,04;
  - vias industriais: ×0,3.
- A densidade cresce com a distância do miolo denso (até +55% a 900 m).
- **Contra a regularidade:**
  - espaçamento variável de 8–17 m;
  - 18% dos lados de rua sem árvores;
  - trechos inteiros pulados;
  - pares ocasionais de mudas;
  - uma espécie dominante por lado de rua (62%), o que varia a leitura de quarteirão para quarteirão.
- **Sem obstrução:**
  - nada a menos de 8 m das esquinas;
  - afastamento de postes, luminárias, hidrantes, placas e caixas técnicas (1,8–2,8 m);
  - afastamento das entradas dos lotes (1,4 m; 4,5 m em portões de oficinas, armazéns, depósitos e estacionamentos);
  - nenhuma árvore nos recuos dos heróis ou nas praças.
- **Sob a fiação** só entram espécies pequenas (ipê e muda).
- **Resultado:**
  - 4.773 árvores de calçada;
  - 175 terrenos vazios viraram pracinhas (grama, caminho cimentado, guia, 2–4 árvores);
  - 1.434 arbustos sobre muros de arrimo, o que reforça a leitura do relevo.
- As árvores de praça e de quintal do W1.5 receberam espécie por contexto. Total da camada Vegetation: **8.251 instâncias**.
- **Na calçada:** 4.773 covas (terra com aro de concreto) ou canteiros curtos de grama entre árvores em ruas residenciais largas. As fileiras regulares das ruas principais foram removidas.

**Espécies** (proxies melhores que as esferas do W1.5, ainda provisórios; 100–400 tris cada, copas suavizadas):

| Espécie | Instâncias | Perfil |
|---|---|---|
| oiti | 2.164 | copa densa e arredondada |
| sibipiruna | 864 | copa larga e chata |
| mangueira | 1.111 | domo escuro, em quintais e pracinhas |
| ipê amarelo | 1.114 | pequeno, florido |
| ipê rosa | 554 | pequeno, florido |
| muda | 972 | árvore jovem com tutores |
| palmeira | 38 | praças e ruas nobres |
| arbusto | 1.434 | — |

**Capturas:** `w25_19_rua_arborizada.jpg`, `w25_20_pracinha.jpg`, `w25_21_residencial_obliqua.jpg`. A vista oblíqua mostra o norte residencial mais arborizado que o miolo.

**Custo:**
- tris instanciados de 23,70 M para 24,82 M (**+4,7%**);
- +0,24 M em meshes simples (covas, canteiros, pracinhas).

IDs, marcadores e lotes foram re-auditados e continuam **idênticos**.

**Limites:** as copas ainda são proxies poligonais (sem folhas em alpha nem LOD); falta vegetação rasteira em taludes e terrenos.

## 6. Desempenho e organização (Parte 6)

| Base da Cidade Antiga | W2 | W2.5 | Δ |
|---|---|---|---|
| Objetos | 2.160 | 2.476 | +316 (subcélulas de fiação e de pódios/arrimos) |
| Tris de meshes simples (inclui heróis vinculados e LOD1 oculto) | 2,50 M | 3,01 M | +0,51 M (escadarias, canal, arrimos, fiação, decals de via) |
| Instâncias | 59.574 | 70.002 | +10.428 (acessórios de bairro) |
| Tris instanciados | 22,76 M | 23,70 M | **+4,2%** |
| Maior mesh única | 34,5 k | 34,5 k | sem geometria gigante nova |

- Coleções por camada/subcélula preservadas (1 km / 250 m).
- Novos objetos `OT_SlopeWorks_*` (Architecture) e `OT_Infrastructure_Wires_*` (Infrastructure).
- Heróis continuam vinculados (`W2I_*`), e a lógica do LOD1 oculto foi mantida.
- O wear é shader, sem custo de geometria. Decals são planos finos.

## 7. Validação (Parte 7)

| Item | Resultado |
|---|---|
| Reabertura em processo novo, sem dados faltando | **PASS** — 9 heróis, base da Cidade Antiga (com os 9 vinculados), masterplan v1.5, kit |
| Validação do masterplan / rotas | **PASS** / sem inalcançáveis |
| 9 heróis vinculados | **PASS** — `w2_heroes_linked` = 9 |
| IDs e marcadores de gameplay | **IDÊNTICOS** ao commit anterior: 98 marcadores `GP_/SLOT_/PROXY_`, 9 âncoras `HERO_*`, 16 `facility_id`, 9 instâncias vinculadas, 13.003 lotes (IDs e variantes) |
| Posições | mudam só em altura (o relevo), por projeto; a Unity não usa estas coordenadas ainda |

Script de auditoria: `Tools/Blender/audit_ids_markers.py`.

## 8. Capturas (Parte 8) — `Reviews/W2_5/`

| # | Pedido | Arquivo |
|---|---|---|
| 1 | Cidade Antiga oblíqua | `w25_01_cidade_antiga_obliqua.jpg` |
| 2 | Rua com relevo | `w25_02_rua_relevo.jpg` (10,5%) |
| 3 | Lar exterior | `w2_home_01_rua.jpg`, `w2_home_02_entrada.jpg`, `w25_08_lar_na_cidade.jpg` |
| 4 | Lar interior | `w2_home_03_apto12_interior.jpg`, `w2_home_04_apto12_cozinha_banheiro.jpg` |
| 5 | Oficina exterior | `w2_garage_01_rua.jpg`, `w2_garage_02_portao.jpg`, `w25_09_oficina_na_cidade.jpg` |
| 6 | Oficina interior | `w2_garage_03_galpao.jpg`, `w2_garage_04_recepcao_quadro.jpg`, `w2_garage_06_bancada.jpg` |
| 7 | Horizonte exterior | `w2_horizonte_01_rua.jpg`, `w25_10_horizonte_na_cidade.jpg` |
| 8 | Horizonte área técnica | `w2_horizonte_05_quadro_tecnico.jpg`, `w2_horizonte_06_casa_bombas.jpg`, `w2_horizonte_07_medidores.jpg` |
| 9 | Teatro exterior | `w2_imperial_01_largo.jpg`, `w2_imperial_02_portico.jpg`, `w25_11_teatro_na_cidade.jpg` |
| 10 | Teatro interior | `w2_imperial_04_plateia.jpg`, `w2_imperial_05_palco.jpg`, `w2_imperial_06_quadro_antigo.jpg` |
| 11 | Apartamentos | `w2_apartments_01_rua.jpg` (+ entrada, interior, técnico, aérea) |
| 12 | Mercearia | `w2_grocery_01_rua.jpg` (+ …) |
| 13 | Restaurante | `w2_restaurant_01_rua.jpg` (+ …) |
| 14 | Oficina local | `w2_workshop_01_rua.jpg` (+ …) |
| 15 | Pequeno escritório | `w2_smalloffice_01_rua.jpg` (+ …) |
| 16 | Rua antes/depois do wear | `w25_06_rua_antes_wear.jpg` / `w25_07_rua_depois_wear.jpg` |
| 17 | Desnível urbano | `w25_05_vale_panorama.jpg` (rua descendo ao vale, 8,7%), `w25_03_alto_aurora_desnivel.jpg` |
| 18 | Canal/vale × cidade | `w25_04_vale_corrego.jpg` (córrego canalizado), `w25_18_cidade_antiga_vale_canal.jpg` (masterplan: Cidade Antiga → vale da R02 → canal) |

---

## 9. Gate visual da Cidade Antiga: **PARTIAL PASS**

**Atendido:**
- relevo visível e coerente ao nível da rua (subidas, descidas, embasamentos, arrimos, escadarias, vale com córrego);
- bairro mais vivido (fiação, muros e portões, lixeiras, puxadinhos, calçadas por testada, carros, varais);
- desgaste consistente e reversível (`SA_WEAR`);
- os 5 heróis secundários com identidade própria;
- IDs e marcadores intactos.

**Por que não é PASS pleno:**
1. Nas vistas aéreas e oblíquas o relevo ainda é discreto: o terreno tem um material único e falta oclusão e sombra de talude.
2. Vegetação e carros são proxies; não há pedestres.
3. Edificações genéricas da cidade são famílias LOD1 com acessórios. Interiores fora dos heróis não existem.
4. Iluminação é de revisão (exposição −1,4, céu estourado). Vidros não transmitem.
5. Decals procedurais não substituem texturas autorais (pichações, cartazes legíveis, sujeira pintada à mão).

---

## 10. O que falta para o visual final e próximos passos

1. Material de terreno com variação (grama, terra, cascalho) e taludes com vegetação rasteira para ler o relevo de cima.
2. Vegetação autoral com LOD (N2), carros e mobiliário com modelagem final.
3. Look de iluminação (W4): exposição, céu, AO, vidro com transmissão, iluminação noturna.
4. Texturas PBR autorais e decals pintados nos heróis (W3); variantes LOD0 das famílias mais vistas.
5. Revisão visual do usuário destas capturas antes de replicar o padrão para outros distritos.

---

**Continuação:** o W3 (vertical slice de alta fidelidade) está documentado em `Docs/W3_HIGH_FIDELITY_VERTICAL_SLICE.md`.
