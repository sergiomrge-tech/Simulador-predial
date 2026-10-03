# GDD Master — Facility Ops (codinome)

## 1. Resumo

**Gênero:** Simulation / Management / Job Simulator  
**Perspectiva:** primeira pessoa  
**Plataforma inicial:** Windows PC / Steam  
**Engine:** Unity 6 LTS  
**Input:** teclado + mouse; gamepad em fase posterior  
**Modo:** single-player  
**Estrutura:** hub empresarial + locais de serviço instanciados  
**Modelo de venda:** jogo premium

## 2. Loop principal

1. Ver chamados disponíveis.
2. Avaliar pagamento, urgência, distância/complexidade simulada e risco de reputação.
3. Preparar ferramentas e peças.
4. Viajar/carregar o local da missão.
5. Conversar rapidamente com cliente/zelador/gerente.
6. Inspecionar o local e coletar sintomas.
7. Usar ferramentas de diagnóstico.
8. Identificar a causa.
9. Executar reparo.
10. Testar o sistema.
11. Entregar serviço.
12. Receber dinheiro, experiência e reputação.
13. Repor peças e investir na empresa.
14. Desbloquear trabalhos/contratos mais complexos.

## 3. Metaloop

### Começo

O jogador possui:

- pequeno escritório/oficina alugada;
- kit básico de ferramentas;
- celular/tablet de trabalho;
- poucos fornecedores;
- reputação local baixa;
- chamados residenciais e comerciais simples.

### Meio do jogo

- van própria;
- estoque de peças;
- ferramentas especializadas;
- contratos preventivos;
- primeiro funcionário;
- sistema de agenda;
- edifícios de médio porte;
- chamados simultâneos que exigem priorização.

### Late game

- empresa consolidada;
- vários técnicos;
- veículos especializados;
- contratos de hospitais, hotéis, shopping centers e plantas industriais fictícias;
- central de operações;
- manutenção preventiva baseada em indicadores;
- grandes incidentes sistêmicos;
- gerenciamento de equipes e custos.

## 4. Estrutura de mundo

Não usar mundo aberto no MVP.

### Hub

Sede da empresa evolutiva:

- mesa/PC;
- depósito;
- bancada;
- prateleiras;
- estacionamento;
- mural de contratos;
- área administrativa;
- futuras salas para funcionários.

### Locais de serviço

Mapas independentes reutilizáveis com variações:

- apartamento;
- casa;
- pequena loja;
- escritório;
- condomínio;
- pequeno prédio comercial;
- hotel;
- hospital;
- shopping;
- indústria/galpão;
- data center/infraestrutura crítica fictícia.

Cada local possui uma rede lógica de sistemas internos.

## 5. Estrutura de missão

Cada missão é composta por:

- cliente;
- local;
- sintomas;
- sistemas afetados;
- possíveis causas;
- causa real sorteada ou definida;
- condições ambientais;
- requisitos de ferramenta;
- requisitos de peça;
- urgência;
- pagamento base;
- bônus;
- penalidades;
- avaliação final.

## 6. Classificação de chamados

### Rotina

Problemas simples e comuns. Baixo risco, baixo pagamento.

### Urgente

Tempo conta contra a recompensa ou reputação.

### Diagnóstico difícil

Sintoma ambíguo. Mais de uma causa plausível.

### Preventivo

Inspeção periódica. O jogador busca problemas antes da falha.

### Emergência

Um ou mais sistemas degradando simultaneamente.

### Contrato

Conjunto de tarefas em uma instalação recorrente.

## 7. Resultado de serviço

Avaliar:

- problema correto resolvido;
- tempo;
- desperdício de peças;
- danos causados;
- limpeza/organização;
- testes finais executados;
- satisfação do cliente;
- retorno/reincidência.

## 8. Estados de falha

Evitar “game over” frequente. Falhas devem gerar consequências econômicas:

- retorno sem cobrança;
- avaliação menor;
- perda de reputação;
- peça desperdiçada;
- cliente perdido;
- multa contratual;
- redução de acesso a contratos premium.

## 9. Sistema de dificuldade

A dificuldade aumenta por:

- sintomas menos explícitos;
- instalações maiores;
- dependências entre sistemas;
- várias falhas simultâneas;
- tempo limitado;
- restrição de peças;
- prioridade de contratos;
- necessidade de delegação.

## 10. Objetivo de retenção

O jogador deve sempre enxergar o próximo salto:

- “só falta esse contrato para comprar a van nova”;
- “mais 2 níveis para desbloquear climatização avançada”;
- “se eu subir a reputação para 4 estrelas, libero o hospital”;
- “preciso contratar um técnico para aceitar dois chamados simultâneos”.

## 11. Conteúdo emergente

Eventos podem modificar missões:

- temporal fictício aumenta chamados de infiltração;
- onda de calor aumenta climatização;
- queda de energia gera chamados elétricos;
- prédio antigo aumenta chance de falhas múltiplas;
- cliente premium exige prazo curto;
- peça em falta aumenta custo/logística.

## 12. Vitória / fim

Não há encerramento rígido no modo carreira. O objetivo final é transformar a empresa em uma operação de alto nível. Uma campanha pode ter marcos e uma “conclusão” narrativa, mas o save continua.
