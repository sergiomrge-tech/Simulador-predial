# 05 — PBR, UV, texturas e terreno

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

A biblioteca procedural (37 materiais) já tem slots nomeados `SLOT_BaseColor/Normal/Roughness/Metallic/AO` e pasta-alvo `ArtSource/Textures/<material>/`. O W3 preenche esses slots com texturas autorais, de Material Maker ou de fontes CC0 registradas.

## PBR, UV e texturas

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [TexTools-Blender](https://github.com/franMarz/TexTools-Blender) | GPL-3.0 | v1.6.1 / `89cb4cfe486d` | 2024-12-02 | **OPTIONAL** | REVIEW_REQUIRED | referência | Utilitários de UV/texel density/bake. |
| [Material Maker](https://github.com/RodZill4/material-maker) | MIT | 1.7 / `4d29a8154898` | 2026-10-03 | **RECOMMENDED** | SAFE_TO_USE | referência | Autoria procedural de texturas PBR (tileables, trim sheets) exportando Base Color/Normal/Roughness/Metallic/AO para os slots já criados. |
| [ArmorPaint / ArmorTools](https://github.com/armory3d/armorpaint) | zlib (fonte); binários pagos | 26.09 / `81d27990be65` | 2026-10-02 | **OPTIONAL** | REVIEW_REQUIRED | referência | Pintura 3D PBR (fonte zlib; binários pagos). |
| [Poly Haven](https://polyhaven.com/license) | CC0-1.0 | por asset | — | **ESSENTIAL** | SAFE_TO_USE | referência | Texturas, HDRIs e modelos CC0 (uso comercial livre) — referência e base de materiais/iluminação. |
| [ambientCG](https://ambientcg.com/) | CC0-1.0 | por asset | — | **ESSENTIAL** | SAFE_TO_USE | referência | Materiais PBR CC0 (concreto, tijolo, asfalto, metal...). |
| [Kenney](https://kenney.nl/support) | CC0-1.0 | por pacote | — | **OPTIONAL** | SAFE_TO_USE | referência | Assets CC0 para protótipos/UI placeholder. |
| [Megascans / Fab](https://www.fab.com/) | Fab Standard License (qualquer engine; maioria paga desde 2025) | — | — | **REJECTED** | REVIEW_REQUIRED | referência | Scans fotogramétricos de altíssima qualidade. |
| [Adobe Substance 3D Painter/Designer](https://www.adobe.com/products/substance3d.html) | Assinatura comercial | — | — | **OPTIONAL** | REVIEW_REQUIRED | referência | Padrão da indústria para texturização. |

**Riscos**

- **TexTools-Blender**: Último push 2024-12 (risco de quebra no 5.2); GPL-3.
- **ArmorPaint / ArmorTools**: Compilar da fonte ou comprar; avaliar só se pintura 3D for necessária.
- **Kenney**: Estilo low-poly: nunca como arte final.
- **Megascans / Fab**: Termos e preços mudaram em 2024–2025; exige revisão jurídica e orçamento antes de qualquer uso.
- **Adobe Substance 3D Painter/Designer**: Custo recorrente; preferir open source/CC0 primeiro.

**Instalação (somente com aprovação)**

- **Material Maker**: Executável standalone fora do repositório; texturas exportadas entram em ArtSource/Textures/<material>/.

**Notas**

- **Poly Haven**: Registrar cada asset usado em Tools/Skills/asset_license_registry.csv (nome, URL, data).
- **ambientCG**: Registrar cada asset usado no registro de licenças.

## Terreno / GIS (apenas técnica)

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [BlenderGIS](https://github.com/domlysz/BlenderGIS) | GPL-3.0 | 2215 / `2add45ffec54` | 2025-12-20 | **OPTIONAL** | REVIEW_REQUIRED | referência | Técnica de DEM/OSM/georreferência (apenas estudo). |
| [A.N.T. Landscape (extensão)](https://extensions.blender.org/add-ons/antlandscape/) | GPL | extensão atual | — | **OPTIONAL** | SAFE_TO_USE | referência | Terrenos procedurais simples. |
| [OpenStreetMap (dados)](https://www.openstreetmap.org/copyright) | ODbL-1.0 | — | — | **REJECTED** | DO_NOT_INSTALL | referência | Dados urbanos reais. |
| [Unity Terrain Tools (com.unity.terrain-tools)](https://docs.unity3d.com/Packages/com.unity.terrain-tools@latest) | Unity Companion License | via Package Manager | — | **OPTIONAL** | SAFE_TO_USE | referência | Ferramentas de terreno Unity (se for usado Terrain em vez de malha Blender). |

**Riscos**

- **BlenderGIS**: Nunca importar cidade real como Santa Aurora; dados OSM são ODbL (share-alike).
- **OpenStreetMap (dados)**: Share-alike e cidade real: proibido como conteúdo de Santa Aurora; só estudo de técnica.

**Notas**

- **A.N.T. Landscape (extensão)**: Nosso relevo vem de sa_terrain.py (determinístico); usar só para estudos.
- **Unity Terrain Tools (com.unity.terrain-tools)**: Nosso terreno vem do Blender (malha por subcélula).

## Workflow recomendado

**Materiais**
- Tileables 2K (arquitetura 256–512 px/m), trim sheets para molduras, rodapés, frisos e chapas, decals (infiltração, ferrugem, óleo, rachaduras, sinalização) em atlas.
- Camadas: base + sujeira por cavidade (AO/curvatura) + sujeira de rodapé + desgaste de borda; molhado por roughness/darkening (Shader Graph na Unity).
- Concreto, tijolo, asfalto, metal, ferrugem, vidro, madeira, cerâmica e plástico: começar por ambientCG/Poly Haven (CC0), ajustar no Material Maker, registrar origem.

**UV e baking**
- UVs métricos já existem em toda a geometria (projeção de caixa). Heróis ganham *unwrap* manual com texel density uniforme e ilhas alinhadas a trim sheets.
- UDIM só em heróis enormes, se necessário; o padrão é atlas e trim.
- Bake de normal e AO no próprio Blender (Cycles) de high para low; mapas Roughness/Metallic/AO lineares, Normal no padrão OpenGL (Unity espera Y+; o Blender exporta OpenGL).
- Compressão na Unity: BC7 (cor), BC5 (normal), máscaras empacotadas (R=Metallic, G=AO, A=Smoothness no URP Lit).

**Terreno / GIS (apenas técnica)**
- Nosso relevo vem de `sa_terrain.py` (determinístico, dirigível). BlenderGIS e DEM servem para estudar técnica de drenagem e erosão, nunca para importar cidade real. Dados OSM (ODbL) estão proibidos como conteúdo.

