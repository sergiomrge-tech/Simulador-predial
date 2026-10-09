# R12 — revisão espacial de terrenos na Unity, sem modificar gameplay

**Checkpoint técnico 09/10/2026.** Repositório `Simulador-predial`, branch independente `codex/r12-gameplay-visual-bridge`. Continuação da auditoria GIS real do mapa Copacabana 2.000×1.000 m, EPSG:32723/46°.

## Artefatos concretos
1. Gerador Python `Tools/Bridge/prepare_r12_unity_review_markers.py` transforma sete retângulos candidatos P0, P1, P2, P3, P4, P6 e P7 do OSM local x/y para o sistema de mundo Unity X/Z, seguindo `WorldX = x*cos(46°) - y*sin(46°)` e `WorldZ = -x*sin(46°) - y*cos(46°)`. Ele valida roundtrip com erro abaixo de 1e-5 m, geometria e área. `P5` continua sem posição, e porta da casa e barraca não foram mapeadas a entradas oficiais. Fonte hash: `Docs/PROJECT_RESORT_EXECUTION/R12_GEO_UNITY_REVIEW_MARKERS.json`.
2. `ResortR12GeoCandidatePreview.Build` — script real do Editor Unity em `Assets/_Game/Scripts/Resort/Editor`. Carrega a cena visual R12 local e gera CÓPIA separada com sete retângulos destacados por 28 trechos/quadros visuais e sete rótulos **UNVERIFIED**; contornos e rótulos marcados `EditorOnly`, sem física/colliders. O script nunca chama gameplay/spawn/save nem muda cena principal.
3. Cena derivada gerada apenas no workspace Windows da validação, não comitada: `Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_GeometricCandidates_Review.unity`. Essa pasta contém os assets gerados de grande porte e permanece excluída do Git para não misturar o projeto do gameplay com FBX provisórios. O arquivo é reprodutível quando o cache de assets/scene do R12 for restaurado da fonte autorizada.

## Resultado de validação Nativa — PASS técnico
Unity 6000.6.2f1 (Editor batch no PC, D3D11), método `ResortAurora.EditorTools.ResortR12GeoCandidatePreview.Build`:
- `R12_GEO_CANDIDATES_UNITY_NATIVE_PASS outlines=28 labels=7 migration=BLOCKED`, encerrou batch normalmente.
- Cena R12 fonte **não foi alterada**; SHA256 original `ed3d5295473aa8353d9f06cd38173b2c2efb87efb326132f346b85d0b27250d5`.
- Gerados 7 contornos de quatro arestas e 7 etiquetas; 0 colliders novos; aprovação de plot, altitude, navmesh e rotas de gameplay permanecem FALSO.
- Evidência versionada `Docs/PROJECT_RESORT_EXECUTION/R12_GEO_CANDIDATE_PREVIEW_NATIVE_QA.json`, com teste automatizado `Tools/Bridge/test_r12_editor_preview_native_qa.py` para assegurar origem real Unity e política Editor-only. O report **NÃO** comprova screenshot, percurso caminhável ou verificação de colisões.

## Limitações e próximo passo
Candidato geométrico não é lote construível nem terreno reservado. O P5 240×190m continua inalterado e sem posição viável nas premissas. A câmera de revisão e os contornos em `y=0.64m` são apenas marcações visuais, não altitude real. A próxima fase verificará se cada retângulo fica visível, sobrepõe estruturas 3D ou tem caminho praticável na cena R14, depois construirá navmesh/física e adaptação de missões/saves em uma build separada. Nenhuma cena jogável, avatar, save ou EXE foi alterado.
