# W2 — Cidade Antiga Base (Etapa D) — relatório parcial

> **Atualização W2.5 (2026-10-04):** relevo urbano, wear pass, refino dos 5 heróis secundários e bairro mais vivido. Ver `Docs/W2_5_VISUAL_FIDELITY_GATE.md` (gate visual: **PARTIAL PASS**). As seções abaixo descrevem o estado W2; contagens novas estão no relatório W2.5.

**Data:** 2026-10-04 · **Branch:** `claude/w1-masterplan` · **Blender:** 5.2.1 LTS headless
**Estágio:** base de produção, **não é arte final**. Faltam texturas autorais, decals, desgaste pintado, LOD0 final, vegetação autoral, look de iluminação e integração na Unity. Nada foi alterado no protótipo Unity, nos saves, nos IDs ou nas coordenadas de runtime. Nenhum add-on, MCP ou asset externo foi instalado ou usado; todos os materiais são procedurais e próprios.

---

## 1. O que foi entregue

| Item do NEXT_TASK | Entrega | Evidência |
|---|---|---|
| 1. Kit modular (N3) | Biblioteca `Tools/Blender/sa_detail.py` com 30+ componentes detalhados e chanfrados, cada um com pivô próprio e pronto para virar prefab: janelas de correr e basculantes, portas internas com batente/alizar/folha articulada, porta metálica de entrada, quadro de distribuição, tomadas e interruptores, chuveiro elétrico, louças, bancada, caixa d'água de 1000 L, padrão de entrada, interfone, caixas de correio, extintor, escada em U e props H0/G0. Linha de amostras no kit (`KIT_Detalhe_W2`, marcada no Asset Browser). | `w2_kit_detalhe.jpg`, `ArtSource/Blender/Kits/SantaAurora_CidadeAntiga_Kit_v1.blend` |
| N3 — esquinas e rebaixos | Esquinas de calçada com filete curvo: curva quadrática cujo controle é o cruzamento das linhas de meio-fio, com face de meio-fio contínua (antes era um chanfro reto). Rebaixo de calçada com piso tátil nas esquinas do núcleo histórico. | 2.223 esquinas curvas, 983 rebaixos (`oldtown_generation_report.json → w2`); `ot_04`, `ot_05` |
| 2. Materiais PBR | +14 materiais procedurais (cerâmicas, azulejo, louça, granito, inox, tecidos, plásticos, papelão, parede pintada, concreto aparente), `piso_intertravado` e emissivo de lâmpada. Veio de madeira refeito: faixas finas e de baixo contraste no lugar de anéis grandes. Proveniência: 100% procedural/autoral, sem fonte externa. | `ArtSource/Materials/material_library_v1.json`, `w2_kit_materiais.jpg` |
| 3. Repetição (N1) | Acessórios por regra, com semente estável por lote (crc32 do ID), instanciados por subcélula: caixas d'água (plástico e fibrocimento), aquecedor solar, antenas, parabólicas, condensadoras na frente e no fundo, padrão de entrada, tubos de descida. Peças leves (sem bevel, poucos segmentos), porque são vistas da rua. | 29.381 instâncias novas em 181 subcélulas (`OT_Accessories_*`, camada Architecture) |
| 4. Ambiente urbano (N4) | Recuos dos heróis em piso intertravado, com floreiras nas esquinas do lado da rua e linha de balizadores que deixa livre o eixo da entrada. O Horizonte ganhou muro, gradil, portões, marquise com letreiro e canteiros no próprio herói. | 18 floreiras, 158 balizadores; `ot_05_lar_inicial.jpg`, `w2_horizonte_01/02/09` |
| 5–6. Heróis A, B e C | Um `.blend` por herói (seção 2) em frame local sob um empty raiz posicionado no mundo. | `ArtSource/Blender/World/OldTown/Heroes/` |
| 7. Desempenho | Instanciamento mantido, peças por andar ou componente (nenhuma geometria única gigante), janelas leves mescladas por andar no Horizonte, contagens antes e depois (seção 3). | `Reviews/W2/before/reopen_oldtown.json` × `Reviews/W2/reopen_oldtown.json` |
| 8–9. Reabertura e capturas | Todos os arquivos foram reabertos em processo novo, sem dados faltando. 33 capturas reais. | `Reviews/W2/reopen_*.json`, `Reviews/W2/*.jpg` |

