# Grand Aurora — modelagem do resort final (v1)

Data: 2026-10-06. Prioridade definida pelo usuário: **primeiro a modelagem do resort, depois mecânicas e sistemas.**
Este documento registra o que existe, como regenerar e o que falta para chegar ao "extremamente grandioso e lindo" do GDD v2.

## Arquivos

| Item | Caminho |
|---|---|
| Gerador da cena | `Tools/Blender/create_grand_aurora.py` |
| Kit arquitetônico de luxo | `Tools/Blender/sa_resort.py` |
| Render de revisão | `Tools/Blender/render_grand_aurora.py` |
| Terreno e parcelas (fonte do Unity e do Blender) | `Tools/Map/export_resort_site.py` → `FacilityOps/Assets/_Game/Resources/Resort/ResortSite.json` + `ResortSiteHeights.bytes` |
| Blend dia / noite | `ArtSource/Blender/Resort/SantaAurora_GrandAurora_v1.blend` e `..._noite.blend` |
| Capturas | `ArtSource/Blender/Resort/Capturas/` e `Capturas_noite/` (8 câmeras cada) |

Regenerar (nesta ordem):

```
python Tools/Map/export_resort_site.py
blender --background --factory-startup --python Tools/Blender/create_grand_aurora.py -- --root . [--night]
blender --background ArtSource/Blender/Resort/SantaAurora_GrandAurora_v1.blend --python Tools/Blender/render_grand_aurora.py -- --root .
```

Atenção: o mesmo terreno alimenta o Unity e o Blender. Mudar alturas ou parcelas no exportador muda os dois.
A névoa volumétrica (`haze`) deixa o EEVEE preto neste ambiente; o gerador a mantém em 0.

## Composição (platô P5, 240 × 189 m, quatro terraços)

Terraços planos de verdade, com degraus de 4,5 m: **T1 6,5 m (clube de praia) → T2 11,0 (spa) → T3 15,5 (lagoa) → T4 20,0 (chegada, saguão e torre)**.
Os terraços têm 39, 42, 39 e 69 m de profundidade; cada degrau cai sobre uma grade de 1,5 m, e o muro fica no meio da célula de degrau.

- **Eixo central** de água e pedra, do hotel ao mar: escadaria monumental dupla com cascata entre os lances, bacias de azulejo e muros de arcada.
- **Grande Saguão** (90 × 24 m, pé-direito de 13 m): colunata de fuste redondo, fachada de vidro com caixilhos de latão, telhado de quatro águas com beiral de 4 m e lanterna, forro de madeira, recepção de mármore, sala de estar, lustre.
- **Torre Aurora**: 18 pavimentos escalonados, pilares de travertino, varandas de teca, **coroa em lanterna de vidro** (eco do farol) acesa à noite.
- **Alas de quartos**: 8 alas de 4 a 7 pavimentos, com arcada no térreo, varandas com guarda-corpo de vidro e corrimão de latão, brise-soleil de teca, pavilhões de canto com telhado de terracota e cobertura jardim.
- **Chegada**: pórtico em colunas sobre o pátio, fonte em camadas e postes de luz.
- **T3**: lagoa de 72 × 28 m com ilha e palapa, pergolado, restaurante e salão de eventos.
- **T2**: spa com piscinas espelhadas, canal axial.
- **T1**: piscina de borda infinita para o mar, espreguiçadeiras, guarda-sóis, palapas, 8 bangalôs com piscina privativa, bar da praia, canteiros formais.
- **Paisagem**: 146 palmeiras-imperiais modeladas à mão (tronco afunilado e anelado, copa de 16 folhas), arbustos, buganvílias, alameda de palmeiras até a avenida.

## Verificado

- Gerador roda sem erro (~8 s); 400 mil polígonos, dos quais ~290 mil são o terreno de 1,5 m.
- 8 câmeras renderizadas de dia e de noite (`Capturas*`). O Unity (teste PlayMode do prólogo) continua passando com o terreno novo.

## Limites honestos desta versão

- **Ainda é massing detalhado, não arte final.** Geometria feita de caixas e prismas com materiais procedurais; sem texturas autorais, sem esquadrias modeladas (janelas são painéis com caixilho), sem mobiliário interior além do saguão.
- A aérea ainda lê "grande conjunto bem organizado" e não "monumental e lindo": faltam variação de volumes (torreões, cúpulas, loggias duplas), jardins em escala de paisagismo, água em movimento, pessoas e sombras de vegetação de verdade.
- O terreno ao redor do platô (talude norte e laterais) é um declive de grama; falta o muro de contenção e o acesso viário final.
- Os prédios da vila ao redor são só caixas (contexto).
- Nada disto foi exportado para a Unity como malha; o Unity ainda mostra só o terreno (com os terraços) e a vila em caixas.

## Próximos passos de modelagem (ordem)

1. Segunda passada de qualidade na aérea: torreões e cúpulas nos pavilhões, loggias, telhados variados, jardins em parterres maiores, bosques de palmeiras em grupos, água animada (normal/espuma).
2. Quarto-modelo: suíte completa (cama, banheiro, varanda) e saguão com mobiliário, para a primeira pessoa de inspeção.
3. Texturas PBR autorais para travertino, estuque, teca e telha (hoje procedurais).
4. Restauro do Grande Hotel Palmeiras (P4) como joia histórica e o farol (P6).
5. Exportação modular para a Unity: kit de peças (ala, saguão, torre, arcada, bangalô, piscina) com LOD, em vez de uma malha única.
6. Evolução por etapas: versões "ruína", "pousada", "hotel" e "complexo" das mesmas parcelas (estados do mesmo registro).
