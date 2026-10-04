# PROTOCOLO AUTÔNOMO — CLAUDE CODE / FACILITY OPS

**Branch de trabalho:** `claude/w1-masterplan`  
**Objetivo:** permitir execução contínua e segura por etapas, com checkpoints claros no GitHub.

## Regras obrigatórias

1. Trabalhar somente na branch `claude/w1-masterplan`.
2. Nunca fazer merge no `main` automaticamente.
3. Antes de cada nova etapa:
   - executar `git pull`;
   - reler `CLAUDE.md`;
   - reler `Docs/CLAUDE_NEXT_TASK.md`;
   - confirmar que não há conflito com decisões mais recentes.
4. Ao concluir uma etapa:
   - validar;
   - atualizar documentação;
   - fazer commits organizados;
   - fazer push;
   - garantir working tree limpa;
   - voltar ao passo 3 e procurar a próxima tarefa.
5. Continuar autonomamente enquanto houver tarefa explícita em `Docs/CLAUDE_NEXT_TASK.md` e recursos de uso disponíveis.
6. Se o limite de uso do Claude for atingido, simplesmente parar em estado limpo, com tudo commitado/pushado até onde foi possível.
7. Se houver erro crítico, corrupção, conflito de Git, dúvida de licença, mudança destrutiva de save/IDs, ou necessidade de decisão de produto não coberta pelos documentos, parar e registrar o bloqueio em `Docs/STATUS_IMPLEMENTACAO.md`.
8. Não instalar add-ons/MCPs/dependências externas sem aprovação explícita.
9. Não executar código externo desconhecido sem revisão.
10. Preservar IDs, saves, arquivos `.meta`, o protótipo Unity funcional e os fontes Blender existentes.
11. Visual final: realista, denso, PBR e não-low-poly. Blockout simples só é permitido em etapas de massing.
12. VEIN é referência de patamar visual/atmosfera, nunca fonte para copiar assets, layouts, texturas ou identidade.

## Handshake entre etapas

Ao terminar cada etapa:
- faça push;
- aguarde alguns segundos;
- rode `git pull`;
- releia `Docs/CLAUDE_NEXT_TASK.md`;
- se a tarefa mudou, execute a nova;
- se permanecer a mesma mas já estiver concluída, registre isso e aguarde uma atualização do coordenador;
- não invente uma nova macro-etapa fora do planejamento oficial.

## Prioridades permanentes

1. mundo e estruturas primeiro;
2. depois Cidade Antiga em alta fidelidade;
3. depois integração Unity do mundo;
4. depois sistemas/economia/veículos;
5. novas missões só quando o mundo necessário estiver pronto.

## Saída mínima por etapa

- relatório Markdown;
- validações executadas;
- capturas reais quando houver trabalho visual;
- SHA dos commits;
- push confirmado;
- limitações explícitas;
- próximo ponto de continuidade.
