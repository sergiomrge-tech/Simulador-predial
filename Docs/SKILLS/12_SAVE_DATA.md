# 12 — Save e dados

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O save atual já é v1 com flags de versão (`servicePresenceVersion`, `chapterOneDataVersion`). A regra é preservar compatibilidade e nunca serializar GameObjects.

## Save e dados

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Newtonsoft Json (com.unity.nuget.newtonsoft-json)](https://docs.unity3d.com/Packages/com.unity.nuget.newtonsoft-json@latest) | MIT | via Package Manager | — | **RECOMMENDED** | SAFE_TO_USE | referência | Saves versionados com migração (JObject), mais flexível que JsonUtility. |
| [MessagePack-CSharp](https://github.com/MessagePack-CSharp/MessagePack-CSharp) | MIT | v3.1.11 / `242bdad51f89` | 2026-10-03 | **OPTIONAL** | REVIEW_REQUIRED | referência | Serialização binária rápida. |

**Riscos**

- **MessagePack-CSharp**: Saves binários dificultam depuração e migração; JSON primeiro.

## Workflow recomendado

- **Versionamento**: `saveVersion` + migrações encadeadas (v1→v2→…) testadas com fixtures de saves reais anonimizados (EditMode).
- **Escrita atômica**: gravar em `slot.tmp`, `Flush(true)`, renomear para `slot.json` (o `File.Replace` mantém backup `slot.bak`); manter 3 backups rotativos.
- **Corrupção**: validar o JSON e o hash ao carregar; se falhar, oferecer o último backup válido.
- **Perfis**: pasta por perfil; nomes de arquivo estáveis (compatível com Steam Auto-Cloud sem código).
- **Dados de conteúdo**: JSON com schema e validador (como no masterplan); IDs estáveis; geradores donos dos arquivos gerados.

