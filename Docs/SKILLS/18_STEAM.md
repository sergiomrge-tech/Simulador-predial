# 18 — Steam (preparar; não integrar ainda)

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

A integração Steam fica para depois do vertical slice. Agora só se preparam as escolhas e a compatibilidade.

## Steam

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Steamworks SDK + documentação](https://partner.steamgames.com/doc/home) | Steamworks SDK Access Agreement (parceiro) | — | — | **RECOMMENDED** | REVIEW_REQUIRED | referência | Conquistas, stats, Steam Cloud, Rich Presence, Steam Input, SteamPipe (upload de depots). |
| [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET) | MIT | 2025.164.1 / `ba71581f1ed7` | 2026-08-07 | **RECOMMENDED** | REVIEW_REQUIRED | referência | Wrapper fiel da API Steamworks para Unity. |
| [Facepunch.Steamworks](https://github.com/Facepunch/Facepunch.Steamworks) | MIT | 2.5.2 / `e5d449049987` | 2026-09-15 | **OPTIONAL** | REVIEW_REQUIRED | referência | Wrapper C# idiomático alternativo. |
| [Steam Cloud (Auto-Cloud)](https://partner.steamgames.com/doc/features/cloud) | Serviço Steam | — | — | **RECOMMENDED** | SAFE_TO_USE | referência | Saves em pasta fixa por perfil, nomes estáveis e arquivos pequenos -> compatível com Auto-Cloud sem código. |

**Riscos**

- **Steamworks SDK + documentação**: Exige conta de parceiro; não integrar ainda.
- **Steamworks.NET**: Integrar só na etapa Steam; fixar versão compatível com o SDK.

## Workflow recomendado

- Wrapper: Steamworks.NET (MIT, fiel à API) como padrão; Facepunch.Steamworks como alternativa.
- Steam Cloud via Auto-Cloud: saves em pasta fixa por perfil, arquivos pequenos e nomes estáveis (doc 12).
- Conquistas e estatísticas por IDs estáveis definidos em dados; Rich Presence com região e chamado atual.
- Steam Input: mapear as ações do Input System (já em uso) para os *action sets* do Steam.
- SteamPipe: upload de depots via ContentBuilder num script separado, sem credenciais no repositório.

