# W1 — RELATÓRIO DE GERAÇÃO E VALIDAÇÃO DO MASTERPLAN

**Data:** 2026-10-03
**Blender:** 5.2.1 LTS (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, fora do PATH)
**Arquivo:** `ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend` (S0 / massing, não é arte final)
**Status:** gate técnico **PASS**. Revisão crítica (seção 7): **W1 NÃO APROVADO**, com 2 bloqueios. Aprovação final é decisão do usuário.
**Folha de revisão:** `ArtSource/Blender/World/Reviews/W1/review_sheet.html` (gerada por `Tools/Map/build_w1_review_sheet.py`)

---

## 1. Como reproduzir

```
powershell -ExecutionPolicy Bypass -File Tools/Blender/Run-W1Masterplan.ps1
```

O runner executa, em ordem:

1. `python Tools/Map/validate_masterplan.py .` → `Docs/masterplan-validation-v1.json`
2. `blender --background --factory-startup --python Tools/Blender/create_santa_aurora_masterplan.py -- --root .`
   → `.blend` + `ArtSource/Blender/World/masterplan_generation_report.json`
3. `blender --background --factory-startup <blend> --python Tools/Blender/verify_masterplan_v1.py -- --root .`
   → reabre o arquivo em processo novo, audita e renderiza as 10 capturas em `ArtSource/Blender/World/Reviews/W1/`
   → `Reviews/W1/w1_reopen_report.json`

O layout é determinístico (seed fixa) e vem de `Tools/Map/masterplan_layout.py`, que é usado **tanto pelo validador quanto pelo gerador**. O que é validado é exatamente o que é gerado. O gerador recusa gerar se o layout tiver erros.

O `.blend` antigo `ArtSource/Blender/SantaAurora_Masterplan.blend` não foi tocado.

---

## 2. Resultado

| Item W1 | Resultado |
|---|---|
| Validação estática | PASS: 0 erros, 0 warnings |
| Geração Blender | sem exceção, 874 objetos |
| Reabertura | PASS em processo novo: 0 missing data, 10 coleções, 24/24 campanha, 20/20 vida, 8 vias, 64 células |
| Unidade | METRIC, scale 1.0; terreno 8000×8000 m |
| Distritos | 6, com tint por propriedade resolvida em subcélulas de 250 m |
| Corredores | 8 polilinhas (R01–R08), arterial 30 m, coletora 18 m |
| Malha local | 319,8 km de ruas de 12 m, 6 trechos desconectados descartados |
| Acesso | 44 acessos gerados; todos os 44 locais com via a ≤120 m (maior: leisure.fishing, 117,6 m, parque linear) |
| Sobreposição | nenhum lote/marcador sobreposto; nenhuma via/canal invade lote (recuo de 6 m) |
| Skyline | 530 shells (old 170, expansion 110, civic 45, corporate 65, industrial 75+10 chaminés, technology 55) + tecido de quadra |
| Capturas | 10 renders Workbench reais do arquivo salvo, revisados visualmente |
| Reserva de expansão | 32,9% das subcélulas fora de distritos (transição/reserva) |

### Distâncias-chave (linha reta)

| Par | m |
|---|---:|
| home.starter → garage | 206 (lotes distintos) |
| garage → horizonte | 495 |
| garage → imperial | 820 |
| garage → recurringcondo | 3050 |
| garage → central | 3890 |
| garage → factory | 4627 |
| garage → mall | 5028 |
| garage → datacenter | 7006 |

A pé o bairro inicial funciona; Expansão, Central e os demais distritos justificam veículo.

---

## 3. Ajustes feitos no spec (e por quê)

A validação original passava, mas só verificava limites, IDs e sobreposição entre lotes. Com a checagem de vias × lotes, apareceram conflitos reais:

