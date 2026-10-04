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
