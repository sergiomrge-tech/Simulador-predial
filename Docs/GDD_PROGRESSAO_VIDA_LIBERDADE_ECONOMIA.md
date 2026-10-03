# GDD — Vida, patrimônio, liberdade de trabalho e economia

**Projeto:** Facility Ops / Simulador Predial  
**Status:** planejamento oficial de produção — sistemas descritos aqui ainda não estão todos implementados  
**Engine:** Unity 6000.6.2f1 / URP / C# / primeira pessoa  
**Direção visual:** realismo urbano cru, atmosférico e detalhado, usando VEIN apenas como referência de linguagem visual e materialidade, sem copiar assets, mapas, layouts ou identidade protegida.

---

## 1. Visão geral

O jogador começa como um técnico autônomo com poucos recursos, poucas ferramentas, uma moradia simples e acesso a uma quantidade limitada de trabalhos.

A progressão deve combinar quatro fantasias:

1. **ser um técnico competente**;
2. **escolher como ganhar dinheiro**;
3. **construir uma empresa**;
4. **melhorar a própria vida**.

O ciclo macro é:

**escolher trabalho → viajar → diagnosticar → reparar → testar → documentar → receber → pagar custos → decidir como gastar/investir → desbloquear novas opções → repetir em escala maior.**

O objetivo não é conduzir o jogador por um corredor linear de missões. A campanha narrativa existe, mas deve conviver com uma economia semiaberta de serviços.

---

## 2. Liberdade de trabalho

### Regra central

O jogador deve ter liberdade para decidir:

- qual serviço aceitar;
- em qual região trabalhar;
- qual cliente priorizar;
- qual especialidade desenvolver primeiro;
- quando fazer campanha principal;
- quando fazer trabalhos livres;
- quando descansar ou gastar dinheiro em vida pessoal;
- quando investir em ferramentas, veículo, imóvel ou empresa.

### Início pequeno, expansão gradual

No começo, o escopo é propositalmente pequeno.

Exemplo inicial:

- Cidade Antiga;
- Edifício Horizonte;
- apartamentos;
- mercearia;
- restaurante;
- alguns chamados livres simples;
- elétrica básica;
- hidráulica básica.

Conforme o jogador progride:

- novos bairros entram no mapa;
- novos tipos de clientes aparecem;
- contratos recorrentes surgem;
- sistemas técnicos mais complexos são liberados;
- trabalhos de maior risco/pagamento aparecem;
- ferramentas específicas passam a ser necessárias;
- veículos maiores permitem transportar mais equipamento;
- reputação abre clientes mais exigentes.

### Nenhum caminho único

O jogador pode escolher, por exemplo:

- especializar-se primeiro em elétrica;
- investir em hidráulica;
- focar em contratos preventivos;
- fazer muitos serviços pequenos;
- economizar para um veículo;
- comprar ferramentas avançadas;
- melhorar a casa;
- juntar para mudar de imóvel.

A campanha principal continua disponível como eixo narrativo, mas não deve impedir a economia livre.

---

## 3. Estrutura de oferta de trabalhos

Criar um sistema de **Mercado de Serviços**.

### Fontes de chamados

- clientes de bairro;
- condomínio;
- comércio;
- escola;
- hospital;
- hotel;
- indústria;
- contratos recorrentes;
- emergências;
- indicações de NPCs;
- clientes antigos;
- quadro de serviços da Oficina Aurora;
- futura reputação online fictícia.

### Tipos de trabalho

#### Elétrica
- tomada sem energia;
- iluminação;
- disjuntor;
- relé;
- quadro;
- curto intermitente;
- falha em alimentação;
- manutenção preventiva;
- gerador.

#### Hidráulica
- torneira;
- registro;
- vazamento;
- bomba;
- reservatório;
- pressão;
- drenagem;
- recalque;
- preventiva.

#### Climatização
- filtro;
- sensor;
- condensadora;
- evaporadora;
- bomba de condensado;
- falta de refrigeração;
- redundância.

#### Segurança e incêndio
- alarme;
- sensor;
- iluminação de emergência;
- bomba de incêndio;
- central;
- teste preventivo.

#### Acesso e telecom
- interfone;
- fechadura;
- controle de acesso;
- rede;
- câmera;
- cabeamento.

### Oferta dinâmica

O jogador deve receber uma pequena lista de trabalhos disponíveis, não centenas.

Exemplo:

- 3 a 5 trabalhos ativos no início;
- 5 a 8 no meio do jogo;
- 8 a 12 na fase avançada.

