# Gameplay markers — Blender → Unity

O primeiro vertical slice não deve digitar coordenadas de gameplay manualmente na Unity.

Os pontos autorais já existentes no Blender são contratos de dados.

## Exemplos já existentes

No Edifício Horizonte:
- GP_prologue_spawn_corridor
  - kind: spawn
  - entrada do jogador no corredor do prólogo
- GP_quadro_tecnico
  - kind: interaction
  - ponto do quadro técnico do primeiro chamado

Também existem:
- SLOT_ / W2_SLOT_ para estados de progressão;
- PROXY_ para referências/proxies;
- HERO_ anchors;
- markers sa_layer=Gameplay.

## Exportador Blender

Tools/Blender/export_unity_gameplay_markers.py

Exemplo:

blender -b ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend --python Tools/Blender/export_unity_gameplay_markers.py -- --root . --name horizonte

Saída esperada:

ArtSource/Blender/World/UnityExport/Markers/horizonte.markers.json

O arquivo registra:
- name;
- facilityId;
- kind;
- state;
- item;
- note;
- posição Unity;
- forward Unity;
- up Unity;
- escala;
- propriedades customizadas.

## Conversão espacial

Contrato:
- Blender X → Unity X;
- Blender Y → Unity Z;
- Blender Z → Unity Y.

Orientação:
- Blender local -Y é tratado como forward;
- Blender local +Z é up;
- Unity reconstrói com Quaternion.LookRotation(forward, up).

Isso evita tentar converter Euler angles manualmente.

## Importador Unity

Facility Ops > World > Import Gameplay Marker Catalog...

Arquivo:
FacilityOps/Assets/_Game/Editor/WorldGameplayMarkerImporter.cs

Requisitos:
- uma Scene de célula aberta;
- exatamente um WorldCellRoot;
- child Gameplay existente.

O importador:
- cria GameObjects vazios;
- não adiciona comportamento de missão;
- adiciona WorldGameplayMarker;
- preserva nomes e metadata;
- atualiza um marker existente pelo mesmo nome;
- usa Undo;
- marca a Scene como dirty.

## Regra de arquitetura

WorldGameplayMarker é metadata, não lógica.

O sistema de gameplay existente decide:
- qual marker é spawn;
- qual marker recebe interação;
- qual marker corresponde ao chamado ativo;
- quando um SLOT aparece.

Assim o mundo visual não passa a controlar progressão sozinho.

## Gate do Horizonte

Antes do primeiro build jogável:

1. exportar horizonte.markers.json;
2. importar na célula/hero Scene correta;
3. confirmar GP_prologue_spawn_corridor;
4. confirmar GP_quadro_tecnico;
5. posicionar o player no spawn;
6. raycast/interação alcançar o quadro;
7. comparar posição visual com o Blender;
8. garantir que o fluxo antigo do prólogo continua funcionando;
9. salvar/reabrir a Scene;
10. rodar marker audit.

Não remover o sistema de coordenadas procedural antigo até esse teste passar.
