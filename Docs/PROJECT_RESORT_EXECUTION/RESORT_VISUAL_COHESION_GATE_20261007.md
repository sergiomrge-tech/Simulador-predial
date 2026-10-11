# PROJECT RESORT — DIREÇÃO VISUAL ÚNICA E GATE DE COERÊNCIA (obrigatório)
Atualização: 07/10/2026. Ordem expressa do proprietário: **todos os assets devem ter o mesmo estilo visual**. Esta diretriz prevalece sobre o desejo de importar o maior número possível de recursos.

## Identidade visual oficial para integração
**Resort costeiro brasileiro, contemporâneo, fotorrealista e premium, com entorno urbano plausível**. Praia / orla tropical / calçadão / avenida / hotel / quiosques / residências e serviços. As construções podem ter tipologias distintas para parecer um bairro de verdade, mas a fidelidade visual, escala, materiais e iluminação devem ser coerentes. Evitar parque temático, cidade europeia deslocada, industrial distópico, fantasia e móveis de épocas incompatíveis.

### Regras técnicas de unidade visual
1. PBR fisicamente plausível em **Unity URP Lit**; base color, normal, metallic, roughness/smoothness e AO coerentes; nada de albedo plano que imite textura por cor. Corrigir color space, normal map e handedness na importação. **A mesma exposição, pós-processamento e iluminação em todos os elementos**.
2. Luz do dia e sombras coerentes com a latitude costeira; sombras de contato e oclusão moderada, sem áreas absurdamente negras nem objetos flutuando. Madeira, concreto, calçadas, fachadas e vegetação devem reagir de forma consistente à luz.
3. Referência cromática para arquitetura e mobiliário: **branco quente, areia, pedra clara, cinza concreto natural, madeira clara/média** com vidros azul/verde discretos, ferragens grafite; cor de destaque em doses moderadas (vegetação tropical, sinalização urbana, azulejaria pontual). Evitar saturação artificial e repetição mecânica.
4. Escala REAL (1 unidade Unity = 1 metro), proporção de portas, janelas, pavimentos, árvores e mobiliário. Pivôs, orientação, fundações, portas de acesso, colliders e sombras realistas. **Não esmagar/escalar modelos arquitetônicos para caber em lotes incompatíveis**: substituir com outro modelo que caiba ou manter candidato em espera.
5. Reservar 2K para material com visão próxima / 1K a 2K para props intermediários, com LOD e instancing; não baixar/usar 4K indiscriminadamente em objetos distantes. Consistência de Texel Density, roughness e detalhe microfaceta é mais importante que a resolução nominal.
6. Distribuição de fachada e vegetação deve ser VARIADA MAS COESA: 2–4 famílias arquitetônicas compatíveis por quadra, não clones idênticos; calçada/ruas sem buracos ou barreiras; vegetação tropical de porte apropriado, sem misturar árvores temperadas à beira da praia, evitar excesso/enchimento aleatório.
7. Arquitetura urbana existente: `vrbn Studios Free Buildings URP Bundle 001` é uma **fonte de candidatos**, NÃO um selo automático de aprovação para todos os prédios; inspeção de tipologia, altura, fachada e cor na CENA REAL em conjunto é obrigatória.
8. O Furniture Mega Pack contém 511 prefabs mas **não** estão automaticamente aprovados; selecionar apenas modelos com qualidade de geometria PBR e cores consistentes, excluindo os que pareçam toy-like, estilizados, low-poly ou fora da época.
9. **Gate visual**: cadastrar cada família/prefab novo na matriz com origem/licença, categoria, escala, shaders, estilo e 1 print REAL do Unity ao lado dos elementos vizinhos sob a mesma luz antes de liberar uso em massa. O status fica `CANDIDATE`, `HOLD` ou `APPROVED_ON_SCENE`; `APPROVED_ON_SCENE` requer verificação visual e nativa, não apenas download, screenshot de loja ou parser.
10. Se não existir opção compatível, deixar *lacuna organizada e listada*, buscar alternativa realista; jamais preencher com assets incongruentes ou falsificar um print de jogo. A inclusão de assets em biblioteca externa **não** implica importação no jogo.

## Compatibilidade por função / curadoria inicial
- **CANDIDATE para teste na cena**: arquitetura contemporânea/coesa do vrbn; sofás/camas/cadeiras/banheiros contemporâneos do Furniture Mega Pack após avaliação; mesa de madeira natural, vasos de cerâmica neutros, luminárias contemporâneas, lâmpadas discretas, gramíneas, palmeiras realistas, rochas costeiras e bancos de jardim; texturas Poly Haven claras/coerentes.
- **HOLD (não importar nem colocar no cenário principal sem revisão)**: elementos *industrial_wall_lamp*, *caged_hanging_light*, *vintage_suitcase*, *wine_barrel_01*, *brass_pot_01*, *plastic_monobloc_chair_01*, *modular_chainlink_fence*, *BarberShopChair_01*, qualquer *GothicBed*, castelo, itens fantasiosos, decorações excessivamente rústicas. Podem servir em cenários muito específicos, mas NÃO definem a estética do resort.
- **CANDIDATE CONTEXTUAL**: *jacaranda_tree* apenas em ruas afastadas do calçadão após prova de adaptação botânica; flores/forrações conforme bioma litorâneo, evitar jardinagem temperada deslocada. *wooden_picnic_table* apenas se encaixar como quiosque de praia real, não no lobby premium.
- **HOLD permanente como resultado final**: todos os blocos genéricos/procedurais sem acabamento ou low-poly/stylized. Temporários podem ficar exclusivamente enquanto o substituto compatível não passar pelo gate, nunca apresentados como versão visual final.

## Responsabilidades / ordem de execução
**Codex edifícios:** revisar aplicação dos vrbn por conjunto urbanístico, garantir coerência entre prédios vizinhos, escala, fachadas e materiais. Não maximizar número de prefabs a qualquer custo. Preservar tráfego, colisões e entradas.
**Frente auxiliar de assets:** catalogar novos recursos baixados na unidade D: sem importar cegamente; separar CANDIDATE vs HOLD; manter licenças e hashes, preparar vista de comparação real para revisão.
**Diretor:** aprovar/recusar composição final olhando prints REAIS tirados do Unity. Sem dizer que estilo aprovado enquanto a inspeção não ocorrer.

**Importante:** o arquivo é a referência para todo novo trabalho visual, inclusive quando mapa terrestre crescer para 2 km².
