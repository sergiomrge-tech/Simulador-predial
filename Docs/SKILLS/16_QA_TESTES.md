# 16 — QA e testes automatizados

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

Já existem um smoke test de runtime (`RuntimeSmoke.cs`), `Tools/Test-Windows.ps1`, validadores Python (masterplan, rotas) e auditorias de reabertura no Blender.

## QA e testes automatizados

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| Skill própria: visual-review (`Tools/Skills/qa/visual-review/SKILL.md`) | Licença do repositório | 1.0 (2026-10-03) | — | **ESSENTIAL** | SAFE_TO_USE | salvo: `Tools/Skills/qa/visual-review` | Capturas reais, review sheets geradas de JSON e regressão visual com Pillow (já instalado). |
| [nowsprinting/claude-code-settings-for-unity](https://github.com/nowsprinting/claude-code-settings-for-unity) | Unlicense | (sem release) / `b6615fa78d76` | 2026-05-26 | **OPTIONAL** | SAFE_TO_USE | referência | Configurações/skills de um especialista em testes Unity; referência para fluxo de testes com Claude. |
| [Unity Test Framework 1.8.0](https://docs.unity3d.com/Packages/com.unity.test-framework@1.8/manual/index.html) | Unity Companion License | 1.8.0 (instalado) | — | **ESSENTIAL** | SAFE_TO_USE | referência | EditMode/PlayMode; smoke tests (RuntimeSmoke já existe), migração de saves, validadores de assets. |
| [Performance Testing Extension](https://docs.unity3d.com/Packages/com.unity.test-framework.performance@latest) | Unity Companion License | via Package Manager | — | **RECOMMENDED** | SAFE_TO_USE | referência | Medições de desempenho reproduzíveis em testes. |
| [Pillow (já instalado)](https://python-pillow.org/) | MIT-CMU (HPND) | 12.3.0 (instalado) | — | **ESSENTIAL** | SAFE_TO_USE | referência | Diferença de imagens/contato visual sem nova dependência. |
| [pixelmatch](https://github.com/mapbox/pixelmatch) | ISC | v7.2.0 / `b2800051f2b7` | 2026-09-15 | **OPTIONAL** | REVIEW_REQUIRED | referência | Diff perceptual de imagens. |
| [odiff](https://github.com/dmtrKovalenko/odiff) | MIT | v4.5.0 / `644c2348441b` | 2026-08-24 | **OPTIONAL** | REVIEW_REQUIRED | referência | Diff de imagens muito rápido. |
| [GameCI unity-test-runner](https://github.com/game-ci/unity-test-runner) | MIT | v4.3.2 / `365104178907` | 2026-10-03 | **OPTIONAL** | REVIEW_REQUIRED | referência | Testes Unity em CI. |

**Riscos**

- **nowsprinting/claude-code-settings-for-unity**: Repositório arquivado.
- **pixelmatch**: Node; Pillow cobre o necessário.
- **odiff**: Binário nativo; só se o volume exigir.
- **GameCI unity-test-runner**: Mesmo requisito de licença/segredos.

## Workflow recomendado

- **EditMode**: regras de serviço, economia, migração de saves com fixtures, validação de catálogos e IDs.
- **PlayMode**: cena determinística de smoke (carregar célula, entrar no lar, aceitar chamado, salvar e recarregar).
- **Validadores de assets** (AssetPostprocessor + testes): escala, UV, materiais, colisores, LOD, orçamento de vértices e texturas, nomes.
- **Regressão visual**: capturas por câmera fixa + diff Pillow (skill `visual-review`).
- **Separação de dados**: testes nunca tocam o progresso do jogador (perfil de teste isolado — regra do CLAUDE.md).

