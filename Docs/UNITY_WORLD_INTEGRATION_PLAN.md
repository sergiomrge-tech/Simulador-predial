# Santa Aurora → Unity — plano de integração do mundo

**Branch de trabalho:** `gpt/unity-world-integration`  
**Regra:** não substituir o protótipo jogável atual antes de um vertical slice integrado e validado.

## Objetivo

Levar a Cidade Antiga criada no Blender para Unity sem quebrar:
- gameplay existente;
- saves;
- IDs;
- primeiro contrato;
- catálogo de campanha;
- fluxo de QA.

## Princípio central

O protótipo atual e o mundo grande devem coexistir durante a migração.

Não mover o runtime inteiro para coordenadas de ±4 km em uma única mudança.

## Fase U0 — contratos de dados

Entregue nesta fundação:
- `WorldStreamingId` como regra única para nomes de células;
- validador Editor do manifesto Blender;
- convenções oficiais Blender→Unity;
- orçamento de performance.

Gate:
- parser de IDs determinístico;
- manifesto validável sem dependências externas;
- nenhuma mudança de gameplay.

## Fase U1 — exportação de uma célula

Selecionar uma subcélula do corredor W3 que contenha parte do vertical slice.

Exportar:
- Terrain;
- Roads;
- Architecture;
- Infrastructure;
- Props;
- Vegetation.

Gameplay markers ficam em arquivo/camada própria.

Importar em pasta isolada:
`Assets/_Game/World/SantaAurora/OldTown/Cells/<cell>/`.

Não ativar no Bootstrap ainda.

Gate:
- escala 1:1;
- orientação correta;
- materiais sem erro;
- pivô da célula correto;
- marker audit PASS.

## Fase U2 — cena aditiva de célula

Gerar uma Scene por subcélula piloto:
- nome estável da célula;
- root único;
- Static flags;
- LODGroups;
- colliders;
- metadata.

Criar `WorldStreamService` separado de `WorldBuilder`.

O serviço novo não substitui o sistema antigo nessa fase.

Gate:
- load/unload manual no Editor;
- nenhuma duplicação de sistemas globais;
- nenhuma alteração de save.

## Fase U3 — corredor

Carregar conjunto 3×3 ao redor do jogador.

Adicionar:
- preload;
- unload com margem/histerese;
- fila assíncrona;
- limite de operações por frame;
- fallback se uma célula falhar.

Gate:
- atravessar múltiplas células;
- nenhum buraco visível importante;
- nenhuma célula órfã;
- sem hitch grave;
- profiler capturado.

## Fase U4 — hero locations

Heróis são carregados como conteúdo de maior fidelidade e podem ter ciclo próprio.

Primeiros:
1. Lar;
2. Oficina Aurora;
3. Horizonte;
4. cliente do Capítulo I do corredor.

Markers do Blender devem mapear para:
- spawns;
- portas;
- quadros;
- bombas;
- slots de progressão;
- zonas de serviço.

Não codificar posição manual se marker oficial existir.

## Fase U5 — integração de gameplay

Só depois do mundo visual funcionar:
- o chamado passa a apontar para o hero físico;
- ida/retorno deixa de ser apenas instância procedural;
- manter compatibilidade com chamadas antigas;
- migração de saves se qualquer posição persistente for adicionada.

## Fase U6 — Addressables

Addressables é recomendado, mas não instalar nesta branch sem autorização explícita.

Primeiro provar o modelo com cenas aditivas e AssetDatabase no Editor.

Quando autorizado:
- grupo por distrito;
- labels por macro/subcélula/camada;
- hero assets separados;
- catálogo local;
- validação de dependências;
- teste de unload real.

## Fase U7 — build QA

Criar smoke test específico do mundo:

1. abrir Bootstrap;
2. carregar célula inicial;
3. spawnar jogador;
4. caminhar por fronteiras;
5. entrar no Horizonte;
6. verificar GP markers;
7. descarregar células distantes;
8. confirmar memória;
9. salvar;
10. reabrir;
11. repetir rota.

## Compatibilidade com o runtime atual

`WorldBuilder` continua sendo o fallback do protótipo até o gate do mundo.

Não apagar:
- previews;
- blocos de serviço;
- QA antigo.

A remoção só pode acontecer quando a versão de mundo grande reproduzir os fluxos já validados.

## Riscos principais

### Coordenadas grandes
8 km ainda é administrável em float para um jogo dessa escala, mas:
- física;
- sombras;
- partículas;
- precisão de detalhes
precisam de teste.

Floating origin só será adotado se profiling/QA mostrar necessidade. Não introduzir complexidade preventiva.

### Custo de importação
Não importar 13 mil prédios como prefabs únicos.

Usar:
- variantes;
- instancing;
- HLOD;
- células.

### Materiais
Não criar cópias de materiais por edifício.

### Hero interiors
Não manter interiores pesados carregados quando longe.

### Iluminação
Bake global de cidade inteira é proibitivo. Planejar iluminação por células/heróis.

## Critério de sucesso da integração inicial

Uma pequena região da Cidade Antiga deve permitir:

- andar em primeira pessoa;
- perceber o relevo;
- ver vegetação e materiais W3;
- cruzar ao menos uma fronteira de streaming;
- entrar em um hero location;
- usar um marker de gameplay;
- retornar;
- manter 60 FPS na máquina de referência;
- carregar/descarregar sem corrupção;
- manter save e campanha atuais intactos.
