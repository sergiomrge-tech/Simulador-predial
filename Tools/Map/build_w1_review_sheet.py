#!/usr/bin/env python3
"""Build the W1 review sheet (HTML) next to the real Blender captures.

Usage: python Tools/Map/build_w1_review_sheet.py [PROJECT_ROOT]
Reads: Docs/masterplan-routes-v1.json, ArtSource/Blender/World/Reviews/W1/w1_reopen_report.json
Writes: ArtSource/Blender/World/Reviews/W1/review_sheet.html (images referenced relatively)
"""
import html
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
review = root / "ArtSource" / "Blender" / "World" / "Reviews" / "W1"
routes = json.loads((root / "Docs" / "masterplan-routes-v1.json").read_text(encoding="utf-8"))
reopen = json.loads((review / "w1_reopen_report.json").read_text(encoding="utf-8"))
esc = html.escape

DISTRICTS = [("old", "Cidade Antiga"), ("expansion", "Expansão"), ("industrial", "Industrial"),
             ("corporate", "Corporate"), ("technology", "Technology"), ("civic", "Central")]
DNAME = dict(DISTRICTS)

# (file, title, district key or "all", camera, verdict, critique)
SHOTS = [
    ("01_top_8km.jpg", "Visão superior 8×8 km", "all", "CAM_Masterplan_Top · ortho 8400 m", "warn",
     "Os seis distritos e as oito vias são legíveis. 11 de 64 células de 1 km ficam sem distrito; as faixas vazias entre os bairros fazem a cidade parecer um conjunto de ilhas, não um tecido contínuo."),
    ("02_oblique_city.jpg", "Visão oblíqua da cidade", "all", "CAM_Masterplan_Oblique · 30 mm", "warn",
     "Lê como cidade na escala certa, mas plana e uniforme. Fora do Corporate, faltam marcos verticais e topografia; as bordas sul e leste ficam vazias."),
    ("03_cidade_antiga.jpg", "Cidade Antiga", "old", "CAM_District_old · ortho tilt 32°", "block",
     "É o distrito mais denso (23,7% de ocupação), mas a grade perfeita de 180 m contradiz um núcleo histórico nascido da ferrovia e do porto seco. Não há ferrovia modelada. Os locais hero somem na escala do distrito."),
    ("04_expansao.jpg", "Cinturão da Expansão", "expansion", "CAM_District_expansion · ortho tilt 32°", "block",
     "Condomínios, hotel e HQ têm volume e lote corretos. Não há ligação viária direta com a Cidade Antiga: a rota até a escola tem 7,6 km para 2,2 km em linha reta (3,4×). O miolo das quadras de 260 m está vazio (10,7% de ocupação)."),
    ("05_industrial.jpg", "Distrito Industrial", "industrial", "CAM_District_industrial · ortho tilt 32°", "warn",
     "Os pátios da fábrica e do galpão funcionam, e a casa de bombas fica junto ao canal. O tecido de galpões é ralo (107 volumes em 9,3 km²). Faltam ferrovia, porto seco e o ramal que liga o distrito à Cidade Antiga."),
    ("06_corporate.jpg", "Zona Empresarial", "corporate", "CAM_District_corporate · ortho tilt 32°", "ok",
     "A hierarquia lê bem: shopping, hospital 03:17, Vértice e torre do apagão na Av. Santa Aurora. São 28 torres acima de 60 m e máximo de 125 m. Funciona para skyline de cidade média-grande."),
    ("07_technology.jpg", "Distrito Tecnológico", "technology", "CAM_District_technology · ortho tilt 32°", "warn",
     "Tem 8,1 km² para dois locais de campanha e uma residência premium. Com 6,3% de ocupação, o risco aqui é o oposto de pequeno demais: grande e vazio. Data center e smart tower ficam bem separados."),
    ("08_santa_aurora_central.jpg", "Santa Aurora Central", "civic", "CAM_District_civic · ortho tilt 32°", "ok",
     "Campus de 360×420 m com 10 alas e túneis em cruz; R03 chega ao portão sul, R01/R05 passam a sul/norte e R04 sai a leste. Ainda falta um eixo ou praça cívica que anuncie o complexo como final da campanha."),
    ("09_skyline.jpg", "Composição do skyline", "all", "CAM_Skyline · 40 mm, 420 m de altura", "warn",
     "Corporate e Technology formam uma silhueta; a Expansão em primeiro plano lê como subúrbio de média altura. O conjunto parece cidade média-grande, não metrópole."),
    ("10_streaming_grid.jpg", "Grid de streaming", "all", "CAM_Masterplan_Top · grid 1 km + 250 m", "ok",
     "As 64 células SA_M00_00…SA_M07_07 estão nomeadas, com subgrid de 250 m. A célula mais carregada tem 3 locais de campanha, o que é viável para streaming."),
    ("11_district_highlight.jpg", "Destaque dos distritos", "all", "CAM_Masterplan_Top · cores de revisão", "ok",
     "Captura extra, só para revisão: distritos em cores saturadas, sem shells. Mostra a posse resolvida das costuras e a relação de cada local com o seu distrito."),
]

