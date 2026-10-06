# Evolução física do resort — modelagem das 7 etapas

Data: 2026-10-06. Um único blend (`ArtSource/Blender/Resort/SantaAurora_Estagios_v1.blend`) mostra a mesma terra evoluindo da barraca ao Grand Aurora.
Cada objeto carrega `st_from`/`st_to`; o laço de render liga só o que existe em cada etapa.

Regenerar: `blender --background --factory-startup --python Tools/Blender/create_stages.py -- --root . --render` (precisa do `SantaAurora_GrandAurora_v1.blend`).
Capturas: `ArtSource/Blender/Resort/Estagios/` (`estagioN_{A_orla,B_aerea,C_plato,D_barraca}.jpg` e as folhas `evolucao_A_orla.jpg`, `evolucao_B_aerea.jpg`).

| Etapa | O que aparece | Onde |
|---|---|---|
| 1 Barraca | barraca de madeira com toldo listrado, chapa, freezer; guarda-sóis; palmeiras do calçadão | P0 |
| 2 Quiosque | quiosque de alvenaria com palapa grande, deck, mesas, luzes de varal, sanitários | P1 |
| 3 Restaurante + pousada | restaurante coberto ao lado; **sobrado colonial** do Seu Tonico (venezianas azuis, sacada de madeira, telhado de terracota) | P1, P2 |
| 4 Hotel | bloco de 5 pavimentos com loggia e varandas, saguão, piscina com espreguiçadeiras | P3 |
| 5 Complexo | salão de eventos, spa, seis bangalôs na praia | P3 e orla |
| 6 Resort em obras | platô terraplenado, terraços 1–2 construídos, **grua**, estruturas de concreto das próximas alas, **Grande Hotel restaurado** | P5, P4 |
| 7 Grand Aurora | o resort completo; farol aceso | P5, P6 |

Presente em todas as etapas: o **Grande Hotel Palmeiras** (em ruína até a 5: janelas tapadas, colunas quebradas, trepadeiras, telhado caído, torre desabada)
e o **farol** de 38 m (apagado até a 6). O terreno é o "natural" nas etapas 1–5 e o terraceado nas 6–7 (`ResortSiteHeights_natural.bytes` / `ResortSiteHeights.bytes`).

## Limites
- Todas as peças ainda são volumes com detalhe arquitetônico, sem textura autoral. Os interiores só existem no saguão e na suíte.
- O Grande Hotel restaurado tem fachada, pórtico, mansarda e torre do relógio, mas não tem interior.
- A grua e as estruturas da etapa 6 são ilustrativas.
- Nada foi exportado para a Unity como malha ainda.

## Integração na Unity (2026-10-06)

- `Tools/Blender/export_resort_kit.py` exporta cada peça de etapa como FBX em `FacilityOps/Assets/_Game/Resources/Art/Resort/` (38 peças, ~220 mil polígonos) e escreve `resort_stages.json` (peça, etapa inicial e final). As cores dos materiais são gravadas como valores simples (os nós procedurais não sobrevivem ao FBX).
- `ResortStages` (Unity) instancia as peças na origem. A conversão de eixos do FBX as gira 180° em Y, então a raiz compensa com uma rotação de 180°; o teste `StagesTests` confere o alinhamento (Grande Hotel, torre) contra o terreno.
- A etapa vem das terras compradas: P1 → 2, P2 → 3, P3 → 4, P4 → 5, P5 → 6, P6 → 7. O terreno troca de "natural" para "terraceado" na etapa 6. `RESORT_STAGE=N` força uma etapa (capturas e testes).
- A barraca e o quiosque não são exportados: a barraca é a do jogo (procedural) e o quiosque entra com a jogabilidade dele.
- Pendências: LOD e colisão das peças; materiais PBR de verdade; a etapa 5 ainda não tem gatilho próprio além de comprar P4.
- Aviso de repositório: cada regeneração commita `.blend` de dezenas de MB; convém Git LFS ou não versionar os `.blend` regeneráveis.

## Qualidade na Unity (2026-10-06)

- **Materiais**: `export_resort_kit.py` escreve `resort_materials.json` e copia para `Resources/Art/Resort/Textures/` as texturas PBR autorais (cor base + normal) dos conjuntos reaproveitados: `ladrilho` (travertino e mármore), `reboco` (estuque), `madeira` (teca, brise, madeira escura, tronco), `telha` (terracota), `pastilha` (azulejo), `granito` (basalto) e `concreto`. `ResortMaterials` monta os materiais URP Lit em execução, com tiling em metros; vidro, água e luz têm valores próprios.
- Peças do platô vinham com materiais duplicados (`travertino.001`); o exportador e o Unity agora normalizam o nome.
- **Colisão**: prédios e terraços ganham `MeshCollider`; vegetação, água e grua não.
- **Luz**: ambiente em três cores (céu, horizonte, chão) para as fachadas na sombra manterem forma e cor.
- Cascatas verticais de água agora têm as duas faces (a engine usa face única).
- Teste de PlayMode confere materiais texturizados e colisão. Capturas: `ArtSource/Blender/World/Reviews/R4/`.
- Os `.blend` do resort (`ArtSource/Blender/Resort/*.blend`) deixaram de ser versionados (regeneráveis por script, 25–50 MB cada).
- Pendente: LOD, janelas modeladas e mais texturas próprias (vidro, tecido, água), interiores do Grande Hotel.
