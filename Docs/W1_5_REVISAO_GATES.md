# W1.5 — Revisão visual e gates (Etapa C)

**Data:** 2026-10-03 · **Branch:** `claude/w1-masterplan`
**Base:** 26 capturas reais do Blender 5.2.1 LTS, renderizadas depois de reabrir cada `.blend` num processo novo (`ArtSource/Blender/World/Reviews/W1_5/`, `reopen_*.json` 3/3 PASS, 0 dados faltando), mais a validação estática PASS (0 erros) e as rotas pela rede viária.
**Review sheet:** `ArtSource/Blender/World/Reviews/W1_5/review_sheet.html` (W1 × W1.5 lado a lado).

---

## 1. Problemas encontrados na revisão e corrigidos nesta etapa

| # | Problema (visto nas capturas) | Correção | Verificação |
|---|---|---|---|
| C1 | **Edificações de fundo ocupavam o recuo frontal dos heróis.** No Horizonte, um prédio tapava a fachada de entrada; uma câmera caiu dentro dele. | `OldTown.forecourts()`: recuo reservado entre a frente de cada herói e a borda da sua rua (sem atravessar a rua), bloqueado para lotes; nova checagem no validador ("lot blocks the forecourt"). | Validação PASS; capturas `07b_horizonte_fachada` e `05_lar_inicial` mostram fachadas livres |
| C2 | Recuos frontais em terra crua | Recuos pavimentados no nível da calçada | Captura `07b` |
| C3 | Nenhuma captura mostrava a entrada do Horizonte | Nova câmera `CAM_OT_Horizonte_Frente` e captura `07b_horizonte_fachada` | Marquise, portões, grade e interfone visíveis |
| C4 | Câmera do lar dentro de parede depois do reempacotamento | Câmera sobre a Rua das Oficinas (sempre livre) | `05_lar_inicial` |

Depois de C1, o pipeline inteiro foi rerodado: validação, rotas, 3 geradores, 3 reaberturas e todas as capturas.

---

## 2. Gates

| Critério | Resultado | Evidência | Observação |
|---|---|---|---|
| Santa Aurora lê como cidade grande | **PASS** | `01`, `02`, `13`; ~25,7 mil edificações no layout + campanha; nenhuma célula de 1 km sem uso | Fora da Cidade Antiga é massing (caixas); ler como "cidade" e não como "arte" |
| Cidade Antiga não parece grid artificial | **PASS** | `03`, `04`; 9 bairros; entropia de orientação 0,83 (W1 = 0,0); 157 ruas sem saída, 58 becos, 10 passagens, 6 praças | Algumas esquinas chanfradas em ângulos agudos |
| Industrial não parece vazio | **PASS** | `09`, `09b`; ocupação de 27,7%; 869 galpões, 2.979 docas, 256 tanques, 207 silos, 122 chaminés, 90 subestações | — |
| Transições entre distritos existem | **PASS** | `14`; 8 zonas no spec, todas com ≥25 edifícios | — |
| Relevo e drenagem plausíveis | **PASS** | `16`; canal é o eixo mais baixo; drenagem a 4,7 m, a 218 m do canal; platô tecnológico; rampas ≤5,6% | O relevo é suave por projeto e pouco visível fora da captura de curvas de nível |
| Rede viária justifica veículos | **PASS** | rotas: Expansão a 14–19 min a pé (3 m/s); Central 31 min; data center 48 min; de carro, 5–18 min | — |
| Distâncias lar/oficina/clientes/fornecedores coerentes | **PASS** | oficina 0,4 km; ferramentas 0,4 km; revenda 0,9 km; Horizonte 1,0 km; clientes do Cap. I 4–8 min a pé | — |
| Heróis narrativamente corretos | **PASS** | `05`–`08`, `07b`; footprints iguais aos do spec; entradas, serviço e vagas conforme o JSON | — |
| Skyline diferencia distritos | **PASS** | `13`; medianas: Antiga 2, Expansão 5, Central 4, Empresarial 16 (máx. 35), Tecnológico 9 (máx. 29), Industrial 1 + estruturas | — |
| Nada de low-poly tratado como arte final | **PASS** | estágio marcado em todos os relatórios, na review sheet e em propriedades `sa_stage` dos objetos | Árvores-proxy e famílias LOD1 rotuladas como blockout |

**BLOCKED técnico ou espacial conhecido: nenhum.**

---

## 3. NEEDS_FIX (subjetivo ou acabamento, a tratar no W2/W3; não bloqueia)

| # | Item | Onde | Plano |
|---|---|---|---|
| N1 | Repetição perceptível das 47 variantes de perto; laterais e fundos simples | `04`, `07` | W2: mais variantes, acessórios por regra, decals |
| N2 | Árvores-proxy (esferas) | todas as vistas de rua | W3/W4: vegetação autoral com LOD |
| N3 | Esquinas de calçada chanfradas e pequenas sobreposições em ângulos agudos | vistas de rua | W2: filete curvo nas esquinas, rebaixos |
| N4 | Área entre o recuo do Horizonte e a rua ainda sem acabamento; paisagismo dos recuos e praças básico | `07b`, `08` | W2: paisagismo, mobiliário urbano, piso detalhado |
| N5 | Tom de revisão (Standard, exposição −1,4); céu estourado no skyline | `13` | look final é trabalho de iluminação (W4) |
| N6 | Masterplan fora da Cidade Antiga é massing | `01`, `02`, `10`–`12` | W6+: replicar o pipeline da Cidade Antiga por distrito |
| N7 | Interiores só onde validam espaço; mobiliário dos estados é proxy | `05b`, `06b` | W2/W3: mobiliário H0–H4 e G0–G4, interiores do Horizonte (prólogo) |

---

## 4. Decisão

**Gate C: aprovado tecnicamente**, sem bloqueios conhecidos. As limitações subjetivas estão registradas acima, e a aprovação visual final continua sendo do usuário. Próxima etapa da fila: **D — W2 Cidade Antiga Base**.
