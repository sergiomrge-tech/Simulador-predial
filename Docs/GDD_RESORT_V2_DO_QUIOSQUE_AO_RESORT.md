# GDD v2 — Do Quiosque ao Resort (Resort Aurora)

Status: **direção vigente a partir de 2026-10-06**, decidida pelo usuário (ideia central) e detalhada por Claude como diretor.
Esta versão **prevalece** sobre `GDD_RESORT_SANTA_AURORA.md` (v1) em: ideia central, progressão, tamanho do mapa e abertura do jogo.
O restante da v1 (hóspedes, construção, economia, reputação, eventos, riscos) continua como base de sistemas. A história está em
`LORE_RESORT_AURORA.md`.

## 1. Ideia central

> Você começa com **uma barraca de lanches na areia**, vendendo para quem passa pela Orla. Trabalho, risco, vontade e uma história maior
> te levam, degrau por degrau, até construir o **resort 5 estrelas de luxo mais grandioso e bonito da costa**, com tudo o que um resort
> desse nível tem.

O prazer do jogo é **ver a evolução com os próprios olhos**: o mesmo trecho de praia que abre com uma barraca de lona termina com um
complexo monumental. O jogador deve sentir orgulho de cada fase e, no fim, ficar parado olhando o que construiu.

Pilares:
1. **Humildade → grandiosidade**: cada fase muda de verdade a paisagem, a luz da noite, o som e as pessoas.
2. **Trabalho com as mãos primeiro**: o início é tátil (servir, preparar, atender), depois vira gestão.
3. **Terreno como recurso**: a evolução depende de conquistar terrenos; o espaço é o mapa de progressão.
4. **Uma cidade pequena e viva, não um mundo vazio**: só o bairro da Orla, bem feito.
5. **Difícil, mas recuperável**; nunca game over (ver v1, seção 7).

## 2. Mapa: somente o Bairro da Orla

Santa Aurora inteira deixa de ser jogável. O mundo vira **um bairro costeiro**, o **Bairro das Palmeiras**, finalizado em altíssima
fidelidade. O resto da cidade existe como **fora de cena**: chega por estrada, ônibus, entregas e mensagens.

### 2.1 Extensão (decisão)
Uma faixa de ~1,6 km (leste–oeste) × ~0,9 km (norte–sul), da vila residencial ao promontório do farol:

| Zona | Papel |
|---|---|
| **Vila da Orla** (borda sul da Cidade Antiga, ~500 m da praia) | Casa do protagonista (Apto 12 do Lar), mercearia, padaria, ponto de ônibus, comércio de bairro, fornecedores locais, onde mora a equipe |
| **Avenida das Palmeiras → Avenida da Orla** | Eixo de entrada de turistas e entregas; ponto do ônibus intermunicipal; trânsito |
| **Calçadão e Praia das Palmeiras** | Onde tudo começa: barraca, quiosque, passeio, banhistas, píer central |
| **Platô e encosta atrás da avenida** | Terrenos de expansão em terraços (o futuro resort) |
| **Praia do Farol e promontório** | Fase final: ala exclusiva, spa, heliponto, farol restaurado |
| **Marina leste** (menor) | Fase tardia: marina e passeios de barco |
| **Grande Hotel Palmeiras (ruínas)** | Lote histórico central da história; vira o coração do resort |

Fora da faixa: uma **entrada da estrada** (portal de chegada de ônibus e caminhões) e o **horizonte do mar**. Nada além do necessário.

### 2.2 O que acontece com o trabalho feito
- Reaproveitado: a Orla inteira (W4), a Vila/Cidade Antiga sul (W3.2 e W5S), o terreno e o ciclo dia/noite.
- Descartado do escopo jogável: Zona Empresarial, Distrito Tecnológico, Industrial, Expansão e Centro (ficam como arte arquivada).
- Locais de campanha antigos (Horizonte, Imperial, Mercearia) viram **locais do bairro** ou são citados fora de cena.

### 2.3 Parcelas (terrenos de evolução)
O mapa é dividido em **parcelas** compradas ou conquistadas. O espaço livre é o ponto central da progressão: **sempre há terreno
disponível para crescer**, mas ele exige dinheiro, licença, reputação ou uma decisão de história.

