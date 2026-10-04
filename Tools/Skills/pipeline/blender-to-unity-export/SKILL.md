---
name: blender-to-unity-export
description: >
  Convenções planejadas para exportar a Cidade Antiga do Blender para a Unity (FBX por subcélula/camada, escala,
  eixos, pivôs, LOD, colisores, materiais, manifesto, AssetPostprocessor). Use ao preparar a integração Unity
  (W5). Estado: PLANO, ainda não validado na Unity.
---

# Blender → Unity (plano W1.5, validar antes de produzir em massa)

## Princípios
- A fonte é sempre o `.blend` + o manifesto (`OldTown/oldtown_streaming_manifest_v1.json`). Nada é editado à mão na Unity sem voltar à fonte.
- Escala real 1 m = 1 unidade. Teste com um cubo de 1 m e com o lar (piso a piso de 3,0 m).
- Exporte por **subcélula × camada** (`SA_Mxx_yy_Sxx_yy`), alinhado com cenas aditivas e Addressables.

## FBX (exportador nativo do Blender)
- `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_UNITS'`, `axis_forward='-Z'`, `axis_up='Y'`, `use_space_transform=True`, `bake_space_transform=True` para estáticos.
- `mesh_smooth_type='FACE'` ou `'EDGE'` conforme sharp edges; `use_tspace=True` para normal maps.
- Instâncias de Geometry Nodes: **não** exporte instâncias realizadas aos milhares. Exporte as variantes como prefabs e recrie as instâncias na Unity a partir do manifesto (posição, rotação, variante).
- glTF é útil para revisão e para web, mas o pipeline Unity padrão do projeto é FBX.

## Nomes
- Prefabs: `SA_FAM_<variante>`, `SA_KIT_<peça>`, `SA_PROP_<tipo>`, `SA_HERO_<id>_<parte>`.
- LOD: sufixos `_LOD0`, `_LOD1`, `_LOD2` (a Unity cria LODGroup automaticamente na importação).
- Colisores: `UCX_<malha>` (convexo) ou malha `_COL` simplificada; heróis com colisão por pavimento.
- Materiais: o nome do material Blender (`reboco_antigo`, `concreto`, …) mapeia para materiais URP Lit com os mesmos nomes (biblioteca em `ArtSource/Materials/material_library_v1.json`).

## Pivôs
- Edificações: pivô no centro do footprint, no nível do térreo (é o que o manifesto usa).
- Props: pivô na base. Peças de kit: canto inferior esquerdo da face externa (paredes) ou base.

## Unity
- `AssetPostprocessor` (Editor) para: escala, `importMaterials` com remapeamento por nome, geração de LODGroup, colisores por convenção, rótulos Addressables por subcélula.
- Validação na importação: UV ausente, material ausente, escala ≠ 1, vértices acima do orçamento, textura acima do limite, nome fora do padrão.
- Cenas aditivas por macrocélula; conteúdo por subcélula como grupos Addressables; heróis como cenas próprias carregadas por proximidade ou portal.

## Antes de produzir em massa
1. Exportar 1 subcélula do núcleo + o lar + a oficina.
2. Importar, medir (draw calls, memória, tempo de carga) e comparar escala.
3. Só então automatizar todas as 181 subcélulas.
