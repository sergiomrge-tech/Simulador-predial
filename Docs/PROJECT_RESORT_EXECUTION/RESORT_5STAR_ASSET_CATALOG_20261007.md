# PROJECT RESORT — BIBLIOTECA CINCO ESTRELAS E AUDITORIA DE LACUNAS (07/10/2026)

**Escopo oficial:** o protagonista começa com um pequeno quiosque na orla brasileira contemporânea, evolui para um beach club, hotel e finalmente um resort cinco estrelas com piscinas, piscina com rio/lazy river, hospedagem e serviços integrados. **Visual obrigatório: realista premium, coeso e consistente, sem modelos estilizados/low-poly como arte final.** Unity 6000.6.2f1 / URP PBR. O mapa terrestre-alvo terá 2 km²; versão 2.000 × 1.000 m está em staging com QA 13/13, ainda NÃO foi aplicada ao jogo principal.

## Estado auditado — distinguir biblioteca, importação, substituição e aprovação

### DOWNLOAD CONFIRMADO NA UNIDADE D:
- vrbn Studios Free Buildings URP Bundle 001, `5.547.073.514 bytes`, licença Unity Asset Store. `D:\ProjectResort_AssetLibrary\UnityFree\AssetStoreCache\...` (diretório `vrbn studios\3D ModelsEnvironmentsUrban`).
- Furniture Mega Pack – Free, `1.807.679.361 bytes`, 511 prefabs URP / bedrooms, bathrooms, kitchens, sofas, chairs and tables. Licença Unity Asset Store. Curadoria de 11 modelos+dependências concluída em `D:\ProjectResort_AssetLibrary\Staging\FurnitureCoherentCandidates_20261007` (54 arquivos/113 MB); **ainda não integrado nem visualmente aprovado**.
- A.U.R.W. URP Free, `70.034.090 bytes`, shader de água com refração/espuma/profundidade, Unity Asset Store EULA. `D:\ProjectResort_AssetLibrary\UnityFree\AssetStoreCache\Asset Store-5.x\The Phantom Studios\Shaders\AURW URP Free.unitypackage`. Gzip/TAR integral lido e verificado, 326 membros. **Ainda não importado; testar separadamente da água existente antes de usar.**
- Poly Haven CC0 (sem login), coleção inicial de mais de 100 modelos e materiais catalogados em `D:\ProjectResort_AssetLibrary\PolyHaven_CC0`, com fontes e licenças.
- **Novos pacotes especializados cinco estrelas:** 14 materiais PBR 2K + 7 modelos 3D 1K FBX, num total de **21 novos recursos / 91 arquivos / 381,7 MB**, verificados. Materiais em `D:\ProjectResort_AssetLibrary\PolyHaven_CC0\Resort5StarPBRMaterials2K`; modelos em `D:\ProjectResort_AssetLibrary\PolyHaven_CC0\FiveStarResortAmenities_20261007`. Auditoria: `D:\ProjectResort_Autonomy\RESORT_5STAR_DOWNLOAD_QA_20261007.json`, PASS, 0 erros.
- Materiais adicionais: tiled_floor_001, long_white_tiles, interior_tiles, square_tiles_03, patio_tiles, marble_tiles, granite_tile_04, white_stucco_02, rectangular_facade_tiles, stone_tiles_02, brushed_concrete_2, coast_sand_02, coast_sand_03 e leafy_grass; 4 mapas PBR por recurso (difusa/normal DX/rugosidade/AO), checksums verificados.
- Novos modelos: lifebuoy (boia de salvamento), ocean_buoy (boia marítima), television_02 (suítes), wicker_basket_01/02 (decoração), planter_box_01 (jardins), street_lamp_02 (iluminação). Verificar aparência antes de usar.
- Mobile Palm Pack (URP) consta adquirido gratuitamente na conta, mas não confirmado como arquivo baixado. O anúncio descreve ~100–170 triângulos por árvore — **não aprovar como palmeira de destaque do resort** devido ao requisito de realismo. Coconut Palm Tree Pack é candidato Unity gratuito, mas não confirmado como arquivo baixado.

### IMPORTAÇÃO/EXECUÇÃO REAL CONFIRMADA
- Codex integrou o SUBSET vrbn de 4 prefabs (B00004, B00274, B00275 e B00276), **39/234 lotes no mapa antigo**, escala uniforme, colliders originais preservados, screenshots REAIS sob luz diurna. Regressão PlayMode Unity isolada: 31/31 testes aprovados (XML em `D:\ProjectResort_Autonomy\CodexVRBNIntegration\Evidence\full_playmode_final.xml`). A integração do projeto não equivale a uma aprovação artística completa do mundo; **195 lotes ainda têm o kit anterior**.
- A arquitetura realista dos prédios se aproxima do padrão, mas o paisagismo nas capturas diurnas ainda apresenta muitas faixas de verde plano, vegetação esparsa e materiais que precisam do mesmo refinamento PBR.

