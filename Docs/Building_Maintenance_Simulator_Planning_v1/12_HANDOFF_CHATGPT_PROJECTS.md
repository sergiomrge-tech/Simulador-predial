# Handoff para ChatGPT Projects / Novo Chat no PC

Copie este arquivo junto com o restante do ZIP para o projeto.

## Contexto do projeto

Estamos desenvolvendo um novo jogo indie de simulação para PC/Steam.

### Decisões confirmadas

- Engine: Unity.
- Linguagem: C#.
- Plataforma inicial: Windows PC / Steam.
- Perspectiva: primeira pessoa.
- Single-player inicialmente.
- Modelo comercial: premium.
- Visual pretendido: 3D estilizado-realista, comercial, sem depender de hiper-realismo.
- Não fazer clone de supermercado, carro, cafeteria, restaurante ou loja genérica.

### Conceito

O jogador começa como técnico autônomo de manutenção predial/facilities. Ele recebe chamados que descrevem sintomas, visita o local, investiga a origem, utiliza ferramentas de diagnóstico gamificadas, identifica a causa, executa o reparo, testa o sistema e recebe pagamento.

Com o progresso, compra ferramentas, peças, van, estoque, melhora a sede, contrata funcionários e assume contratos de edifícios maiores como condomínios, escritórios, hotéis, shopping centers, hospitais e instalações técnicas fictícias.

### Diferencial principal

O jogador não deve apenas seguir um waypoint e segurar um botão. O gameplay central é:

**Sintoma → hipóteses → testes → evidências → diagnóstico → reparo → validação.**

O mesmo sintoma pode possuir causas diferentes. O jogador precisa realmente descobrir o problema.

### Sistemas planejados

- elétrica;
- hidráulica;
- climatização;
- bombas;
- alarmes/incêndio fictícios;
- geradores;
- rede/telecom;
- infiltração;
- elevadores como conteúdo avançado gamificado.

### Estratégia de escopo

Primeiro criar um vertical slice pequeno com três famílias de problema bem feitas. Não construir mundo aberto, multiplayer ou dezenas de sistemas no início.

### Primeira meta

Construir em Unity um protótipo com:

- movimentação em primeira pessoa;
- sala/local de teste;
- um sintoma;
- três causas possíveis;
- uma ferramenta de diagnóstico;
- coleta de evidências;
- diagnóstico;
- reparo;
- teste final;
- recompensa.

### Regras de continuidade

1. Ler todos os arquivos deste ZIP antes de alterar o escopo.
2. Manter arquitetura modular e IDs persistentes.
3. Não transformar o jogo em treinamento profissional real; os sistemas devem ser gamificados.
4. Priorizar diversão, leitura e feedback audiovisual.
5. Validar cada milestone em build Windows.
6. Não chamar algo de pronto sem teste.
7. Preservar saves versionados pensando em atualizações futuras.
8. Evitar crescimento prematuro de escopo.

## Prompt recomendado para iniciar no PC

> Leia integralmente todos os arquivos do pacote de planejamento do projeto Facility Ops. Considere `00_README_PRIMEIRO.md` como entrada e `02_GDD_MASTER.md` como documento mestre. A partir daí, crie a fundação do projeto em Unity 6 LTS/C#, começando apenas pela Fase 0 e pelo protótipo de diagnóstico da Fase 1. Preserve o escopo, a arquitetura modular e o diferencial Sintoma → Hipóteses → Testes → Evidências → Diagnóstico → Reparo → Validação. Antes de expandir conteúdo, entregue uma primeira versão técnica jogável no Windows e documente tudo o que foi implementado, testado, pendente e qualquer desvio do planejamento.
