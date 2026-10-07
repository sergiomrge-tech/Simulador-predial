# Relatório — Fase 02: Vertical slice do quiosque

Data: 2026-10-06. Gate: **PASS em teste automatizado; pendente: sessão humana com teclado e mouse.**

## Loop entregue
casa (Apto 12, a ~150 m do quiosque) → praia → **abrir** o quiosque (placa verde no balcão) → conferir estoque (caixa do fornecedor) → atender → vender → receber → **fechar** o quiosque/caixa (placa ou 22:00) → resumo do dia (fechamento de caixa, salva) → voltar para casa → **dormir** na cama do Apto 12 → manhã seguinte na porta de casa.

## O que foi feito nesta fase
- **Produtos** (data-driven em `Sim/Catalog.cs`): água, refrigerante, suco/água de coco, cerveja, lanche, salgado, milho e picolé (os seis mínimos + dois).
- **Abrir/fechar**: o quiosque só recebe clientes aberto; fechar encerra o dia assim que a fila é atendida. O dia nunca começa aberto.
- **Casa e dormir**: kitnet modelada (porta de 2,5 m, cozinha, mesa, cama, banheiro, guarda-roupa), cama como interação "Dormir", disponível só depois do fechamento. O Lar foi aproximado da praia (150 m) para a rotina caber.
- **Save**: o fechamento salva com `dayClosed`; recarregar retoma na manhã seguinte sem repetir o dia (dinheiro, estoque, reputação e dia preservados).
- Mercado (HUD) compactado para caber 8 produtos e 4 melhorias.

## Verificação (PlayMode, `LoopTests`, 8 testes no total passando)
Dois dias consecutivos completos (um fechado pela placa às ~17h, outro pelo relógio), cada um com abertura, estoque, atendimento, fechamento de caixa, ida para casa, sono e novo dia; depois recarga da cena confirmando dia, dinheiro, estoque e reputação. Capturas reais da Unity em `ArtSource/Blender/World/Reviews/R5/`.

## Limitações
- Sem sessão humana: o ritmo, a clareza do HUD e a vontade de repetir o dia não foram avaliados por uma pessoa (o gate de diversão da fase 02 precisa disso).
- O jogo ainda não tem noite visual completa nem sono animado; a UI é IMGUI provisória.
- A geladeira/freezer e as prateleiras do quiosque são decorativas (o estoque vive no modelo de dados).
- Aprovação da fase 02 para avançar à 03 depende de uma sessão humana curta.

---

# Adendo — praia viva, dia/noite, costa ambiente e quiosque da REF 01/02 (2026-10-06)

**Status: COMPILADO, TESTADO (17/17 PlayMode, Unity 6000.6.2f1, modo gráfico) e CAPTURADO. Gate técnico: PASS. Gate humano: `HUMAN_GATE_PENDING`. Gate visual: aberto até uma pessoa avaliar (a cena ainda é blockout).**

