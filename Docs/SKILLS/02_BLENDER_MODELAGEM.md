# 02 — Blender: modelagem, arquitetura, kits e salas técnicas

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

A modelagem de produção segue a Art Bible: escala métrica, bordas chanfradas, espessura real, peças separadas onde a câmera chega perto. O W1.5 já criou o construtor paramétrico (`Tools/Blender/sa_arch.py`), o kit modular (`sa_kit.py`) e os heróis (`sa_heroes.py`). A estratégia é **automação própria + autoria manual nos heróis**, não add-ons genéricos.

## Blender: modelagem, arquitetura e kits

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| Skill própria: blender-headless-bpy (`Tools/Skills/blender/blender-headless-bpy/SKILL.md`) | Licença do repositório | 1.0 (2026-10-03) | — | **ESSENTIAL** | SAFE_TO_USE | salvo: `Tools/Skills/blender/blender-headless-bpy` | Padrões bpy validados no Blender 5.2: malha eficiente, UV métrico, bevel bmesh, GN instancing (correção 5.x), cor, assets, auditoria. |
| [donth77/blender-game-skills](https://github.com/donth77/blender-game-skills) | MIT | (sem release) / `f0ef29385a03` | 2026-09-26 | **OPTIONAL** | REVIEW_REQUIRED | referência | Concept art -> asset riggado; ideias de fases/gates para assets. |
| [LevyBytes/AI-SKILL-blender](https://github.com/LevyBytes/AI-SKILL-blender) | AGPL-3.0 | (sem release) / `59dda21f5282` | 2026-06-22 | **OPTIONAL** | DO_NOT_INSTALL | referência | Referência extensa da API bpy organizada em subskills. |
| [Blender 5.2.1 LTS](https://www.blender.org/download/lts/) | GPL-2.0-or-later (arquivos gerados são do autor) | 5.2.1 LTS (build 2026-08-25) | — | **ESSENTIAL** | SAFE_TO_USE | referência | Ferramenta principal de modelagem/geração; já instalada; LTS garante estabilidade da API. |
| [Blender Python API 5.2](https://docs.blender.org/api/5.2/) | CC-BY-SA (documentação) | 5.2 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Referência oficial bpy/bmesh/GN. |

**Riscos**

- **donth77/blender-game-skills**: Muito novo (0 estrelas), inclui scripts; fluxo image-to-3D fora da direção autoral.
- **LevyBytes/AI-SKILL-blender**: AGPL-3.0: não copiar para o repositório; consultar online apenas.

**Instalação (somente com aprovação)**

- **Skill própria: blender-headless-bpy**: Copiar para .claude/skills/ quando aprovado.
- **Blender 5.2.1 LTS**: Já instalado em C:/Program Files/Blender Foundation/Blender 5.2

**Notas**

- **Blender 5.2.1 LTS**: Fixar a série 5.2 LTS durante W2–W4.

## Workflow recomendado

**Hard-surface e arquitetura (heróis, W2–W4)**
- Bevel com perfil e 2–3 segmentos nas quinas visíveis; *weighted normals* (modificador nativo) para sombreamento limpo; sharp edges por ângulo de 30–35°.
- Kit modular com grade de 0,5 m e alturas de piso de 3,0 m (residencial) e 4–5 m (comercial/técnico); pivôs na face externa inferior; cada peça com LOD0 bevelado e LOD1 simplificado.
- Janelas e portas: batente, folha, vidro e peitoril como peças separadas (já assim no kit); grades com barras de 12–16 mm.
- Telhados com espessura, beiral, calha e rufos; telhas cerâmicas por textura + bump nos LODs distantes e geometria na borda/cumeeira de perto.
- Escadas: espelho de 17–18 cm e piso de 28 cm (regra 2E+P≈63 cm); corrimão a 0,90 m.

**Salas técnicas (diferencial do jogo)**
- Quadros elétricos, bombas, HVAC e geradores: modelar a partir de catálogos genéricos e de fotos *próprias* (nunca de assets de terceiros), com marcas fictícias.
- Tubulação por curvas (Curve → bevel circular de 16–24 lados de perto), flanges e suportes como peças instanciadas.
- Elementos interativos (registros, disjuntores, painéis) com pivô e eixo corretos para animação na Unity.

**Veículos, mobiliário e ferramentas**: hero props com 1024 px/m, desgaste coerente (Art Bible §7) e marcas fictícias.

