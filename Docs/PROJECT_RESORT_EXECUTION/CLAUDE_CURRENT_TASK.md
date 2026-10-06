# PROJECT RESORT — Tarefa Atual do Claude

Atualizado em 2026-10-06 (fim da rodada de validação da Fase 02).

## Fase atual

**Fase 02 — Vertical Slice do Quiosque** — gate técnico **PASS**; **HUMAN_GATE_PENDING** (jogada humana).

A Fase 03 NÃO está liberada.

## Estado real (verificado no Unity 6000.6.2f1, modo gráfico)

- 15/15 testes de PlayMode passam (`Tools/Autonomy/Run-UnityResortTests.ps1 -Graphics`), sem erros no console.
- Loop completo (casa → praia → abrir → estoque → atender → fechar → caixa → casa → dormir → save/load) coberto por `LoopTests`/`PrologueDayTests` e passando.
- Praia viva (67–72 pessoas ao meio-dia, LOD/pooling), ciclo dia/pôr do sol/noite com lâmpadas, ondas, gaivotas, palmeiras ao vento, áudio ambiente procedural.
- Mar a 55,1 m do quiosque (antes ~165 m), via `BEACH_WATER_DZ` em `Tools/Map/export_resort_site.py`.
- Desempenho (render em lote, sem IMGUI): ~2,8 ms/quadro com a multidão; estágio 7 ~2,9 ms.
- Capturas reais: `ArtSource/Blender/World/Reviews/F02/` e `Desktop\Capturas PROJECT RESORT\01_Unity_Reais\F02_praia_viva_dia_noite\`.
- Relatório: `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md` (adendo de 2026-10-06).

## Pendente (nada disso se resolve só com código)

1. **HUMAN_GATE_PENDING**: uma pessoa precisa jogar dois dias e avaliar ritmo, clareza do HUD, diversão e a "vida" da praia; ouvir o áudio; olhar as capturas.
2. Gate visual segue aberto: personagens/quiosque/guarda-sóis ainda são blockout; mar sem shader de água; noite sem contraste de arte.

## Trabalho seguro dentro da Fase 02 (se a rodada continuar antes do gate humano)

- Clientes sentarem nas mesas também no estágio 2 (quiosque exportado).
- Melhorar a leitura do HUD do quiosque (fila, pedido, caixa) sem aumentar escopo.
- Refinar o rig/roupas dos NPCs e o shader/cor do mar; mais variedade de atividades na areia.
- Ajustar fila/spawn de clientes por horário e reputação (equilíbrio, não novos sistemas).

## O que NÃO fazer

- não iniciar a Fase 03;
- não construir pousada/hotel/resort novos;
- não chamar blockout de arte final;
- não marcar o gate visual/humano como PASS sem uma pessoa jogar.