---

## 2. Heróis

Cada herói é gerado a partir de `oldtown_heroes_v1.json` (cômodos, entradas, vagas, slots). Os footprints, os IDs (`facility_id`) e as posições no mundo não mudaram. A raiz `W2_<id>_ROOT` carrega a transformação do mundo, e todos os filhos ficam em coordenadas locais com a frente em −Y.

### A. Lar inicial — Edifício Santa Clara, Apto 12 (`create_w2_hero_home.py`)
- Paredes reais com duas peles (reboco externo e pintura interna), vãos recortados, rodapé cerâmico e frisos de laje. Fachada sem variação de tinta por andar.
- Térreo com porta metálica, marquise, degraus, número, caixas de correio, interfone e padrão de entrada. Corredor central com 4 unidades por andar e portas fechadas; a do Apto 12 está entreaberta.
- Escada em U com abertura nas lajes. Cobertura com platibanda e rufo, 2 caixas d'água sobre base, alçapão, respiros e descidas pluviais.
- Apto 12 completo:
  - piso cerâmico e banheiro azulejado;
  - vaso, lavatório e chuveiro elétrico;
  - quitinete;
  - quadro de distribuição e interruptor na entrada, 5 tomadas;
  - lâmpada nua H0 com eletroduto aparente, rodapé;
  - props H0 (colchão, cadeira velha, caixas) e a maleta do Guto (permanente);
  - slots H0–H4 como empties com tamanho.
- Condensadoras e mangueiras na fachada. Recuo com 2 vagas, passagens laterais.
- **111 mil tris, 152 meshes, 11 luzes, 32 objetos interativos.** Capturas: `w2_home_01…07`.

### B. Oficina Aurora, estado G0 (`create_w2_hero_garage.py`)
- Galpão com pórticos de aço (7 quadros), terças galvanizadas e telhado de duas águas atrás de platibanda, com telhas translúcidas, cumeeira, calha e descidas.
- Pilastras expressando os pórticos, letreiro pintado desbotado (o letreiro novo é o slot G4), marquise da recepção.
- Paredes internas e portas derivadas dos cômodos do JSON por um planejador genérico (`sa_w2.partition_plan`): recepção, escritório, banheiro, depósito, almoxarifado, com lajes a 3 m.
- Portão de enrolar parcialmente aberto (interativo), porta da recepção, porta traseira do depósito, janelas com grade e basculantes altos.
- Serviços:
  - quadro geral de 12 circuitos;
  - padrão de entrada;
  - 6 luminárias high-bay;
  - caixa d'água sobre o banheiro, louças;
  - eletroduto aparente com tomadas na bancada.
- G0: bancada velha, estante única, caixas, PC antigo na mesa dobrável, cadeira, quadro de chamados, balcão da recepção, maleta do Guto. Slots G1–G4 e mezanino reservado (G3).
- Pátio: 3 vagas com batentes, zebrado de acesso de veículo, guia, quintal lateral com alambrado e tambores.
- **59 mil tris, 70 meshes, 8 luzes.** Capturas: `w2_garage_01…08`.

### C. Edifício Horizonte (`create_w2_hero_horizonte.py`)
- 12 pavimentos (térreo de 4 m), separados em objetos por andar: casca, janelas e varandas. Pastilha na torre e granito no térreo, friso por andar.
- Janelas leves mescladas por andar (LOD0-light), cortinas variadas por regra e planos internos provisórios para os apartamentos fechados.
- Varandas com variação: fechamento em vidro em cerca de 30%, condensadoras, vasos e varal.
- Núcleo com escada em U em todos os pavimentos e 2 elevadores com portas inox, botoeira e indicador no térreo e no 4º andar.
- Térreo:
  - portaria com fachada de vidro, porta dupla, balcão com monitor e 24 caixas de correio;
  - sala de medidores com 48 medições, quadro geral e prumadas;
  - casa de bombas com 2 conjuntos, barrilete, registros e painel;
  - reservatório inferior, lixeiras;
  - garagem térrea com pilares e vagas.
