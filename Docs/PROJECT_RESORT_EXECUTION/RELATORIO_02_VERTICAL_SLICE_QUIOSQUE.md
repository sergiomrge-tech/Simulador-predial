# Relatório — Fase 02: Vertical slice do quiosque

Data: 2026-10-06. Gate: **PASS em teste automatizado; pendente: sessão humana com teclado e mouse.**

## Loop entregue
casa (Apto 12, a ~150 m do quiosque) → praia → **abrir** o quiosque (placa verde no balcão) → conferir estoque (caixa do fornecedor) → atender → vender → receber → **fechar** o quiosque/caixa (placa ou 22:00) → resumo do dia (fechamento de caixa, salva) → voltar para casa → **dormir** na cama do Apto 12 → manhã seguinte na porta de casa.

## O que foi feito nesta fase
- **Produtos** (data-driven em `Sim/Catalog.cs`): água, refrigerante, suco/água de coco, cerveja, lanche, salgado, milho e picolé (os seis mínimos + dois).
- **Abrir/fechar**: o quiosque só recebe clientes aberto; fechar encerra o dia assim que a fila é atendida. O dia nunca começa aberto.
- **Casa e dormir**: kitnet modelada (porta de 2,5 m, cozinha, mesa, cama, banheiro, guarda-roupa), cama como interação "Dormir", disponível só depois do fechamento. O Lar foi aproximado da praia (150 m) para a rotina caber.
- **Save**: o fechamento salva com `dayClosed`; recarregar retoma na manhã seguinte sem repetir o dia (dinheiro, estoque, reputação e dia preservados).
- Mercado (HUD) compactado para caber 8 produtos e 4 melhorias.

## Verificação (PlayMode, `LoopTests`, 8 testes no total passando)
Dois dias consecutivos completos (um fechado pela placa às ~17h, outro pelo relógio), cada um com abertura, estoque, atendimento, fechamento de caixa, ida para casa, sono e novo dia; depois recarga da cena confirmando dia, dinheiro, estoque e reputação. Capturas reais da Unity em `ArtSource/Blender/World/Reviews/R5/`.

## Limitações
- Sem sessão humana: o ritmo, a clareza do HUD e a vontade de repetir o dia não foram avaliados por uma pessoa (o gate de diversão da fase 02 precisa disso).
- O jogo ainda não tem noite visual completa nem sono animado; a UI é IMGUI provisória.
- A geladeira/freezer e as prateleiras do quiosque são decorativas (o estoque vive no modelo de dados).
- Aprovação da fase 02 para avançar à 03 depende de uma sessão humana curta.
