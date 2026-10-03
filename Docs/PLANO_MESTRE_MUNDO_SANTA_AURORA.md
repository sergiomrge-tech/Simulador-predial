# PLANO MESTRE — MUNDO GRANDE DE SANTA AURORA

**Projeto:** Facility Ops / Simulador Predial  
**Status:** planejamento oficial de produção  
**Engine:** Unity 6000.6.2f1 / URP / C# / primeira pessoa  
**Objetivo:** transformar Santa Aurora em uma cidade grande, coerente, explorável e preparada para anos de expansão de conteúdo.

---

# 1. Princípio central

Santa Aurora não pode parecer uma sequência de mapas pequenos desconectados.

O projeto passa a adotar como regra:

> **Santa Aurora deve ser percebida como uma cidade grande, contínua e funcional, com bairros, vias, imóveis, áreas industriais, infraestrutura e distância suficiente para justificar veículos, patrimônio, logística e escolha de onde trabalhar.**

Mesmo que a produção seja realizada por setores e cenas carregadas por streaming, a experiência do jogador deve transmitir um único mundo coerente.

---

# 2. Meta de escala

## 2.1. Footprint planejado

Meta de planejamento para a área metropolitana principal:

- **8 km × 8 km de footprint máximo planejado**;
- aproximadamente **64 km² de território reservado**;
- não significa 64 km² com densidade urbana uniforme;
- parte da área será composta por:
  - bairros densos;
  - bairros residenciais;
  - áreas industriais;
  - vias arteriais;
  - zonas verdes;
  - terrenos;
  - drenagem;
  - infraestrutura;
  - áreas de expansão.

O objetivo não é preencher cada metro com conteúdo, mas criar distância, geografia e escala real suficientes para o jogador sentir que se desloca por uma cidade.

## 2.2. Área de alta densidade

Meta:

- aproximadamente **20–30 km² com conteúdo urbano significativo** ao longo do desenvolvimento;
- áreas restantes funcionam como transição, infraestrutura, paisagem, vias e reserva de expansão.

## 2.3. Regra de produção

Nunca construir os 64 km² em qualidade final de uma vez.

Produção em camadas:

1. footprint;
2. macrogeografia;
3. malha viária;
4. massas urbanas;
5. hero locations;
6. interiores importantes;
7. clutter e acabamento;
8. otimização.

---

# 3. Comparação de referência e alvo visual

VEIN é utilizado como **referência de patamar visual, atmosfera e densidade**, não como fonte para cópia.

A página oficial do VEIN descreve um mundo aberto e a intenção dos desenvolvedores de expandir o mapa para 14 × 14 km. Isso serve apenas para reforçar que uma sensação de grande escala é compatível com a referência visual escolhida; Santa Aurora terá geografia e escopo próprios.

## Regras visuais oficiais

### Proibido como direção final

- low-poly evidente;
- geometria excessivamente simples;
- prédios em forma de caixas sem acabamento;
- paredes e terrenos sem microvariação;
- materiais flat;
- texturas genéricas repetidas em excesso;
- interiores vazios;
- fachadas repetidas sem identidade;
- assets de protótipo visíveis na versão de produção.

### Obrigatório para a direção final

- proporções realistas;
- materiais PBR;
- normal maps;
- roughness coerente;
- decals;
- sujeira localizada;
- desgaste;
- imperfeições;
- variação de superfícies;
- iluminação atmosférica;
- clutter funcional;
- vegetação coerente;
- objetos técnicos realistas;
- interiores densos quando visitáveis;
- diferenciação visual entre bairros.

### Observação importante

O objetivo é atingir uma **linguagem visual comparável em realismo e atmosfera ao VEIN**, sem copiar literalmente:

- modelos;
- texturas;
- edifícios;
- ruas;
- layouts;
- personagens;
- interface;
- identidade artística exclusiva.

Santa Aurora deve ser visualmente própria.

---

# 4. Estrutura macro de Santa Aurora

A cidade continua organizada nos 6 distritos já definidos pelo projeto.

Cada distrito precisa possuir escala, arquitetura, economia e tipos de trabalho próprios.

---

# 5. Distrito 1 — Cidade Antiga

