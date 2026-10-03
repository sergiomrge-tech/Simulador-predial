# Estrutura de Santa Aurora

Fonte: LORE_CAMPANHA_ORIGINAL.md. Perspectiva vigente: primeira pessoa. Engine: Unity 6000.6.2f1.

6 distritos, 24 locais, 15 etapas e 182 setores. A posição geográfica, dimensões e nomes de locais genéricos são propostas de level design; não foram apresentados como fatos adicionais da lore.

## Organização espacial

Cidade no tablet → local instanciado → pavimento → setores interligados. A viagem entre pavimentos usa o tablet no protótipo; escadas/elevadores físicos ainda não implementados. O catálogo inteiro pode ser visitado no modo de prévia, independentemente dos desbloqueios futuros. Essa prévia não avança história, reputação ou missões.

| Distrito | Locais | Identidade |
|---|---|---|
| Cidade Antiga | Garagem original; Edifício Horizonte; Apartamentos do bairro antigo; Mercearia do bairro; Restaurante em crescimento; Oficina local; Pequeno escritório; Teatro Imperial | Ferrovia, porto seco, prédios antigos e instalações de várias gerações. |
| Cinturão da Expansão | Escola pública; Condomínio indicado por Helena; Condomínio do contrato perdido; Hotel em reforma; Hospital pequeno; Sede expandida da empresa | Condomínios, escolas e hotéis com infraestrutura padronizada envelhecendo. |
| Zona Empresarial | Shopping; Hospital / ocorrência 03:17; Torre empresarial / apagão; Vértice Serviços Integrados | Torres, shopping e contratos de grande escala. |
| Distrito Industrial | Galpão logístico; Fábrica; Casa de bombas / drenagem | Galpões, fábricas e redes de alta demanda. |
| Distrito Tecnológico | Data center; Edifício inteligente | Data centers, automação e edifícios conectados. |
| Santa Aurora Central | Santa Aurora Central | Complexo municipal e palco da operação Cascata. |

## Progressão da campanha

| Etapa | Locais | Acontecimento |
|---|---|---|
| Prólogo — O primeiro chamado | Garagem original; Edifício Horizonte | Sintoma não é causa; a falha do prólogo é autoral e distinta dos chamados aleatórios. |
| I — Pequenos problemas | Apartamentos do bairro antigo; Mercearia do bairro; Restaurante em crescimento; Oficina local; Pequeno escritório; Edifício Horizonte | Construir reputação e conquistar a indicação de Helena. |
| II — Prevenir é mais barato | Condomínio indicado por Helena; Escola pública; Teatro Imperial | Inspeção preventiva, recomendação ignorada, encontro com Lara. |
| III — O contrato perdido | Condomínio do contrato perdido | Concorrência vencida pela Vértice e primeiros indícios de inspeções falsas. |
| IV — Sistemas críticos | Hotel em reforma; Shopping; Hospital pequeno; Galpão logístico | Falhas em cadeia e redundância não testada no hotel. |
| V — 03:17 | Hospital / ocorrência 03:17 | Emergência de climatização e documentação incompatível com a condição real. |
| VI — A dívida técnica | Fábrica; Hotel em reforma; Vértice Serviços Integrados | Lara e Íris correlacionam o padrão de manutenção omitida. |
| VII — Onda de calor | Data center; Edifício inteligente; Sede expandida da empresa | Escolha de prioridades e equipes necessárias para múltiplos chamados. |
| VIII — A tempestade | Casa de bombas / drenagem; Shopping; Hospital / ocorrência 03:17; Edifício Horizonte | Recursos limitados, alagamentos e consequências persistentes. |
| IX — O apagão | Torre empresarial / apagão | Colapso de redundâncias e início da investigação oficial. |
| X — A auditoria | Vértice Serviços Integrados; Sede expandida da empresa | Oferta de Victor Salles e conflito econômico. |
| XI — O arquivo | Vértice Serviços Integrados | Comparar relatórios antigos e atuais com ajuda de Íris. |
| XII — Santa Aurora Central | Santa Aurora Central | Auditoria municipal e pendências interdependentes. |
| XIII — Cascata | Santa Aurora Central; Sede expandida da empresa | Operação final por equipes, com escolhas de isolamento e capacidade. |
| XIV — O último chamado | Santa Aurora Central; Garagem original; Edifício Horizonte | Amanhecer, mensagem de Guto e memória do crescimento. |

