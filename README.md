# Facility Ops — protótipo de manutenção predial

Projeto iniciado a partir de `Building_Maintenance_Simulator_Planning_v1.zip`, preservado integralmente em `Docs/Building_Maintenance_Simulator_Planning_v1/`.

Engine escolhida pelo usuário: **Unity 6000.6.2f1**, já instalada. C#, URP, novo Input System, **primeira pessoa** e single-player. Campanha em Santa Aurora, codinome **PROJECT FACILITY**, sem publicação Steam nesta etapa. `Docs/DECISOES_ATUAIS.md` registra as decisões mais recentes.

## Abrir e jogar

- Build Windows: `Builds/Windows/FacilityOps.exe`. Também pode executar `Jogar.ps1`.
- Editor: Unity Hub → Projects → Add project from disk → selecionar **FacilityOps** dentro desta pasta. Abrir `Assets/_Game/Scenes/Bootstrap.unity` e pressionar Play.
- Compilar novamente: `Tools/Build.ps1` ou menu **Facility Ops / Preparar e compilar Windows** no editor.
- Repetir verificação do executável: `Tools/Test-Windows.ps1`.

## Primeiro serviço

Confira o estoque no tablet e aceite **PRÓLOGO / O primeiro chamado**. Helena relata falta de energia no Horizonte e Guto orienta a investigação. A causa autoral é o isolamento danificado de uma luminária antiga: religar o disjuntor sem reparar acende as luzes por alguns segundos, mas a falha reaparece ao aquecer.

1. Caminhe até QD-01, CT-01 e LM-01.
2. Inspecione e compare energia de entrada/saída e passagem de sinal. Registre pelo menos duas medições.
3. Abra o tablet e registre a hipótese **Isolamento da luminária** após inspecionar LM-01.
4. Use **[6] + E no QD-01** para isolar e **[5] + E na LM-01** para confirmar. A troca fica bloqueada sem essas duas ações.
5. Use **[4] + E na LM-01** para substituir o módulo. O circuito permanece isolado.
6. Use **[7] + E no QD-01** para restaurar, aguarde cinco segundos em campo e faça **[5] + E no QD-01** para validar estabilidade. O tablet pausa o ensaio.
7. Entregue pelo tablet. Pagamento, conclusão e mensagens de Guto/Helena são salvos. A aba **MENSAGENS** guarda o diário.

Após o prólogo, o botão principal oferece três serviços autorais do Capítulo I, em sequência: tomada de apartamento, iluminação da mercearia e torneira do restaurante. Cada chamado viaja para seu local no catálogo. Nos três, registre a hipótese, isole na origem [6], confirme no componente [5], troque [4], restaure [7] e espere três segundos antes do teste final [5] na origem. O serviço hidráulico mede pressão/vazão virtuais e usa kit de vedação separado.

Os chamados livres continuam disponíveis pelo botão secundário, com três causas variáveis e ferramentas 1–5. Eles não concluem serviços autorais. Após os três serviços iniciais e reputação **25**, Helena registra a indicação ao primeiro contrato recorrente. O primeiro contrato preventivo de bomba no condomínio já foi integrado ao código, com diagnóstico, isolamento, kit próprio, validação de estabilidade e histórico persistente; **os commits recentes ainda precisam ser revalidados no runtime da Unity**. Detalhes em `Docs/PROLOGO_IMPLEMENTADO.md`, `Docs/CAPITULO_I_IMPLEMENTADO.md` e `CLAUDE.md`.

## Progressão, liberdade de trabalho e vida pessoal

O planejamento oficial de carreira semiaberta, escolha de trabalhos/regiões, dificuldade recuperável, ferramentas, veículos, moradias, móveis, patrimônio e lazer está em `Docs/GDD_PROGRESSAO_VIDA_LIBERDADE_ECONOMIA.md`.

Regras centrais planejadas:
- o jogador escolhe entre campanha e trabalhos livres disponíveis;
- o começo oferece poucas opções e a liberdade cresce com reputação, ferramentas, dinheiro e transporte;
- o dinheiro pode ser investido na empresa ou na vida pessoal;
- a moradia evolui de kitnet para apartamentos/casas maiores, sem caminho obrigatório;
- lazer e conforto existem como gastos opcionais;
- o jogo deve ser difícil, mas sempre possuir uma rota econômica de recuperação.

A direção visual futura do mapa, casas, estruturas e interiores usa VEIN apenas como referência de atmosfera/materialidade, mantendo Santa Aurora, layouts e assets originais.

## Estrutura da campanha / visitar mapas

No tablet, abra **CIDADE**, escolha um distrito e um local, e clique em **Visitar / nível**. A prévia permite caminhar pelos setores e ler registros, sem avançar a campanha ou alterar recompensas. Para trocar de pavimento, use a mesma aba; **Voltar à garagem** retorna ao hub.

