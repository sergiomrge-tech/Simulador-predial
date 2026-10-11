# AGENTS.md — Project Resort / FacilityOps

## Instruções obrigatórias para agentes de programação e modelagem
- O usuário estabeleceu expressamente: **TODOS OS ASSETS PRECISAM TER O MESMO ESTILO VISUAL**. Esse requisito tem precedência sobre quantidade de assets integrados ou velocidade.
- Antes de alterar prédios, interiores, vegetação, iluminação ou materiais, leia `Docs/PROJECT_RESORT_EXECUTION/RESORT_VISUAL_COHESION_GATE_20261007.md` e confira `D:\ProjectResort_Autonomy\RESORT_VISUAL_CURATION_20261007.json`.
- Direção visual: **resort costeiro brasileiro contemporâneo e premium fotorrealista (Unity URP PBR)**; materiais coesos, arquitetura adequada ao local, praia tropical e paisagismo natural, luz/sombras de mesma qualidade em todos os objetos. Proibido mesclar low-poly, fantasia, stylized, construções europeias anacrônicas ou props industriais incompatíveis.
- Os pacotes vrbn e Furniture Mega Pack são bancos de CANDIDATOS, não garantia de aprovação de todos os modelos. O status `HOLD` veda integração no mapa principal até uma revisão explícita.
- Nunca editar o projeto inteiro a partir do download do pacote. Estagiar em D:, importar subset aprovado, preservar os GUIDs originais, colisões, game loop, save, scripts e ruas. Manter asset original em backup; não executar `git clean/reset` destrutivo.
- Validar unidade métrica, escala, pivô, shader, terreno, acesso, conjunto arquitetônico, materiais e renderização real no Unity, com capturas REAIS e condições de luz comparáveis. Não afirmar visual aprovado se ainda estiver pendente.
- O mapa do resort terá 2 km² de território terrestre segundo pedido do usuário. Evitar limites fixos relacionados a protótipos de 900x720m; seguir SiteData quando houver expansão.
- Para código de produção, priorize evidência de compilação e teste antes de declarar conclusão. Não usar screenshots de ilustração como execução real.

## Arquivos e responsabilidades
- Projeto Unity: `FacilityOps/`; cena costeira `FacilityOps/Assets/_Game/Scenes/ResortPrologue.unity`.
- Biblioteca independente de assets: `D:\ProjectResort_AssetLibrary`.
- Codex edifícios: `D:\ProjectResort_Autonomy\CodexVRBNIntegration`.
- Não importar assets de status HOLD; descarte visual deve ser lógico (não apagar licenças, backups ou arquivos da biblioteca externa).