## Plantas e acessos

### Garagem original — garage

Distrito: Cidade Antiga. Primeiro uso: etapa 0. Personagem associado: Augusto Moreira.

Sistemas: elétrica.

- Térreo / serviço: Bancada → Estoque inicial → Computador antigo → Garagem / veículo usado. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: A primeira maleta de Augusto permanece na parede após a campanha.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Edifício Horizonte — horizonte

Distrito: Cidade Antiga. Primeiro uso: etapa 0. Personagem associado: Helena Prado.

Sistemas: elétrica, hidráulica, bombas, acesso.

- Térreo / serviço: Recepção → Garagem → Corredor residencial → Casa de bombas. Portas bidirecionais seguem a grade registrada no JSON.
- Pavimento técnico: Quadro técnico → Reservatório → Portão / interfone → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Corredor sem energia; componente antigo e falha ao aquecer. Primeiro chamado de Guto.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Apartamentos do bairro antigo — apartments

Distrito: Cidade Antiga. Primeiro uso: etapa 1. Personagem associado: Moradores.

Sistemas: elétrica, hidráulica.

- Térreo / serviço: Entrada → Sala → Cozinha → Banheiro → Área de serviço → Corredor técnico. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Instalações improvisadas e reparos anteriores contam a história dos moradores.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Mercearia do bairro — grocery

Distrito: Cidade Antiga. Primeiro uso: etapa 1. Personagem associado: Comerciante.

Sistemas: elétrica, climatização.

- Térreo / serviço: Loja → Estoque → Câmara de apoio → Copa → Quadro técnico → Carga e descarga. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Equipamentos de diferentes épocas dividem o mesmo circuito fictício.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Restaurante em crescimento — restaurant

Distrito: Cidade Antiga. Primeiro uso: etapa 1. Personagem associado: Proprietário.

Sistemas: elétrica, hidráulica, climatização.

- Térreo / serviço: Salão → Cozinha → Despensa → Copa / lavagem → Sala técnica → Carga e descarga. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: O pequeno restaurante cresce junto com a empresa do jogador.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Oficina local — workshop

Distrito: Cidade Antiga. Primeiro uso: etapa 1. Personagem associado: Proprietário.

Sistemas: elétrica, hidráulica.

- Térreo / serviço: Recepção → Bancada → Área de serviço → Depósito → Quadro técnico → Pátio. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Reparos temporários permanecem em uso há anos.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Pequeno escritório — smalloffice

Distrito: Cidade Antiga. Primeiro uso: etapa 1. Personagem associado: Gerente.

Sistemas: elétrica, rede.

- Térreo / serviço: Recepção → Estações de trabalho → Copa → Banheiro → Corredor → Sala técnica. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Primeiros serviços profissionais e recomendações de Helena.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Teatro Imperial — imperial

Distrito: Cidade Antiga. Primeiro uso: etapa 2. Personagem associado: Direção do teatro.

Sistemas: elétrica, climatização.

- Térreo / serviço: Foyer → Plateia → Palco → Bastidores → Cabine técnica → Depósito → Quadro antigo → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Teatro com orçamento apertado e sistema elétrico ultrapassado.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Escola pública — school

Distrito: Cinturão da Expansão. Primeiro uso: etapa 2. Personagem associado: Direção escolar.

Sistemas: elétrica, hidráulica, bombas.

- Térreo / serviço: Recepção → Salas de aula → Pátio → Cozinha → Banheiros → Sala técnica → Reservatório → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Manutenção eficiente com orçamento limitado; primeira inspeção de Lara.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Condomínio indicado por Helena — recurringcondo

Distrito: Cinturão da Expansão. Primeiro uso: etapa 2. Personagem associado: Administrador.

Sistemas: elétrica, hidráulica, bombas, acesso.

