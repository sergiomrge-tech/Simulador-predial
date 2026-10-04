# Pipeline de exportação por célula — Blender → Unity

O objetivo é importar Santa Aurora em unidades pequenas sem destruir o arquivo-fonte Blender nem transformar milhares de edifícios em prefabs únicos.

## Regra principal

Nunca exportar diretamente após aplicar modificadores ou desvincular instâncias no arquivo-fonte.

O .blend oficial continua como fonte autoral.

Qualquer:
- Geometry Nodes realize;
- conversão para mesh;
- triangulação;
- bake;
- merge;
- simplificação de collider

deve acontecer numa cópia/staging de exportação.

## Preflight por célula

Ferramenta:
Tools/Blender/preflight_unity_cell_export.py

Exemplo:

blender -b ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend --python Tools/Blender/preflight_unity_cell_export.py -- --root . --cell SA_M01_01_S00_02

Saída:
ArtSource/Blender/World/UnityExport/preflight_SA_M01_01_S00_02.json

Confere:
- célula válida;
- presença no manifesto;
- objetos esperados;
- layers;
- tipos de objeto;
- tris;
- maior mesh;
- Geometry Nodes;
- collection instances;
- hero IDs;
- gameplay markers.

## Política por tipo de conteúdo

### Static export
- Terrain
- Roads
- Architecture de fundo
- Infrastructure
- Props estáticos
- Vegetation

### Dados separados
- Gameplay markers
- Lighting

### Hero locations

Lar, Oficina, Horizonte e demais heroes não devem ser cegamente fundidos ao FBX da célula.

Devem permanecer fontes/prefabs independentes para permitir:
- interiores;
- estados de progressão;
- unload próprio;
- gameplay;
- LOD próprio.

## Geometry Nodes

Instâncias de famílias e vegetação precisam ser tratadas no staging.

Opções a testar:
1. exportar instâncias preservando repetição via pipeline próprio;
2. realizar somente geometria visível da célula e reconstruir instancing na Unity;
3. converter famílias em prefab + transform list.

Preferência inicial:
prefab/family + transform list, porque evita duplicação maciça de mesh.

Não escolher abordagem final sem benchmark.

## Célula piloto

Primeira:
SA_M01_01_S00_02 — Lar inicial.

Essa célula valida:
- escala;
- eixos;
- relevo;
- ruas;
- árvores;
- Lar;
- materiais;
- collider;
- streaming root.

A Oficina entra depois.

## Export plan

Ferramenta:
Tools/Map/build_unity_cell_export_plan.py

Ela lê:
- manifesto do Blender;
- corredor piloto;

e gera:
Docs/unity-cell-export-plan-v1.json

O plano lista por célula:
- Scene Unity;
- heroes;
- número de lotes;
- layers;
- relatório de preflight esperado.

## FBX

Caso FBX seja usado para a geometria estática:

- escala global 1;
- aplicar unidades;
- Unity em metros;
- preservar nomes;
- custom props quando úteis;
- tangents/normals explícitos;
- sem animação em célula estática;
- não bakear hero interiors junto.

Configuração precisa ser validada no primeiro asset; não assumir que orientação visual no Blender garante import correto.

## Markers

Gameplay markers devem ser exportados como dados:

- name;
- facility_id;
- kind;
- posição;
- rotação;
- célula.

Na Unity:
- criar Transforms vazios;
- nunca fundir marker a mesh;
- validar contagem.

## Colliders

Gerar separadamente de render mesh quando possível.

Rua:
- collider simples/contínuo.

Prédios de fundo:
- volumes simples.

Hero:
- colliders autorados por espaços jogáveis.

Vegetação:
- apenas tronco/volume necessário.

## Gate da primeira célula

A célula do Lar só passa quando:

- preflight PASS;
- escala 1:1;
- eixo correto;
- relevo correto;
- Scene metadata correta;
- materiais sem missing;
- player anda sem cair;
- collider não bloqueia acessos;
- árvore não bloqueia calçada;
- Lar aparece na posição correta;
- memória/performance registradas.

Depois disso avançar para Oficina.
