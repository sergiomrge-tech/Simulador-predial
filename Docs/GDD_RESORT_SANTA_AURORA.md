# GDD — Resort Aurora (simulador de resort em Santa Aurora)

Status: **proposta de planejamento, 2026-10-06.** Nasce da decisão do usuário de abandonar a manutenção como núcleo ("achei muito chato") e
aproveitar ao máximo a cidade já construída. Nada aqui está implementado. Itens marcados **[DECIDIR]** precisam de resposta do usuário
antes da produção.

## 1. Pitch

Você herda uma pousada decadente na Orla das Palmeiras, a costa sul de Santa Aurora, e a transforma, ao longo de anos de jogo, no maior
complexo de lazer da região: hotel, praia, restaurantes, marina, spa, eventos. A cidade inteira, da Cidade Antiga ao Distrito Tecnológico,
deixa de ser pano de fundo e vira **a engrenagem do negócio**: de onde vêm os hóspedes, os funcionários, os fornecedores, as atrações e a
concorrência.

Pilares:
1. **Construir e personalizar** (a fantasia principal): terreno, edifícios, quartos, jardins, piscinas, decoração, fachada.
2. **Receber pessoas**: hóspedes com perfis, desejos e histórias, vistos de perto, em primeira pessoa e do alto.
3. **Crescer com a cidade**: cada distrito desbloqueado muda quem chega, o que se vende e o que se pode construir.
4. **Difícil, mas sempre recuperável**: crises (clima, reputação, dívida) pressionam, nunca travam o jogo.

## 2. O que muda em relação ao projeto anterior

| Antes (manutenção) | Agora (resort) |
|---|---|
| Diagnóstico → reparo → teste → pagamento | Planejar → construir → operar → crescer |
| Chamados e contratos preventivos | Hóspedes, eventos, temporadas |
| Reputação com clientes de serviço | Reputação do resort (estrelas, avaliações) |
| Garagem/oficina como base | Pousada como base, depois o complexo |
| Prólogo elétrico no Horizonte | Prólogo de reabertura da pousada (ver 9) |

Preservar (decisões já tomadas e ativos prontos):
- Unity 6000.6.2f1, URP, Windows/Steam, single-player, **primeira pessoa** (ver 4 e [DECIDIR] 1).
- Santa Aurora, o masterplan 8×8 km, streaming por subcélulas, IDs estáveis, saves compatíveis.
- Direção visual realista, PBR, densa; nada low-poly como resultado final.
- Difícil porém recuperável (decisão 11); lazer opcional e não punitivo.
- Lore: personagens (Guto, Helena etc.) reaproveitados como sócios, funcionários e rivais. O hotel `camp.hotel`, o shopping, a Torre
  Imperial e o Horizonte existentes viram **locais de turismo e parcerias**, não missões de reparo.
- O código de manutenção (`ServiceSession`, `ChapterOne`, `ElectricalNetwork`) fica **congelado, não deletado**, até haver um plano de
  migração do save. Sistemas de ferramenta e falha podem voltar como mini-eventos de gestão (ver 6.6).

## 3. Como a cidade vira o jogo

### 3.1 Mapa de papéis dos distritos

| Distrito / local | Papel no resort |
|---|---|
| **Orla das Palmeiras** (3 praias, calçadão, 2 píeres, farol, quiosques) | Terreno do resort e do negócio de praia. Todo o núcleo jogável nasce aqui. |
| **Cidade Antiga** (vila_sul, porto_seco, oficinas) | Fonte de funcionários baratos, pousadas concorrentes, turismo cultural (mercearia, restaurante, Horizonte), fornecedores locais. Casa do protagonista. |
| **Santa Aurora Central** | Aeroporto/rodoviária de chegada, agência de viagens, prefeitura (alvarás), banco. Vitrine para atrair hóspedes. |
| **Zona Empresarial** | Hóspedes corporativos, convenções, eventos de empresas, contratos de salão. |
| **Distrito Tecnológico** | Reservas online, avaliações, marketing, automação do hotel, eventos de tecnologia. |
| **Distrito Industrial** | Lavanderia industrial, gás, alimentos, grandes compras, logística de suprimentos. |
| **Cinturão da Expansão** | Terrenos para segundo resort, hospedagem econômica, mão de obra, dormitórios de equipe. |
| Lugares de vida/lazer (`leisure.cafe`, `gym`, `cinema`, `park`, `fishing`) | Atrações e parcerias: pacotes de passeio, ingressos cortesia, pesca esportiva. |