## Papel

Área inicial e mais histórica.

## Dimensão planejada

Aproximadamente:

- 1,6 km × 1,8 km de área urbana principal;
- ruas menores;
- quarteirões irregulares;
- alta densidade de pequenos imóveis.

## Identidade

- construções antigas;
- lojas de rua;
- apartamentos;
- edifícios mistos;
- pequenos estacionamentos;
- oficinas;
- postes;
- instalações técnicas de épocas diferentes;
- adaptações e reformas antigas.

## Locais principais

- lar inicial do protagonista;
- Oficina Aurora;
- Edifício Horizonte;
- apartamentos do bairro antigo;
- mercearia;
- restaurante;
- oficina local;
- pequeno escritório;
- Teatro Imperial.

## Função

É o primeiro vertical slice de qualidade comercial.

---

# 6. Distrito 2 — Cinturão da Expansão

## Dimensão planejada

Aproximadamente:

- 2 km × 2 km;
- avenidas maiores;
- condomínios;
- escolas;
- hotelaria;
- zonas residenciais intermediárias.

## Identidade

- urbanização mais nova;
- edifícios de médio porte;
- garagem subterrânea;
- áreas técnicas padronizadas;
- reservatórios;
- bombas;
- portarias;
- condomínios fechados.

## Locais principais

- Condomínio indicado por Helena;
- Condomínio do contrato perdido;
- Escola pública;
- Hotel em reforma;
- Hospital pequeno;
- futura sede expandida.

---

# 7. Distrito 3 — Industrial

## Dimensão planejada

Aproximadamente:

- 2,5 km × 2 km;
- quarteirões grandes;
- vias largas;
- pátios;
- ferrovias/logística quando coerente.

## Identidade

- galpões;
- docas;
- fábricas;
- tanques;
- tubulações;
- bombas;
- painéis de grande porte;
- subestações;
- geradores;
- drenagem;
- telecom.

## Locais principais

- galpão logístico;
- fábrica;
- casa de bombas/drenagem.

---

# 8. Distrito 4 — Centro urbano

## Papel

Concentração de prédios maiores, comércio e infraestrutura de serviços.

## Identidade

- avenidas;
- prédios comerciais;
- estacionamentos verticais;
- lojas;
- escritórios;
- shopping;
- edificações mais modernas;
- maior densidade vertical.

---

# 9. Distrito 5 — Saúde / tecnologia / infraestrutura crítica

## Identidade

- hospital de maior porte;
- data center;
- prédios técnicos;
- subestações;
- redundância;
- automação;
- geradores;
- UPS;
- climatização crítica.

Essa região representa o salto do jogador para contratos premium.

---

# 10. Distrito 6 — Santa Aurora Central / endgame

Área de maior complexidade técnica.

## Deve incluir

- Santa Aurora Central;
- infraestrutura urbana crítica;
- redes interdependentes;
- grandes bombas;
- energia;
- telecom;
- automação;
- geradores;
- drenagem;
- setores de emergência.

É o palco ideal para a crise final "Cascata".

---

# 11. Rede viária

O mapa grande só funciona se a circulação fizer sentido.

## Hierarquia

### Vias arteriais

- conectam distritos;
- trânsito mais rápido;
- postos;
- cruzamentos grandes;
- acesso industrial.

### Vias coletoras

- conectam bairros às arteriais.

### Vias locais

- residenciais;
- comerciais;
- estacionamento;
- acesso a clientes.

### Acessos técnicos

- docas;
- estacionamentos;
- entradas de serviço;
- rampas;
- becos;
- portões;
- áreas de carga.

---

# 12. Deslocamento

## Fase inicial

Pode usar transições controladas entre setores para acelerar produção.

## Fase intermediária

Veículos fisicamente presentes:

- sair da residência;
- entrar no veículo;
- viajar;
- estacionar no cliente.

## Fase avançada

Dirigibilidade entre regiões onde for tecnicamente e economicamente viável.

## Regra

A arquitetura do mapa deve ser preparada desde o início para condução, mesmo se a primeira versão usar deslocamento simplificado.

---

# 13. Tamanho de ruas e escala

Referências internas de produção:

