# W3.2.x — Patch urbano do corredor (Cidade Antiga, vertical slice v0.1)

Branch `gpt/unity-world-integration`. Escopo: só o corredor Lar → Oficina → Horizonte → Mercearia (15 sub-células). Nada de W3.3, sem expandir a cidade, sem mexer em saves, IDs, `GP_`/`SLOT_`/`PROXY_`, `facility_id`, âncoras ou escala 1:1. Os heróis (`W2_*.blend`) não foram alterados. Tudo abaixo foi medido com auditores próprios (`Tools/Blender/audit_w32x_corridor.py`, `Tools/Map/audit_w32x_roads.py`) e confirmado em capturas reais do Unity.

## O que causava cada problema (diagnóstico)

| # | Sintoma | Causa real encontrada |
| --- | --- | --- |
| 1 | Ruas retas, cruzamentos secos | Cada aresta do grafo era um retângulo reto entre dois nós (média 41 m; deflexão média de 12,7° nos nós intermediários, até 138°); o desenho não tinha raio nem curvatura entre cruzamentos. |
| 2 | Carros enterrados / flutuando | A altura vinha de **um** ponto no centro do carro e só havia *pitch* (nenhum *roll*, nenhum apoio por roda). Medido no slice anterior: 183 de 878 carros com roda >6 cm abaixo do piso (um a 1,31 m), 72 flutuando, 124 com >12 cm de diferença entre rodas. |
| 3 | Telhados / coberturas flutuando | A laje plana fica em `H−0,10` m, mas as peças de cobertura (caixas, claraboias, painéis, antenas, volumes técnicos) foram posicionadas em `H+0,05`: **15 cm no ar** em 10.076 peças. Em lotes em declive, anexos e puxadinhos ficavam sem apoio no terreno. |
| 4 | Fachadas sem porta | Não faltava porta no modelo (as 45 variantes têm). Dois acessórios eram **caixas sólidas**: o revestimento de reforma (`w31_reforma*`, 45% dos sobrados/casas) cobria o térreo inteiro, porta incluída; a escada externa (`w31_escada_ext`) era um bloco no meio da fachada. Além disso, hidrômetros, caixas, postes e árvores ficavam sobre a linha da porta, e lotes em declive tinham a porta no ar, sem degraus. |
| 5/6 | "Massa cinza" entre prédios, falta de acabamento | O terreno usa o material procedural `terreno_w3` (grama/terra/cascalho/concreto por declividade e ruído), que o Unity **não lê**: exportava como uma cor chapada (0,30 / 0,30 / 0,18), sem textura. É o cinza-oliva liso das capturas anteriores. |
| 7 | Ruas "que não se conectam" | Em cada nó intermediário, dois retângulos de estrada se encontram em ângulo: cunha de vazio num lado e sobreposição no outro (até ~3 m nas dobras maiores). A malha lógica, em si, estava conectada. |

## Correções

- **Curvas** (`Tools/Map/oldtown_layout.py`, `_curve_network`): cada cadeia local/main entre cruzamentos é reamostrada (~26 m) e recebe um arco suave de raio grande (amplitude ≤ 7,5 m, proporcional ao comprimento, atenuada perto de heróis); cada trecho é validado contra obstáculos e cruzamentos, com fallback (outro lado → metade da amplitude → reta). Becos sem saída não são curvados.
- **Cantos arredondados** (`_round_corners`): ruas que apenas viram (nó de grau 2, deflexão >35°) ganham arco (raio 9 m local / 14 m main), propagado a lotes, calçadas, postes e carros porque todos leem o grafo.
- **Juntas** (`create_oldtown_base.py`, `strip`/`joint_ends`): faixa, calçada e meio-fio usam normal e largura de esquadro (*miter*) nos nós intermediários, eliminando as cunhas.
- **Carros**: apoio pelas **quatro rodas**, por raios contra a malha real de via e terreno, com ajuste de plano (*pitch* + *roll*) e altura sem nenhuma roda sob o piso; vaga com degrau, inclinação excessiva (pitch >11°, roll >5°), superfície não plana ou obstáculo lateral é descartada, nunca forçada.
- **Coberturas e peças de chão**: cada acessório é registrado na colocação e testado contra a superfície real da variante do prédio (cobertura) ou o piso (peças de chão); peça flutuando é abaixada até o apoio, peça fora da laje é recolhida ou removida.
- **Entradas**: soleira + marquise alinhadas à porta real de cada variante; revestimento de reforma reconstruído **por variante com recortes das aberturas reais**; escada externa deslocada para longe da porta (ou removida); hidrômetros, caixas, postes, hidrantes e árvores removidos da linha porta → rua; degraus que acompanham o terreno nos lotes em que a soleira fica acima do chão.
- **Terreno** (`export_unity_cell_fbx.py`, `split_terrain_materials`): reproduz por face os mesmos mascaramentos do material procedural (declividade, ruído nos mesmos comprimentos de onda) e atribui `grama`/`terra`/`concreto` PBR autorais, em vez de uma cor chapada.
- **Unity**: reexportação das 15 células, reimportação, NavMesh de referência, rota contínua e gates refeitos; argumento `-worldSliceRoute` no Player para rodar a rota de evidências.

