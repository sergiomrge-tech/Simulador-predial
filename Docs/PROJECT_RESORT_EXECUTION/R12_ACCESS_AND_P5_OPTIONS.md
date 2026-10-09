# Copacabana: acessos pedonais e alternativas para o lote P5

**Checkpoint 09/10/2026 — análise geográfica, sem alterar o jogo.**
Fonte: OSM congelado da R13 (commit 5217a65751a334f8ea3934ae1e7f0c75f7594a9c); mapa de 2.000m na orla × 1.000m para dentro; CRS EPSG:32723, rotação 46 graus. Código versionado em Tools/Bridge/audit_r12_access_and_p5_options.py, QA em Docs/PROJECT_RESORT_EXECUTION/R12_ACCESS_AND_P5_OPTIONS.json.

## O que foi medido
Foram encontrados 1.936 segmentos de vias rotuladas no OSM com uso pedestre (footway, path, pedestrian, steps, living_street). Para cada terreno P0–P7 com localização candidata do relatório anterior, o algoritmo mede distância EUCLIDIANA mínima às linhas OSM, separando caminhos indicados para pedestres de eixos de ruas comuns. **Não é um trajeto caminhável** e não prova calçada, direito de acesso, entrada em prédio, colisões, alturas ou navmesh Unity. O player spawn e a barraca ainda não estão mapeados para locais aprovados.

| Terreno | Distância à via pedonal rotulada | Distância ao eixo de rua OSM | Situação |
|---|---:|---:|---|
| P0, barraca | 10,7 m | 33,9 m | localização apenas candidata |
| P1, quiosque | 32,2 m | 75,7 m | localização apenas candidata |
| P2, sobrado | 148,1 m | 54,9 m | alerta de acesso |
| P3, quarteirão | 79,7 m | 118,8 m | alerta de acesso |
| P4, hotel | 214,5 m | 98,9 m | alerta de acesso |
| P5, platô | — | — | nenhum lote original encontrado |
| P6, ponta | 74,7 m | 121,6 m | alerta de acesso |
| P7, marina fictícia | 28,5 m | 66,9 m | localização apenas candidata |

Os quatro alertas são reais: mesmo que um retângulo esteja livre de edifícios e vias no plano, pode não oferecer acesso de gameplay. Dados pedonais OSM incompletos também podem subestimar o acesso verdadeiro. Por isso, **nenhum desses pontos é aproveitado automaticamente**.

## Terreno P5 original e alternativas quantitativas
O lote legado P5 é 240×190m = 45.600m² e não encontrou posição livre no grid de 25m, considerando edifícios, vias, buffers costeiros e os outros sete lotes candidatos. Sem mudar a forma narrativa do jogo, a ferramenta testou CINCO tamanhos menores, ainda como alternativas sujeitas a design e aprovação:

| Proposta de novo footprint | Área | Centros geométricos possíveis no grid |
|---|---:|---:|
| 180×125 m | 22.500m² | 85 |
| 150×125 m | 18.750m² | 93 |
| 120×100 m | 12.000m² | 131 |
| 100×80 m | 8.000m² | 199 |
| 80×60 m | 4.800m² | 233 |

Essas contagens não são terrenos reais à venda, nem posições aptas a navmesh. **O P5 de 240×190m permanece intacto nos arquivos do gameplay.** Uma decisão de redesign pode optar por instalar um empreendimento maior fora do recorte de 2×1km ou converter sua função em vários lotes/contratos ao longo da campanha, mas NENHUMA opção foi implementada sem aprovação.

## Segurança comprovada e próximos gates
- O report tem SHA do OSM compactado (bytes intactos), footprints, frame e arquivos de gameplay, com CRLF/LF de JSON normalizados; a CI reconstrói o conteúdo a partir de checkout esparso do snapshot congelado.
- Não foram removidos prédios, alteradas vias, editados saves, modificadas missões nem substituído executável.
- Migração continua explicitamente DESLIGADA; inventário original guarda target=null e R12GameplayWorldGate falha fechado.
- Próxima etapa técnica: mapear efetivamente a porta do protagonista e a barraca para locais e caminhos jogáveis, testar colliders e NavMesh em Unity, obter aprovação de redesign do P5 e só então fazer build separado para avaliação. O aplicativo original não foi trocado.
