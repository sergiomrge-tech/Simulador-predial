# Fase 02 — continuação Codex de 2026-10-07

Branch inicial: `claude/w1-masterplan`; HEAD inicial `3935f19`.
Objetivo: corrigir e validar o passe visual/assets, mantendo a Fase 03 bloqueada.

## Preservação

O estado inicial tinha 43 capturas locais modificadas, `KioskDecor.cs`, quatro arquivos de testes e a automação/evidência Codex ainda não commitada. Nenhum reset, checkout, clean, revert ou exclusão foi feito. O runner desta continuação usa diretórios próprios em `D:\ProjectResort_Autonomy\Evidence\CODEX_F02_20261007_Continuation`.

**Incidente de preservação:** a suíte completa revelou três testes antigos (`StagesTests`, `PousadaInteriorTests`, `PrologueDayTests`) que ignoravam `RESORT_TEST_CAPTURE_ROOT` e gravavam em Reviews. Quinze capturas R2/R4 foram regeneradas. As quatro ocorrências foram corrigidas para respeitar a pasta de evidências. Comparação com `CODEX_REVIEWS_HASHES_2026-10-07.json` detectou 15 hashes diferentes; não foi encontrada cópia com os hashes originais nas evidências ou no Desktop. Esses PNGs não devem ser incluídos no commit como se fossem alterações intencionais desta continuação. Não alegar preservação integral dos PNGs anteriores; o código e demais trabalhos foram mantidos.

Outra continuação Codex (`codex_20261007_0852_run4`) estava ativa no mesmo working tree. Suas mudanças também foram preservadas. Tentativas de abrir Unity enquanto esse processo tinha o projeto aberto saíram com código 1 e sem XML: isso não é resultado de teste. Uma tentativa intermediária encontrou chamadas a `RealisticKioskAssets` antes da criação desse arquivo; foi registrada como falha de compilação, sem declarar PASS.

## Mudanças desta continuação

- Limites dos nadadores explicitados e ordenados com `Min/Max`, mantendo os mesmos extremos físicos e tolerância de 1 cm. A expressão já estava ordenada no estado encontrado; o resultado antigo de 13/14 não descrevia a árvore atual.
- Contornos e legendas de parcelas desativados desde a criação; exibidos somente com painel de compra ou `PlacementSystem.IsActive`, mantendo proximidade e sinais físicos interativos. Teste de regressão cobre abrir/fechar o painel perto do terreno.
- Nome do quiosque fixado em uma testeira física, com texto proporcional; aviso de vagas fixado ao quadro; indicação de abertura reduzida à distância de interação.
- `BEACH_WATER_DZ` de 114 para 138 no exportador existente. Regenerados JSON e os dois heightfields com `Tools/Map/export_resort_site.py`; calçadão, rua, lotes e sistemas permanecem na mesma implantação. A água deve ficar aproximadamente 31 m do quiosque, em vez de aproximadamente 55 m.
- Primeiros 12 grupos de praia distribuídos em faixa menor perto do quiosque; primeiros grupos de passeio também mais próximos. Quantidade de spots/população, pooling, orçamento de humanos animados e regras de exclusão do quiosque preservados.
- Mapa de AO/smoothness dos materiais autorais preparado pelo exportador existente `export_resort_kit.py --surface-maps-only`, sem reexportar FBX de estágios. Máscara linear: R=0, G=AO, A=1-roughness. Madeira mantém o trabalho de UV métrico anterior; plástico e superfícies usam mapas compartilhados.
- Bairro existente recebeu reboco/telha/madeira PBR, UV métrico, caixilhos, peitoris, panes e portas em meshes combinados. Nenhum lote, interior ou fase futura foi acrescentado. Fachadas ainda não são arte final.
- Scan CC0 `Aerial Beach 01` aplicado em uma superfície acompanhando o heightfield, sem collider novo; normal DirectX convertido para Y+. Fonte e licença preservadas na biblioteca e em `sand_LICENSE.txt`.
- Correção de integração: o metal da cobertura não escala UV métrico uma segunda vez. Teste de madeira ignora filtros sem renderer deixados pela substituição de móveis e continua exigindo ocultação de toda madeira de estágio 1.

## Assets presentes no conjunto integrado

| Asset | Origem e uso | Limite |
|---|---|---|
| Madeira, plástico, reboco, telha, galvanizado | `ArtSource/Textures`, autorais/propriedade do projeto | Incremento PBR; não torna toda geometria final |
| Aerial Beach 01 | Poly Haven, CC0, `D:\ProjectResort_AssetLibrary\PolyHaven_CC0\AerialBeach01_2K` | Normal convertido; textura importada com mipmaps |
| Outdoor Table Chair Set 01 | Poly Haven, CC0; integração da continuação concorrente | Três conjuntos compartilhados, LOD/culling; collider e seats preservados |
| Pedra portuguesa | Mapas autorais; calçadão integrado pela continuação concorrente | Superfície visual, collider original |
| Human Basic Motions FREE | Já integrado em `ThirdParty/Resources/HBM` | Somente animação; manequins ainda provisórios |

