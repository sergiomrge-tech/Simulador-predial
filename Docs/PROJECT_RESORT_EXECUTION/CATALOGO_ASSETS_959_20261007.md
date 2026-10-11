# PROJECT RESORT — ASSETS GRATUITOS (BIBLIOTECA ATUALIZADA) — 07/10/2026
Status: **DOWNLOAD E INTEGRIDADE VALIDADOS; IMPORTAÇÃO E APROVAÇÃO VISUAL AINDA PENDENTES**.

## Dados confirmados depois do download
- **959 modelos GLB novos**, auditados com SHA-256 e leitura de cabeçalho glTF; 0 erros, aproximadamente 113,4 MB no total.
- **951 modelos CC0 da 3DAssets.dev** distribuídos entre 10 pacotes; esses modelos têm estética CAD/procedural e em muitos casos não trazem detalhes fotorrealistas, portanto devem ser considerados **COMPONENTES DE PROTOTIPAGEM/ALVOS DE MELHORIA, não ARTE FINAL**. Não importar em massa e não apresentar visual simplificado como o padrão exigido.
- **8 modelos CC0 da Innerscene** com materiais e mapas de texturas embutidos, com 79 slots de textura no conjunto, mais adequados como candidatos para ambientes de primeiro plano. Ainda exige teste visual Unity.
- **Licenças de todos estes downloads:** CC0 1.0 Universal (cada arquivo/fonte registrado na pasta); os downloads anteriores da Unity são licenciados sob Unity Asset Store EULA e NÃO podem ser tratados como CC0.
- **Integridade:** `D:\ProjectResort_Autonomy\RESORT_5STAR_FREE_ASSET_DOWNLOAD_AUDIT_20261007.json`.
- **Atenção:** não são animações de hóspedes, física de água, colisão nem scripts de gameplay. Esses sistemas continuam exigindo implementação.

## Pacotes novos (quantidades verificadas)
| Pacote | Quantidade | Aplicação possível |
| --- | ---: | --- |
| Hotel and Resort Operations | 140 | Suítes, lobby, camareiras, buffet, spa, equipamentos de piscina |
| Waterpark and Pool Operations | 31 | Piscinas, escorregadores, segurança e equipamentos hidráulicos |
| Restaurant Kitchen and Dining Room | 143 | Cozinha industrial, restaurantes e buffet |
| Cafe, Bakery and Coffee Bar | 112 | Quiosque, máquinas de café, padaria, expositores |
| Beach Surf and Paddle Kit | 52 | Praia, salva-vidas, guarda-sóis, cadeiras, chuveiros |
| Public Swimming Baths and Poolside | 54 | Infraestrutura aquática, circulação e equipamentos |
| Fitted Kitchen and Bathroom Builder | 132 | Banheiros, pias, quartos, sistemas modulares |
| Bar Pub and Brewery Taproom | 130 | Equipamentos de bar, dispensadores, cervejaria — filtrar elementos de pub incompatíveis com resort brasileiro |
| Gym and Fitness Studio | 46 | Academia, musculação, cardio, estúdio |
| Office Lobby and Facilities | 111 | Recepção, corredores, elevadores, back-office e manutenção |
| Innerscene Hotel Original Furnishing | 8 | Cama, sofá de lobby, consoles, guarda-roupa, bagageiros |
| **Total** | **959** | **Biblioteca de candidatos, não assets finais do jogo** |

## Pastas exatas no D:
- `D:\ProjectResort_AssetLibrary\CC0_3DAssetsDev_Resort20261007` — 426 modelos.
- `D:\ProjectResort_AssetLibrary\CC0_3DAssetsDev_ResortExpansion20261007` — 368 modelos.
- `D:\ProjectResort_AssetLibrary\CC0_3DAssetsDev_Gym20261007` — 46 modelos.
- `D:\ProjectResort_AssetLibrary\CC0_3DAssetsDev_Office20261007` — 111 modelos.
- `D:\ProjectResort_AssetLibrary\CC0_Innerscene_Hotel20261007` — 8 modelos com texturas.
- Todas as coleções têm manifestos de fontes, licença CC0, URLs e SHA-256.