- faixa de carro: ~3,0–3,5 m;
- rua residencial: ~6–8 m;
- avenida: ~14–28 m;
- calçada: ~1,5–4 m;
- pé-direito residencial: ~2,6–3 m;
- técnico/comercial: ~3–5 m;
- galpão: 6–12+ m.

Toda modelagem deve manter escala métrica real.

---

# 14. Grid de produção e streaming

Para suportar mundo grande na Unity, o mapa será dividido tecnicamente.

## Estrutura sugerida

### Macro células

- células de **1 km × 1 km** para organização de mundo.

### Subcélulas

- aproximadamente **250 m × 250 m** para streaming e detalhe.

## Cada subcélula pode conter

- terreno;
- ruas;
- construções externas;
- props;
- vegetação;
- iluminação local;
- pontos de interesse.

## Hero locations

Interiores grandes ou complexos podem ser cenas adicionais carregadas sob demanda.

---

# 15. Streaming na Unity

Direção técnica proposta:

- cenas aditivas;
- Addressables quando necessário;
- carregamento por distância;
- descarregamento de células distantes;
- LOD Groups;
- GPU instancing;
- occlusion culling;
- light probes;
- reflection probes;
- interiores separados;
- pooling de objetos recorrentes.

Evitar uma única cena gigantesca contendo a cidade inteira.

---

# 16. LOD e HLOD

## Regras

Todo asset exterior relevante deve ter:

- LOD0;
- LOD1;
- LOD2;
- proxy distante quando necessário.

Prédios maiores devem possuir proxy/HLOD de quarteirão quando distantes.

## Importante

LOD não significa visual low-poly próximo.

O jogador nunca deve perceber uma geometria grosseira em distância de inspeção.

---

# 17. Arquitetura modular sem parecer modular

Criar kit modular no Blender.

## Exterior

- paredes;
- quinas;
- fachadas;
- janelas;
- portas;
- telhados;
- beirais;
- grades;
- portões;
- fundações;
- marquises;
- calhas;
- caixas técnicas;
- tubulações.

## Regra

As peças modulares precisam receber:

- variação de material;
- decals;
- sujeira;
- danos;
- elementos únicos;
- signage;
- props.

A repetição não pode ser óbvia.

---

# 18. Biblioteca de materiais

Criar uma biblioteca PBR própria.

## Categorias

- concreto;
- reboco;
- tijolo;
- asfalto;
- metal galvanizado;
- aço pintado;
- ferrugem;
- madeira;
- plástico;
- cerâmica;
- vidro;
- borracha;
- alumínio;
- pintura industrial.

## Variações

Cada material relevante deve possuir múltiplas variações.

---

# 19. Decals

Sistema de decals é obrigatório.

## Tipos

- infiltração;
- mofo;
- ferrugem;
- óleo;
- poeira;
- rachadura;
- tinta reparada;
- numeração;
- aviso;
- etiquetas;
- marcas de manutenção;
- piso desgastado;
- marcas de pneu.

---

# 20. Terreno

O terreno não deve parecer um plano com ruas colocadas em cima.

## Necessário

- variação de altura;
- taludes;
- drenagem;
- sarjetas;
- terrenos vazios;
- vegetação;
- barrancos;
- canais;
- muros de contenção;
- áreas pavimentadas;
- transições naturais.

---

# 21. Clima e iluminação

Planejar suporte futuro para:

- manhã;
- tarde;
- noite;
- chuva;
- neblina leve;
- tempo nublado;
- pós-chuva;
- iluminação urbana.

A iluminação precisa reforçar o realismo.

---

# 22. Edifícios visitáveis

Nem todo prédio terá interior completo.

## Nível A — Hero

Interior detalhado e visitável.

## Nível B — Gameplay

Somente áreas relevantes à manutenção.

## Nível C — Shell

Exterior realista, interior indisponível.

## Nível D — Background

Apenas composição urbana distante.

---

# 23. Hero locations obrigatórios

Ao longo da produção:

- lar inicial;
- Oficina Aurora;
- Edifício Horizonte;
- condomínio de Helena;
- Teatro Imperial;
- hospital;
- hotel;
- fábrica;
- casa de bombas;
- data center;
- Vértice;
- Santa Aurora Central.

