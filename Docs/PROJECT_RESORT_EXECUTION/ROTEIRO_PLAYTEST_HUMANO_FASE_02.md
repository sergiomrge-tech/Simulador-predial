# Roteiro de playtest humano — Fase 02 (vertical slice do quiosque)

Este roteiro serve para fechar o `HUMAN_GATE_PENDING` da Fase 02. Ele só vale se uma pessoa real jogar com teclado e mouse e preencher a ficha no fim. Nenhum campo pode ser preenchido por automação ou por suposição.

O gate técnico já é PASS (20/20 PlayMode, ver `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md`). Este roteiro avalia o que testes não medem: ritmo, clareza, diversão, "vida" da praia, áudio e aparência.

## Preparação

1. Abrir o projeto `FacilityOps` na Unity 6000.6.2f1 e abrir `Assets/_Game/Scenes/ResortPrologue.unity`.
2. Dar Play (aba Game em tela cheia, resolução 1920x1080 ou maior, modo gráfico real, sem `-batchmode`).
3. Fones de ouvido ligados: o áudio ambiente é procedural e ainda não foi ouvido por uma pessoa.
4. Não apagar o save do jogador. Para começar do zero sem perder progresso, renomear `ResortAurora/save_v1.json` dentro de `Application.persistentDataPath` (por exemplo para `save_v1.json.bak`) antes de jogar e restaurar depois.

## Controles (os mesmos de F1 no jogo)

| Tecla | Ação |
|---|---|
| WASD / mouse | andar / olhar |
| Shift | correr |
| E | usar o objeto em foco (segurar E na chapa) |
| F1 | ajuda "Como jogar" |
| Esc | fechar painel |

## Roteiro (duas sessões, ~15–20 min cada, sem ajuda de quem desenvolveu)

**Dia 1**
1. Sair de casa e achar o quiosque sem instruções externas. Anotar quanto tempo levou e se a faixa de "próximo passo" bastou.
2. Comprar estoque na caixa do fornecedor e ajustar preços.
3. Abrir o quiosque na placa.
4. Atender pelo menos 8 clientes: anotar pedido no balcão, preparar na chapa (segurar E), entregar.
5. Deixar o dia fechar, conferir o caixa/resumo, voltar para casa e dormir.
6. Confirmar que o dinheiro e a reputação do dia aparecem no HUD.

**Save/load**
7. Sair do Play, abrir de novo e conferir que dinheiro, dia, estoque e reputação voltaram como estavam.

**Dia 2**
8. Repetir o ciclo tentando ir melhor. Avaliar se há uma razão clara para jogar o dia 2 (contratar ajudante no mural, melhorar a barraca).

**Observação livre (5 min)**
9. Andar pelo calçadão e pela areia por volta de 12h, 18h20 e 20h30 (dia, pôr do sol, noite). Olhar mar, céu, banhistas, jogadores de bola, vendedor ambulante, leitores, lâmpadas e palmeiras.
10. Ouvir o áudio: mar, gaivotas, vento, movimento da praia, mudança à noite.

## Ficha de avaliação (nota 1–5 + comentário curto)

Preencher no fim, com data e nome/apelido de quem jogou.

| Item | Nota | Comentário |
|---|---|---|
| Achei o que fazer sem ajuda (faixa de próximo passo, placas) | | |
| Ritmo do dia (espera de clientes, 6–8h quase vazias, pico) | | |
| Atender/preparar/entregar é divertido ou repetitivo | | |
| Clareza do HUD (barra de status, estoque baixo, ABERTO/FECHADO) | | |
| Dinheiro/reputação dão sensação de progresso | | |
| Vontade de jogar o dia 2 | | |
| A praia parece viva (nunca vazia) | | |
| Pessoas parecem plausíveis (sem flutuar, sem clones óbvios) | | |
| Dia → pôr do sol → noite: leitura e beleza | | |
| Áudio ambiente | | |
| Aparência geral (aceitável como blockout melhorado?) | | |
| Desempenho percebido (travadas?) | | |
| Save/load funcionou | sim / não | |

Também anotar: bugs vistos, onde ficou perdido, o que mais incomodou e o que mais agradou.

## Como o resultado destrava (ou não) a Fase 03

- Itens de gameplay (ritmo, clareza, diversão, save/load) com média >= 3 e nenhum bug bloqueante: gate humano de **jogabilidade** pode ser marcado PASS.
- Itens visuais/áudio com nota <= 2: o gate visual continua aberto e vira lista de correções dentro da Fase 02 (ou débito explícito para a Fase 15, por decisão do Diretor).
- O Diretor decide o PASS final; a Fase 03 só é liberada depois que o resultado for registrado em `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md` e em `CLAUDE_CURRENT_TASK.md`.
