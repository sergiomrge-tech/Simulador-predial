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
