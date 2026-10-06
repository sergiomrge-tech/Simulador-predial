# Relatório — Fase 01: Auditoria e consolidação da base

Data: 2026-10-06. Gate: **PASS** (estado conhecido, sem risco de sobrescrita, base reproduzível).

## Estado do repositório
- Branch de produção do resort: **`claude/w1-masterplan`** (confirmada). Working tree limpo, nenhum stash, nenhum arquivo não rastreado relevante.
- Outras branches: `main` (desatualizada), `gpt/unity-world-integration`, `codex/unity-world-integration-validation`, `codex/vertical-slice-qa` (linhas de integração do mundo Unity; **não** mescladas aqui, nenhum trabalho delas foi sobrescrito).
- Remoto: mesclado duas vezes (GDD mestre e plano de execução) sem perda; os conflitos foram só no `CLAUDE.md` e resolvidos mantendo o texto oficial.
- Disco: crítico (≈ 650 MB livres). Mitigações: `gc.auto 0` no repositório; `.blend` do resort fora do Git (regeneráveis por script).

## Cenas e sistemas encontrados
- `Bootstrap.unity` (legado, manutenção) — intacta.
- `ResortPrologue.unity` (jogo do resort em primeira pessoa) e `ResortSite.unity` (protótipo RTS/grid, opcional) — geradas por `Resort Aurora > Create ... Scene`.

## Mapa — reaproveitado e criado
| Área | Situação |
|---|---|
| Unity 6000.6.2f1, URP, Input System | mantidos |
| Primeira pessoa, interação por raio, CharacterController | nova implementação enxuta no namespace `ResortAurora` (`Game/PlayerController.cs`, `Interactable.cs`); o `Interaction.cs` legado não foi tocado |
| Save versionado | novo `SaveStore` JSON próprio (escrita atômica, `.bak`), separado do save legado; campos novos têm valor padrão (saves antigos carregam) |
| Mundo Santa Aurora, terreno, vias, vila | `Tools/Map/export_resort_site.py` (terreno real do masterplan, bairro das Palmeiras, parcelas) |
| Pipeline Blender → Unity | `Tools/Blender/*` (kit do resort, estágios, exportação FBX, texturas PBR reaproveitadas) |
| Testes | `Tests/PlayMode` (prólogo, estágios, quiosque, desempenho, pousada, interior) + `ResortSimSmokeTest` |

## Sistemas legados isolados (não removidos)
`Core/` (ChapterOne, ServiceSession, SaveService), `Runtime/` (CampaignMap, Interaction, TabletUI, WorldBuilder) e a cena `Bootstrap`: congelados, sem dependência do resort, reaproveitáveis como subsistema futuro de manutenção.

## Conflitos entre documentação antiga e nova
- `GDD_RESORT_SANTA_AURORA.md` (v1) e `GDD_RESORT_V2...` falam em modo Planta/RTS como principal; **o GDD mestre prevalece: primeira pessoa**. O protótipo RTS (R0/R1) fica como ferramenta opcional.
- `CLAUDE.md` oficial vale sobre o texto antigo de manutenção.

## Riscos
Disco cheio; interiores só no saguão do Grande Hotel, na suíte e no sobrado; UI provisória (IMGUI); equilíbrio sem teste humano.