## Matriz de produção e cobertura de recursos

| Área de jogo | Recursos já disponíveis (apenas candidato quando não validado) | Falta de verdade para versão cinco estrelas | Ação prioritária |
| --- | --- | --- | --- |
| **Orla, praia e calçadão** | areia costeira CC0, rochas, píer, iluminação urbana, modelos vegetais, texturas de calçamento | espreguiçadeiras PBR, guarda-sóis coerentes, duchas de praia, salva-vidas/guarita, lixeiras, placas e acesso de pedestres contínuo | Selecionar somente PBR tropical contemporâneo; construir acessos e detalhes do lugar sem clones aleatórios. |
| **Quiosque → bar de praia → beach club** | caixa registradora, garrafas, copos/utensílios CC0, 511 móveis candidatos, modelos de cozinha; estruturas do quiosque existentes | balcão/bar molhado realista, cardápios e expositores, máquina de gelo, refrigeradores comerciais, mesas de praia e atendentes com interação | Refinar o quiosque principal ANTES dos hotéis; preservar sua progressão e pontos jogáveis. |
| **Pousada → hotel → resort cinco estrelas** | subset vrbn, esquadrias/pisos PBR, cama/armário/banheiro/cozinha URP, TVs candidatas | edifício de recepção, lobby com concierge, suítes premium completas, elevadores/interiores, varandas, corredores, sinalização e fachada de hotel alto padrão | Construir módulos autorais que combinem com a arquitetura selecionada; grandes VRBN só onde cabem sem distorção. |
| **Piscina principal / borda infinita** | shader A.U.R.W. URP, azulejos, antiderrapantes, pedra clara, mármore, concreto, salva-vidas | piscina 3D sob medida, borda infinita/overflow, escadas, ralos, skimmers, deck, móveis e caustics/espuma adequados | Criar geometria de piscina com fundo e colisão; testar shader na cópia Unity, sem trocar o mar atual diretamente. |
| **Piscina com rio / lazy river** | A.U.R.W., pisos/materiais, rochas e areia CC0, salva-vidas/boias | canal curvo 3D, conexão hidráulica, correnteza, profundidade, trechos de segurança, boias para hóspedes, acesso, pontes, plataformas e paisagismo coerente | Implementação autoral em **spline + malha com leito e paredes + fluxo visível**; sem promessa de pack pronto gratuito com todas as mecânicas. |
| **Spa, wellness, sauna e hidromassagem** | banheiras, vasos, pedra, mármore, roupas/texturas, luminárias | jacuzzis funcionais, sauna seca/vapor, macas, toalhas, mobiliário de massagem, equipamentos e VFX de vapor | Procurar somente modelos sob licença compatível, padronizar materiais e montagem. |
| **Restaurantes, buffets e bares** | móveis/mesas, fogões/fornos/geladeiras e utensílios, garrafas, texturas PBR | cozinha industrial, buffet quente/frio, máquinas de café, balcões refrigerados, buffet com pratos e decoração integrada | Compor modularmente; evitar packs cartoon e materiais destoantes. |
| **Academia, recreação e crianças** | poucos modelos genéricos, materiais de piso seguros | esteiras/bicicletas, halteres, piscina infantil/splash pad, jogos e equipamentos seguros | Lacuna importante. Buscar assets específicos ou modelar os conjuntos principais. |
| **Jardins, caminhos, fachadas e iluminação** | vegetação Poly Haven, plantas tropicais, calçamento, iluminação urbana e jardins CC0 | palmeiras de qualidade para primeiro plano, arbustos e canteiros integrados ao terreno, variação controlada, postes/luminárias do mesmo kit | Gate visual lado a lado sob mesma iluminação; não espalhar árvores aleatoriamente. |
| **Serviços operacionais 5 estrelas** | algumas caixas/equipamentos genéricos | housekeeping, carrinhos, lavanderia, bombas/filtros, climatização, segurança, lixeiras, geradores e bastidores | Objetos e gameplay específicos; importante em simulador, não apenas cenografia. |
| **Personagens e animações** | existe base de humanos realistas e atividades prévias do projeto | hóspedes na piscina, salva-vidas, garçons, camareiros, recepção, manutenção e animações de água | Validar rig, escala, roupa e animações realistas; não usar bonecos imóveis. |
| **Som e ambientação** | ciclo diurno/noturno e alguns VFX existentes | água correndo no rio, ondas, respingos, passarinhos, música lounge, equipamentos de piscina | Obter sons gratuitos sob licenças apropriadas e editar volumes/loop. |

## Fontes gratuitas verificadas e status