- Térreo / serviço: Portaria → Garagem → Corredores → Casa de bombas → Quadro técnico → Reservatórios → Área comum → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Primeiro contrato recorrente; recomendações de inspeção terão consequências.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Condomínio do contrato perdido — lostcondo

Distrito: Cinturão da Expansão. Primeiro uso: etapa 3. Personagem associado: Administrador / Íris.

Sistemas: elétrica, bombas, geradores, acesso.

- Térreo / serviço: Portaria → Garagem → Casa de bombas → Gerador → Quadro principal → Central de acesso → Reservatórios → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Vértice vence a concorrência. Adesivos recentes contrastam com a condição dos equipamentos.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Hotel em reforma — hotel

Distrito: Cinturão da Expansão. Primeiro uso: etapa 4. Personagem associado: Gerência.

Sistemas: hidráulica, bombas, climatização.

- Térreo / serviço: Recepção → Quartos / corredor → Lavanderia → Sala de bombas. Portas bidirecionais seguem a grade registrada no JSON.
- Pavimento técnico: Água quente → Bomba reserva → HVAC → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: A bomba reserva não foi testada, embora o laudo registre redundância operacional.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Shopping — mall

Distrito: Zona Empresarial. Primeiro uso: etapa 4. Personagem associado: Administração.

Sistemas: elétrica, climatização, bombas, segurança.

- Térreo / serviço: Praça central → Lojas → Doca → Segurança → Sala elétrica → HVAC → Bombas → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: A operação precisa continuar; durante a tempestade, pode ter prioridade menor que o hospital.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Hospital pequeno — smallhospital

Distrito: Cinturão da Expansão. Primeiro uso: etapa 4. Personagem associado: Administração / Lara.

Sistemas: elétrica, climatização, bombas, geradores.

- Térreo / serviço: Recepção → Ala assistencial → Sala de equipamentos → HVAC → Bombas → Gerador → Quadro técnico → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Introdução a sistemas críticos e efeitos em cadeia.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Galpão logístico — logistics

Distrito: Distrito Industrial. Primeiro uso: etapa 4. Personagem associado: Operações.

Sistemas: elétrica, bombas, rede, segurança.

- Térreo / serviço: Doca → Armazenagem → Expedição → Escritório → Sala elétrica → Bombas → Telecom → Pátio. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Infraestrutura de alta demanda mantém a distribuição da cidade.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Hospital / ocorrência 03:17 — hospital0317

Distrito: Zona Empresarial. Primeiro uso: etapa 5. Personagem associado: Lara / administração.

Sistemas: elétrica, climatização, automação, hidráulica.

- Térreo / serviço: Recepção de serviço → Ala quente → HVAC principal → Automação → Válvula de circulação → Backup térmico → Quadro técnico → Sala de evidências. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Filtro com meses de sujeira e etiqueta de manutenção de oito dias atrás.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Fábrica — factory

Distrito: Distrito Industrial. Primeiro uso: etapa 6. Personagem associado: Gerência industrial.

Sistemas: elétrica, bombas, climatização.

- Térreo / serviço: Portaria → Produção → Máquina auxiliar → Oficina → Quadro principal → Bombas → HVAC → Pátio técnico. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Decisão entre parar produção e continuar com equipamento auxiliar degradado.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Data center — datacenter

Distrito: Distrito Tecnológico. Primeiro uso: etapa 7. Personagem associado: Operações de TI.

Sistemas: elétrica, climatização, rede, redundância.

- Térreo / serviço: Controle de acesso → Sala de racks A → Sala de racks B → Refrigeração → Energia A → Energia B → Telecom → Sala de operação. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Não pode ficar offline; calor e redundância condicionam a ordem dos reparos.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Edifício inteligente — smarttower

Distrito: Distrito Tecnológico. Primeiro uso: etapa 7. Personagem associado: Gerência técnica.

Sistemas: elétrica, automação, climatização, acesso, rede.

