# Corredor piloto Unity — Cidade Antiga

O primeiro recorte de integração não será uma célula isolada nem a Cidade Antiga inteira.

Foi definido um corredor contínuo de **15 subcélulas de 250 m**, equivalente a aproximadamente **750 × 1.250 m**, cobrindo a progressão inicial mais importante:

**Lar inicial → Oficina Aurora → Edifício Horizonte → Mercearia São Jorge**

Fonte machine-readable:
`Docs/unity-vertical-slice-corridor-v1.json`

Gerador:
`Tools/Map/select_unity_vertical_slice.py`

## Por que este corredor

Ele contém:
- moradia;
- sede/oficina;
- principal prédio do prólogo;
- cliente do Capítulo I;
- diferentes tipos de rua;
- trechos com relevo;
- infraestrutura urbana;
- mistura residencial/comercial;
- distância suficiente para testar streaming de verdade.

Assim, um único recorte testa simultaneamente:
- exploração;
- deslocamento;
- streaming;
- hero locations;
- materiais;
- vegetação;
- iluminação;
- colisão;
- gameplay markers.

## Âncoras

| Local | Subcélula |
|---|---|
| Lar inicial | `SA_M01_01_S00_02` |
| Oficina Aurora | `SA_M01_01_S01_03` |
| Horizonte | `SA_M01_02_S02_00` |
| Mercearia | `SA_M01_02_S01_02` |

## Regra de integração

Não é necessário carregar as 15 células em LOD0 ao mesmo tempo.

Estratégia:
- jogador em uma célula;
- 3×3 próximo em alta qualidade;
- células restantes do corredor como LOD/HLOD quando visíveis;
- hero interiors carregados por proximidade/entrada.

## Ordem recomendada de importação

1. célula do Lar;
2. célula da Oficina;
3. ponte de células entre ambas;
4. Horizonte;
5. células intermediárias;
6. Mercearia;
7. corredor completo.

Cada expansão precisa passar:
- escala;
- materiais;
- colliders;
- markers;
- memória;
- frame time.

## Vegetação

O corredor deve incorporar a decisão atual do projeto:
- árvores de calçada mais presentes em áreas residenciais e periféricas;
- menor densidade nas áreas técnicas/comerciais estreitas;
- variação irregular e plausível;
- LOD/instancing desde a primeira importação.

## Não fazer ainda

- não expandir para os seis distritos;
- não trocar o runtime atual;
- não migrar saves;
- não instalar Addressables sem autorização;
- não assumir que performance Blender = performance Unity.

O corredor só vira padrão para o resto da cidade depois do benchmark real.