A pasta `UnityFree/Realistic_PBR_Whitelist` continha apenas `WHITELIST.txt`: nenhum dos pacotes Unity realistas enumerados estava baixado. Nenhum pacote de monstro/mago/fantasia ou low-poly foi importado. A recomendação antiga de Low Poly Tropical Beach no audit de assets foi revogada pelas instruções atuais do Diretor.

## Validação real

| Execução | Resultado | Evidência |
|---|---|---|
| LivingWorld, baseline, Unity com gráficos | 10/10 PASS | `Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/logs/unity_PlayMode_20261007_085219.xml` |
| ResortAurora.Tests, baseline, Unity com gráficos | 21/21 PASS | mesmo diretório, `unity_PlayMode_20261007_085356.xml` |
| Primeiro bloco visual, LivingWorld com gráficos | 11/11 PASS | `CODEX_F02_20261007_Continuation/VisualBlock1/logs/unity_PlayMode_20261007_085813.xml` |
| Integração de móveis intermediária | 10/11; exceção no teste de madeira corrigida | `CODEX_Visual_20261007_0900/logs/unity_PlayMode_20261007_090117.xml` |
| Teste de móveis intermediário | 1/2; busca do LOD no objeto errado corrigida pela outra continuação | `CODEX_Visual_20261007_0904/logs/unity_PlayMode_20261007_090340.xml` |
| Conjunto com scan de areia | 23/24; último teste ainda compilado antes da correção de busca de LOD em objetos inativos | `CODEX_F02_20261007_Continuation/FinalScanFull/logs/unity_PlayMode_20261007_090419.xml` |
| Teste de móveis corrigido | 2/2 PASS | `CODEX_F02_20261007_Continuation/FurnitureCorrection/logs/unity_PlayMode_20261007_090657.xml` |
| Revalidação completa | **24/24 PASS, Unity exit 0, nenhum skip** | `CODEX_F02_20261007_Continuation/FinalVerified/logs/unity_PlayMode_20261007_090858.xml` |

O primeiro bloco mediu render da câmera da praia: média 3,0 ms, p95 3,5 ms, pior 3,8 ms, 85 pessoas, 18 lâmpadas cadastradas. É medição de render em lote com readback mínimo, não FPS de gameplay interativo. Baseline tinha outro seed/clima/população; não constitui comparação controlada de desempenho.

Capturas reais do primeiro bloco foram inspecionadas: vista das mesas sem linhas vermelhas ou texto técnico grande; mar visivelmente mais próximo. Noite capturada já apresentava céu azul-marinho e iluminação comercial quente. Nenhuma screenshot foi criada fora da execução Unity.

## Gate e pendências

Fase 02 permanece em revisão visual e `HUMAN_GATE_PENDING`; Fase 03 não liberada. Pessoas/manequins, guarda-sóis, equipamentos do balcão e parte da arquitetura ainda têm geometria provisória. Falta personagem realista aprovado, acabamento de móveis/equipamentos restantes, transição de areia molhada e revisão humana de dois dias jogáveis/áudio/ritmo. A aquisição de um pacote não substitui validação de estilo, licença, URP, escala e custo.

## Resultado final

Suíte completa `ResortAurora.Tests -Graphics`: **24/24 PASS**, 0 falhas, 0 skips. Nenhum `error CS` ou `Shader error` encontrado no log final. LivingWorld no conjunto inclui o novo teste de modo de parcelas, e RealisticFurniture cobre escala, mapas, LOD, upgrade e troca de estágio.

Render em lote final da praia: média **3,3 ms**, p95 **3,8 ms**, pior **4,5 ms**, 44 pessoas naquele cenário/clima. Estágio 1: aérea 3,0 ms e chão 2,9 ms. Os testes de regressão dos estágios já existentes também passaram; isso não autoriza criar conteúdo de fases posteriores. Continua sem medição de FPS interativo.

Capturas finais reais em `D:\ProjectResort_Autonomy\Evidence\CODEX_F02_20261007_Continuation\FinalVerified\captures`. A versão `FinalScanFull` já foi inspecionada no enquadramento das mesas, do calçadão/quiosque e da noite: mesa/cadeiras substituídas, areia com scan, contornos ausentes, nome em testeira, céu navy e luz quente. As capturas `RealisticFurniture/tables_day.png` e `tables_night.png` dão o enquadramento próximo. Repetição da areia e transições de margem precisam de polimento; manequins ainda impedem PASS visual final.

Os arquivos `source-hashes.json` e o XML/log final ficam com a execução. A automação existente recebeu mutex e espera por execuções Unity anteriores, evitando disputar o lock do projeto. Os testes legados R2/R4 agora respeitam `RESORT_TEST_CAPTURE_ROOT`.

Commit deve abranger somente código, ferramentas, assets licenciados e notas deste passe; nenhum PNG pré-existente de Reviews, pacote bruto Unity ou pasta temporária será incluído. Trabalho anterior de madeira PBR e redirecionamento de testes foi mantido e integrado ao mesmo bloco visual. O gate humano e visual permanece aberto.
