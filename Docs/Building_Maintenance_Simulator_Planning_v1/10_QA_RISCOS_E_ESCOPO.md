# QA, Riscos e Controle de Escopo

## 1. Maiores riscos

### Risco A — virar um simulador superficial

Mitigação:

Validar diagnóstico real antes de criar muitos mapas.

### Risco B — sistemas técnicos complexos demais

Mitigação:

Usar abstrações consistentes e divertidas. O jogo não é treinamento profissional.

### Risco C — conteúdo caro

Mitigação:

Construir mapas modulares e falhas combinatórias.

### Risco D — aparência de asset flip

Mitigação:

Curadoria visual, materiais consistentes, iluminação própria, props customizados, UI e identidade fortes.

### Risco E — progressão virar grind

Mitigação:

Upgrades frequentes e significativos; repetir pouco o mesmo tipo de missão.

### Risco F — Unity project debt

Mitigação:

Arquitetura modular, testes e ferramentas internas desde cedo.

## 2. Escopo proibido no MVP

- multiplayer;
- mundo aberto;
- tráfego urbano;
- direção veicular realista;
- construção livre;
- clima complexo;
- centenas de NPCs;
- simulação técnica profissional;
- crafting de dezenas de recursos;
- economia online.

## 3. Testes de gameplay

Perguntas essenciais:

- o jogador entende o sintoma?
- existem pelo menos 2 hipóteses plausíveis?
- o teste ajuda a reduzir hipóteses?
- a solução parece descoberta, não entregue?
- o reparo tem feedback satisfatório?
- o jogador sabe que terminou?
- o pagamento parece justo?

## 4. Testes técnicos

- save/load;
- migração de save;
- missões não bloqueiam;
- falhas sempre têm solução;
- nenhuma missão exige item impossível;
- inventário não perde item;
- economia não entra em estado negativo impossível;
- interação funciona em diferentes FPS;
- controles remapeáveis antes do lançamento.

## 5. Mission Validator

Automatizar validação:

- causa tem evidências suficientes;
- ferramentas exigidas são acessíveis;
- peça existe;
- local suporta falha;
- recompensa cobre custo mínimo;
- estado final é alcançável.

## 6. Performance

Testar em três perfis:

- mínimo;
- recomendado;
- desenvolvimento.

Meta padrão: 60 FPS em 1080p no hardware recomendado.

## 7. Acessibilidade

Planejar:

- FOV ajustável;
- sensibilidade;
- remapeamento;
- legendas;
- tamanho de UI;
- redução de movimento/camera shake;
- opção de destacar interações sem mostrar solução;
- modos de daltonismo quando o uso de cor for funcional.

## 8. Critério de versão jogável

Nunca chamar um build de “jogável” apenas porque abre.

Deve existir:

- loop completo;
- objetivo;
- sucesso/falha;
- save mínimo;
- sem blockers conhecidos;
- build Windows testado.
