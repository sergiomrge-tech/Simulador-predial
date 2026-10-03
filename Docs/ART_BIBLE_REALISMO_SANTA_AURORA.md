# ART BIBLE — REALISMO DE SANTA AURORA

**Projeto:** Facility Ops / Simulador Predial  
**Status:** direção visual oficial de produção  
**Referência principal:** VEIN como alvo de realismo, atmosfera, densidade e materialidade.  
**Regra legal/criativa:** não copiar assets, texturas, prédios, layouts, personagens, UI ou identidade exclusiva de VEIN.

---

# 1. Objetivo visual

Santa Aurora deve apresentar um realismo urbano convincente em primeira pessoa.

O jogador precisa acreditar que:

- as casas foram construídas para pessoas morarem;
- os prédios possuem infraestrutura de verdade;
- as salas técnicas pertencem ao edifício;
- ruas e bairros foram usados por anos;
- materiais envelhecem de forma coerente;
- objetos têm peso, escala e função.

O jogo não usará low-poly como estilo final.

---

# 2. Pilares

## Realismo de proporção

Tudo em escala métrica real.

## Materialidade

Todo material importante precisa reagir à luz de forma fisicamente plausível.

## Densidade

Ambientes visitáveis não podem parecer vazios.

## História ambiental

Desgaste e clutter devem contar como o local é usado.

## Coerência técnica

Equipamentos precisam fazer sentido dentro da instalação.

---

# 3. Geometria

Blockout pode ser simples.

Asset final não.

## Próximo da câmera

- bordas chanfradas;
- espessura real;
- peças separadas quando visualmente necessário;
- parafusos/placas/tampas onde forem importantes;
- formas não perfeitamente retas quando o objeto real não é.

## Proibido

- caixas simples representando móveis finais;
- cilindros facetados visíveis;
- telhado sem espessura;
- janela apenas como textura;
- porta sem batente;
- tubulação quadrada improvisada;
- mobiliário sem detalhe de uso.

---

# 4. PBR

Materiais finais devem utilizar quando aplicável:

- Base Color;
- Normal;
- Metallic;
- Roughness/Smoothness;
- AO;
- Height/Parallax seletivo;
- emissive em equipamentos.

Nenhum material de produção deve depender apenas de cor flat.

---

# 5. Texel density

Definir padrão por categoria.

Sugestão inicial:

- hero props: 1024 px/m ou equivalente;
- props próximos: 512–1024 px/m;
- arquitetura: 256–512 px/m;
- background: reduzido via LOD/proxy.

Atlases e trimsheets podem ser utilizados desde que não destruam variedade visual.

---

# 6. Bordas

Bordas perfeitamente afiadas reduzem realismo.

Usar bevel coerente com escala do objeto.

Exemplos:

- armário metálico;
- bancada;
- painel elétrico;
- concreto;
- móveis;
- eletrodomésticos.

---

# 7. Desgaste

Desgaste deve ter lógica.

## Metal

- quinas;
- parafusos;
- base próxima ao piso;
- pontos de contato.

## Parede

- umidade;
- marcas;
- reparos;
- sujeira próxima ao rodapé.

## Piso

- rotas de circulação;
- óleo;
- água;
- abrasão.

Não aplicar sujeira procedural uniforme em tudo.

---

# 8. Decals

Decals obrigatórios em ambientes finais.

Categorias:

- infiltração;
- ferrugem;
- rachaduras;
- poeira;
- óleo;
- tinta descascada;
- remendos;
- números;
- etiquetas;
- sinais;
- avisos;
- marcas de manutenção;
- fita;
- identificação elétrica/hidráulica.

---

# 9. Arquitetura residencial

Casas e apartamentos precisam ter:

- portas e batentes;
- tomadas;
- interruptores;
- rodapés;
- conduítes quando aplicável;
- luminárias;
- janelas;
- cortinas;
- móveis;
- objetos pessoais;
- imperfeições;
- áreas de armazenamento.

Nenhuma residência principal deve parecer cenário de showroom.

---

# 10. Arquitetura comercial

Lojas e escritórios:

- sinalização;
- estoque;
- mobiliário;
- caixas;
- equipamentos;
- iluminação realista;
- áreas de serviço;
- instalações técnicas.

---

# 11. Arquitetura industrial

Galpões/fábricas:

- estrutura metálica;
- eletrocalhas;
- tubulação;
- válvulas;
- painéis;
- máquinas;
- plataformas;
- guarda-corpo;
- sinalização;
- piso marcado;
- áreas de manutenção;
- drenagem.

---

# 12. Salas técnicas

Recebem prioridade máxima.

## Elétrica

- QGBT;
- quadros;
- disjuntores;
- etiquetas;
- eletrocalhas;
- cabos;
- aterramento;
- sinalização.

## Bombas

- bombas;
- bases;
- motor;
- flange;
- válvula;
- manômetro;
- tubulação;
- dreno;
- quadro local.

## HVAC

- dutos;
- unidades;
- bandeja;
- tubulação;
- isolamentos;
- sensores.

## Geradores

