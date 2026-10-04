# WORLD BIBLE v1 — SANTA AURORA

**Status:** fundação espacial oficial para produção do mundo grande  
**Escala:** metros reais / origem (0,0) no eixo cívico de Santa Aurora  
**Extensão reservada:** X -4000..4000 m / Z -4000..4000 m  
**Área total reservada:** 64 km²  
**Regra:** este documento substitui as coordenadas pequenas do protótipo apenas para a produção futura do mundo. O catálogo runtime atual permanece intacto até a migração controlada.

---

## 1. Filosofia espacial

Santa Aurora precisa funcionar como uma cidade antes de funcionar como uma coleção de missões.

A posição de cada local deve responder a quatro perguntas:

1. por que esse prédio existe aqui?
2. como o jogador chega nele?
3. quais sistemas urbanos o conectam ao restante da cidade?
4. quais eventos da história dependem dessa geografia?

O mundo final deve permitir que o jogador reconheça bairros, memorize rotas, tenha motivos para comprar veículos e perceba fisicamente sua ascensão econômica.

---

## 2. Macrogeografia

### Limites

- Oeste: zona ferroviária antiga, terrenos de manutenção e acesso ao porto seco.
- Leste: expansão tecnológica e novos empreendimentos.
- Sul: bairros residenciais e eixo de expansão urbana.
- Norte: distrito industrial, drenagem e infraestrutura pesada.
- Centro: Santa Aurora Central e conexões metropolitanas.

### Topografia

**Revisão W1.5 (decisão do usuário):** a cidade escoa para o **canal de drenagem, que é o eixo mais baixo** (cota de cerca de 3 m). A antiga indicação "sul e sudoeste: cota mais baixa" fica substituída. Implementação: `Tools/Map/sa_terrain.py`.

- Canal de drenagem: norte-oeste → centro-norte, com leito e taludes. A casa de bombas fica no ponto baixo junto ao canal, ao lado de uma bacia de retenção murada.
- O terreno sobe gradualmente com a distância do canal, até cerca de 20–25 m.
- Cidade Antiga: colina suave (Alto do Horizonte), núcleo histórico em ligeira elevação junto à ferrovia.
- Nordeste: platô tecnológico (+16 m), com borda em talude suave.
- Norte industrial: terrenos amplos e baixos, perto do canal.
- Expansão: sobe suavemente para o sul.
- Rampas viárias ≤ 6% nas arteriais e ≤ 8% nas coletoras (dirigibilidade).
- Não criar montanhas artificiais dominantes; o relevo é urbano e funcional.

---

## 3. Distritos oficiais

| ID | Distrito | Centro aproximado | Faixa espacial | Papel |
|---|---|---:|---|---|
| old | Cidade Antiga | (-2350,-1900) | X -3800..-900 / Z -3400..-500 | início, comércio local, edifícios envelhecidos |
| expansion | Cinturão da Expansão | (0,-2100) | X -1200..1500 / Z -3600..-700 | condomínios, escola, hotel, sede futura |
| civic | Santa Aurora Central | (0,450) | X -1100..1100 / Z -700..1600 | administração, infraestrutura municipal, conexão de vias |
| corporate | Zona Empresarial | (2350,-150) | X 1200..3800 / Z -1600..1300 | torres, shopping, Vértice, hospital crítico |
| industrial | Distrito Industrial | (-2350,1950) | X -3900..-900 / Z 500..3600 | fábricas, logística, drenagem, infraestrutura pesada |
| technology | Distrito Tecnológico | (2300,2350) | X 900..3900 / Z 1100..3800 | data center, automação, edifícios inteligentes |

Áreas entre distritos não são vazios técnicos: recebem vias, terrenos, vegetação, postos, bairros de transição e infraestrutura.

---

## 4. Corredores viários principais

### R01 — Avenida Santa Aurora
- arterial leste-oeste;
- do acesso ferroviário da Cidade Antiga até o Distrito Tecnológico;
- aproximadamente 7,2 km;
- 2×2 faixas nos trechos centrais;
- conecta old → civic → corporate/technology.

### R02 — Avenida do Trabalho
- eixo norte-sul do lado oeste;
- conecta Cidade Antiga ao Distrito Industrial;
- tráfego de utilitários e caminhões;
- passa próximo de Oficina Aurora e Galpão Logístico.

### R03 — Avenida das Palmeiras
- eixo sul-centro;
- conecta Cinturão da Expansão a Santa Aurora Central;
- condomínios, escola, hotel e serviços.

### R04 — Via Tecnológica
- radial civic → technology;
- vias largas, canteiro central, infraestrutura nova.

