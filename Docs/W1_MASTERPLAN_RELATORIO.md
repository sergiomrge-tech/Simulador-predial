# W1 — RELATÓRIO DE GERAÇÃO E VALIDAÇÃO DO MASTERPLAN

**Data:** 2026-10-03
**Blender:** 5.2.1 LTS (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, fora do PATH)
**Arquivo:** `ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend` (S0 / massing, não é arte final)
**Status:** gate técnico **PASS**; aprovação espacial/narrativa **pendente de revisão do usuário**

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

**Technology:** o data center tem pátio de energia e perímetro técnico parcial (muros S/W). A smart tower fica 750 m a sudeste, sem competir com o campus.

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

Depois que o usuário aprovar as capturas: **W2 — Cidade Antiga, blockout de produção** (traçado irregular, calçadas, shells de bairro, lar inicial, Oficina Aurora, Horizonte, primeiros clientes, Teatro), conforme `Docs/W1_MASTERPLAN_CHECKLIST.md` seção H.