- 4º andar (prólogo):
  - corredor com forro rebaixado;
  - apartamentos 401–404 com portas numeradas;
  - quadro técnico (gabinete metálico com etiqueta e eletroduto para o shaft), hidrante de parede, extintor, placa “4º ANDAR”;
  - marcadores `GP_prologue_spawn_corridor` e `GP_quadro_tecnico`.
- Cobertura:
  - impermeabilização, platibanda com rufo;
  - casa de máquinas com porta e venezianas;
  - reservatório superior com escada marinheiro;
  - alçapão, para-raios e antenas.
- Terreno: muro baixo com gradil, portões fechados de pedestre e de veículo, interfone, padrão de entrada, marquise com letreiro, canteiros com arbustos-proxy, acesso de veículos e rampa para o subsolo.
- **171 mil tris, 143 meshes, 12 luzes.** Capturas: `w2_horizonte_01…11`.

### D. Teatro Imperial (`create_w2_hero_imperial.py`)
- Volumes do JSON:
  - foyer de 3 pavimentos;
  - plateia de 19 m com telhado cerâmico de duas águas;
  - caixa cênica de tijolo com 33 m;
  - doca de carga.
- Alas de camarins (listadas no registro de estruturas) preenchem o espaço entre a caixa cênica e os caminhos laterais, para que a porta de artistas (`stage_door`) tenha parede.
- Fachada clássica:
  - base rusticada, ordem gigante de pilastras;
  - janelas em arco com bandeira e balcões com balaústres;
  - cornija, balaustrada e ático com “TEATRO IMPERIAL”.
- Pórtico com 8 colunas, entablamento, frontão com “MCMXII” e escadaria.
- Interiores:
  - foyer com colunas, bilheteria e escada;
  - plateia em declive com cerca de 2,4 mil poltronas mescladas por bloco, fosso de orquestra;
  - balcão em U com cabine, forro com rosácea e lustre;
  - palco com boca de cena, cortina, galerias de manobra, urdimento e varas;
  - bastidores.
- Narrativa do Capítulo II, “patrimônio envelhecido, instalações antigas convivendo com retrofit”:
  - quadro antigo de ardósia com chaves-faca e fusíveis de porcelana, ao lado de um quadro novo de 24 circuitos com eletrodutos interrompidos no meio (retrofit inacabado);
  - HVAC sobre o telhado;
  - eletrodutos aparentes na fachada lateral;
  - andaime com lona em uma ala da fachada (reforma parcial).
- Porão técnico: só o marcador do alçapão, porão não modelado.
- **123 mil tris, 14 luzes.** Capturas: `w2_imperial_01…09`.

### Integração na base da Cidade Antiga
- `create_oldtown_base.py` liga os **nove** `.blend` W2 como **instâncias de coleção vinculadas** (`OT_Heroes_W2_LOD0`, objetos `W2I_<id>`, caminho relativo). As raízes já carregam a posição no mundo.
- O massing W1.5 de cada herói continua no arquivo, oculto no render e marcado `sa_lod = LOD1`. Os marcadores de gameplay (`GP_*`, `SLOT_*`) e os IDs não mudaram.
- Câmeras, sol e placas de chão de captura ficam numa coleção `__SceneOnly` fora da coleção do herói, então não viajam com a instância.
- `verify_world_v1_5.py` agora preserva o estado `hide_render` gravado (antes reexibia tudo e trazia o LOD1 de volta nas capturas).
- Capturas `ot_04…08` mostram os heróis W2 dentro da cidade.