Trabalhos podem expirar ou ser substituídos, mas a campanha principal nunca deve ser perdida permanentemente.

---

## 4. Escolha geográfica

Santa Aurora deve ser dividida por regiões.

Cada região possui:

- tipos de edifício;
- distância;
- custo de deslocamento;
- perfil de cliente;
- dificuldade;
- chance de chamados;
- sistemas mais comuns;
- faixa de pagamento.

### Cidade Antiga

- prédios antigos;
- instalações remendadas;
- clientes menores;
- baixa barreira de entrada;
- diagnóstico imprevisível;
- pagamentos menores;
- ótimo para início.

### Cinturão da Expansão

- condomínios;
- escolas;
- hotéis;
- instalações padronizadas;
- contratos recorrentes;
- pagamentos médios.

### Distrito Industrial

- galpões;
- fábricas;
- bombas;
- alta carga elétrica;
- maior risco;
- pagamentos altos;
- ferramentas e veículo adequados exigidos.

### Centro moderno / infraestrutura crítica

- hospitais;
- data center;
- grandes edifícios;
- sistemas redundantes;
- alta exigência;
- contratos premium.

O jogador pode escolher onde trabalhar entre as regiões desbloqueadas.

---

## 5. Dificuldade — difícil, mas nunca impossível

### Filosofia

O jogo deve punir decisões ruins, não o desconhecimento arbitrário.

A dificuldade deve vir de:

- diagnóstico;
- pressão econômica;
- planejamento;
- escolha de equipamento;
- tempo;
- priorização;
- reputação;
- risco de desperdício;
- manutenção do veículo;
- contratos que exigem preparo.

### Nunca usar

- falhas impossíveis de deduzir;
- puzzles sem pistas;
- custos que deixam o jogador permanentemente sem saída;
- perda total irreversível por um erro;
- eventos aleatórios que destroem progresso;
- exigência de ferramenta que o jogador não tinha como prever;
- missão obrigatória impossível sem grind excessivo.

### Garantias de recuperabilidade

Sempre manter pelo menos uma rota de recuperação:

- trabalhos simples continuam disponíveis;
- fornecedor oferece crédito limitado;
- peças básicas podem ser compradas;
- jogador pode vender item/veículo não essencial;
- contratos principais não expiram;
- reputação pode ser recuperada;
- dívida não bloqueia aceitar trabalho básico;
- existe renda mínima possível com serviços de baixo risco.

### Curva sugerida

**Início:** baixa complexidade, pouca margem de dinheiro.  
**Meio:** maior complexidade, melhor margem, mais custos.  
**Final:** sistemas difíceis, grandes recompensas e alto custo operacional.

---

## 6. Sistema de avaliação de trabalho

Cada serviço avalia:

- diagnóstico correto;
- número de medições;
- peças desperdiçadas;
- tempo;
- segurança/procedimento;
- teste final;
- documentação;
- satisfação do cliente.

Resultado:

- pagamento;
- bônus;
- reputação;
- XP;
- chance de indicação;
- histórico persistente no prédio.

Erro não deve significar automaticamente falha total. Pode significar:

- menor pagamento;
- perda de bônus;
- custo de peça;
- reputação menor;
- retorno ao local;
- consequência futura.

---

## 7. Economia profissional

### Receitas

- chamados avulsos;
- bônus por diagnóstico limpo;
- contratos recorrentes;
- preventiva;
- emergências;
- grandes contratos;
- indicações.

### Custos

- peças;
- ferramentas;
- kits;
- combustível;
- manutenção;
- dívida;
- salários futuros;
- seguros abstratos;
- parcela de veículo;
- aluguel/sede;
- impostos simplificados fictícios, se usados.

### Regra

O dinheiro precisa permanecer relevante durante toda a campanha.

---

## 8. Progressão de ferramentas

### Tier 0 — início

- ferramentas manuais;
- multímetro simples;
- lanterna;
- maleta;
- kit hidráulico básico.

### Tier 1 — profissional inicial

- detector de tensão;
- medidor de pressão;
- parafusadeira;
- câmera de inspeção;
- melhor EPI.

### Tier 2 — técnico avançado

- câmera térmica;
- detector de vazamento;
- megômetro abstrato;
- equipamentos de bomba;
- ferramentas HVAC.

### Tier 3 — empresa

- instrumentos premium;
- kits redundantes;
- equipamentos de laudo;
- ferramentas compartilhadas por equipe.

Ferramenta melhor deve abrir possibilidades, dar precisão ou eficiência, nunca "resolver automaticamente" o diagnóstico.