## Evidência real (execução da Unity)
- Comando: `Tools/Autonomy/Run-UnityResortTests.ps1 -Graphics` -> `TESTS total=17 passed=17 failed=0`. Logs em `D:\ProjectResort_Autonomy\logs\`.
- Console: sem erros nem exceções na execução final.
- Capturas reais da Unity (cópias também em `Desktop\Capturas PROJECT RESORT\01_Unity_Reais\F02_praia_viva_dia_noite\`): `ArtSource/Blender/World/Reviews/F02/f02_{1_dia,2_tarde_dourada,3_por_do_sol,4_noite}_{kiosque_da_calcada,praia_para_o_mar,mesas_na_areia,calcadao_leste,aerea}.png` e `f02_5_ondas_e_gaivotas.png`.

## O que cada requisito da fase mostra hoje
| Requisito | Resultado medido |
|---|---|
| Praia e calçadão ocupados | Meio-dia: 67–72 pessoas ativas (≈34 passeando, 26 na areia, 8 na água, 3 ciclistas); noite: 4–5 no calçadão; manhã (6h): 16–18 incl. 3 corredores. |
| Atividades variadas | Papéis vistos: caminhante, ciclista, banhista (deita/senta), criança, nadador. Casais, famílias e grupos pelo calçadão. |
| Clientes usando o quiosque | Fluxo do loop (LoopTests) + clientes servidos sentam em mesa, bebem e saem (teste dedicado). |
| Sem flutuar/afundar | Teste confere a altura de cada pessoa ao terreno (nadadores à superfície ou no fundo raso). |
| Densidade sem custo | Render do ponto de vista da praia: média 2,8 ms (~360 fps), p95 3,1 ms, pior 3,7 ms com ~67 pessoas, LOD [11, 56, 0, 0], 18 lâmpadas. Estágio 1 a nível do chão 2,6 ms; estágio 7 (217 copas de palmeira divididas) 2,3–2,9 ms. *Medido com `Camera.Render` em lote nesta máquina, sem a UI IMGUI; não é FPS de um jogo completo em hardware-alvo.* |
| Dia -> pôr do sol -> noite | Luminância média dos quadros (0–1): dia 0,65–0,76; tarde dourada 0,47–0,58; pôr do sol 0,23–0,30; noite (20h30) 0,20–0,24. Sol, lua, estrelas, névoa e ambiente seguem o relógio; 18 lâmpadas (calçadão, quiosque, casa) acendem à noite com pool de 8 luzes reais. |
| Noite legível | Capturas noturnas mostram quiosque e calçadão iluminados; não é preto nem estourado (testes de luminância). Ainda é uma noite azul-ardósia plana: falta contraste de arte. |
| Distância quiosque–mar | **55,1 m** (antes ~165 m). Perfil comprimido no exportador do terreno; calçadão a 62 m do mar. |
| Ondas | 5 linhas de espuma entram, perdem velocidade e se desfazem ao longo da linha d'água (alfa de pico 0,3+ verificado em teste). |
| Vento/vegetação | Copas de palmeira divididas do mesh soldado (54 no estágio 1; 217 no estágio 7) e balançando; ângulo máximo medido > 0,2 graus. |
| Aves | 9 gaivotas voando de dia (>= 6 verificadas), recolhidas à noite. |
| Áudio | Mar (segue o jogador ao longo da costa), vento, murmúrio da multidão (escala com a população), grilos à noite, gritos de gaivota. Sintetizado em código (placeholder); clipes normalizados (pico 0,85), sem clipping. |

## Decisões e correções desta rodada
- **Praia estreitada** (decisão antes pendente): `BEACH_WATER_DZ = 114` no exportador desloca a linha d'água para dentro; calçadão, avenida, parcelas e lotes não mudaram de posição. Alturas re-exportadas; os testes de alinhamento de peças e estágios continuam passando. Os estágios futuros (marina, ponta do farol) herdam o perfil novo; reavaliar nas fases 05/09.
- **Guarda-sóis pretos**: a malha dupla-face dividia vértices e as normais se anulavam; agora topo e fundo têm vértices próprios.
- **Marcadores de terreno** (linhas vermelhas): mais finos e só aparecem a até 70 m da parcela.
- Teste de nadadores tinha intervalo inválido (`from > to`) quando o fundo estava acima de 0,05 m; corrigido.

## Corpos animados (Human Basic Motions FREE) — adicionado depois do primeiro fechamento da rodada
Seguindo `Docs/ASSET_LIBRARY/UNITY_FREE_ASSETS.md` (prioridade A): pessoas próximas e médias passam a usar os manequins humanoides do pacote gratuito *Human Basic Motions FREE* (Kevin Iglesias, Unity Asset Store) com os clipes reais de idle, caminhada, corrida e conversa, sobre a lógica existente do `BeachLife` (não foi trocada).
- **Código**: `Game/HumanVisual.cs` (novo) + integração em `Game/PersonRig.cs` (`TryHuman`). Um `PlayableGraph` em tempo de execução mistura os clipes (sem Animator Controller); o manequim é "vestido" por pintura: uma cópia da malha por gênero tem os UVs remapeados por região do corpo (tronco, mangas, bermuda/calça, canelas, sapatos, cabelo) e cada pessoa recebe uma paleta de 12 pixels. Custo: 1 material e nenhum renderer extra por pessoa.
- **Regras**: caminhar, correr, parar e conversar usam o corpo animado quando LOD <= 1 e há menos de 40 ativos (`HumanVisual.MaxActive`); sentar, deitar, nadar, pedalar e gestos de celular/bebida continuam procedurais (o pacote não tem esses clipes). LOD 2+ volta ao corpo procedural simplificado. Animators ficam em `AlwaysAnimate` porque animators culled congelam o grafo (verificado: o tempo do clipe não avançava).
- **Licença / repositório**: os arquivos do pacote ficam só em `FacilityOps/Assets/_Game/ThirdParty/Resources/HBM/` (ignorado pelo git; o repositório é público). Sem o pacote, `HumanVisual.Available` é falso e tudo cai no corpo procedural; os testes `HumanVisualTests` fazem `Assert.Ignore`. Para reinstalar: copiar de `D:\ProjectResort_AssetLibrary\UnityFree\ExtractedForReview\Human Basic Motions FREE` (2 modelos + Idle01/02, Walk01_Forward, Run01_Forward, Talk01 de M e F) e ligar Read/Write nos dois modelos.
- **Medido (Unity, modo gráfico)**: passada do pé em caminhada 0,147 m, corrida 0,345 m, parado 0,000 m; 24–34 corpos animados de 40–59 ativos na praia; render 2,7 ms médio (p95 3,0 ms) com a multidão — sem regressão. Capturas: `f02_6_pessoas_animadas.png`.
- **Limitações**: são manequins atléticos genéricos pintados (blockout melhorado, não arte final); roupas são só cores por região; criança = adulto escalado; troca visual procedural<->animado ocorre ao sentar/levantar; pés nem sempre assentam perfeitamente no chão (sem IK).

## Limitações que permanecem
- Personagens, quiosque, guarda-sóis e fauna são blockout procedural; mar é plano com espuma, sem shader de água; sem arte final.
- Sem sessão humana: ritmo, clareza do HUD, diversão e "vida" percebida **não foram avaliados**. A fase 03 continua bloqueada até essa aprovação.
- ~~Estágio 2+ (quiosque exportado): clientes ainda não sentam~~ — resolvido no adendo de 2026-10-06 (rodada 2).
- Áudio procedural não foi ouvido por uma pessoa nesta rodada (só medido: pico, RMS, volumes por hora).
- UI continua IMGUI provisória.

## Como reproduzir
```
powershell -ExecutionPolicy Bypass -File Tools/Autonomy/Run-UnityResortTests.ps1 -Graphics
```
Depois abrir `ResortPrologue` e jogar: olhar o calçadão às 12h, 18h20 e 20h30, conferir a geladeira (E), ouvir o mar e observar as palmeiras.

---

# Adendo 2 — mesas do estágio 2, HUD de próximo passo, guarda de balanceamento (2026-10-06, rodada 2)

**Status: COMPILADO, TESTADO (20/20 PlayMode, modo gráfico, sem erros no console) e CAPTURADO. Gate técnico segue PASS. `HUMAN_GATE_PENDING` continua; a Fase 03 NÃO está liberada.**

## O que mudou
- **Clientes sentam no quiosque exportado (estágio 2+)**: `StallLayout.AddKioskSeats` cria 10 cadeiras nas 5 mesas do deck do modelo de Blender (mesas em x ±7 m e 1/4/7 m atrás da origem; a mesa oeste a 7 m foi pulada porque o modelo a coloca dentro do bloco de banheiros — defeito do `sa_stages.kiosk`, a corrigir na próxima regeneração do FBX). Os assentos do estágio 1 desligam e os do deck ligam em `SetKioskLook`. Rota própria (`RouteToSeat`): sai pela ponta do balcão (x ±5,2 m), desce pelo corredor entre as mesas e atravessa até a cadeira, e volta pelo mesmo caminho.
- **Altura sobre o deck**: o deck do estágio 2 fica 0,14 m acima do chão; `StallLayout.Ground` agora o considera (`OnDeck`, `DeckLift`), então a fila e os clientes ficam em cima do deck, e não 14 cm dentro dele. Antes, a fila do estágio 2 afundava os pés.
- **HUD** (`Sim/ServiceHints.cs`, puro, e `ResortHud.DrawHint`): faixa sob a barra de status com o próximo passo ("Abra o quiosque na placa", "Cliente na fila: anote o pedido no balcão", "Pedido na chapa: segure [E] na grelha", "Pedido pronto: entregue no balcão", "Dia encerrado: volte para casa...") e aviso de estoque baixo (≤ 3 un.). A barra de status passou a mostrar ABERTO/FECHADO/FECHANDO e as vendas do dia (R$).
- **Guarda de balanceamento** (valores esperados, sem aleatoriedade): primeiro dia com preços-base ≈ 25–70 clientes, pico de 3–9 clientes/hora e lucro esperado > R$ 120. Não altera a curva; só avisa se alguém desbalancear.

## Evidência
- `Run-UnityResortTests.ps1 -Graphics` -> `TESTS total=20 passed=20 failed=0`. Novos: `ServedCustomersSitOnTheDeckTablesOfTheStageTwoKiosk` (cliente chega, senta e permanece na cadeira do deck; alturas seguem o deck), `HudHintsPointToTheNextStepAndFlagLowStock`, `FirstDayDemandIsWorthPlayingAndProfitable`.
- Captura real da Unity: `ArtSource/Blender/World/Reviews/F02/f02_7_estagio2_clientes_no_deck.png` (cliente sentado na mesa do deck do quiosque do estágio 2; o texto espelhado nos letreiros é só porque a câmera do teste foi movida antes do `LateUpdate` do Billboard).

## Limitações
- O HUD é IMGUI provisório e **não foi visto por uma pessoa**; os textos do HUD não aparecem nas capturas de câmera (IMGUI não vai para `Camera.Render`).
- Sentar continua pose procedural (sem clipes de cadeira nos pacotes gratuitos avaliados).
- A mesa oeste a 7 m do modelo do quiosque atravessa o bloco de banheiros (modelagem).


---

# Adendo 3 — shader do mar e céu noturno (2026-10-06, rodada 3)

**Status: COMPILADO, TESTADO (20/20 PlayMode, modo gráfico, sem erros de shader/compilação no log) e CAPTURADO. Gate técnico segue PASS. `HUMAN_GATE_PENDING` continua; a Fase 03 NÃO está liberada.**

## O que mudou
- **Mar com shader próprio** (`Resources/ResortSea.shader`, `ResortAurora/Sea`, URP/HLSL): cor por profundidade (turquesa raso -> azul profundo, vertex color), transparência no raso (areia molhada aparece), ondulações analíticas em duas escalas (marola longa + chop que some com a distância), reflexo de Fresnel do céu (usa o ambiente/fog que o `DayNightCycle` já controla, então o mar acompanha o relógio sem C# por quadro) e brilho de sol/lua. Antes era um plano `Lit` liso que refletia o céu e parecia um bloco ciano lavado.
- **Malha do mar** (`ResortSite.BuildSea`): colunas a cada 8 m ao longo da costa e 14 fileiras por distância da linha d'água (a primeira escondida sob a praia; até 1,5 km mar adentro, dentro do far clip de 1500 m). Um plano escuro fica 6 cm abaixo como rede de segurança (lagoas/baías que o scan da linha d'água ignora).
- **Céu noturno**: o sol era preso a >= 1 grau acima do horizonte, e o skybox procedural seguia essa direção, deixando um brilho oliva/amarelo a noite toda. Agora o sol desce de verdade abaixo do horizonte (a luz já era desligada por `vis`; sombras só com sol > 1 grau). Resultado: noite com estrelas sobre céu escuro, quiosque e lâmpadas legíveis (luminância média das capturas noturnas 0,11–0,18).

## Evidência
- `Run-UnityResortTests.ps1 -Graphics` -> `TESTS total=20 passed=20 failed=0` (4 execuções nesta rodada; a última com o código final). 0 ocorrências de `error CS` / `Shader error` no log.
- Desempenho (render em lote, sem IMGUI): praia ao meio-dia 2,8 ms médio (p95 3,2 ms, pior 3,5 ms, 63 pessoas); estágio 1 2,6–2,7 ms; estágio 7 2,3–3,0 ms. Sem regressão.
- Capturas reais regeneradas: `ArtSource/Blender/World/Reviews/F02/f02_{1_dia,2_tarde_dourada,3_por_do_sol,4_noite}_*.png` (mar novo visível em `*_praia_para_o_mar` e `*_aerea`).

## Limitações
- O mar ainda não tem espuma de profundidade, refração real nem reflexo de objetos (planar/SSR); o brilho da lua é fraco nas capturas testadas.
- O céu noturno é preto com estrelas (sem gradiente azul); o crepúsculo ainda é um oliva sujo do skybox procedural.
- Nada disso foi visto por uma pessoa: o gate visual e o humano continuam abertos.


---

# Adendo 4 — shader de céu próprio (2026-10-06, rodada 4)

**Status: COMPILADO, TESTADO (20/20 PlayMode, modo gráfico, 0 `error CS` / `Shader error` no log) e CAPTURADO. Gate técnico segue PASS. `HUMAN_GATE_PENDING` continua; a Fase 03 NÃO está liberada.**

## O que mudou
- **Céu com shader próprio** (`Resources/ResortSky.shader`, `ResortAurora/Sky`, URP/HLSL) no lugar do `Skybox/Procedural`: gradiente zênite -> horizonte dirigido pelo relógio, faixa quente do lado do sol, halo e disco solar, dither de 1/255 contra faixas. O horizonte do céu usa exatamente a cor da névoa, então céu, mar distante e névoa se encontram sem emenda em qualquer hora.
- **`DayNightCycle.Apply`**: cores de zênite/horizonte por hora (azul de dia, lilás/laranja na tarde dourada, violeta no crepúsculo, azul-marinho profundo à noite); o crepúsculo roxo só aparece enquanto a noite sobe (`dusk`). Se o shader não for encontrado, cai no céu procedural antigo.
- Antes: pôr do sol com céu oliva sujo e noite preta pura; agora: pôr do sol violeta e noite azul-marinho com estrelas.

## Evidência
- Execução A (código antigo, linha de base desta rodada): `TESTS total=20 passed=20 failed=0`.
- Execução B (código novo): `TESTS total=20 passed=20 failed=0`. Luminância média das capturas: pôr do sol 0,20–0,23 (antes 0,13–0,19), noite 0,13–0,19 (antes 0,11–0,18); dia e tarde sem mudança relevante.
- Capturas reais regeneradas: `ArtSource/Blender/World/Reviews/F02/f02_{1..4}_*.png` (ver `f02_3_por_do_sol_praia_para_o_mar.png`, `f02_4_noite_praia_para_o_mar.png`, `f02_2_tarde_dourada_calcadao_leste.png`).

## Limitações
- Sem nuvens; a tarde dourada ficou mais lilás que alaranjada nas capturas olhando para leste (o brilho quente fica do lado do sol, para oeste); ajuste fino de arte depende de olho humano.
- O desempenho não foi remedido nesta rodada (o céu é um único quad de skybox, custo desprezível); a medição de 2,8 ms do adendo 3 permanece a última real.
- Nada disso foi visto por uma pessoa: gate visual e humano continuam abertos.


---

# Adendo 5 — nuvens no céu (2026-10-06, rodada 5)

**Status: COMPILADO, TESTADO (20/20 PlayMode, modo gráfico, 0 `error CS` / `Shader error` no log) e CAPTURADO. Gate técnico segue PASS. `HUMAN_GATE_PENDING` continua; a Fase 03 NÃO está liberada.**

## O que mudou
- `Resources/ResortSky.shader`: camada de nuvens procedural (fbm de ruído de valor, projetada na cúpula, mais densa perto do horizonte, derivando devagar com `_Time`), com borda clara do lado do sol. Novas propriedades `_CloudColor` e `_CloudCover`.
- `DayNightCycle.Apply`: cor das nuvens por hora (branco de dia, rosado/dourado no pôr do sol, violeta no crepúsculo, azul-marinho escuro à noite) e cobertura 0,4 (0,78 quando o clima é `Cloudy`).

## Evidência
- `Run-UnityResortTests.ps1 -Graphics` -> `TESTS total=20 passed=20 failed=0`; 0 `error CS` / `Shader error`.
- Capturas reais regeneradas em `ArtSource/Blender/World/Reviews/F02/` (ver `f02_1_dia_praia_para_o_mar.png`: fiapos de nuvem sobre o mar; crepúsculo e noite continuam limpos).

## Limitações
- Nuvens são só cosméticas (sem sombra no chão, sem volume); desempenho não remedido (custo: 10 amostras de ruído por pixel de céu, desprezível). Nada disso foi visto por uma pessoa.
