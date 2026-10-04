# Procedência — Nice-Wolf-Studio/unity-claude-skills

| Campo | Valor |
|---|---|
| Origem | https://github.com/Nice-Wolf-Studio/unity-claude-skills |
| Autor | Nice-Wolf-Studio |
| Licença | MIT (arquivo `LICENSE` copiado sem alterações) |
| Commit fixado | `a149d3e995420432f52b0899092daa4b069f441f` (branch `main`, último push 2026-09-15) |
| SHA-256 do tarball baixado | `ac892cbf201ddcae6a5263f62f83cfe4bac6104d756014210d71e83f312e4c6a` |
| Data da cópia | 2026-10-03 |
| Base declarada | documentação do Unity 6.3 LTS (o projeto usa Unity 6000.6.2f1; conferir APIs novas) |

## O que foi copiado
- `skills/` inteiro (35 skills em markdown: SKILL.md + `references/`).
- `LICENSE` e `UPSTREAM_README.md`.

## O que NÃO foi copiado (motivo)
- `unity-ops/` (plugin com `hooks/hooks.json` e scripts shell de teste): executa comandos, então é REVIEW_REQUIRED e não deve ser ativado sem revisão.
- `.claude-plugin/plugin.json` e `audit/`: metadados do marketplace, desnecessários.

## Verificação feita
- Nenhum `` !`comando` ``, bloco ```` ```! ````, `allowed-tools`, `curl`, `wget` ou `Invoke-WebRequest` nos SKILL.md copiados.
- Nenhum arquivo de código (.py/.sh/.ps1/.js/.cs/.exe/.dll) na cópia.

## Ativação
**Inerte por padrão.** O Claude Code só carrega skills de `.claude/skills/`. Para ativar uma skill, depois de aprovação do usuário, copie a pasta dela para `.claude/skills/<nome>/`. Não ative as 35 de uma vez: escolha as necessárias para a etapa (ex.: `unity-scene-assets`, `unity-performance`, `unity-testing`, `unity-save-system` na integração W5).
