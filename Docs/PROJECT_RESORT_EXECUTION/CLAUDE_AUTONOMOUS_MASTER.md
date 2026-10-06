# PROJECT RESORT — Modo Autônomo do Claude

Este arquivo é a ordem permanente de trabalho do Claude Code para o PROJECT RESORT.

## Fonte de verdade

Antes de qualquer alteração, leia nesta ordem:

1. `CLAUDE.md`
2. `Docs/GDD_PROJECT_RESORT_MASTER.md`
3. `Docs/PROJECT_RESORT_EXECUTION/00_EXECUTION_INDEX.md`
4. `Docs/PROJECT_RESORT_EXECUTION/CLAUDE_CURRENT_TASK.md`
5. o arquivo da fase atual em `Docs/PROJECT_RESORT_EXECUTION/`
6. `Docs/VISUAL_REFERENCES/PROJECT_RESORT_VISUAL_REFERENCES.md`
7. `Docs/VISUAL_REFERENCES/PROJECT_RESORT_STARTER_PACK/README.md`
8. relatórios mais recentes da fase atual.

O projeto físico principal está em `D:\sergi\Documents\Simulador-predial`.
O caminho antigo no C: é apenas um junction de compatibilidade.

## Missão

Desenvolver o PROJECT RESORT de forma contínua, em ordem de fases, até a conclusão do roadmap oficial. Não esperar instrução a cada microetapa.

O jogo é um simulador em primeira pessoa para PC/Steam em Unity, com crescimento físico e empresarial longo: quiosque simples -> quiosque ampliado -> área de atendimento maior -> pousada -> hotel -> complexo -> resort -> resort de luxo -> cinco estrelas -> endgame monumental.

## Princípios obrigatórios

- sensação de mundo real ou próxima disso;
- praia e cidade vivas, nunca vazias;
- NPCs plausíveis com atividades, variedade e LOD/pooling;
- ciclo completo de dia/noite com noite bonita e iluminada;
- progressão longa, com várias fases e crescimento físico visível;
- first-person como experiência principal;
- construção, operação, gestão e vida pessoal integradas;
- automação cresce com o empreendimento;
- todo grande avanço deve aparecer visualmente no mundo;
- desempenho e estabilidade importam desde cedo;
- dados e sistemas devem ser modulares e extensíveis.

## Regras de execução

1. Trabalhe somente na branch `claude/w1-masterplan`, salvo instrução explícita do Diretor.
2. Não fazer merge em `main`.
3. Não usar `git reset --hard`, `git clean -fd`, force-push ou exclusões destrutivas.
4. Nunca apagar saves do jogador.
5. Preserve todo trabalho local existente.
6. Antes de editar, verifique `git status` e os commits recentes.
7. Faça commits pequenos, descritivos e frequentes.
8. Faça push para `origin/claude/w1-masterplan` a cada marco validado.
9. Não pule fases.
10. Código existir não significa tarefa concluída.
11. Não chamar concept art de screenshot do jogo.
12. Só chamar de captura real o que saiu de uma execução real da Unity.
13. Não inventar playtest humano, FPS, testes ou validações.
14. Se algo depender de teste humano, marque claramente `HUMAN_GATE_PENDING` e continue apenas com trabalho seguro da mesma fase.
15. Se uma ferramenta falhar, diagnostique, registre e tente uma alternativa segura antes de parar.
16. Se bater limite de uso/franquia, salve estado, commit/push do que estiver seguro e escreva o próximo passo em `CLAUDE_CURRENT_TASK.md`.

## Gate universal de cada fase

Antes de promover a fase para PASS:

- compilar no Unity;
- executar testes relevantes;
- executar a cena real;
- verificar loop principal da fase;
- validar save/load quando aplicável;
- verificar progressão;
- revisar referências quebradas;
- verificar erros de console;
- verificar regressões dos sistemas reutilizados;
- medir desempenho quando a fase adiciona carga;
- gerar evidência real da Unity;
- registrar limitações;
- atualizar o relatório da fase;
- fazer commit e push.

Se houver gate humano pendente, não avançar para a próxima fase.

## Unity — procedimento oficial de automação

Use preferencialmente:

`Tools/Autonomy/Run-UnityResortTests.ps1`

Esse script prepara o ambiente do Unity Package Manager, usa o projeto no D:, executa os testes e grava logs/resultados em `D:\ProjectResort_Autonomy\`.

Não use `-noUpm` para validar o projeto, pois isso remove Input System/URP/EventSystems da compilação e gera falsos erros.

## Arte e visual

O STARTER PACK é concept art de direção, não captura de jogo.

Na fase inicial, prioridade visual:
1. praia + quiosque inicial;
2. operação do balcão;
3. estoque/reposição;
4. casa inicial.

As refs da pousada e do resort cinco estrelas são north-star de fases futuras e não autorizam implementação precoce.

A praia inicial deve parecer viva: pedestres, casais, famílias, grupos, banhistas, clientes, mesas ocupadas e atividades plausíveis. NPCs não podem flutuar, afundar, atravessar objetos de forma evidente ou parecer clones óbvios.

## Ciclo dia/noite

A base do ciclo deve existir cedo. O ambiente deve transicionar por amanhecer, manhã, meio-dia, tarde, pôr do sol, noite e madrugada. Luzes arquitetônicas e do calçadão devem criar uma noite legível, bonita e plausível.

## Progressão longa

Não comprimir a campanha. O jogador deve sentir várias etapas intermediárias de expansão. Cada fase importante deve aumentar espaço físico, operações, equipe, infraestrutura, clientela e responsabilidade.

## Quando terminar uma rodada de trabalho

Sempre:
1. rode os testes possíveis;
2. atualize `CLAUDE_CURRENT_TASK.md` com estado real;
3. atualize o relatório da fase se houver avanço;
4. commit/push do que estiver validado;
5. deixe uma próxima ação concreta.

Se a fase ainda estiver aberta, continue nela.
Se o gate estiver realmente fechado, atualize a tarefa atual para a próxima fase e continue.

## Biblioteca local de assets gratuitos

Claude deve consultar também:

`Docs/ASSET_LIBRARY/UNITY_FREE_ASSETS.md`

Biblioteca local disponível no computador:

`D:\ProjectResort_Autonomy\assets`

Esse caminho é um junction para:

`D:\ProjectResort_AssetLibrary`

Prioridade atual:
1. usar `Human Basic Motions FREE` para substituir animações procedurais/estáticas dos NPCs próximos e médios, sem quebrar BeachLife/LOD;
2. avaliar `Environment Pack Free Forest Sample` apenas onde a estética for compatível;
3. não integrar automaticamente assets de fantasia/monstros/VFX mágicos;
4. nunca commitar os pacotes brutos da Unity Asset Store no GitHub público;
5. se precisar de um asset pago para atingir visual realmente superior, documentar a necessidade e aguardar aprovação do usuário antes da compra.

Ao integrar animações:
- preferir Humanoid/Mecanim;
- idle/walk/run/jog/talk;
- transições suaves;
- Root Motion apenas onde fizer sentido;
- manter pool/LOD;
- evitar Animator completo em personagens distantes;
- validar performance e capturas reais antes/depois.