### R05 — Anel Norte
- conecta industrial → civic norte → technology;
- principal rota de cargas e infraestrutura.

### R06 — Eixo Empresarial
- conecta civic → corporate;
- torres, shopping, hospital 03:17 e Vértice.

### R07 — Estrada do Porto Seco
- oeste;
- logística, ferrovia e terrenos de baixa densidade.

### R08 — Marginal do Canal
- acompanha drenagem ao norte;
- acesso operacional à casa de bombas e eventos da tempestade.

### R09 — Avenida dos Ferroviários (W1.5)
- arterial leste-oeste ao sul;
- liga Cidade Antiga, Expansão e Expansão Leste (correção do bloqueio W1: o desvio até a escola caiu de 3,4× para 1,1×).

### R10 — Avenida Leste (W1.5)
- coletora norte-sul entre a Expansão Leste (R09) e o Eixo Empresarial (R06).

### Rotatórias (W1.5)
- Rotatória da Central (R01/R03/R06) e Rotatória Tecnológica (R04/R05/R08).

### Ferrovia histórica (W1.5)
- Linha Ferroviária Oeste, paralela à R07: porto seco (sul), Estação Velha (Cidade Antiga), ramal da logística, fábrica (Industrial).

### Zonas de transição (W1.5)
- 8 zonas no spec (`transitionZones`), preenchendo os vazios entre distritos (ver `Docs/W1_5_WORLD_FOUNDATION_RELATORIO.md`).

---

## 5. Locais da campanha — coordenadas de produção

As coordenadas abaixo são âncoras macro. A implantação fina será ajustada durante o blockout métrico, mas os bairros e relações espaciais devem ser preservados.

| ID | Local | Distrito | X | Z | Footprint inicial | Prioridade |
|---|---|---|---:|---:|---|---|
| garage | Oficina Aurora / garagem original | old | -2700 | -2150 | 32×38 m | HERO |
| horizonte | Edifício Horizonte | old | -2350 | -1800 | 42×55 m | HERO |
| apartments | Apartamentos do bairro antigo | old | -3050 | -1550 | 48×62 m | A |
| grocery | Mercearia do bairro | old | -2580 | -1480 | 28×36 m | A |
| restaurant | Restaurante em crescimento | old | -2140 | -1420 | 34×42 m | A |
| workshop | Oficina local | old | -3200 | -2050 | 45×58 m | B |
| smalloffice | Pequeno escritório | old | -1850 | -1900 | 38×44 m | B |
| imperial | Teatro Imperial | old | -2050 | -2650 | 78×96 m | HERO |
| school | Escola pública | expansion | -500 | -2450 | 100×125 m | A |
| recurringcondo | Condomínio indicado por Helena | expansion | 350 | -2150 | 145×180 m | HERO |
| lostcondo | Condomínio do contrato perdido | expansion | 950 | -1800 | 160×200 m | A |
| hotel | Hotel em reforma | expansion | 600 | -2950 | 95×120 m | HERO |
| smallhospital | Hospital pequeno | expansion | -250 | -1250 | 115×145 m | HERO |
| companyhq | Sede expandida do jogador | expansion | 1100 | -2650 | 125×150 m | HERO |
| mall | Shopping | corporate | 2050 | -500 | 230×260 m | HERO |
| hospital0317 | Hospital / ocorrência 03:17 | corporate | 2850 | -900 | 175×220 m | HERO |
| blackouttower | Torre empresarial / apagão | corporate | 3000 | 350 | 95×110 m | HERO |
| vertice | Vértice Serviços Integrados | corporate | 1900 | 450 | 120×150 m | HERO |
| logistics | Galpão logístico | industrial | -3150 | 1650 | 240×290 m | A |
| factory | Fábrica | industrial | -2200 | 2450 | 300×340 m | HERO |
| drainage | Casa de bombas / drenagem | industrial | -1130 | 3070 | 130×160 m | HERO |
| datacenter | Data center | technology | 2450 | 2600 | 190×230 m | HERO |
| smarttower | Edifício inteligente | technology | 3150 | 1850 | 110×130 m | HERO |
| central | Santa Aurora Central | civic | 0 | 650 | 360×420 m | SUPER-HERO |

---

## 6. Novos locais necessários para a vida do jogador

Estes locais não substituem os 24 da campanha. Eles sustentam economia, patrimônio e lazer.

