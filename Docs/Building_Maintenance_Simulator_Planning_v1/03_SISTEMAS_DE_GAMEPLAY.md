# Sistemas de Gameplay

## 1. Sistema de diagnóstico

Este é o sistema mais importante do jogo.

### Conceito

Cada falha possui:

- sintomas visíveis;
- sintomas ocultos;
- causas candidatas;
- testes disponíveis;
- evidências;
- peça/ação corretiva;
- teste de confirmação.

### Modelo lógico

Exemplo abstrato:

`Sintoma -> Hipóteses -> Testes -> Evidências -> Diagnóstico -> Reparo -> Validação`

O jogo deve evitar exibir a resposta diretamente. O HUD pode registrar observações, mas não resolver o problema pelo jogador.

### Ferramentas de diagnóstico fictícias/gamificadas

- scanner técnico;
- medidor elétrico simplificado;
- detector de umidade;
- câmera térmica estilizada;
- manômetro simplificado;
- testador de rede;
- leitor de alarmes;
- tablet de manutenção com histórico do equipamento.

As ferramentas devem usar valores e feedback simplificados para não virar treinamento profissional.

## 2. Sistema elétrico

### MVP

- quadro de distribuição fictício;
- circuitos independentes;
- luminárias;
- tomadas;
- interruptores;
- falhas de componentes;
- sobrecarga simulada;
- circuitos que podem ser isolados no gameplay.

### Gameplay

- identificar qual circuito está ligado ao sintoma;
- encontrar componente com falha;
- substituir componente;
- restaurar alimentação virtual;
- testar.

## 3. Sistema hidráulico

### MVP

- tubulação segmentada;
- válvulas;
- torneiras;
- sanitários;
- sifões/conexões;
- vazamentos;
- pressão abstrata.

### Gameplay

- localizar vazamento;
- fechar setor;
- desmontar conexão;
- substituir componente;
- secar área;
- reabrir/testar.

## 4. Climatização

Primeira expansão após MVP.

- termostatos;
- filtros;
- unidades internas/externas estilizadas;
- ventilação;
- falhas de componentes abstratos;
- temperatura de zonas.

O foco deve ser diagnóstico de sintomas e manutenção visualmente satisfatória, sem replicar procedimentos técnicos perigosos.

## 5. Bombas e reservatórios

- bombas de água;
- sensores;
- reservatórios;
- válvulas;
- pressão/nível;
- alternância de bombas;
- falha de alimentação ou componente.

## 6. Incêndio e alarmes

Sistema fictício e simplificado:

- sensores;
- painéis;
- zonas;
- sirenes;
- falha de comunicação;
- bateria fictícia;
- inspeção preventiva.

## 7. Rede e telecom

- racks estilizados;
- switches fictícios;
- pontos de rede;
- cabos;
- dispositivos;
- conectividade por zonas;
- ferramenta de diagnóstico simplificada.

## 8. Geradores

Conteúdo de mid/late game:

- gerador;
- combustível abstrato;
- painel;
- bateria;
- transferência de energia simulada;
- manutenção preventiva.

## 9. Elevadores

Sistema avançado e altamente gamificado.

Deve ser tratado como quebra-cabeça técnico fictício, não como reprodução de manutenção real. Pode trabalhar com sensores, portas, alimentação, controle e estado do elevador em abstração.

## 10. Infiltração e estrutura superficial

- manchas de umidade;
- origem não necessariamente no ponto visível;
- janelas/telhado/tubulação como causas possíveis;
- detector de umidade;
- selagem/reparo gamificado;
- secagem.

## 11. Ferramentas

### Categorias

- manuais;
- diagnóstico;
- limpeza;
- acesso;
- reparo;
- especializadas.

### Estatísticas possíveis

- velocidade;
- precisão;
- durabilidade;
- alcance;
- qualidade do diagnóstico;
- número de funções.

Ferramentas melhores não devem eliminar completamente a habilidade do jogador.

## 12. Sistema de peças

Cada item possui:

- ID;
- categoria;
- compatibilidade;
- custo;
- qualidade;
- tamanho de estoque;
- fornecedor;
- raridade logística;
- chance de falha futura baseada em qualidade.

Qualidade barata pode economizar hoje e gerar reincidência futura.

## 13. Inventário de trabalho

Duas camadas:

### Inventário carregado

O que o jogador leva para a missão. Espaço limitado.

### Estoque da empresa

Grande quantidade de peças e consumíveis.

Essa limitação cria planejamento sem virar survival.

## 14. Tablet/telefone do jogador

Funções:

- chamados;
- mapa de planta simplificada;
- checklist;
- histórico do cliente;
- catálogo de peças;
- agenda;
- equipe;
- câmera/fotos antes e depois;
- orçamento simplificado;
- diagnóstico registrado.

## 15. Funcionários

Funcionários têm:

- nome;
- salário;
- especialização;
- nível;
- velocidade;
- qualidade;
- confiabilidade;
- disponibilidade.

O jogador pode enviar técnicos para trabalhos conhecidos, enquanto executa missões mais difíceis pessoalmente.

## 16. Delegação

Cada chamado delegado produz resultado probabilístico com base em:

- nível do técnico;
- especialização;
- complexidade;
- ferramentas disponíveis;
- qualidade das peças;
- carga de trabalho.

O jogador recebe relatório e pode precisar fazer retrabalho.

## 17. Reputação

Eixos possíveis:

- qualidade;
- pontualidade;
- preço;
- confiabilidade;
- especialização.

A reputação abre clientes melhores e contratos recorrentes.

## 18. Sistema de contratos

Contratos podem exigir:

- manutenção mensal;
- inspeções;
- SLA fictício;
- atendimento de emergência;
- disponibilidade de peças;
- equipe mínima.

Geram receita recorrente, mas criam obrigações.

## 19. Eventos dinâmicos

Eventos servem para variar demanda:

- calor;
- chuva;
- blecaute local fictício;
- temporada de manutenção;
- obra no prédio;
- ocupação máxima;
- falha em fornecedor.

## 20. Fotos antes/depois

Sistema opcional importante para sensação de trabalho concluído e para trailers. O jogo pode registrar automaticamente um enquadramento de antes/depois de certas tarefas.