| Problema encontrado | Correção |
|---|---|
| R02 reta passava sobre `garage` | R02 virou polilinha a x≈-2745, correndo em frente à Oficina Aurora |
| R01 atravessava `vertice` | R01 contorna pelo sul (z≈290 em x=1900) e passa ao sul da blackouttower |
| R03 atravessava o campus `central` | R03 termina no portão sul do campus (z=410) |
| R04 atravessava `datacenter` | R04 passa a sudeste do campus do data center |
| R05 atravessava `logistics` | R05 passa ao sul do galpão (z≈1440) |
| `drainage` a 625 m da Marginal | Canal (`canal.drainage`, 36 m) adicionado ao spec; R08 corre paralela, a 62 m, pela margem sul/oeste |
| R08 a 3,3 m da casa de bombas | `drainage` deslocada 30 m W / 30 m S para (-1130, 3070), ainda junto ao canal |
| Parque municipal só como marcador | `openSpaces.park.municipal` 260×200 m |

Os campos `from`/`to` das vias continuam presentes (primeiro/último ponto) para compatibilidade; o campo novo `points` tem a geometria completa. Nenhum ID foi alterado. O catálogo runtime e as coordenadas da Unity **não** foram modificados.

---

## 4. Revisão espacial (checklist D)

**Cidade Antiga:** lar a 206 m da Oficina, em outro lote. Horizonte, mercearia, restaurante e apartamentos ficam em ruas locais. O Teatro Imperial é o maior volume horizontal do bairro, com caixa cênica de 29 m. A R02 cruza o bairro de norte a sul e a R01 passa ao norte, na faixa de transição.

**Expansão:** os condomínios têm pódio + 2 ou 3 torres em lotes de 145×180 e 160×200. Escola e hospital pequeno têm acesso por rua local. O hotel tem doca de serviço; a HQ tem galpão de frota e área de carga.

**Industrial:** a fábrica tem pátio de 200×80 m e o galpão tem pátio de caminhões de 220×60 m. A casa de bombas fica entre o canal e a Marginal.

**Corporate:** blackouttower (114 m) e smarttower (91 m) mais shells de até 125 m formam o skyline vertical. O hospital 03:17 tem ala de rota técnica. O Vértice fica na Av. Santa Aurora.

**Technology:** o data center tem pátio de energia e perímetro técnico parcial (muros S/W). A smart tower fica a cerca de 1,0 km a sudeste, sem competir com o campus.

**Central:** campus 360×420 m com 10 alas nomeadas (administrativo, monitoramento, data center municipal, telecom, emergência, distribuição elétrica, geradores, bombas, HVAC, automação), túneis de serviço em cruz e pátio central. R03 chega ao portão sul, R04 sai a leste e R01/R05 passam a sul/norte.

---

## 5. Limitações conhecidas (honestas)

- **Malha ortogonal regular**, especialmente na Cidade Antiga. Isso serve para massing, mas um bairro histórico real terá traçado irregular. Revisar em W2.
- **Faixas de transição vazias** entre distritos (só vias). O World Bible pede bairros de transição, postos e vegetação; não foram modelados em W1.
- **Terreno plano**: a topografia descrita (cota baixa a SW, platô NE) não foi aplicada.
- **Costuras entre distritos**: grades com espaçamentos diferentes não se alinham na divisa; a conexão acontece pelas arteriais.
- **Industrial**: o tecido de galpões gerou só 22 volumes extras (muitos blocos são descartados por tocarem corredores). O distrito lê como industrial, mas pode ficar mais denso.
- **Marcadores de vida/economia** são cubos de 20×20 m sem projeto de imóvel.
- **Visual**: Workbench com cores de leitura. Nada aqui representa material, PBR ou estilo final; a regra "não low-poly" vale para a produção, não para este massing.
- Os itens do gate "corresponde à história", "nenhum distrito parece pequeno demais" e "distâncias justificam transporte" são julgamentos. O relatório dá a evidência, mas **a aprovação é do usuário**.

---

## 6. Próximo passo

Não avançar para W2 antes de resolver os bloqueios da seção 7 (iteração W1.1) e de o usuário aprovar as capturas. Depois: **W2 — Cidade Antiga, blockout de produção** (traçado irregular, calçadas, shells de bairro, lar inicial, Oficina Aurora, Horizonte, primeiros clientes, Teatro), conforme `Docs/W1_MASTERPLAN_CHECKLIST.md` seção H.

