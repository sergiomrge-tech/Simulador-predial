# W1 — CHECKLIST DE CONSTRUÇÃO DO MASTERPLAN

**Marco:** Santa Aurora Foundation / World Foundation W1  
**Objetivo:** obter um masterplan Blender grande, métrico, reabrível e coerente com a história antes de aprofundar novas missões.

---

## A. Pré-validação

- [ ] Repositório limpo.
- [ ] Ler `Docs/WORLD_BIBLE_SANTA_AURORA_V1.md`.
- [ ] Ler `Docs/REGISTRO_ESTRUTURAS_SANTA_AURORA_V1.md`.
- [ ] Ler `Docs/ART_BIBLE_REALISMO_SANTA_AURORA.md`.
- [ ] Confirmar Blender disponível.
- [ ] Executar:
  `python Tools/Map/validate_masterplan.py .`
- [ ] Resultado precisa ter `passed: true`.

---

## B. Gerar masterplan

Com Blender no PATH:

`blender --background --factory-startup --python Tools/Blender/create_santa_aurora_masterplan.py -- --root CAMINHO_DO_PROJETO`

Saída esperada:

- `ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend`
- `ArtSource/Blender/World/masterplan_generation_report.json`

O script não deve sobrescrever `SantaAurora_Masterplan.blend` antigo.

---

## C. Verificação Blender

Abrir manualmente `SantaAurora_Masterplan_v1.blend`.

### Conferir
- [ ] unidade métrica;
- [ ] terreno 8×8 km;
- [ ] seis distritos;
- [ ] 8 vias principais;
- [ ] 24 locais da campanha;
- [ ] 20 locais de vida/economia;
- [ ] grid 1 km;
- [ ] IDs nos objetos;
- [ ] câmera top;
- [ ] câmera oblíqua;
- [ ] escala plausível dos footprints.

---

## D. Revisão espacial

### Cidade Antiga
- [ ] lar inicial perto da Oficina Aurora, mas não no mesmo lote;
- [ ] Horizonte reconhecível na malha;
- [ ] mercearia/restaurante/apartamentos acessíveis por ruas locais;
- [ ] Teatro Imperial funciona como landmark;
- [ ] saída clara para Avenida Santa Aurora e Avenida do Trabalho.

### Expansão
- [ ] condomínios têm lotes grandes;
- [ ] escola e hospital possuem acesso;
- [ ] hotel comporta doca/serviço;
- [ ] HQ futura comporta frota.

### Industrial
- [ ] galpão e fábrica possuem pátios;
- [ ] caminhões podem teoricamente manobrar;
- [ ] casa de drenagem fica próxima do canal/marginal.

### Corporate
- [ ] torres e shopping formam skyline;
- [ ] hospital 03:17 possui acesso técnico;
- [ ] Vértice fica em região corporativa plausível.

### Technology
- [ ] data center possui perímetro técnico;
- [ ] smart tower não compete espacialmente com o campus do data center.

### Civic
- [ ] Santa Aurora Central tem campus próprio;
- [ ] corredores viários chegam ao complexo;
- [ ] área suporta múltiplos edifícios e túneis de serviço.

---

## E. Screenshots obrigatórios

Capturas reais do Blender, nunca mockups:

1. visão superior 8×8 km;
2. visão oblíqua da cidade;
3. Cidade Antiga;
4. Expansão;
5. Industrial;
6. Corporate;
7. Technology;
8. Santa Aurora Central;
9. composição do skyline;
10. grid/streaming com locais marcados.

Salvar em:
`ArtSource/Blender/World/Reviews/W1/`

---

## F. Reabertura

- [ ] salvar;
- [ ] fechar Blender;
- [ ] abrir novamente o `.blend`;
- [ ] confirmar ausência de missing data;
- [ ] confirmar objetos/coleções;
- [ ] registrar contagem de objetos;
- [ ] registrar versão do Blender.

---

## G. Gate de aprovação W1

W1 só recebe PASS quando:

- [ ] validação estática passa;
- [ ] geração Blender termina sem exceção;
- [ ] arquivo reabre;
- [ ] screenshots reais revisados;
- [ ] todos os 24 locais da campanha estão posicionados;
- [ ] todos os locais possuem acesso plausível;
- [ ] não há footprints sobrepostos;
- [ ] nenhum distrito parece pequeno demais;
- [ ] distâncias justificam transporte;
- [ ] há reserva de expansão;
- [ ] o masterplan corresponde à história.

**Não avaliar qualidade final de malha/PBR nesta etapa. W1 é massing espacial.**

---

## H. Depois do PASS

Próximo marco:

### W2 — Cidade Antiga / arquitetura de produção

1. terreno detalhado;
2. malha viária local;
3. calçadas;
4. infraestrutura;
5. shells de bairro;
6. kit arquitetônico PBR;
7. lar inicial;
8. Oficina Aurora;
9. Horizonte;
10. primeiros clientes;
11. Teatro Imperial;
12. iluminação e clutter;
13. LOD/HLOD;
14. integração Unity.

---

## I. Regra de segurança do projeto

Enquanto W1/W2 são produzidos:

- preservar o protótipo Unity atual;
- não remover o catálogo existente;
- não mudar IDs de save;
- não migrar coordenadas runtime sem tarefa dedicada;
- não afirmar que mundo grande está jogável antes de integração e testes.
