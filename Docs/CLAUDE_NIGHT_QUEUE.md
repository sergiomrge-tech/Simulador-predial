# FILA AUTÔNOMA — FACILITY OPS

Esta fila foi explicitamente autorizada pelo usuário em 2026-10-03.

O Claude Code pode avançar entre as etapas abaixo sem pedir confirmação a cada transição, desde que os gates objetivos estejam satisfeitos e não exista bloqueio crítico, conflito de Git, risco de licença ou alteração destrutiva de IDs/saves.

## Ordem obrigatória

### ETAPA A — Skills e ferramentas
Executar integralmente a pesquisa e curadoria descrita em `Docs/CLAUDE_NEXT_TASK.md`.

Gate A:
- `Docs/SKILLS/` criado e preenchido;
- `Tools/Skills/catalog.json` válido;
- TOP 10 e TOP 5 definidos;
- licenças/riscos documentados;
- nada externo instalado sem aprovação;
- commit + push;
- working tree limpa.

Ao passar o Gate A, seguir imediatamente para a Etapa B.

---

### ETAPA B — W1.5 Santa Aurora Foundation

Objetivo: fechar a fundação espacial do mundo e preparar a Cidade Antiga como primeira região de produção.

Executar:

1. Refinar relevo urbano e drenagem.
2. Corrigir a ligação viária Cidade Antiga ↔ Expansão.
3. Implementar presença coerente de ferrovia/porto seco conforme lore.
4. Tornar a Cidade Antiga menos ortogonal e mais orgânica.
5. Preencher transições vazias entre distritos.
6. Aumentar densidade e variedade do Industrial.
7. Refinar as 8 vias principais, acessos, cruzamentos e vias coletoras.
8. Melhorar skyline e leitura de alturas por distrito.
9. Preservar 24 locais de campanha, 20 de vida/economia, IDs e coerência narrativa.
10. Preparar Cidade Antiga com:
   - ruas principais/secundárias;
   - becos;
   - calçadas;
   - estacionamentos;
   - entradas de garagem;
   - infraestrutura urbana base;
   - famílias de massing variadas.
11. Avançar arquitetura-base dos Hero Locations da Cidade Antiga:
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
13. Preparar estrutura PBR/material library sem transformar o blockout em arte final.
14. Manter streaming 1 km / subcélulas 250 m.
15. Executar pipeline real do Blender, salvar, fechar e reabrir o .blend.

Gate B:
- masterplan valida sem erro crítico;
- .blend reabre sem missing data;
- bloqueios W1 anteriores resolvidos ou explicitamente justificados;
- Cidade Antiga possui base urbana coerente;
- Hero Locations reconhecíveis por footprint/volume/acesso;
- capturas reais novas geradas;
- relatório `Docs/W1_5_WORLD_FOUNDATION_RELATORIO.md`;
- commit + push;
- working tree limpa.

Ao passar o Gate B, seguir para a Etapa C.

---

### ETAPA C — Revisão visual e gates W1.5

Criar revisão crítica das capturas reais.

Verificar objetivamente:

- Santa Aurora lê como cidade grande;
- Cidade Antiga não parece grid artificial;
- Industrial não parece vazio;
- transições entre distritos existem;
- relevo/drenagem são plausíveis;
- rede viária justifica veículos;
- distâncias entre casa/oficina/clientes/fornecedores são coerentes;
- Hero Locations permanecem narrativamente corretos;
- skyline diferencia distritos;
- nenhum asset final está sendo tratado como low-poly aceitável.

Gerar:
- pelo menos 15 capturas reais;
- review sheet W1.5;
- comparação W1 × W1.5;
- lista PASS / NEEDS_FIX / BLOCKED.

Se houver bloqueio objetivo:
- corrigir autonomamente;
- rerodar validações;
- regerar capturas;
- repetir a revisão.

Se restar apenas aprovação subjetiva do usuário, registrar isso, mas é permitido começar a Etapa D de forma limitada na Cidade Antiga, sem propagar arte final para outros distritos e sem merge no main.

Gate C:
- nenhum BLOCKED técnico/espacial conhecido;
- limitações subjetivas claramente registradas;
- commit + push;
- working tree limpa.

---

### ETAPA D — W2 Cidade Antiga Base

Objetivo: iniciar a primeira região de alta fidelidade sem tentar terminar a cidade inteira.

Prioridade:

1. Kit arquitetônico modular de produção:
   - paredes;
   - quinas;
   - portas;
   - janelas;
   - molduras;
   - telhados;
   - beirais;
   - grades;
   - portões;
   - calhas;
   - escadas;
   - rampas;
   - muros;
   - calçadas.

2. Materiais PBR-base:
   - concreto;
   - reboco;
   - tijolo;
   - asfalto;
   - metal;
   - aço pintado;
   - ferrugem;
   - madeira;
   - vidro;
   - cerâmica;
   - plástico;
   - borracha.

3. Ambiente urbano:
   - postes;
   - iluminação pública;
   - caixas elétricas;
   - hidrômetros;
   - drenagem;
   - tampas;
   - telecom;
   - placas;
   - hidrantes;
   - lixo/clutter controlado;
   - vegetação urbana.

4. Hero Locations, nesta ordem:
   A. Lar inicial;
   B. Oficina Aurora;
   C. Edifício Horizonte;
   D. Teatro Imperial;
   E. demais locais da Cidade Antiga.

5. Para cada Hero Location:
   - exterior;
   - acessos;
   - serviço;
   - estacionamento quando aplicável;
   - arquitetura coerente;
   - interiores somente onde gameplay exigir;
   - escala realista;
   - PBR;
   - iluminação de teste;
   - LOD/otimização planejados.

6. Criar capturas reais e medições de complexidade/performance sempre que possível.

Regras:
- VEIN = referência de patamar visual/atmosfera, nunca fonte para copiar.
- Não aceitar low-poly como arte final.
- Não escalar W2 para os demais distritos antes de validar Cidade Antiga.
- Não quebrar protótipo Unity.
- Não alterar saves/IDs sem migração e necessidade demonstrada.
- Não fazer merge no main.

Gate D parcial:
- primeiro vertical slice visual da Cidade Antiga claramente superior ao massing;
- pelo menos Lar + Oficina + Horizonte com evolução concreta;
- pipeline Blender→Unity documentado/preparado;
- capturas reais;
- relatório de continuidade;
- commit + push.

Se o limite de uso chegar antes disso:
- parar em ponto seguro;
- salvar;
- commit;
- push;
- working tree limpa;
- registrar exatamente onde continuar.

## Uso de recursos

Enquanto houver capacidade:
- prefira trabalho estrutural de alto valor;
- evite polimento microscópico;
- evite reprocessar imagens sem necessidade;
- reutilize ferramentas/skills aprovadas;
- não instale dependências sem autorização explícita.

## Conclusão noturna

Ao parar, atualizar:
- `Docs/STATUS_IMPLEMENTACAO.md`;
- relatório da etapa corrente;
- próximo ponto de continuidade;
- SHA final;
- validações realizadas;
- limitações/bloqueios.