## Bibliotecas anteriores preservadas
- 3 pacotes oficiais Unity em D: `vrbn Studios Free Buildings URP Bundle 001`, `Furniture Mega Pack - Free`, `AURW URP Free`; `Mobile Palm Pack URP` também consta agora em cache D: (não adequado como palmeira hero por poucos triângulos).
- Poly Haven CC0 de modelos 3D e acabamentos PBR 2K, com coleção de +100 candidatos, incluindo recentemente 14 acabamentos de piscina/spa + 7 novos props específicos. Primeira fonte para texturas finais fotorrealistas.
- Variedade de renderpeople já disponível. Não criar bonecos estáticos como se fossem animações.

## Gate visual — obrigatório em Unity 6 URP
1. **Não importar os 959 modelos automaticamente nem substituir modelos realistas do Codex por versões simples.**
2. Priorizar os GLBs **Innerscene com materiais/texturas** e modelos **Poly Haven** no primeiro plano; usar os modelos 3DAssets.dev só após melhorar shader/material PBR e aprovar capturas reais na mesma iluminação. Não misturar cartoon, estilo cinza de CAD, toy-like ou low-poly simplista no visual final.
3. Para importar GLB, verificar se o projeto possui `com.unity.cloud.gltfast` (Unity glTFast) ou usar conversão offline para FBX preservando materiais; não alterar o projeto enquanto a cena VRBN estiver sob testes.
4. Adequar materiais ao padrão costeiro premium brasileiro: pedra clara, madeira natural, reboco areia/branco quente, vidro, vegetação tropical com PBR realista, água com URP. Mesmo sol/exposição/fog/reflexos/sombra em todos os modelos.
5. Piscina principal, borda infinita e *lazy river* precisam de geometria personalizada, água e fluxo, segurança, colisões e interações. **Pacote grátis não substitui engenharia de jogo.**
6. Integrar primeiro **orla e quiosque** (núcleo jogável), depois hotéis e evolução, depois complexo aquático e serviços. Não aprovar o cenário sem capturas REAIS (screenshots de pacotes são apenas referências, nunca prints do jogo).
7. Terreno de 2 km² preparado em `D:\ProjectResort_Autonomy\Map2km2_Staging` com QA de dados 13/13, mas ainda precisa ser validado e aplicado na cena Unity. Não confundir com 900×720 m ainda no runtime principal.
8. Codex VRBN: 39/234 prédios integrados na escala antiga, último PlayMode 31/31. 195 construções ainda precisam de modelos coerentes, sem repetição e sem colisões problemáticas.

## Fontes abertas e comprovadas
- https://3dassets.dev/packs/hotel-and-resort-operations
- https://3dassets.dev/packs/waterpark-and-pool-operations
- https://3dassets.dev/packs/restaurant-kitchen-and-dining
- https://3dassets.dev/packs/bakery-and-cafe
- https://3dassets.dev/packs/beach-surf-and-paddle-kit
- https://3dassets.dev/packs/public-swimming-baths-and-poolside
- https://3dassets.dev/packs/fitted-kitchen-and-bathroom-builder
- https://3dassets.dev/packs/bar-pub-and-brewery-taproom
- https://3dassets.dev/packs/gym-and-fitness-studio
- https://3dassets.dev/packs/office-lobby-and-facilities
- https://www.innerscene.com/tools/library/3d-parts/desk-with-chair-original-hotel-furnishing-8302c2bb
- https://polyhaven.com

## Resultado
**DOWNLOADS DOS 959 NOVOS ITENS COMPLETOS (QA 0 erros)**. Cobertura de cenografia funcional muito melhor; a qualidade visual final e a integração jogável NÃO estão concluídas e exigem triagem, shaders/texturas, modelagem própria das piscinas, animações e testes. Não anunciar jogo pronto.
