# W3 — Cidade Antiga High Fidelity Vertical Slice

**Data:** 2026-10-04 · **Branch:** `claude/w1-masterplan` · **Blender:** 5.2.1 LTS headless (EEVEE)
**Arquivo do slice:** `ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend`
**Capturas:** `ArtSource/Blender/World/Reviews/W3/` (82 imagens reais)
**Continuação de:** `Docs/W2_5_VISUAL_FIDELITY_GATE.md` (W2.5, PARTIAL PASS)

---

## 1. Recorte (corredor do vertical slice)

**Retângulo:** x −3000…−2250, y −2500…−1250. São 15 subcélulas de 250 m, alinhadas ao streaming (1 km / 250 m).

**Conteúdo:**
- Lar inicial, Oficina Aurora, Edifício Horizonte e o cliente do Capítulo I **Mercearia São Jorge** (serviço I.2, luzes da mercearia);
- o vale da Av. do Trabalho com o córrego canalizado;
- ruas com relevo (até 11,2% dentro do recorte), praça, pracinhas e infraestrutura urbana.

**Como o slice é montado:**
- É gerado pelo mesmo gerador da Cidade Antiga, em modo `--slice`. As subcélulas do recorte são refeitas em alta fidelidade.
- Fora dele, 844 objetos das subcélulas vizinhas (até 900 m) são **vinculados** da base do distrito como contexto.
- Os nomes de streaming são os mesmos: não há duplicação nem costura entre os dois.
- Os demais distritos **não** receberam acabamento.

## 2. Entregas

| Item do W3 | Entrega |
|---|---|
| **2. Materiais PBR autorais** | 21 conjuntos tileáveis (BaseColor, Normal OpenGL, Roughness, AO, Height e Metallic nos metais) em `ArtSource/Textures/` (detalhes abaixo). |
| **1. Terreno e relevo** | Material `terreno_w3` em todo o distrito (detalhes abaixo). Cotas e rampas preservadas; validação do masterplan PASS. |
| **4. Vegetação de produção** | `Tools/Blender/sa_vegetation.py` (detalhes abaixo). |
| **5. Iluminação / céu** | Look de produção (`sa_bl.production_look`, detalhes abaixo); variante de fim de tarde em `w3_18`. |
| **6. Vidro** | Vidro dielétrico com opacidade por Fresnel e sombra transparente (detalhes abaixo). |
| **3. Fachadas LOD0** | Famílias do recorte geradas em `detail="lod0"` (detalhes abaixo). |
| **7. Clutter e decals** | No recorte, por regra de uso (detalhes abaixo). Mantido do W2.5: pneu, óleo, remendos, umidade, sujeira, lixeiras, caçambas, muros, fiação. |
| **8. Heróis** | Lar, Oficina, Horizonte e os demais com texturas, vidro funcional e luz interior recalibrada; Mercearia com interior abastecido (detalhes abaixo). Estados H0–H4 e G0–G4 e todos os slots preservados. |

**Materiais PBR — detalhe:**
- Fonte procedural **própria**: `Tools/Blender/bake_pbr_textures.py`, com ruído e voronoi periódicos num toro 4D e grades inteiras por tile, para que nada mostre emenda. Baked com Cycles, 1024², JPEG.
- Conjuntos: reboco, concreto, tijolo, asfalto, meio-fio, pedra portuguesa, intertravado, ladrilho hidráulico, aço pintado, galvanizado, ferrugem, madeira, cerâmica, telha, plástico, borracha, grama, terra, cascalho, pastilha e granito.
- `sa_materials.build_textured` aplica os mapas sobre UVs métricas com tamanho real de tile.
- Por cima dos mapas ficam a variação macro em espaço de objeto, o tingimento por instância e as camadas de desgaste do W2.5 (`SA_WEAR`).
- Procedência e licença: `ArtSource/Textures/texture_library_w3.json` e `Tools/Skills/asset_license_registry.csv` (propriedade do projeto, sem fonte externa).

**Terreno — detalhe:**
- Blend de grama, solo exposto, cascalho e concreto residual, guiado pela declividade (normal) e por ruído.
- Taludes e trechos gastos mostram terra.
- No recorte: malha de 4 m (era 8 m), 15.470 tufos de grama e ervas em taludes e terreno livre, e 8.995 ervas em frestas de meio-fio e calçada.

**Vegetação — detalhe:**
- 7 espécies (oiti, sibipiruna, mangueira, ipê amarelo, ipê rosa, muda, palmeira) mais arbusto.
- LOD0 com tronco, galhos primários e secundários e 250–630 cards de folha em alpha recortado (0,3–1,4 mil tris).
- LOD1 guardado no arquivo (`OT_Lib_Vegetation_LODs`); LOD2 é o proxy do W2.5, usado fora do recorte.
- Tufos de grama (cards de lâminas) e de erva.
- Máscaras procedurais próprias, sem imagens externas.