---

## 7. Revisão crítica das capturas (2026-10-03)

As 10 capturas obrigatórias foram revisadas, junto com uma captura extra de destaque de distritos (`11_district_highlight.jpg`: cores saturadas, sem shells, só no passe de render; o `.blend` não é salvo). As distâncias agora são medidas **pela rede viária** com `Tools/Map/masterplan_routes.py` → `Docs/masterplan-routes-v1.json`, e não mais em linha reta.

### 7.1 Por captura

| # | Captura | Distrito | Câmera | Parecer |
|---|---|---|---|---|
| 01 | `01_top_8km.jpg` | cidade | CAM_Masterplan_Top | Atenção: distritos e vias legíveis; 11/64 células sem distrito fazem a cidade parecer "ilhas" |
| 02 | `02_oblique_city.jpg` | cidade | CAM_Masterplan_Oblique | Atenção: plana e uniforme; sem marcos fora do Corporate |
| 03 | `03_cidade_antiga.jpg` | Cidade Antiga | CAM_District_old | **Bloqueia**: grade perfeita de 180 m e nenhuma ferrovia/porto seco, contra a lore |
| 04 | `04_expansao.jpg` | Expansão | CAM_District_expansion | **Bloqueia**: nenhuma ligação direta com a Cidade Antiga (desvio até 3,4×) |
| 05 | `05_industrial.jpg` | Industrial | CAM_District_industrial | Atenção: pátios OK; tecido ralo (107 volumes / 9,3 km²) |
| 06 | `06_corporate.jpg` | Corporate | CAM_District_corporate | Adequado: hierarquia e skyline (28 torres ≥60 m, máx. 125 m) |
| 07 | `07_technology.jpg` | Technology | CAM_District_technology | Atenção: grande e vazio (6,3% de ocupação, 2 locais) |
| 08 | `08_santa_aurora_central.jpg` | Central | CAM_District_civic | Adequado: campus legível; falta eixo cívico |
| 09 | `09_skyline.jpg` | cidade | CAM_Skyline | Atenção: lê como cidade média-grande, não metrópole |
| 10 | `10_streaming_grid.jpg` | cidade | CAM_Masterplan_Top + grid | Adequado: 64 células nomeadas; no máximo 3 locais por célula |

### 7.2 Parece uma cidade grande?

**Parcialmente.** Em planta, a escala é de cidade grande. Em perspectiva, lê como cidade média-grande com um centro empresarial. Motivos:
- ocupação do solo baixa: Cidade Antiga 23,7%, Expansão 10,7%, Civic 9,8%, Industrial 15,7%, Corporate 16,0%, Technology 6,3%;
- 11 de 64 células de 1 km sem distrito;
- malha ortogonal repetida e terreno plano;
- sem ferrovia, sem vegetação e sem marcos fora do Corporate.

### 7.3 Algum distrito pequeno demais?

**Não.** Todos têm entre 5,06 e 9,30 km². O risco real é o oposto: **Technology** e **Industrial** parecem grandes e vazios. A Cidade Antiga concentra os 8 locais iniciais num núcleo de cerca de 1,4×1,2 km.

### 7.4 As distâncias justificam veículos?

**Sim.** Capítulo I a pé: 8–16 min da garagem aos clientes (0,67–1,37 km pela rede). Do Capítulo II em diante, os locais fora da Cidade Antiga ficam a 4,6–8,9 km pela rede, o que dá 56–107 min a pé contra 9–18 min de carro urbano. A revenda de usados fica a 0,87 km do lar. A escala de tempo do jogo ainda não foi definida, então esses minutos são equivalentes reais. Parte da distância até a Expansão é artificial (desvio de 2,3–3,4×) e vai encolher com a ligação Old↔Expansão; a necessidade de veículo continua.

### 7.5 Coerência dos 24 locais com a história