---

# 24. Lar do protagonista

O lar inicial deve ser um dos cenários mais detalhados.

## Regras

- totalmente visitável;
- objetos pessoais;
- móveis;
- cozinha;
- banheiro;
- cama;
- PC/TV futuros;
- ferramentas;
- roupa;
- documentos;
- armazenamento;
- vista exterior coerente com o bairro.

## Evolução

O lar muda fisicamente conforme compras.

Mais tarde, o personagem pode comprar:

- apartamento compacto;
- apartamento com garagem;
- apartamento maior;
- casa;
- casa com oficina;
- residência premium.

Os imóveis antigos continuam existentes fisicamente na cidade.

---

# 25. Oficina Aurora

Deve começar pequena e plausível.

## Evolução

- bancada;
- estoque;
- ferramentas;
- depósito;
- escritório;
- veículos;
- equipe.

Mais tarde a empresa pode mudar para sede maior.

---

# 26. Estacionamentos e veículos

Todo local importante deve considerar:

- onde o jogador estaciona;
- acesso de serviço;
- carga/descarga;
- garagem;
- veículo de cliente;
- veículo técnico.

Isso deve ser definido na planta antes da modelagem final.

---

# 27. Infraestrutura urbana visível

Santa Aurora precisa parecer uma cidade técnica.

Adicionar de maneira coerente:

- postes;
- caixas;
- transformadores;
- hidrantes;
- bocas de lobo;
- redes de drenagem;
- caixas de telecom;
- antenas;
- câmeras;
- placas;
- semáforos;
- iluminação pública;
- medidores;
- válvulas;
- tampas técnicas.

---

# 28. Interiores técnicos

O diferencial visual do jogo está aqui.

## Exemplos

- casa de bombas;
- sala elétrica;
- quadro geral;
- geradores;
- HVAC;
- sala de máquinas;
- telecom;
- shaft;
- cobertura;
- reservatório;
- sala de incêndio.

Esses ambientes devem receber qualidade igual ou superior aos interiores comuns.

---

# 29. História ambiental

Cada hero location deve contar história sem texto.

## Exemplos

- reparos antigos;
- etiquetas;
- peças substituídas;
- improvisos;
- marcas de vazamento;
- relatórios;
- datas;
- ferramentas esquecidas;
- equipamento desativado.

---

# 30. População visual futura

Planejar espaço para:

- pedestres;
- clientes;
- NPCs;
- carros estacionados;
- tráfego;
- funcionários.

Não é necessário implementar tudo na primeira etapa, mas o layout não pode impedir isso.

---

# 31. Pipeline Blender → Unity

## Blender

Responsável por:

- masterplan;
- arquitetura;
- kit modular;
- props;
- hero assets;
- UV;
- LOD;
- colisões quando aplicável.

## Unity

Responsável por:

- composição final;
- materiais URP;
- decals;
- iluminação;
- streaming;
- gameplay;
- física;
- NPCs;
- otimização.

---

# 32. Estrutura de arquivos sugerida

ArtSource/Blender/World/
- Masterplan/
- Districts/
- Buildings/
- Residential/
- Industrial/
- Infrastructure/
- HeroLocations/
- Interiors/
- Props/
- Vehicles/
- Materials/

Unity:
Assets/_Game/World/
- Streaming/
- Districts/
- Streets/
- Buildings/
- HeroLocations/
- Interiors/
- Infrastructure/
- Props/

---

# 33. IDs permanentes

Todo local jogável deve possuir ID estável.

Não usar nome visual como identificador de save.

Exemplo:

- world.cityold.block.001
- world.horizonte.main
- world.home.starter
- world.aurora.office
- world.recurringcondo.main

---

# 34. Ordem de modelagem

## Etapa 1 — World Foundation

- relevo macro;
- footprint 8×8 km;
- distritos;
- vias arteriais;
- quarteirões;
- posição dos 24 locais atuais;
- reserva de novos locais.

## Etapa 2 — Cidade Antiga

- malha completa;
- residência inicial;
- oficina;
- Horizonte;
- primeiros clientes;
- Teatro.

## Etapa 3 — Vertical Slice

