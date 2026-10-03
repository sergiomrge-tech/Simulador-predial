# Estado da implementação — 03/10/2026

## Entregue nesta etapa

- Unity 6000.6.2f1/URP/C#, Input System, primeira pessoa e personagem com colisão.
- Garagem inicial, tablet, estoque, chamados e retorno à sede.
- Uma rede elétrica abstrata com três causas do mesmo sintoma, duas ferramentas de medição e inspeção visual.
- Evidências, escolha de diagnóstico, consumo de peças, penalidade por troca errada, reparo, validação e pagamento único.
- Dinheiro, experiência, reputação, reposição de peças e crédito do fornecedor para recuperar falta de estoque/saldo.
- Save local versionado v1, escrita temporária, backup, recuperação e progresso de chamado ativo.
- Três equipamentos autorais do Blender e corredor arquitetônico inicial importados em FBX e preparados para URP.
- Estudo de implantação de Santa Aurora no Blender com os 24 locais da campanha.
- Catálogo com 6 distritos, 24 locais, 182 setores, 30 pavimentos e prólogo + capítulos I–XIV.
- Visitas de prévia aos locais, com portas físicas, mudança de pavimento pelo tablet e registros ambientais. A prévia não concede recompensas nem avança a história.
- Documentos de decisões atuais, plantas, lore original e handoff para Claude.

## Verificações e evidências

- Regras de domínio verificadas pelo editor antes do build: três causas, pré-requisitos, peças, troca errada, teste final obrigatório, pagamento duplicado bloqueado, crédito e backup de save.
- Executável Windows testado com save próprio de QA: interação por raycast, colisão com piso/parede, evidências, três reparos, luzes restauradas, validação, retorno ao hub, economia e save/load.
- Catálogo validado: todos os IDs de locais de capítulos existem e todos os grafos de setores são conectados.
- 30 pavimentos e 213 conexões de portas percorridos pelo CharacterController no executável.
- Equipamentos Blender verificam orientação vertical e escala em metros no runtime. Capturas de câmera mostram corredor, equipamentos e uma planta de Santa Aurora Central.
- Os arquivos `.blend` foram reabertos para conferir geometria, UVs do kit/corredor, textura incorporada do kit e presença dos 24 locais no estudo da cidade.

Relatórios completos locais: `Logs/unity-build.log`, `Logs/rules-passed.txt`, `Logs/windows-smoke.log` e `Builds/Windows/QA/PASSED.txt`. Resultados resumidos portáveis: `Docs/map-validation.json`, `Docs/QA_RESULTADO.txt` e `ArtSource/Blender/*verification.json`.

As capturas foram feitas com render request URP fora da tela. Elas verificam a câmera e o cenário; não representam captura de todos os estados do tablet IMGUI. Interação humana e usabilidade das abas ainda precisam de playtest.

## Limites da entrega

Esta é a fundação e estrutura explorável de um protótipo, não a campanha inteira concluída nem a arte final premium.

Os locais avançados usam uma grade modular de teste. A dimensão e posição dos distritos são uma proposta de level design baseada na lore, não uma geografia fornecida pelo usuário. A arquitetura completa de cada local precisa de curadoria própria. As ligações verticais estão registradas no catálogo e usam viagem pelo tablet; escadas e elevadores físicos ainda não existem.

O chamado inicial de teste sorteia três causas. O prólogo da lore possui causa autoral e exige aquecimento fictício, isolamento de circuito e reincidência, ainda pendentes. NPCs, diálogos, fotografias/laudos, eventos climáticos, auditoria, escolhas, finais, equipes e Cascata estão estruturados narrativamente, mas não implementados como campanha jogável.

UI é provisória em IMGUI. Os ScriptableObjects são definições iniciais ainda sem catálogo de assets conectado; missões de teste estão no código. Ambientes são montados em runtime e precisam migrar para cenas/prefabs editáveis. Não houve validação de 60 FPS em máquinas de referência, gamepad ou acessibilidade final. Steamworks não integrado.

## Ordem recomendada de continuidade

1. Playtest da câmera em primeira pessoa, prompts e tablet.
2. Prefabs/cena do Edifício Horizonte e garagem; mãos, ferramentas e ações táteis.
3. Prólogo autoral de Guto e Helena.
4. Inspeção/documentação e memória persistente dos prédios.
5. Hidráulica e bombas; segundo ciclo de serviço completo.
6. Arte final de um pequeno conjunto de setores antes de expandir acabamento aos 24 locais.
7. Climatização, redundância e equipes; depois campanha avançada e operação Cascata.
