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
  - exatamente 9 hero locations do array `heroes`;
  - contagem de lotes e subcélulas contra o relatório de geração;
  - round-trip dos 1.024 IDs possíveis do grid 8×8 km;
  - não instala pacote e não modifica assets.

- `WorldStreamingPolicy.cs` + `WorldStreamingSceneNaming.cs`
  - política inicial de 3×3 células carregadas;
  - anel 5×5 de retenção/histerese;
  - naming estável `SA_Cell_SA_Mxx_yy_Sxx_yy`.

- `WorldStreamService.cs`
  - carregamento aditivo opt-in;
  - desativado por padrão;
  - só tenta carregar cenas realmente disponíveis no build;
  - reconstrói o índice a partir de cenas já carregadas;
  - controla loads/unloads pendentes para não duplicar operações;
  - não toca em saves e não substitui `WorldBuilder`.

- cenas piloto
  - `WorldCellRoot` como metadata estável;
  - scaffolder de 15 Scenes aditivas;
  - estrutura por Terrain/Roads/Architecture/Infrastructure/Props/Vegetation/Lighting/Gameplay;
  - validador de Scene;
  - sincronização opcional com Build Settings;
  - nenhuma Scene foi gerada automaticamente nesta branch.

- primeiro executável
  - `WorldIntegrationQa` encadeia manifesto + cenas + regras antigas;
  - `WorldSliceBuilder` prepara o build Windows v0.1 somente após os gates;
  - bootstrap separado `WorldSliceBootstrap.unity`;
  - launcher `Jogar_CidadeAntiga.bat` usa a flag `-worldSlice`;
  - `WorldSliceRuntimeBridge` espera a célula do Lar carregar antes de ocultar o cenário procedural;
  - overlay de streaming disponível apenas para QA/development.

- gameplay markers
  - exportador Blender para GP_/SLOT_/PROXY_/Gameplay;
  - contrato de posição X/Y/Z Blender → X/Z/Y Unity;
  - forward/up em vez de Euler frágil;
  - importador Unity de metadata;
  - `WorldGameplayMarker` sem lógica acoplada;
  - documentação específica para o spawn e quadro técnico do Horizonte.

- exportação por célula
  - preflight Blender read-only por subcélula;
  - detecção de Geometry Nodes, linked heroes, markers e complexidade;
  - gerador de plano de exportação do corredor;
  - política de não modificar o .blend-fonte.

- EditMode tests
  - round-trip dos 1.024 IDs;
  - rejeição de IDs inválidos;
  - células esperadas de Lar/Oficina/Horizonte/Mercearia;
  - 3×3 / 5×5;
  - clipping nas bordas do mundo;
  - round-trip do nome da Scene.

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
- nenhuma substituição do `WorldBuilder` no modo normal;
- ponte `-worldSlice` é opt-in e ainda não foi executada;
- nenhum Addressables;
- nenhuma afirmação de performance real.

## Corredor piloto já definido

`Docs/unity-vertical-slice-corridor-v1.json` registra um corredor contínuo de 15 subcélulas (~750 × 1.250 m):

**Lar → Oficina Aurora → Horizonte → Mercearia São Jorge**

Gerador determinístico:
`Tools/Map/select_unity_vertical_slice.py`.

Isso evita escolher células de forma manual depois do W3.

## Próximo passo desta branch

Depois que o Claude fechar o W3 visual:
1. trazer o W3 para a branch de integração sem merge no main;
2. confirmar que o corredor continua compatível com os assets finais W3;
3. rodar `validate_unity_streaming_contract.py`;
4. gerar o plano de exportação;
5. executar preflight da célula do Lar;
6. exportar/importar primeiro a célula do Lar;
7. criar as 15 Scene scaffolds no Unity e preencher a primeira;
8. criar `WorldSliceBootstrap`;
9. rodar EditMode tests + WorldIntegrationQa;
10. ativar `-worldSlice` e validar caminhada no Lar;
11. expandir até Oficina e Horizonte;
12. importar markers do Horizonte;
13. integrar o primeiro chamado somente depois da geometria/markers estarem confirmados;
14. medir performance real antes de qualquer expansão.

Até lá, esta branch serve como base técnica sem competir com a produção visual.

## Validação atual

- revisão estática da lógica e das convenções concluída;
- a branch não modifica o Bootstrap normal, saves, IDs ou assets visuais;
- o modo de mundo grande está isolado em scripts/Scene separada e exige `-worldSlice`;
- **ainda não houve compilação/teste no Unity desta branch**;
- portanto, os novos testes e o serviço aditivo não devem ser descritos como runtime-validado até uma execução real no Unity 6000.6.2f1.
