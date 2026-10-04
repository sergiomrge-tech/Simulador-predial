# FILA AUTÔNOMA — FACILITY OPS

Esta fila foi explicitamente autorizada pelo usuário em 2026-10-03.

## REGRA DE CONTINUIDADE NOTURNA

Durante esta execução noturna, NÃO parar entre etapas por simples conclusão de tarefa.

Ao concluir qualquer etapa:
1. validar o máximo possível;
2. atualizar relatório/status;
3. commit;
4. push;
5. confirmar working tree limpa;
6. executar git pull;
7. reler este arquivo e Docs/CLAUDE_NEXT_TASK.md;
8. iniciar imediatamente a próxima etapa autorizada.

Não aguardar confirmação do usuário entre A → B → C → D.

Só parar se ocorrer:
- limite de uso efetivamente bloqueando novas execuções;
- conflito Git;
- erro crítico que possa corromper projeto;
- dúvida real de licença/segurança;
- necessidade de decisão de produto não coberta pela documentação.

Se o contexto da sessão ficar muito grande e o Claude Code permitir reinício/novo contexto, preserve primeiro todo o estado no GitHub e continue a partir deste arquivo em contexto limpo.

Quando o limite de uso voltar, retomar pela última etapa incompleta registrada no GitHub.

## Ordem obrigatória

### ETAPA A — W1.5 Santa Aurora Foundation

O Claude já está trabalhando nesta etapa. NÃO interromper o masterplan para começar a pesquisa de skills.

Objetivo: fechar a fundação espacial de Santa Aurora e preparar a Cidade Antiga como primeira região de produção.

Executar:
1. Refinar relevo urbano e drenagem.
2. Corrigir a ligação viária Cidade Antiga ↔ Expansão.
3. Implementar ferrovia/porto seco conforme a lore.
4. Tornar a Cidade Antiga menos ortogonal e mais orgânica.
5. Preencher transições vazias entre distritos.
6. Aumentar densidade e variedade do Industrial.
7. Refinar as 8 vias principais, acessos, cruzamentos e vias coletoras.
8. Melhorar skyline e leitura de alturas por distrito.
9. Preservar 24 locais de campanha, 20 locais de vida/economia, IDs e coerência narrativa.
10. Preparar Cidade Antiga com ruas, becos, calçadas, estacionamentos, acessos, infraestrutura urbana-base e famílias variadas de massing.
11. Avançar arquitetura-base dos Hero Locations:
   - lar inicial;
   - Oficina Aurora;
   - Edifício Horizonte;
   - apartamentos antigos;
   - mercearia;
   - restaurante;
   - oficina local;
   - pequeno escritório;
   - Teatro Imperial.
12. Criar kit arquitetônico inicial reutilizável.
13. Preparar estrutura PBR/material library sem tratar blockout como arte final.
14. Manter streaming 1 km / subcélulas 250 m.
15. Executar pipeline real do Blender, salvar, fechar e reabrir o .blend.

Gate A:
- masterplan valida sem erro crítico;
- .blend reabre sem missing data;
- bloqueios W1 anteriores resolvidos ou explicitamente justificados;
- Cidade Antiga possui base urbana coerente;
- Hero Locations reconhecíveis por footprint/volume/acesso;
- capturas reais novas geradas;
- relatório Docs/W1_5_WORLD_FOUNDATION_RELATORIO.md;
- commit + push;
- working tree limpa.

Ao passar o Gate A, seguir imediatamente para a Etapa B.

---

### ETAPA B — Pesquisa e curadoria de skills/ferramentas

Executar a pesquisa ampla já solicitada pelo usuário.

Cobrir:
- Claude Code Agent Skills;
- Blender / bpy / Python;
- Geometry Nodes;
- hard-surface / arquitetura;
- procedural city / roads / façades / scattering;
- large scenes / Asset Browser / linked libraries / instancing;
- PBR / UV / trim sheets / decals;
- terrain / GIS / OSM / DEM apenas como técnica;
- Blender→Unity;
- Unity C# / URP / Shader Graph / VFX Graph;
- additive scenes / Addressables / world streaming;
- LOD / HLOD / occlusion / profiling;
- first-person / IK / Animation Rigging;
- vehicles / WheelCollider;
- NavMesh / NPC;
- economy / progression / anti-softlock;
- properties / housing;
- inventories / ScriptableObjects / stable IDs;
- save versioning / migrations / backups;
- UI Toolkit / map / tablet / accessibility;
- audio / VFX / weather;
- automated QA;
- build automation;
- Git/GitHub/Git LFS;
- Steamworks / Steam Cloud / Steam Input;
- localization;
- documentation;
- simulator balancing;
- procedural jobs;
- data-driven content;
- asset validation;
- visual regression.

