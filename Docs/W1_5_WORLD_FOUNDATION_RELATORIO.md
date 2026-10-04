# W1.5 — SANTA AURORA FOUNDATION + CIDADE ANTIGA BASE

**Data:** 2026-10-03
**Blender:** 5.2.1 LTS (headless, `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`)
**Branch:** `claude/w1-masterplan` (sem merge no `main`)
**Status:** base estrutural concluída e verificada. **Não é arte final.** A aprovação visual é do usuário.
**Review sheet:** `ArtSource/Blender/World/Reviews/W1_5/review_sheet.html` (W1 × W1.5 + 26 capturas reais)
**Gates da Etapa C:** `Docs/W1_5_REVISAO_GATES.md`

---

## 1. Como reproduzir

```
powershell -ExecutionPolicy Bypass -File Tools/Blender/Run-W15World.ps1
```

O runner executa, em ordem:
1. validação estática;
2. rotas pela rede viária;
3. geração do masterplan, da Cidade Antiga e do kit;
4. reabertura de cada `.blend` em processo novo, com auditoria e capturas.

Todo o layout é determinístico. A mesma base Python (`Tools/Map/`) alimenta o validador, as rotas e os três geradores Blender.

| Arquivo | Conteúdo | Objetos |
|---|---|---:|
| `ArtSource/Blender/World/SantaAurora_Masterplan_v1_5.blend` | cidade inteira 8×8 km (massing + relevo + vias) | 526 |
| `ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend` | Cidade Antiga, base de produção | 1.267 |
| `ArtSource/Blender/Kits/SantaAurora_CidadeAntiga_Kit_v1.blend` | kit modular, infraestrutura, famílias, materiais (assets marcados) | 280 |
| `ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend` | W1, mantido intacto para comparação | — |

Relatórios gerados:
- `Docs/masterplan-validation-v1.json`
- `Docs/masterplan-routes-v1.json`
- `ArtSource/Blender/World/masterplan_generation_report.json`
- `ArtSource/Blender/World/OldTown/oldtown_generation_report.json`
- `ArtSource/Blender/World/OldTown/oldtown_streaming_manifest_v1.json`
- `ArtSource/Blender/Kits/kit_report.json`
- `ArtSource/Materials/material_library_v1.json`
- `ArtSource/Blender/World/Reviews/W1_5/reopen_*.json`

---

## 2. O que mudou

### 2.1 Relevo (`Tools/Map/sa_terrain.py`)
- A cidade escoa para o canal, que é o eixo mais baixo (decisão do usuário no W1.5).
- Superfície entre 2,6 e 40,0 m, média de 20,4 m.
- A casa de drenagem fica a 4,7 m, junto ao canal.
- Platô Tecnológico elevado: média de 26,1 m, com borda em talude suave.
- Colina do Alto do Horizonte na Cidade Antiga.
- Ondulação suave entre bairros.
- Canal com leito e taludes, bacia de retenção murada.
- Rampa máxima nas vias: 5,6% (limite de 6% nas arteriais e 8% nas coletoras), dirigível.

### 2.2 Cidade Antiga orgânica (`Tools/Map/oldtown_layout.py` + `oldtown_heroes_v1.json`)
- 9 bairros com orientação, tamanho de quadra e deformação próprios: Largo da Estação, Vila Horizonte, Bairro Imperial, Oficinas, Alto da Aurora, Mercado Norte, Leste Antigo, Porto Seco e Vila Sul.
- 7 ruas principais desenhadas à mão, para que todo herói tenha frente para uma rua. Somam-se R02, R09 e a ferrovia histórica com a Estação Velha e o pátio do porto seco.
- 157 ruas sem saída, 58 becos, 10 passagens, 6 praças e 76 costuras entre bairros. Entropia de orientação 0,83 (a grade do W1 era 0,0).
- 13.865 lotes em 10 famílias e 47 variantes; ocupação do núcleo de 30%. Os recuos frontais dos heróis ficam reservados e pavimentados até a rua (correção da Etapa C).

### 2.3 Transições (`transitionZones` no spec)
8 zonas:
- Cidade Antiga → Expansão;
- Estação Norte/serviços;
- Industrial → Central;
- eixo institucional Expansão → Central;
- escritórios Central → Empresarial;
- campus Empresarial → Tecnológico;
- Várzea do Canal;
- Expansão Leste.

**Nenhuma célula de 1 km sem uso** (o W1 tinha 11).

### 2.4 Industrial
- De 107 volumes no W1 para 869 galpões, 2.979 docas, 720 escritórios, 256 tanques, 207 silos, 122 chaminés e 90 subestações.
- Pátios, estacionamento de caminhões e ramal ferroviário da logística.
- Ocupação de 27,7%.

