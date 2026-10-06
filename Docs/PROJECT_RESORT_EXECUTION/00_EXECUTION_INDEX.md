# PROJECT RESORT — ORDEM OFICIAL DE EXECUÇÃO

Este diretório é a fila oficial de produção do PROJECT RESORT para o Claude.

## Regra principal

Executar as fases em ordem. Não pular fase sem registrar explicitamente que o gate anterior foi aprovado.

Antes de começar qualquer fase:

1. ler `CLAUDE.md`;
2. ler `Docs/GDD_PROJECT_RESORT_MASTER.md`;
3. ler este índice;
4. ler o arquivo da fase atual;
5. verificar o estado real da branch e do working tree;
6. preservar trabalho já existente;
7. executar, testar, documentar e commitar.

## Ordem

1. `01_AUDITORIA_E_BASE.md`
2. `02_VERTICAL_SLICE_QUIOSQUE.md`
3. `03_ECONOMIA_FORNECEDORES.md`
4. `04_FUNCIONARIOS_INICIAIS.md`
5. `05_EXPANSAO_DE_TERRENO.md`
6. `06_POUSADA_VERTICAL_SLICE.md`
7. `07_CONSTRUCAO_MODULAR.md`
8. `08_HOTEL_COMPLETO.md`
9. `09_PISCINA_LAZER_E_PRAIA.md`
10. `10_RESORT_OPERACIONAL.md`
11. `11_RESORT_DE_LUXO.md`
12. `12_VIDA_PESSOAL_E_PATRIMONIO.md`
13. `13_MUNDO_VIVO_E_SAZONALIDADE.md`
14. `14_ENDGAME_CINCO_ESTRELAS.md`
15. `15_POLIMENTO_UX_AUDIO_VISUAL.md`
16. `16_OTIMIZACAO_QA_E_ESCALA.md`
17. `17_DEMO_STEAM.md`
18. `18_PRE_LANCAMENTO_E_RELEASE.md`

## Gate universal

Nenhuma fase é concluída apenas porque o código compila.

Cada fase precisa, quando aplicável:

- compilar;
- executar;
- jogar;
- testar save/load;
- testar progressão;
- validar ausência de duplicação de dinheiro/itens;
- verificar visualmente;
- medir performance;
- registrar limitações;
- gerar capturas reais da Unity;
- produzir relatório curto;
- commitar tudo.

## Regra de escopo

Não implementar sistemas de fases futuras só porque parecem interessantes. Preparar interfaces e dados é permitido quando necessário para evitar retrabalho, mas o foco deve permanecer na fase atual.

## Regra de branches

A branch `main` está desatualizada e não representa o estado mais avançado.

Antes de iniciar, comparar quando necessário com:
- `gpt/unity-world-integration`
- `codex/unity-world-integration-validation`
- `codex/vertical-slice-qa`
- `claude/w1-masterplan`

Nunca sobrescrever trabalho local não commitado.