Saída:
- Docs/SKILLS/00_INDICE_GERAL.md até 22_RECOMENDACOES.md;
- Tools/Skills/README.md;
- Tools/Skills/catalog.json;
- registrar URL, autor, licença, versão/tag/commit, dependências, risco e valor para o projeto;
- classificar ESSENTIAL / RECOMMENDED / OPTIONAL / REJECTED;
- classificar SAFE_TO_USE / REVIEW_REQUIRED / DO_NOT_INSTALL;
- selecionar TOP 10 geral e TOP 5 para W1.5/W2.

Regras:
- não instalar nada sem aprovação explícita;
- não executar código externo desconhecido;
- priorizar open source e licença comercial clara;
- manter por referência quando copiar a skill/fonte não for apropriado.

Gate B:
- biblioteca de skills documentada;
- catalog.json válido;
- TOP 10 e TOP 5 definidos;
- riscos/licenças registrados;
- commit + push;
- working tree limpa.

Ao passar o Gate B, seguir imediatamente para a Etapa C.

---

### ETAPA C — Revisão visual e gates W1.5

Criar revisão crítica das capturas reais.

Verificar:
- Santa Aurora lê como cidade grande;
- Cidade Antiga não parece grid artificial;
- Industrial não parece vazio;
- transições entre distritos existem;
- relevo/drenagem são plausíveis;
- rede viária justifica veículos;
- distâncias casa/oficina/clientes/fornecedores são coerentes;
- Hero Locations continuam narrativamente corretos;
- skyline diferencia distritos;
- não há low-poly sendo tratado como arte final.

Gerar:
- pelo menos 15 capturas reais;
- review sheet W1.5;
- comparação W1 × W1.5;
- lista PASS / NEEDS_FIX / BLOCKED.

Se houver bloqueio objetivo:
- corrigir autonomamente;
- rerodar validações;
- regerar capturas;
- repetir revisão.

Gate C:
- nenhum BLOCKED técnico/espacial conhecido;
- limitações subjetivas claramente registradas;
- commit + push;
- working tree limpa.

Ao passar o Gate C, seguir para a Etapa D.

---

### ETAPA D — W2 Cidade Antiga Base

Objetivo: iniciar a primeira região de alta fidelidade sem tentar terminar a cidade inteira.

Prioridades:
1. Kit arquitetônico modular de produção.
2. Materiais PBR-base.
3. Infraestrutura urbana e clutter controlado.
4. Hero Locations nesta ordem:
   A. Lar inicial;
   B. Oficina Aurora;
   C. Edifício Horizonte;
   D. Teatro Imperial;
   E. demais locais da Cidade Antiga.
5. Interiores somente onde gameplay exigir.
6. Escala realista, iluminação de teste e planejamento de LOD/otimização.
7. Capturas reais e medições de complexidade/performance quando possível.
8. Documentar/preparar pipeline Blender→Unity.

Regras:
- VEIN = referência de patamar visual/atmosfera, nunca fonte para copiar;
- não aceitar low-poly como arte final;
- não escalar W2 para outros distritos antes de validar Cidade Antiga;
- não quebrar protótipo Unity;
- não alterar saves/IDs sem necessidade e migração;
- não fazer merge no main.

Se o limite de uso chegar:
- parar em ponto seguro;
- salvar;
- commit;
- push;
- working tree limpa;
- registrar exatamente onde continuar.

## Regras gerais

- Trabalhar somente na branch claude/w1-masterplan.
- Nunca fazer merge no main automaticamente.
- Antes de cada etapa: git pull, reler CLAUDE.md, este arquivo e Docs/CLAUDE_NEXT_TASK.md.
- Ao concluir: validar, documentar, commit, push, working tree limpa.
- Não instalar add-ons/MCPs/dependências sem aprovação.
- Preservar IDs, saves, .meta e o protótipo Unity.
- Blockout simples é temporário; visual final deve ser realista, PBR, denso e não-low-poly.