### 2.5 Rede viária
- Arteriais com curvas de raio de 160 m e coletoras de 90 m.
- 2 rotatórias: Central (R01/R03/R06) e Tecnológica (R04/R05/R08).
- **R09 Avenida dos Ferroviários**: liga Cidade Antiga, Expansão e Expansão Leste, e resolve o bloqueio do W1.
- **R10 Avenida Leste**.
- Seção completa: pistas, canteiro gramado, calçadas, faixas tracejadas, pontes sobre o canal.
- 482 km de vias locais, 65 km industriais, 12,6 km de ruas principais, 1,9 km de becos.
- 40 acessos a lotes da campanha e de vida.

### 2.6 Skyline (pavimentos, mediana e máximo)
| Zona | Alvo | Mediana | Máx. |
|---|---|---:|---:|
| Cidade Antiga | 2–6 | 2 | 6 |
| Expansão | 4–16 | 5 | 17* |
| Central | médio institucional | 4 | 12 |
| Empresarial | 12–35 | 16 | 35 |
| Tecnológico | 8–28 | 9 | 29* |
| Industrial | baixo + estruturas técnicas | 1 | 1 (+ chaminés e silos) |

\* Inclui o pavimento de pódio, dentro da tolerância de +2 do validador.

### 2.7 Escala (Parte 2)
- 8×8 km, 64 km² reservados, diagonal de 11,3 km.
- Com as velocidades reais do protótipo (`Interaction.cs`: andar 3 m/s, correr 5 m/s), **atravessar a cidade leva 44 min andando e 27 min correndo**; a diagonal correndo leva 38 min.
- Do lar, pela rede viária:
  - Oficina 0,4 km; loja de ferramentas 0,4 km; revenda de usados 0,9 km; Horizonte 1,0 km — tudo em 2–6 min a pé;
  - Escola 2,6 km e condomínio de Helena 3,4 km — 14–19 min a pé ou 5–7 min de carro;
  - Central 5,5 km; hospital 03:17 7,7 km; data center 8,6 km — 31–50 min a pé contra 11–18 min de carro.
- **O veículo passa a fazer sentido a partir do Capítulo II e é indispensável a partir do IV.**
- Reserva de expansão: faixas verdes nas bordas oeste, norte, sul e leste.

### 2.8 Cidade Antiga — base de produção (Partes 3, 3.1, 3.2, 3.3 e 11)
- Ruas, calçadas com meio-fio, esquinas, faixas, travessias de pedestre nos cruzamentos semaforizados, praças, estacionamentos, terrenos vazios, entradas de veículos e ferrovia com dormentes.
- Infraestrutura no núcleo, em instâncias:
  - 2.061 postes (412 com transformador);
  - 1.049 tampas, 2.428 bocas de lobo, 296 hidrantes;
  - 687 armários de telecom, 2.191 caixas elétricas, 5.067 hidrômetros;
  - 353 placas de rua, 167 placas de pare, 28 semáforos;
  - 84 bancos, 224 frades;
  - 2.661 árvores-proxy e 2.061 pontos de iluminação.
- 13.003 edificações instanciadas por Geometry Nodes a partir de 47 variantes, com variação de cor por instância.
- Streaming: 8 camadas (Terrain, Roads, Architecture, Infrastructure, Props, Vegetation, Lighting, Gameplay) × 181 subcélulas `SA_Mxx_yy_Sxx_yy`. Manifesto com cada lote (variante, posição, rotação, subcélula) pronto para a integração na Unity.

### 2.9 Hero locations (Partes 4 a 7)
Os 9 heróis e o lar têm footprint definitivo, entrada, acesso de serviço, estacionamento, relação com a rua, fachada, altura e volumes. Cada pavimento é um objeto separado (corte possível). Marcadores de gameplay para entradas, serviço e vagas.

| Local | Destaques |
|---|---|
| Lar (Ed. Santa Clara, Apto 12) | 4 pavimentos; kitnet de 41,0 m² no 1º andar, com banheiro, armário, cozinha, sala/quarto, mesa, janelas e vagas na frente; slots H0–H4 e spawn |
| Oficina Aurora | galpão de 22×32 m, portão de enrolar de 4,0×4,2 m para utilitário, recepção, escritório, banheiro, depósito, estoque, bancada, 3 vagas, reserva de mezanino; slots G0–G4 e maleta do Guto |
| Horizonte | 12 pavimentos visíveis, lobby, marquise, portões e interfone, medidores, shafts, casa de bombas, cisterna, garagem e subsolo, cobertura técnica com reservatório; pavimento tipo 3 com corredor e quadro (prólogo) |
| Apartamentos | bloco em C, passagem de veículos, pátio de estacionamento |
| Mercearia | vitrine, toldo, beco de carga, câmara fria |
| Restaurante | frente com vagas, travessa de serviço, cozinha, despensa e lavagem |
| Oficina local | dente-de-serra, 2 boxes, pátio |
| Pequeno escritório | 3 pavimentos, estacionamento nos fundos |
| Teatro Imperial | foyer, pórtico de 8 colunas com frontão, auditório, caixa cênica de 33 m, doca nos fundos, condensadores, Largo do Imperial |