São **6 distritos, 24 locais, 182 setores, 30 pavimentos e 15 etapas** (prólogo + capítulos I–XIV). A documentação detalhada das plantas, sistemas e acontecimentos está em `Docs/MAPA_CAMPANHA.md`; a lore original está preservada em `Docs/LORE_CAMPANHA_ORIGINAL.md`.

O catálogo mantém garagem original, Edifício Horizonte, Teatro Imperial, escola, hotéis, hospitais, fábrica, data center, Vértice e Santa Aurora Central. Plantas são estruturas de protótipo com portas físicas e ligações verticais por tablet. Escadas/elevadores físicos, eventos e missões dos capítulos ainda serão implementados.

| Controle | Ação |
|---|---|
| WASD / mouse | Andar / olhar |
| Shift | Andar mais rápido |
| E | Interagir com o objeto em foco |
| 1 | Inspeção visual |
| 2 | Scanner de energia fictícia |
| 3 | Sonda de sinal fictícia |
| 4 | Kit de reparo |
| 5 | Teste integrado |
| 6 | Isolar na origem do sistema, nos serviços autorais |
| 7 | Restaurar na origem do sistema, nos serviços autorais |
| Tab / Esc | Abrir ou fechar tablet |

## Save e economia

Save v1 em `%USERPROFILE%/AppData/LocalLow/OficinaAurora/Facility Ops Prototype/career-v1.json`, com backup `.bak`. Salva missão ativa, evidências, reparo, dinheiro, XP, reputação, peças, dívida, conclusão do prólogo e diário. No prólogo também conserva isolamento, confirmação e ensaio térmico. Um marcador explícito distingue ausência de chamado de uma instância vazia criada pela serialização inline da Unity. Campos antigos são preservados na leitura de v1. Autosave nas ações e a cada 30 segundos. Um save ilegível sem backup é preservado e bloqueia sobrescrita, mostrando aviso.

Peças elétricas custam R$ 60 e kits hidráulicos R$ 50. É possível voltar à sede durante uma visita, preservando o estado isolado do chamado. Se faltar saldo, o fornecedor oferece crédito e desconta a dívida nos pagamentos, evitando que uma carreira fique presa por falta de peças. Essa regra é uma adaptação de protótipo e precisa de balanceamento. O save também guarda a lista de serviços do capítulo, estoque hidráulico, indicação do contrato e histórico por prédio. Na prévia de um local atendido, use E na placa **MANUTENÇÃO REGISTRADA** para ler o resultado anterior.

O teste automático usa `Builds/Windows/QA/smoke-career.json`, separado do progresso do jogador.

## Fluxo de arte

- Fontes editáveis: `ArtSource/Blender/Aurora_TechnicalKit.blend`, `Aurora_Corridor.blend` e `SantaAurora_Masterplan.blend`.
- Geração reproduzível: `Tools/Blender/create_technical_kit.py`.
- Exportações FBX e textura: `FacilityOps/Assets/_Game/Resources/Art/`.
- Catálogo/origem: `ArtSource/Blender/catalog.json`.
- Verificação de reabertura, UVs e textura incorporada: `ArtSource/Blender/verification.json`.

Geometria e textura foram criadas para este projeto. O kit técnico e a arquitetura inicial do corredor foram modelados no Blender; a sede, personagem e os demais interiores permanecem blocos provisórios. `SantaAurora_Masterplan.blend` é um estudo de implantação dos 24 locais, não um mundo aberto final. Materiais são preparados para URP na execução. Isso ainda não representa a qualidade visual final de um produto premium.

## Arquitetura e limites

`FacilityOps.Core` contém rede elétrica abstrata, máquina de estados do serviço, economia, inventário e save. `FacilityOps.Runtime` contém movimento, raycast, interação, cenário e tablet. `FacilityOps.Editor` prepara a cena e executa verificações de regras antes de gerar o build.

Para regenerar o catálogo e as plantas: `node Tools/Map/generate_campaign.mjs CAMINHO_DA_RAIZ`. O gerador verifica referências de capítulos e conectividade de cada pavimento. `CLAUDE.md` contém o handoff técnico para colaboração no GitHub.

Os ScriptableObjects de conteúdo são a base para a próxima etapa; o chamado inicial ainda é definido no código. Interface do tablet é provisória em IMGUI e deverá migrar para UI Toolkit/uGUI antes do vertical slice. A cena Bootstrap monta os ambientes em runtime; a próxima etapa deve converter a área artística aprovada em prefabs editáveis no editor.

Ainda pendentes: validação Unity dos commits recentes do contrato preventivo, animações táteis de desmontagem, ferramentas visíveis nas mãos, áudio elaborado, acabamento arquitetônico autoral, mercado livre de 3–5 chamados/regiões, lar inicial detalhado e comprável, veículos, patrimônio, lazer, climatização, expansão da lista de chamados, upgrades, funcionários, localização completa, configurações/remapeamento, testes de desempenho e integração Steam.

Os resultados confirmados de validação ficam em `Docs/STATUS_IMPLEMENTACAO.md` e nos logs da execução.