**Iluminação — detalhe:**
- Céu físico com sol (sun 5,0, sky 0,3, sol quente).
- Tone mapping **Khronos PBR Neutral**, exposição −1,4: o céu não estoura e a saturação dos materiais é preservada.
- AO e GI por raytracing ou horizon scan, sombras suaves.
- Luzes interiores recalibradas (×3,5, mais quentes) para o equilíbrio com a luz do dia através do vidro claro.
- Base pronta para dia/noite: sol e céu são os únicos drivers.

**Vidro — detalhe:**
- `vidro` e `vidro_vitrine` são claros (heróis e vitrines com interior modelado).
- `vidro_fachada` é refletivo com um falso interior sutil, para as famílias sem interior. Janelas não são mais placas opacas.

**Fachadas LOD0 — detalhe:**
- Molduras e peitoris em todas as fachadas, inclusive fundos e laterais.
- Barra de rodapé, rufo/cornija, condutor pluvial com sapata, cabo de serviço até a caixa de medição, placa de número, grelhas de ventilação e ganchos de varal nos fundos.

**Clutter — detalhe:**
- Cartazes fictícios em comércios e imóveis abandonados ("ALUGA-SE", "VENDE-SE", "FESTA NA PRACA", "CONSERTOS").
- Sacos de lixo junto a comércios.
- Paletes junto a armazéns e oficinas.
- Placas de proibido estacionar em portões.
- 36 pontos de obra com cones em torno de bueiros.

**Mercearia — interior:**
- Gôndolas com mercadorias nos dois lados.
- Expositor refrigerado com portas de vidro.
- Banca de hortifrúti.

## 3. Métricas — complexidade (W2.5 × W3)

| Métrica | Base do distrito W2.5 | Base do distrito W3 | Slice W3 (recorte + contexto vinculado) |
|---|---|---|---|
| Objetos | 2.509 | 2.512 | 2.198 (844 vinculados) |
| Meshes | — | 2.254 | 1.964 |
| Tris de meshes simples | 3,25 M | 3,27 M | 2,70 M |
| Instâncias | 75.195 | 75.195 | 93.643 (+tufos e ervas) |
| Tris instanciados | 24,82 M | 24,82 M | 24,12 M |
| Maior mesh | 34,5 k (foyer do Teatro) | igual | igual |
| Materiais em uso | — | 398 | 456 |
| Luzes | — | 66 | 66 |
| Texturas | 0 (procedural) | 108 arquivos únicos (21 conjuntos × 4–6 mapas, 1024²) | idem |

**Memória de texturas:**
- 108 mapas únicos de 1024², cerca de 0,57 GB em RGBA8 sem compressão (cerca de 0,15 GB em BC7 na engine).
- O "textureMemoryMB_est" do Blender (2,9–3,3 GB) conta a mesma imagem uma vez por arquivo vinculado (cada `.blend` de herói tem seu datablock). No disco são 19 MB (JPEG).

**Vegetação LOD0:** cerca de 1,3 mil tris para árvores grandes e 0,6 mil para ipês. No recorte as árvores somam menos de 5 M de tris instanciados. Na Unity, os LOD groups (LOD0/LOD1/proxy) reduzem isso com a distância.

## 4. Validações

| Verificação | Resultado |
|---|---|
| Reabertura em processo novo, sem dados faltando | **PASS** — slice W3, base do distrito, masterplan v1.5, kit e os 9 heróis. O verificador agora resolve imagens vinculadas relativas à biblioteca de origem. |
| Masterplan / rotas | **PASS** / sem inalcançáveis |
| 9 heróis vinculados | **PASS** — base com `W2I_*` × 9; slice com os 9 (locais ou do contexto) |
| IDs e marcadores | **IDÊNTICOS** ao commit anterior: 98 `GP_`/`SLOT_`/`PROXY_`, 9 âncoras `HERO_*`, 16 `facility_id`, 9 instâncias vinculadas (`Tools/Blender/audit_ids_markers.py`) |
| Footprints e lotes | **IDÊNTICOS**: 13.003 lotes (ID, variante, x, y); heróis inalterados |
| Streaming | **PRESERVADO**: 181 subcélulas no manifesto do distrito; o slice usa as mesmas 15 e vincula as vizinhas pelos mesmos nomes |
| Licenças | Só fontes próprias (texturas e vegetação procedurais), registradas |

## 5. Capturas (Reviews/W3)

