# PROJECT RESORT — Referências Visuais Oficiais

Este arquivo é a referência visual oficial para o início da produção do PROJECT RESORT.

## Regra de uso

Estas imagens são **concept art de direção visual**, não assets finais do jogo.

Use-as para orientar:
- arquitetura;
- materiais;
- escala;
- densidade de props;
- ambientação;
- leitura espacial;
- composição do quiosque;
- relação praia/calçadão/rua;
- progressão visual até o resort cinco estrelas.

NÃO copiar literalmente marcas, logos, rótulos ou elementos comerciais reais.
NÃO usar estas imagens diretamente como textura final do jogo.
NÃO tratar arte conceitual como screenshot real da Unity.

---

## REF 01 — QUIOSQUE INICIAL / INÍCIO DO JOGO

**Função:** direção visual oficial do primeiro empreendimento do jogador.

**OpenArt**
- modelo: Nano Banana 2 Lite
- historyId: `z6ur6UfjhwchNIQCgfhK`
- resolução: 1376×768
- proporção: 16:9

![PROJECT RESORT — Quiosque inicial](https://cdn.openart.ai/watermarked_images/midDvIPdPOqIRg2XgTN9/thumbnail_07972c24_1791318605421.webp)

Link direto:
https://cdn.openart.ai/watermarked_images/midDvIPdPOqIRg2XgTN9/thumbnail_07972c24_1791318605421.webp

### Elementos que devem ser preservados

- quiosque pequeno e humilde;
- madeira envelhecida / estrutura simples;
- balcão aberto;
- geladeira pequena;
- freezer horizontal;
- prateleiras com bebidas e snacks;
- pequeno estoque/reposição;
- mesas e cadeiras simples;
- poucos guarda-sóis;
- praia imediatamente ao lado;
- calçadão bem definido;
- via urbana atrás;
- bairro costeiro habitado;
- palmeiras e vegetação tropical;
- sensação clara de “começo pequeno”.

### O que NÃO fazer

- transformar o quiosque inicial em beach club de luxo;
- aumentar demais a estrutura;
- colocar piscina, spa, lobby ou hotel nesta fase;
- usar arquitetura genérica de resort já no começo.

---

## REF 02 — QUIOSQUE EM OPERAÇÃO / GAMEPLAY

**Função:** orientar o vertical slice jogável e o layout prático do balcão.

**OpenArt**
- modelo: Kling 3 Omni
- historyId: `AXURrNf0t9qgaa5OL7c4`
- resolução: 1360×768
- proporção: 16:9

![PROJECT RESORT — Quiosque em operação](https://cdn.openart.ai/watermarked_images/midDvIPdPOqIRg2XgTN9/thumbnail_96df8167_1791318744789.webp)

Link direto:
https://cdn.openart.ai/watermarked_images/midDvIPdPOqIRg2XgTN9/thumbnail_96df8167_1791318744789.webp

### Usar para modelagem do vertical slice

Priorizar:
- balcão acessível;
- caixa/ponto de pagamento;
- bebidas;
- água;
- refrigerantes;
- sucos;
- snacks;
- pequena área de preparo;
- geladeira;
- freezer;
- caixas/crates de reposição;
- lixeira;
- área de circulação do jogador;
- área de fila;
- 2–4 mesas;
- clientes visíveis;
- leitura clara do fluxo operacional.

### Fluxo espacial esperado

```
entrega/estoque
→ reposição
→ preparação
→ balcão
→ pedido
→ pagamento
→ cliente sai/consome
```

O layout precisa ser reproduzível em primeira pessoa e não apenas bonito em uma imagem.

---

## REF 03 — VISÃO FUTURA / RESORT CINCO ESTRELAS

**Função:** north star visual do projeto. NÃO construir nesta fase.

**OpenArt**
- modelo: Nano Banana 2 Lite
- historyId: `I1kKnxy8lZGE02Ah9Euq`
- resolução: 1376×768
- proporção: 16:9

![PROJECT RESORT — Resort cinco estrelas](https://cdn.openart.ai/watermarked_images/midDvIPdPOqIRg2XgTN9/thumbnail_f20bb783_1791318607434.webp)

Link direto:
https://cdn.openart.ai/watermarked_images/midDvIPdPOqIRg2XgTN9/thumbnail_f20bb783_1791318607434.webp

### Elementos de direção futura

- mesmo litoral;
- mesma identidade de Santa Aurora;
- arquitetura tropical sofisticada;
- integração com praia;
- piscinas em níveis;
- paisagismo abundante;
- pedra natural;
- madeira;
- áreas de descanso premium;
- restaurantes;
- beach club;
- suítes;
- villas/bangalôs;
- circulação elegante;
- iluminação quente;
- sensação de empreendimento monumental.

### Regra central

A progressão visual deve fazer o jogador reconhecer que o resort final nasceu do mesmo terreno onde começou o quiosque.

---

# DIREÇÃO VISUAL GERAL

## Estilo

- realista;
- tropical contemporâneo;
- brasileiro;
- comercial;
- PBR;
- primeira pessoa;
- escala humana;
- arquitetura plausível;
- sem low-poly genérico como direção final.

## Materiais principais

### Fase inicial
- madeira simples;
- metal pintado;
- plástico;
- concreto;
- pedra portuguesa/calçamento;
- tecido de toldo;
- equipamentos comerciais simples.

### Fases avançadas
- madeira tratada premium;
- pedra natural;
- concreto arquitetônico;
- vidro;
- metais escovados;
- paisagismo de alto padrão;
- tecidos e mobiliário premium.

## Progressão visual obrigatória

```
improvisado
→ simples
→ organizado
→ profissional
→ confortável
→ sofisticado
→ premium
→ monumental
```

Não pular diretamente do quiosque improvisado para arquitetura de luxo.

---

# ORDEM PARA CLAUDE

Na fase atual, use prioritariamente:

1. REF 01 — ambiente e identidade;
2. REF 02 — layout operacional;
3. GDD e arquivo `02_VERTICAL_SLICE_QUIOSQUE.md` — regras de gameplay.

REF 03 serve apenas como referência de destino de longo prazo.

Ao modelar:
- respeitar medidas reais;
- manter circulação para CharacterController;
- separar objetos interativos;
- usar IDs persistentes;
- preparar colliders;
- pensar em LOD desde cedo;
- não comprometer FPS por excesso de detalhe pequeno;
- manter objetos de estoque identificáveis;
- garantir acesso pelo jogador em primeira pessoa.

---

# GERAÇÃO E PROVENIÊNCIA

As três referências acima foram geradas especificamente para PROJECT RESORT via OpenArt em 06/10/2026.

São referências de desenvolvimento e direção visual. Não devem ser tratadas como assets finais licenciados para distribuição dentro da build sem revisão de licença e proveniência antes do lançamento.


---

# STARTER PACK LOCAL NO GITHUB

As seis referências principais também devem existir como arquivos PNG locais no repositório em:

`Docs/VISUAL_REFERENCES/PROJECT_RESORT_STARTER_PACK/`

Arquivos:

- `01_PRAIA_SANTA_AURORA_QUIOSQUE_INICIAL.png`
- `02_QUIOSQUE_OPERACAO_BALCAO.png`
- `03_QUIOSQUE_ESTOQUE_REPOSICAO.png`
- `04_CASA_INICIAL_JOGADOR.png`
- `05_PRIMEIRA_POUSADA.png`
- `06_RESORT_CINCO_ESTRELAS_NORTH_STAR.png`

O arquivo `README.md` dessa pasta define a ordem de uso.

## Prioridade imediata

Para a implementação atual do Claude:

1. 01 — localização/identidade;
2. 02 — balcão e loop de atendimento;
3. 03 — estoque e reposição;
4. 04 — rotina da casa.

05 e 06 não autorizam implementação antecipada; são apenas direção visual futura.