### E. Demais heróis (`create_w2_hero_generic.py --hero <id>`)
Um gerador paramétrico deriva tudo do JSON:
- volumes com várias alas, sem janelas nas faces compartilhadas;
- tipo de cada entrada pela função (porta, porta de enrolar, passagem de veículo, portão de terreno);
- vitrine no lado `shopfront`;
- telhado (platibanda, duas águas, quatro águas, shed);
- toldo, volumes secundários (câmara fria), condensadoras, vagas, pátios e muros.

O térreo é equipado por função de cômodo:
- quadro, medidores, sala técnica e rack → quadros e racks com marcador `GP_`;
- salão → gôndolas (mercearia) ou mesas e cadeiras (restaurante);
- cozinha → linha de bancadas e ilha inox;
- banheiros → louças;
- estações de trabalho → mesas;
- boxes da oficina → elevadores automotivos de 2 colunas e quadro;
- depósito → estantes;
- recepção → balcão.

Andares superiores ficam fechados (casca, janelas leves e cortinas).

| Herói | Tris | Capturas |
|---|---|---|
| Residencial Vila Antiga (`apartments`) | 74 mil | `w2_apartments_01…06` |
| Mercearia São Jorge (`grocery`) | 28 mil | `w2_grocery_01…06` |
| Restaurante Dona Cida (`restaurant`) | ~45 mil | `w2_restaurant_01…06` |
| Auto Elétrica Ferreira (`workshop`) | 23 mil | `w2_workshop_01…06` |
| Escritório Contábil Paiva (`smalloffice`) | 44 mil | `w2_smalloffice_01…06` |

Esses cinco têm nível de detalhe menor que o dos quatro heróis principais (gerador genérico, interiores simplificados) e são o candidato natural a refino autoral depois da revisão do usuário.

---

## 3. Complexidade — antes × depois (Cidade Antiga completa)

Medido pela mesma rotina (`verify_world_v1_5.py`, `checks.complexity`): tris das meshes simples + instâncias × tris da peça da biblioteca. O arquivo “antes” é o `.blend` do commit anterior, extraído do git.

| Métrica | Antes (W1.5) | Depois (W2) | Δ |
|---|---|---|---|
| Objetos | 1.267 | 1.432 | +165 (subcélulas de acessórios) |
| Meshes | 1.147 | 1.312 | +165 |
| Tris de meshes simples | 1.718.696 | 1.809.830 | +91 mil (esquinas curvas, floreiras, balizadores) |
| Instâncias | 30.193 | 59.574 | +29.381 (acessórios N1) |
| Tris instanciados | 21.696.572 | 22.756.842 | **+4,9%** |
| Maior mesh única | 33.810 (HERO_apartments rear wing F00) | igual | nenhuma geometria gigante nova |
| Subcélulas / camadas | 181 / 8 | 181 / 8 | streaming 1 km / 250 m preservado |

- A primeira versão dos acessórios (com bevel) somava +13 milhões de tris; foi reduzida para +1,06 milhão antes do commit.
- Um bug de sorteio, em que todas as regras disparavam a partir da 8ª chave, foi corrigido antes da medição final.
- Os totais são da cidade inteira. Em jogo, o streaming carrega só as subcélulas próximas.

Heróis isolados: Lar 111 mil, Oficina 59 mil, Horizonte 171 mil, Teatro 123 mil tris. A maior peça única tem 34,5 mil tris (fachada do foyer do Teatro).

Com os nove heróis W2 vinculados, os tris de meshes simples da base passam de 1,81 milhão para 2,50 milhões. A contagem inclui o LOD0 W2 vinculado e o LOD1 W1.5 oculto; o render usa só um dos dois por herói.

**Plano de LOD:**
- LOD0 = heróis W2.
- LOD1 = massing W1.5 dos heróis, que já existe na base.
- Janelas leves por andar e acessórios sem bevel como LOD intermediário.
- Imposters/HLOD por subcélula ficam para a W5 (Unity).

---

## 4. Validações

