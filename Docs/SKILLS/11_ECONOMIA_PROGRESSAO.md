# 11 — Economia, progressão e imóveis

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

Regra do projeto: **difícil, porém sempre recuperável**. A economia precisa ser provada por simulação antes de ser exposta ao jogador.

## Economia e progressão

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| Simulador de economia próprio (Python, a criar) (`(a criar em Tools/Balance/)`) | Licença do repositório | planejado | — | **RECOMMENDED** | SAFE_TO_USE | referência | Rodar milhares de carreiras simuladas (chamados, custos, reputação) para provar 'difícil porém recuperável' e ausência de softlock. |
| [Machinations](https://machinations.io/) | Proprietária (planos) | — | — | **OPTIONAL** | REVIEW_REQUIRED | referência | Modelagem visual de economias de jogos. |

**Riscos**

- **Machinations**: Dados do design em serviço externo.

## Workflow recomendado

- Simulador Python próprio (`Tools/Balance/`, a criar): milhares de carreiras com políticas de jogador (cautelosa, gananciosa, desastrada) medindo caixa, dívida, reputação e tempo até cada desbloqueio.
- Anti-softlock: sempre há chamados baratos acessíveis a pé; o crédito tem limite; ferramentas essenciais nunca saem do mercado; falência leva a recomeço parcial, nunca a beco sem saída.
- Transações seguras para o save: operação atômica (débito + item) registrada no mesmo commit do save.
- Imóveis e lar: estados H0–H4 já têm slots no lar; compras viram objetos físicos; imóveis antigos continuam existindo; garagens com vagas reais.
- Progressão aberta: o mercado livre oferece 3–5 chamados por região desbloqueada; a curva de dificuldade segue reputação, ferramentas e veículo (GDD).

