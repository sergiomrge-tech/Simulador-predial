# Trabalho paralelo — fundação da integração Unity

**Branch:** `gpt/unity-world-integration`  
**Base:** checkpoint W2.5 + definição W3 da branch do Claude.  
**Escopo:** trabalho paralelo, sem alterar os arquivos visuais do W3.

## Entregue

- `WorldStreamingId.cs`
  - parser determinístico de `SA_Mxx_yy_Sxx_yy`;
  - valida limites 8×8 km / 1 km / 250 m;
  - converte posição XZ para célula;
  - fornece centro da subcélula;
  - documenta eixo Blender→Unity.

- `WorldStreamingManifestValidator.cs`
  - menu Editor somente leitura;
  - confere presença dos 3 arquivos de mundo;
  - schemaVersion;
  - estrutura mínima;
  - nomes/ranges das subcélulas;
  - referências de lotes para células existentes;
  - IDs duplicados de lotes;
  - IDs dos heróis;
  - contagem de lotes e subcélulas contra o relatório de geração;
  - não instala pacote e não modifica assets.

- `BLENDER_UNITY_EXPORT_CONVENTIONS.md`
  - escala/eixos;
  - pivôs;
  - naming;
  - LOD;
  - colliders;
  - materiais;
  - UV/lightmap;
  - gameplay markers;
  - cenas aditivas.

- `PERFORMANCE_BUDGET_PC_STEAM.md`
  - frame budget;
  - orçamento de geometria, batches, texturas e luzes;
  - estratégia de streaming;
  - métricas obrigatórias de profiling.

- `UNITY_WORLD_INTEGRATION_PLAN.md`
  - migração U0→U7 sem quebrar o protótipo;
  - coexistência do mundo atual e do mundo grande;
  - célula piloto antes da expansão;
  - Addressables somente após autorização.

## O que deliberadamente NÃO foi feito

- nenhum merge no main;
- nenhuma mudança na branch `claude/w1-masterplan`;
- nenhuma instalação de pacote;
- nenhuma alteração de save;
- nenhuma mudança de IDs;
- nenhuma substituição do `WorldBuilder`;
- nenhum Addressables;
- nenhuma afirmação de performance real.

## Próximo passo desta branch

Depois que o Claude fechar o W3 visual:
1. escolher a subcélula piloto do corredor aprovado;
2. exportar somente essa célula;
3. validar escala/materiais/markers;
4. montar primeira cena aditiva;
5. medir no Unity 6000.6.2f1.

Até lá, esta branch serve como base técnica sem competir com a produção visual.