A progressão espacial acompanha a campanha: Cidade Antiga → Expansão (II–III) → Corporate/Industrial (IV–VI, IX–XI) → Technology (VII) → Central (XII–XIV). Pontos fortes:
- o condomínio perdido fica a cerca de 700 m do condomínio de Helena;
- o hospital 03:17 fica a 16 min de carro, o que reforça a tensão do chamado;
- no Cap. VII, HQ, data center e smart tower ficam em lados opostos da cidade, o que força a priorização;
- todas as arteriais convergem em Central.

Contradições:
1. **Sem ligação Old↔Expansão.** O Cap. II mistura Teatro (Old) com escola e condomínio (Expansão), e a lore diz que a Expansão cresceu a partir da cidade antiga.
2. **Sem ferrovia nem porto seco.** A lore e o `MAPA_CAMPANHA.md` dizem que a Cidade Antiga nasceu "ao redor da ferrovia, do porto seco e das primeiras indústrias", mas ela está separada do Industrial por cerca de 1 km vazio.
3. **Relevo × drenagem.** O World Bible põe a cota mais baixa no SW, mas o canal corre no norte. A enchente do Cap. VIII precisa de uma lógica consistente. Requer decisão do usuário.

Também: o Teatro Imperial não funciona como marco (falta praça ou eixo), e Central não tem eixo cívico de chegada.

### 7.6 Correções exigidas antes de reapresentar (W1.1)

1. **Bloqueio**: ligação viária Cidade Antiga ↔ Expansão (coletora leste-oeste no sul) e costura das malhas locais nas divisas. Meta: desvio ≤1,6 até school, recurringcondo, hotel e smallhospital.
2. **Bloqueio**: corredor ferroviário oeste e porto seco ligando Cidade Antiga, R07 e Industrial, com armazéns antigos na borda oeste.
3. Definir relevo e drenagem e aplicar terreno com declividade suave.
4. Ocupar as faixas de transição. Meta: no máximo 5 células de 1 km sem uso.
5. Praça e eixo de chegada do Teatro Imperial; eixo cívico de Central.
6. Malha orgânica e ocupação ≥35% na Cidade Antiga (pode ficar para o blockout W2).
7. Revisar escala ou densidade de Technology e Industrial.

### 7.7 Regras mantidas

- Tudo aqui é massing S0. Nenhuma tentativa de transformar o massing em arte final.
- **O visual final de Santa Aurora não pode ser low-poly** (Art Bible: PBR, bevels, decals, clutter funcional, LOD, iluminação atmosférica).
- **VEIN é apenas referência de patamar visual** (realismo, atmosfera, densidade, materialidade). Nenhum asset, textura, prédio, layout ou mapa é copiado.
- **W1 não foi aprovado automaticamente.** A decisão é do usuário, depois das correções W1.1.

---

## 8. Resolução no W1.5 (2026-10-03)

As correções W1.1 foram absorvidas pelo marco W1.5 (`Docs/W1_5_WORLD_FOUNDATION_RELATORIO.md`):

1. **Ligação Old↔Expansão**: R09 Avenida dos Ferroviários. Desvios até school/recurringcondo/hotel/smallhospital agora entre 1,07× e 1,36× (meta ≤1,6).
2. **Ferrovia e porto seco**: Linha Ferroviária Oeste, Estação Velha, pátio do porto seco e ramal da logística.
3. **Relevo × drenagem**: decidido pelo usuário (canal como eixo mais baixo) e implementado.
4. **Faixas de transição**: 8 zonas; nenhuma célula de 1 km sem uso.
5. **Praça e eixo do Teatro**: Largo do Imperial com pórtico; eixo institucional Expansão → Central.
6. **Malha orgânica da Cidade Antiga**: 9 bairros, ocupação de 30% no núcleo (a meta de 35% vale para o W2, com lotes mais profundos).
7. **Technology e Industrial**: Industrial com ocupação de 28%; Tecnológico com campus, verdes e 22%.

O W1 original (`SantaAurora_Masterplan_v1.blend` e capturas em `Reviews/W1/`) foi mantido para comparação.

