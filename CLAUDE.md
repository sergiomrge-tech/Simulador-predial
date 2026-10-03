# PROJECT FACILITY — contexto para Claude

Leia primeiro `Docs/DECISOES_ATUAIS.md`, `Docs/LORE_CAMPANHA_ORIGINAL.md`, `Docs/MAPA_CAMPANHA.md`, `Docs/STATUS_IMPLEMENTACAO.md` e `README.md`.

## Direção vigente

Unity 6000.6.2f1, URP, C#, Windows/Steam, single-player, **primeira pessoa**. O usuário chegou a pedir terceira pessoa, mas decidiu voltar à primeira pessoa. Manter a engine instalada, a lore de Santa Aurora e o diferencial diagnóstico → reparo → teste → pagamento.

## Onde trabalhar

- Projeto ativo: `FacilityOps/`. Cena `Assets/_Game/Scenes/Bootstrap.unity`.
- Regras: `Assets/_Game/Scripts/Core/`.
- Câmera/colisões/interação: `Assets/_Game/Scripts/Runtime/Interaction.cs`.
- Tablet provisório: `TabletUI.cs`. Migrar para UI Toolkit ou uGUI antes de polir.
- Mundo: `WorldBuilder.cs`. Garagem e chamado inicial; prévias de plantas do catálogo.
- Campanha: `Assets/_Game/Resources/World/campaign.json`, gerado por `Tools/Map/generate_campaign.mjs`.
- Fontes de arte: `ArtSource/Blender/`; FBX em `Assets/_Game/Resources/Art/`.
- Build e verificações: `Tools/Build.ps1`, `Tools/Test-Windows.ps1`.

Não editar JSON gerado sem atualizar o gerador. IDs devem permanecer estáveis. Não serializar GameObjects no save. Não sobrescrever progresso do usuário durante testes. Preservar arquivos `.meta`. Mudanças de câmera não podem estender o alcance de interação além da distância do personagem.

## Próximas tarefas recomendadas

1. Conferir a área inicial em primeira pessoa e adicionar mãos/ferramentas com animações táteis, sem alterar o alcance do raycast.
2. Converter a garagem, o corredor aprovado e os equipamentos em prefabs/cenas editáveis, mantendo componentes e IDs.
3. Implementar o prólogo autoral no Horizonte: aquecimento fictício, isolamento, teste, troca, restauração e conversa/mensagens de Guto/Helena.
4. Substituir um conjunto pequeno de setores do catálogo por arquitetura e props finais do Blender, mantendo as conexões.
5. Construir inspeção, fotografia/laudo e consequências persistentes antes de desbloquear capítulos avançados.
6. Adicionar hidráulica e bombas e depois climatização; somente então implementar Cascata e coordenação de equipes.

Os mapas de campanha são estruturas de protótipo. Os capítulos, NPCs, decisões e finais não estão todos implementados. Não afirmar qualidade premium, desempenho alvo ou campanha pronta sem evidência de execução e inspeção visual.

Use branches `codex/` ou `claude/` e mudanças focadas para permitir integração. Este arquivo é contexto de colaboração, não autorização para publicar releases, enviar mensagens ou mudar a visibilidade do repositório.
