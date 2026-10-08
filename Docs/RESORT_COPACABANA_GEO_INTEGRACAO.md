# Handoff futuro — integrar Copacabana OSM real ao Resort Unity

Data: 2026-10-08. **Esta branch contém fonte geográfica e modelos-base**, NÃO a versão atual do Resort. Não mesclar na main do antigo Facility Ops sem inspeção da pasta atual no PC.

## Evidências concluídas na nuvem

- Execução GitHub Actions GIS real: https://github.com/sergiomrge-tech/Simulador-predial/actions/runs/37846206946
- Dados fonte OSM (ODbL): `Tools/Copacabana/data/copacabana.osm.gz`.
- 1.468 footprints de edifícios, 468 vias, 563 árvores, 124 áreas, 1 linha de costa e 3 trechos aquáticos no recorte.
- As vias incluem Avenida Atlântica, Nossa Senhora de Copacabana, Barata Ribeiro e Tonelero. IDs OSM preservados nos GeoJSON.
- Alturas: **14 declaradas OSM, 56 estimadas de número de pavimentos, 1.398 alturas genéricas**. Nunca atribuir alturas estimadas como reais.
- Recorte exato: 2000 × 1000 metros, polígono rotacionado UTM23S, orientação +46° a partir do Leste e centro deslocado 300 m para interior a partir do ponto de referência da Avenida Atlântica.
- OSM2World 0.4.0 GLB: execução https://github.com/sergiomrge-tech/Simulador-predial/actions/runs/37846402065 (arquivo artifact comprimido, não no Git).
- Planta baseada em footprints OSM: `Tools/Copacabana/data/mapa_real_copacabana.svg`.

## Operação no PC reconectado

1. **Não importar em cima da cena original.** Localizar o projeto ativo Resort Unity no PC, conferir versão real e fazer um backup datado da cena e dos dados. O GitHub atual é linhagem antiga (Facility Ops/Santa Aurora).
2. Baixar/atualizar somente esta branch num diretório separado. Guardar `report.json` e a licença ODbL.
3. Abrir em Blender ou testar GLB do OSM2World **em cena temporária**. O GLB do OSM2World cobre o BBOX do download, **maior** que 2 km². O OBJ próprio já está recortado pelo ROI.
4. Normalizar e documentar sistemas de eixos: dados próprios OBJ **Z-up**, **X longitudinal à praia**, **Y para interior**. Unity é Y-up. Não somar GLB e OBJ dos mesmos edifícios na cena final.
5. O BlenderGIS pode importar `copacabana.osm` obtido ao extrair o `.osm.gz`, trabalhando com georreferenciamento UTM23S. Relevo exige DEM verdadeiro; o arquivo OBJ atual tem solo plano.
6. Inserir somente o sistema de vias/quadras e volumetria de edifícios como **referência desligável**; preservar prédios/resort/hotéis/piscinas existentes até comparação visual.
7. Identificar trecho piloto de 300 × 300 m da Avenida Atlântica: calçadão com padrão de ondas original, quiosques, avenida, calçadas, edifícios PBR, paisagismo e acesso ao resort. Checar distâncias reais e conectividade.
8. Substituir volumetrias por fachadas variadas moduladas em múltiplos PBR, não repetir prédios como blocos genéricos. Caso OSM não inclua edifício real, preencher com modelo aprovado e deixar marcado como inferido.
9. **Validação no Unity:** importação real, screenshot real, verificação de colisão, culling, occlusion, LOD, tempos de carregamento e FPS em máquina-alvo; sem declarar desempenho aprovado sem testes.
10. Após aprovação do piloto, ampliar para todo recorte com streaming urbano e distintas camadas de detalhe por distância.

## Responsabilidades sugeridas para até três agentes Luna Alto

- R1 (geografia/QA): importar OSM2World/OBJ, validar escalar/CRS, traçado, lotes e ruas; somente cenário de teste.
- R2 (arquitetura): mapear footprints e alturas OSM, biblioteca de fachadas premium não repetitivas, evitar colidência/lotes vazios não justificados.
- R3 (arte/integração): resort, calçadão, paisagismo, iluminação e métricas de desempenho; não editar arquivos em que R1/R2 estejam trabalhando.

Nenhuma parte deste documento autoriza publicar jogo, sobrescrever projeto ou apresentar captura simulada como render real. Dados © OpenStreetMap contributors, ODbL: https://www.openstreetmap.org/copyright
