# HANDOFF CLAUDE — PROJECT RESORT
## Próxima execução oficial

Leia primeiro, nesta ordem:

1. `CLAUDE.md`
2. `Docs/GDD_PROJECT_RESORT_MASTER.md`
3. `Docs/STATUS_IMPLEMENTACAO.md`
4. `Docs/W3_2X_URBAN_PATCH.md` se existir nesta branch ou em branch integrada
5. `Docs/PLANO_MESTRE_MUNDO_SANTA_AURORA.md`
6. `Docs/WORLD_BIBLE_SANTA_AURORA_V1.md`
7. `Docs/ART_BIBLE_REALISMO_SANTA_AURORA.md`

## CONTEXTO

O projeto mudou oficialmente de simulador de manutenção predial para **PROJECT RESORT**.

A fantasia central agora é:

```
pequeno quiosque de praia
→ quiosque profissional
→ pousada
→ pequeno hotel
→ hotel completo
→ resort
→ resort de luxo
→ resort cinco estrelas monumental
```

A base técnica do Facility Ops deve ser reaproveitada sempre que fizer sentido.

O antigo sistema de manutenção deixa de ser o loop principal e passa a ser um subsistema futuro do resort.

## REGRA CRÍTICA

NÃO comece apagando ou reescrevendo a base.

Antes de implementar qualquer coisa, faça uma auditoria real do estado do repositório e da máquina local.

### ETAPA 0 — AUDITORIA OBRIGATÓRIA

Verifique:

- branch local atual;
- HEAD atual;
- arquivos modificados não commitados;
- arquivos não rastreados;
- stash;
- branches locais;
- branches remotas;
- commits mais recentes;
- cenas Unity existentes;
- estado da cena Bootstrap;
- sistemas já criados para resort;
- qualquer asset, script, prefab, cena, documento ou protótipo relacionado a:
  - resort;
  - hotel;
  - pousada;
  - praia;
  - quiosque;
  - hóspedes;
  - estoque;
  - funcionários;
  - construção;
  - terrenos;
  - fornecedores.

Não sobrescreva trabalho local não commitado.

Se já houver conversão para resort localmente, continue dali.

## BASE TÉCNICA MAIS VALIOSA A PRESERVAR

Preservar, adaptar ou migrar quando tecnicamente viável:

- Unity 6000.6.2f1;
- URP;
- primeira pessoa;
- FirstPersonController;
- câmera;
- CharacterController;
- raycast/interação;
- portas;
- colisões;
- save versionado;
- autosave/backup;
- Santa Aurora;
- streaming por células;
- relevo;
- vias;
- calçadas;
- vegetação;
- edifícios urbanos;
- veículos;
- casa do jogador;
- sistema de interação;
- elétrica;
- hidráulica;
- bombas;
- manutenção;
- ferramentas Blender;
- pipeline Blender → Unity;
- validadores;
- gates de build;
- testes de navegação;
- métricas de performance;
- screenshots reais de runtime.

Não remover sistemas antigos apenas por não serem mais centrais. Isole-os para reaproveitamento futuro.

## REFERÊNCIA TÉCNICA JÁ VALIDADA

Na linha mais avançada de integração Unity já houve validação de:

- corredor jogável em primeira pessoa;
- terreno texturizado;
- ruas conectadas;
- carros assentados no relevo;
- entradas de prédios;
- NavMesh;
- caminhada contínua real;
- build Windows;
- save/load;
- captura real do Player;
- streaming de células.

Antes de descartar qualquer implementação existente, compare com as branches:
- `gpt/unity-world-integration`
- `codex/unity-world-integration-validation`
- `codex/vertical-slice-qa`

A branch `main` está desatualizada e NÃO deve ser usada como referência principal de progresso.

## DECISÃO DE PRODUÇÃO

O primeiro conteúdo novo do PROJECT RESORT será um vertical slice pequeno, completo e jogável.

### FASE ATUAL: QUIOSQUE VERTICAL SLICE

Objetivo: o jogador conseguir viver pelo menos um dia completo de trabalho.

Fluxo mínimo:

```
acordar em casa
→ ir até a praia
→ abrir o quiosque
→ conferir estoque
→ receber clientes
→ vender bebidas/lanches
→ receber pagamentos
→ repor/organizar produtos
→ fechar o caixa
→ fechar o quiosque
→ voltar para casa
→ dormir
→ salvar
```