1. **Unity Asset Store:** https://assetstore.unity.com/packages/vfx/shaders/a-u-r-w-urp-free-195139 — A.U.R.W. URP Free, já em cache D, versão 4.1, licença padrão Unity.
2. **Unity Asset Store:** https://assetstore.unity.com/packages/3d/props/furniture/furniture-mega-pack-free-330002 — mobiliário URP gratuito, já baixado; curadoria estrita.
3. **Unity Asset Store:** https://assetstore.unity.com/packages/3d/environments/urban/vrbn-studios-free-buildings-urp-bundle-001-264015 — prédios URP gratuitos, já baixados, subset parcialmente integrado.
4. **Poly Haven:** https://polyhaven.com — modelos e materiais realistas CC0 já baixados com manifesto e QA.
5. **ambientCG:** https://ambientcg.com — alternativa para **materiais PBR CC0** quando houver lacunas; não foram baixados novos pacotes desta fonte nesta etapa, nem assumir que itens de terceiros seguem CC0.
6. **Sketchfab:** https://sketchfab.com/3d-models/swimming-pool-f69f7b35f6134688befdbbe495756f81 — CN Entertainment, piscina retangular realista, CC BY; **não baixado**, requer login Sketchfab.
7. **Sketchfab:** https://sketchfab.com/3d-models/sun-lounger-1427d638427a4055b0dcc2fd53c7a26b — Yarosha, espreguiçadeira mais detalhada, CC BY; **não baixado**, requer login Sketchfab.
8. **Sketchfab:** https://sketchfab.com/3d-models/piscina-aquecida-com-bar-molhado-3a0353788da64b839db1e187dcbaac0b — João Marcello Morais, piscina com bar molhado, CC BY; **não baixado**, avaliar escala e qualidade antes de usar.
9. **Licenças:** cada objeto CC BY requer **atribuição ao autor + link + licença no registro de créditos**. Não importar modelos CC BY-NC, CC BY-NC-SA ou de uso não comercial para a versão comercial. Não burlar login/downloader do site.
10. **Outros candidatos:** WaterWorks (Unity) é antigo e deve ficar em `HOLD` até checagem Unity 6 URP; Mobile Palm Pack com 100–170 triângulos fica em `HOLD` para primeiro plano.

## Gates de aprovação para os agentes

- **MATERIAIS:** URP Lit realista, texel density consistente, normal DX, roughness para smoothness corretamente convertido, materiais físicos para vidro, piso e água, e iluminação unificada.
- **GEOMETRIA:** 1 Unity unit = 1 m; sem deformação de hotel para caber em lote; pivôs, acessos, colisões, canalizações e rotas de funcionário/hóspedes.
- **VISUAL:** comparar no MESMO print real do Unity os edifícios, calçada, jardins, mobiliário de piscina, mar e água da piscina; rejeitar contraste entre fotogrametria e low-poly/plano. Não considerar compras grátis/downloads como integração.
- **PERFORMANCE:** LODs, culling, instancing, iluminação e água com URP, evitando lag em mapa de 2 km² com centenas de edificações. Testar FPS e VRAM reais.
- **SEGURANÇA:** nenhum asset da Unity deve ser importado inteiro no projeto sem subset/backup. Alterações estruturais de piscina/rios apenas em cena ou projeto isolado até passar no QA.
- **STATUS:** o material para construir a base do resort já é significativo. **NÃO É CORRETO dizer que TODOS OS ASSETS necessários estão baixados**; faltam itens de áreas aquáticas, equipamentos especializados, modelos hoteleiros e animações. Para chegar ao padrão de luxo sem pagar, será necessário modelar alguns conjuntos do resort de forma original reaproveitando texturas/móveis/água PBR gratuitos.

## Prioridade de implementação após gate dos edifícios

**Fase A — núcleo do jogo:** orla + quiosque premium + calçadão e praia + acessos com materiais finais. **Fase B — evolução:** pousada, hotel, quartos premium, lobby e serviços. **Fase C — luxo 5 estrelas:** piscina com borda infinita, rio lento, bar molhado, spa, jardins densos, restaurante, academia e lazer infantil. **Fase D — operação:** pessoas, animações, manutenção, filtros/fluxo de água, staff, desempenho, validação e progressão no jogo.

**Arquivos de auditoria:** `D:\ProjectResort_Autonomy\RESORT_5STAR_DOWNLOAD_QA_20261007.json`, `D:\ProjectResort_Autonomy\RESORT_VISUAL_CURATION_20261007.json` e `D:\sergi\Documents\Simulador-predial\Docs\PROJECT_RESORT_EXECUTION\RESORT_VISUAL_COHESION_GATE_20261007.md`.

**Situação desta etapa:** downloads complementares terminados e verificados; 39 edifícios integrados tecnicamente; água e móveis não importados ainda; piscina principal e rio lento não foram construídos; 2 km² de mapa estão em staging. A versão de produção NÃO está visualmente finalizada.
