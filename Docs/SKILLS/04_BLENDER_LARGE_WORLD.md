# 04 — Blender: grandes cenas

Curadoria W1.5 (2026-10-03). Fonte de dados: `Tools/Skills/catalog.json` (gerado por `Tools/Skills/build_catalog.py`). Nada aqui foi instalado ou executado.

O W1.5 já trabalha em grande escala: 13 mil edificações instanciadas, 181 subcélulas e 8 camadas em um `.blend` de 28 MB que reabre em segundos.

## Blender: grandes cenas

| Item | Licença | Versão / commit | Atualizado | Prioridade | Segurança | Armazenamento | Valor para o projeto |
|---|---|---|---|---|---|---|---|
| [Asset Browser + bibliotecas vinculadas](https://docs.blender.org/manual/en/latest/editors/asset_browser.html) | GPL | 5.2 | — | **RECOMMENDED** | SAFE_TO_USE | referência | Kit como biblioteca de assets (já marcado), linking entre .blend por camada/célula. |
| [Blender Asset Tracer (BAT v2)](https://projects.blender.org/blender/blender-asset-tracer) | GPL-2.0-or-later | v2 (requer Blender 5.1+) | — | **OPTIONAL** | REVIEW_REQUIRED | referência | Lista/empacota dependências de .blend (texturas, libs) — útil quando entrarem texturas e links. |

**Riscos**

- **Blender Asset Tracer (BAT v2)**: Ferramenta Python externa: revisar antes de executar.

## Workflow recomendado

- **Coleções por camada × célula** (`OT_<Camada>_SA_Mxx_yy`) e objetos por subcélula. Facilita exportação, revisão e streaming.
- **Instancing por GN** com bibliotecas ocultas; uma malha por variante. Nunca realizar instâncias em massa no arquivo-fonte.
- **Bibliotecas vinculadas**: quando o kit amadurecer, os arquivos de distrito *vinculam* `SantaAurora_CidadeAntiga_Kit_v1.blend` (Asset Browser) em vez de copiar. Usar caminhos relativos e verificar com BAT antes de empacotar.
- **Proxies e LOD**: LOD1/2 gerados por decimate controlado ou simplificação manual por variante; HLOD por quarteirão (malha única + atlas) para distâncias acima de 750 m.
- **Desempenho do viewport**: exibir instâncias como *bounds* fora do núcleo; *simplify* de subdivisão; cores de objeto no Workbench.
- **Automação**: todo o arquivo é reprodutível por script. Mudanças manuais em heróis devem migrar para o gerador ou para um `.blend` de herói vinculado.

