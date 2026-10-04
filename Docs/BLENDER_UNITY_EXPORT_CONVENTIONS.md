# Blender → Unity — Convenções oficiais do mundo de Santa Aurora

**Status:** fundação técnica paralela ao W3 visual.  
**Objetivo:** impedir que cada exportação invente escala, eixos, pivôs, LODs ou nomes diferentes.

## 1. Sistema de coordenadas

A fonte espacial autoral continua sendo o Blender.

- Blender: X/Y no plano, Z para altura.
- Unity: X/Z no plano, Y para altura.
- Conversão oficial:
  - Blender X → Unity X
  - Blender Y → Unity Z
  - Blender Z → Unity Y
- Unidade: **1 metro = 1 Unity unit**.
- Nenhuma escala global de correção deve ser aplicada ao mundo depois de importado.

O runtime atual ainda usa coordenadas pequenas para o protótipo. O mundo 8×8 km **não deve substituir essas coordenadas silenciosamente**. A migração será deliberada, com compatibilidade de saves e QA.

## 2. Streaming

Nomenclatura compartilhada:

- macro: `SA_Mxx_yy` = célula de 1 km;
- subcélula: `SA_Mxx_yy_Sxx_yy` = 250 m;
- camadas:
  - Terrain
  - Roads
  - Architecture
  - Infrastructure
  - Props
  - Vegetation
  - Lighting
  - Gameplay

O manifesto gerado pelo Blender é a fonte de inventário espacial. Unity não deve renomear IDs de células.

## 3. Arquivos exportados

Estrutura prevista:

```
Assets/_Game/World/SantaAurora/
  Shared/
    Materials/
    Textures/
    Prefabs/
  OldTown/
    Cells/
      SA_Mxx_yy_Sxx_yy/
        Terrain/
        Roads/
        Architecture/
        Infrastructure/
        Props/
        Vegetation/
        Gameplay/
    Heroes/
      home.starter/
      garage/
      horizonte/
      ...
```

Durante W3/W4, não exportar toda a cidade por força bruta. Primeiro validar um corredor de vertical slice.

## 4. Pivôs

- células: pivô no centro geométrico da subcélula ou origem documentada da célula;
- prédios: pivô no térreo, preferencialmente próximo ao acesso principal;
- portas/portões: pivô na dobradiça/eixo real;
- rodas: pivô no centro do cubo;
- props soltos: pivô no ponto natural de apoio;
- heróis: raiz estável; filhos podem ser locais.

A origem não pode mudar entre LODs de um mesmo asset.

## 5. Naming

Prefixos reservados:

- `SA_` — mundo/células;
- `HERO_` — hero location;
- `GP_` — gameplay marker;
- `SLOT_` — slots de progressão;
- `PROXY_` — representação provisória/LOD;
- `LOD0_`, `LOD1_`, `LOD2_` — níveis explícitos quando necessário;
- `COL_` — collider autorado;
- `TRG_` — trigger;
- `FX_` — ponto de efeito;
- `SND_` — ponto de áudio.

Não reutilizar `GP_` ou `SLOT_` para decoração.

## 6. LOD

Heróis:
- LOD0: W2/W3 de alta fidelidade;
- LOD1: simplificação intermediária;
- LOD2: massing/W1.5 quando apropriado;
- culling apenas quando o skyline não for afetado.

Famílias de fundo:
- LOD0 apenas no corredor visível de alta fidelidade;
- LOD1 nas ruas próximas;
- HLOD/proxy por subcélula para média/longa distância.

Todos os LODs devem compartilhar:
- posição;
- rotação;
- footprint;
- silhueta coerente;
- material fallback funcional.

## 7. Colliders

Evitar MeshCollider complexo como padrão.

Prioridade:
1. BoxCollider / CapsuleCollider / composição simples;
2. collider autorado `COL_*`;
3. MeshCollider somente quando a geometria realmente exigir.

Regras:
- decoração sem interação não deve carregar collider desnecessário;
- collider de prédio deve privilegiar navegação e gameplay;
- detalhes de fachada não precisam de colisão fina;
- escadas precisam ser testadas com o CharacterController real.

## 8. Materiais e texturas

Unity URP é o alvo atual.

Texturas:
- Base Color: sRGB;
- Normal: import type Normal Map;
- Roughness: converter/empacotar de forma consistente para URP;
- Metallic: linear;
- AO: linear;
- Height: opcional, somente onde trouxer benefício claro.

Recomendação de packing para produção:
- R = Metallic
- G = AO
- B = máscara auxiliar
- A = Smoothness

A convenção final de packing deve ser única no projeto; não misturar mapas arbitrariamente.

## 9. Lightmaps e UV

- UV0 = material;
- UV1 = lightmap quando necessário;
- densidade de texel deve ser coerente por categoria;
- heróis podem ter orçamento superior a prédios de fundo;
- nada de sobreposição UV em lightmap para geometria estática que dependa de bake.

## 10. Marcadores de gameplay

`GP_`, `SLOT_` e IDs `facility_id` são contratos de dados, não decoração.

Na importação:
- preservar nome e ID;
- converter markers em GameObjects/Transforms sem renderer;
- não fundir markers dentro de meshes;
- não aplicar otimização que os remova;
- validar contagem antes/depois da exportação.

## 11. Cenas aditivas

Cada subcélula deve poder tornar-se uma unidade carregável.

Separar:
- geometria estática;
- hero locations;
- gameplay;
- iluminação quando necessário.

A cena Bootstrap permanece dona dos sistemas globais. Células não devem duplicar:
- GameRuntime;
- save service;
- áudio global;
- input;
- UI.

## 12. Gate antes de exportar a Cidade Antiga inteira

Somente expandir quando o vertical slice provar:

- escala correta em Unity;
- eixo correto;
- materiais equivalentes;
- LOD funcionando;
- collider funcionando;
- streaming sem hitch grave;
- IDs/markers íntegros;
- iluminação coerente;
- orçamento de memória aceitável;
- 60 FPS em máquina-alvo definida.

Até lá, exportar apenas células do corredor de teste.
