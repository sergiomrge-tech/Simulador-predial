# PROJECT RESORT — Tarefa Atual do Claude

Atualizado em 2026-10-06 (fim da rodada 3 de refinamentos seguros da Fase 02).

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
- Relatório: `RELATORIO_02_VERTICAL_SLICE_QUIOSQUE.md` (adendos 1, 2 e 3 de 2026-10-06).

## Pendente (nada disso se resolve só com código)

1. **HUMAN_GATE_PENDING**: uma pessoa precisa jogar dois dias e avaliar ritmo, clareza do HUD, diversão e a "vida" da praia; ouvir o áudio; olhar as capturas.
2. Gate visual segue aberto: personagens/quiosque/guarda-sóis ainda são blockout; mar com shader simples (sem refração/reflexo de objetos); noite com céu preto e estrelas.

## Trabalho seguro dentro da Fase 02 (se a rodada continuar antes do gate humano)

- ~~Clientes sentarem nas mesas no estágio 2~~ (feito). ~~HUD de próximo passo~~ (feito; falta olhar humano).
- Corrigir no Blender (`Tools/Blender/sa_stages.py::kiosk`) a mesa oeste a 7 m que cai dentro do bloco de banheiros e então reativar essa mesa em `StallLayout.AddKioskSeats` (exige o `.blend` base e regenerar/re-exportar o FBX do estágio 2).
- Sentar/deitar/nadar ainda são procedurais: avaliar clipes gratuitos (Human Crafting Animations FREE, Creative Characters FREE) e o aspecto dos corpos animados; se os manequins ainda parecerem artificiais de perto, o Diretor deve apresentar 1–3 opções pagas ao usuário antes de comprar qualquer coisa.
- Refinar o rig/roupas dos NPCs; mar sem espuma de profundidade/reflexos de objetos e céu noturno preto sem gradiente (cosmético); mais variedade de atividades na areia.
- Equilíbrio fino da fila/spawn só com dados de jogada humana (curva atual: 6–8h quase sem clientes; o teste `FirstDayDemandIsWorthPlayingAndProfitable` protege a faixa).

## Próxima ação concreta

Pedir a uma pessoa que jogue dois dias (`ResortPrologue`), anote ritmo/HUD/diversão/áudio e olhe as capturas F02. Só então avaliar o gate humano; sem isso, a Fase 03 permanece bloqueada.

## O que NÃO fazer

- não iniciar a Fase 03;
- não construir pousada/hotel/resort novos;
- não chamar blockout de arte final;
- não marcar o gate visual/humano como PASS sem uma pessoa jogar.