## ETAPA 1 — FUNDAÇÃO PROJECT RESORT

Criar/adaptar namespaces e estrutura sem quebrar o código legado.

Estrutura sugerida:

```
Resort.Core
Resort.Economy
Resort.Inventory
Resort.Business
Resort.Guests
Resort.Staff
Resort.World
Resort.Player
Resort.UI
Resort.Save
Resort.Maintenance
```

Não é necessário mover todo o código antigo imediatamente.

Criar uma camada de compatibilidade e migrar por etapas.

## ETAPA 2 — ÁREA INICIAL DE PRAIA

Criar/adaptar um pequeno trecho costeiro de Santa Aurora.

Precisa conter:

- praia;
- calçadão;
- acesso viário;
- espaço inicial do jogador;
- quiosque;
- ponto de entrega;
- área mínima para clientes;
- ligação física com a casa/rota do jogador.

Nesta fase NÃO construir o resort completo.

O foco é uma área pequena e polida.

## ETAPA 3 — QUIOSQUE

Criar o primeiro empreendimento funcional.

Elementos mínimos:

- balcão;
- caixa;
- geladeira;
- freezer pequeno;
- prateleiras;
- chapa ou preparo simples;
- lixeira;
- pequeno estoque.

Criar IDs estáveis para todos os objetos persistentes.

## ETAPA 4 — PRODUTOS E ESTOQUE

Começar com poucos produtos.

Exemplo:

- água;
- refrigerante;
- suco;
- cerveja;
- sanduíche simples;
- salgado/porção simples.

Cada produto deve ter definição data-driven com:

- ID;
- nome;
- categoria;
- custo;
- preço base;
- estoque;
- volume;
- validade futura opcional.

Criar inventário persistente.

## ETAPA 5 — CLIENTES

Criar cliente simples, sem IA complexa.

Fluxo:

1. chegar;
2. entrar na fila;
3. escolher produto;
4. pedir;
5. aguardar;
6. pagar;
7. consumir/sair.

Estados básicos devem ser claros e debuggáveis.

Não criar dezenas de perfis ainda.

Começar com 1–3 perfis simples.

## ETAPA 6 — VENDA

Criar sistema de transação.

Venda deve:

- conferir estoque;
- remover item;
- receber dinheiro;
- registrar receita;
- atualizar caixa;
- atualizar estatísticas;
- persistir no save.

Não permitir dinheiro duplicado.

## ETAPA 7 — CAIXA DIÁRIO

Criar abertura e fechamento do dia.

Registrar:

- saldo inicial;
- receita;
- custo estimado;
- quantidade vendida;
- lucro bruto;
- perdas;
- saldo final.

Exibir resumo simples ao fechar.

## ETAPA 8 — ROTINA CASA → TRABALHO → CASA

Reaproveitar a casa existente quando viável.

Implementar:

- acordar;
- horário;
- deslocamento;
- abertura do quiosque;
- fechamento;
- retorno;
- dormir;
- avançar dia.

Não transformar isso em life sim complexo.

## ETAPA 9 — FORNECEDOR MÍNIMO

Criar fornecedor simples para o vertical slice.

Primeiro nível pode ser:

- pedido pelo celular/tablet;
- entrega em ponto específico;
- caixas físicas opcionais;
- reposição manual ou simplificada.

Persistir pedidos e custo.

## ETAPA 10 — REPUTAÇÃO INICIAL

Criar reputação simples.

Aumenta com:

- vendas;
- atendimento;
- produtos disponíveis;
- poucos erros.

Diminui com:

- falta de estoque;
- demora;
- cliente não atendido.

Nesta fase, reputação ainda não precisa liberar hotel.

## ETAPA 11 — PRIMEIRO FUNCIONÁRIO

Somente depois do quiosque manual estar estável.

Adicionar um funcionário básico.

Exemplo: atendente.

Ele deve ser capaz de:

- assumir caixa ou atendimento;
- ter salário;
- ter horário;
- ser contratado/demitido;
- persistir no save.

## ETAPA 12 — PRIMEIRA EXPANSÃO DE TERRENO

