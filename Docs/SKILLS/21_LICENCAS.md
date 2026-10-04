# 21 — Licenças e registro de origem

## Política
- **Uso comercial permitido e claro** é pré-requisito: CC0, MIT, Apache-2.0, BSD, zlib e ISC são aceitos. CC-BY só com atribuição registrada nos créditos.
- **GPL/AGPL**: ferramentas GPL (Blender, BAT, add-ons) podem ser *usadas*; o que produzimos com elas é nosso. **Não copiar código GPL/AGPL para o jogo nem para o repositório.** Ex.: AI-SKILL-blender (AGPL) fica só como referência online.
- **Sem licença declarada = não copiar** (ex.: Citronetic/unity-claude-skill).
- **Licenças Unity** (Companion/Package Distribution/Reference-only): usar como pacotes; código reference-only só para leitura.
- **Marketplaces** (Fab/Megascans, Substance, Sketchfab): revisar termos asset a asset antes de qualquer uso; nada de assets cuja licença proíba redistribuição em build.
- **Dados geográficos reais** (OSM/ODbL, DEMs com restrições): proibidos como conteúdo de Santa Aurora.
- **VEIN**: referência de qualidade visual apenas, nenhum asset, textura, layout, mapa ou identidade.

## Registro persistente
Todo recurso externo que entrar no projeto (textura, HDRI, modelo, fonte, som, código) é registrado em `Tools/Skills/asset_license_registry.csv` com: `id, tipo, nome, url, autor, licença, versão/commit/data, onde é usado, atribuição exigida, revisado_por, data`. Skills salvas têm `LICENSE` + `PROVENANCE.md` com commit e SHA-256.

## Segurança de dependências (checklist antes de salvar ou instalar)
1. Repositório oficial, autor identificável, atividade recente, não arquivado (ou anotado).
2. Licença lida no arquivo LICENSE (não só no SPDX do GitHub).
3. Fixar commit ou tag; registrar hash do pacote baixado.
4. Varredura: binários desconhecidos, scripts ofuscados, downloads em tempo de execução, `allowed-tools` amplos, `` !`comando` ``, hooks.
5. Nada de tokens ou credenciais no repositório; MCPs que pedem token ficam DO_NOT_INSTALL sem autorização.
6. Executar só depois de revisão, e em branch isolada.

## Ferramentas de conformidade
| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [REUSE (FSFE)](https://github.com/fsfe/reuse-tool) | GPL-3.0-or-later (ferramenta; dados CC0) | v6.2.0 / `61c9abeaa937` | 2026-10-01 | **OPTIONAL** | REVIEW_REQUIRED | referência | Conformidade de licenças com SPDX. |

**Riscos**

- **REUSE (FSFE)**: Ferramenta GPL (não é distribuída com o jogo); um registro CSV próprio cobre o necessário agora.

