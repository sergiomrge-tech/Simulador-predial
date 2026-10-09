# Project Resort — ponte técnica entre a cidade visual R12 e o jogo jogável
Data: 2026-10-09 · Executor paralelo: ChatGPT · **ART GATE pendente**

## Objetivo e limites
O usuário quer que o visual de Copacabana passe a integrar o **jogo real**, mantendo missões,
jogabilidade, quiosques, construção, economia e saves. A base visual é
`sergiomrge-tech/Resort-Simulator-` branch `codex/r12-urban-storefronts`
(`afa4dfa`); o jogo está em `sergiomrge-tech/Simulador-predial`
(`bc11f2b` mais alterações locais ainda não enviadas, que **não foram tocadas**).
Trabalho executado somente em um novo worktree: `codex/r12-gameplay-visual-bridge`.

## Feito — código e teste concreto (Unity real)
1. `Tools/Bridge/stage_r12_preview.py`: importador determinístico de dependências
   Unity por **GUID / SHA-256**, em vez de copiar assets aleatoriamente. Percorre recursivamente
   as referências de cena, material, FBX, importadores e shaders autorais, mantendo as .meta
   originais. Não modifica fontes nem arquivos da cena jogável.
2. **622 assets Unity reais**, com **121.093.212 bytes**, extraídos do projeto visual
   já testado para `FacilityOps/Assets/_Game/Preview/CopacabanaR12` (staging local,
   excluído do Git para não duplicar assets binários entre dois repositórios).
   Detectou **0 colisões GUID** e 9 referências de GUID não presentes no
   escopo de assets locais (pacotes Unity/builtins, a confirmar via importação Unity).
   Manifest rastreável em `R12_GAME_BRIDGE_DEPENDENCIES.json`, com SHA por arquivo.
3. `ResortR12GameBridgeAudit.cs` importou e abriu essa cena de verdade no
   projeto `FacilityOps` via **Unity 6000.6.2f1, Direct3D11 / RTX 4060 Ti**.
   O teste aceitou 350 renderers R8, 210 R11, 19 R12, 9 de calçadão
   R10, 48 árvores, 3.731 triângulos de vias, **0 materiais/shaders/scripts
   faltando** e **0 UV0 ausentes** em R8/R10/R11/R12.
4. **Achado de arte importante:** os 48 meshes de árvore `R9_TREE_*`
   do código de origem antigo carecem de UV0. O teste separa esse problema de
   "shader quebrado"; a vegetação exige nova UV/folha/textura na R13, sem
   bloquear a importação do restante. Não chamar árvores de aprovação visual.
5. Três testes Python usam projetos temporários falsos **somente para verificar
   o importador**, nunca como screenshots do jogo: árvore de dependências,
   rerun idempotente, recusa de sobrescrever staging alterado e proteção
   contra colisão GUID. Todos aprovados.
6. Unity salvou JSON técnico: `R12_GAME_BRIDGE_UNITY_QA.json`. **NÃO foi
   compilado nenhum executável de jogo com a nova cidade**, e nenhum save,
   Bootstrap, ResortPrologue ou gameplay ativo foi sobrescrito.

## BLOQUEIO GEOGRÁFICO QUE EXIGE ETAPA DE ENGENHARIA (não maquiar)
- O jogo atual `ResortSite.json` contém **900 × 720 m** de cena local,
  origem local `(-450, -3965.7347)`, quiosque/lar/pontos de missão
  construídos nessas coordenadas, 234 lotes genéricos.
- A R12 tem **2.000 × 1.000 m**, 1.468 edifícios e base **OSM geográfica**
  EPSG:32723, rotação de quadro 46 graus. **Não há correspondência direta
  comprovada de quiosque, casa ou lotes entre os dois mundos.**
- `ResortSite.Build()` já cria terreno, rua, vila, mar, vegetação, quiosques,
  inclusive colisões. Adicionar a cena R12 simultaneamente faria o mapa
  duplicado/sobreposto e a progressão ficaria sem direção.
