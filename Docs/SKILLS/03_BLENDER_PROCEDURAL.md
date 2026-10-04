# 03 — Blender: procedural e Geometry Nodes

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

Santa Aurora já é procedural: ruas, calçadas, cruzamentos, lotes, famílias, infraestrutura e vegetação vêm de `Tools/Map/` (Python determinístico) e são instanciados por Geometry Nodes. Add-ons procedurais de terceiros duplicariam essa base.

## Blender: procedural e Geometry Nodes

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Geometry Nodes (nativo)](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html) | GPL (parte do Blender) | 5.2 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Instancing em massa (já usado para 13k edificações), scattering, cabos, cercas, variação procedural. |
| [building_tools](https://github.com/ranjian0/building_tools) | MIT | v1.0.13 / `0216534645b1` | 2026-09-24 | **OPTIONAL** | REVIEW_REQUIRED | referência | Gerador procedural de edifícios (paredes, janelas, portas, escadas); ideias para heróis futuros. |
| [Sverchok](https://github.com/nortikin/sverchok) | GPL-3.0 | v1.4.0 / `edc6e443e5e2` | 2026-09-24 | **OPTIONAL** | REVIEW_REQUIRED | referência | Nós paramétricos avançados. |
| [Parish & Müller — Procedural Modeling of Cities (SIGGRAPH 2001)](https://doi.org/10.1145/383259.383292) | Artigo acadêmico (citar) | 2001 | — | **RECOMMENDED** | SAFE_TO_USE | referência | Fundamento de redes viárias L-system e lotes; base conceitual do nosso gerador. |
| [WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) | MIT | v1.00 / `de7d22e705e8` | 2026-03-22 | **OPTIONAL** | SAFE_TO_USE | referência | Geração por restrições (fachadas, interiores). |
| [TownGeneratorOS](https://github.com/watabou/TownGeneratorOS) | GPL-3.0 | (sem release) / `7fbc87a9398c` | 2021-01-09 | **OPTIONAL** | DO_NOT_INSTALL | referência | Gerador de cidades medievais (ideias de malha). |

**Riscos**

- **building_tools**: Sobrepõe nosso gerador próprio (sa_arch); adicionar dependência sem necessidade.
- **Sverchok**: GPL-3; Geometry Nodes nativo cobre o necessário.
- **TownGeneratorOS**: GPL-3: não copiar código; só inspiração.

## Workflow recomendado

- **Ruas e calçadas**: grafo → faixas de pista, calçadas elevadas 15 cm com meio-fio, esquinas e faixas de pedestre (já em `create_oldtown_base.py`). Próximo passo: esquinas curvas (filete) e rebaixos de calçada em garagens.
- **Postes, fios e cabos**: pontos já gerados; cabos entre postes por catenária (Curve com 8–12 pontos, flecha de 0,5–1,0 m) num grupo GN *Curve to Mesh*.
- **Muros e cercas**: GN *Resample Curve* + *Instance on Points* com peças do kit (`KIT_Muro_2m`, pilares).
- **Fachadas**: variação por seed (variantes) + quebra de repetição com decals e acessórios (condensadores, toldos, placas) distribuídos por regras, não por acaso.
- **Scattering**: distribuição por máscaras (calçada, praça, terreno vazio) com distância mínima (*Distribute Points on Faces* em modo Poisson).
- **Sinalização e infraestrutura**: regras por tipo de cruzamento (já: semáforo em principal×principal, PARE em local→principal).
- Referência conceitual: Parish & Müller (2001). WFC pode ajudar em interiores repetitivos.

