# Copacabana REAL — fundação geográfica isolada

**Status:** pipeline GIS na branch `codex/copacabana-osm-real-20261008`. **Não** foi integrado à Unity / atual Simulador de Resort. O repositório principal ainda contém o projeto anterior Facility Ops; não copiar por cima do Resort recente.

## O que é real e o que ainda não é

- Fonte geográfica: OpenStreetMap (OSM) ao vivo, sem prédios inventados. As ruas e os edifícios são extraídos das geometrias e etiquetas OSM existentes no momento da consulta.
- Área de jogo: **2.000 x 1.000 m = 2 km²**, polígono rotacionado junto à orla da Copacabana, em **UTM 23S EPSG:32723**, origens locais em metros. O download é de um BBOX envolvente maior; os GeoJSON e o OBJ próprios são recortados na área exata.
- Prédios OBJ: footprints reais, alturas OSM se disponíveis; sem altura publicada, um volume de visualização de 18 m **estimado**, não a altura verdadeira. Materiais são marcadores neutros; fachadas, telhados, marquises, quiosques e vegetação ainda não são detalhados.
- O terreno do OBJ é plano. Relevo, montanhas e praia detalhada precisam de DEM e arte específicos. Não interpretar OSM2World como fotorealismo.
- Relações multipolígono de áreas complexas: ainda não reconstituídas pelo nosso conversor leve; OSM2World pode fornecer geometria adicional da fonte OSM bruta. Registrar essa limitação no QA.

## Primeira execução sem PC (GitHub Actions)

O workflow `.github/workflows/copacabana_real.yml` roda no push desta branch e também pode ser disparado manualmente em Actions (dependendo das permissões e configuração da conta). Ele:
1. consulta Overpass para geometrias OSM;
2. gera **GeoJSON em WGS84** e OBJ em metros locais, mais um arquivo compactado `copacabana.osm.gz`;
3. executa testes estáticos;
4. publica todos os resultados como artifact do GitHub Actions;
5. tenta versionar os arquivos geográficos derivados **apenas nesta branch**.

Se Overpass estiver indisponível, a execução falha explicitamente; **não** substitui dados reais por cidade fictícia. As ações executam na nuvem do GitHub, não no PC do usuário.

## Execução em Windows, Mac ou Linux

Instale Python 3.11+; na pasta raiz do repositório:

```bash
python -m pip install -r Tools/Copacabana/requirements.txt
python Tools/Copacabana/pipeline.py --download
python Tools/Copacabana/pipeline.py
python -m unittest discover -s Tools/Copacabana/tests -v
```

Saídas locais em `Tools/Copacabana/data/`: `copacabana.osm` (OSM original, para BlenderGIS/OSM2World), `copacabana.osm.gz`, `buildings.geojson`, `roads.geojson`, `coast_and_land.geojson`, `copacabana_base.obj`, `copacabana_base.mtl`, `roi.geojson` e `report.json`.

## BlenderGIS — dados originais e relevo

1. Instalar plugin oficial <https://github.com/domlysz/BlenderGIS> pela documentação compatível com a versão instalada do Blender.
2. No Blender, importar `data/copacabana.osm` por **GIS → Import → OpenStreetMap**; se importar o OBJ em vez do OSM, manter transformação **métrica** sem escalonar e organizar em coleções.
3. Para georreferenciar e obter elevação, usar BlenderGIS, selecionar **UTM 23S EPSG:32723** e um DEM de proveniência identificável. DEM, basemaps e serviços podem exigir chave/API e têm licenças distintas; não usar imagens de mapa/Google como textura sem autorização.
4. Os arquivos GeoJSON são WGS84 (`lon,lat`) para GIS. O OBJ usa eixo `X` paralelo à orla, `Y` para interior e `Z` para cima, com origem na área piloto. **Não alinhar manualmente outro modelo sem registrar a transformação.**

## OSM2World — modelo 3D adicional

Instalar Java 17+ e a versão oficial <https://osm2world.org/download/> (0.4.0 ou superior). Exemplo da interface CLI documentada:

```bash
osm2world -i Tools/Copacabana/data/copacabana.osm -o Tools/Copacabana/data/osm2world_copacabana.glb
```

Em Windows a instalação pode ter `osm2world.bat`; usar o nome do executável presente no pacote. Conferir `--help` na versão instalada, pois os parâmetros podem mudar. **Importante:** esse GLB cobre o bbox baixado, que é maior que 2 km²; recortar depois no Blender conforme `roi.geojson`. Não duplicar edifícios entre OBJ e GLB: escolher um deles como representação predominante.

## Para a Unity / colaboração

- Integrar primeiro **apenas** em uma cópia ou branch da versão Resort mais recente, após backup e identificação dos assets existentes.
- Pôr o OSM real como geometria/traçado de referência; não substituir o resort, piscinas nem hotéis já aprovados.
- Separar bloco geográfico de estética: malhas de vias, lotes, edificações; lotes vazios reais requerem praças/vegetação planejadas, sem inventar que Copacabana possui grandes vazios.
- Usar 300x300 m como vertical slice de acabamento. Depois aplicar fachada modular PBR, LODs e streaming aos 2 km².
- Não prometer FPS, parsing Unity, importação Blender ou renders antes de executar esses ambientes.

## Direitos e origem

© OpenStreetMap contributors, dados licenciados ODbL 1.0: <https://www.openstreetmap.org/copyright>. Manter atribuição em mapa, jogo e documentos, e analisar obrigações relativas a bases derivadas. A licença OSM **não** autoriza copiar fotografias, texturas ou modelos proprietários. BlenderGIS e OSM2World são ferramentas separadas, obtidas de seus repositórios oficiais; nenhum binário de terceiro é incluído aqui.
