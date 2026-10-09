# Project Resort — preparação segura das âncoras do gameplay para Copacabana R12/R13

**09/10/2026, frente paralela à arte R13 de Sol 6.1**
**Branch de gameplay:** `codex/r12-gameplay-visual-bridge` do repositório `sergiomrge-tech/Simulador-predial`.

## Resultado implementado
O script `Tools/Bridge/build_r12_anchor_inventory.py` lê o mapa jogável
`FacilityOps/Assets/_Game/Resources/Resort/ResortSite.json`, preserva
seu SHA-256 e exporta dez posições sem modificar o jogo. Copia também para
este repositório o **frame R4 original** de `Resort-Simulator-` (fonte
`Docs/PROJECT_RESORT_EXECUTION/R12_SOURCE_FRAME.json`) e registra seu hash.

| Âncora de gameplay | Posição LOCAL do jogo antigo | OSM real |
|---|---|---|
| HOME_DOOR, porta do Apto 12 | X 330, Z 338,5 | NÃO MAPEADO |
| STALL_PROMENADE, barraca inicial | X 450, Z 255,995, interpolado na polilinha do calçadão | NÃO MAPEADO |
| PARCEL_P0…P7 | centros de oito lotes, armazenados no JSON | NÃO MAPEADO |

Essas coordenadas pertencem somente ao mapa **Bairro das Palmeiras
(900 × 720 m)**, não à cidade de Copacabana. A R12 geográfica
permanecia com **2.000 × 1.000 m**, CRS **EPSG:32723**, orientação 46 graus.
**Nenhuma posição foi convertida por regra de três ou inventada.**
Translação/rotação com escala 1:1 exigirá correspondências geográficas
reais e inspeção de colisões.

### Proteção programática instalada
- `Assets/_Game/Scripts/Resort/Site/R12GameplayWorldGate.cs`:
  valida hash da fonte, dimensões originais, política de movimento
  rígido, IDs, estados aprovados e dez pontos; **sempre devolve false**
  ao pedido de ativar R12 enquanto não houver loader, física, navegação,
  save migration, validação por cena e teste de jogo. Ou seja, não
  há possibilidade de ativação acidental.
- `Assets/_Game/Scripts/Resort/Editor/ResortR12GameplayAnchorAudit.cs`:
  teste real com Editor Unity, valida o inventário importado como
  `TextAsset`, os 8 lotes, a porta e o quiosque, mapa legado,
  SHA-256 da cena jogável, e que o modo Copacabana permanece bloqueado.
- `FacilityOps/Assets/_Game/Resources/Resort/R12GameplayAnchorInventory.json`:
  versionamento dos 10 IDs (target = null, status
  GEOGRAPHIC_PLACEMENT_UNVERIFIED); pode ser consumido no futuro
  como documentação e candidata a tabela de migração, nunca como
  licença para spawn.
- `R12_GAMEPLAY_ANCHORS_QA.json` e
  `R12_GAMEPLAY_ANCHOR_NATIVE_QA.json` registram resultado Python
  e Unity. O Unity tem comportamento particular: JsonUtility pode
  materializar `null` como instância default para campos tipo
  classe serializável. Para não aceitar coordenada `(0,0)` acidental,
  a inspeção verifica explicitamente os flags de status e a existência
  de `target: null` no documento fonte; ativação continua BLOQUEADA.

### Evidência real
- Python local: oito suítes no bridge/âncoras (3 anteriores + 5
  novas) + checagem de determinismo do manifesto — aprovadas;
  teste de QA nativo adicional verifica hash da cena.
- Unity 6000.6.2f1: primeiro erro de compilação corrigido movendo a
  auditoria para o asmdef correto `ResortAurora.Resort.Editor`.
  Segunda tentativa encontrou a questão de `JsonUtility` citada
  acima e foi corrigida. Terceira tentativa **PASSOU** com
  `R12_GAMEPLAY_ANCHORS_NATIVE_PASS anchors=10 target=0
  migration=BLOCKED` e encerramento batch código 0.
- Nenhum script `ResortGame.Start`, `ResortSite.Build`, cena
  `ResortPrologue.unity`, save, executável ou mapa já aprovado foi
  alterado. Este checkpoint ainda **NÃO é integração jogável R12**.

## Próximas etapas objetivas
1. Selecionar por geometria e inspeção real da R12 posições candidatas
   para porta/casa, barraca e P0–P7. Eliminar footprint de prédios,
   vias e água, verificar terrenos navegáveis e circulação. Gerar
   JSON com **candidato** e fonte — não aprovado até QA de colisão.
2. Construir modo ambiental opt-in por célula com **um** solo,
   **um** oceano, **uma** rede de ruas, iluminação e física; não
   instanciar `ResortSite.Build` e R12 inteiros ao mesmo tempo.
3. Adaptar casa, barraca, personagens, missões e oito lotes ao
   mapa do litoral; adaptar minimapa e NPCs.
4. Migração de saves estritamente versionada: conservar saldo,
   progresso, inventário, missões e histórico; somente mover
   personagem quando todas as âncoras necessárias tiverem QA.
5. Capturar gameplay real e medir 1080p/60 FPS como meta, sem declarar
   métricas não medidas; depois criar build R13 separada no D:,
   mantendo executáveis anteriores.

**Gate atual**: integridade e preparação de migração **PASS**,
georreferenciamento de gameplay **PENDENTE**, gameplay no mapa
Copacabana **PENDENTE**, aprovação artística R13 **PENDENTE**.
