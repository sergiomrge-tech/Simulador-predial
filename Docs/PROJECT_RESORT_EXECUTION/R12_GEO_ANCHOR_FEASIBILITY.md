# Project Resort — viabilidade preliminar dos terrenos do gameplay em Copacabana

**Data:** 2026-10-09
**Branch isolada:** codex/r12-gameplay-visual-bridge, repo Simulador-predial
**Status:** auditoria planar GIS, **NENHUMA posição aprovada para gameplay**.

## O que foi efetivamente calculado
A ferramenta nova Tools/Bridge/analyze_r12_geo_anchor_feasibility.py analisou a posição e os tamanhos originais dos oito terrenos do gameplay (P0–P7), sem alterar o arquivo ResortSite.json, nenhum save, prefab ou executável. Usou o snapshot frozen OSM da R13 commit 5217a65 (geo/data/copacabana.osm.gz), transformação UTM EPSG:32723/46 graus, 1.468 footprints poligonais de edifícios e 3.895 segmentos de ruas geográficas (extraídos de 641 vias OSM).

Para cada lote, gerou retângulos candidatos exatamente com a largura/profundidade herdadas, num grid de centros a cada 25m, rejeitando quando:
- não coubessem em 2.000 x 1.000m;
- invadissem o polígono de qualquer edifício OSM, com margem de 1,25m;
- cruzassem ruas OSM (largura cartográfica quando marcada, ou largura conservadora por tipo de via) + margem de 1,5m;
- se aproximassem da linha de costa real a menos de 55m;
- se sobrepusessem a outros terrenos candidatos, com buffer de 4m.

A implementação usa Liang–Barsky para segmentos e retângulos e point-in-polygon para checar pegadas de edifícios, com hashes SHA256 dos dados originais e relatório determinístico. Os testes do algoritmo tratam travessias, tangências e polígonos.

## Resultado do teste de viabilidade — NÃO são locais oficiais
| Terreno | Dimensão herdada | Resultado no grid 25m |
|---|---|---|
| P0, ponto da barraca | 6 x 12m | candidato planar |
| P1, faixa do quiosque | 28 x 24m | candidato planar |
| P2, sobrado | 40 x 40m | candidato planar |
| P3, quarteirão | 70 x 60m | candidato planar |
| P4, hotel | 90 x 80m | candidato planar |
| P5, platô | **240 x 190m** | **ZERO candidatos livres** |
| P6, ponta | 110 x 100m | candidato planar |
| P7, marina | 100 x 40m | candidato planar |

O algoritmo encontrou **7/8 retângulos potenciais**. P5 não tem candidato nessa resolução e sob essas premissas, mesmo antes de reservar outros lotes. Isso **não prova impossibilidade global**, mas indica que o P5 não deve ser migrado simplesmente para um lote fictício de 45.600m² dentro de bairro densamente edificado. Para manter o mapa 2km x 1km e edifícios GIS, será necessário **reprojetar a missão/parcelamento ou decidir explícita adaptação de escopo**; não apagar prédios reais para acomodá-lo automaticamente.

## Limites críticos ainda pendentes
1. As coordenadas x,y geradas são **apenas CANDIDATAS DE PLANIMETRIA**, não têm altitude, collider, navegação, propriedade/uso real, reserva ou acessibilidade comprovados.
2. OSM descreve ruas/footprints; calçadas/terrenos reais com declive, faixas livres, entrada e ocupação atual exigem outra validação.
3. A posição HOME_DOOR exige uma **entrada real verificável** ou design ficcional declarado; a posição STALL_PROMENADE deve estar em passeio transitável com fluxo do jogador. Nenhuma das duas foi definida como alvo.
4. P7 se chama Marina no jogo legado; **não implica** marina real existente na zona R12. A função narrativa de P7 deverá ser adaptada sem inventar infraestrutura factual.
5. O script NÃO preenche o campo target em R12GameplayAnchorInventory.json; R12GameplayWorldGate continua retornando false até integração, QA Unity, física, PlayerController, missões, NPCs e saves.

## Entregas de QA
- Relatório com 8 lotes, candidaturas, score, motivos de rejeição e SHA dos snapshots: Docs/PROJECT_RESORT_EXECUTION/R12_GEO_ANCHOR_FEASIBILITY.json.
- Testes do script, dos retângulos e da segurança contra migração automática: Tools/Bridge/test_r12_geo_anchor_feasibility.py.
- GitHub Actions cruza **a mesma revisão congelada dos dados OSM** por checkout esparso em frozen-visual, reproduz o relatório byte a byte com --check e executa os testes antigos. Não exige PC permanentemente.
- Unity 6000.6.2f1 validou anteriormente a preservação de gameplay e a tabela de âncoras, mas **não testou essas sete candidaturas em 3D ainda**.

## Próxima implementação na frente gameplay
Projetar a equivalência narrativa de P5 sem remover o contexto geográfico; realizar validação de terreno/colliders real para sete lotes; localizar porta da casa e quiosque no mapa R12/R14; validar navegação e economia/saves antes da ativação. Nenhum merge deve ocorrer até o funcionamento de verdade e um build Windows jogável independente.
