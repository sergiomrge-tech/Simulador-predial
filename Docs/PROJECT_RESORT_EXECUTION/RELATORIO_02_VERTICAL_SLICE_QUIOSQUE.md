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

# Adendo — praia viva, dia/noite e quiosque da REF 01/02 (continuação, 2026-10-06)

**Status: IMPLEMENTADO, NÃO COMPILADO E NÃO EXECUTADO.** Nesta sessão (não interativa) o Unity, o `dotnet` e o `sed` exigiam aprovação manual e foram negados; só foi possível editar arquivos e revisar o código à mão. Nada abaixo conta como evidência de gate. O gate visual da Fase 02 continua **aberto** até alguém rodar os testes e olhar as capturas.

## O que o requisito novo exigia e o que ainda faltava no estado anterior
- Praia/calçadão com população ambiente (só havia "Walkers" cápsula, máx. 40, sem atividades, LOD ou pooling).
- Dia → pôr do sol → noite com luz artificial (o relógio ia a 22h sem céu, lua nem lâmpadas; o sol nascia a oeste).
- Quiosque mais próximo da REF 01/02 (telhado listrado vermelho/branco, geladeira/freezer decorativos).

## O que foi escrito (Unity, namespace `ResortAurora`)
| Arquivo | Conteúdo |
|---|---|
| `Sim/Daylight.cs` | `Daylight` (noite 0..1, elevação do sol, hora de acender lâmpadas, fase do dia) e `PopulationModel` (densidade por hora × clima × reputação × estágio e metas por papel). C# puro. |
| `Game/DayNightCycle.cs` | Sol (leste → norte → oeste), lua, ~700 estrelas, céu procedural, névoa, ambiente trilight, reflexos; lâmpadas do calçadão, quiosque e casa (cabeças emissivas compartilhadas + pool de 8 luzes reais para as mais próximas da câmera). |
| `Game/PersonRig.cs` | Humano procedural (pele, cabelo, roupa variados; 2 segmentos por perna) com poses: andar, correr, sentar na areia/cadeira, deitar, nadar, pedalar; gestos (celular, beber, conversar, cavar); LOD 0–3. |
| `Game/BeachLife.cs` | População pooled (84 adultos + 24 crianças): grupos que passeiam e param para olhar o mar (casais, amigos, famílias com crianças), corredores, ciclistas, banhistas que deitam/sentam, crianças cavando, nadadores que entram e saem do mar. Chegam e saem a pé (sem pop-in à vista). LOD por distância (38/100/230 m), sem NavMeshAgent. |
| `Game/KioskDecor.cs` | Quiosque estágio 1: telhado de zinco sobre caibros, tábuas envelhecidas, prateleiras com garrafas, **geladeira, freezer e prateleira como estações para conferir estoque**, caixa registradora, caixas, lixeira, lâmpadas, mesas amarelas com cadeiras brancas e guarda-sóis (1 mesa no início, 3 com a melhoria "Mesas"). Peças `S1_*` somem no estágio 2. |
| `Game/Agents.cs` | Clientes e funcionários usam o `PersonRig`; clientes servidos podem sentar numa mesa, beber e sair. |
| `Tests/PlayMode/LivingWorldTests.cs` | Curva de luz e população; praia viva de dia/noite (contagens, papéis, chão, exclusão do quiosque, LOD); tempo de frame com a multidão; capturas dia/tarde dourada/pôr do sol/noite em 5 ângulos (`ArtSource/Blender/World/Reviews/F02/`) com luminância média; geladeira/freezer/mesas. |

Removidos: `UpdateSun` do `ResortGame`, `StallBuilder.Person` e os pedestres cosméticos "Walker".

## Como validar (precisa de uma pessoa ou de uma sessão com permissão para o Unity)
```
Unity.exe -batchmode -projectPath FacilityOps -runTests -testPlatform PlayMode -testFilter ResortAurora.Tests -logFile Logs/f02.log
```
Esperado: os 8 testes anteriores continuam passando + 5 novos (`LivingWorldTests`). Depois abrir `ResortPrologue` e jogar: olhar o calçadão às 12h, às 18h20 e às 20h30, conferir a geladeira (E), sentar clientes nas mesas, medir FPS.
**Risco conhecido:** limiares de luminância e contagens de pessoas nos testes foram escolhidos sem poder rodar; podem precisar de ajuste.

## Descoberta que afeta o gate visual (decisão pendente)
No ponto do quiosque a areia tem **~170 m** de profundidade (mar em z≈80, calçadão em z≈255; perfil de 1,6% do Blender). A REF 01 mostra o mar a poucos metros do quiosque. A população foi distribuída para funcionar nessa praia larga (banhistas de 5 a 110 m do calçadão, nadadores na linha d'água distante), mas o enquadramento "quiosque + mar na mesma cena" da REF só existe se o perfil da praia for estreitado na origem (`Tools/Map/export_resort_site.py`, reexportando as alturas). Isso mexe no layout de todos os estágios futuros (marina, ponta do farol), por isso **não foi alterado** sem decisão.

## Outras limitações
- Pessoas e quiosque ainda são blockout de primitivas (não arte final); sem áudio de mar/vozes; sem ondas animadas; sem aves.
- Estágio 2+ (modelo exportado do quiosque): os clientes não sentam (mesas do estágio 1 ficam ocultas).
- A UI continua IMGUI provisória.
