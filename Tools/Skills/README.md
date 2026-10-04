# Tools/Skills — biblioteca curada (Etapa B, 2026-10-03)

Biblioteca técnica de skills, workflows, ferramentas e referências para Facility Ops / Simulador Predial.
Documentação completa: `Docs/SKILLS/00_INDICE_GERAL.md` … `22_RECOMENDACOES.md`.

## Regras
- **Nada aqui está ativo.** O Claude Code só carrega skills de `.claude/skills/`. Para ativar, copie a pasta da skill para `.claude/skills/<nome>/` **depois de aprovação explícita**, revisando `allowed-tools` e comandos `` !`…` ``.
- Nada foi instalado e nenhum código externo foi executado. Os metadados vieram de `gh api` (somente leitura).
- Só foi copiado **markdown com licença permissiva (MIT)**, com `LICENSE` e `PROVENANCE.md` (commit fixado + SHA-256 do tarball). Scripts, hooks e binários foram removidos.
- Nenhuma credencial é armazenada. MCPs que exigem token ficam `DO_NOT_INSTALL`.
- Recursos externos usados no jogo entram em `asset_license_registry.csv`.

## Estrutura
| Caminho | Conteúdo |
|---|---|
| `catalog.json` | 102 itens com URL, autor, licença, versão/commit, data, prioridade, segurança, valor, riscos (gerado) |
| `build_catalog.py` + `guides_pt.py` | gerador do catálogo e dos documentos `Docs/SKILLS/` |
| `sources/github_metadata_2026-10-03.json` | metadados brutos coletados do GitHub |
| `claude/santa-aurora-world-pipeline/` | skill própria: pipeline do mundo |
| `claude/superpowers-subset/` | 4 skills de metodologia (MIT, obra/superpowers v6.4.2) |
| `blender/blender-headless-bpy/` | skill própria: padrões bpy validados no Blender 5.2 |
| `unity/nice-wolf-unity-claude-skills/` | 35 skills Unity 6 (MIT, commit `a149d3e`) |
| `pipeline/blender-to-unity-export/` | skill própria: convenções de exportação (plano, validar na W5) |
| `qa/visual-review/` | skill própria: capturas reais + regressão visual |
| `steam/` | só referências (integração Steam fica para depois) |
| `asset_license_registry.csv` | registro de origem e licença de qualquer recurso externo |

## Classificação
- Prioridade: `ESSENTIAL`, `RECOMMENDED`, `OPTIONAL`, `REJECTED`.
- Segurança: `SAFE_TO_USE`, `REVIEW_REQUIRED`, `DO_NOT_INSTALL`.

## Regenerar
```
python Tools/Skills/build_catalog.py .
```
