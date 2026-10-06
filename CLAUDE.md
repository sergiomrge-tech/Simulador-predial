# PROJECT RESORT — contexto oficial para Claude

## NOVA DIREÇÃO DO PROJETO

A direção anterior **PROJECT FACILITY / simulador de manutenção predial** deixou de ser o objetivo principal.

O projeto passa oficialmente a ser **PROJECT RESORT**, um simulador de empreendedorismo, hotelaria, construção e gestão em primeira pessoa.

Leia **ANTES DE QUALQUER ALTERAÇÃO**:

1. `Docs/GDD_PROJECT_RESORT_MASTER.md` — documento mestre e autoridade principal da nova direção.
2. `Docs/STATUS_IMPLEMENTACAO.md` — estado técnico legado e checkpoints existentes.
3. `Docs/PLANO_MESTRE_MUNDO_SANTA_AURORA.md`
4. `Docs/WORLD_BIBLE_SANTA_AURORA_V1.md`
5. `Docs/ART_BIBLE_REALISMO_SANTA_AURORA.md`
6. `README.md`

Quando houver conflito entre documentação antiga do Facility Ops e `Docs/GDD_PROJECT_RESORT_MASTER.md`, **o GDD do PROJECT RESORT vence**.

## Conceito central

O jogador começa com um pequeno quiosque/barraquinha na praia de Santa Aurora, vendendo bebidas e lanches.

A progressão deve ser física, econômica e visual:

```
quiosque pequeno
→ quiosque profissional
→ pousada
→ pequeno hotel
→ hotel completo
→ primeiro resort
→ resort de luxo
→ resort cinco estrelas monumental
```

O jogador vive fisicamente nesse mundo em primeira pessoa, tem sua própria casa, acorda, trabalha, retorna para casa e evolui seu patrimônio pessoal junto com o empreendimento.

O resort final deve representar transformação extrema: lobby monumental, recepção de luxo, piscinas, restaurantes, academia, spa, suítes premium, suíte presidencial, beach club, salão de eventos, áreas VIP, administração e infraestrutura técnica completa.

## Regra de reaproveitamento

Não descartar a base existente sem necessidade.

Preservar e adaptar quando tecnicamente viável:

- Unity 6000.6.2f1;
- URP;
- C#;
- primeira pessoa;
- FirstPersonController;
- câmera;
- raycast/interação;
- colisões;
- Santa Aurora;
- estradas;
- calçadas;
- relevo;
- streaming e células;
- assets urbanos;
- casa do jogador;
- veículos;
- portas e objetos interativos;
- arquitetura de save;
- elétrica;
- hidráulica;
- bombas;
- sistemas de manutenção;
- ferramentas de Blender/Unity;
- validações e pipelines úteis.

O antigo loop de manutenção predial deixa de ser o núcleo. Manutenção passa a ser **um subsistema interno do resort**, podendo ser realizada pelo jogador ou delegada a funcionários.

## Regra crítica antes de continuar

O usuário informou que a conversão para resort **já pode ter sido iniciada localmente**.

Portanto, antes de implementar qualquer nova tarefa:

1. identificar a branch local atual;
2. verificar o último commit;
3. verificar arquivos modificados e não commitados;
4. procurar qualquer código, cena, documentação ou asset já criado para resort;
5. comparar esse estado com `Docs/GDD_PROJECT_RESORT_MASTER.md`;
6. continuar do ponto real;
7. não refazer trabalho existente;
8. não apagar sistemas reaproveitáveis;
9. não sobrescrever trabalho local não commitado.

## Primeira prioridade de produção

Depois da auditoria, a primeira meta funcional é o **vertical slice do quiosque**.

Ele deve conter, no mínimo:

- área de praia funcional;
- pequeno quiosque;
- produtos;
- estoque;
- fornecedor/abastecimento mínimo;
- clientes;
- atendimento;
- pagamento;
- caixa;
- abertura e fechamento do dia;
- dinheiro persistente;
- reputação inicial;
- rotina casa → trabalho → casa;
- save/load.

O quiosque precisa ser divertido e jogável antes da expansão para hotel.

## Regra de desenvolvimento

Não criar dezenas de sistemas incompletos.

Prioridade:

```
Quiosque divertido
↓
Economia funcional
↓
Funcionários
↓
Compra de terreno
↓
Pousada funcional
↓
Hotel funcional
↓
Construção modular
↓
Resort
↓
Luxo / cinco estrelas
```

Cada estágio precisa fechar seu loop antes de expandir.

## Qualidade

Nenhuma fase é considerada pronta apenas porque o código compila.

Para concluir uma fase:

1. compilar;
2. executar;
3. jogar;
4. validar interações;
5. testar save/load;
6. testar progressão;
7. verificar visualmente;
8. verificar performance;
9. registrar evidências reais.

Toda captura apresentada como gameplay deve ser captura real da Unity. Nunca usar mockup como se fosse gameplay.

## Visual

O alvo continua sendo um jogo comercial para PC/Steam, visual realista e coerente.

Blockout é permitido durante produção, mas não deve ser tratado como arte final.

Manter Santa Aurora original. Referências externas podem orientar qualidade e atmosfera, nunca ser copiadas.

## Branches e integração

Trabalhar em branch `claude/` ou branch explicitamente indicada para a conversão.

Fazer commits pequenos e descritivos.

Não publicar releases, mudar visibilidade do repositório ou apagar histórico sem autorização.

## Documentação legada

Documentos do Facility Ops continuam úteis como fonte técnica, lore, mundo e sistemas reutilizáveis, mas **não comandam mais o design principal**.

Especialmente:

- manutenção predial;
- chamados;
- contratos técnicos;
- diagnóstico/reparo;

devem ser tratados como material reutilizável para o futuro módulo de manutenção do resort, não como campanha central.

## Objetivo de longo prazo

A experiência final deve permitir ao jogador olhar para um enorme resort cinco estrelas e saber que aquele complexo nasceu da pequena barraquinha onde ele começou vendendo bebidas na praia.

Essa transformação é o coração de PROJECT RESORT.


## Próxima tarefa operacional

Antes de iniciar nova implementação, execute integralmente o handoff em:

`Docs/CLAUDE_NEXT_TASK_PROJECT_RESORT.md`

Esse documento define a auditoria inicial, o vertical slice do quiosque, os gates de qualidade, o que reaproveitar e o que NÃO implementar ainda.


## ORDEM OFICIAL DE EXECUÇÃO DO PROJECT RESORT

A execução completa do projeto está organizada em ordem obrigatória em:

`Docs/PROJECT_RESORT_EXECUTION/00_EXECUTION_INDEX.md`

Esse índice referencia as fases 01 a 18. Siga-as em ordem e só avance quando o gate da fase atual estiver aprovado e registrado.

A sequência oficial é:

1. Auditoria e consolidação da base
2. Vertical slice do quiosque
3. Economia e fornecedores
4. Funcionários iniciais
5. Expansão de terreno
6. Vertical slice da pousada
7. Construção modular
8. Hotel completo
9. Piscina, lazer e praia
10. Primeiro resort operacional
11. Resort de luxo
12. Vida pessoal e patrimônio
13. Mundo vivo e sazonalidade
14. Endgame cinco estrelas
15. Polimento UX/áudio/visual
16. Otimização, QA e escala
17. Demo Steam
18. Pré-lançamento e release

Não pular fases, não antecipar escopo futuro e não tratar uma fase como concluída apenas porque o código compila.
