# 20 — Pipeline Blender → Unity e validação de assets

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

A skill própria `blender-to-unity-export` registra as convenções planejadas. Elas precisam ser validadas com uma subcélula piloto antes da produção em massa.

## Pipeline Blender → Unity

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| Skill própria: blender-to-unity-export (plano) (`Tools/Skills/pipeline/blender-to-unity-export/SKILL.md`) | Licença do repositório | 0.1 plano (2026-10-03) | — | **ESSENTIAL** | SAFE_TO_USE | salvo: `Tools/Skills/pipeline/blender-to-unity-export` | Convenções FBX/nomes/LOD/colisores/pivôs/manifesto para a integração W5; marcada como plano a validar. |
| [glTF-Blender-IO](https://github.com/KhronosGroup/glTF-Blender-IO) | Apache-2.0 | 2.79 / `6e6990a22385` | 2026-10-03 | **RECOMMENDED** | SAFE_TO_USE | referência | Export glTF embutido; útil para revisão/web. |
| [Exportador FBX nativo](https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html) | GPL | 5.2 | — | **ESSENTIAL** | SAFE_TO_USE | referência | Formato padrão Blender -> Unity do projeto. |

## Workflow recomendado

1. **Piloto**: exportar 1 subcélula do núcleo + lar + oficina em FBX (escala 1, -Z frente, Y cima) e recriar as instâncias de fundo na Unity a partir do manifesto.
2. **AssetPostprocessor**: remapear materiais por nome, gerar LODGroup por sufixo, colisores por `UCX_`/`_COL`, rótulos Addressables por subcélula.
3. **Validador de importação**: escala, UV ausente, material ausente, colisor ausente, LOD ausente, malha acima do orçamento, textura grande demais, nome fora do padrão. Falha visível no console e em teste EditMode.
4. Exportação em lote por script Blender (subcélula × camada) com relatório JSON comparável entre execuções.