| ID planejado | Local | Distrito | X | Z | Função |
|---|---|---|---:|---:|---|
| home.starter | Kitnet inicial | old | -2860 | -2280 | lar inicial |
| home.apartment.01 | Apartamento compacto | expansion | -750 | -1850 | primeiro imóvel melhor |
| home.apartment.02 | Apartamento com garagem | expansion | 150 | -3150 | patrimônio intermediário |
| home.house.01 | Casa pequena | expansion | 1050 | -3350 | garagem/oficina |
| home.house.02 | Casa com oficina | old/transition | -1350 | -3250 | patrimônio avançado |
| home.premium.01 | Residência premium | technology | 3300 | 3200 | endgame opcional |
| supplier.tools | Loja de ferramentas | old | -2480 | -2320 | ferramentas iniciais |
| supplier.parts | Distribuidora técnica | industrial | -1700 | 1200 | peças maiores |
| supplier.electrical | Casa elétrica | old | -1800 | -2350 | elétrica |
| supplier.hydraulic | Hidráulica Santa Aurora | expansion | -850 | -2850 | hidráulica |
| vehicles.used | Revenda de usados | old | -3400 | -2550 | primeiro veículo |
| vehicles.commercial | Veículos comerciais | expansion | 1250 | -3050 | utilitários/vans |
| fuel.old | Posto Cidade Antiga | old | -1550 | -900 | combustível/serviço |
| fuel.north | Posto Anel Norte | industrial | -1350 | 900 | combustível |
| leisure.cafe | Café do bairro | old | -2450 | -1700 | NPC/social |
| leisure.gym | Academia | expansion | 900 | -2350 | lazer |
| leisure.cinema | Cinema / centro cultural | corporate | 1650 | -250 | lazer |
| leisure.park | Parque municipal | civic | -650 | 1050 | lazer/exploração |
| leisure.fishing | Parque linear do canal | industrial/civic | -850 | 2200 | pesca/fotografia |
| property.agency | Imobiliária Santa Aurora | expansion | -200 | -2050 | compra de imóveis |

---

## 7. Estruturas visuais de fundo

Além de locais visitáveis, cada distrito precisa de shells que deem escala.

### Cidade Antiga
- 120–180 shells de baixa/média altura;
- 2–6 pavimentos;
- fachadas comerciais no térreo;
- sobrados;
- armazéns antigos;
- oficinas;
- depósitos;
- cortiços/reformas.

### Expansão
- 80–120 shells;
- 4–14 pavimentos;
- condomínios;
- escolas privadas de fundo;
- comércio de avenida;
- estacionamentos;
- clínicas.

### Corporate
- 45–70 shells;
- 8–35 pavimentos;
- torres comerciais;
- hotéis;
- estacionamentos;
- edifícios mistos.

### Industrial
- 50–80 grandes volumes;
- galpões;
- pátios;
- tanques;
- subestações;
- ferrovias;
- silos e estruturas técnicas.

### Technology
- 35–60 shells;
- campus;
- torres;
- laboratórios;
- data centers;
- edifícios novos.

### Civic
- 30–50 shells;
- administração;
- prédios públicos;
- terminal;
- praças;
- estacionamento.

Esses números são metas de composição, não obrigação de criar centenas de hero assets únicos.

---

## 8. Alturas e skyline

### Cidade Antiga
- predominância 2–6 pavimentos;
- Horizonte pode se destacar com ~12 pavimentos;
- Teatro Imperial como marco horizontal.

### Expansão
- 5–16 pavimentos;
- condomínios formam skyline intermediário.

### Corporate
- 12–35 pavimentos;
- skyline mais vertical.

### Technology
- 8–28 pavimentos;
- volumes modernos e campus.

### Industrial
- baixa altura geral, mas com chaminés, silos, pórticos e torres técnicas.

### Central
- conjunto monumental técnico, não necessariamente a torre mais alta.

---

## 9. Estruturas finais dos locais principais

### Edifício Horizonte
- ~12 pavimentos visíveis;
- garagem térrea/subsolo;
- lobby;
- corredores residenciais;
- shaft;
- casa de bombas;
- reservatório/cobertura;
- quadro geral;
- portão/interfone;
- apenas pavimentos relevantes precisam ser totalmente interiores.

### Teatro Imperial
- foyer;
- plateia;
- palco;
- bastidores;
- cabine;
- subsolo técnico;
- cobertura/HVAC;
- elétrica antiga.

### Condomínio Helena
- 2 torres residenciais;
- portaria;
- garagem;
- casa de bombas;
- reservatórios;
- quadro;
- área comum;
- cobertura técnica.

### Hotel
- 8–12 pavimentos visíveis;
- lobby;
- corredor/hóspedes amostral;
- lavanderia;
- bombas;
- água quente;
- HVAC;
- cobertura.

### Hospitais
- múltiplas alas;
- doca/entrada técnica;
- energia;
- HVAC;
- bombas;
- gerador;
- áreas críticas;
- rotas de serviço independentes do público.