VERDICT = {"ok": "Adequado", "warn": "Atenção", "block": "Bloqueia aprovação"}

# id, district, chapters, verdict, note
LOCS = [
    ("garage", "old", "Prólogo, I, XIV", "ok", "Fica na Av. do Trabalho, a 0,4 km do lar pela rede. Base plausível para começar a pé."),
    ("horizonte", "old", "Prólogo, I, VIII, XIV", "ok", "Fica a 0,76 km da garagem pela rede. Com 37 m, é o prédio mais alto do bairro (o tecido vai a 19 m) e se destaca na malha."),
    ("apartments", "old", "I", "ok", "0,95 km por rua local."),
    ("grocery", "old", "I", "ok", "0,95 km por rua local."),
    ("restaurant", "old", "I", "ok", "1,4 km. Ainda dá para ir a pé."),
    ("workshop", "old", "I", "ok", "0,67 km."),
    ("smalloffice", "old", "I", "ok", "1,2 km."),
    ("imperial", "old", "II", "warn", "Distância correta (1,2 km), mas sem praça ou eixo que o faça funcionar como marco. O lote de 78×96 m some no tecido."),
    ("school", "expansion", "II", "block", "Primeira inspeção de Lara. Rota de 7,6 km para 2,2 km em linha reta, por falta de ligação Old↔Expansão."),
    ("recurringcondo", "expansion", "II", "warn", "Faz sentido como primeiro contrato fora do bairro e pede o V1. A rota de 6,9 km (2,3× a linha reta) vem do mesmo defeito de conexão."),
    ("lostcondo", "expansion", "III", "ok", "Fica a cerca de 700 m do condomínio de Helena. O concorrente vizinho reforça o drama do Cap. III."),
    ("hotel", "expansion", "IV, VI", "warn", "Lote e doca corretos. A rota de 8,8 km (2,6×) vem do defeito de conexão."),
    ("smallhospital", "expansion", "IV", "warn", "Acesso local correto. A rota de 6,2 km (2,4×) vem do defeito de conexão."),
    ("companyhq", "expansion", "VII, X, XIII", "ok", "Fica perto dos veículos comerciais, com galpão de frota. Coerente com a fase de equipes."),
    ("mall", "corporate", "IV, VIII", "ok", "Fica no Eixo Empresarial, a 7,1 km. O Cap. IV exige veículo."),
    ("hospital0317", "corporate", "V, VIII", "ok", "16 min de carro a partir da garagem. A distância reforça a tensão do chamado das 03:17."),
    ("blackouttower", "corporate", "IX", "ok", "Fica na Av. Santa Aurora; é a torre de 114 m visível do skyline."),
    ("vertice", "corporate", "III, VI, X, XI", "ok", "Fica a cerca de 1,1 km da torre do apagão. Sede corporativa plausível."),
    ("logistics", "industrial", "IV", "ok", "Pátio de caminhões de 220×60 m, junto ao Anel Norte."),
    ("factory", "industrial", "VI", "ok", "Pátio de 200×80 m e chaminé de 48 m. 4,6 km da garagem."),
    ("drainage", "industrial", "VIII", "warn", "Fica entre o canal e a Marginal. O Bible coloca a cota mais baixa no SW (Cidade Antiga), mas o canal corre no norte; a lógica da enchente precisa ser decidida."),
    ("datacenter", "technology", "VII", "ok", "8,6 km da garagem. Com a smart tower e a HQ em lados opostos da cidade, o Cap. VII força a escolha de prioridades."),
    ("smarttower", "technology", "VII", "ok", "8,9 km, longe do campus do data center."),
    ("central", "civic", "XII, XIII, XIV", "ok", "Fica no centro geométrico, onde as vias convergem, a 4,9 km da garagem."),
]

