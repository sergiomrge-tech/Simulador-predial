---
name: blender-headless-bpy
description: >
  Padrões validados para gerar e auditar cenas Blender 5.2 em modo headless com bpy (malha via from_pydata,
  UVs métricos, bevel por bmesh, instâncias por Geometry Nodes, EEVEE/Workbench, gestão de cor, assets,
  reabertura sem missing data). Use ao escrever ou depurar scripts em Tools/Blender.
---

# Blender headless com bpy (5.2 LTS)

Autoria: projeto Facility Ops. Tudo abaixo foi verificado em Blender 5.2.1 LTS no W1/W1.5.

## Execução
```bash
blender --background --factory-startup --python script.py -- --root <projeto>
blender --background --factory-startup arquivo.blend --python verify.py -- ...   # reabrir = processo novo
```
- Sempre use `--factory-startup` (sem add-ons ou preferências do usuário) e passe argumentos depois de `--`.
- Para reabrir, abra o `.blend` num processo novo e nunca salve no passo de verificação.

## Geometria eficiente
- Monte vértices e faces em Python e use `mesh.from_pydata(verts, [], faces)` + `polygons.foreach_set("material_index", ...)`. Evite `bpy.ops` em laço.
- Escreva UVs métricos por projeção de caixa (1 UV = 1 m), porque materiais 2D (tijolo, ladrilho, ondulado) **precisam de UV**. Coordenadas `Object` em textura 2D amostram uma única linha numa parede vertical (bug real que corrigimos).
- Para bevel real, use `bmesh.ops.remove_doubles` e depois `bmesh.ops.bevel` só nas arestas com ângulo > 30°. Aplique em peças de kit e heróis; não aplique em milhares de edificações de fundo (custo).

## Instâncias em massa (Geometry Nodes)
- Um objeto só de vértices por célula, com atributos `variant` (INT), `rot` (FLOAT) e `scl` (FLOAT) → grupo GN com Collection Info (Separate/Reset Children) → Instance on Points (Pick Instance, Instance Index = `variant`).
- **Blender 5.x:** atribuir coleção via `modifier[identifier] = collection` falha ("id properties not supported"). Defina `CollectionInfo.inputs["Collection"].default_value` **dentro** de um grupo por biblioteca.
- A ordem dos filhos da coleção define o índice. Vincule em ordem alfabética e guarde o mapa nome → índice.
- `Object Info → Random` varia por instância (bom para cor). Objetos divididos por pavimento recebem randoms diferentes, então use material sem variação nesses casos.

## Materiais
- `material.use_nodes` está obsoleto (sempre ligado). Envolva em `try`.
- Slots de textura para o futuro: crie `ShaderNodeTexImage` **sem imagem** e sem ligação. Assim não geram missing data.
- Defina `material.diffuse_color` para o Workbench.

## Render e cor
- EEVEE funciona em headless nesta máquina (GPU NVIDIA). O Workbench é mais rápido para plantas.
- Em background, a enumeração de `view_transform`/`look` volta `['NONE']`, mas atribuir pelo nome funciona (`"Standard"`, `"AgX"`).
- Céu `ShaderNodeTexSky` (`MULTIPLE_SCATTERING`): desligue `sun_disc` quando já houver uma luz SUN (senão a luz é dobrada e a imagem estoura).
- Revisão: Standard com exposição −1,4, sol 4 e céu 0,35 deram contraste legível. O sol de oés-sudoeste ilumina fachadas voltadas para câmeras ao sul.

## Organização e assets
- Coleções por camada e célula. Bibliotecas de instâncias ficam em coleção com `hide_render=True`.
- `obj.asset_mark()` funciona em background (previews podem faltar).
- Salve com `bpy.ops.wm.save_as_mainfile(filepath=..., compress=True)`.

## Auditoria de reabertura (mínimo)
- `bpy.data.libraries`/`images`/`fonts` com arquivo inexistente devem estar vazios.
- Unidades métricas com escala 1.0; contagem de objetos por coleção; IDs (`facility_id`) presentes.
- Todo modificador GN aponta para uma coleção não vazia.

## Armadilhas já vividas
- Sombreamento de nome: uma variável `sub` (subcélula) escondeu a função `sub` de vetores. Importe com alias.
- Python `hash()` de string muda a cada processo. Para seeds, use `zlib.crc32`.
