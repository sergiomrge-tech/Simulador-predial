# 13 — UI/UX, tablet e mapa

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O `TabletUI.cs` é provisório. A migração planejada é para UI Toolkit antes de polir.

## UI/UX

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [UI Toolkit (nativo)](https://docs.unity3d.com/6000.6/Documentation/Manual/UIElements.html) | Unity EULA | 6000.6 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Migração do tablet provisório (TabletUI.cs) — job board, inventário, finanças, mapa. |

## Workflow recomendado

- UI Toolkit (UXML/USS) para tablet, job board, inventário, finanças, imóveis, lojas e configurações; tema único com tokens de cor e escala de fonte.
- **Mapa/GPS**: conversão mundo→mapa linear (8×8 km com origem no centro, já definida); camadas de distritos, POIs, chamados e imóveis; filtros; rota pelo grafo viário (Dijkstra já existe em Python e vira um serviço C# na W5).
- **Minimapa**: render ortográfico pré-gerado por célula (tiles do masterplan) em vez de câmera em tempo real.
- **Acessibilidade**: escala de fonte, alto contraste, indicadores de interação, legendas (doc 19).

