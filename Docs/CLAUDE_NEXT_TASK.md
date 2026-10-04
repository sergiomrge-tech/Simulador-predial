# CLAUDE NEXT TASK — W3.2

## Cidade Antiga — Final Visual Gate

Base:
- W3: `d58c4d2`
- W3.1: `ebeff568`
- relatório: `Docs/W3_1_VISUAL_POLISH_GATE.md`

Objetivo: tentar transformar o mesmo recorte de 15 subcélulas em **PASS visual**, corrigindo apenas as limitações objetivas ainda abertas no W3.1.

Não tocar em:
- Unity;
- C#;
- streaming runtime;
- saves;
- branch `gpt/unity-world-integration`;
- masterplan global;
- cotas do terreno.

---

## 1. Carros de perto — prioridade máxima

Os carros W3.1 já funcionam a 10–40 m, mas ainda ficam facetados a 3–5 m.

Refinar LOD0 das 6 famílias existentes:
- perfil lateral com mais pontos;
- capô e teto com curvatura mais natural;
- para-brisa e vidro traseiro com inclinação coerente;
- painéis de porta;
- caixas de roda mais suaves;
- aros com raios simples;
- pneus com ombro mais natural;
- interior mínimo visível pelo vidro:
  - bancos dianteiros;
  - banco traseiro;
  - painel;
  - volante;
  - console simples;
- espelhos com haste;
- faróis e lanternas com volume interno simples.

Preservar:
- famílias;
- IDs;
- distribuição;
- instancing;
- LOD1/proxy;
- ausência de marcas reais.

Não aumentar custo sem controle:
- LOD0 alvo aproximado: 12k–22k tris por família;
- LOD1 continua agressivo;
- proxy continua para distância.

---

## 2. Repetição aérea — telhados e volumes

A vista aérea ainda denuncia repetição das famílias W2.

No mesmo recorte, introduzir variação autoral de cobertura e silhueta:
- platibandas com alturas diferentes;
- telhados coloniais parciais;
- telha fibrocimento;
- telhado metálico;
- laje com caixa d’água;
- laje com reservatório menor;
- coberturas de escada;
- anexos de fundos;
- claraboias simples;
- antenas;
- placas solares ocasionais;
- condensadoras;
- varais;
- chaminés/exaustores;
- pequenos volumes técnicos.

Regra:
- variar por quarteirão/lote com seed determinística;
- evitar poluição visual;
- manter coerência socioeconômica do bairro;
- não remodelar toda Santa Aurora.

---

## 3. Máscara de fachada para decals

Corrigir cartazes/placas caindo sobre vidro.

Criar regra por família que diferencie:
- parede opaca;
- vitrine;
- portão;
- porta;
- janela;
- faixa de marquise.

Decals devem preferir:
- parede cheia;
- muros;
- pilares;
- tapumes;
- platibandas;
- portões apropriados.

Nunca posicionar automaticamente cartaz grande no centro de vitrine transparente.

---

## 4. Interiores vistos do exterior

No slice W3/W3.1, os heróis entram por link e a iluminação interna não é lida corretamente do exterior.

Resolver no recorte sem tocar na Unity:
- verificar como os links dos 4 heróis principais entram no slice;
- garantir que luzes internas necessárias estejam visíveis no render do slice;
- preservar os arquivos-fonte dos heróis;
- não duplicar luzes desnecessariamente;
- Lar, Oficina, Horizonte e Mercearia precisam parecer ocupados/legíveis do lado de fora;
- evitar vazamento de luz através de paredes.

---

## 5. Rua de proximidade

Criar ao menos duas cenas/câmeras em altura humana com:
- carro a 3–5 m;
- carro a 10–15 m;
- fachada de comércio;
- árvore;
- calçada;
- clutter;
- decal;
- prédio de fundo.

Essas capturas serão o teste principal do gate.

---

## 6. Performance

W3.1 já subiu bastante:
- 8,53 M mesh tris;
- 31,78 M tris instanciados;
- 116.713 instâncias GN.

W3.2 não pode crescer de forma descontrolada.

Registrar:
- meshTris;
- instancedTris;
- object count;
- material count;
- image count;
- tamanho do .blend;
- custo adicional dos carros LOD0;
- custo adicional dos telhados/volumes.

Preservar estratégia de LOD já existente.

---

## 7. Capturas reais

Salvar em:
`ArtSource/Blender/World/Reviews/W3_2/`

Mínimo:
1. carro hatch a 3–5 m;
2. sedan/SUV a 3–5 m;
3. van/picape de serviço;
4. rua completa em primeira pessoa;
5. segunda rua em primeira pessoa;
6. vista aérea mostrando telhados variados;
7. quarteirão oblíquo;
8. fachada comercial sem decal sobre vidro;
9. Lar visto de fora com interior legível;
10. Oficina vista de fora;
11. Horizonte visto de fora;
12. Mercearia vista de fora;
13. comparação W3.1 × W3.2 carros;
14. comparação W3.1 × W3.2 aérea;
15. visão geral do corredor.

Se a GPU voltar a falhar:
- não mascarar o problema;
- registrar a falha;
- usar render CPU se viável;
- não afirmar captura nova se não foi renderizada.

---

## 8. Gate

Criar:
`Docs/W3_2_FINAL_VISUAL_GATE.md`

Classificação:
- PASS;
- PARTIAL PASS;
- NEEDS_FIX.

PASS somente se:
- carro a 3–5 m não parecer placeholder;
- vista aérea não parecer repetição óbvia de famílias;
- decals não atravessarem vitrines;
- os 4 heróis principais tiverem leitura interna convincente do exterior;
- integridade e performance permanecerem controladas.

Não rebaixar padrões para obter PASS.

---

## 9. Validação obrigatória

Ao final:
- reabrir slice em processo novo;
- reabrir arquivos de heróis alterados;
- masterplan/rotas continuam PASS;
- IDs/GP_/SLOT_/PROXY_ idênticos;
- 9 heróis preservados;
- 13.003 lotes preservados;
- 181 subcélulas preservadas;
- 15 células no recorte;
- licença/proveniência atualizadas se necessário;
- working tree limpa.

---

## 10. Git

Branch:
`claude/w1-masterplan`

Ao terminar:
- atualizar `Docs/STATUS_IMPLEMENTACAO.md`;
- commit;
- push;
- working tree limpa;
- informar SHA final.

Não fazer merge no main.

## Autonomia

Trabalhe até concluir esta etapa sem pedir confirmação para microdecisões.
Se encontrar erro técnico, corrija e rerode.
Não iniciar outro distrito.
