# CLAUDE NEXT TASK — W3.1

## Cidade Antiga — Visual Polish Gate

W3 foi concluído como **PARTIAL PASS** no commit `d58c4d2`.

Esta etapa NÃO deve tocar na Unity, no streaming runtime, nos saves, no gameplay C# nem na branch `gpt/unity-world-integration`.

Objetivo: corrigir os principais itens que impediram o W3 de receber PASS visual, mantendo o mesmo recorte de 15 subcélulas.

---

## 1. Carros — prioridade máxima

Os carros atuais ainda leem como proxies/caixas e prejudicam muito as capturas de rua.

Substituir por modelos autorais/procedurais simples, mas visualmente críveis, com:
- rodas;
- pneus;
- caixas de roda;
- vidros;
- faróis;
- lanternas;
- para-choques;
- espelhos;
- placas fictícias;
- silhuetas diferentes;
- pelo menos 5 famílias de veículo:
  - hatch compacto;
  - sedan;
  - utilitário leve;
  - SUV compacto;
  - van de serviço.

Regras:
- sem copiar modelos/marcas reais;
- nada de logotipo real;
- variação de cor e estado;
- alguns carros mais antigos nos bairros afastados;
- veículos de serviço próximos a Oficina/Horizonte;
- LOD0/LOD1/proxy;
- instancing quando possível.

---

## 2. Edificações de fundo — quebrar repetição

No corredor W3, reduzir aparência de famílias genéricas repetidas.

Criar variantes autorais por quarteirão:
- diferentes telhados;
- caixas d’água;
- platibandas;
- anexos;
- marquises;
- portões;
- muros;
- varandas;
- escadas externas;
- condensadoras;
- antenas;
- telhas;
- fachadas reformadas/parcialmente reformadas;
- fundos e laterais tratados.

Não remodelar a Cidade Antiga inteira.
Foco apenas no corredor W3 e vistas principais.

---

## 3. Grama e vegetação de chão

Corrigir o efeito de “pente” dos tufos atuais.

Melhorar:
- lâminas curvas;
- variação de altura;
- variação de largura;
- inclinação;
- cor;
- densidade;
- mistura de grama curta, erva e mato espontâneo.

Evitar:
- cards idênticos;
- alinhamento vertical repetitivo;
- densidade uniforme.

Preservar performance e LOD.

---

## 4. Relevo / taludes — leitura visual

Criar uma captura dedicada de um talude real, sem telhados bloqueando a leitura.

Melhorar visualmente:
- muros de arrimo;
- escadas;
- rampas;
- drenagem;
- transição calçada/solo;
- vegetação de talude;
- sombra de contato.

Não alterar as cotas validadas do terreno.

---

## 5. Interiores

Corrigir ambientes ainda frios/escuros:
- Apto 12;
- galpão da Oficina;
- Mercearia.

Ajustar:
- luz de preenchimento;
- temperatura de cor;
- exposição;
- enquadramento;
- visibilidade de gôndolas/mercadorias;
- contraste exterior/interior.

Não esconder problemas de material com pós-processo forte.

---

## 6. Decals autorais

Adicionar um primeiro conjunto de decals pintados/procedurais próprios:
- pichação fictícia;
- cartazes ricos;
- etiquetas;
- placas de comércio;
- manchas;
- umidade;
- ferrugem;
- pintura descascada;
- cola de cartaz;
- marcas de obra.

Sem marcas reais.
Sem conteúdo ofensivo.
Sem material de terceiros sem licença clara.

---

## 7. Árvores e calçadas

As árvores do W3 já são melhores, mas revisar o corredor para:
- evitar clones próximos;
- variar idade/porte;
- podas sob fiação;
- covas/canteiros mais naturais;
- raízes/sujeira leve em alguns pontos;
- garantir circulação nas calçadas;
- não bloquear portões/garagens.

---

## 8. Gate visual

Gerar novas capturas reais em:
`ArtSource/Blender/World/Reviews/W3_1/`

Mínimo:
1. rua com carros novos;
2. outra rua com variedade de veículos;
3. quarteirão com variantes de fundo;
4. close de fachada;
5. grama melhorada;
6. talude/arrimo;
7. Apto 12 interior;
8. Oficina interior;
9. Mercearia interior;
10. decals;
11. rua arborizada;
12. visão geral do corredor;
13. comparação W3 × W3.1.

Classificar:
- PASS;
- PARTIAL PASS;
- NEEDS_FIX.

PASS somente se os carros e fundos não parecerem mais placeholders evidentes nas vistas principais.

---

## 9. Validação

Ao final:
- reabrir slice e arquivos alterados em Blender novo;
- masterplan/rotas continuam PASS;
- IDs/GP_/SLOT_/PROXY_ idênticos;
- 9 heróis preservados;
- 13.003 lotes preservados;
- 181 subcélulas preservadas;
- registrar impacto de tris/instâncias/texturas;
- working tree limpa.

---

## 10. Documentação

Criar:
`Docs/W3_1_VISUAL_POLISH_GATE.md`

Atualizar:
`Docs/STATUS_IMPLEMENTACAO.md`

Não reescrever histórico do W3.

---

## 11. Git

Branch:
`claude/w1-masterplan`

Ao terminar:
- commit;
- push;
- working tree limpa;
- informar SHA final.

Não fazer merge no main.

## Regra de autonomia

Trabalhe até concluir a etapa sem pedir confirmação para microdecisões.
Se encontrar erro técnico, corrija e rerode.
Não tocar nos arquivos de integração Unity da branch do GPT.
