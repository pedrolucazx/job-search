#!/usr/bin/env python3
"""build_dashboard.py — gera um dashboard.html autossuficiente do pipeline.

Le daily/<data>/*.json (vagas ranqueadas) e documents/applications/*/
(metadata.json + outcome.md) para derivar o estado de cada candidatura e
embutir tudo inline num unico HTML estatico. Stdlib apenas.

Uso:
  python3 scripts/build_dashboard.py            # gera dashboard.html na raiz
  python3 scripts/build_dashboard.py --check     # roda o self-check e sai
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from outcome import DISCARDED_STATUS, STAGES, parse

ROOT = Path(__file__).resolve().parent.parent
DRAFT_PDF = "cv_draft.pdf"


def norm_url(url):
    return (url or "").split("?", 1)[0].rstrip("/").lower()


def derive_state(outcome):
    if outcome is None:
        return "ranked"
    if DISCARDED_STATUS.lower() in outcome["status"].lower():
        return "discarded"
    if outcome["furthest"]:
        return "closed" if outcome["furthest"] == STAGES[-1] else "interview"
    if "applied" in outcome["status"].lower():
        return "applied"
    return "compiled"


def pick_pdf(folder):
    delivered = sorted(p for p in folder.glob("*.pdf") if p.name != DRAFT_PDF)
    if delivered:
        return delivered[0]
    draft = folder / DRAFT_PDF
    return draft if draft.exists() else None


def load_jobs():
    jobs = {}
    for f in sorted(ROOT.glob("daily/*/*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        jobs[norm_url(d.get("url"))] = {**d, "state": "ranked", "pdf": None, "interview_stage": None}

    for meta_path in sorted(ROOT.glob("documents/applications/*/metadata.json")):
        folder = meta_path.parent
        try:
            d = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        outcome_path = folder / "outcome.md"
        outcome = parse(outcome_path.read_text(encoding="utf-8")) if outcome_path.exists() else None
        pdf = pick_pdf(folder)
        rec = {
            **d,
            "state": derive_state(outcome),
            "pdf": str(pdf.relative_to(ROOT)) if pdf else None,
            "interview_stage": outcome["furthest"] if outcome else None,
            "resolution": outcome["resolution"] if outcome else "",
        }
        jobs[norm_url(d.get("url"))] = rec
    return list(jobs.values())


def render(jobs):
    data = json.dumps(jobs, ensure_ascii=False)
    return HTML.replace("__DATA__", data)


def _selfcheck():
    assert derive_state(None) == "ranked"
    assert derive_state({"status": "Applied", "furthest": None}) == "applied"
    assert derive_state({"status": "waiting for send confirmation", "furthest": None}) == "compiled"
    assert derive_state({"status": "Applied", "furthest": "Technical interview"}) == "interview"
    assert derive_state({"status": "Applied", "furthest": "Offer received"}) == "closed"
    assert derive_state({"status": "Discarded", "furthest": None}) == "discarded"
    assert derive_state({"status": "Discarded", "furthest": "Phone screen"}) == "discarded"
    assert norm_url("https://x.com/a/?utm=1") == "https://x.com/a"

    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        assert pick_pdf(folder) is None
        (folder / DRAFT_PDF).touch()
        assert pick_pdf(folder).name == DRAFT_PDF
        (folder / "Ana_Souza_CV.pdf").touch()
        assert pick_pdf(folder).name == "Ana_Souza_CV.pdf"

    print("ok")


HTML = r"""<!doctype html>
<html lang="pt-BR" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Search — Painel</title>
<style>
  :root{
    --bg:#09090b; --panel:#111113; --line:#26262b; --line2:#1c1c20;
    --txt:#e4e4e7; --mut:#8a8a93; --dim:#5c5c64;
    --full:#34d399; --partial:#fbbf24; --absent:#fb7185; --accent:#38bdf8;
    --r:10px;
  }
  *{box-sizing:border-box}
  html,body{margin:0}
  body{background:var(--bg);color:var(--txt);
    font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
    -webkit-font-smoothing:antialiased}
  .mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-variant-numeric:tabular-nums}
  header{position:sticky;top:0;z-index:20;background:rgba(9,9,11,.85);
    backdrop-filter:blur(8px);border-bottom:1px solid var(--line);
    padding:14px 20px;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px}
  header h1{font-size:16px;font-weight:650;margin:0;letter-spacing:-.01em}
  header .gen{color:var(--dim);font-size:12px}
  .metrics{margin-left:auto;display:flex;flex-wrap:wrap;gap:6px 16px;align-items:baseline}
  .metric{display:flex;align-items:baseline;gap:6px}
  .metric b{font-size:16px;font-weight:600}
  .metric span{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
  main{display:flex;gap:14px;padding:20px;overflow-x:auto;align-items:flex-start;min-height:60vh}
  .lane{flex:0 0 300px;min-width:300px}
  .lane-h{display:flex;align-items:center;gap:8px;padding:0 4px 10px;
    border-bottom:1px solid var(--line);margin-bottom:12px}
  .lane-h h2{font-size:12px;font-weight:600;margin:0;text-transform:uppercase;letter-spacing:.07em;color:var(--mut)}
  .lane-h .n{margin-left:auto;color:var(--dim);font-size:12px}
  .cards{display:flex;flex-direction:column;gap:10px}
  .card{background:var(--panel);border:1px solid var(--line2);border-radius:var(--r);
    padding:12px 13px;cursor:pointer;transition:border-color .12s,transform .12s}
  .card:hover{border-color:#3a3a42;transform:translateY(-1px)}
  .card:active{transform:translateY(0)}
  .card .top{display:flex;align-items:flex-start;gap:10px}
  .card .co{font-weight:600;font-size:14px;line-height:1.3}
  .card .role{color:var(--mut);font-size:12.5px;margin-top:2px}
  .score{margin-left:auto;flex:none;font-size:17px;font-weight:650;line-height:1}
  .chips{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}
  .chip{font-size:11px;color:var(--txt);background:#1a1a1e;border:1px solid var(--line2);
    border-radius:6px;padding:2px 7px}
  .chip.more{color:var(--dim)}
  .fit{display:flex;height:4px;border-radius:3px;overflow:hidden;margin-top:11px;background:#1a1a1e}
  .fit i{display:block;height:100%}
  .meta{display:flex;gap:10px;margin-top:9px;color:var(--dim);font-size:11px}
  .empty{color:var(--dim);font-size:12px;padding:8px 4px;font-style:italic}
  #scrim{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:40;display:none}
  #scrim.on{display:block}
  #drawer{position:fixed;top:0;right:0;height:100%;width:min(460px,100%);z-index:41;
    background:var(--panel);border-left:1px solid var(--line);transform:translateX(100%);
    transition:transform .2s ease;overflow-y:auto;padding:22px}
  #drawer.on{transform:translateX(0)}
  #drawer .dh{display:flex;align-items:flex-start;gap:12px}
  #drawer .dh .score{font-size:26px}
  #drawer h3{font-size:18px;margin:0;font-weight:650}
  #drawer .drole{color:var(--mut);margin-top:3px}
  #drawer .close{position:absolute;top:16px;right:16px;background:none;border:0;color:var(--mut);
    font-size:22px;cursor:pointer;line-height:1}
  .req{display:flex;gap:18px;margin:20px 0 6px}
  .req div{display:flex;flex-direction:column}
  .req b{font-size:22px;font-weight:650}
  .req span{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
  .sec{margin-top:22px;font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--dim);
    border-bottom:1px solid var(--line2);padding-bottom:6px}
  table{width:100%;border-collapse:collapse;margin-top:8px}
  td{padding:6px 0;border-bottom:1px solid var(--line2);vertical-align:top;font-size:13px}
  td.sk{white-space:nowrap;padding-right:10px}
  td.st{width:1%;padding-right:10px}
  td.nt{color:var(--mut);font-size:12px}
  .pill{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;
    padding:2px 7px;border-radius:5px}
  .links{display:flex;gap:10px;margin-top:22px}
  .links a{flex:1;text-align:center;text-decoration:none;font-size:13px;font-weight:550;
    padding:9px;border-radius:8px;border:1px solid var(--line);color:var(--txt)}
  .links a.primary{background:var(--accent);color:#04121c;border-color:var(--accent)}
  .links a.disabled{opacity:.35;pointer-events:none}
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<header>
  <h1>Job Search</h1>
  <span class="gen mono" id="gen"></span>
  <div class="metrics" id="metrics"></div>
</header>
<main id="board"></main>
<div id="scrim"></div>
<aside id="drawer"></aside>
<script>
const DATA = __DATA__;
const LANES = [
  ["ranked","Ranqueada"],["compiled","CV pronto"],["applied","Aplicada"],
  ["interview","Entrevista"],["closed","Fechada"],["discarded","Descartada"],
];
const C = {full:getComputedStyle(document.documentElement).getPropertyValue("--full"),
  partial:getComputedStyle(document.documentElement).getPropertyValue("--partial"),
  absent:getComputedStyle(document.documentElement).getPropertyValue("--absent")};

function scoreColor(s){ if(s>=80)return"var(--full)"; if(s>=65)return"var(--partial)"; return"var(--dim)"; }
function el(tag,cls,txt){ const e=document.createElement(tag); if(cls)e.className=cls; if(txt!=null)e.textContent=txt; return e; }

function fitBar(j){
  const bar=el("div","fit"), t=j.total_requisitos||1;
  [["requisitos_full",C.full],["requisitos_partial",C.partial],["requisitos_absent",C.absent]].forEach(([k,c])=>{
    const seg=el("i"); seg.style.width=(100*(j[k]||0)/t)+"%"; seg.style.background=c; bar.appendChild(seg);
  });
  return bar;
}

function card(j){
  const c=el("div","card"); c.onclick=()=>openDrawer(j);
  const top=el("div","top");
  const w=el("div"); w.appendChild(el("div","co",j.empresa)); w.appendChild(el("div","role",j.cargo));
  top.appendChild(w);
  const sc=el("div","score mono",j.score); sc.style.color=scoreColor(j.score); top.appendChild(sc);
  c.appendChild(top);
  const chips=el("div","chips"); const stack=j.stack||[];
  stack.slice(0,4).forEach(s=>chips.appendChild(el("span","chip",s)));
  if(stack.length>4)chips.appendChild(el("span","chip more","+"+(stack.length-4)));
  c.appendChild(chips);
  c.appendChild(fitBar(j));
  const meta=el("div","meta");
  meta.appendChild(el("span",null,j.fonte||"—"));
  if(j.nivel&&j.nivel!=="Não informado")meta.appendChild(el("span",null,j.nivel));
  if(j.interview_stage)meta.appendChild(el("span",null,j.interview_stage));
  c.appendChild(meta);
  return c;
}

function board(){
  const b=document.getElementById("board"); b.innerHTML="";
  for(const [key,label] of LANES){
    const jobs=DATA.filter(j=>j.state===key).sort((a,z)=>z.score-a.score);
    const lane=el("div","lane");
    const h=el("div","lane-h"); h.appendChild(el("h2",null,label));
    h.appendChild(el("span","n mono",jobs.length)); lane.appendChild(h);
    const cards=el("div","cards");
    if(!jobs.length)cards.appendChild(el("div","empty","vazia"));
    jobs.forEach(j=>cards.appendChild(card(j)));
    lane.appendChild(cards); b.appendChild(lane);
  }
}

function metrics(){
  const m=document.getElementById("metrics");
  const applied=DATA.filter(j=>["applied","interview","closed"].includes(j.state)).length;
  const avg=DATA.length?Math.round(DATA.reduce((s,j)=>s+(j.score||0),0)/DATA.length):0;
  const items=[[DATA.length,"vagas"],[applied,"aplicadas"],
    [DATA.filter(j=>j.state==="interview").length,"entrevistas"],[avg,"score médio"]];
  items.forEach(([n,l])=>{ const d=el("div","metric");
    const b=el("b","mono",n); if(l==="score médio")b.style.color=scoreColor(n);
    d.appendChild(b); d.appendChild(el("span",null,l)); m.appendChild(d); });
}

function pill(status){
  const p=el("span","pill",status);
  const c={full:C.full,partial:C.partial,absent:C.absent}[status]||C.absent;
  p.style.color=c; p.style.background=c+"22"; return p;
}

function openDrawer(j){
  const d=document.getElementById("drawer"); d.innerHTML="";
  const close=el("button","close","×"); close.onclick=hideDrawer; d.appendChild(close);
  const dh=el("div","dh"); const w=el("div");
  w.appendChild(el("h3",null,j.empresa)); w.appendChild(el("div","drole",j.cargo)); dh.appendChild(w);
  const sc=el("div","score mono",j.score); sc.style.color=scoreColor(j.score); dh.appendChild(sc);
  d.appendChild(dh);
  const req=el("div","req");
  [["requisitos_full","full"],["requisitos_partial","partial"],["requisitos_absent","absent"],["total_requisitos","total"]]
    .forEach(([k,l])=>{ const box=el("div"); const b=el("b","mono",j[k]??0);
      if(C[l])b.style.color=C[l]; box.appendChild(b); box.appendChild(el("span",null,l)); req.appendChild(box); });
  d.appendChild(req);
  if((j.gaps||[]).length){
    d.appendChild(el("div","sec","Análise de fit"));
    const t=el("table"); (j.gaps||[]).forEach(g=>{ const tr=el("tr");
      tr.appendChild(el("td","sk",g.skill));
      const st=el("td","st"); st.appendChild(pill(g.status)); tr.appendChild(st);
      tr.appendChild(el("td","nt",g.nota||"")); t.appendChild(tr); });
    d.appendChild(t);
  }
  const links=el("div","links");
  const vaga=el("a",null,"Abrir vaga"); vaga.href=j.url||"#"; vaga.target="_blank"; links.appendChild(vaga);
  const pdf=el("a","primary","Abrir CV"); if(j.pdf){pdf.href=j.pdf;pdf.target="_blank";}else pdf.className="primary disabled";
  links.appendChild(pdf); d.appendChild(links);
  document.getElementById("scrim").classList.add("on"); d.classList.add("on");
}
function hideDrawer(){ document.getElementById("drawer").classList.remove("on");
  document.getElementById("scrim").classList.remove("on"); }
document.getElementById("scrim").onclick=hideDrawer;
document.addEventListener("keydown",e=>{ if(e.key==="Escape")hideDrawer(); });

const dates=[...new Set(DATA.map(j=>j.data).filter(Boolean))].sort();
document.getElementById("gen").textContent=dates.length?("· "+dates[dates.length-1]):"";
metrics(); board();
</script>
</body>
</html>
"""


def main():
    if "--check" in sys.argv:
        _selfcheck()
        return
    jobs = load_jobs()
    out = ROOT / "dashboard.html"
    out.write_text(render(jobs), encoding="utf-8")
    print(f"{len(jobs)} vagas -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
