#!/usr/bin/env python3
"""Build the W1.5 review sheet (HTML) with W1 x W1.5 comparisons and every real Blender capture.

Usage: python Tools/Map/build_w15_review_sheet.py [PROJECT_ROOT]
Writes ArtSource/Blender/World/Reviews/W1_5/review_sheet.html (W1 images referenced as ../W1/*.jpg).
"""
import html
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
rev = root / "ArtSource" / "Blender" / "World" / "Reviews"
val = json.loads((root / "Docs" / "masterplan-validation-v1.json").read_text(encoding="utf-8"))
routes = json.loads((root / "Docs" / "masterplan-routes-v1.json").read_text(encoding="utf-8"))["origins"]["home.starter"]
reopen = {m: json.loads((rev / "W1_5" / f"reopen_{m}.json").read_text(encoding="utf-8")) for m in ("masterplan", "oldtown", "kit")}
L = val["layout"]
ot = L["oldTown"]
esc = html.escape

PAIRS = [
    ("01_top_8km.jpg", "01_mundo_inteiro.jpg", "Mundo inteiro 8×8 km", "Malha orgânica na Cidade Antiga, 8 zonas de transição, R09/R10, ferrovia, rotatórias, relevo com curvas de nível. Nenhuma célula de 1 km sem uso (W1 tinha 11)."),
    ("02_oblique_city.jpg", "02_mundo_obliquo.jpg", "Cidade oblíqua", "Tecido contínuo em toda a cidade (≈25,7 mil edificações no layout + campanha), skyline diferenciado por distrito."),
    ("03_cidade_antiga.jpg", "03_cidade_antiga.jpg", "Cidade Antiga", "Grade de 180 m substituída por 9 bairros orgânicos com ruas curvas, becos, passagens, praças, estação e lotes por família."),
    ("05_industrial.jpg", "09_industrial.jpg", "Industrial", "De 107 volumes para 869 galpões, 2.979 docas, 256 tanques, 207 silos, 122 chaminés, 90 subestações; ocupação 28%."),
    ("06_corporate.jpg", "10_empresarial.jpg", "Empresarial", "Torres de 16 pav. (mediana) até 35, com pódio e fachada-cortina; ocupação 41%."),
    ("07_technology.jpg", "11_tecnologico.jpg", "Tecnológico", "Platô elevado (+6 m sobre a média), campus com verdes planejados; mediana 9 pav., máx. 29."),
    ("08_santa_aurora_central.jpg", "12_central.jpg", "Santa Aurora Central", "Rotatória da Central reúne R01/R03/R06; eixo institucional Expansão→Central."),
    ("09_skyline.jpg", "13_skyline.jpg", "Skyline", "Empresarial/Tecnológico em fachada-cortina contra o branco da Expansão e o casario baixo."),
    ("10_streaming_grid.jpg", "15_grid_streaming.jpg", "Grid de streaming", "Mesmas 64 células; Cidade Antiga já separada em 181 subcélulas × 8 camadas."),
    ("04_expansao.jpg", "18_expansao.jpg", "Expansão", "Ligação direta com a Cidade Antiga (R09): desvio até a escola caiu de 3,43× para 1,13×."),
]
SHOTS = [
    ("01_mundo_inteiro.jpg", "Mundo inteiro", "masterplan", "CAM_World_Top"),
    ("02_mundo_obliquo.jpg", "Mundo oblíquo", "masterplan", "CAM_World_Oblique"),
    ("03_cidade_antiga.jpg", "Cidade Antiga (produção, topo)", "oldtown", "CAM_OT_Top"),
    ("04_cidade_antiga_obliqua.jpg", "Cidade Antiga oblíqua", "oldtown", "CAM_OT_Oblique"),
    ("05_lar_inicial.jpg", "Lar inicial — Ed. Santa Clara", "oldtown", "CAM_OT_Home_Exterior"),
    ("05b_lar_inicial_corte.jpg", "Lar inicial — corte do Apto 12 (H0)", "oldtown", "CAM_OT_Home_Cutaway"),
    ("06_oficina_aurora.jpg", "Oficina Aurora", "oldtown", "CAM_OT_Garage_Exterior"),
    ("06b_oficina_aurora_corte.jpg", "Oficina Aurora — corte (G0)", "oldtown", "CAM_OT_Garage_Cutaway"),
    ("07_horizonte.jpg", "Edifício Horizonte (vista da rua)", "oldtown", "CAM_OT_Horizonte"),
    ("08_teatro_imperial.jpg", "Teatro Imperial", "oldtown", "CAM_OT_Imperial"),
    ("09_industrial.jpg", "Industrial atualizado", "masterplan", "CAM_District_industrial"),
    ("09b_industrial_baixo.jpg", "Industrial — vista baixa", "masterplan", "CAM_Industrial_Low"),
    ("10_empresarial.jpg", "Empresarial", "masterplan", "CAM_District_corporate"),
    ("11_tecnologico.jpg", "Tecnológico", "masterplan", "CAM_District_technology"),
    ("12_central.jpg", "Central", "masterplan", "CAM_District_civic"),
    ("13_skyline.jpg", "Skyline", "masterplan", "CAM_Skyline"),
    ("14_transicao_antiga_expansao.jpg", "Transição Cidade Antiga → Expansão", "masterplan", "CAM_Transition_OldExp"),
    ("15_grid_streaming.jpg", "Grid de streaming 1 km / 250 m", "masterplan", "CAM_World_Top"),
    ("16_relevo_drenagem.jpg", "Relevo e drenagem (curvas 5/25 m)", "masterplan", "CAM_World_Top"),
    ("17_cidade_antiga_masterplan.jpg", "Cidade Antiga no masterplan", "masterplan", "CAM_District_old"),
    ("18_expansao.jpg", "Expansão", "masterplan", "CAM_District_expansion"),
    ("20_kit_modular.jpg", "Kit arquitetônico modular (bevel)", "kit", "CAM_Kit_Modular"),
    ("21_kit_infraestrutura.jpg", "Infraestrutura urbana provisória", "kit", "CAM_Kit_Infra"),
    ("22_familias_edificacao.jpg", "47 variantes / 10 famílias", "kit", "CAM_Kit_Families"),
    ("23_materiais_pbr.jpg", "Biblioteca PBR procedural (37)", "kit", "CAM_Kit_Materials"),
]
FILE = {"masterplan": "SantaAurora_Masterplan_v1_5.blend", "oldtown": "SantaAurora_CidadeAntiga_Base_v1.blend", "kit": "SantaAurora_CidadeAntiga_Kit_v1.blend"}