garage = routes["origins"]["garage"]
home = routes["origins"]["home.starter"]


def chip(did):
    if did == "all":
        return '<span class="chip chip-all">Cidade inteira</span>'
    return f'<span class="chip" style="--d: var(--d-{did})">{esc(DNAME[did])}</span>'


def pill(v):
    return f'<span class="pill pill-{v}">{VERDICT[v]}</span>'


figs = []
for i, (f, title, did, cam, v, text) in enumerate(SHOTS, 1):
    square = "square" if f.startswith(("01_", "10_", "11_")) else ""
    figs.append(f"""
    <figure class="shot {square}">
      <button class="frame" type="button" data-src="{f}" data-title="{esc(title)}" aria-label="Ampliar {esc(title)}">
        <img src="{f}" alt="{esc(title)}: captura real do Blender" loading="lazy">
      </button>
      <figcaption>
        <div class="cap-head"><span class="num">{i:02d}</span><h3>{esc(title)}</h3>{pill(v)}</div>
        <div class="cap-meta">{chip(did)}<code>{esc(cam)}</code></div>
        <p>{esc(text)}</p>
        <code class="file">{esc(f)}</code>
      </figcaption>
    </figure>""")

loc_rows = []
for lid, did, ch, v, note in LOCS:
    r = garage.get(lid, {})
    loc_rows.append(f"""<tr><td><code>{lid}</code></td><td>{chip(did)}</td><td>{esc(ch)}</td>
      <td class="n">{r.get('networkM', 0) / 1000:.1f}</td><td class="n">{r.get('detour', '')}</td><td>{pill(v)}</td><td class="note">{esc(note)}</td></tr>""")

route_ids = [("supplier.tools", "Loja de ferramentas"), ("vehicles.used", "Revenda de usados (V1)"), ("horizonte", "Horizonte"),
             ("supplier.electrical", "Casa elétrica"), ("fuel.old", "Posto Cidade Antiga"), ("central", "Santa Aurora Central"),
             ("recurringcondo", "Condomínio de Helena"), ("school", "Escola pública"), ("hospital0317", "Hospital 03:17"),
             ("datacenter", "Data center")]
route_rows = []
for lid, name in route_ids:
    r = home[lid]
    m = r["minutes"]
    route_rows.append(f"""<tr><td>{esc(name)}</td><td>{chip(r['district'])}</td><td class="n">{r['networkM'] / 1000:.1f}</td>
      <td class="n">{m['walk']:.0f}</td><td class="n">{m['v0_initial']:.0f}</td><td class="n">{m['car_urban']:.0f}</td></tr>""")

legend = "".join(f'<li><span class="sw" style="--d: var(--d-{d})"></span>{esc(n)}</li>' for d, n in DISTRICTS)

