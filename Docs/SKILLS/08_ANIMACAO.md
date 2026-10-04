# 08 — Animação

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O foco é animação em primeira pessoa e de máquinas. Personagens completos ficam para depois.

## Animação

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Animation Rigging](https://docs.unity3d.com/Packages/com.unity.animation.rigging@latest) | Unity Companion License | via Package Manager | — | **RECOMMENDED** | SAFE_TO_USE | referência | IK das mãos em primeira pessoa (segurar ferramentas, apertar, inspecionar). |

## Workflow recomendado

- **Blender**: rig de braços em primeira pessoa (armature com controles IK/FK); ações por ferramenta (pegar, usar, guardar, inspecionar) exportadas como clips FBX separados; máquinas (portas, bombas, ventiladores, disjuntores) com animação por objeto ou feitas na Unity.
- **Unity**: Animator com camadas (base, mãos, aditivo de respiração); Animation Rigging para ajustar a mão ao alvo (registro, disjuntor, maçaneta); Timeline para eventos narrativos curtos.
- Rigs humanoides de NPC: retarget pelo Avatar Humanoid; biblioteca CC0 ou captura própria (registrar licença).

