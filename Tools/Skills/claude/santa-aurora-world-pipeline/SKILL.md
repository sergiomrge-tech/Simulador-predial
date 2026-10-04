---
name: santa-aurora-world-pipeline
description: >
  Pipeline do mundo de Santa Aurora (Facility Ops): validar o masterplan, gerar os .blend (masterplan v1.5,
  Cidade Antiga base, kit), reabrir/auditar e gerar capturas e review sheets. Use ao mexer em
  ArtSource/Blender/World, Tools/Map ou Tools/Blender, ou ao preparar um gate W1.5/W2.
---

# Santa Aurora — pipeline do mundo

Autoria: projeto Facility Ops (W1.5, 2026-10-03). Licença: a do repositório.

## Regras que nunca mudam
- IDs da campanha/vida em `ArtSource/Blender/World/masterplan_spec_v1.json` são estáveis. Nunca renomeie nem remova.
- Não edite JSON gerado sem atualizar o gerador. Spec, heróis (`OldTown/oldtown_heroes_v1.json`) e registry são fontes; os relatórios são gerados.
- Low-poly só como blockout temporário. Arte final: PBR, bevel, decals, clutter, LOD (Art Bible).
- VEIN é referência de patamar visual, nunca fonte para copiar assets, layouts, texturas ou mapas.
- Não tocar o protótipo Unity, saves ou `.meta` sem tarefa dedicada.

## Fonte única de layout
`Tools/Map/` é Python puro e determinístico (seed fixa):
- `sa_geom.py`: OBB, SAT, hash espacial, filetes de curva, ruído.
- `sa_terrain.py`: relevo (canal é o eixo mais baixo); `surface()` para vias/lotes e `ground()` com taludes do canal.
- `urban_fabric.py`: famílias, malha orgânica, grafo de ruas, empacotamento de lotes por cadeia de ruas, compositor industrial.
- `oldtown_layout.py`: Cidade Antiga (9 bairros, ruas principais, becos, praças, ferrovia, lotes, pontos de infraestrutura).
- `masterplan_layout.py`: cidade inteira (vias suavizadas, rotatórias, zonas de transição, distritos, vegetação, verificações).

## Comandos
```powershell
python Tools/Map/validate_masterplan.py .          # gate estático -> Docs/masterplan-validation-v1.json
python Tools/Map/masterplan_routes.py .            # rotas pela rede -> Docs/masterplan-routes-v1.json
powershell -ExecutionPolicy Bypass -File Tools/Blender/Run-W15World.ps1   # tudo: valida, gera 3 .blend, reabre, captura
python Tools/Map/build_w15_review_sheet.py .       # review sheet W1 x W1.5
```
O Blender está fora do PATH: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (o runner encontra sozinho).

## Saídas
- `ArtSource/Blender/World/SantaAurora_Masterplan_v1_5.blend` (o W1 `..._v1.blend` fica intacto).
- `ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend` + `oldtown_streaming_manifest_v1.json`.
- `ArtSource/Blender/Kits/SantaAurora_CidadeAntiga_Kit_v1.blend` (assets marcados).
- Capturas e `reopen_*.json` em `ArtSource/Blender/World/Reviews/W1_5/`.

## Convenções
- Coordenadas do spec: x = leste, z = norte. No Blender, z do spec vira Y. Metros 1:1.
- Streaming: `SA_Mxx_yy` (1 km) / `SA_Mxx_yy_Sxx_yy` (250 m). Camadas: Terrain, Roads, Architecture, Infrastructure, Props, Vegetation, Lighting, Gameplay.
- Objetos de herói: `HERO_<id>__<parte>__F<nn>` (um por pavimento) e `__ROOF`. Marcadores: `GP_*`, slots de estado `SLOT_<id>__<H0..H4|G0..G4>__<item>`.
- Edificações de fundo: instâncias por Geometry Nodes (um objeto de pontos por subcélula, atributos `variant`, `rot` e `scl`).

## Antes de declarar um gate
1. Validação PASS e `reopen_*.json` com `passed: true` e `missingData: []`.
2. Abrir e olhar as capturas novas. Scripts executando não bastam.
3. Atualizar o relatório em `Docs/` e o `STATUS_IMPLEMENTACAO.md`.
4. Commits organizados, push e árvore limpa (protocolo em `Docs/CLAUDE_AUTONOMOUS_PROTOCOL.md`).