Somente depois de economia e funcionário estarem funcionando.

Criar:

- lote inicial;
- lote adjacente;
- preço de compra;
- requisito de reputação/dinheiro;
- limite visível;
- persistência de propriedade.

A compra deve alterar fisicamente a área disponível.

## ETAPA 13 — GANCHO PARA POUSADA

Não construir a pousada nesta entrega.

Apenas preparar o sistema para a próxima fase:

- lote suficiente;
- categoria de construção;
- primeiro blueprint/placeholder de recepção/quarto;
- requisito econômico.

## DATA-DRIVEN

Conteúdo novo deve preferencialmente usar ScriptableObjects ou dados equivalentes:

- ProductDefinition
- EmployeeRoleDefinition
- GuestProfileDefinition
- BuildItemDefinition
- SupplierDefinition
- UpgradeDefinition

Evitar hardcode de conteúdo.

## SAVE

Criar evolução de save sem quebrar saves antigos.

O novo save precisa começar a armazenar:

- dia;
- hora;
- dinheiro;
- caixa;
- estoque;
- vendas;
- reputação;
- estado do quiosque;
- terrenos;
- funcionário futuro;
- localização do jogador quando apropriado.

Manter:
- versionamento;
- backup;
- migração;
- proteção contra corrupção.

## VISUAL

Blockout é aceitável durante implementação.

Mas:

- não tratar blockout como arte final;
- não usar low-poly genérico como direção final;
- manter proporção realista;
- manter coerência com Santa Aurora;
- usar materiais PBR quando entrar em polimento;
- não copiar assets ou layouts externos.

## PERFORMANCE

Não comprometer a base já validada.

Medir pelo menos:

- FPS médio;
- pior frame;
- memória;
- GC;
- quantidade de NPCs ativos.

Clientes fora da área imediata podem futuramente usar simulação simplificada.

## GATE DO VERTICAL SLICE

O quiosque só pode ser marcado como concluído quando for possível:

1. abrir build/editor;
2. acordar em casa;
3. chegar à praia;
4. abrir o quiosque;
5. vender pelo menos três categorias de produto;
6. consumir estoque corretamente;
7. receber dinheiro corretamente;
8. fechar caixa;
9. fechar o dia;
10. voltar para casa;
11. dormir;
12. recarregar o save;
13. confirmar que dinheiro, estoque, reputação e dia persistiram;
14. repetir o ciclo sem erro;
15. validar que não há duplicação de dinheiro/estoque;
16. registrar capturas reais da Unity;
17. registrar relatório curto de QA.

## NÃO FAZER AGORA

Não implementar ainda:

- resort cinco estrelas;
- piscina gigante;
- spa completo;
- suíte presidencial;
- centro de convenções;
- dezenas de quartos;
- centenas de hóspedes;
- multiplayer;
- campanha longa;
- sistema completo de estrelas;
- IA complexa;
- sistema completo de construção de hotel.

Esses itens pertencem às fases futuras.

## ENTREGA ESPERADA DO CLAUDE

Ao terminar esta rodada, entregar:

1. relatório da auditoria inicial;
2. branch usada;
3. commit inicial e commit final;
4. lista exata do que já existia para resort;
5. lista do que foi reaproveitado;
6. lista do que foi criado;
7. vertical slice do quiosque funcionando ou, se não couber em uma única rodada, o maior recorte jogável estável possível;
8. testes executados;
9. erros/limites restantes;
10. screenshots reais;
11. próximos 3 passos objetivos;
12. tudo commitado no GitHub.

## REGRA DE AUTONOMIA

Não interromper para pedir decisões pequenas.

Quando houver várias soluções tecnicamente válidas:

- escolher a mais simples;
- preservar compatibilidade;
- evitar retrabalho;
- favorecer sistemas modulares;
- priorizar o loop jogável.

Só parar se houver risco real de perda de trabalho, destruição de dados, necessidade de credencial ou decisão de design que altere substancialmente o conceito central.

## REGRA FINAL

O objetivo desta rodada NÃO é construir o resort inteiro.

É transformar a base existente em um **primeiro dia de PROJECT RESORT que já seja um jogo**.

O jogador precisa sentir, desde a primeira versão:

> “Estou começando pequeno, mas isso pode virar um resort gigantesco.”
