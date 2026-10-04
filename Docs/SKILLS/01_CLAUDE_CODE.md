# 01 — Claude Code, Agent Skills e MCP

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O Claude Code carrega skills de `.claude/skills/` (projeto), `~/.claude/skills/` (usuário) e de plugins. **Por isso a biblioteca fica em `Tools/Skills/`: guardada, versionada e inerte.** Ativar uma skill é copiá-la para `.claude/skills/`, sempre com aprovação, e revisando o campo `allowed-tools` e qualquer `` !`comando` `` (a documentação oficial alerta que skills podem executar comandos).

## Claude Code, Agent Skills e MCP

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| Skill própria: santa-aurora-world-pipeline (`Tools/Skills/claude/santa-aurora-world-pipeline/SKILL.md`) | Licença do repositório | 1.0 (2026-10-03) | — | **ESSENTIAL** | SAFE_TO_USE | salvo: `Tools/Skills/claude/santa-aurora-world-pipeline` | Codifica o pipeline do mundo (validação, geradores, reabertura, capturas, convenções de IDs/células). |
| [Anthropic Agent Skills (oficial)](https://github.com/anthropics/skills) | Apache-2.0 (maioria das skills) + source-available (docx/pdf/pptx/xlsx) | (sem release) / `8a1541c4a3ff` | 2026-10-03 | **RECOMMENDED** | SAFE_TO_USE | referência | Fonte oficial de skills e do padrão SKILL.md; skill-creator, mcp-builder e webapp-testing úteis para criar skills próprias. |
| [Documentação Claude Code (skills, hooks, permissões)](https://code.claude.com/docs/en/skills) | Proprietário (documentação) | consultado 2026-10-03 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Regras de carregamento de skills (.claude/skills), frontmatter, allowed-tools, segurança de skills de terceiros. |
| [obra/superpowers (subconjunto salvo)](https://github.com/obra/superpowers) | MIT | v6.4.2 / `8ca22dba9a94` | 2026-09-27 | **RECOMMENDED** | SAFE_TO_USE | salvo: `Tools/Skills/claude/superpowers-subset` | Metodologia: systematic-debugging, verification-before-completion, TDD, writing-plans. Reforça gates com evidência. |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | MIT | (sem release) / `fd4c28d3be55` | 2026-10-02 | **OPTIONAL** | SAFE_TO_USE | referência | Descoberta de skills oficiais/comunidade (1000+). |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | sem licença declarada | (sem release) / `1da55aa810f2` | 2026-04-28 | **OPTIONAL** | SAFE_TO_USE | referência | Lista de skills e recursos. |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | sem licença declarada | (sem release) / `be2a406907db` | 2026-09-18 | **OPTIONAL** | SAFE_TO_USE | referência | Lista grande por categoria. |
| [ahujasid/blender-mcp](https://github.com/ahujasid/mcp-for-blender) | MIT | (sem release) / `60d2a31b4632` | 2026-09-30 | **OPTIONAL** | DO_NOT_INSTALL | referência | Controle do Blender aberto via MCP (popular, 29,9k estrelas). |
| [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | MIT | v10.2.0 / `842aa4be56aa` | 2026-10-04 | **OPTIONAL** | REVIEW_REQUIRED | referência | Controle do Editor Unity via MCP (cenas, assets, console); pode acelerar W5. |
| [IvanMurzak/Unity-MCP](https://github.com/IvanMurzak/Unity-MCP) | Apache-2.0 | 0.93.2 / `8d0cdd57798d` | 2026-10-04 | **OPTIONAL** | REVIEW_REQUIRED | referência | Alternativa Apache-2.0 ao unity-mcp. |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | MIT -> Apache-2.0 (transição) | 2026.8.31 / `f46d9578190b` | 2026-10-01 | **REJECTED** | DO_NOT_INSTALL | referência | Servidores de referência MCP. |

**Riscos**

- **Anthropic Agent Skills (oficial)**: Skills de documento são source-available (não copiar para redistribuição).
- **obra/superpowers (subconjunto salvo)**: Plugin completo instala hooks e altera fluxo -> não instalar; subconjunto markdown salvo sem scripts.
- **VoltAgent/awesome-agent-skills**: Lista; cada item exige revisão própria.
- **ahujasid/blender-mcp**: Socket que executa Python arbitrário dentro do Blender; integrações opcionais com chaves de API. Desnecessário: usamos bpy headless versionado.
- **CoplayDev/unity-mcp**: Instala pacote Unity + servidor Python (uv); execução de comandos no Editor. Avaliar em branch isolada.
- **IvanMurzak/Unity-MCP**: Mesmo perfil de risco (execução no Editor).
- **modelcontextprotocol/servers**: Filesystem/git redundantes com ferramentas nativas do Claude Code.

**Instalação (somente com aprovação)**

- **Skill própria: santa-aurora-world-pipeline**: Copiar a pasta para .claude/skills/ quando aprovado.
- **Anthropic Agent Skills (oficial)**: /plugin marketplace add anthropics/skills (só com aprovação); várias já estão disponíveis na sessão como anthropic-skills:*

## Workflow recomendado

1. **Skills próprias primeiro.** Elas descrevem o *nosso* pipeline (validadores, geradores, convenções), exatamente o que skills genéricas não sabem.
2. Skills de terceiros: só markdown, licença permissiva, commit fixado, `PROVENANCE.md` com hash do tarball e varredura de shell injection/allowed-tools. Scripts e hooks ficam de fora.
3. MCPs: o projeto já automatiza Blender (bpy headless versionado) e GitHub (`gh` autenticado). MCPs de controle do Blender ou da Unity aumentam a superfície de execução. Avaliar o `unity-mcp` só na etapa W5, em branch isolada.
4. Toda skill nova passa pela checagem `claude plugin validate` (quando for plugin) e por revisão humana antes de ir para `.claude/skills/`.