page = f"""<title>Revisão W1 Santa Aurora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75,600;75,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: prancha de revisão — carimbo técnico no topo, capturas em grade 2 colunas, depois parecer e tabelas. */
:root {{
  --paper: #eef1f3; --sheet: #f8f9fa; --ink: #182028; --muted: #56626d; --line: #c9d0d6;
  --accent: #b85d0c;
  --ok: #2e7d4f; --warn: #a86b00; --block: #b3261e;
  --ok-bg: #e3f1e8; --warn-bg: #f8edd6; --block-bg: #f9e1df;
  --d-old: #c4561a; --d-expansion: #4a8f32; --d-industrial: #8a7769; --d-corporate: #3a5fc4; --d-technology: #138f99; --d-civic: #b59a10;
  --f-display: "Archivo", "Arial Narrow", Arial, sans-serif;
  --f-body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper: #12171b; --sheet: #192026; --ink: #dfe5ea; --muted: #97a3ad; --line: #2f3a43;
  --accent: #e88f3e; --ok: #6cc28d; --warn: #e3ad4a; --block: #f0827a;
  --ok-bg: #1b3326; --warn-bg: #3a2e14; --block-bg: #3d1d1b;
  --d-old: #e07a3e; --d-expansion: #73b85a; --d-industrial: #ab998b; --d-corporate: #6f8fe8; --d-technology: #3cc0c9; --d-civic: #d8bd3a;
  color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --paper: #12171b; --sheet: #192026; --ink: #dfe5ea; --muted: #97a3ad; --line: #2f3a43;
  --accent: #e88f3e; --ok: #6cc28d; --warn: #e3ad4a; --block: #f0827a;
  --ok-bg: #1b3326; --warn-bg: #3a2e14; --block-bg: #3d1d1b;
  --d-old: #e07a3e; --d-expansion: #73b85a; --d-industrial: #ab998b; --d-corporate: #6f8fe8; --d-technology: #3cc0c9; --d-civic: #d8bd3a;
  color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ background: var(--paper); color: var(--ink); font: 15px/1.55 var(--f-body); }}
.wrap {{ max-width: 1240px; margin: 0 auto; padding-inline: 20px; padding-block: 28px 64px; display: grid; gap: 40px; }}
h1, h2, h3 {{ font-family: var(--f-display); font-stretch: 75%; text-wrap: balance; margin: 0; }}
h1 {{ font-size: clamp(30px, 5vw, 46px); font-weight: 800; letter-spacing: .01em; line-height: 1; }}
h2 {{ font-size: 26px; font-weight: 800; }}
h3 {{ font-size: 19px; font-weight: 600; }}
code {{ font-family: var(--f-mono); font-size: 12.5px; }}
.eyebrow {{ font: 500 12px var(--f-mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }}
p {{ margin: 0; }}
.lede {{ max-width: 68ch; color: var(--muted); }}

/* Carimbo */
.titleblock {{ display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); border: 2px solid var(--ink); background: var(--sheet); }}
.tb-main {{ padding: 22px; display: grid; gap: 12px; border-right: 2px solid var(--ink); }}
.tb-fields {{ display: grid; grid-template-columns: auto minmax(0, 1fr); margin: 0; }}
.tb-fields dt, .tb-fields dd {{ margin: 0; padding: 7px 12px; border-bottom: 1px solid var(--line); }}
.tb-fields dt {{ font: 500 11px var(--f-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); border-right: 1px solid var(--line); }}
.tb-fields dd {{ font-family: var(--f-mono); font-size: 13px; overflow-wrap: anywhere; }}
.status {{ display: inline-flex; align-items: center; gap: 10px; padding: 8px 14px; border: 2px solid var(--block); color: var(--block);
  background: var(--block-bg); font: 800 15px var(--f-display); font-stretch: 75%; letter-spacing: .06em; text-transform: uppercase; justify-self: start; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 8px 18px; list-style: none; padding: 0; margin: 0; }}
.legend li {{ display: flex; align-items: center; gap: 8px; font-weight: 500; }}
.sw {{ width: 14px; height: 14px; background: var(--d); border-radius: 2px; }}

/* Capturas */
.shots {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px 24px; }}
.shot {{ margin: 0; display: grid; gap: 12px; align-content: start; min-width: 0; }}
.frame {{ display: block; padding: 0; border: 1px solid var(--line); background: #7d8a96; cursor: zoom-in; width: 100%; aspect-ratio: 16 / 9; overflow: hidden; }}
.shot.square .frame {{ aspect-ratio: 16 / 9; }}
.frame img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .25s ease; }}
.shot.square .frame img {{ object-fit: cover; object-position: center; }}
.frame:hover img {{ transform: scale(1.02); }}
.frame:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 2px; }}
figcaption {{ display: grid; gap: 8px; min-width: 0; }}
.cap-head {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
.num {{ font: 500 13px var(--f-mono); color: var(--accent); }}
.cap-head .pill {{ margin-left: auto; }}
.cap-meta {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; color: var(--muted); }}
.file {{ color: var(--muted); font-size: 11.5px; }}
.chip {{ display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 600; white-space: nowrap; }}
.chip::before {{ content: ""; width: 10px; height: 10px; border-radius: 2px; background: var(--d); }}
.chip-all::before {{ background: linear-gradient(90deg, var(--d-old) 0 16%, var(--d-expansion) 16% 33%, var(--d-industrial) 33% 50%, var(--d-corporate) 50% 66%, var(--d-technology) 66% 83%, var(--d-civic) 83%); }}
.pill {{ font: 600 11px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; white-space: nowrap; }}
.pill-ok {{ color: var(--ok); background: var(--ok-bg); }}
.pill-warn {{ color: var(--warn); background: var(--warn-bg); }}
.pill-block {{ color: var(--block); background: var(--block-bg); }}

/* Parecer */
.section {{ display: grid; gap: 16px; }}
.findings {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr)); gap: 16px; }}
.finding {{ border-top: 3px solid var(--line); padding-top: 12px; display: grid; gap: 8px; align-content: start; }}
.finding.block {{ border-color: var(--block); }} .finding.warn {{ border-color: var(--warn); }} .finding.ok {{ border-color: var(--ok); }}
.finding h3 {{ display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }}
.finding p, .finding li {{ max-width: 70ch; }}
.finding ul {{ margin: 0; padding-left: 18px; display: grid; gap: 4px; }}
.tablebox {{ overflow-x: auto; border: 1px solid var(--line); background: var(--sheet); }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font: 500 11px var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); background: var(--paper); position: sticky; top: 0; }}
td.n, th.n {{ text-align: right; font-variant-numeric: tabular-nums; font-family: var(--f-mono); }}
td.note {{ min-width: 280px; color: var(--muted); }}
.fixes {{ counter-reset: fix; list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }}
.fixes li {{ counter-increment: fix; display: grid; grid-template-columns: 36px minmax(0, 1fr); gap: 10px; align-items: baseline; }}
.fixes li::before {{ content: counter(fix, decimal-leading-zero); font: 500 13px var(--f-mono); color: var(--accent); }}
.rules {{ border: 2px solid var(--ink); padding: 18px 20px; display: grid; gap: 8px; background: var(--sheet); }}
.rules strong {{ font-family: var(--f-display); font-stretch: 75%; font-size: 18px; }}
footer {{ color: var(--muted); font-size: 13px; display: grid; gap: 4px; }}

dialog {{ border: 0; padding: 0; background: var(--sheet); color: var(--ink); max-width: min(96vw, 1800px); width: 100%; }}
dialog::backdrop {{ background: rgb(8 10 12 / .82); }}
dialog img {{ width: 100%; height: auto; display: block; max-height: 86vh; object-fit: contain; background: #7d8a96; }}
.dlg-bar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 14px; }}
.dlg-bar button {{ font: 600 13px var(--f-body); padding: 6px 12px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }}

@media (max-width: 760px) {{
  .titleblock {{ grid-template-columns: minmax(0, 1fr); }}
  .tb-main {{ border-right: 0; border-bottom: 2px solid var(--ink); }}
  .shots {{ grid-template-columns: minmax(0, 1fr); }}
}}
@media (prefers-reduced-motion: reduce) {{ .frame img {{ transition: none; }} }}
</style>

<div class="wrap">
  <header class="titleblock">
    <div class="tb-main">
      <span class="eyebrow">Project Facility · World Foundation</span>
      <h1>Revisão W1 Santa Aurora</h1>
      <p class="lede">Prancha de revisão do masterplan métrico 8×8 km. São 10 capturas obrigatórias e 1 extra, todas renders reais do arquivo salvo, reaberto em processo novo. Este é um massing S0: nada aqui é arte final.</p>
      <span class="status">W1 não aprovado · aguardando decisão</span>
      <ul class="legend" aria-label="Distritos">{legend}</ul>
    </div>
    <dl class="tb-fields">
      <dt>Arquivo</dt><dd>SantaAurora_Masterplan_v1.blend</dd>
      <dt>Blender</dt><dd>{esc(reopen['blenderVersion'])}</dd>
      <dt>Objetos</dt><dd>{reopen['objectCount']} · missing data: {len(reopen['missingData'])}</dd>
      <dt>Campanha</dt><dd>{reopen['campaignObjects']}/24 locais · vida {reopen['lifeObjects']}/20</dd>
      <dt>Vias / células</dt><dd>{reopen['roads']} corredores · {reopen['streamingCells']} células 1 km</dd>
      <dt>Gate técnico</dt><dd>PASS (validação + reabertura)</dd>
      <dt>Gate W1</dt><dd>Reprovado nesta revisão; 2 bloqueios</dd>
      <dt>Branch</dt><dd>claude/w1-masterplan</dd>
    </dl>
  </header>

  <section class="section" aria-labelledby="h-shots">
    <h2 id="h-shots">Capturas</h2>
    <div class="shots">{''.join(figs)}
    </div>
  </section>

  <section class="section" aria-labelledby="h-review">
    <h2 id="h-review">Parecer crítico</h2>
    <div class="findings">
      <article class="finding warn">
        <h3>Parece uma cidade grande? {pill('warn')}</h3>
        <p>Em planta, sim: 64 km², seis distritos e oito arteriais. Em perspectiva, lê como <strong>cidade média-grande com centro empresarial</strong>, não como metrópole.</p>
        <ul>
          <li>Ocupação do solo baixa: Cidade Antiga 23,7%, Expansão 10,7%, Technology 6,3%. Um centro histórico real costuma passar de 40%.</li>
          <li>11 de 64 células de 1 km (17%) estão fora de qualquer distrito. São as faixas vazias entre bairros.</li>
          <li>A malha ortogonal é idêntica em toda parte, e não há topografia, ferrovia, vegetação nem marcos fora do Corporate.</li>
        </ul>
      </article>
      <article class="finding warn">
        <h3>Algum distrito pequeno demais? {pill('warn')}</h3>
        <p>Nenhum é pequeno: todos têm entre 5,1 e 9,3 km², e Central é o menor por ser um campus. O risco é o contrário: <strong>Technology (8,1 km², 2 locais) e Industrial (9,3 km², 107 volumes) parecem grandes e vazios</strong>. Já a Cidade Antiga concentra os 8 locais iniciais num núcleo de cerca de 1,4×1,2 km dentro de 8,4 km².</p>
      </article>
      <article class="finding ok">
        <h3>As distâncias justificam veículo? {pill('ok')}</h3>
        <p>Sim. O Capítulo I cabe a pé, com 8–16 min da garagem a cada cliente. Do Capítulo II em diante, os locais fora da Cidade Antiga ficam a 4,6–8,9 km pela rede: 56–107 min a pé contra 9–18 min de carro. A revenda de usados fica a 0,9 km do lar, o que permite comprar o V1 cedo.</p>
        <p>Ressalva: parte da distância para a Expansão é artificial (desvio de 2,3–3,4×) e some quando a ligação Old↔Expansão for criada. A necessidade de veículo continua.</p>
      </article>
      <article class="finding block">
        <h3>Os 24 locais são coerentes com a história? {pill('block')}</h3>
        <p>A progressão espacial acompanha a campanha: começa na Cidade Antiga, passa pela Expansão, segue para Corporate e Industrial, depois Technology, e termina em Central. Dois pontos contradizem a lore:</p>
        <ul>
          <li><strong>Sem ligação Old↔Expansão.</strong> O Cap. II mistura Teatro (Old) com escola e condomínio (Expansão), e a lore diz que a Expansão cresceu a partir da cidade antiga.</li>
          <li><strong>Sem ferrovia nem porto seco.</strong> A lore e o MAPA_CAMPANHA definem a Cidade Antiga como nascida "ao redor da ferrovia, do porto seco e das primeiras indústrias", mas ela fica isolada do Industrial por 1 km de vazio.</li>
          <li>Precisa de decisão: o Bible coloca a cota mais baixa no SW, mas o canal de drenagem corre no norte. A enchente do Cap. VIII precisa de uma lógica de relevo consistente.</li>
        </ul>
      </article>
    </div>
  </section>

  <section class="section" aria-labelledby="h-locs">
    <h2 id="h-locs">Os 24 locais da campanha</h2>
    <p class="lede">A distância é medida pela rede viária a partir da Oficina Aurora (<code>garage</code>). O desvio é a razão entre a rota e a linha reta; acima de 2 indica falta de ligação.</p>
    <div class="tablebox"><table>
      <thead><tr><th>ID</th><th>Distrito</th><th>Capítulos</th><th class="n">Rede km</th><th class="n">Desvio</th><th>Parecer</th><th>Nota</th></tr></thead>
      <tbody>{''.join(loc_rows)}</tbody>
    </table></div>
  </section>

  <section class="section" aria-labelledby="h-routes">
    <h2 id="h-routes">Rotas a partir do lar inicial</h2>
    <p class="lede">Os minutos são equivalentes reais (a pé 5 km/h, transporte inicial V0 15 km/h, carro urbano 30 km/h). A escala de tempo do jogo ainda não foi definida, então a tabela só compara modos.</p>
    <div class="tablebox"><table>
      <thead><tr><th>Destino</th><th>Distrito</th><th class="n">Rede km</th><th class="n">A pé min</th><th class="n">V0 min</th><th class="n">Carro min</th></tr></thead>
      <tbody>{''.join(route_rows)}</tbody>
    </table></div>
  </section>

  <section class="section" aria-labelledby="h-fix">
    <h2 id="h-fix">Correções para a próxima iteração (W1.1)</h2>
    <ol class="fixes">
      <li><span><strong>Bloqueio:</strong> criar ligação viária Cidade Antiga ↔ Expansão (coletora leste-oeste no sul, z≈-2000 a -2600) e costurar as malhas locais nas divisas. Meta: desvio ≤1,6 até school, recurringcondo, hotel e smallhospital.</span></li>
      <li><span><strong>Bloqueio:</strong> modelar o corredor ferroviário oeste e o porto seco ligando Cidade Antiga, Estrada do Porto Seco e Industrial, com armazéns antigos na borda oeste da Cidade Antiga.</span></li>
      <li><span>Decidir a lógica de relevo e drenagem (para onde a água escoa, onde alaga no Cap. VIII) e aplicar terreno com declividade suave.</span></li>
      <li><span>Ocupar as faixas de transição com bairros de baixa densidade, postos, vegetação e infraestrutura. Meta: no máximo 5 células de 1 km sem uso definido.</span></li>
      <li><span>Dar ao Teatro Imperial uma praça frontal e eixo de chegada, e à Central um eixo cívico.</span></li>
      <li><span>Quebrar a regularidade da malha da Cidade Antiga (traçado orgânico) e subir a ocupação para ≥35%. Isso pode ficar para o blockout W2.</span></li>
      <li><span>Revisar escala de Technology e Industrial: reduzir área útil ou adensar, para que não leiam como vazios.</span></li>
    </ol>
  </section>

  <aside class="rules">
    <strong>Regras que continuam valendo</strong>
    <p>Isto é massing de planejamento espacial. <strong>O visual final de Santa Aurora não pode ser low-poly</strong>: produção exige PBR, bevels, decals, clutter funcional, LOD e iluminação atmosférica, conforme a Art Bible.</p>
    <p><strong>VEIN é só referência de patamar visual</strong> (realismo urbano, atmosfera, densidade e materialidade). Nenhum asset, textura, prédio, layout ou mapa é copiado.</p>
  </aside>

  <footer>
    <span>Gerado por <code>Tools/Map/build_w1_review_sheet.py</code> a partir de <code>Docs/masterplan-routes-v1.json</code> e <code>Reviews/W1/w1_reopen_report.json</code>.</span>
    <span>Relatório completo: <code>Docs/W1_MASTERPLAN_RELATORIO.md</code>.</span>
  </footer>
</div>

<dialog id="viewer" aria-label="Captura ampliada">
  <div class="dlg-bar"><strong id="viewer-title"></strong><button type="button" id="viewer-close">Fechar</button></div>
  <img id="viewer-img" alt="">
</dialog>
<script>
(() => {{
  const dlg = document.getElementById("viewer");
  const img = document.getElementById("viewer-img");
  const title = document.getElementById("viewer-title");
  document.querySelectorAll(".frame").forEach(btn => btn.addEventListener("click", () => {{
    img.src = btn.dataset.src; img.alt = btn.dataset.title; title.textContent = btn.dataset.title;
    if (dlg.showModal) dlg.showModal();
  }}));
  document.getElementById("viewer-close").addEventListener("click", () => dlg.close());
  dlg.addEventListener("click", e => {{ if (e.target === dlg) dlg.close(); }});
}})();
</script>
"""
out = review / "review_sheet.html"
out.write_text(page, encoding="utf-8")
print("wrote", out.relative_to(root).as_posix())