### 3.2 Loops entre resort e cidade
- **Fluxo de turistas**: cada distrito aberto ao jogador adiciona um segmento de hóspede (ver 5.1).
- **Fluxo de suprimentos**: compras em fornecedores da cidade, com preço, prazo e qualidade; entrega em caminhão que cruza a cidade.
- **Fluxo de pessoas**: equipe mora na cidade, depende de transporte, tem humor e rotina.
- **Fluxo de dinheiro**: investimentos em obras públicas, parcerias e eventos mudam a cidade (novos píeres, ônibus, iluminação).
- **Reputação cruzada**: o resort afeta bairros (empregos, trânsito, preços); a cidade reage (apoio, protestos, vizinhos concorrentes).

### 3.3 Aproveitamento dos ativos prontos (W1–W4)
- Orla: calçadão, avenida, píeres, farol, quiosques, torres de salva-vidas, vida (carros, pedestres, banhistas), ciclo dia/noite. Viram o
  cenário e as atrações **do jogo desde o primeiro dia**.
- Cidade Antiga em alta fidelidade (recorte W3.2): vila viva para o jogador explorar, comprar e recrutar.
- Streaming por subcélulas, carros, vegetação, iluminação noturna: reaproveitados sem mudança.
- Lotes (13.003) e IDs: base para propriedades compráveis, concorrentes e populações.

## 4. Câmera e controle

- **Modo Passeio** (primeira pessoa): andar pelo resort, conversar com hóspedes e equipe, atender recepção, servir, inspecionar quartos,
  decorar em escala 1:1. É onde o jogo é "vivido".
- **Modo Planta** (câmera aérea livre): construir, posicionar, ver fluxo de hóspedes e mapa de calor. É onde o jogo é "administrado".
- Alternar entre os dois com uma tecla, sem tela de carregamento (mesma cena).
- **[DECIDIR] 1:** manter a primeira pessoa como visão principal (decisão vigente) ou tornar o Modo Planta o principal e a primeira pessoa
  apenas para visita. Recomendação: manter as duas, com construção só no Modo Planta.

## 5. Sistemas centrais

### 5.1 Hóspedes
Cada hóspede é um agente com:
- **Perfil**: casal, família, grupo de amigos, corporativo, aposentado, influenciador, nômade digital, lua de mel, atleta.
- **Orçamento e expectativa** (estrelas desejadas).
- **Necessidades**: descanso, comida, diversão, higiene, tranquilidade, conectividade, segurança, social.
- **Gostos e aversões**: praia, silêncio, festa, gastronomia, crianças, pets, cultura.
- **Estada**: chegada, check-in, rotina diária, eventos, check-out, avaliação (nota + texto gerado a partir do que viveu).
- **Memória**: hóspedes recorrentes lembram bons e maus momentos e voltam (ou trazem amigos).

Segmentos desbloqueados por marcos: econômico e mochileiro (início) → casais e famílias → corporativo → luxo → celebridades/eventos.

### 5.2 Construção
- **Terrenos** da Orla divididos em lotes (grade de 1 m, compras por lote). Preço varia com a distância do mar.
- **Edifícios**: pousada → blocos de quartos → torre → bangalôs na areia, sobre píer, jardim. Cada um com plantas modulares.
- **Quartos**: tipologias (simples, família, suíte, bangalô, cobertura). Móveis, decoração, varanda, vista. A vista (mar, jardim, rua) é
  calculada e afeta preço e nota.
- **Áreas comuns**: recepção, lobby, restaurante, bar, cozinha, café, piscinas, spa, academia, salão de eventos, kids club, marina, deck,
  quadra, jardim, anfiteatro, heliponto.