- tanque;
- painel;
- escapamento;
- ventilação;
- isolamento.

---

# 13. Vegetação

Vegetação não pode parecer genérica.

Usar:

- árvores com variação;
- arbustos;
- gramíneas;
- vegetação espontânea;
- plantas urbanas;
- sujeira junto a muros;
- crescimento em terrenos abandonados.

LOD obrigatório.

---

# 14. Ruas

Ruas finais precisam conter:

- asfalto com variação;
- remendos;
- faixas;
- bueiros;
- sarjetas;
- tampas;
- postes;
- placas;
- meio-fio;
- sujeira;
- vegetação marginal;
- estacionamentos;
- entradas de garagem.

---

# 15. Iluminação

A luz deve vender materialidade.

## Exterior

- sol direcional;
- céu;
- nuvens;
- reflexos;
- sombras;
- variação climática.

## Interior

- fluorescentes;
- LED;
- lâmpadas residenciais;
- luz de emergência;
- iluminação de serviço;
- luz entrando pelas janelas.

Evitar ambientes uniformemente iluminados.

---

# 16. Clima

Preparar visual para:

- ensolarado;
- nublado;
- chuva;
- pós-chuva;
- noite;
- amanhecer;
- neblina leve.

Superfícies molhadas devem ter resposta de roughness coerente.

---

# 17. Clutter

Clutter precisa ser funcional.

Exemplos:

- caixas;
- ferramentas;
- papéis;
- baldes;
- embalagens;
- EPIs;
- cabos;
- extensões;
- peças;
- pallets;
- carrinhos;
- lixo;
- roupas;
- alimentos;
- eletrônicos.

Nunca distribuir objetos aleatoriamente apenas para encher espaço.

---

# 18. Lar do protagonista

É hero location.

Precisa superar o padrão médio de detalhe.

Deve possuir:

- objetos pessoais;
- roupas;
- calçados;
- documentos;
- contas;
- ferramentas;
- comida;
- eletrônicos;
- produtos de higiene;
- objetos de lazer;
- itens comprados aparecendo fisicamente.

Cada melhoria financeira deve alterar o ambiente.

---

# 19. Veículos

Veículos próprios devem ter:

- exterior detalhado;
- interior legível;
- painel;
- bancos;
- porta-malas/carga;
- desgaste;
- sujeira;
- reflexos;
- rodas e pneus adequados.

Veículo técnico precisa mostrar organização do equipamento.

---

# 20. Personagem em primeira pessoa

Mãos e braços precisam combinar com o realismo geral.

- luvas;
- mangas;
- sujeira;
- animação de ferramenta;
- contato com objetos;
- transições suaves.

Ferramentas não podem apenas flutuar na câmera.

---

# 21. Ferramentas

Hero props.

Precisam ter:

- materiais corretos;
- marcas fictícias próprias;
- botões;
- display;
- parafusos;
- desgaste;
- animações;
- som.

---

# 22. Marcas e identidade

Criar marcas fictícias para:

- ferramentas;
- eletrodomésticos;
- bombas;
- painéis;
- veículos quando necessário;
- lojas;
- fornecedores.

Evitar uso indevido de marcas reais.

---

# 23. LOD

Toda otimização visual deve ser invisível em gameplay normal.

LOD0 não pode parecer low-poly.

LOD1/2 podem reduzir geometria.

HLOD/proxy apenas para distância.

---

# 24. Performance sem sacrificar estética

Preferir:

- LOD;
- HLOD;
- occlusion;
- streaming;
- instancing;
- batching;
- impostors distantes;
- light baking seletivo;
- texture streaming.

Não resolver performance transformando o jogo em estética low-poly.

---

# 25. Gate de aprovação visual

Um ambiente só recebe status FINAL quando:

- blockout removido/oculto;
- materiais PBR aplicados;
- iluminação revisada;
- decals aplicados;
- clutter coerente;
- escala validada;
- colisão funcional;
- LOD presente;
- repetição modular disfarçada;
- screenshots reais revisadas;
- performance medida.

---

# 26. Comparação com referência

Antes de aprovar hero location:

1. capturar screenshots reais da Unity;
2. comparar densidade, iluminação, materialidade e leitura espacial com screenshots oficiais da referência;
3. identificar lacunas;
4. corrigir;
5. repetir.

A comparação é de qualidade, não de identidade de assets.

---

# 27. Ordem de produção visual

1. kit de materiais;
2. kit modular arquitetônico;
3. infraestrutura urbana;
4. props residenciais;
5. props comerciais;
6. props industriais;
7. kit técnico;
8. lar;
9. Oficina Aurora;
10. Horizonte;
11. Cidade Antiga;
12. demais distritos.

---

# 28. Regra final

**A versão de produção de Santa Aurora deve ser realista e detalhada.**

Blockout, placeholders e low-poly só podem existir enquanto ferramentas internas de desenvolvimento.

O objetivo é que, em screenshots reais, o jogador perceba um nível de realismo, densidade e atmosfera comparável ao alvo visual escolhido, enquanto todos os assets e a identidade de Santa Aurora permanecem originais.