| Parcela | Local | Tamanho | Como se obtém |
|---|---|---|---|
| P0 | Ponto da barraca no calçadão | ~6 × 4 m | Licença de ambulante (prólogo) |
| P1 | Faixa do quiosque, frente da praia | ~20 × 12 m | Concessão municipal do quiosque |
| P2 | Lote da pousada atrás da avenida | ~40 × 40 m | Compra do sobrado do Seu Tonico |
| P3 | Quarteirão ao lado | ~70 × 60 m | Compra, desapropriação negociada ou parceria |
| P4 | **Grande Hotel Palmeiras (ruínas)** | ~90 × 80 m | Escritura histórica (arco central da história) |
| P5 | Platô em terraços | ~200 × 120 m | Licença ambiental + obra de terraplanagem |
| P6 | Promontório do Farol | ~150 × 100 m | Última etapa; acordo com a prefeitura |
| P7 | Marina e píer leste | ~120 × 60 m | Concessão portuária |

Terrenos são terraplanados ao desbloquear (terraços planos para o grid, como no `ResortSite`). Dificuldade de relevo: o platô sobe ~9–12 m,
usado de propósito para dar **vista, escadarias e piscinas em cascata** ao resort final.

## 3. Progressão: sete etapas

Cada etapa tem **um marco físico**, **uma paisagem nova**, **um conjunto de sistemas** e **um capítulo da história**.

| # | Etapa | Marco | O que muda no jogo |
|---|---|---|---|
| 1 | **Barraca** | 1 barraca de lanches na areia | Primeira pessoa: preparar e servir. Estoque, preço, clima, horário de movimento |
| 2 | **Quiosque** | Quiosque fixo com mesas, 2 funcionários | Cardápio, equipe, cozinha pequena, licença, música, cadeiras de praia |
| 3 | **Restaurante e pousada** | Restaurante coberto e 6 quartos no sobrado | Hospedagem, recepção, limpeza, reservas, 1ª nota de avaliação |
| 4 | **Hotel** | 30–60 quartos, piscina, bar, lobby | Modo Planta (construção livre), equipe departamental, eventos pequenos |
| 5 | **Complexo** | Spa, salão de eventos, bangalôs, academia, kids club | Segmentos (família, casais, corporativo), pacotes, concorrência |
| 6 | **Resort** | Praia privativa de serviço, gastronomia autoral, marina | Luxo, celebridades, prêmios, restauração do Grande Hotel |
| 7 | **Grand Aurora** | O resort 5 estrelas completo no platô e no promontório | Clímax: inauguração, final da história, modo livre |

### 3.1 Prólogo e primeiro dia
Abre em primeira pessoa, de manhã, na casa do protagonista (Apto 12): a janela mostra a vila; ele desce, pega o ônibus ou vai a pé até a
Orla, abre a barraca. É o **tutorial vivo**: preparar, servir, cobrar, fechar a conta do dia, comprar estoque na mercearia e voltar.
Dura ~20 minutos e termina com a primeira poupança e uma carta de Guto.

### 3.2 Barraca (etapa 1) em detalhe
- Produtos: pastel, milho, queijo coalho, água de coco, caipirinha sem álcool, picolé, sanduíche natural.
- Demanda: pedestres do calçadão geram fila por horário, clima e eventos (jogo de futebol, feriado, maré).
- Perigos pequenos: sol forte derrete o estoque, vento derruba o toldo, fiscal pede licença, concorrente ambulante.
- Dinheiro: lucro diário pequeno, mas suficiente para a primeira melhoria: **toldo, freezer, fogão**, e depois a **licença de quiosque**.
- Objetivo da etapa: juntar a concessão do quiosque (cerca de 2 semanas de jogo).

### 3.3 Passagem para a gestão
Ao chegar ao quiosque, o jogador ganha o **Modo Planta**: uma prancheta de obra que liga a câmera aérea e o grid. Antes disso o
grid nem aparece. As funções de primeira pessoa não somem: servir, inspecionar e decorar continuam como **modo de visita** (e cada etapa
tem um trabalho de campo próprio, como atender na recepção do dia 1 da pousada).

### 3.4 O resort final (a visão)
Deve ser **extremamente grandioso e lindo**. Metas de composição, a serem refinadas com a arte:
- **Silhueta**: torres escalonadas em terraços sobre o platô, vistas do mar de todos os quartos, farol restaurado no promontório.
- **Água**: piscina infinita em cascata descendo o platô, lagoa-laguna, spa termal, praia privativa com deques e bangalôs sobre a água.
- **Entrada**: grande alameda de palmeiras imperiais, fonte, lobby em átrio de vários andares, o Grande Hotel restaurado como joia histórica.
- **Serviços**: 5–6 restaurantes e bares (incluindo gastronomia autoral), spa completo, academia, quadras, kids club, anfiteatro, salão
  de eventos e casamentos, marina e iate clube, heliponto, loja de grife, concierge, adega, cinema ao ar livre, trilhas, jardins temáticos.
