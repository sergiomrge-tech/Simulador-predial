import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2] ?? process.cwd();
const districts = [
  ['old','Cidade Antiga',-85,-55,'Ferrovia, porto seco, prédios antigos e instalações de várias gerações.'],
  ['expansion','Cinturão da Expansão',0,-60,'Condomínios, escolas e hotéis com infraestrutura padronizada envelhecendo.'],
  ['corporate','Zona Empresarial',70,0,'Torres, shopping e contratos de grande escala.'],
  ['industrial','Distrito Industrial',-85,60,'Galpões, fábricas e redes de alta demanda.'],
  ['technology','Distrito Tecnológico',65,80,'Data centers, automação e edifícios conectados.'],
  ['civic','Santa Aurora Central',0,25,'Complexo municipal e palco da operação Cascata.'],
].map(([id,name,x,z,description])=>({id,name,x,z,description}));
const rows = [
 ['garage','Garagem original','old',0,'Augusto Moreira',['Bancada','Estoque inicial','Computador antigo','Garagem / veículo usado'],['elétrica'],'A primeira maleta de Augusto permanece na parede após a campanha.'],
 ['horizonte','Edifício Horizonte','old',0,'Helena Prado',['Recepção','Garagem','Corredor residencial','Casa de bombas','Quadro técnico','Reservatório','Portão / interfone','Cobertura'],['elétrica','hidráulica','bombas','acesso'],'Corredor sem energia; componente antigo e falha ao aquecer. Primeiro chamado de Guto.'],
 ['apartments','Apartamentos do bairro antigo','old',1,'Moradores',['Entrada','Sala','Cozinha','Banheiro','Área de serviço','Corredor técnico'],['elétrica','hidráulica'],'Instalações improvisadas e reparos anteriores contam a história dos moradores.'],
 ['grocery','Mercearia do bairro','old',1,'Comerciante',['Loja','Estoque','Câmara de apoio','Copa','Quadro técnico','Carga e descarga'],['elétrica','climatização'],'Equipamentos de diferentes épocas dividem o mesmo circuito fictício.'],
 ['restaurant','Restaurante em crescimento','old',1,'Proprietário',['Salão','Cozinha','Despensa','Copa / lavagem','Sala técnica','Carga e descarga'],['elétrica','hidráulica','climatização'],'O pequeno restaurante cresce junto com a empresa do jogador.'],
 ['workshop','Oficina local','old',1,'Proprietário',['Recepção','Bancada','Área de serviço','Depósito','Quadro técnico','Pátio'],['elétrica','hidráulica'],'Reparos temporários permanecem em uso há anos.'],
 ['smalloffice','Pequeno escritório','old',1,'Gerente',['Recepção','Estações de trabalho','Copa','Banheiro','Corredor','Sala técnica'],['elétrica','rede'],'Primeiros serviços profissionais e recomendações de Helena.'],
 ['imperial','Teatro Imperial','old',2,'Direção do teatro',['Foyer','Plateia','Palco','Bastidores','Cabine técnica','Depósito','Quadro antigo','Cobertura'],['elétrica','climatização'],'Teatro com orçamento apertado e sistema elétrico ultrapassado.'],
 ['school','Escola pública','expansion',2,'Direção escolar',['Recepção','Salas de aula','Pátio','Cozinha','Banheiros','Sala técnica','Reservatório','Cobertura'],['elétrica','hidráulica','bombas'],'Manutenção eficiente com orçamento limitado; primeira inspeção de Lara.'],
 ['recurringcondo','Condomínio indicado por Helena','expansion',2,'Administrador',['Portaria','Garagem','Corredores','Casa de bombas','Quadro técnico','Reservatórios','Área comum','Cobertura'],['elétrica','hidráulica','bombas','acesso'],'Primeiro contrato recorrente; recomendações de inspeção terão consequências.'],
 ['lostcondo','Condomínio do contrato perdido','expansion',3,'Administrador / Íris',['Portaria','Garagem','Casa de bombas','Gerador','Quadro principal','Central de acesso','Reservatórios','Cobertura'],['elétrica','bombas','geradores','acesso'],'Vértice vence a concorrência. Adesivos recentes contrastam com a condição dos equipamentos.'],
 ['hotel','Hotel em reforma','expansion',4,'Gerência',['Recepção','Quartos / corredor','Lavanderia','Sala de bombas','Água quente','Bomba reserva','HVAC','Cobertura'],['hidráulica','bombas','climatização'],'A bomba reserva não foi testada, embora o laudo registre redundância operacional.'],
 ['mall','Shopping','corporate',4,'Administração',['Praça central','Lojas','Doca','Segurança','Sala elétrica','HVAC','Bombas','Cobertura'],['elétrica','climatização','bombas','segurança'],'A operação precisa continuar; durante a tempestade, pode ter prioridade menor que o hospital.'],
 ['smallhospital','Hospital pequeno','expansion',4,'Administração / Lara',['Recepção','Ala assistencial','Sala de equipamentos','HVAC','Bombas','Gerador','Quadro técnico','Cobertura'],['elétrica','climatização','bombas','geradores'],'Introdução a sistemas críticos e efeitos em cadeia.'],
 ['logistics','Galpão logístico','industrial',4,'Operações',['Doca','Armazenagem','Expedição','Escritório','Sala elétrica','Bombas','Telecom','Pátio'],['elétrica','bombas','rede','segurança'],'Infraestrutura de alta demanda mantém a distribuição da cidade.'],
 ['hospital0317','Hospital / ocorrência 03:17','corporate',5,'Lara / administração',['Recepção de serviço','Ala quente','HVAC principal','Automação','Válvula de circulação','Backup térmico','Quadro técnico','Sala de evidências'],['elétrica','climatização','automação','hidráulica'],'Filtro com meses de sujeira e etiqueta de manutenção de oito dias atrás.'],
 ['factory','Fábrica','industrial',6,'Gerência industrial',['Portaria','Produção','Máquina auxiliar','Oficina','Quadro principal','Bombas','HVAC','Pátio técnico'],['elétrica','bombas','climatização'],'Decisão entre parar produção e continuar com equipamento auxiliar degradado.'],
 ['datacenter','Data center','technology',7,'Operações de TI',['Controle de acesso','Sala de racks A','Sala de racks B','Refrigeração','Energia A','Energia B','Telecom','Sala de operação'],['elétrica','climatização','rede','redundância'],'Não pode ficar offline; calor e redundância condicionam a ordem dos reparos.'],
 ['smarttower','Edifício inteligente','technology',7,'Gerência técnica',['Lobby','Escritórios','Automação','Controle de acesso','HVAC','Energia','Telecom','Cobertura'],['elétrica','automação','climatização','acesso','rede'],'Tudo está conectado: uma falha se propaga entre subsistemas.'],
 ['drainage','Casa de bombas / drenagem','industrial',8,'Defesa civil',['Acesso elevado','Poço de drenagem','Bomba A','Bomba B','Comando','Energia','Reservatório','Saída de emergência'],['bombas','elétrica','hidráulica'],'A tempestade ameaça inundar a instalação; prioridade compete com outros chamados.'],
 ['blackouttower','Torre empresarial / apagão','corporate',9,'Lara / administração',['Lobby','Escritórios','Gerador principal','Tanque fictício','Partida / baterias','Backup secundário','Quadro principal','Sala de evidências'],['elétrica','geradores','redundância'],'Testes mensais registrados não aconteceram. Três redundâncias anunciadas, nenhuma operacional.'],
 ['vertice','Vértice Serviços Integrados','corporate',10,'Victor Salles / Íris',['Recepção','Sala de propostas','Diretoria','Engenharia','Arquivo antigo','Base de relatórios','Sala de reunião','Acesso de serviço'],['rede','documentação'],'Oferta de terceirização e arquivo de recomendações omitidas. Sem invasão ou missão de combate.'],
 ['companyhq','Sede expandida da empresa','expansion',7,'Equipe do jogador',['Recepção / atendimento','Administração','Oficina','Almoxarifado','Treinamento','Monitoramento','Garagem / frota','Sala de planejamento'],['gestão','elétrica','rede'],'Funcionários, frota e central de operações tornam visível o crescimento.'],
 ['central','Santa Aurora Central','civic',12,'Lara / equipe / município',['Centro administrativo','Monitoramento urbano','Data center municipal','Telecomunicações','Centro de emergência','Distribuição elétrica','Geradores','Bombas / drenagem','HVAC principal','Controlador / automação','Corredor de serviço','Pátio do amanhecer'],['elétrica','geradores','bombas','climatização','rede','automação'],'Cascata: aquecimento, refrigeração reduzida, drenagem parada e perda de comunicação.'],
];
const chapters = [
 ['Prólogo — O primeiro chamado',['garage','horizonte'],'Sintoma não é causa; a falha do prólogo é autoral e distinta dos chamados aleatórios.'],
 ['I — Pequenos problemas',['apartments','grocery','restaurant','workshop','smalloffice','horizonte'],'Construir reputação e conquistar a indicação de Helena.'],
 ['II — Prevenir é mais barato',['recurringcondo','school','imperial'],'Inspeção preventiva, recomendação ignorada, encontro com Lara.'],
 ['III — O contrato perdido',['lostcondo'],'Concorrência vencida pela Vértice e primeiros indícios de inspeções falsas.'],
 ['IV — Sistemas críticos',['hotel','mall','smallhospital','logistics'],'Falhas em cadeia e redundância não testada no hotel.'],
 ['V — 03:17',['hospital0317'],'Emergência de climatização e documentação incompatível com a condição real.'],
 ['VI — A dívida técnica',['factory','hotel','vertice'],'Lara e Íris correlacionam o padrão de manutenção omitida.'],
 ['VII — Onda de calor',['datacenter','smarttower','companyhq'],'Escolha de prioridades e equipes necessárias para múltiplos chamados.'],
 ['VIII — A tempestade',['drainage','mall','hospital0317','horizonte'],'Recursos limitados, alagamentos e consequências persistentes.'],
 ['IX — O apagão',['blackouttower'],'Colapso de redundâncias e início da investigação oficial.'],
 ['X — A auditoria',['vertice','companyhq'],'Oferta de Victor Salles e conflito econômico.'],
 ['XI — O arquivo',['vertice'],'Comparar relatórios antigos e atuais com ajuda de Íris.'],
 ['XII — Santa Aurora Central',['central'],'Auditoria municipal e pendências interdependentes.'],
 ['XIII — Cascata',['central','companyhq'],'Operação final por equipes, com escolhas de isolamento e capacidade.'],
 ['XIV — O último chamado',['central','garage','horizonte'],'Amanhecer, mensagem de Guto e memória do crescimento.'],
].map(([name,locationIds,beat],index)=>({id:`chapter.${index}`,index,name,locationIds,beat}));
const locations = rows.map(([id,name,districtId,chapter,npc,roomNames,systems,lore],index)=>{
 const district = districts.find(d=>d.id===districtId);
 const within = rows.slice(0,index).filter(r=>r[2]===districtId).length;
 const levels = id==='central' ? 3 : ['horizonte','hotel','blackouttower','smarttower'].includes(id) ? 2 : 1;
 const floors = Array.from({length:levels},(_,f)=>{
   const names = levels===1 ? roomNames : roomNames.slice(f*4,(f+1)*4);
   const rooms=names.map((name,i)=>({id:`${id}.f${f}.r${i}`,name,x:(i%2)*8,z:Math.floor(i/2)*8,width:8,depth:8,systemIds:systems,hotspot:i===names.length-1?lore: `Área ${name}; pontos técnicos e histórico ainda em produção.`}));
   const links=[];
   for(let i=0;i<rooms.length;i++){
     if(i%2===0&&i+1<rooms.length)links.push({from:rooms[i].id,to:rooms[i+1].id,type:'door'});
     if(i+2<rooms.length)links.push({from:rooms[i].id,to:rooms[i+2].id,type:'door'});
   }
   return {id:`${id}.floor.${f}`,name:f===0?'Térreo / serviço':f===1?'Pavimento técnico':'Nível superior',index:f,rooms,connections:links};
 });
 const verticalConnections = Array.from({length:levels-1},(_,f)=>({from:floors[f].id,to:floors[f+1].id,type:'service-stair-or-lift',previewTravel:'tablet'}));
 return {id,name,districtId,unlockChapter:chapter,npc,systems,lore,x:district.x+(within%3-1)*19,z:district.z+Math.floor(within/3)*20,floors,verticalConnections,productionState:['garage','horizonte'].includes(id)?'prototype':'layout-blockout',persistentFlags:[`${id}.inspected`,`${id}.documented`,`${id}.improved`],visitAfterCampaign:true};
});
const dependencies = [
 {from:'elétrica',to:'bombas',effect:'Bombas virtuais sem alimentação param.'},
 {from:'elétrica',to:'climatização',effect:'HVAC sem alimentação perde capacidade.'},
 {from:'bombas',to:'climatização',effect:'Circulação insuficiente reduz refrigeração.'},
 {from:'climatização',to:'rede',effect:'Calor crescente reduz capacidade de servidores.'},
 {from:'rede',to:'automação',effect:'Perda de comunicação impede comando remoto.'},
 {from:'automação',to:'redundância',effect:'Backup pode não assumir automaticamente.'},
];
const data = {schemaVersion:1,codename:'PROJECT FACILITY',city:'Santa Aurora',perspective:'first-person',worldMode:'hub-and-instanced-locations',geographyStatus:'Proposed spatial arrangement based on supplied lore',districts,chapters,locations,dependencies};
for (const loc of locations) {
 for (const floor of loc.floors) {
   if(!floor.rooms.length)throw Error(`Empty floor ${floor.id}`);
   const ids=new Set(floor.rooms.map(r=>r.id));
   for(const link of floor.connections)if(!ids.has(link.from)||!ids.has(link.to))throw Error('Broken room link');
   const reachable=new Set([floor.rooms[0].id]);
   for(let i=0;i<floor.rooms.length;i++)for(const link of floor.connections){if(reachable.has(link.from))reachable.add(link.to);if(reachable.has(link.to))reachable.add(link.from);}
   if(reachable.size!==ids.size)throw Error(`Disconnected floor ${floor.id}`);
 }
}
for(const ch of chapters)for(const id of ch.locationIds)if(!locations.some(l=>l.id===id))throw Error('Invalid chapter location');
const target = path.join(root,'FacilityOps/Assets/_Game/Resources/World');fs.mkdirSync(target,{recursive:true});
fs.writeFileSync(path.join(target,'campaign.json'),JSON.stringify(data,null,2)+'\n');
const count=locations.reduce((n,l)=>n+l.floors.reduce((s,f)=>s+f.rooms.length,0),0);
const md=`# Estrutura de Santa Aurora\n\nFonte: LORE_CAMPANHA_ORIGINAL.md. Perspectiva vigente: primeira pessoa. Engine: Unity 6000.6.2f1.\n\n${districts.length} distritos, ${locations.length} locais, ${chapters.length} etapas e ${count} setores. A posição geográfica, dimensões e nomes de locais genéricos são propostas de level design; não foram apresentados como fatos adicionais da lore.\n\n## Organização espacial\n\nCidade no tablet → local instanciado → pavimento → setores interligados. A viagem entre pavimentos usa o tablet no protótipo; escadas/elevadores físicos ainda não implementados. O catálogo inteiro pode ser visitado no modo de prévia, independentemente dos desbloqueios futuros. Essa prévia não avança história, reputação ou missões.\n\n| Distrito | Locais | Identidade |\n|---|---|---|\n${districts.map(d=>`| ${d.name} | ${locations.filter(l=>l.districtId===d.id).map(l=>l.name).join('; ')} | ${d.description} |`).join('\n')}\n\n## Progressão da campanha\n\n| Etapa | Locais | Acontecimento |\n|---|---|---|\n${chapters.map(c=>`| ${c.name} | ${c.locationIds.map(id=>locations.find(l=>l.id===id).name).join('; ')} | ${c.beat} |`).join('\n')}\n\n## Plantas e acessos\n\n${locations.map(l=>`### ${l.name} — ${l.id}\n\nDistrito: ${districts.find(d=>d.id===l.districtId).name}. Primeiro uso: etapa ${l.unlockChapter}. Personagem associado: ${l.npc}.\n\nSistemas: ${l.systems.join(', ')}.\n\n${l.floors.map(f=>`- ${f.name}: ${f.rooms.map(r=>r.name).join(' → ')}. Portas bidirecionais seguem a grade registrada no JSON.`).join('\n')}\n\nPista/identidade: ${l.lore}\n\nPersistência prevista: inspeção, documentação, melhorias, histórico; revisitas após a campanha.`).join('\n\n')}\n\n## Santa Aurora Central / Cascata\n\nTrês pavimentos, 12 setores, rotas de serviço e ligação vertical. Energia, bombas, HVAC, telecom e controlador ficam em setores próprios para distribuir a equipe. Pátio superior reservado à saída ao amanhecer.\n\nDependências planejadas (ainda não simuladas no catálogo):\n\n${dependencies.map(d=>`- ${d.from} → ${d.to}: ${d.effect}`).join('\n')}\n\n## O que é estrutura e o que é campanha implementada\n\nO catálogo, as conexões e as prévias espaciais são implementados. Os 15 capítulos não são apresentados como missões prontas. Diálogos, eventos climáticos, escolhas, equipes, irregularidades persistentes, prova documental e finais estão planejados. O loop elétrico inicial permanece como chamado de teste; o prólogo autoral exige ainda aquecimento/isolamento de circuito e reincidência.\n`;
fs.writeFileSync(path.join(root,'Docs/MAPA_CAMPANHA.md'),md);
fs.writeFileSync(path.join(root,'Docs/map-validation.json'),JSON.stringify({districts:districts.length,locations:locations.length,chapters:chapters.length,sectors:count,allRoomGraphsConnected:true,allChapterLocationsExist:true},null,2));
console.log(`Campaign generated: ${locations.length} locations / ${count} sectors / all room graphs connected.`);
