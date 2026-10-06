# PROJECT RESORT — Biblioteca de Assets Gratuitos

## Regra de licença

O repositório GitHub atual é público. Não commitar arquivos brutos de Unity Asset Store nem outros assets cuja licença proíba redistribuição em source form.

Os pacotes licenciados ficam localmente em:

`D:\ProjectResort_AssetLibrary\`

Claude pode usar os assets no jogo local, mas deve manter origem/licença registrada. Antes de publicar binários ou tornar o repositório de assets compartilhável, revisar as licenças.

## Disponível localmente agora

### PRIORIDADE A — integrar na Fase 02

**Human Basic Motions FREE — Kevin Iglesias — Unity Asset Store**

Local:
`D:\ProjectResort_AssetLibrary\UnityFree\ExtractedForReview\Human Basic Motions FREE`

Pacote:
`D:\ProjectResort_AssetLibrary\UnityFree\Packages\Human Basic Motions FREE.unitypackage`

Conteúdo verificado:
- 121 FBX;
- 8 idle;
- 32 walk;
- 32 run;
- 20 sprint;
- 8 turn;
- 14 jump/fall;
- 2 talk/conversation;
- versões male/female;
- várias versões Root Motion;
- modelos humanoid dummy e avatar masks.

Uso no Resort:
- caminhar no calçadão;
- correr/jogging;
- idle;
- conversa em pares/grupos;
- transições naturais dos NPCs;
- base para clientes e funcionários.

Direção:
Não substituir a IA/LOD do BeachLife. Usar Animator/Humanoid sobre o comportamento existente. Manter sistema atual como fallback de LOD distante enquanto os modelos visuais próximos evoluem.

### PRIORIDADE B — vegetação/filler

**Environment Pack Free Forest Sample — Supercyan — Unity Asset Store**

Local:
`D:\ProjectResort_AssetLibrary\UnityFree\ExtractedForReview\Environment Pack Free Forest Sample`

Conteúdo verificado:
- 16 FBX;
- 20 prefabs;
- 16 texturas;
- materiais e vegetação.

Uso:
- avaliar para planos médios/distantes;
- filler de áreas verdes;
- não usar automaticamente como vegetação hero/close-up se destoar da meta realista.

## Já baixados mas NÃO prioritários para PROJECT RESORT

- Earth Mage — fantasia;
- Magic Effects FREE — magia/VFX;
- Fantasy Monster 3D Model 03 — criatura;
- FreeTrial 30 Monster Stylized Fantasy — criaturas.

Não integrar no Resort salvo necessidade futura específica.

## Fila de gratuitos pesquisados na Unity Asset Store

A baixar/adicionar quando disponível na conta/cache:

### Animações
- Human Crafting Animations FREE — Kevin Iglesias;
- MC Sample - Believable 3D Animations by MoCap Central;
- Creative Characters FREE - Animated Pack;
- usar apenas os clips coerentes com vida cotidiana/hotelaria.

### Vegetação/praia
- Coconut Palm Tree Pack — grátis;
- Grass Flowers Pack Free — grátis;
- Terrain Textures Pack Free — grátis;
- avaliar Ultimate Nature – Starter — grátis.

### Materiais
- Yughues Free Concrete Materials — grátis, PBR e compatível URP;
- Yughues Free Architectural Materials — grátis;
- HDRI Pack | Starter Assets — grátis;
- AllSky Free — grátis, apenas se visualmente coerente.

### Estruturas/props
- Modular European House — grátis; usar somente componentes reaproveitáveis/coerentes;
- Lowpoly Art Deco Furniture — grátis; priorizar apenas props que não denunciem estilo low-poly;
- procurar packs modernos/realistas gratuitos de móveis, cozinha, restaurante, hotel e praia.

## Regra visual

Grátis não significa aprovado.

Todo asset candidato precisa passar:
1. escala real;
2. compatibilidade URP/Unity 6 ou conversão segura;
3. material coerente;
4. licença compatível;
5. LOD/performance adequada;
6. estética próxima do real;
7. não parecer pack genérico ou colagem de estilos.

## Estratégia de personagens

Fase 02:
- manter lógica BeachLife;
- integrar animações Humanoid gratuitas;
- melhorar rig/modelo visual progressivamente;
- close/medium LOD com Animator;
- far LOD pode permanecer simplificado;
- evitar centenas de Animators completos.

Se os personagens gratuitos continuarem parecendo artificiais perto da câmera, o Diretor deve apresentar ao usuário 1–3 opções pagas realmente superiores antes de qualquer compra.
