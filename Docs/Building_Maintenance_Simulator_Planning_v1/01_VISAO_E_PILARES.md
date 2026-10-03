# Visão do Produto e Pilares

## High concept

Um simulador em primeira pessoa no qual o jogador começa como técnico autônomo de manutenção predial. Ele recebe chamados, visita instalações, investiga defeitos, identifica a causa, executa o reparo, testa o sistema e recebe pagamento. Conforme ganha reputação e capital, compra ferramentas, veículos, peças, contrata técnicos e passa a administrar contratos de manutenção de edifícios cada vez maiores.

## Fantasia do jogador

> “Eu comecei sozinho, com uma caixa de ferramentas e pequenos reparos. Agora administro uma empresa responsável por manter prédios inteiros funcionando.”

A fantasia não é apenas “consertar coisas”. É **tornar-se indispensável para o funcionamento de uma cidade e de grandes instalações**.

## Diferencial comercial

A maior parte dos simuladores de trabalho usa uma estrutura simples: vá até o objeto, pressione um botão e receba dinheiro. O diferencial deste projeto deve ser:

- o problema nem sempre estar onde o sintoma aparece;
- existir mais de uma causa possível para o mesmo sintoma;
- o jogador usar pistas, ferramentas e testes para restringir hipóteses;
- escolhas erradas terem custo de tempo, peças, reputação ou retorno ao local;
- o sistema empresarial transformar trabalhos manuais em operação escalável.

## Pilares de design

### 1. Diagnóstico antes do reparo

O chamado descreve um **sintoma**, não a solução.

Exemplo de sintoma no jogo: “As luzes do corredor do 4º andar apagaram.”

Possíveis causas internas do sistema de jogo:

- circuito desarmado;
- luminária danificada;
- componente de comando defeituoso;
- sobrecarga simulada;
- falha em um quadro secundário;
- problema gerado por evento recente no edifício.

O jogador coleta pistas e identifica a causa correta.

### 2. Interações táteis e satisfatórias

As tarefas precisam ter feedback visual e sonoro forte:

- abrir tampas e painéis;
- desapertar/remover peças;
- conectar equipamento de teste fictício;
- remover água/resíduos;
- substituir componentes;
- alinhar/conectar peças;
- testar funcionamento;
- ouvir o sistema voltar a operar.

O objetivo é gerar vídeos agradáveis de assistir, bons para trailers, Shorts e streams.

### 3. Crescimento empresarial

O dinheiro deve mudar visivelmente o jogo:

- ferramentas melhores;
- mala/kit maior;
- estoque próprio;
- van;
- oficina/sede;
- recepcionista/dispatcher;
- técnicos contratados;
- contratos recorrentes;
- especializações;
- instalações maiores e mais complexas.

### 4. Problemas sistêmicos

Os edifícios devem parecer sistemas conectados. Um problema pode afetar outro setor. Isso cria profundidade e histórias emergentes sem exigir narrativa cinematográfica cara.

### 5. Escopo modular

Cada área técnica é um módulo independente que pode ser adicionado ao jogo sem reescrever a base:

- elétrica;
- hidráulica;
- climatização;
- bombas;
- incêndio/alarme;
- acesso e segurança;
- geradores;
- rede/telecom;
- elevadores como sistema avançado;
- infiltração e danos ambientais.

## Público-alvo

- fãs de simuladores de trabalho em primeira pessoa;
- jogadores de gerenciamento e progressão;
- pessoas que gostam de desmontar, organizar e reparar;
- público que consome jogos como “job simulator”, “repair simulator” e “management simulator”;
- streamers que buscam situações engraçadas, emergenciais ou satisfatórias.

## Sessão ideal

- 20 a 45 minutos para uma sessão curta;
- 1 a 3 horas para sessões de progressão;
- chamados simples: 5–12 minutos;
- contratos médios: 15–30 minutos;
- grandes ocorrências: 30–60 minutos.

## Tom

Realista o suficiente para parecer técnico, mas **gamificado** o suficiente para ser divertido e seguro. Não é um treinamento profissional real.

## Princípios que não devem ser quebrados

- não transformar o jogo em uma lista de quick-time events;
- não obrigar o jogador a decorar procedimentos profissionais reais;
- não fazer mapas enormes sem função;
- não adicionar multiplayer antes do núcleo single-player estar excelente;
- não inflar o número de sistemas antes de validar o diagnóstico + reparo;
- cada nova profissão/sistema deve gerar novas decisões, não apenas novas animações.