- **Noite**: iluminação cênica, fogos de inauguração, trilha sonora própria. A noite do final é a recompensa visual do jogo.
- **Estilos** (escolha do jogador na etapa 4): colonial litorâneo, moderno tropical, art déco, mediterrâneo. Todos chegam a um 5 estrelas.

Critérios de "5 estrelas": nota mínima, serviços obrigatórios (spa, 3 restaurantes, concierge 24 h, suíte presidencial, piscina,
acesso à praia), sustentabilidade e prêmio de gastronomia. Eles viram a lista de metas da etapa 6.

## 4. Câmera e controle (decisão)
- **Etapas 1–2**: primeira pessoa, sem grid.
- **Etapa 3 em diante**: alternância entre **Modo Visita** (primeira pessoa) e **Modo Planta** (aérea RTS com grid).
- A câmera RTS do protótipo R0 e o `ResortSite` continuam válidos. O grid de cada parcela é ativado conforme o terreno é conquistado.

## 5. Economia da evolução
- Moeda única, mais **reputação**, **influência local** (prefeitura, comunidade) e **confiança** (equipe e moradores).
- Ritmo alvo: etapa 1 ≈ 1–2 h; etapa 2 ≈ 2–3 h; etapa 3 ≈ 4 h; etapa 4 ≈ 6 h; etapa 5 ≈ 6 h; etapa 6 ≈ 8 h; etapa 7 ≈ 4 h. Total ~35 h, mais modo livre.
- Dinheiro vem de vendas, hospedagem, eventos e parcerias, nunca de maneira pura de "esperar". A decisão (o que construir, onde, para quem)
  decide a curva.
- Recuperável: falir uma etapa devolve o jogador à anterior com cicatriz de reputação; nunca há game over.

## 6. Sistemas por etapa (resumo)
- E1: estoque, preparo, atendimento, filas, clima, licença, tipos de cliente.
- E2: equipe, cozinha, cardápio, mesas, layout, música, limpeza, caixa.
- E3: quartos, reserva, check-in, camareira, café da manhã, avaliação.
- E4: construção em grid, departamentos, turnos, eventos, preços dinâmicos.
- E5: segmentos de hóspede, pacotes, spa, concorrência, marketing, sustentabilidade.
- E6: gastronomia, prêmios, VIPs, restauração histórica, marina.
- E7: obras monumentais, inauguração, legado.

## 7. Impacto ecológico (diferencial)
Tartarugas desovam na Praia do Farol. Obras, luz e lixo afetam a desova. Uma **pontuação ambiental** liga a licenças, bônus de
hóspede e ao final da história. É um custo e uma oportunidade, não um sermão.

## 8. Marcos de produção (substituem R2+ do GDD v1)
| Marco | Entrega |
|---|---|
| **R2 — Prólogo jogável** | Apto 12 → caminho → barraca em primeira pessoa. Preparo, venda, caixa, fim de dia, save |
| **R3 — Mapa do Bairro** | Recorte do bairro (vila + avenida + Orla + platô) em Unity, em escala e fidelidade alvo, com parcelas |
| **R4 — Economia e tempo** | `GameManager`/`TimeManager`/`EconomyManager`, eventos, save JSON, UI |
| **R5 — Quiosque e equipe** | Etapa 2 completa, IA de clientes e funcionários |
| **R6 — Pousada e hóspedes** | Etapa 3, reservas e avaliações, Modo Planta com grid |
| **R7 — Hotel e complexo** | Etapas 4–5, kit modular, segmentos |
| **R8 — Resort e Grand Aurora** | Etapas 6–7, clímax visual, final |
| **R9 — Polimento** | Áudio, UI final, desempenho, fotografia |

## 9. Riscos novos
| Risco | Mitigação |
|---|---|
| Começar pequeno exige **qualidade tátil** de primeira pessoa (mãos, animações, preparo) | R2 é um vertical slice só disso, antes de qualquer expansão |
| Clímax grandioso exige muita arte | Kit modular + estilos + terraços reaproveitando regras; começar pelo silhueta e pela noite |
| Mapa pequeno cansar | Eventos sazonais, mudança de clima e hóspedes recorrentes; a evolução do mapa é o conteúdo |
| Mundo antigo (8×8 km) ficar órfão | Arquivar; só o bairro conta como entrega |
