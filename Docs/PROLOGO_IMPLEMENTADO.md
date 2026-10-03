# Prólogo jogável — O primeiro chamado

Base: prólogo da lore original de PROJECT FACILITY. Edifício Horizonte, corredor do quarto andar, Helena Prado e orientação remota de Augusto “Guto” Moreira. Primeira pessoa; Unity 6000.6.2f1.

## Percurso

1. Na garagem, aceitar o primeiro chamado. Guto apresenta sua filosofia e Helena descreve o defeito; as mensagens ficam no diário do tablet.
2. Inspecionar QD-01 e LM-01 e reunir duas medições distintas. A inspeção da luminária identifica isolamento danificado e marcas de aquecimento.
3. Opcionalmente religar QD-01 com a ferramenta 7. As luzes acendem, mas cinco segundos de aquecimento virtual provocam novo desarme. Isso não resolve o chamado nem permite pagamento.
4. Registrar a hipótese da luminária. Isolar QD-01 com a ferramenta 6 e confirmar ausência de energia fictícia na LM-01 com a ferramenta 5.
5. Substituir o módulo da luminária com a ferramenta 4. Sem isolamento e confirmação, a tentativa é bloqueada sem consumir estoque. Uma hipótese errada ainda pode desperdiçar peça depois da confirmação.
6. Restaurar QD-01 com a ferramenta 7. Aguardar cinco segundos em campo e testar estabilidade com a ferramenta 5 no QD-01. Abrir o tablet, ir à garagem ou explorar prévias pausa o ensaio.
7. Entregar pelo tablet. O jogador retorna à garagem, recebe o pagamento e as mensagens finais; a conclusão é persistida e não pode conceder outro pagamento.

Rearmar repetidamente não reinicia um ensaio já em andamento. Uma nova operação de isolamento invalida o teste final anterior. Trocar a peça não reenergiza automaticamente o circuito.

## Persistência e continuidade

O save conserva o estado de isolamento, a confirmação, o componente reparado, o tempo de ensaio, as evidências e o diário. A ausência de missão ativa possui marcador explícito para evitar a criação de um chamado vazio pelo serializador inline da Unity.

Carreiras v1 anteriores conservam economia e chamados existentes. Se um chamado livre já estiver ativo, o jogador pode concluí-lo antes de iniciar o prólogo. A conclusão do prólogo aponta para os três serviços iniciais do Capítulo I, descritos em `CAPITULO_I_IMPLEMENTADO.md`; chamados livres com três causas possíveis também continuam disponíveis. O modo livre não substitui nem conclui a lista autoral.

## Adaptações e limites

A temperatura é um temporizador lógico de cinco segundos, não uma simulação térmica real. Medições usam unidades fictícias. Isolamento, teste e substituição são interações abstratas nos equipamentos; ainda não há desmontagem, mãos animadas ou execução física detalhada. O módulo de luminária usa a categoria de estoque de driver já existente. R$ 320 mais bônus de R$ 80 mantém a economia de teste, sem alegação de balanceamento final.

Guto e Helena aparecem como mensagens no tablet, sem NPCs modelados, voz ou diálogo ramificado. Os demais capítulos, reincidências de outros edifícios, auditoria e finais ainda precisam de implementação própria. Este percurso torna o prólogo verificável e jogável; não conclui a campanha inteira.
