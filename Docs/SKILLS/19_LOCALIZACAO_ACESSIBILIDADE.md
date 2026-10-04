# 19 — Localização e acessibilidade

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O idioma base é português (pt-BR). A localização deve ser possível desde já, mas sem traduzir agora.

## Localização e acessibilidade

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Localization (com.unity.localization)](https://docs.unity3d.com/Packages/com.unity.localization@latest) | Unity Companion License | via Package Manager | — | **RECOMMENDED** | SAFE_TO_USE | referência | String tables, smart strings, plural, pseudo-localização para QA de expansão de texto. |
| [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/) | Leitura livre | web | — | **ESSENTIAL** | SAFE_TO_USE | referência | Legendas, remapeamento, contraste, movimento reduzido, indicadores de interação. |
| [Xbox Accessibility Guidelines](https://learn.microsoft.com/gaming/accessibility/guidelines) | Documentação | web | — | **RECOMMENDED** | SAFE_TO_USE | referência | Checklist detalhado de acessibilidade. |

## Workflow recomendado

- Unity Localization: string tables por domínio (UI, chamados, narrativa), smart strings para valores e plural, pseudo-localização para testar expansão de texto (+30–40%).
- Fontes com cobertura latina estendida; nada de texto embutido em textura (exceto marcas fictícias decorativas).
- Acessibilidade (Game Accessibility Guidelines/XAG): legendas com indicação de quem fala, remapeamento completo, sensibilidade, modos para daltonismo nos indicadores técnicos (não depender só de cor nos LEDs e quadros), escala de fonte, movimento reduzido (head bob e balanço de câmera), alto contraste e pistas sonoras.