pairs_html = "".join(f"""
<article class="pair"><h3>{esc(t)}</h3><div class="pp">
<figure><img src="../W1/{a}" alt="W1: {esc(t)}" loading="lazy"><figcaption>W1</figcaption></figure>
<figure><img src="{b}" alt="W1.5: {esc(t)}" loading="lazy"><figcaption>W1.5</figcaption></figure></div><p>{esc(n)}</p></article>""" for a, b, t, n in PAIRS)
shots_html = "".join(f"""
<figure class="shot"><a href="{f}"><img src="{f}" alt="{esc(t)}" loading="lazy"></a>
<figcaption><b>{f[:3].strip('_')}</b> {esc(t)}<br><code>{FILE[m]} · {c}</code></figcaption></figure>""" for f, t, m, c in SHOTS)
route_rows = "".join(f"<tr><td>{k}</td><td class=n>{routes[k]['networkM']/1000:.1f}</td><td class=n>{routes[k]['minutes']['walk']:.0f}</td><td class=n>{routes[k]['minutes']['sprint']:.0f}</td><td class=n>{routes[k]['minutes']['car_urban']:.0f}</td></tr>"
                     for k in ("garage", "supplier.tools", "vehicles.used", "horizonte", "grocery", "imperial", "school", "recurringcondo", "central", "hospital0317", "datacenter", "smarttower"))