- Proibido simplesmente redimensionar X/Z não uniformemente: distorce
  texturas, colisor, posições de NPC e arquitetura; proibido deslocar OSM
  para coincidir com um edifício fictício sem decisão explícita de design.

## Implementação necessária no PR de integração jogável futuro
### Gate I — Acordo geográfico e pontos de gameplay
Definir a cidade 2 km × 1 km como autoridade para o mapa principal.
Mapear semanticamente `Home`, `Stall`, parcelas P1–P8, NPCs, acessos,
missões e travessias para coordenadas **do mundo R12** por ids/âncoras
versionados (`ResortR12GameplayAnchors.json`), mantendo 1 unidade = 1 m.
Os marcadores fictícios podem coexistir apenas como locais ficcionalizados;
isso deve ser declarado no mundo do jogo. Não alterar dados OSM.
A migração dos saves deve preservar dinheiro, estoque, etapas e missões e
converter apenas posições quando existir ponto semântico mapeado.

### Gate II — Uma só paisagem
Construir `ResortEnvironmentMode` com modo `Legacy` (padrão seguro)
e `CopacabanaR12` (opt-in). Desativar somente as *superfícies* legadas
`terrain/sea/roads/buildings` quando R12 ativo, mantendo instâncias de gameplay
quiosques/hotel/casa que tenham âncoras mapeadas. Manter **uma única** camada
de iluminação principal e céu URP; evitar dois soles, oceanos e render textures.
Carregar recursos divididos por setores, não 622 assets numa cena à força
se FPS/VRAM estiverem comprometidos.

### Gate III — Física e fluxo crítico
Adicionar colliders coerentes nas ruas/praia e entradas de colisão, com
`CharacterController` testado em altura certa. Validar respawn, caminhada
da casa ao trabalho, acesso ao quiosque, interação/troca de painéis,
construção por parcela, entrada/saída, entrega, iniciar dia e salvar/carregar.
Sem atraves­sar parede ou nascer no mar. Ajustar minimapa, GPS e
guia de missões. São obrigatórios testes reais em **jogo** além do
projeto visual de QA.

### Gate IV — Estética e desempenho
Refinar vegetação UV-less, aprovar casas/prédios adjacentes com PBR coeso,
cobertura da orla por 10 setores de 200 m, capturar Unity real por setor.
Perfilar FPS/GPU/memória e LOD no Windows; só atualizar atalho **Jogar**
quando houver build jogável derivado, sem sobrescrever a build antiga.

## Reprodutibilidade
Em Windows com o projeto visual R12 validado e copiado para D:, executar:

```powershell
python Tools/Bridge/stage_r12_preview.py --visual D:\ProjectResort_R8_UnityQA\UnityProject --game D:\ProjectResort_GameIntegration_R12
python -m unittest discover -s Tools/Bridge -p "test_*.py" -v
& "C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe" -batchmode -quit -force-d3d11 -projectPath D:\ProjectResort_GameIntegration_R12\FacilityOps -executeMethod ResortAurora.EditorTools.ResortR12GameBridgeAudit.Audit -logFile D:\ProjectResort_GameIntegration_R12\R12_bridge_unity.log
```

GitHub versiona o **código, documentação, contrato de hashes e resultados de QA**;
arquivos FBX/PNG Unity de 121MB são regeneráveis pelo workflow R12 do
repositório visual, portanto a cópia nesta branch permanece gitignored.
Antes de usar outro PC, reconstruir R7→R12 no repositório visual e executar
`ResortR7FacadeFinish.Build` até `ResortR12StreetFinish.Build` para obter
cena R12 e `.meta` originais — não importar cena sem gerar materiais PBR.

### Resultado desta etapa
**PASS importação Unity / integridade do projeto principal.**
**PENDENTE alinhamento R12↔gameplay, revisão visual, correção de UV da vegetação,
física, FPS e executável jogável R12.**
