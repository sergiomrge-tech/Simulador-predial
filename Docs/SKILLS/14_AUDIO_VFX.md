# 14 — Áudio, VFX e clima

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O áudio vende os sistemas técnicos: zumbido elétrico, bombas, HVAC, chuva e trânsito distante.

## Áudio, VFX e clima

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [VFX Graph](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@latest) | Unity Companion License | via Package Manager | — | **OPTIONAL** | SAFE_TO_USE | referência | Chuva/faíscas/vapor em grande escala (GPU). |
| [Steam Audio](https://github.com/ValveSoftware/steam-audio) | Apache-2.0 | v4.8.1 / `480dd64f513c` | 2026-03-25 | **RECOMMENDED** | REVIEW_REQUIRED | referência | Oclusão/transmissão/reverb físico para interiores técnicos (bombas, HVAC, zumbido elétrico). |
| [FMOD Studio](https://www.fmod.com/licensing) | Proprietária (licença indie gratuita até limite de receita) | — | — | **OPTIONAL** | REVIEW_REQUIRED | referência | Áudio adaptativo/zonas de ambiente. |

**Riscos**

- **Steam Audio**: Plugin nativo; avaliar custo de CPU.
- **FMOD Studio**: Licença por faturamento; o mixer nativo da Unity + Steam Audio cobre o início.

**Notas**

- **VFX Graph**: Para efeitos pequenos (vazamento, faísca, poeira) o Particle System nativo basta.

## Workflow recomendado

- Zonas de ambiente por célula e por interior; loops de máquinas com variação; oclusão e transmissão via Steam Audio (avaliar o custo de CPU) ou raycast simples no início.
- Passos por material da superfície (tags nos materiais da biblioteca).
- **VFX**: Particle System para faíscas fictícias, vapor, vazamento, poeira e condensação; VFX Graph só para chuva em larga escala.
- **Clima**: gerenciador com estados (ensolarado, nublado, chuva, tempestade, onda de calor, neblina) que alimenta gameplay (chamados, falhas) e visual (molhado, neblina, iluminação). O orçamento de partículas segue a distância.

