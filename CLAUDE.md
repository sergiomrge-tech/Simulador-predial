# PROJECT FACILITY — contexto para Claude

Leia primeiro `Docs/DECISOES_ATUAIS.md`, `Docs/PLANO_MESTRE_MUNDO_SANTA_AURORA.md`, `Docs/GDD_PROGRESSAO_VIDA_LIBERDADE_ECONOMIA.md`, `Docs/LORE_CAMPANHA_ORIGINAL.md`, `Docs/MAPA_CAMPANHA.md`, `Docs/STATUS_IMPLEMENTACAO.md` e `README.md`.

## Direção vigente

Unity 6000.6.2f1, URP, C#, Windows/Steam, single-player, **primeira pessoa**. O usuário chegou a pedir terceira pessoa, mas decidiu voltar à primeira pessoa. Manter a engine instalada, a lore de Santa Aurora e o diferencial diagnóstico → reparo → teste → pagamento.

A direção visual do mapa, casas, estruturas e interiores usa **VEIN apenas como referência de qualidade e linguagem visual**: realismo urbano cru, materiais PBR usados, iluminação atmosférica, clutter funcional e interiores densos. **Não aceitar low-poly como resultado final.** Blockouts podem ser simples apenas durante produção. Não copiar assets, texturas, prédios, layouts ou mapas.

Nova regra de progressão: campanha + mercado livre de trabalhos. O jogador decide em que trabalhar e em quais regiões desbloqueadas atuar. O escopo inicial é pequeno e cresce com reputação, dinheiro, ferramentas e veículo. O jogo deve ser difícil, porém sempre recuperável.

## Onde trabalhar

- Projeto ativo: `FacilityOps/`. Cena `Assets/_Game/Scenes/Bootstrap.unity`.
- Regras: `Assets/_Game/Scripts/Core/`.
- Serviços autorais iniciais do Capítulo I: `ChapterOne.cs`, IDs estáveis, local/causa/preço/nomes dos equipamentos. `Docs/CAPITULO_I_IMPLEMENTADO.md` registra o escopo e as adaptações.
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
3. Polir o prólogo autoral implementado no Horizonte: aquecimento fictício, isolamento, teste, troca, restauração e mensagens persistentes de Guto/Helena. Ler `Docs/PROLOGO_IMPLEMENTADO.md`. Converter mensagens em apresentação narrativa sem quebrar as regras de intervenção.
4. Substituir um conjunto pequeno de setores do catálogo por arquitetura e props finais do Blender, mantendo as conexões.
5. Construir inspeção, fotografia/laudo e consequências persistentes antes de desbloquear capítulos avançados.
6. Validar na Unity o primeiro contrato preventivo de bomba já integrado no código e ajustar qualquer erro de parser/runtime antes de expandir.
7. Antes de ampliar sistemas, transformar `SantaAurora_Masterplan.blend` em masterplan métrico seguindo o plano 8×8 km, posicionando distritos, vias e todos os locais de campanha.
8. Criar o kit arquitetônico PBR e o kit técnico modular da Cidade Antiga sem aparência low-poly final.
9. Produzir o lar inicial, Oficina Aurora, Horizonte e primeiros clientes como primeiro conjunto de alta fidelidade.
10. Validar a Cidade Antiga como vertical slice visual/funcional e só então replicar o padrão para os demais distritos.
11. Depois implementar mercado livre de 3–5 chamados, veículos, patrimônio, climatização e liberdade econômica. Só então avançar Cascata e coordenação de equipes.

Os mapas de campanha são estruturas de protótipo. Os capítulos, NPCs, decisões e finais não estão todos implementados. Não afirmar qualidade premium, desempenho alvo ou campanha pronta sem evidência de execução e inspeção visual.

O primeiro aceite da campanha usa `ServiceSession.AcceptPrologue`; os três serviços iniciais seguintes usam `AcceptChapterOne(id)` em ordem. Chamados livres continuam com `Accept(cause)` e não contam como serviços autorais. Save v1 inclui `servicePresenceVersion/hasActiveService` para impedir que uma classe inline vazia represente um chamado encerrado e `chapterOneDataVersion` para adicionar o estoque hidráulico em carreiras anteriores.

`CareerData.completedChapterOneJobs/buildingHistory/recurringContractUnlocked` são persistentes. Três serviços mais reputação 25 liberam a indicação de Helena. O primeiro contrato preventivo de bomba foi integrado ao código com ID estável `campaign.c2.recurringcondo.pump.v1`, estoque `pumpKits`, flags persistentes e extensão do smoke test; **essa nova etapa ainda precisa de validação real na Unity após os commits recentes**. A classe `ElectricalNetwork` conserva o nome original por compatibilidade e também fornece leituras hidráulicas abstratas. Preservar compatibilidade de saves, IDs e testes separados do jogador.

Use branches `codex/` ou `claude/` e mudanças focadas para permitir integração. Este arquivo é contexto de colaboração, não autorização para publicar releases, enviar mensagens ou mudar a visibilidade do repositório.
