# PROJECT RESORT — Tarefa Atual do Claude

Atualizado em 2026-10-06 (rodada 19: estado idêntico ao da rodada 18 — HEAD == origin, mesmos 6 pacotes na biblioteca, sem código novo; aguardando jogada humana).

## Fase atual

**Fase 02 — Vertical Slice do Quiosque** — gate técnico **PASS**; **HUMAN_GATE_PENDING** (jogada humana).

A Fase 03 NÃO está liberada.

## Estado real (verificado no Unity 6000.6.2f1, modo gráfico)

- 20/20 testes de PlayMode passam (`Tools/Autonomy/Run-UnityResortTests.ps1 -Graphics`), sem erros no console.
- Loop completo (casa → praia → abrir → estoque → atender → fechar → caixa → casa → dormir → save/load) coberto por `LoopTests`/`PrologueDayTests` e passando.
- Praia viva (67–72 pessoas ao meio-dia, LOD/pooling), ciclo dia/pôr do sol/noite com lâmpadas, ondas, gaivotas, palmeiras ao vento, áudio ambiente procedural.
- Pessoas próximas e médias usam os manequins animados do *Human Basic Motions FREE* (idle/caminhar/correr/conversar), pintados por região; pacote só local (`ThirdParty/`, git-ignorado), com fallback procedural.
- Mar a 55,1 m do quiosque (antes ~165 m), via `BEACH_WATER_DZ` em `Tools/Map/export_resort_site.py`.
- Desempenho (render em lote, sem IMGUI): ~2,8 ms/quadro com a multidão; estágio 7 ~2,9 ms.
- Capturas reais: `ArtSource/Blender/World/Reviews/F02/` e `Desktop\Capturas PROJECT RESORT\01_Unity_Reais\F02_praia_viva_dia_noite\`.
- Rodada 2 (feita): clientes sentam nas mesas do deck do quiosque do estágio 2 (10 cadeiras, rota própria, altura do deck); HUD com faixa de "próximo passo" + estoque baixo + ABERTO/FECHADO + vendas do dia; guarda de balanceamento do primeiro dia. Captura: `f02_7_estagio2_clientes_no_deck.png`.
- Rodada 3 (feita): mar com shader próprio (`Resources/ResortSea.shader`: cor por profundidade, ondulação, Fresnel, brilho) e malha que segue a linha d'água; céu noturno sem o brilho amarelo (o sol agora desce abaixo do horizonte). 20/20 testes, sem regressão de desempenho (2,8 ms).
- Rodada 4 (feita): céu com shader próprio (`Resources/ResortSky.shader`): crepúsculo violeta e noite azul-marinho com estrelas no lugar do oliva/preto; 20/20 testes, 0 erros de shader.
- Rodada 5 (feita): nuvens procedurais no shader do céu (`ResortSky.shader`, cor por hora, cobertura maior com clima nublado); 20/20 testes, 0 erros de shader.
- Rodada 6 (feita): duplas jogando bola na areia (`BeachLife.Role.Player`, `Gesture.Hit`, `Mix.Players`); 20/20 testes, 0 erros de shader/compilação. Captura: `f02_8_bola_na_areia.png`.
- Rodada 7 (feita): vendedor ambulante com caixa de isopor andando pela areia (`BeachLife.Role.Vendor`, `Mix.Vendors`); 20/20 testes, 0 erros de shader/compilação. Captura: `f02_9_vendedor_na_areia.png`.
- Rodada 8 (feita): banhistas sentados lendo um livro (`Gesture.Read`, ~35% dos que se sentam; livro só em LOD 0–1); 20/20 testes, 0 erros de shader/compilação. Captura: `f02_10_leitor_na_areia.png`.
- Desempenho remedido após as rodadas 6–8 (adendo 9): praia ao meio-dia 2,8 ms média / 3,7 ms pior, estágio 7 2,5–3,0 ms; sem regressão.
- Rodada 10 (feita): HEAD revalidado (20/20, 0 erros); decidido NÃO regenerar o estágio 2 no Blender só pela mesa do banheiro (débito cosmético, Fase 15).
- Rodada 11 (feita): só documentação — `ROTEIRO_PLAYTEST_HUMANO_FASE_02.md` para o humano fechar o gate (sem mudança de código; HEAD e remoto já sincronizados, 20/20 da rodada 10 continua válido).
- Rodada 12 (feita): reauditoria — branch `claude/w1-masterplan`, HEAD == origin (0/0), todos os itens de população/atividades/dia-noite da fase 02 já cobertos no código; nenhum código novo seguro restante que não seja cosmético. 43 PNGs de `Reviews/{F02,R2,R4,R5}` aparecem modificados: são capturas regeneradas pela rodada 10 (execução real da Unity), mantidas só locais/não commitadas para não inflar o histórico; podem ser commitadas se o humano quiser as versões atuais.
- Rodada 13 (feita): reconfirmação — HEAD == origin/claude/w1-masterplan (0/0); desde a última validação Unity (rodada 10, 20/20) só houve commits de documentação (`git diff --name-only 4df7a13 HEAD` fora de `Docs/` vazio), então a validação continua válida e não foi reexecutada. Nenhum código novo seguro restante; os 43 PNGs modificados seguem só locais.
- Rodada 14 (feita): reconfirmação sem mudança de código — HEAD == origin (0/0); `git status` fora de `Reviews/` está limpo (só os 43 PNGs regenerados, locais); nenhum commit novo desde a rodada 13, então a validação Unity da rodada 10 (20/20) segue válida. Nenhum trabalho seguro e não cosmético restante na Fase 02; Fase 03 continua bloqueada pelo gate humano.
- Rodada 15 (feita): reconfirmação — HEAD == origin/claude/w1-masterplan (0/0) após `git fetch`; nenhum arquivo fora de `Reviews/` modificado; nenhum commit de código desde a validação Unity da rodada 10 (20/20), que segue válida. Sem trabalho seguro e não cosmético restante; **parar de repetir rodadas de reconfirmação até haver jogada humana ou nova instrução**.
- Rodada 16 (feita): HEAD == origin (0/0) após `git fetch`; nenhum arquivo fora de `Reviews/` modificado; nenhum commit de código desde a rodada 10 (20/20 válido, Unity não reexecutada). A biblioteca local `D:\ProjectResort_AssetLibrary\UnityFree\Packages` só contém Human Basic Motions FREE, Environment Pack Forest Sample e pacotes de fantasia: **Human Crafting Animations FREE / Creative Characters FREE / MC Sample ainda não foram baixados** (o usuário precisa adicioná-los à conta/cache), então sentar/deitar/nadar seguem procedurais. Sem trabalho seguro novo; a próxima rodada só deve ocorrer após jogada humana, novos pacotes na biblioteca ou nova instrução.
- Rodada 17 (feita): `git fetch` — HEAD == origin (0/0), nada novo fora de `Reviews/`, biblioteca de assets inalterada (mesmos 6 pacotes), nenhum commit de código desde a rodada 10 (20/20 válido). Nenhuma ação segura nova; Unity não reexecutada. **Bloqueio real: jogada humana (`ROTEIRO_PLAYTEST_HUMANO_FASE_02.md`) ou novos pacotes/instrução.**
- Rodada 18 (feita): `git fetch` — HEAD == origin (0/0), nada novo fora de `Reviews/`, biblioteca de assets com os mesmos 6 pacotes; nenhuma mudança de código ou validação nova. Estado idêntico ao da rodada 17. Não há trabalho seguro novo; **parar até haver jogada humana, novos pacotes na biblioteca ou nova instrução do Diretor**.
- Relatório: `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md` (adendos 1 a 10 de 2026-10-06).

## Pendente (nada disso se resolve só com código)

1. **HUMAN_GATE_PENDING**: uma pessoa precisa jogar dois dias e avaliar ritmo, clareza do HUD, diversão e a "vida" da praia; ouvir o áudio; olhar as capturas.
2. Gate visual segue aberto: personagens/quiosque/guarda-sóis ainda são blockout; mar com shader simples (sem refração/reflexo de objetos); céu com nuvens só cosméticas; noite sem reflexo de objetos na água.

## Trabalho seguro dentro da Fase 02 (se a rodada continuar antes do gate humano)

- ~~Clientes sentarem nas mesas no estágio 2~~ (feito). ~~HUD de próximo passo~~ (feito; falta olhar humano).
- ~~Mesa oeste do banheiro no Blender~~ (adiado para a Fase 15: exige regenerar os 7 estágios + todos os FBX; `AddKioskSeats` já pula a mesa).
- Sentar/deitar/nadar ainda são procedurais: avaliar clipes gratuitos (Human Crafting Animations FREE, Creative Characters FREE) e o aspecto dos corpos animados; se os manequins ainda parecerem artificiais de perto, o Diretor deve apresentar 1–3 opções pagas ao usuário antes de comprar qualquer coisa.
- Refinar o rig/roupas dos NPCs; mar sem espuma de profundidade/reflexos de objetos (cosmético); mais variedade de atividades na areia (feito: duplas jogando bola; feito: vendedor ambulante; feito: leitores sentados; faltam p.ex. cachorro, pessoas dormindo sob guarda-sol; opcionais, exigem rig/clipes novos).
- Equilíbrio fino da fila/spawn só com dados de jogada humana (curva atual: 6–8h quase sem clientes; o teste `FirstDayDemandIsWorthPlayingAndProfitable` protege a faixa).

## Próxima ação concreta

Pedir a uma pessoa que jogue dois dias (`ResortPrologue`) seguindo `ROTEIRO_PLAYTEST_HUMANO_FASE_02.md` (roteiro + ficha de avaliação, criado na rodada 11), anote ritmo/HUD/diversão/áudio e olhe as capturas F02. Só então avaliar o gate humano; sem isso, a Fase 03 permanece bloqueada.

## O que NÃO fazer

- não iniciar a Fase 03;
- não construir pousada/hotel/resort novos;
- não chamar blockout de arte final;
- não marcar o gate visual/humano como PASS sem uma pessoa jogar.