### 2.10 Kit e materiais (Partes 8 e 9)
- 40 peças modulares com bevel real:
  - paredes de 1, 2 e 3 m, com janela, porta, vitrine, porta de enrolar e varanda;
  - quinas, portas, janelas, molduras e cornijas, telhados, beirais;
  - grades, portões, calhas, escadas, rampa, muros, calçada, meio-fio e sarjeta.
- 15 peças de infraestrutura.
- 37 materiais PBR procedurais: concreto, reboco, tijolo, asfalto, metais, aço pintado, ferrugem, madeira, vidro, cerâmica, plástico, borracha, telhas e outros.
- Cada material tem variação de cor, rugosidade, bump, sujeira por AO, sujeira de rodapé e slots nomeados Base Color/Normal/Roughness/Metallic/AO, sem imagem (portanto sem missing data).
- UVs métricos em toda a geometria.

---

## 3. Validações (Parte 12)

| Verificação | Resultado |
|---|---|
| `validate_masterplan.py` | PASS, 0 erros, 0 avisos |
| Geração Blender (3 arquivos) | sem exceção |
| Reabertura em processo novo | 3/3 PASS, 0 dados faltando |
| Escala | métrica 1:1; mundo 8×8 km |
| IDs | 24/24 campanha, 20/20 vida; nenhum ID alterado |
| Footprints | dimensões dos lotes de campanha conferidas no `.blend` |
| Acessos | todos os 44 locais ≤90 m (parques ≤130 m) |
| Vias | nenhuma via, ferrovia ou canal invade lote; nenhum lote sobreposto |
| Células | 64 células, 64 terrenos; 181 subcélulas na Cidade Antiga |
| Instanciadores | todos com biblioteca não vazia |
| Estados | H0–H4 e G0–G4 presentes |

---

## 4. O que está aprovado como base, o que ainda é blockout e o que precisa de arte final

**Base estrutural pronta para receber arte:**
- traçado da Cidade Antiga;
- footprints, entradas, serviço e estacionamento dos heróis;
- organização de streaming;
- famílias e kit com dimensões reais;
- slots de estado;
- biblioteca de materiais estruturada.

**Ainda blockout ou provisório:**
- masterplan fora da Cidade Antiga (caixas de massing);
- famílias de fundo em LOD1, sem bevel;
- árvores-proxy;
- infraestrutura provisória em escala correta;
- proxies de mobiliário H0/G0;
- interiores apenas onde validam espaço;
- iluminação de revisão com sol e céu.

**Precisa de arte final (W3/W4):**
- texturas PBR autorais;
- decals (infiltração, ferrugem, óleo, marcas, sinalização);
- clutter funcional;
- LOD0 final dos heróis com detalhamento de fachada;
- vegetação autoral com LOD;
- mobiliário dos estados H/G;
- iluminação interior;
- exportação FBX por subcélula e integração na Unity.

---

## 5. Limitações conhecidas

- O núcleo da Cidade Antiga tem lotes com fachada detalhada, mas os fundos e as laterais das famílias são simples. A repetição das 47 variantes ainda é perceptível de perto.
- As árvores são proxies de esferas. Não representam a vegetação final.
- Algumas esquinas de calçada são chanfradas em vez de curvas, e há pequenas sobreposições em junções em ângulo agudo.
- O tom das capturas (Standard, exposição −1,4) é de revisão, não de look final.
- O Horizonte foi capturado da rua com um vizinho na frente. A fachada de entrada aparece nas plantas e nos marcadores, mas não nessa captura.
- O masterplan fora da Cidade Antiga é massing. Os demais distritos repetem o pipeline da Cidade Antiga quando chegarem a W6+.
- A escala de tempo do jogo não foi definida; os minutos são equivalentes reais.

---

## 6. Próximos passos

1. Revisão visual do usuário nas capturas W1.5.
2. **W2/W3**: texturas PBR autorais nos slots, decals, kit LOD0 detalhado e substituição das famílias LOD1 no núcleo.
3. Mobiliário e clutter dos estados H0–H4 e G0–G4. Interiores do Horizonte para o prólogo.
4. Exportação FBX por subcélula + importação na Unity com `AssetPostprocessor`, mantendo IDs e manifesto. Primeira cena aditiva da Cidade Antiga.
5. Só depois: vertical slice (W5) e demais distritos.

**Regras mantidas:** low-poly só como blockout temporário. VEIN é referência de qualidade visual (escala, realismo, densidade, materialidade, iluminação, atmosfera, clutter); nenhum asset, mapa, prédio, textura, personagem ou layout é copiado.
