# Conteúdo, Missões e Instalações

## 1. Estratégia de conteúdo

Construir poucos mapas modulares capazes de gerar muitas missões através de estados diferentes.

A profundidade deve vir de combinações de:

- local;
- sintoma;
- causa;
- sistema;
- urgência;
- restrição;
- evento contextual.

## 2. MVP — locais

### Local A — Apartamento

Ambientes:

- sala;
- cozinha;
- banheiro;
- quarto;
- corredor técnico simples.

Falhas iniciais:

- iluminação;
- tomada;
- vazamento;
- torneira;
- sanitário.

### Local B — Pequena loja

Ambientes:

- área de vendas;
- estoque;
- banheiro;
- quadro técnico;
- pequeno depósito.

Falhas:

- circuito;
- luminária;
- tomada;
- vazamento;
- falha de equipamento de apoio fictício.

### Local C — Escritório pequeno

- recepção;
- estações de trabalho;
- copa;
- banheiro;
- sala técnica.

Introduz diagnóstico com múltiplos circuitos.

## 3. Vertical slice recomendado

Um único prédio pequeno com:

- térreo comercial;
- 2 ou 3 andares;
- apartamentos/escritórios;
- sala técnica.

Três famílias de problema:

1. circuito/iluminação;
2. vazamento hidráulico;
3. falha simples de climatização ou bomba.

Objetivo: provar o loop completo, não quantidade.

## 4. Banco de sintomas

Exemplos de linguagem de cliente:

- “A luz fica piscando e depois apaga.”
- “Tem água aparecendo no teto.”
- “A torneira perdeu pressão.”
- “O ar está ligado, mas a sala continua quente.”
- “Uma parte do escritório ficou sem energia.”
- “O alarme está acusando falha.”

O texto nunca deve revelar diretamente a peça defeituosa.

## 5. Geração de missão

Estrutura de dados:

- MissionDefinition
- LocationDefinition
- SymptomDefinition
- FailureDefinition
- RequiredToolTags
- RequiredPartTags
- EvidenceSet
- CompletionChecks
- RewardProfile

Missões podem ser:

- autorais;
- procedurais controladas;
- híbridas.

Recomendação: usar **procedural controlado**, com combinações validadas manualmente.

## 6. Cadeias de chamados

Alguns clientes devem voltar.

Exemplo:

1. pequeno escritório chama por uma tomada;
2. depois oferece contrato preventivo;
3. semanas depois surge uma emergência;
4. bom desempenho libera indicação para um prédio maior.

Isso cria história sem exigir cutscenes caras.

## 7. Contratos principais

### Condomínio residencial

Foco:
- hidráulica;
- elétrica;
- bombas;
- iluminação comum.

### Hotel

Foco:
- climatização;
- água;
- energia;
- alta pressão de tempo.

### Shopping

Foco:
- grande circulação;
- múltiplos setores;
- escalas de funcionários;
- chamados simultâneos.

### Hospital fictício

Late game.

Foco:
- redundância;
- criticidade;
- geradores;
- climatização;
- resposta rápida.

### Data center fictício

Late game.

Foco:
- energia;
- climatização;
- alarmes;
- rede simplificada;
- redundância.

## 8. Missões especiais

- preparação para inspeção;
- prédio após temporal;
- mudança de escritório;
- reforma parcial;
- pane durante evento;
- falta de peças;
- cliente VIP;
- contrato em risco.

## 9. NPCs

Tipos iniciais:

- proprietário;
- zelador;
- gerente;
- morador;
- funcionário;
- fornecedor;
- técnico contratado.

NPCs não precisam de IA social complexa no MVP.

## 10. Narrativa ambiental

Pequenos detalhes tornam locais memoráveis:

- avisos;
- objetos pessoais;
- caixas;
- equipamentos antigos;
- manutenção improvisada anterior;
- áreas recém-reformadas;
- histórico do prédio.

## 11. Rejogabilidade

Gerada por:

- causas diferentes para sintomas semelhantes;
- mapas reutilizados com layouts/objetos variantes;
- economia;
- contratos;
- funcionários;
- eventos;
- desafios opcionais;
- progressão de empresa.