- Térreo / serviço: Lobby → Escritórios → Automação → Controle de acesso. Portas bidirecionais seguem a grade registrada no JSON.
- Pavimento técnico: HVAC → Energia → Telecom → Cobertura. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Tudo está conectado: uma falha se propaga entre subsistemas.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Casa de bombas / drenagem — drainage

Distrito: Distrito Industrial. Primeiro uso: etapa 8. Personagem associado: Defesa civil.

Sistemas: bombas, elétrica, hidráulica.

- Térreo / serviço: Acesso elevado → Poço de drenagem → Bomba A → Bomba B → Comando → Energia → Reservatório → Saída de emergência. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: A tempestade ameaça inundar a instalação; prioridade compete com outros chamados.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Torre empresarial / apagão — blackouttower

Distrito: Zona Empresarial. Primeiro uso: etapa 9. Personagem associado: Lara / administração.

Sistemas: elétrica, geradores, redundância.

- Térreo / serviço: Lobby → Escritórios → Gerador principal → Tanque fictício. Portas bidirecionais seguem a grade registrada no JSON.
- Pavimento técnico: Partida / baterias → Backup secundário → Quadro principal → Sala de evidências. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Testes mensais registrados não aconteceram. Três redundâncias anunciadas, nenhuma operacional.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Vértice Serviços Integrados — vertice

Distrito: Zona Empresarial. Primeiro uso: etapa 10. Personagem associado: Victor Salles / Íris.

Sistemas: rede, documentação.

- Térreo / serviço: Recepção → Sala de propostas → Diretoria → Engenharia → Arquivo antigo → Base de relatórios → Sala de reunião → Acesso de serviço. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Oferta de terceirização e arquivo de recomendações omitidas. Sem invasão ou missão de combate.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Sede expandida da empresa — companyhq

Distrito: Cinturão da Expansão. Primeiro uso: etapa 7. Personagem associado: Equipe do jogador.

Sistemas: gestão, elétrica, rede.

- Térreo / serviço: Recepção / atendimento → Administração → Oficina → Almoxarifado → Treinamento → Monitoramento → Garagem / frota → Sala de planejamento. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Funcionários, frota e central de operações tornam visível o crescimento.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

### Santa Aurora Central — central

Distrito: Santa Aurora Central. Primeiro uso: etapa 12. Personagem associado: Lara / equipe / município.

Sistemas: elétrica, geradores, bombas, climatização, rede, automação.

- Térreo / serviço: Centro administrativo → Monitoramento urbano → Data center municipal → Telecomunicações. Portas bidirecionais seguem a grade registrada no JSON.
- Pavimento técnico: Centro de emergência → Distribuição elétrica → Geradores → Bombas / drenagem. Portas bidirecionais seguem a grade registrada no JSON.
- Nível superior: HVAC principal → Controlador / automação → Corredor de serviço → Pátio do amanhecer. Portas bidirecionais seguem a grade registrada no JSON.

Pista/identidade: Cascata: aquecimento, refrigeração reduzida, drenagem parada e perda de comunicação.

Persistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.

## Santa Aurora Central / Cascata

Três pavimentos, 12 setores, rotas de serviço e ligação vertical. Energia, bombas, HVAC, telecom e controlador ficam em setores próprios para distribuir a equipe. Pátio superior reservado à saída ao amanhecer.

Dependências planejadas (ainda não simuladas no catálogo):

- elétrica → bombas: Bombas virtuais sem alimentação param.
- elétrica → climatização: HVAC sem alimentação perde capacidade.
- bombas → climatização: Circulação insuficiente reduz refrigeração.
- climatização → rede: Calor crescente reduz capacidade de servidores.
- rede → automação: Perda de comunicação impede comando remoto.
- automação → redundância: Backup pode não assumir automaticamente.

## O que é estrutura e o que é campanha implementada

O catálogo, as conexões e as prévias espaciais são implementados. Os 15 capítulos não são apresentados como missões prontas. Diálogos, eventos climáticos, escolhas, equipes, irregularidades persistentes, prova documental e finais estão planejados. O loop elétrico inicial permanece como chamado de teste; o prólogo autoral exige ainda aquecimento/isolamento de circuito e reincidência.
