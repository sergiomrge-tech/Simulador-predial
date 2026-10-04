# 17 — Build, Git/GitHub e documentação

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

Build Windows por `Tools/Build.ps1` (batchmode). A branch de trabalho é `claude/w1-masterplan`, sem merge automático no `main`.

## Build, Git e GitHub

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [github/github-mcp-server](https://github.com/github/github-mcp-server) | MIT | v1.14.0 / `71ef8266e481` | 2026-10-03 | **REJECTED** | DO_NOT_INSTALL | referência | Operações GitHub via MCP. |
| Tools/Build.ps1 + Test-Windows.ps1 (existentes) (`Tools/Build.ps1`) | Licença do repositório | atual | — | **ESSENTIAL** | SAFE_TO_USE | referência | Build Unity em batchmode já funcional; base para smoke launch automatizado. |
| [GitHub Actions (validadores Python)](https://docs.github.com/actions) | Serviço GitHub | — | — | **RECOMMENDED** | SAFE_TO_USE | referência | Rodar validate_masterplan.py e build_catalog.py a cada push (sem licença Unity, sem segredos). |
| [GameCI unity-builder](https://github.com/game-ci/unity-builder) | MIT | v6.0.0 / `ae0171202cd8` | 2026-09-16 | **OPTIONAL** | REVIEW_REQUIRED | referência | Build Unity em CI. |
| [Git LFS](https://github.com/git-lfs/git-lfs) | MIT | v3.8.0 / `0043a6450479` | 2026-10-01 | **RECOMMENDED** | REVIEW_REQUIRED | referência | Para binários grandes futuros (texturas 4K, FBX, .blend de produção). Instalado (3.7.1), ainda não usado. |
| [github/gitignore (Unity.gitignore)](https://github.com/github/gitignore) | CC0-1.0 | (sem release) / `0e5d690153ca` | 2026-10-02 | **RECOMMENDED** | SAFE_TO_USE | referência | Comparar com o .gitignore atual. |

**Riscos**

- **github/github-mcp-server**: Exige token; redundante com o gh CLI já autenticado.
- **GameCI unity-builder**: Exige ativação de licença Unity como segredo no GitHub; decidir com o usuário.
- **Git LFS**: Não reescrever histórico existente; cota de banda/armazenamento do GitHub; decidir com o usuário antes de ativar.

**Instalação (somente com aprovação)**

- **GitHub Actions (validadores Python)**: Workflow .github/workflows/ (propor com aprovação; não depende de credenciais).

## Documentação

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Keep a Changelog](https://github.com/olivierlacan/keep-a-changelog) | MIT | v1.1.1 / `08d0df5a7e93` | 2026-09-07 | **RECOMMENDED** | SAFE_TO_USE | referência | Formato de CHANGELOG por marco (W1, W1.5...). |
| [Architecture Decision Records (modelos)](https://github.com/architecture-decision-record/architecture-decision-record) | sem SPDX (ver repositório) | (sem release) / `464354b7d949` | 2026-09-25 | **RECOMMENDED** | SAFE_TO_USE | referência | Registrar decisões (terreno, streaming, LFS) em Docs/ADR/NNNN-*.md com um template próprio. |
| [adr-tools](https://github.com/npryce/adr-tools) | GPL-3.0 | 3.0.0 / `b3279baf9be2` | 2024-04-25 | **OPTIONAL** | REVIEW_REQUIRED | referência | CLI para ADRs. |

**Riscos**

- **adr-tools**: GPL-3 e bash; um template markdown basta.

## Workflow recomendado

- **CI barato e sem segredos**: GitHub Actions rodando `validate_masterplan.py` e `build_catalog.py` a cada push (Python puro). Builds Unity em CI (GameCI) só com decisão do usuário sobre a licença Unity como segredo.
- **Binários**: hoje os `.blend` vão como binários normais (`.gitattributes`). Git LFS (3.7.1 instalado) para texturas e FBX de produção, **sem reescrever o histórico**. Decidir com o usuário considerando a cota do GitHub.
- **Versionamento de build**: `major.minor.patch+commit` injetado pelo `Build.ps1`; smoke launch automático após o build.
- **Documentação**: relatório por marco (padrão W1/W1.5); CHANGELOG no formato Keep a Changelog; ADRs curtos em `Docs/ADR/` para decisões duráveis (relevo, streaming, LFS, Steam).