---

## 9. Veículos

### Função

Veículo influencia:

- distância acessível;
- capacidade de ferramentas;
- estoque transportado;
- tipo de contrato;
- custo operacional;
- imagem profissional.

### Progressão

#### V0 — transporte inicial
- quase sem capacidade;
- baixo custo.

#### V1 — compacto usado
- primeiras ferramentas;
- custo baixo;
- pequeno estoque.

#### V2 — utilitário/perua
- mais capacidade;
- contratos médios.

#### V3 — furgão
- oficina móvel;
- estoque grande;
- contratos maiores.

#### V4 — van profissional
- equipe;
- grandes equipamentos.

#### V5 — frota
- múltiplos funcionários e veículos.

### Atributos

- preço;
- capacidade;
- confiabilidade;
- consumo;
- manutenção;
- condição;
- valor de revenda.

---

## 10. Moradia e patrimônio

A residência deve ser visitável em primeira pessoa.

### H0 — kitnet/quarto simples
- início;
- móveis usados;
- pouco espaço;
- ferramentas misturadas à vida pessoal.

### H1 — kitnet melhorada
- pintura;
- iluminação;
- cama;
- armário;
- mesa;
- TV pequena.

### H2 — apartamento compacto com vaga
- garagem;
- escritório pequeno;
- armazenamento.

### H3 — apartamento maior
- sala;
- cozinha completa;
- quarto;
- escritório;
- melhor garagem.

### H4 — casa pequena
- garagem;
- depósito;
- oficina doméstica.

### H5 — casa com oficina anexa
- 2 veículos;
- bancada profissional;
- depósito;
- escritório;
- hobby.

### H6 — residência premium
- alto padrão;
- garagem grande;
- área de lazer;
- coleções;
- símbolo de ascensão.

### Mercado imobiliário

Imóveis têm:

- preço;
- bairro;
- garagem;
- armazenamento;
- conforto;
- despesas;
- valor de revenda;
- financiamento;
- slots/áreas de decoração.

O jogador nunca é obrigado a mudar.

---

## 11. Móveis e casa

### Quarto
- cama;
- colchão;
- armário;
- iluminação;
- cortina.

### Sala
- sofá;
- TV;
- estante;
- som;
- tapete.

### Cozinha
- geladeira;
- fogão;
- micro-ondas;
- cafeteira;
- armários.

### Escritório
- computador;
- monitor;
- impressora;
- cadeira;
- arquivo.

### Garagem/oficina
- bancada;
- painel;
- armário;
- prateleira;
- compressor;
- carrinho.

### Decoração
- fotos;
- certificados;
- lembranças;
- placas;
- miniaturas;
- itens de campanha;
- coleções.

---

## 12. Lazer

O jogador precisa ter motivos para gastar dinheiro fora do trabalho.

### Entretenimento em casa

- TV;
- videogame;
- PC;
- som;
- livros;
- filmes.

### Hobbies

- eletrônica;
- marcenaria;
- restauração;
- modelismo;
- fotografia;
- rádio fictício;
- impressão 3D fictícia.

### Atividades externas

- pesca;
- academia;
- ciclismo;
- trilha;
- fotografia urbana;
- kart fictício;
- eventos locais.

### Vida social

- cafeteria;
- restaurante;
- cinema;
- encontros com NPCs;
- eventos.

### Viagens

- fim de semana;
- hotel;
- passeio regional;
- souvenirs.

### Coleções

- ferramentas antigas;
- miniaturas;
- placas;
- livros;
- objetos históricos;
- lembranças de contratos.

Lazer é opcional e não pode ser requisito para concluir a campanha.

---

## 13. Conforto

Índice simples derivado de:

- cama;
- cozinha;
- iluminação;
- climatização;
- entretenimento;
- organização.

Benefícios leves:

- descanso;
- pequenas falas;
- animações;
- avanço de tempo;
- bônus mínimos.

Sem fome/sede/higiene obrigatórios.

---

## 14. Despesas recorrentes

Possíveis:

- aluguel;
- condomínio;
- energia/água;
- internet;
- seguro;
- manutenção;
- parcelas;
- custos empresariais.

Regras:

- periodicidade clara;
- previsão antes da cobrança;
- nunca causar softlock;
- permitir renegociação;
- manter trabalhos simples disponíveis.

---

## 15. Financiamento e revenda

### Veículos e imóveis

- entrada;
- parcelas;
- juros simplificados;
- total exibido;
- antecipação opcional;
- revenda.

### Dívida