| Pedido | Arquivo(s) |
|---|---|
| Visão geral do corredor | `w3_01_corredor_visao_geral.jpg` |
| Rua subindo/descendo | `w3_02_rua_relevo.jpg` (11,2%) |
| Terreno/talude | `w3_03_terreno_talude.jpg` (fraca, ver limitações), `w3_17_relevo_aereo.jpg` |
| Lar exterior / interior | `w3_04_lar_exterior.jpg`, `w2_home_01_rua.jpg`, `w2_home_02_entrada.jpg` / `w2_home_03…05` |
| Oficina exterior / interior | `w3_06_oficina_exterior.jpg`, `w2_garage_01_rua.jpg` / `w2_garage_03_galpao.jpg`, `w2_garage_04…06` |
| Horizonte exterior / técnico | `w3_08_horizonte_exterior.jpg`, `w2_horizonte_01_rua.jpg` / `w2_horizonte_05_quadro_tecnico.jpg`, `w2_horizonte_06_casa_bombas.jpg`, `w2_horizonte_07_medidores.jpg` |
| Cliente Capítulo I exterior / interior | `w3_10_mercearia_exterior.jpg`, `w2_grocery_01_rua.jpg` / `w2_grocery_03_interior.jpg`, `w2_grocery_04_tecnico.jpg` |
| Detalhe de material PBR | `w3_12_material_pbr_detalhe.jpg` |
| Vegetação | `w3_13_vegetacao.jpg` |
| Vidro exterior / interior | `w3_14_vidro_exterior.jpg` / `w2_home_03_apto12_interior.jpg` (céu e rua vistos pelas janelas) |
| Clutter e decals | `w3_15_clutter_decals.jpg` |
| Fim de tarde | `w3_18_fim_de_tarde.jpg` |
| Antes/depois W2.5 × W3 | `Reviews/W2_5/w25_08…11` × `Reviews/W3/w3_04/06/08` e `w25_01_cidade_antiga_obliqua` × `w25_01_cidade_antiga_obliqua` (W3, mesma câmera) |

## 6. Comparação W2.5 × W3

| Aspecto | W2.5 | W3 |
|---|---|---|
| Materiais | procedurais (ruído) com desgaste | texturas PBR autorais tileáveis (normal, roughness, AO, metallic) + desgaste |
| Terreno | material único "terra" | blend grama/terra/cascalho/concreto por declividade; tufos nos taludes |
| Vegetação | proxies de esferas | árvores com galhos e folhas em alpha, 7 espécies, LOD0/LOD1; grama e ervas |
| Vidro | placa opaca | dielétrico com Fresnel e transparência; interiores visíveis nos heróis |
| Luz | Standard, exposição −1,4, céu estourado | Khronos PBR Neutral, céu sem clipping, AO/GI raytrace, interiores quentes |
| Fachadas do recorte | LOD1 | LOD0 com molduras, rufos, condutores, cabos, medidores, números |
| Clutter | acessórios genéricos | cartazes, sacos de lixo, paletes, placas, cones de obra por regra de uso |

## 7. Gate W3: **PARTIAL PASS**

**Atendido:**
- materiais deixaram de ser placeholders;
- vegetação deixou de ser proxy;
- vidro funcional;
- iluminação com identidade e céu controlado;
- recorte coerente com relevo legível ao nível da rua;
- desempenho controlado (instancing, sem mesh gigante, streaming e IDs intactos).

**Por que não é PASS (lista objetiva de correções):**
1. **Carros:** ainda são proxies de caixas e são muito visíveis nas vistas de rua (`w3_10`). Precisam de modelos com rodas, vidros e silhueta reais.
2. **Edificações de fundo:** mesmo em LOD0, continuam famílias instanciadas com volume simples (e cores de reboco saturadas no LOD1). Faltam variantes autorais por quarteirão no recorte e telhados com mais detalhe.
3. **Tufos de grama:** os cards ainda leem como "pente" de perto. Precisam de lâminas curvas e variação de altura e cor.
4. **Relevo aéreo:** ainda moderado. A captura `w3_03` (talude) caiu sobre telhados e não demonstra bem os arrimos; é preciso escolher uma câmera dedicada a um talude real.
5. **Interiores:** a luz ainda é fria/escura em alguns ambientes (sala do Apto 12, galpão), e a câmera da Mercearia (`w2_grocery_03`) não enquadra as gôndolas. Ajustar câmeras e luzes de preenchimento.
6. **Decals:** procedurais (umidade, sujeira, óleo) e os cartazes têm texto simples. Faltam decals pintados (pichação fictícia, cartazes ricos, manchas autorais).
7. **Distância:** sem LOD automático na Unity ainda, e sem imposters para o contexto vinculado.

## 8. Próximos passos recomendados

Corrigir os itens 1–5 no mesmo recorte (sem expandir para outros distritos) e reavaliar o gate. Depois, exportar o recorte para a Unity (FBX + texturas, mantendo os IDs) como primeira cena de alta fidelidade.