- **Infraestrutura (leve)**: energia, água, esgoto, internet e cozinha como *capacidades* abstratas por prédio. Em vez de reparo manual,
  o jogador **dimensiona e melhora** (gerador, caixa d'água, ETE). Falhas viram eventos de gestão (6.6).
- **Estilo arquitetônico**: temas (colonial litorâneo, moderno tropical, rústico praiano, art déco, luxo minimalista) com bônus de
  nicho. Kit modular reaproveitando o pipeline Blender do W3.
- **Licenças e prefeitura**: alvarás, gabarito, restrições ambientais perto da praia (progressão e dificuldade, ver 7).

### 5.3 Operação
- **Equipe**: recepção, camareiras, garçons, cozinha, manutenção (papel menor), segurança, salva-vidas, jardineiros, animadores,
  gerentes. Cada um com habilidades, salário, turno, humor, fadiga e lealdade. Contratar na cidade (Cidade Antiga, Expansão).
- **Turnos e escalas**: jogador define horários; automação progressiva com gerentes.
- **Serviços**: limpeza, café da manhã, restaurante, room service, lavanderia, bar, passeios, eventos.
- **Estoque e compras**: alimentos, bebidas, enxoval, amenities, combustível, produtos de limpeza. Fornecedores da cidade.
- **Preços e pacotes**: diária por tipologia, temporada, promoções, all inclusive, pacotes de passeio.
- **Marketing**: agência no Centro, parcerias com a Zona Empresarial, influenciadores, plataforma de reservas do Distrito Tecnológico.

### 5.4 Economia
- Receita: diárias, alimentos e bebidas, spa, passeios, eventos, aluguel de espaços, lojas, estacionamento.
- Custos: folha, compras, impostos, financiamento, obras, energia e água, marketing, seguros.
- Crédito: banco do Centro, juros, investidores (exigem metas). **Falência não existe**: o último recurso é uma reestruturação (ver 7).
- Tempo: 1 dia de jogo ≈ 8–12 minutos reais (ajustável); pausa e velocidade 1×/2×/4× no Modo Planta.
- Sazonalidade: alta temporada, feriados, chuva, tempestades tropicais, eventos da cidade.

### 5.5 Reputação e avaliações
- Nota geral de 1 a 5 estrelas e categorias (quartos, limpeza, comida, atendimento, localização, custo-benefício, ambiente).
- Avaliações escritas, geradas a partir da experiência real do hóspede (não aleatórias). Elas alimentam o fluxo futuro.
- Prêmios e selos (sustentabilidade, gastronomia, família, luxo).

### 5.6 Eventos e crises (substituem a "manutenção")
Eventos curtos, tomados como **decisões**, com consequência e saída:
- Clima: ressaca, tempestade, onda de calor, maré vermelha.
- Estrutura: queda de energia, falta de água, mofo, praga. Resolvidos por **escolha** (acionar equipe, contratar terceiros, trocar equipamento),
  nunca por um puzzle de diagnóstico obrigatório. O antigo mini-reparo em primeira pessoa pode existir como **atividade opcional** que
  economiza dinheiro.
- Pessoas: hóspede VIP exigente, briga, doença, greve, funcionário em crise, concorrente sabotando.
- Cidade: apagão, protesto, obra bloqueando a avenida, festival.

### 5.7 Concorrência e mercado
Pousadas e hotéis da Cidade Antiga e da Expansão competem por hóspedes. Preços e reputação deles variam. Possibilidade de comprar,
parceria ou superar. Um rival narrativo opcional (a "Rede Vértice") expande pela costa.

## 6. Progressão

### 6.1 Fases (campanha livre, ~30–50 h)
| Fase | Marco | Desbloqueios |
|---|---|---|
| 1. Reabrir | Pousada com 6 quartos, 1 funcionário, praia pública | Operação básica, primeiros hóspedes econômicos |
| 2. Pousada | 20 quartos, restaurante, quiosque, 1,5 estrelas | Equipe, fornecedores da Cidade Antiga, banco |
| 3. Hotel | 60 quartos, piscina, spa, 3 estrelas | Famílias, eventos pequenos, Praia do Farol |
| 4. Complexo | Marina, salão de eventos, bangalôs, 4 estrelas | Corporativo, Zona Empresarial, Distrito Tecnológico |
| 5. Resort | All inclusive, anfiteatro, farol, heliponto, 5 estrelas | Luxo, celebridades, Praia do Cais |
| 6. Legado | Segundo resort, fundação, cidade turística | Expansão, modo livre, metas de legado |

### 6.2 Liberdade
Depois da fase 2 o jogador escolhe o estilo: luxo exclusivo, resort familiar, turismo de aventura, negócios, festa, eco-resort,
vida noturna. Cada estilo muda hóspedes, edifícios, eventos e metas.

### 6.3 Campanha e mercado livre
- **Campanha narrativa** (a herança da pousada, os sócios, o rival, o segredo do terreno): capítulos que abrem opções e dão recursos.
- **Modo livre**: metas abertas, objetivos sazonais, desafios (ex.: sobreviver à temporada baixa).

## 7. Dificuldade recuperável
- Dificuldade vem de **gestão** (fluxo de caixa, escala, reputação), não de falha cega.
- Toda crise dá **aviso** e **pelo menos uma saída** pagável.
- "Reestruturação": se o caixa zera, o banco assume parte do resort, o jogador mantém um núcleo e reinicia a fase com uma cicatriz de
  reputação. Nunca game over.
- Níveis: Tranquilo (sem crises graves), Padrão, Exigente (crédito caro, concorrência agressiva).
- Auto-save, voltar ao dia anterior (limitado), explicação visível de **por que** a nota caiu.

## 8. Mundo e ativos necessários

### 8.1 Já existe
Orla (massing), Cidade Antiga, masterplan, veículos, vegetação, pedestres e banhistas (baixa/média), cenário noturno.

### 8.2 A criar (por prioridade)
1. **Terreno da pousada e entorno** na Orla (recorte W5 em andamento: transição Cidade Antiga ↔ Orla, `W5S`).
2. **Kit modular do resort**: paredes, pisos, fachadas, janelas, varandas, telhas, pergolados, decks, bangalôs. PBR autoral.
3. **Quartos**: 6 tipologias com móveis e decoração em variantes (~150 itens), prontos para uso no catálogo.
4. **Áreas comuns**: recepção, restaurante, cozinha, bar, piscina, spa.
5. **Pessoas**: kit de personagens (corpo, rosto, cabelo, roupas) com **animações**: andar, sentar, servir, limpar, nadar, tomar sol,
   conversar. Hoje as figuras são de baixa/média complexidade; este é o item de arte de **maior risco**.
6. **UI**: tablet/painel de gestão, catálogo, mapa de calor, finanças, avaliações. Migrar o `TabletUI` provisório para UI Toolkit.
7. **Áudio**: ondas, vento, restaurante, quarto, piscina, multidão.
8. **Textos**: avaliações, diálogos e eventos (geração composicional + escrita autoral nas cenas de campanha).

### 8.3 Princípio visual
Realismo caloroso de litoral: luz do sol baixo, sal, vento, madeira e pedra, vegetação tropical. Não low-poly, não cartunesco.

## 9. Prólogo e primeiras horas
1. **Chegada**: o protagonista recebe a pousada abandonada do tio (ou sócio) numa tarde de ressaca, com 30 mil e uma dívida pequena.
2. **Limpeza guiada** (primeira pessoa): abrir portas, varrer, abrir os quartos, arrumar a recepção. Ensina andar, interagir e o Modo Planta.
3. **Primeiro hóspede**: um mochileiro que sobrou do último ônibus. Check-in, quarto, café da manhã, check-out, primeira avaliação.
4. **Primeira semana**: comprar suprimentos na Cidade Antiga, contratar a primeira funcionária, consertar o letreiro (mini-tarefa),
   decidir o que construir com os primeiros 10 mil.
5. Fim do prólogo: pousada com nota aberta, 3 quartos úteis, meta de reabrir 6.

## 10. Plano de produção técnica

### 10.1 Marcos (substituem a lista antiga de "Próximas tarefas")
| Marco | Entrega | Critério de aceite |
|---|---|---|
| **R0 — Decisão e documentação** | Este GDD, decisões registradas, conflitos resolvidos | Usuário aprova o escopo e os itens [DECIDIR] |
| **R1 — Terreno jogável da Orla** | Importar Orla + Cidade Antiga sul na Unity, streaming, colisão, câmera dupla | Andar do prédio-pousada à praia e ao centro, sem quedas e sem interromper |
| **R2 — Vertical slice da Pousada** | 1 prédio de 6 quartos + recepção + quiosque em alta fidelidade, interiores decorados | Captura real do jogo e perfil de desempenho |
| **R3 — Núcleo de simulação** | Hóspede, quarto, reserva, equipe mínima, finanças, tempo, avaliação | Simulação headless: 30 dias sem erro, saldo coerente |
| **R4 — Construção** | Grade de lotes, catálogo, colocação, remoção, validação de regras | Montar e demolir sem corromper o save |
| **R5 — Loop jogável** | Prólogo + primeira semana + fases 1–2 | Partida de ~3 h do início ao hotel de 20 quartos |
| **R6 — Cidade viva** | Fornecedores, contratação, concorrentes e eventos ligados aos distritos | Cada distrito aberto muda algo mensurável |
| **R7 — Expansão e polimento** | Fases 3–6, estilos, eventos, áudio, UI final | Gate visual e de desempenho |

### 10.2 Arquitetura de código (resumo)
- **Dados**: ScriptableObjects/JSON versionados para tipologias, itens, hóspedes, eventos. IDs estáveis (como hoje).
- **Simulação**: núcleo determinístico, independente de GameObjects (permite testes em lote e acelerar o tempo).
- **Apresentação**: agentes (hóspedes/equipe) representados por GameObjects e *job system* para movimentação em massa; navegação com
  NavMesh por streaming.
- **Save**: sem serializar GameObjects. Versão nova do save (`resortDataVersion`), migrando só o essencial do v1 (dinheiro, nome, flags).
  Nunca sobrescrever saves do usuário nos testes.
- **Estrutura de pastas**: `Assets/_Game/Scripts/Resort/` (Sim, Build, Guests, Staff, Economy, UI). O código de manutenção permanece
  em `Core/` até uma decisão de remoção.

### 10.3 Desempenho
Meta (a validar, não afirmada): 60 fps em hardware médio com ~150 agentes ativos visíveis, streaming por subcélulas, LOD/HLOD, instancing,
simulação de baixa frequência para agentes distantes.

### 10.4 Riscos e mitigação
| Risco | Mitigação |
|---|---|
| Escopo enorme (construção + simulação + arte + animação) | Marcos pequenos com gates; vertical slice antes de expandir |
| Pessoas de qualidade final | Pipeline de personagens ainda ausente; decidir ferramenta e contratar/comprar assets licenciados (R2) |
| Agentes em massa em primeira pessoa | Dois níveis de detalhe: perto (animado), longe (impostores/simulação abstrata) |
| Simulação desbalanceada | Testes headless e planilhas de balanceamento antes do polimento |
| Perda da identidade do projeto | Manter a cidade, a lore e o realismo; o resort entra como motor de progressão |
| Saves antigos | Migração mínima, testada; save v1 continua carregável |

## 11. Itens a decidir
1. **[DECIDIR] Câmera principal**: primeira pessoa com Modo Planta (recomendado) ou vice-versa.
2. **[DECIDIR] Tom**: realista-cálido (recomendado) ou mais leve e cômico.
3. **[DECIDIR] Narrativa**: manter a lore existente (Guto, Helena, Vértice) como elenco do resort, ou nova história.
4. **[DECIDIR] Pessoas**: assets licenciados de personagens (rápido) ou criação autoral (lento, mais controle).
5. **[DECIDIR] Multijogador/cooperativo**: fora do escopo por padrão (single-player).
6. **[DECIDIR] Destino do código de manutenção**: congelar (recomendado) ou remover.