Dívida deve gerar pressão, mas não destruir a campanha.

---

## 16. Patrimônio

Tela futura:

### Ativos
- dinheiro;
- imóvel;
- veículo;
- ferramentas;
- empresa.

### Passivos
- dívida;
- financiamento;
- parcelas.

### Patrimônio líquido

Indicador de evolução, não condição de vitória.

---

## 17. Progressão por campanha

### Prólogo
- kitnet;
- ferramentas básicas;
- poucos trabalhos;
- Cidade Antiga.

### Capítulo I
- primeiros serviços livres;
- pequenas compras;
- móveis básicos;
- reputação inicial.

### Capítulo II
- primeiro contrato preventivo;
- bomba;
- primeiro veículo relevante;
- apartamento com vaga possível;
- mais liberdade de região.

### Capítulos III–V
- novos sistemas;
- casa pequena;
- utilitário;
- escritório;
- hobbies.

### Capítulos VI–IX
- casa/oficina;
- van;
- contratos maiores;
- equipe inicial;
- lazer caro.

### Capítulos X–XIV
- sede separada;
- frota;
- imóvel premium opcional;
- ferramentas top;
- patrimônio consolidado.

---

## 18. Balanceamento inicial

Valores provisórios.

### Pequenos gastos
- lazer curto: R$ 15–80
- decoração: R$ 50–400
- móveis: R$ 200–1.500
- eletrônicos: R$ 500–5.000

### Ferramentas
- básicas: R$ 50–500
- intermediárias: R$ 500–5.000
- avançadas: R$ 5.000–25.000

### Veículos
- usado: R$ 15.000–30.000
- utilitário: R$ 35.000–80.000
- furgão/van: R$ 80.000–180.000

### Imóveis
- kitnet/apto simples: R$ 120.000–250.000
- apartamento maior: R$ 250.000–450.000
- casa: R$ 350.000–700.000
- casa/oficina: R$ 650.000–1.200.000
- premium: acima disso.

Esses valores só entram em gameplay após recalibrar a renda da campanha.

---

## 19. Mapa e direção visual

A cidade, casas, prédios e interiores devem adotar uma linguagem visual:

- realista;
- detalhada;
- urbana;
- usada;
- materialmente crível;
- com desgaste;
- iluminação atmosférica;
- clutter funcional;
- interiores densos;
- áreas técnicas coerentes.

VEIN é referência de atmosfera e qualidade visual, não fonte de assets ou layouts.

O lar do protagonista precisa receber atenção especial e evoluir visualmente em cada fase.

---

## 20. Ordem de implementação recomendada

### Fase A — economia livre mínima
1. quadro de trabalhos;
2. 3–5 chamados disponíveis;
3. escolha de local;
4. pagamento/custo;
5. reputação;
6. liberdade entre campanha e trabalhos livres.

### Fase B — progressão profissional
1. loja de ferramentas;
2. requisitos por contrato;
3. estoque;
4. veículo inicial;
5. custos de deslocamento.

### Fase C — lar
1. criar kitnet inicial em 3D;
2. móveis compráveis;
3. upgrades visuais;
4. save dos itens.

### Fase D — patrimônio
1. apartamentos;
2. casas;
3. garagem;
4. compra/venda;
5. financiamento.

### Fase E — lazer
1. itens de entretenimento;
2. hobbies;
3. locais sociais;
4. eventos simples.

### Fase F — empresa
1. sede;
2. equipe;
3. frota;
4. contratos simultâneos.

---

## 21. Critérios de qualidade

Antes de considerar o sistema pronto:

- nenhuma compra essencial pode gerar softlock;
- sempre existe trabalho recuperável;
- jogador entende por que um serviço está bloqueado;
- o mapa mostra regiões disponíveis;
- residência evolui visualmente;
- veículo aparece fisicamente;
- móveis aparecem no lar;
- economia não exige grind excessivo;
- campanha não força ordem única de trabalhos livres;
- gastos pessoais são opcionais e satisfatórios;
- dificuldade aumenta por complexidade, não por arbitrariedade.

---

## 22. Regra oficial de design

**O jogador é livre para construir sua carreira e sua vida do jeito que quiser dentro das opções desbloqueadas.**

O escopo começa pequeno para ensinar o jogo. A liberdade cresce junto com:

- conhecimento;
- reputação;
- ferramentas;
- dinheiro;
- transporte;
- patrimônio;
- progresso narrativo.

**Jogo difícil, mas recuperável. Sem caminhos impossíveis e sem punições que destruam a carreira.**
