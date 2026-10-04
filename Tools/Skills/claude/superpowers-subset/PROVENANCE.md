# Procedência — obra/superpowers (subconjunto)

| Campo | Valor |
|---|---|
| Origem | https://github.com/obra/superpowers |
| Autor | Jesse Vincent (obra) e contribuidores |
| Licença | MIT (arquivo `LICENSE` copiado sem alterações) |
| Versão | release `v6.4.2`; commit fixado `8ca22dba9a94f28898bbce59f2537ff4d87c747d` (último push 2026-09-27) |
| SHA-256 do tarball baixado | `99daa57ea03b6f1a68f9f201cea24fa4b56910b8c1cabb7465df857e0f221178` |
| Data da cópia | 2026-10-03 |

## O que foi copiado (só markdown)
- `skills/systematic-debugging/`: método de depuração por causa raiz.
- `skills/verification-before-completion/`: só declarar "pronto" com evidência.
- `skills/test-driven-development/`: ciclo de testes antes do código.
- `skills/writing-plans/`: planos executáveis por etapas.

## Removido da cópia
- `systematic-debugging/find-polluter.sh` e `condition-based-waiting-example.ts`: código executável/exemplo em TS, fora da política "só markdown". Os textos que citam esses arquivos ficam como referência conceitual.
- O restante do plugin (hooks, agentes, comandos e brainstorming) não foi copiado, porque instala hooks e altera o fluxo do Claude Code. É REVIEW_REQUIRED.

## Verificação feita
- Nenhum `allowed-tools`, `` !`comando` `` ou download nos SKILL.md copiados.

## Ativação
Inerte em `Tools/Skills/`. Para ativar, copie a skill escolhida para `.claude/skills/` depois de aprovação.
