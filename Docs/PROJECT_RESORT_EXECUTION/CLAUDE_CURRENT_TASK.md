# PROJECT RESORT — Tarefa Atual do Claude

Atualizado em 2026-10-06.

## Fase atual

**Fase 02 — Vertical Slice do Quiosque**

A Fase 01 está concluída. A Fase 03 ainda NÃO está liberada.

## Estado confirmado

O bloco novo da Fase 02 já contém trabalho local para:

- praia viva / população ambiente;
- NPCs com pooling e LOD;
- casais, famílias, grupos, corredores, ciclistas, banhistas, crianças e nadadores;
- clientes do quiosque usando o novo rig;
- ciclo dia -> pôr do sol -> noite;
- sol, lua, estrelas, névoa e ambiente;
- iluminação de calçadão, quiosque e casa;
- geladeira, freezer e prateleiras ligados ao estoque;
- clientes podendo sentar e consumir;
- testes em `LivingWorldTests.cs`;
- captura automatizada planejada para dia/tarde/pôr do sol/noite.

Esse bloco foi **compilado com sucesso no Unity 6000.6.2f1** em 2026-10-06 quando o UPM foi iniciado corretamente. Ainda precisa de execução dos testes, correções de runtime e validação visual.

## Próxima sequência obrigatória

1. Rodar `Tools/Autonomy/Run-UnityResortTests.ps1`.
2. Corrigir qualquer falha real de compilação/teste/runtime.
3. Validar a praia viva e o comportamento dos NPCs.
4. Validar o ciclo dia/noite e a iluminação noturna.
5. Gerar capturas reais da Unity, incluindo dia e noite.
6. Colocar cópias das capturas aprovadas em `C:\Users\sergi\Desktop\Capturas PROJECT RESORT\01_Unity_Reais\`.
7. Corrigir a composição da praia: o estado atual reporta cerca de 170 m entre quiosque e mar, muito maior que a direção visual. Trabalhar para uma composição costeira mais convincente, preservando layout futuro e sem quebrar estágios. Registrar a distância final.
8. Adicionar/validar vida ambiental básica que couber na fase: ondas/movimento do mar, vento/vegetação, aves e áudio ambiente básico, sem inflar escopo.
9. Rodar regressão do loop completo: casa -> praia -> abrir -> estoque -> atender/vender -> fechar -> caixa -> casa -> dormir -> save/load.
10. Medir desempenho com a população ativa.
11. Atualizar `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md`.
12. Commit/push de blocos validados.
13. Manter `HUMAN_GATE_PENDING` até o usuário jogar a fase e aprovar ritmo/clareza/diversão.

## O que NÃO fazer agora

- não iniciar a Fase 03;
- não construir pousada;
- não construir hotel;
- não construir resort final;
- não implementar dezenas de quartos;
- não expandir escopo para endgame;
- não chamar primitivas/blockout de arte final;
- não marcar gate visual como PASS só porque os testes técnicos passaram.

## Critério para encerrar a rodada atual

Deixar a Fase 02 tecnicamente estável, visualmente muito mais viva, com evidências reais da Unity, relatório atualizado, commits enviados e somente o gate humano explicitamente pendente se for o único bloqueio restante.