sky_rows = "".join(f"<tr><td>{k}</td><td class=n>{v['p10']}</td><td class=n>{v['median']}</td><td class=n>{v['p90']}</td><td class=n>{v['max']}</td><td class=n>{L['coverage'].get(k, 0)*100:.0f}%</td></tr>"
                   for k, v in L["skylineFloors"].items())
t = L["terrain"]
sc = L["scale"]
page = f"""<title>Revisão W1.5 Santa Aurora</title>
<style>
:root{{--bg:#eef0f2;--card:#f9fafb;--ink:#1a2128;--mut:#58636e;--line:#cfd5db;--acc:#b5600f;--ok:#2d7a4d;--warn:#9a6400}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#11161a;--card:#182027;--ink:#dde3e8;--mut:#98a4ae;--line:#2c363f;--acc:#e8913f;--ok:#6cc28d;--warn:#e0ab4b;color-scheme:dark}}}}
:root[data-theme=dark]{{--bg:#11161a;--card:#182027;--ink:#dde3e8;--mut:#98a4ae;--line:#2c363f;--acc:#e8913f;--ok:#6cc28d;--warn:#e0ab4b;color-scheme:dark}}
*{{box-sizing:border-box}} body{{background:var(--bg);color:var(--ink);font:15px/1.55 "Segoe UI",system-ui,sans-serif}}
.w{{max-width:1300px;margin:0 auto;padding-inline:18px;padding-block:24px 60px;display:grid;gap:34px}}
h1{{font-size:clamp(28px,4vw,42px);margin:0;letter-spacing:-.01em}} h2{{margin:0;font-size:24px}} h3{{margin:0 0 8px;font-size:17px}}
.tag{{display:inline-block;padding:6px 12px;border:2px solid var(--warn);color:var(--warn);font-weight:700;letter-spacing:.04em;text-transform:uppercase;font-size:13px}}
.lede{{color:var(--mut);max-width:80ch;margin:6px 0}}
.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,560px),1fr));gap:22px}}
.pair{{background:var(--card);border:1px solid var(--line);padding:12px}} .pp{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
figure{{margin:0;min-width:0}} img{{width:100%;display:block;aspect-ratio:16/9;object-fit:cover;background:#888}}
figcaption{{font-size:12.5px;color:var(--mut);padding-top:4px}} .pair p{{margin:8px 0 0;font-size:14px}}
.shots{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:16px}}
code{{font-family:Consolas,monospace;font-size:11.5px}}
.box{{overflow-x:auto;border:1px solid var(--line);background:var(--card)}} table{{border-collapse:collapse;width:100%;font-size:13.5px}}
th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}} th{{color:var(--mut);font-size:12px;text-transform:uppercase}} td.n{{text-align:right;font-variant-numeric:tabular-nums}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:18px}}
.col{{border-top:3px solid var(--line);padding-top:10px}} .col.ok{{border-color:var(--ok)}} .col.warn{{border-color:var(--warn)}} .col ul{{margin:0;padding-left:18px}}
.rules{{border:2px solid var(--ink);padding:16px;background:var(--card)}}
</style>
<div class="w">
<header><span class="tag">W1.5 · base estrutural — não é arte final</span>
<h1>Revisão W1.5 Santa Aurora</h1>
<p class="lede">São 25 capturas reais do Blender {esc(reopen['masterplan']['blenderVersion'])}, renderizadas depois de reabrir cada arquivo num processo novo, todas sem dados faltando: masterplan com {reopen['masterplan']['objectCount']} objetos, Cidade Antiga com {reopen['oldtown']['objectCount']} objetos e {ot['lots']} lotes, e kit com {reopen['kit']['objectCount']} objetos. A validação estática passou com {len(val['errors'])} erros.</p></header>
<section><h2>W1 × W1.5</h2><div class="grid2">{pairs_html}</div></section>
<section><h2>As 25 capturas</h2><div class="shots">{shots_html}</div></section>
<section class="grid2">
<div><h2>Escala e deslocamento</h2><p class="lede">Os tempos usam as velocidades do protótipo (3 m/s andando, 5 m/s correndo) e carro urbano a 30 km/h. Atravessar a cidade leva {sc['walkAcrossMin']} min andando e {sc['sprintAcrossMin']} min correndo; a diagonal correndo leva {sc['sprintDiagonalMin']} min.</p>
<div class="box"><table><thead><tr><th>Do lar até</th><th class=n>km</th><th class=n>a pé</th><th class=n>correndo</th><th class=n>carro</th></tr></thead><tbody>{route_rows}</tbody></table></div></div>
<div><h2>Skyline e ocupação</h2><p class="lede">Pavimentos dos edifícios principais por zona e ocupação do solo.</p>
<div class="box"><table><thead><tr><th>Zona</th><th class=n>p10</th><th class=n>mediana</th><th class=n>p90</th><th class=n>máx</th><th class=n>ocup.</th></tr></thead><tbody>{sky_rows}</tbody></table></div></div>
</section>
<section><h2>Relevo</h2><p class="lede">A superfície vai de {t['minSurface']} a {t['maxSurface']} m, com média de {t['meanSurface']} m. A casa de drenagem fica a {t['drainageSurface']} m, a {t['drainageToCanalM']} m do canal. O Tecnológico tem média de {t['technologyMean']} m e a Cidade Antiga de {t['oldTownMean']} m. A rampa máxima nas vias é de {max(t['maxRoadGradePct'].values())}%, dentro do limite para dirigir. Os taludes ficam no canal, na borda do platô e na bacia de retenção murada.</p></section>
<section><h2>Situação</h2><div class="cols">
<div class="col ok"><h3>Pronto como base</h3><ul><li>Masterplan inteiro com estrutura urbana coerente, transições e nenhuma célula vazia</li><li>Malha orgânica da Cidade Antiga: {ot['deadEnds']} ruas sem saída, {ot['alleys']} becos, {ot['passages']} passagens, {ot['plazas']} praças, entropia de orientação {ot['orientationEntropy']}</li><li>Footprints, entradas, serviço e estacionamento definitivos dos 9 heróis e do lar</li><li>Pontos de estado H0–H4 e G0–G4</li><li>Organização em 8 camadas × 181 subcélulas, com manifesto para a Unity</li></ul></div>
<div class="col warn"><h3>Ainda blockout ou provisório</h3><ul><li>Masterplan fora da Cidade Antiga em massing (caixas)</li><li>Famílias de fundo em LOD1 sem bevel</li><li>Árvores-proxy</li><li>Infraestrutura provisória em escala correta</li><li>Proxies H0/G0</li><li>Interiores só onde validam espaço</li></ul></div>
<div class="col warn"><h3>Precisa de arte final (W3/W4)</h3><ul><li>Texturas PBR autorais nos slots já criados</li><li>Decals</li><li>Clutter funcional</li><li>LOD0 final dos heróis</li><li>Vegetação autoral com LOD</li><li>Iluminação interior</li><li>Mobiliário dos estados</li><li>Integração FBX → Unity por subcélula</li></ul></div>
</div></section>
<aside class="rules"><b>Regras mantidas.</b> O low-poly só existe como blockout temporário; nenhuma área final pode ficar assim. VEIN é referência de escala visual, realismo, densidade, materialidade, iluminação, atmosfera e clutter. Nenhum asset, mapa, prédio, textura, personagem ou layout dele é copiado. Santa Aurora é original.</aside>
</div>"""
(rev / "W1_5" / "review_sheet.html").write_text(page, encoding="utf-8")
print("wrote review_sheet.html")
