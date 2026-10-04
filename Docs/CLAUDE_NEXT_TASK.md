# CLAUDE NEXT TASK — ETAPA D

## W2 — Cidade Antiga Base

Os Gates A, B e C foram concluídos e registrados no GitHub:

- **Gate A — W1.5:** PASS. Pipeline completo, masterplan v1.5, Cidade Antiga base, kit/material library, validação sem erros, 3/3 reaberturas PASS.
- **Gate B — Skills:** PASS. Biblioteca Docs/SKILLS/00…22 + Tools/Skills/catalog.json, TOP 10/TOP 5, licenças e riscos registrados; nada instalado.
- **Gate C — Revisão:** PASS técnico. 10 critérios PASS, nenhum BLOCKED; 7 NEEDS_FIX subjetivos/acabamento registrados em Docs/W1_5_REVISAO_GATES.md.

A aprovação visual final continua sendo do usuário, mas a fila autorizada permite iniciar W2 de forma limitada na Cidade Antiga.

## Executar agora

Começar **W2 Cidade Antiga Base** sem propagar arte final para outros distritos.

Prioridades:

1. Refinar o kit arquitetônico modular para produção:
   - paredes, quinas, portas, janelas, molduras;
   - telhados, beirais, grades, portões, calhas;
   - escadas, rampas, muros, calçadas, meio-fio;
   - corrigir N3: esquinas chanfradas/sobreposições e adicionar rebaixos coerentes.

2. Elevar materiais da estrutura PBR existente:
   - concreto, reboco, tijolo, asfalto;
   - metal/aço pintado/ferrugem;
   - madeira, vidro, cerâmica, plástico, borracha;
   - manter registro de procedência/licença de qualquer fonte externa;
   - não instalar ferramentas/dependências sem autorização.

3. Reduzir repetição visual da Cidade Antiga (N1):
   - mais variações coerentes;
   - acessórios procedurais;
   - fachadas/laterais/fundos mais ricos no recorte do vertical slice;
   - preservar escala, IDs, footprints, acessos e streaming.

4. Refinar ambiente urbano:
   - postes/iluminação pública;
   - caixas elétricas, hidrômetros, telecom;
   - drenagem, tampas, sinalização e hidrantes;
   - clutter funcional controlado;
   - paisagismo/pisos/recuos (N4).
   - árvores-proxy continuam explicitamente provisórias; vegetação final é etapa posterior.

5. Hero Locations nesta ordem:
   A. Lar inicial;
   B. Oficina Aurora;
   C. Edifício Horizonte;
   D. Teatro Imperial;
   E. demais locais da Cidade Antiga.

6. Para Lar + Oficina + Horizonte:
   - exterior mais detalhado;
   - acessos e áreas de serviço;
   - estacionamento quando aplicável;
   - interiores somente onde gameplay/prológo exigir;
   - estados H0–H4/G0–G4 preservados;
   - preparar clutter/mobiliário sem quebrar a lógica existente.

7. Manter performance desde já:
   - instancing onde adequado;
   - planejamento LOD;
   - evitar geometria única gigante;
   - preservar divisão 1 km / subcélulas 250 m;
   - registrar contagens/complexidade antes e depois.

8. Executar validações e reaberturas reais do Blender.
9. Gerar capturas reais do avanço; nunca mockups.
10. Atualizar relatório/status, commit e push.

## Restrições

- Trabalhar somente em `claude/w1-masterplan`.
- Não fazer merge no `main`.
- VEIN é referência de patamar visual/atmosfera, nunca fonte de assets/layouts/texturas.
- Low-poly continua permitido somente como blockout temporário.
- Não alterar IDs/saves/.meta sem necessidade demonstrada e migração.
- Não quebrar o protótipo Unity.
- Não instalar MCP/add-on/dependência sem autorização explícita.
- Skills próprias e conteúdo já versionado podem ser consultados diretamente; não copiar para ambientes ativos se isso for considerado instalação.
- Não escalar acabamento para outros distritos antes do gate visual/funcional da Cidade Antiga.

## Gate D parcial

Antes de declarar progresso W2 consolidado:
- Lar + Oficina + Horizonte devem mostrar evolução concreta acima do massing;
- kit arquitetônico e ambiente urbano devem ter refinamento verificável;
- N1/N3/N4 devem estar tratados ou claramente medidos;
- pipeline Blender deve reabrir sem missing data;
- capturas reais devem existir;
- complexidade/performance deve estar documentada;
- relatório de continuidade atualizado;
- commit + push;
- working tree limpa.

Se o limite de uso interromper a execução, salvar em ponto seguro, documentar exatamente o que falta, commit/push e deixar a árvore limpa para retomada.
