# FASE 02 — VERTICAL SLICE DO QUIOSQUE

## Objetivo

Transformar PROJECT RESORT em um jogo já reconhecível.

## Loop obrigatório

casa → praia → abrir quiosque → conferir estoque → atender → vender → receber → fechar caixa → fechar quiosque → voltar para casa → dormir → próximo dia.

## Sistemas mínimos

- pequena área costeira;
- quiosque funcional;
- balcão;
- caixa;
- geladeira/freezer;
- prateleiras;
- estoque;
- produtos data-driven;
- 1–3 perfis simples de cliente;
- fila;
- pedido;
- pagamento;
- dinheiro;
- caixa diário;
- reputação inicial;
- relógio/dia;
- casa e dormir;
- save/load.

## Produtos mínimos

- água;
- refrigerante;
- suco;
- cerveja;
- lanche simples;
- salgado/porção.

## Gate

O jogador deve completar dois dias consecutivos sem erro e recarregar o save mantendo dinheiro, estoque, reputação e dia corretos.

Não avançar para funcionários antes de o quiosque manual ser divertido e estável.


## Referência visual obrigatória

Antes de modelar ou alterar a praia/quiosque, ler:

`Docs/VISUAL_REFERENCES/PROJECT_RESORT_VISUAL_REFERENCES.md`

Usar REF 01 para identidade/ambiente e REF 02 para layout operacional. Não antecipar a arquitetura da REF 03.


## REQUISITO OBRIGATÓRIO — PRAIA VIVA E REALISTA

A Fase 02 NÃO pode ser considerada visualmente aprovada com praia, calçadão ou entorno vazios.

O jogador precisa perceber Santa Aurora como um lugar vivo.

### NPCs mínimos na área inicial

Implementar população ambiente com variação visual e comportamental:

- pessoas caminhando pelo calçadão;
- casais passeando;
- famílias com crianças;
- grupos de amigos;
- banhistas na areia;
- pessoas sentadas em cadeiras/toalhas;
- pessoas tomando sol;
- pessoas entrando e saindo do mar quando tecnicamente viável;
- corredores/caminhantes;
- ciclistas ocasionais quando houver espaço apropriado;
- clientes do quiosque;
- pessoas consumindo em mesas;
- funcionários/entregadores quando o sistema correspondente existir.

### Comportamentos

Evitar NPCs parados repetidamente em poses idênticas.

Usar combinações de:
- caminhar;
- conversar;
- sentar;
- levantar;
- observar o mar;
- usar celular;
- beber/comer;
- brincar;
- descansar;
- aproximar-se do quiosque;
- formar fila;
- comprar;
- sair;
- ocupar mesas;
- circular pelo calçadão.

Não é necessário simular cada pessoa com IA completa. NPCs ambientais podem usar comportamento simplificado.

### Densidade dinâmica

A densidade deve variar por:
- horário;
- dia;
- clima;
- demanda futura;
- eventos futuros.

Exemplo:
- manhã: corredores, moradores, poucos turistas;
- meio-dia/tarde: praia e quiosque mais cheios;
- fim de tarde: passeio e consumo;
- noite: movimento reduzido inicialmente, crescendo conforme o empreendimento evoluir.

### Qualidade visual

NPCs devem:
- ter escala humana correta;
- não atravessar objetos;
- não ficar flutuando;
- não afundar no solo;
- evitar clonagem visual óbvia;
- ter roupas e silhuetas variadas;
- usar animações coerentes;
- receber iluminação/sombras compatíveis com a cena;
- manter identidade contemporânea e plausível para uma praia brasileira fictícia.

### Performance

Implementar desde cedo uma estratégia de crowd LOD:

- perto do jogador: Animator/IA completa necessária ao comportamento;
- média distância: animação e decisão simplificadas;
- longe: atualização reduzida;
- fora da área ativa: simulação abstrata ou desativada;
- pooling obrigatório para população recorrente;
- evitar centenas de NavMeshAgents completos simultâneos.

### Ambiente vivo adicional

Além dos NPCs, incluir progressivamente:
- ondas e movimento do mar;
- vento em palmeiras/vegetação;
- pássaros;
- áudio de mar;
- vozes/conversas ambientes;
- trânsito distante;
- objetos de praia;
- pequenas variações de atividade.

### Gate visual

A Fase 02 só recebe PASS visual quando uma execução real da Unity demonstrar:
1. praia e calçadão ocupados;
2. NPCs andando e realizando atividades;
3. clientes chegando e usando o quiosque;
4. ausência de colisões/teleportes visíveis graves;
5. densidade convincente sem comprometer o desempenho;
6. cena significativamente mais próxima das referências realistas do PROJECT RESORT do que de um blockout vazio.

