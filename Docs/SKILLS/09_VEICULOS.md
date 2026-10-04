# 09 — Veículos

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O W1.5 mostrou que, do Capítulo II em diante, o veículo é necessário: clientes ficam a 4,6–8,9 km, 26–50 min a pé contra 9–18 min de carro. A arquitetura viária já respeita dirigibilidade (rampas ≤ 6% nas arteriais, rotatórias, acessos).

## Veículos

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [WheelCollider (nativo) + controlador próprio](https://docs.unity3d.com/6000.6/Documentation/Manual/class-WheelCollider.html) | Unity EULA | 6000.6 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Veículo arcade/realista híbrido leve sem dependências; entrar/sair, carga, estacionamento. |

**Notas**

- **WheelCollider (nativo) + controlador próprio**: Evitar sistemas comerciais pesados (NWH/Edy's) até haver necessidade comprovada.

## Workflow recomendado

- Controlador próprio sobre WheelCollider: torque e freio, curvas de aderência simples, assistências (ABS e estabilidade) para um modelo híbrido arcade/realista.
- Interiores legíveis (painel, bancos, carga) como cena de herói pequena; entrar/sair com transição de câmera em primeira pessoa.
- Carga e inventário do veículo por slots físicos (caixas, ferramentas grandes) sincronizados com o inventário de dados.
- Estacionamento: vagas já definidas nos heróis (`GP_*__parking__*`); validar raio de giro de utilitário (V2/V3) na oficina.
- Tráfego futuro: grafo viário do manifesto vira grafo de navegação de tráfego; não implementar antes do vertical slice.

