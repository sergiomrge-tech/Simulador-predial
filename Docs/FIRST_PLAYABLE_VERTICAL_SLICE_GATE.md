# Gate — Primeiro Build Jogável da Cidade Antiga

Este documento define o mínimo necessário para gerar o primeiro executável Windows com o novo mundo de Santa Aurora.

## Objetivo

Entregar um build de teste em que o jogador consiga:

1. iniciar no Lar;
2. caminhar pela rua;
3. perceber o relevo;
4. chegar à Oficina Aurora;
5. seguir até o Horizonte;
6. entrar no prédio;
7. acessar ao menos uma área técnica;
8. atravessar fronteiras de streaming;
9. chegar à Mercearia;
10. retornar sem corrupção de cena/save.

Não é necessário que o resto de Santa Aurora esteja em arte final.

---

## Gate A — W3 visual

Necessário:
- corredor Lar → Oficina → Horizonte → Mercearia concluído;
- materiais sem aparência de placeholder;
- vegetação do corredor não pode ser proxy grosseiro;
- vidro legível;
- iluminação aceitável;
- relevo claramente visível;
- capturas reais revisadas.

Resultado permitido:
- PASS;
- ou PARTIAL PASS apenas se as limitações não impedirem o teste jogável.

---

## Gate B — Exportação Blender → Unity

Para cada célula piloto:

- escala 1:1;
- eixos corretos;
- pivô/origem documentado;
- layers separados;
- nomes preservados;
- LODs preservados;
- gameplay markers preservados;
- nenhum material faltando;
- colliders preparados.

Primeira célula:
`SA_M01_01_S00_02` — Lar inicial.

Depois:
`SA_M01_01_S01_03` — Oficina Aurora.

---

## Gate C — Cenas aditivas

Usar os scaffolds preparados na branch técnica.

Cada Scene precisa:
- exatamente um `WorldCellRoot`;
- ID igual ao nome da Scene;
- root em transform identity;
- subroots:
  - Terrain;
  - Roads;
  - Architecture;
  - Infrastructure;
  - Props;
  - Vegetation;
  - Lighting;
  - Gameplay.

O Bootstrap continua dono dos sistemas globais.

---

## Gate D — Streaming

Primeiro teste:
- 3×3 células carregadas;
- 5×5 como anel de retenção;
- unload de células distantes;
- nenhuma duplicação de Scene;
- nenhuma célula presa após unload.

Métricas:
- tempo de load;
- tempo de unload;
- maior hitch;
- memória antes/depois;
- GC alloc.

---

## Gate E — Gameplay

No primeiro build:

### obrigatório
- FirstPersonController funcional;
- colisão de chão, paredes e escadas;
- prompts;
- tablet;
- entrada no Horizonte;
- ao menos um marker `GP_` reconhecido;
- serviço do prólogo carregável;
- save/load sem perda de carreira.

### pode permanecer provisório
- NPCs;
- tráfego;
- veículos dirigíveis;
- day/night completo;
- pedestres;
- clima;
- interiores não usados.

---

## Gate F — Performance

Alvo:
- 60 FPS em 1080p na máquina de referência;
- sem stutter repetitivo ao atravessar célula;
- sem crescimento contínuo de memória;
- nenhuma alocação GC contínua relevante em exploração.

Se o build ficar abaixo do alvo:
1. medir antes de reduzir arte;
2. revisar LOD/HLOD;
3. revisar sombras;
4. revisar vegetação;
5. revisar materiais/draw calls;
6. revisar raio de streaming.

---

## Gate G — QA

Rodar:

- EditMode tests do streaming;
- validador do manifesto;
- validador das cenas piloto;
- smoke test antigo do gameplay;
- novo smoke de travessia entre células quando disponível.

Capturas obrigatórias do executável:
1. Lar;
2. rua com relevo;
3. Oficina;
4. Horizonte exterior;
5. Horizonte interior;
6. Mercearia;
7. overlay/profiler de uma travessia de célula.

---

## Critério para entregar ao usuário

Só gerar o executável para teste quando:

- projeto compilar sem erros;
- não houver missing references;
- player não cair pelo mapa;
- portas/entradas essenciais funcionarem;
- streaming básico estiver estável;
- save antigo continuar carregando;
- não houver erro crítico conhecido que impeça o fluxo Lar → Oficina → Horizonte → Mercearia.

O build pode ser chamado:

**Facility Ops — Cidade Antiga Vertical Slice v0.1**

Esse build será um teste técnico/jogável, não uma demo pública.
