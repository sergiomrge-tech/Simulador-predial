# Infraestrutura de QA — Cidade Antiga Vertical Slice v0.1

Entrega na branch `codex/vertical-slice-qa`, a partir de `gpt/unity-world-integration` em `b039cef092dc2a3b102424afd465c31906520d78`. Data: 04/10/2026. O SHA da entrega é o commit desta versão na branch; consulte `git rev-parse HEAD` ou o histórico no GitHub.

Esta entrega prepara a automação e executa a auditoria na base existente. **Não integra outro patch do Claude, não altera geometria, `.blend`, texturas, hero locations, cenas autorais ou saves existentes.** Nenhum merge ou release público foi feito.

## Ferramentas

| Arquivo | Função |
| --- | --- |
| `VerticalSliceQaRunner.cs` | Validador único de 15 células, IDs, referências, materiais, markers, colliders, spawn, save/load, NavMesh e rota. Relatório PASS/FAIL por item e coordenada. |
| `VerticalSliceQaContracts.cs` | Formato dos resultados, tratamento de métricas indisponíveis e gate de entrega. |
| `VerticalSlicePlayerQa.cs` | Harness opt-in para Development Player, caminhada física, save/load, cenas únicas, erros e 13 checkpoints. |
| `VerticalSliceProfiler.cs` | FPS médio/mínimo, frame time, pior frame, memória, GC, load/unload, hitch de streaming e contadores de render disponíveis. |
| `VerticalSliceBuildPipeline.cs` | Valida recibos atuais de testes/rota e gera somente um candidato Windows x64 Development. |
| `Tools/Build-VerticalSlice-V01.ps1` | Orquestra QA, testes, candidato, execução no Player, gate, distribuição, versão e manifest SHA256. Requer PowerShell 7 e Unity CLI. |
| `VerticalSliceQaTests.cs` | Testes dos gates, ausência de métricas falsas, continuidade da rota e lifecycle do profiler em Play Mode. |

Os arquivos C# ficam em `FacilityOps/Assets/_Game/Editor`, `Scripts/Runtime` ou `Tests/Editor`, conforme o papel. Seus `.meta` foram gerados pelo Unity. O walker físico existente foi reaproveitado; seus contadores ausentes agora têm status `INDISPONÍVEL`, e a lista de hitches mantém somente os 12 piores. O overlay existente ganhou posição e estado da superfície NavMesh, sendo ativado apenas por flags de QA em Editor/Development.

## Executar a auditoria

No root do repositório:

```powershell
unity run ./FacilityOps -- -executeMethod FacilityOps.Editor.VerticalSliceQaRunner.Run
```

O comando escreve o relatório, mesmo quando o mapa falha. O modo usado pela automação retorna erro em falha estática:

```powershell
unity run ./FacilityOps -- -executeMethod FacilityOps.Editor.VerticalSliceQaRunner.ValidateStaticBatch
```

Saída: `Docs/ValidationEvidence/VerticalSliceQA/qa.json` e `qa.md`. O runner cria somente dados de QA; a pose aberta das portas é temporária na sessão de referência e as cenas não são salvas. O NavMesh é derivado dos colliders reais, sem adicionar links, remover obstáculos ou fabricar pisos.

## Rota física e checkpoints

A rota usa os IDs de facilities existentes, markers do portão/portaria, `GP_prologue_spawn_corridor` e `GP_quadro_tecnico`. A aproximação do quadro respeita seu forward e altura sobre o piso. O planner verifica cada trecho, distância, cobertura, cápsula contra geometria e células de streaming necessárias. Falhas removem o plano executável antigo e registram trecho/coordenada; nunca são substituídas por uma reta ou por teleporte.

Quando todos os trechos estáticos passam, `route.json` contém:

Lar → Oficina → Horizonte exterior → portão → portaria → quarto andar → área técnica → saída → Mercearia → Lar.

O teste de Play Mode é opt-in, para ser executado depois que o mapa passar:

```powershell
$env:VERTICAL_SLICE_CONTINUOUS_QA='1'
unity test ./FacilityOps --mode EditMode --filter VerticalSliceQaTests.ContinuousPlayerControllerRouteWithoutMidRouteTeleport --timeout 1500 -- -worldSlice -worldSliceQa
Remove-Item Env:VERTICAL_SLICE_CONTINUOUS_QA
```

O contrato permite uma única colocação inicial, depois da aceitação do chamado; rejeita teleporte, nova aceitação que reroteie o jogador e segmentos desconectados após começar a caminhada. O CharacterController, gravidade, colisões, streaming e interação de portas permanecem reais. O teste do Editor não declara capturas como sendo de Player.

O harness de Player gera 13 PNGs reais em um subdiretório de execução dentro de `Docs/Previews/UnityVerticalSliceV01`: Lar, rua, Oficina, Horizonte exterior, portão, portaria, escada, quarto andar, área técnica, Mercearia, streaming overlay, performance overlay e retorno. O gate exige os 13 arquivos. **Não foram geradas imagens substitutas nesta entrega.**

## Profiling e overlay

O Player é iniciado com `-worldSlice -worldSliceQa -verticalSliceQa`, mais root, caminho da rota e fingerprint fornecidos pelo script. A flag utiliza uma carreira nova em arquivo de QA, preservando o save normal. Sem a flag, o harness não é criado. Em build sem Development, ele não é ativado.