- `validate_masterplan.py`: **PASS, 0 erros** (layout inalterado).
- Reaberturas em processo novo, todas **PASS, 0 dados faltando** (incluindo as bibliotecas vinculadas): `W2_home_starter`, `W2_garage`, `W2_horizonte`, `W2_imperial`, os 5 heróis genéricos, Cidade Antiga base (2.160 objetos com os 9 heróis vinculados) e kit.
- Cada herói tem exatamente uma raiz, e todos os objetos são filhos dela. Escala métrica 1:1. Os slots H0–H4 e G0–G4 estão presentes. Nenhum objeto passa de 200 mil tris.

---

## 5. Gate D parcial

| Critério | Resultado |
|---|---|
| Lar + Oficina + Horizonte com evolução concreta acima do massing | **PASS** — interiores e componentes reais nos espaços que o gameplay e o prólogo usam (capturas `w2_*`) |
| Refino do kit e do ambiente urbano verificável | **PASS** — `w2_kit_detalhe`, contagens N3/N4 no relatório de geração |
| N1/N3/N4 tratados ou medidos | **PASS (tratados, não encerrados)** — N1 +29 mil acessórios por regra; N3 esquinas curvas e rebaixos; N4 recuos com piso, floreiras e balizadores |
| Arquivos reabrem sem dados faltando | **PASS** |
| Capturas | **PASS** — 73 capturas em `ArtSource/Blender/World/Reviews/W2/` |
| Complexidade documentada | **PASS** — seção 3 |
| Relatório de continuidade | **PASS** — este documento + STATUS |

---

## 6. Limitações conhecidas (honestas)

- **Visual:**
  - interiores ainda limpos demais;
  - sem decals de sujeira, manchas, fiação e cartazes;
  - vidros opacos não mostram o exterior a partir de dentro;
  - tetos internos aparecem cinza por falta de luz rebatida;
  - a iluminação é de revisão (exposição −1,4), não o look final.
- **Horizonte:**
  - apartamentos fechados, com planos internos provisórios;
  - subsolo (−3 m) só pela rampa, sem laje e sem vagas modeladas;
  - casa de bombas simplificada, sem tubulação completa;
  - acesso à garagem térrea pelo lado oeste, logo antes do início da rampa (adaptação do JSON, que sobrepõe as duas áreas).
- Oficina em G0 propositalmente vazia; G1–G4 só como slots.
- Árvores e arbustos continuam proxies (N2), céu do skyline continua estourado (N5), fora da Cidade Antiga continua massing (N6).
- Os 5 heróis do item E vêm do gerador genérico: fachadas regulares, interiores simplificados, cadeiras e mesas básicas.
- Teatro: porão técnico e camarins internos não modelados; poltronas mescladas por bloco (instancing por poltrona fica para a Unity).

---

## 7. Próximo

1. Revisão visual do usuário das capturas `w2_*` e `ot_*` (gate visual da Cidade Antiga).
2. Refino autoral dos 5 heróis genéricos, começando pelos clientes do Capítulo I.
3. Desgaste e decals procedurais (manchas de escorrimento, sujeira de rodapé, fiação aparente, cartazes) e vidro com transmissão.
4. G1–G4 / H1–H4 modelados como variações de estado.
5. Subsolo do Horizonte e prumadas hidráulicas completas para o contrato da bomba.

Reproduzir:

```
blender -b --factory-startup --python Tools/Blender/create_w2_hero_{home,garage,horizonte,imperial}.py -- --root .   # antes da base (ela vincula os heróis)
blender -b --factory-startup --python Tools/Blender/create_w2_hero_generic.py -- --root . --hero {apartments,grocery,restaurant,workshop,smalloffice}
blender -b --factory-startup ArtSource/Blender/World/OldTown/Heroes/W2_<id>.blend --python Tools/Blender/verify_w2_hero.py -- --root .
blender -b --factory-startup --python Tools/Blender/create_oldtown_base.py -- --root .
blender -b --factory-startup ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend --python Tools/Blender/verify_world_v1_5.py -- --root . --mode oldtown --review W2
```