## Resultados medidos

| Item | Antes | Depois |
| --- | --- | --- |
| Carros no corredor | 878; **183 enterrados**, **72 flutuando**, **124 inclinados** | 499; **0 / 0 / 0** (auditor independente por roda). 105 vagas candidatas descartadas por degrau (30), superfície não plana (4), inclinação (67) ou obstáculo (4) |
| Peças de cobertura sem apoio | 10.076 (≈ 15 cm no ar) | **0** no verificador do gerador; auditor independente por raio: 12 de 700 amostras ainda sinalizadas (1,7%), peças deitadas sobre telhado de quatro águas, visualmente apoiadas |
| Coberturas fora da laje | 21 | 21 recolhidas ou removidas |
| Peças de chão flutuando / enterradas | 884 / 38 | 913 ajustadas, 9 anexos removidos |
| Cadeias de rua curvadas | 0 | 596 de 1.357 na região (118 no corredor); 187 curtas demais e 506 bloqueadas por obstáculo ou cruzamento ficaram retas; 68 de beco sem saída ficaram retas |
| Cantos arredondados | 0 | 100 na região (18 no corredor); 15 ficaram secos por falta de comprimento |
| Deflexão média em nós intermediários | 12,7° (máx. 138°) | 5,9° (p95 24,9°; 36 nós > 25°, máx. 101°: arcos e cantos não arredondados) |
| Ângulos de cruzamento próximos de 90° | 62% | 56% |
| Segmentos de rua ≥ 12 m / média | 41 m médios | média 20,4 m (cadeias reamostradas; 394 trechos < 12 m, a maioria nos arcos) |
| Conectividade (corredor) | conectada | conectada: 99,9% das arestas num só componente; os 2 restantes cruzam a borda do recorte (ficam ligados fora dele); 16 becos sem saída |
| Entradas com soleira + marquise | — | 1.556 lotes |
| Degraus de acesso | — | 483 degraus em 196 lotes |
| Objetos fixos tirados da linha de entrada | — | 792 hidrômetros, 117 caixas elétricas, 18 caixas de telecom, 30 postes, 9 transformadores, 1 hidrante, 27 árvores e 40 canteiros de árvore |
| Terreno no Unity | cor chapada sem textura | grama / terra / concreto texturizados, por face |
| NavMesh de referência (Unity) | 5/5 | 5/5 `PathComplete` |

## Validação no Unity

