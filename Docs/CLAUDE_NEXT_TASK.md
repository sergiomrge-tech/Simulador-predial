# CLAUDE NEXT TASK — W3

## Cidade Antiga High Fidelity Vertical Slice

W2.5 foi concluído e registrado como **PARTIAL PASS** em `Docs/W2_5_VISUAL_FIDELITY_GATE.md`.

O próximo objetivo é transformar um recorte controlado da Cidade Antiga em referência visual real do jogo, sem ainda expandir acabamento para os demais distritos.

### Objetivo principal

Elevar a Cidade Antiga de “base de produção detalhada” para um **vertical slice visual de alta fidelidade**, com foco em:

1. terreno e leitura de relevo;
2. materiais PBR autorais;
3. vegetação urbana final;
4. iluminação e vidro;
5. LOD0 das fachadas mais vistas;
6. clutter e decals autorais;
7. consistência visual dos heróis principais;
8. performance e reprodutibilidade.

---

## 1. Terreno e relevo — leitura visual

O relevo estrutural de W2.5 está aprovado como base.

Agora melhorar sua leitura visual:

- material de terreno com blend de:
  - grama;
  - terra;
  - cascalho;
  - solo exposto;
  - concreto/pavimento residual;
- taludes com vegetação rasteira;
- transição visual entre terreno natural, calçada e lote;
- reforçar sombras e oclusão nos desníveis;
- preservar todas as cotas e rampas validadas;
- não mudar o traçado viário nem os footprints.

Meta:
o relevo precisa ser percebido também em vistas oblíquas/aéreas, não apenas ao nível da rua.

---

## 2. Materiais PBR autorais

Criar materiais de produção para o vertical slice usando fontes próprias/procedurais ou CC0 claramente registradas.

Prioridade:
- reboco envelhecido;
- concreto;
- tijolo;
- asfalto;
- meio-fio;
- pedra portuguesa;
- piso intertravado;
- metal pintado;
- galvanizado;
- ferrugem;
- madeira;
- vidro;
- cerâmica;
- telha;
- plástico;
- borracha.

Cada material deve ter, quando aplicável:
- Base Color;
- Normal;
- Roughness;
- Metallic;
- AO;
- Height opcional.

Evitar aparência “material uniforme de Blender”.

Registrar procedência/licença de qualquer fonte externa.

---

## 3. Fachadas LOD0 — recorte prioritário

Não detalhar a Cidade Antiga inteira de uma vez.

Escolher um corredor de vertical slice que contenha, idealmente:
- Lar inicial;
- Oficina Aurora;
- Horizonte;
- ao menos um comércio do Capítulo I;
- uma rua com relevo;
- uma praça ou espaço público;
- trecho com infraestrutura urbana.

Nesse corredor:
- criar fachadas LOD0 mais ricas;
- molduras;
- peitoris;
- rufos;
- caixas técnicas;
- cabos;
- toldos;
- letreiros;
- sujeira localizada;
- variação de acabamento;
- fundos/laterais visíveis tratados.

---

## 4. Vegetação urbana

Substituir proxies do recorte por vegetação de produção:

- árvores urbanas;
- arbustos;
- gramíneas;
- vegetação espontânea;
- plantas em vasos;
- vegetação de talude;
- pequenas ervas em frestas.

Exigir:
- LOD;
- variação;
- distribuição coerente;
- sem exagerar densidade;
- sem usar assets com licença duvidosa.

---

## 5. Iluminação / céu / exposição

Criar um look de iluminação de produção para o vertical slice:

- céu não estourado;
- exposição equilibrada;
- AO/contato;
- sombras mais legíveis;
- interiores com iluminação coerente;
- transição exterior/interior;
- reflexão adequada;
- teste de fim de tarde ou manhã, se melhorar leitura;
- preparar base para futuro day/night.

Não mascarar problemas de material com pós-processo excessivo.

---

## 6. Vidro e interiores visíveis

Corrigir o vidro provisório:

- transmissão/refração compatível com o pipeline;
- reflexos coerentes;
- interior visível quando apropriado;
- janelas não podem parecer placas opacas.

Nos heróis do vertical slice:
- melhorar interiores que aparecem pela rua;
- evitar vazio total;
- manter apenas interiores úteis ao gameplay completamente detalhados.

---

## 7. Clutter e decals autorais

Adicionar no corredor:
- cartazes fictícios;
- placas;
- números;
- marcas de uso;
- infiltração;
- sujeira localizada;
- ferrugem;
- óleo;
- marcas de pneu;
- lixo controlado;
- caixas;
- pallets;
- ferramentas;
- mobiliário urbano;
- sinalização de serviço.

Nada deve parecer distribuição aleatória sem lógica.

---

## 8. Heróis principais

Aplicar passe de alta fidelidade em:
1. Lar inicial;
2. Oficina Aurora;
3. Edifício Horizonte;
4. um cliente do Capítulo I.

O Teatro Imperial pode receber apenas correções de material/iluminação nesta etapa se não estiver dentro do corredor principal.

Não apagar os estados H0–H4/G0–G4 nem seus slots.

---

## 9. Performance

Registrar antes/depois:
- objetos;
- meshes;
- tris simples;
- tris instanciados;
- materiais;
- texturas;
- memória estimada;
- maior mesh;
- quantidade de luzes.

Regras:
- instancing onde adequado;
- nenhuma mesh monolítica gigante;
- LODs planejados;
- manter divisão 1 km / 250 m;
- evitar texturas gigantes sem justificativa.

---

## 10. Validação

Ao final:

1. reabrir todos os arquivos alterados em Blender novo;
2. 0 missing data;
3. masterplan/rotas continuam PASS;
4. 9 heróis continuam vinculados;
5. IDs e GP_/SLOT_/PROXY_ idênticos;
6. footprints inalterados;
7. streaming preservado;
8. gerar auditoria de complexidade;
9. documentar licenças/procedência;
10. working tree limpa.

---

## 11. Capturas reais

Criar `ArtSource/Blender/World/Reviews/W3/`.

Gerar pelo menos:
- visão geral do corredor;
- rua subindo/descendo;
- terreno/talude;
- Lar exterior;
- Lar interior;
- Oficina exterior;
- Oficina interior;
- Horizonte exterior;
- Horizonte técnico;
- cliente Capítulo I exterior;
- cliente interior;
- detalhe de material PBR;
- vegetação;
- vidro exterior/interior;
- clutter/decals;
- antes/depois comparativo W2.5 × W3;
- vista noturna ou fim de tarde apenas se realmente útil.

Capturas devem ser reais do Blender, nunca mockups.

---

## 12. Gate W3

Classificar ao final:

**PASS** somente se:
- o recorte já parecer plausível como visual de jogo comercial;
- relevo for legível;
- materiais não parecerem placeholders;
- vegetação não for proxy;
- vidro estiver funcional;
- iluminação tiver identidade;
- heróis principais estiverem visualmente coerentes;
- performance permanecer controlada.

Caso contrário:
**PARTIAL PASS** com lista objetiva de correções.

---

## 13. Documentação

Criar:
- `Docs/W3_HIGH_FIDELITY_VERTICAL_SLICE.md`

Atualizar:
- `Docs/STATUS_IMPLEMENTACAO.md`
- `Docs/W2_5_VISUAL_FIDELITY_GATE.md` apenas com link de continuidade, sem reescrever histórico.

---

## 14. Git

Branch:
`claude/w1-masterplan`

Ao terminar:
- commits organizados;
- push;
- working tree limpa;
- SHA final;
- relatório de validação;
- gate W3.

Não fazer merge no main.

## Regra de autonomia

Não aguardar confirmação para microdecisões.
Corrigir problemas encontrados durante a execução antes de finalizar.
Preservar todos os sistemas, IDs, saves, marcadores e decisões aprovadas.