Finalizar visual e gameplay da Cidade Antiga.

## Etapa 4 — Cinturão da Expansão

- condomínios;
- escola;
- hospital;
- hotel;
- sede maior.

## Etapa 5 — Industrial

- galpões;
- fábrica;
- drenagem.

## Etapa 6 — Centro/infraestrutura crítica

- hospital maior;
- shopping;
- data center;
- Vértice.

## Etapa 7 — Santa Aurora Central

Endgame.

---

# 35. Gate visual

Nenhuma área passa para "final" se apresentar:

- geometria de blockout exposta;
- materiais provisórios;
- aparência low-poly;
- iluminação plana;
- interiores vazios;
- escala inconsistente;
- repetição modular óbvia.

---

# 36. Gate funcional

Todo hero location precisa ter:

- acesso;
- estacionamento;
- rota de serviço;
- áreas técnicas;
- colisão;
- navegação;
- pontos de interação;
- save IDs;
- conexão com campanha.

---

# 37. Gate de performance

Meta provisória para PC:

- 1080p;
- 60 FPS em hardware-alvo definido futuramente;
- frame time estável;
- streaming sem travamento perceptível;
- memória monitorada.

A qualidade visual não será reduzida para low-poly. Otimização deve ocorrer através de:

- LOD;
- HLOD;
- occlusion;
- streaming;
- instancing;
- atlas;
- redução de draw calls;
- bake seletivo.

---

# 38. Escopo visual por distância

## Próximo do jogador

Máximo detalhe.

## Quarteirão

LOD intermediário.

## Bairro distante

HLOD/proxy.

## Skyline

silhuetas e proxies.

Isso permite mundo grande sem sacrificar o padrão visual local.

---

# 39. Vertical slice obrigatório antes de escalar acabamento

A Cidade Antiga precisa provar:

- qualidade visual;
- performance;
- trânsito futuro;
- interior/exterior;
- fluxo de trabalho;
- lar;
- oficina;
- economia;
- chamadas;
- veículo.

Somente depois desse padrão aprovado ele será replicado nos outros distritos.

---

# 40. Meta de densidade

O mapa grande não pode ser vazio.

A cada zona urbana, deve haver:

- fachadas;
- entradas;
- quintais;
- veículos;
- postes;
- caixas técnicas;
- vegetação;
- sinalização;
- lixo/objetos;
- manutenção;
- pequenas histórias ambientais.

Áreas vazias só existem quando justificadas pela geografia.

---

# 41. Conteúdo emergente futuro

O mundo deve estar preparado para:

- chamados aleatórios;
- eventos meteorológicos;
- falhas locais;
- аварias de energia;
- alagamentos;
- emergências;
- obras;
- novos imóveis;
- novos clientes.

---

# 42. Expansão pós-lançamento

A reserva territorial do footprint permite adicionar:

- novos bairros;
- bairros rurais/periféricos;
- aeroporto;
- universidade;
- centros comerciais;
- grandes condomínios;
- infraestrutura pública.

---

# 43. Prioridade de produção atual

A partir deste planejamento, a prioridade recomendada é:

1. consolidar a World Bible;
2. transformar SantaAurora_Masterplan.blend em masterplan métrico;
3. definir footprint 8×8 km;
4. fechar posição e dimensão dos distritos;
5. construir malha viária principal;
6. posicionar todos os locais da campanha;
7. criar kit arquitetônico PBR;
8. criar kit técnico;
9. produzir Cidade Antiga;
10. produzir lar inicial;
11. produzir Oficina Aurora;
12. produzir Horizonte e primeiros clientes;
13. validar vertical slice;
14. só então expandir acabamento para demais distritos.

---

# 44. Regra final de direção

**Santa Aurora deve ser grande, realista, densa e tecnicamente crível.**

O jogador deve sentir que:

- trabalha em uma cidade de verdade;
- precisa se deslocar;
- escolhe regiões;
- cresce financeiramente;
- compra imóveis;
- compra veículos;
- muda de vida;
- conhece os bairros;
- cria histórico profissional nos prédios.

**Blockout é permitido apenas durante produção. Low-poly não é aceito como estilo final.**