- Importação (`ImportPilot`): PASS, 15 células, 4 heróis. EditMode: 22 aprovados, 0 falhas, 4 opt-in (rodados à parte: runtime, escada a pé, Lar e modo normal, todos PASS).
- **Caminhada contínua no Player a 1920×1080 (Development):** PASS. Lar → rua → Oficina → rua → Horizonte → interfone/portão → portaria → escada → 4º andar → quadro técnico → saída → Mercearia → retorno ao Lar: 2.808 m em 950 s, 0 penetrações, 0 travamentos, 3 portas abertas por interação real, save/load verificado 2×.
- Desempenho (vsync = 60 FPS, sem afirmação de folga): FPS médio 60,0 em todos os trechos; **um** quadro de 56,5 ms (mínimo 17,7 FPS) em `SA_M01_02_S02_00` no trecho Horizonte → Mercearia, sem operação de célula associada; nos demais trechos o pior quadro foi de 16,7 a 18,8 ms. Memória 418 MiB usados / 1.110 MiB reservados no fim; GC ≈ 3 KB/quadro; SetPass 51–62. Draw calls e batches: **indisponível** (os contadores leem 0 no Player). Triângulos por quadro até 39,9 M (inclui sombras).

## Capturas (`Docs/Previews/UnityVerticalSliceV01/`)

Todas são capturas reais do Player a 1920×1080. Os 15 pontos do percurso (`01-lar` … `15-retorno-lar`) foram refeitos no mundo corrigido; as de evidência têm o prefixo `W32x-`:

- A (ruas e traçado): `A1-rua-curva-residencial`, `A2-curva-com-intersecao`, `A3-rua-acompanhando-relevo` (11,1%), `A4-trecho-lar-oficina`, `A5-trecho-proximo-horizonte`.
- B (superfícies): `B6-espaco-entre-predios-acabamento`, `B7-rua-com-calcada-legivel`, `B8-transicao-rua-calcada-lote`, `B9-grama-canteiro` (terreno vago; não há praça verde a menos de 45 m da rota), `B10-concreto-piso-coerente`.
- C (correções críticas): `C11-carro-apoiado-rua-com-relevo` (pitch 3,95°), `C12-outro-carro-em-area-inclinada` (pitch 3,35°, roll 3,93°), `C13-telhado-cobertura-corrigido`, `C14-fachada-com-porta-legivel`, `C15-conexao-de-rua-corrigida`.
- D (antes/depois, mesmas coordenadas nos dois builds): `D16-rua-curva`, `D17-carros-mercearia`, `D19-espaco-cinza` (+ `D19b`), `D20-conexao-de-rua`.

Limites honestos sobre D: o build "antes" foi capturado enquanto ainda existia e depois substituído (o disco ficou sem espaço para guardar os dois), então só há "antes" real do Unity para os 10 pontos de comparação planejados. Neles, o ganho claro e reproduzível é o chão (cinza chapado → grama/terra texturizadas) e o traçado das ruas curvadas. Os pares de frente de herói (Lar, Oficina, Horizonte) saem idênticos, como esperado. **Não tenho captura "antes" do Unity que mostre um carro enterrado ou um telhado flutuando** (os 10 pontos planejados foram escolhidos por coordenadas, não por defeito, e o build antigo não existe mais para novas capturas); para esses itens a prova é numérica (tabela acima) e as capturas `C11`–`C13` mostram o estado corrigido. Por isso não há par D18 (telhado).

## O que este patch NÃO afirma

- Não há detector automático de "porta visualmente obstruída" ou de "espaço cinza" em todo o corredor; as causas foram achadas e corrigidas na fonte, e verificadas em amostras visuais. Não afirmo que não restam casos visíveis.
- As curvas são suaves, mas moderadas: 506 cadeias ficaram retas por colisão com obstáculos ou outras ruas, e os cruzamentos continuam com 56% de ângulos próximos de 90°.
- O acabamento visual segue de massing refinado, não final.

## Incidente de ambiente (registrado)

O disco `C:` do computador chegou a 100% durante a primeira importação. O Unity gravou um artefato de importação truncado para o herói Horizonte e o Player caía ao carregar o `level13` (`SA_M01_02_S02_00`: "file is corrupted"). A bisseção (camadas da célula) apontou `Architecture/Hero_horizonte`; reimportar com espaço livre resolveu e o build final passou. O disco continua com ~2,7 GB livres, o que é arriscado para builds e para o `git`. Foram removidos apenas temporários desta sessão (`%TEMP%\claude\bash-edit-diff`, ~1 GB) e caches reconstruíveis do Unity (`PlayerDataCache`, `Bee`).