`performance.json` e `performance.md` são escritos em `Docs/ValidationEvidence/VerticalSliceQA` pela rodada real do Player. Cada métrica tem status, valor e unidade. Contador inexistente/sem amostras aparece como **INDISPONÍVEL**, sem um zero fictício. Zero de GC só é medido quando existe uma amostra válida. Render counters sem observações positivas são tratados conservadoramente como indisponíveis; seus valores são médias das observações positivas, conforme a unidade informa.

FPS mínimo significa o inverso do pior frame individual. Capturas e instrumentação fazem parte do custo observado. A medição curta não é prova de ausência de vazamentos; um soak prolongado continua necessário. Memória e número de células são registrados, e a coleta não mantém um histórico ilimitado de frames/hitches.

O overlay requer flags como `-verticalSliceQaOverlay`, `-verticalSliceQa` ou flags legadas de QA. Ele exibe FPS, frame time, memória, GC, célula, contagens/pedidos pendentes, posição e disponibilidade do NavMesh. Ausência de uma superfície é exibida como “NO SURFACE / NOT LOADED”, sem afirmar que o mapa é navegável.

## Gerar e empacotar

```powershell
pwsh -File ./Tools/Build-VerticalSlice-V01.ps1 -ValidateOnly
# Depois que a rota estática passar:
pwsh -File ./Tools/Build-VerticalSlice-V01.ps1
```

O fluxo valida projeto, executa testes e caminhada em Play Mode, confere a atualidade dos recibos e produz um candidato em uma pasta nova de staging. Só depois de executar o Player, comprovar saída limpa, ausência de erros críticos, streaming, save/load, caminhada completa e capturas, o script move o candidato para:

`Builds/Windows/FacilityOps_CidadeAntiga_VerticalSlice_v0.1/`

Inclui executável x64 Development, `Jogar_CidadeAntiga.bat` com `-worldSlice`, `VERSION.txt`, evidências, previews, `FILES_MANIFEST.json` (SHA256 de cada arquivo) e `SHA256SUMS.txt` (hash do manifest). Uma distribuição existente é preservada e o script interrompe a operação; não há limpeza recursiva que apague builds anteriores.

O NavMesh de QA é incluído no candidato como um recurso temporário de Development e removido dos fontes em `finally`. Não há alteração do NavMesh autoral ou das cenas. Testes antigos, recibos, fonte e plano da rota têm verificação de atualidade: mudanças invalidam a aprovação anterior. Um recibo de testes mais antigo que os C# atuais é recusado.

`READY_FOR_USER_TEST = TRUE` exige todos os itens obrigatórios PASS, ausência de FAIL, recibos atuais, Player sem crash/erro crítico e as capturas. Performance abaixo de 60 FPS gera WARNING e pode permitir a entrega técnica. Ausência de execução de Player mantém o estado falso.

## Resultado desta entrega e limites

- Compilação e suíte final: **28 PASS, 0 FAIL, 4 IGNORE** de 32 casos. Incluem testes antigos, regressão do modo normal em Play Mode e lifecycle do profiler.
- Os quatro IGNORE são gates opt-in do Lar, runtime legado por visitas, escada legada e a nova rota contínua. A nova rota completa não foi executada porque a auditoria detectou falhas na base atual.
- Validações de manifesto, 15 cenas, referências/materiais, Build Settings, regras anteriores, save/load isolado, colliders e spawns passam.
- Os markers do portão e da portaria também apresentam sobreposição da cápsula com `EXPORT_W2_horizonte__site` em `(-2350,27.03,-1827.50)` e `EXPORT_W2_horizonte__F00_lobby` em `(-2350,26.97,-1816)`, respectivamente.
- O planner aponta colisão/cobertura suspeita na escada e `PathPartial` no retorno Mercearia → Lar, cuja última posição alcançável é `(-2778.10,19.53,-2163.90)`. Consulte `qa.md` para todos os nomes e coordenadas. Probes de cápsula e cobertura são diagnósticos conservadores; a caminhada física é a prova final, especialmente em escadas/jambas. Nenhum achado foi “corrigido” alterando a arte.
- O comando automatizado com `-ValidateOnly` foi exercitado e interrompeu o fluxo na falha estática, conforme esperado. A criação completa do candidato, execução de Player, 13 screenshots e empacotamento ficam pendentes do mapa aprovado. **Nenhum novo executável, distribuição, métricas reais de Player ou aprovação de entrega foi declarado.**
- `READY_FOR_USER_TEST = FALSE` é o resultado correto desta auditoria. As evidências versionadas descrevem a base `b039cef`; não são aprovação de um futuro mapa do Claude.

Próxima integração da geometria permanece separada desta branch. Execute os mesmos gates novamente após a integração autorizada do patch visual, sem reutilizar evidências antigas.

Para reproduzir somente a suíte desta entrega, incluindo a regressão do modo normal:

```powershell
$env:FACILITY_NORMAL_QA='1'
unity test ./FacilityOps --mode EditMode --output ./Docs/ValidationEvidence/VerticalSliceQA/EditMode.xml -- -worldSliceQa
Remove-Item Env:FACILITY_NORMAL_QA
```