### Fábrica
- pátio;
- produção;
- oficina;
- utilidades;
- bombas;
- sala elétrica;
- HVAC;
- docas;
- circulação de serviço.

### Data center
- controle de acesso;
- racks;
- corredores frio/quente;
- energia A/B;
- UPS abstrata;
- refrigeração;
- telecom;
- operação.

### Santa Aurora Central
- campus de 360×420 m;
- múltiplos edifícios conectados;
- centro administrativo;
- monitoramento;
- data center municipal;
- telecom;
- centro de emergência;
- distribuição elétrica;
- geradores;
- bombas/drenagem;
- HVAC;
- automação;
- túneis/corredores de serviço;
- pátio final.

---

## 10. Interiores

Regra de produção:

- não modelar todos os apartamentos/quartos/escritórios;
- modelar áreas necessárias à campanha e áreas representativas;
- portas fechadas e shells devem ser coerentes;
- nenhum prédio hero deve parecer oco;
- serviços podem reutilizar unidades internas por variantes, mas a repetição precisa ser mascarada.

---

## 11. Células de streaming

### Macrogrid
8×8 células de 1 km².

Convenção:
- SA_M00_00 até SA_M07_07.

### Subgrid
Cada macro célula:
- 4×4 subcélulas de 250×250 m.

Convenção:
- SA_M03_02_S01_03.

### Conteúdo separado
- Terrain
- Roads
- Architecture
- Props
- Vegetation
- Infrastructure
- Audio
- Lighting
- Gameplay anchors

---

## 12. Distâncias de streaming iniciais

Valores a validar, não definitivos:

- célula completa ativa: ~500–750 m ao redor do jogador;
- HLOD de bairro: 750–1800 m;
- skyline/proxy: 1800–4000 m;
- interiores hero: carregar por portal/proximidade;
- props pequenos: culling por distância.

---

## 13. Requisitos para dirigir

Todas as arteriais devem ser projetadas para:

- largura real;
- raio de curva compatível;
- cruzamentos;
- retorno;
- estacionamento;
- áreas de carga;
- entradas de garagem;
- navegação futura de tráfego.

Mesmo antes da dirigibilidade, o blockout precisa respeitar isso.

---

## 14. Ordem de construção do mundo

### W0 — Spec
- esta World Bible;
- coordenadas;
- footprint;
- corredores.

### W1 — Masterplan Blender
- terreno 8×8 km;
- vias arteriais;
- limites de distritos;
- volumes de skyline;
- 24 locais da campanha;
- 20 locais de vida/economia.

### W2 — Cidade Antiga blockout de produção
- ruas completas;
- quarteirões;
- shells;
- lar;
- Oficina Aurora;
- Horizonte;
- primeiros clientes;
- Teatro.

### W3 — Kit visual
- materiais PBR;
- arquitetura modular;
- infraestrutura;
- props técnicos;
- decals.

### W4 — Cidade Antiga high fidelity
- exterior;
- interiores;
- iluminação;
- clutter;
- vegetação;
- LOD.

### W5 — Vertical slice
- gameplay;
- economia;
- trabalhos;
- veículo;
- casa evolutiva.

### W6+ — demais distritos
- Expansão;
- Industrial;
- Corporate;
- Technology;
- Civic/Central.

---

## 15. Regra de história

Antes de modelar definitivamente qualquer hero location:

- identificar capítulos em que aparece;
- listar eventos que ocorrerão;
- reservar setores e acessos necessários;
- registrar estados "antes/depois";
- prever consequências persistentes.

Assim evitamos reconstruir prédios para acomodar missões futuras.

---

## 16. Regra de patrimônio

Todo imóvel comprável precisa ter:

- endereço físico;
- vaga/garagem;
- interior;
- estado vazio;
- estados de mobiliário;
- pontos de upgrade;
- custos;
- valor de revenda;
- presença persistente na cidade.

---

## 17. Gate W1 — Masterplan aprovado

O Masterplan só passa quando houver:

- footprint 8×8 km;
- seis distritos legíveis;
- oito corredores viários;
- 24 locais da campanha posicionados;
- locais de vida/economia posicionados;
- skyline preliminar;
- distâncias plausíveis;
- acesso viário de todos os hero locations;
- nenhuma sobreposição impossível;
- screenshots reais do Blender;
- arquivo .blend reabrível;
- escala métrica confirmada.

---

## 18. Próximo trabalho após esta Bible

**Não criar mais missões antes de W1.**

Próxima tarefa recomendada:

> reconstruir `SantaAurora_Masterplan.blend` seguindo esta World Bible, primeiro como masterplan métrico de alta escala, sem ainda gastar tempo com interiores ou acabamento final.

