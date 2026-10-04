# Facility Ops — Orçamento de performance PC/Steam

**Status:** orçamento de engenharia, ainda não benchmark validado.  
**Meta primária:** 60 FPS em 1080p no preset recomendado do vertical slice.

## 1. Frame budget

60 FPS = **16,67 ms** por frame.

Alvos de engenharia para o vertical slice:

| Área | Meta |
|---|---:|
| CPU main thread | <= 8 ms típico |
| Render thread | <= 6 ms típico |
| GPU | <= 14 ms típico |
| Streaming assíncrono | <= 2 ms médio; evitar picos > 4 ms |
| GC por frame | 0 B em exploração normal |
| frame spikes | nenhum hitch recorrente > 33 ms |

Esses números são metas, não resultados medidos.

## 2. Estratégia de streaming

Base:
- macro: 1 km;
- subcélula: 250 m.

Proposta para teste:
- anel próximo: 3×3 subcélulas em alta fidelidade;
- anel médio: 5×5 com LOD/HLOD;
- longa distância: proxies por macro + skyline;
- hero location pode ser carregado antecipadamente ao entrar em sua zona de aproximação.

O raio final deve ser escolhido por profiling, não por estética isolada.

## 3. Geometria visível

Meta inicial para 1080p:
- tris visíveis próximos: ~2–4 milhões;
- pico controlado: ~5–6 milhões;
- distância média dominada por LOD/HLOD;
- evitar dezenas de milhões de tris simultaneamente no frustum.

A Cidade Antiga no Blender pode conter muito mais geometria total porque o runtime nunca deve carregar/renderizar tudo em LOD0 ao mesmo tempo.

## 4. Draw calls / batches

Meta inicial:
- < 800 batches visíveis em rua típica;
- < 1200 em cenas hero complexas;
- usar SRP Batcher;
- GPU instancing para famílias/props compatíveis;
- evitar material único por prédio.

## 5. Materiais

- biblioteca compartilhada por categoria;
- evitar cópia de material por instância;
- MaterialPropertyBlock quando possível;
- meta de materiais únicos simultaneamente ativos no corredor: < 200;
- shaders transparentes restritos a vidro/efeitos necessários.

## 6. Texturas / VRAM

Preset recomendado:
- evitar 4K por padrão em props comuns;
- 2K para superfícies hero quando justificável;
- 1K/2K para famílias repetidas;
- trim sheets e atlases para arquitetura;
- mipmaps obrigatórios;
- streaming de mipmaps quando validado.

Meta provisória de residência de texturas do vertical slice:
- ~1,5 GB ou menos no cenário típico;
- manter margem para buffers, sombras, meshes e sistema operacional/driver.

## 7. Luzes e sombras

Na rua típica:
- 1 directional principal;
- luzes locais limitadas;
- <= 4 luzes locais com sombra influenciando o mesmo ponto como teto de emergência, não alvo comum;
- luzes decorativas sem sombra sempre que possível.

Interiores hero:
- priorizar bake/mixed quando compatível com gameplay;
- equipamentos interativos podem usar luz dinâmica localizada.

## 8. Vegetação

- GPU instancing;
- LOD agressivo, mas sem popping evidente;
- billboard/impostor para distância longa quando necessário;
- sombras de vegetação reduzidas por distância;
- árvores de calçada não podem custar como hero asset.

## 9. Física

- colliders simples;
- não usar MeshCollider detalhado em arquitetura inteira;
- desabilitar colliders fora da zona relevante se necessário;
- nenhum Rigidbody dinâmico para clutter estático.

## 10. IA/NPC

Ainda não é gate W3, mas reservar orçamento:
- simulação completa apenas perto do jogador;
- agentes distantes em representação reduzida;
- NavMesh por áreas/células;
- evitar pathfinding global contínuo para centenas de NPCs.

## 11. Memória

Orçamento provisório do vertical slice:
- RAM total do processo: alvo < 6 GB em sessão normal;
- VRAM alvo: funcionar com margem em GPU de 6 GB no preset recomendado;
- sem retenção de células descarregadas;
- Addressables/cenas aditivas devem liberar referências corretamente.

## 12. Métricas obrigatórias do primeiro teste Unity do mundo

Capturar:
- CPU/GPU frame time;
- batches/setpass;
- tris/verts;
- memória total;
- memória de textura;
- número de GameObjects;
- número de Renderers;
- tempo de carga por subcélula;
- pico ao atravessar fronteira de célula;
- GC alloc;
- tempo de unload;
- hitch máximo em 5 minutos de travessia.

## 13. Gate

A Cidade Antiga não deve ser propagada para os demais distritos até:

1. corredor W3 aprovado visualmente;
2. importação Blender→Unity validada;
3. streaming 250 m funcionando;
4. profiler real coletado;
5. 60 FPS sustentados na máquina de referência;
6. memória dentro do orçamento;
7. travessia de célula sem hitch grave.

Qualquer número deste documento pode ser ajustado depois do primeiro benchmark real; o importante é existir um orçamento explícito antes da expansão.
