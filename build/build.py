"""Builds README.md and assets/*.svg for the profile. Run daily by .github/workflows/build-readme.yml.
Edit the content blocks (EXP, WINS2, LANES, toolkit rows) and the next run redraws everything."""
import base64, io, html, re, os
from fontTools import subset
from fontTools.ttLib import TTFont
FD=os.environ.get("FONT_DIR","fonts")
FONTS={("Sora",200):f"{FD}/fontsource-sora/files/sora-latin-200-normal.woff2",
       ("Sora",300):f"{FD}/fontsource-sora/files/sora-latin-300-normal.woff2",
       ("Sora",400):f"{FD}/fontsource-sora/files/sora-latin-400-normal.woff2",
       ("Sora",600):f"{FD}/fontsource-sora/files/sora-latin-600-normal.woff2",
       ("JBM",400):f"{FD}/fontsource-jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2",
       ("JBM",500):f"{FD}/fontsource-jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2",
       ("JBM",700):f"{FD}/fontsource-jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2"}
FAM={"Sora":"S","JBM":"M"}
_cache={}
def _subset(path,chars):
    key=(path,chars)
    if key in _cache: return _cache[key]
    f=TTFont(path); opt=subset.Options(); opt.flavor="woff2"; opt.layout_features=["*"]
    s=subset.Subsetter(opt); s.populate(text=chars+" "); s.subset(f)
    b=io.BytesIO(); f.flavor="woff2"; f.save(b); r=base64.b64encode(b.getvalue()).decode(); _cache[key]=r; return r
import itertools
_ctr=itertools.count()
class Doc:
    def __init__(s,W,H): s.W,s.H=W,H; s.parts=[]; s.used={}; s.css=[]; s.defs=[]; s.id=next(_ctr)
    def add(s,x): s.parts.append(x); return s
    def text(s,x,y,t,size,fill,fam="Sora",w=400,anchor="start",ls=0,extra="",cls=""):
        t=str(t); s.used.setdefault((fam,w),set()).update(t)
        st=f"font-family:{FAM[fam]}{s.id},{"monospace" if fam=="JBM" else "sans-serif"};font-weight:{w};font-size:{size}px"+(f";letter-spacing:{ls}px" if ls else "")
        s.parts.append(f'<text x="{x}" y="{y}" fill="{fill}" text-anchor="{anchor}" style="{st}" {extra} {"class="+chr(34)+cls+chr(34) if cls else ""}>{html.escape(t)}</text>'); return s
    def render(s):
        ff=""
        for (fam,w),chars in s.used.items():
            ff+=f"@font-face{{font-family:{FAM[fam]}{s.id};font-display:block;font-weight:{w};src:url(data:font/woff2;base64,{_subset(FONTS[(fam,w)],''.join(sorted(chars)))}) format('woff2')}}"
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.W}" height="{s.H}" viewBox="0 0 {s.W} {s.H}" fill="none">'
                f'<style>{ff}{"".join(s.css)}</style><defs>{"".join(s.defs)}</defs>'+"".join(s.parts)+'</svg>')
def wrap(t,n):
    out=[];cur=""
    for w in t.split():
        if len(cur)+len(w)+1>n: out.append(cur); cur=w
        else: cur=(cur+" "+w).strip()
    if cur: out.append(cur)
    return out

BASE=dict(bg="#0a0a0c",bg2="#070709",panel="#121216",panel2="#17171c",line="#222229",line2="#2d2d35",line3="#3b3b45",
          bone="#efece6",body="#aaa8af",dim="#8d8b94",faint="#6c6a73")
ACCENTS={
 "lime":  dict(acc="#b5f23d",hot="#d6ff86",deep="#86b82a",adim="#4d6b17",dark="#22300b"),
 "orange":dict(acc="#ff7a2f",hot="#ffae80",deep="#d85c15",adim="#87390e",dark="#381807"),
 "violet":dict(acc="#a78bfa",hot="#cbbcff",deep="#7c5ce0",adim="#4a3a8c",dark="#1f1840"),
}
CAT=["#4c9aff","#2bb3a3","#e0a33b","#e0627d","#9a86f0"]
def P(name): d=dict(BASE); d.update(ACCENTS[name]); return d

# ======================= CONTENT =======================
EXP=[("Sep 2025 – Feb 2026","Data Science Intern","Smartlife Foundation",["Encoding system that cleaned 500+","multi-vendor records; MCQ-based","chatbot flows for analytics"]),
     ("Jan – Mar 2026","Data Analytics & ML Intern","Krutanic Solutions",["Random Forest price model on","2,500+ records, live Streamlit","dashboard; executive BI reports"]),
     ("Jun – Aug 2026","AI Intern","TechnoCIT Software Solutions",["LangGraph.js A2A multi-agent","orchestration; LLM adapter for 7","providers; OIDC / Keycloak SSO"])]


# ======================= LIVE DATA (GitHub API) =======================
import json, urllib.request, datetime, math, random, sys
USER="Shanks07-404"
TOKEN=os.environ.get("GITHUB_TOKEN","")
NAME="Vrushank Tipnis"
# Build-log lanes: repo name -> (label shown, lane). Repos not listed here are left off the chart.
LANES={"sense-link-neuro":("sense-link-neuro","ML"),"SenseLink-":("SenseLink","ML"),"Blackberry-PPT-Hackathon-":("Blackberry-PPT","DATA"),
 "Krutanic-Random-Forest":("Krutanic-RF","ML"),"Project-Hermes":("Project-Hermes","ML"),"SkillSwap":("SkillSwap","BACKEND"),
 "prompt_gen_v2":("prompt_gen_v2","AGENTIC"),"Leetcode_SQL":("Leetcode_SQL","DATA"),"claude-token-count":("claude-token-count","AGENTIC"),
 "SSO-login-schema":("SSO-login-schema","BACKEND"),"GradScope":("GradScope","ML"),"FourierLens":("FourierLens","ML"),
 "ProjectKit":("ProjectKit","BACKEND"),"Cassini-Vivant":("Cassini-Vivant","ML")}
def _get(url,data=None):
    h={"User-Agent":USER,"Accept":"application/vnd.github+json"}
    if TOKEN: h["Authorization"]="Bearer "+TOKEN
    req=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers=h)
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read())
def load():
    G=globals()
    q={"query":'query{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'%USER}
    cal=_get("https://api.github.com/graphql",q)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days=[d for w in cal["weeks"] for d in w["contributionDays"]]
    G["C"]=[d["contributionCount"] for d in days]; G["DATES"]=[datetime.date.fromisoformat(d["date"]) for d in days]
    G["TOTAL"]=cal["totalContributions"]; G["ACTIVE"]=sum(1 for x in C if x); G["BEST"]=max(C) if C else 0
    b=cur=0
    for x in C: cur=cur+1 if x else 0; b=max(b,cur)
    G["LONGEST"]=b
    repos=[r for r in _get(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
    G["REPOS"]=len(repos); tot={}
    for r in repos:
        if r["name"]==USER: continue
        for k,v in _get(r["languages_url"]).items(): tot[k]=tot.get(k,0)+v
    allb=sum(tot.values()) or 1
    G["LANGS"]=[(k,round(v*100/allb)) for k,v in sorted(tot.items(),key=lambda x:-x[1])[:5]]
    G["REPOS2"]=sorted([(LANES[r["name"]][0],r["created_at"][:10],r["size"],LANES[r["name"]][1]) for r in repos if r["name"] in LANES],key=lambda x:x[1])
    G["SYNC"]=datetime.date.today().isoformat()
    G["START"]=DATES[0]; G["END"]=DATES[-1]

# ======================= CARDS =======================
WINS2=[("MTC ThinkAI '26","2026","1st","Cassini Vivant","Microclimate AI for vineyards and appellation adaptation. Runs fully offline, Gemini assistant optional.",["FastAPI","React","Gemini"],"Cassini-Vivant"),
 ("IEEE CampusOps","","1st","ProjectKit","Lab procurement: a project idea becomes an AI-built bill of materials, stock-checked, handed over by QR.",["JavaScript","AI BOM","Realtime"],"ProjectKit"),
 ("Space Week × Supernova","","3rd","Barjeel","Third place at Space Week × Supernova.",[],None),
 ("Space Week × Supernova","Oct 2025","1st","Project Hermes","Lunar elevation data in, terrain-risk score out: Safe, Divert or Abort landing zones in real time.",["Python","Flask","OpenCV"],"Project-Hermes"),
 ("ThinkAI '24","Nov 2024","1st","Team Noor","Accessibility tool for visually and hearing-impaired users: real-time OCR and a voice-navigable UI.",["OCR","Voice UI","Adaptive"],None)]
def card_base(d,c,W,H,title,right=""):
    d.add(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{c["bg"]}" stroke="{c["line"]}"/>')
    d.text(32,44,title,11.5,c["acc"],"JBM",700,ls=3.2)
    if right: d.text(W-32,44,right,11.5,c["dim"],"JBM",400,"end")
    d.add(f'<line x1="32" y1="62" x2="{W-32}" y2="62" stroke="{c["line"]}"/>')
def pill(d,c,x,y,t):
    w=len(t)*7.4+22
    d.add(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{c["panel2"]}" stroke="{c["line2"]}"/>')
    d.text(x+11,y+16,t,11.5,c["body"],"JBM",400); return x+w+8
# ---------------- HERO ----------------
def hero(c):
    W,H=1200,430; d=Doc(W,H)
    d.defs.append(f'<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{c["line2"]}"/></pattern>'
                  f'<radialGradient id="glow" cx=".78" cy=".42" r=".55"><stop offset="0" stop-color="{c["acc"]}" stop-opacity=".10"/><stop offset="1" stop-color="{c["acc"]}" stop-opacity="0"/></radialGradient>'
                  )
    d.css.append(".wm{stroke-dasharray:900;animation:wm 2.4s ease-out backwards}@keyframes wm{0%{stroke-dashoffset:900;fill-opacity:0}70%{stroke-dashoffset:0;fill-opacity:0}100%{stroke-dashoffset:0;fill-opacity:1}}"
                 ".bar{transform-box:fill-box;transform-origin:left;animation:bar 1s ease-out 1.6s backwards}@keyframes bar{from{transform:scaleX(0)}}"
                 ".cur{animation:cu 1s steps(1) infinite}@keyframes cu{50%{opacity:0}}.pl{animation:pl 1.8s ease-in-out infinite}@keyframes pl{50%{opacity:.25}}")
    d.add(f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/><rect width="{W}" height="{H}" fill="url(#dots)" opacity=".55"/><rect width="{W}" height="{H}" fill="url(#glow)"/>')
    d.text(70,64,"VT / 2026",11,c["faint"],"JBM",500,ls=3); d.text(W-70,64,"BITS PILANI · DUBAI",11,c["faint"],"JBM",500,"end",ls=3)
    d.add(f'<line x1="70" y1="80" x2="{W-70}" y2="80" stroke="{c["line"]}"/>')
    d.text(72,132,"DATA  →  MACHINE LEARNING  →  AGENTIC AI",12,c["acc"],"JBM",500,ls=4,extra='xml:space="preserve"')
    d.text(66,222,"VRUSHANK",104,c["bone"],"Sora",200,ls=6,extra=f'stroke="{c["bone"]}" stroke-width="1.2"',cls="wm")
    d.add(f'<rect class="bar" x="72" y="240" width="150" height="3" fill="{c["acc"]}"/>')
    PREFIX="data science · ai/ml · "; X0=72; CW=12.0; px=X0+len(PREFIX)*CW
    d.text(X0,276,PREFIX,20,c["body"],"JBM",400,extra='xml:space="preserve"')
    PH=["agents that remember","models from the gradient up","multi-agent systems that delegate","4× hackathon winner","solving systems layer by layer"]
    tc,hold,dc,gap=.07,2.4,.035,.35
    wins=[];t=0
    for p in PH:
        s=t; t+=len(p)*tc; ty=t; t+=hold; h=t; t+=len(p)*dc; e=t; t+=gap; wins.append((s,ty,h,e))
    T=t
    for i,(p,(s,ty,h,e)) in enumerate(zip(PH,wins)):
        n=len(p); kt=[0.0]; vv=[0]
        for k in range(1,n+1): kt.append((s+k*tc)/T); vv.append(k*CW)
        for k in range(1,n+1): kt.append((h+k*dc)/T); vv.append((n-k)*CW)
        if kt[1]==0: kt.pop(0); vv.pop(0)
        d.defs.append(f'<clipPath id="ph{i}"><rect x="{px}" y="252" width="0" height="34"><animate attributeName="width" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{x:.5f}" for x in kt)}" values="{";".join(f"{v:.0f}" for v in vv)}"/></rect></clipPath>')
        d.add(f'<g clip-path="url(#ph{i})">'); d.text(px,276,p,20,c["bone"],"JBM",400,extra='xml:space="preserve"'); d.add('</g>')
    ck=[0.0]; cv=[px]
    for p,(s,ty,h,e) in zip(PH,wins):
        n=len(p)
        for k in range(1,n+1): ck.append((s+k*tc)/T); cv.append(px+k*CW)
        for k in range(1,n+1): ck.append((h+k*dc)/T); cv.append(px+(n-k)*CW)
    if ck[1]==0: ck.pop(0); cv.pop(0)
    d.add(f'<rect class="cur" x="{px}" y="258" width="11" height="22" fill="{c["acc"]}"><animate attributeName="x" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{k:.5f}" for k in ck)}" values="{";".join(f"{x:.0f}" for x in cv)}"/></rect>')
    # cube face that solves itself
    s=62; g=10; x0,y0=870,112; ramp=[c["dark"],c["adim"],c["deep"],c["acc"],c["panel2"],c["hot"]]
    d.add(f'<rect x="{x0-14}" y="{y0-14}" width="{3*s+2*g+28}" height="{3*s+2*g+28}" rx="22" fill="{c["bg2"]}" stroke="{c["line2"]}"/>')
    for i in range(9):
        r,k=divmod(i,3); random.seed(i*11+5); seq=[random.choice(ramp) for _ in range(3)]
        vals=";".join(seq+[c["acc"],c["acc"],seq[0]])
        d.add(f'<rect x="{x0+k*(s+g)}" y="{y0+r*(s+g)}" width="{s}" height="{s}" rx="10" fill="{seq[0]}"><animate attributeName="fill" values="{vals}" keyTimes="0;.15;.3;.45;.9;1" dur="7s" begin="{i*.06:.2f}s" repeatCount="indefinite"/></rect>')
    d.text(x0+(3*s+2*g)/2,y0+3*s+2*g+46,"SOLVED ONE LAYER AT A TIME",10.5,c["faint"],"JBM",500,"middle",ls=2.4)
    d.add(f'<rect x="0" y="{H-58}" width="{W}" height="58" fill="{c["bg2"]}"/><line x1="0" y1="{H-58}" x2="{W}" y2="{H-58}" stroke="{c["line"]}"/>')
    d.add(f'<circle class="pl" cx="76" cy="{H-29}" r="5" fill="{c["acc"]}"/>')
    d.text(92,H-25,"OPEN TO AI/ML ENGINEERING INTERNSHIPS",11.5,c["bone"],"JBM",500,ls=2.4)
    d.text(W-70,H-25,"4× 1ST PLACE  ·  3 INTERNSHIPS  ·  AGENTIC IOT RESEARCH",11.5,c["dim"],"JBM",500,"end",ls=1.6,extra='xml:space="preserve"')
    return d.render()
def chip(c,label,icon):
    W,H=118,34; d=Doc(W,H)
    d.add(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="17" fill="{c["panel"]}" stroke="{c["line2"]}"/><circle cx="20" cy="17" r="4" fill="{c["acc"]}"/>')
    d.text(34,21.5,label,12,c["bone"],"JBM",500,ls=1); return d.render()
def divider(c):
    W,H=1000,28; d=Doc(W,H)
    d.add(f'<line x1="0" y1="14" x2="{W}" y2="14" stroke="{c["line"]}"/>')
    for x in range(0,W+1,50): d.add(f'<line x1="{x}" y1="10" x2="{x}" y2="18" stroke="{c["line2"]}"/>')
    d.add(f'<rect x="{W/2-5}" y="9" width="10" height="10" rx="2" fill="{c["acc"]}" transform="rotate(45 {W/2} 14)"/>'); return d.render()
# ---------------- EXPERIENCE ----------------
def experience(c):
    W,H=1000,400; d=Doc(W,H); card_base(d,c,W,H,"INTERNSHIPS","3 roles · sep 2025 – aug 2026")
    d.css.append(".rail{stroke-dasharray:1000;animation:rl 2.4s ease-out backwards}@keyframes rl{from{stroke-dashoffset:1000}}")
    xs=[32,352,672]; ry=98
    d.add(f'<line x1="44" y1="{ry}" x2="{W-44}" y2="{ry}" stroke="{c["line2"]}" stroke-width="2"/><line class="rail" x1="44" y1="{ry}" x2="{W-44}" y2="{ry}" stroke="{c["acc"]}" stroke-width="2"/>')
    tags=[["Python","Data cleaning","Chatbots"],["scikit-learn","Streamlit","Power BI"],["LangGraph.js","A2A","OIDC"]]
    for i,((dt,role,co,ls),x) in enumerate(zip(EXP,xs)):
        d.add(f'<circle cx="{x+12}" cy="{ry}" r="7" fill="{c["bg"]}" stroke="{c["acc"]}" stroke-width="2.5"/>'+(f'<circle cx="{x+12}" cy="{ry}" r="3" fill="{c["acc"]}"/>' if i==2 else ""))
        d.text(x,138,dt.upper(),11,c["dim"],"JBM",500,ls=1.6)
        d.text(x,172,co,21,c["bone"],"Sora",600) if len(co)<22 else [d.text(x,172,co.split(" ")[0],21,c["bone"],"Sora",600),d.text(x,197,"Software Solutions",21,c["bone"],"Sora",600)]
        yy=200 if len(co)<22 else 225
        d.text(x,yy,role,13.5,c["acc"],"JBM",500)
        for j,l in enumerate(ls): d.text(x,yy+32+j*21,l,14,c["body"],"Sora",400)
        px=x
        for t in tags[i]: px=pill(d,c,px,H-62,t)
    return d.render()
# ---------------- NOW ----------------
def now(c):
    W,H=1000,350; d=Doc(W,H); card_base(d,c,W,H,"CURRENTLY","nov 2026")
    d.css.append(".spin{transform-origin:150px 196px;animation:sp 8s linear infinite}@keyframes sp{to{transform:rotate(360deg)}}.pl{animation:pl 1.6s ease-in-out infinite}@keyframes pl{50%{opacity:.25}}")
    d.add(f'<line x1="500" y1="86" x2="500" y2="{H-30}" stroke="{c["line"]}"/>')
    # left: MAPE-K loop
    cx,cy,r=150,196,70
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{c["line2"]}" stroke-width="2"/>')
    d.add(f'<g class="spin"><path d="M{cx} {cy-r} A{r} {r} 0 0 1 {cx+r} {cy}" stroke="{c["acc"]}" stroke-width="3" stroke-linecap="round"/></g>')
    for k,(lab,a) in enumerate([("M",-90),("A",0),("P",90),("E",180)]):
        x=cx+r*math.cos(math.radians(a)); y=cy+r*math.sin(math.radians(a))
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{c["panel2"]}" stroke="{c["line3"]}"/>'); d.text(x,y+4.5,lab,12,c["bone"],"JBM",700,"middle")
    d.add(f'<circle cx="{cx}" cy="{cy}" r="26" fill="{c["dark"]}" stroke="{c["acc"]}"/>'); d.text(cx,cy+5,"K",15,c["acc"],"JBM",700,"middle")
    d.text(252,112,"RESEARCH · SINCE JAN 2026",11,c["dim"],"JBM",500,ls=1.4)
    for j,l in enumerate(["Agentic AI for","adaptive smart IoT"]): d.text(252,142+j*25,l,19,c["bone"],"Sora",600)
    for j,l in enumerate(["Swapping static MAPE-K loops","for a controller with episodic,","semantic and procedural memory."]): d.text(252,200+j*20,l,13.5,c["body"],"Sora",400)
    d.add(f'<circle class="pl" cx="258" cy="{H-40}" r="4.5" fill="{c["acc"]}"/>'); d.text(270,H-36,"in progress",12,c["acc"],"JBM",500)
    # right: paper
    x=532
    d.text(x,112,"PAPER · IN PROGRESS",11,c["dim"],"JBM",500,ls=1.4)
    for j,l in enumerate(["Scalable data-integrity verification","for retrieval-augmented LLM","intrusion detection"]): d.text(x,142+j*24,l,17,c["bone"],"Sora",600)
    for j,l in enumerate(["A structure-aware detector for knowledge-base","poisoning in network telemetry. Now building a","physical IoT testbed to validate it on real traffic."]): d.text(x,226+j*19,l,13,c["body"],"Sora",400)
    steps=[("detector",2),("iot testbed",1),("evaluation",0)]; sx=x
    for k,(lab,st) in enumerate(steps):
        col=c["acc"] if st else c["line3"]
        d.add(f'<circle {"class=%spl%s"%(chr(34),chr(34)) if st==1 else ""} cx="{sx+6}" cy="{H-40}" r="6" fill="{col if st==2 else c["bg"]}" stroke="{col}" stroke-width="2"/>')
        d.text(sx+18,H-36,lab,12,c["bone"] if st else c["faint"],"JBM",500)
        if k<2: d.add(f'<line x1="{sx+len(lab)*7.3+26}" y1="{H-40}" x2="{sx+len(lab)*7.3+60}" y2="{H-40}" stroke="{c["line3"]}" stroke-dasharray="3 3"/>')
        sx+=len(lab)*7.3+68
    return d.render()
# ---------------- WIN CARDS ----------------
def podium(d,c,x,y,place):
    hs=[22,34,14]; order=[1,0,2]  # left=2nd, mid=1st, right=3rd
    for k in range(3):
        rank=[2,1,3][k]; h=hs[k]; on=(rank==1 and place=="1st") or (rank==3 and place=="3rd")
        d.add(f'<rect x="{x+k*15}" y="{y+34-h}" width="12" height="{h}" rx="2" fill="{c["acc"] if on else c["line2"]}"/>')
def win(c,i,w=None):
    W,H=480,230; d=Doc(W,H)
    d.add(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{c["bg"]}" stroke="{c["line"]}"/>')
    if w is None:
        d.css.append(".cur{animation:cu 1s steps(1) infinite}@keyframes cu{50%{opacity:0}}")
        d.add(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" rx="10" stroke="{c["line2"]}" stroke-dasharray="6 6"/>')
        d.text(34,58,"NEXT",11,c["faint"],"JBM",500,ls=3); d.text(34,104,"the next podium",26,c["bone"],"Sora",300)
        d.text(34,134,"already being built.",15,c["faint"],"Sora",400); d.add(f'<rect class="cur" x="34" y="{H-58}" width="10" height="20" fill="{c["acc"]}"/>')
        return d.render()
    ev,dt,pl,pr,desc,tags,repo=w
    d.text(30,48,(ev+(" · "+dt if dt else "")).upper(),10.5,c["dim"],"JBM",500,ls=1.6)
    podium(d,c,W-74,22,pl)
    d.text(30,98,pl.upper(),36,c["acc"] if pl=="1st" else c["bone"],"Sora",600)
    d.text(30+len(pl)*24+16,98,"place",13,c["faint"],"JBM",400)
    d.text(30,132,pr,20,c["bone"],"Sora",600)
    for j,l in enumerate(wrap(desc,58)[:2]): d.text(30,158+j*18,l,12.5,c["body"],"Sora",400)
    if not tags: d.text(30,H-26,"details soon",11,c["faint"],"JBM",400)
    px=30
    for t in tags: px=pill(d,c,px,H-42,t)
    if repo: d.text(W-30,H-26,"code →",11.5,c["acc"],"JBM",500,"end")
    return d.render()
# ---------------- STATS ----------------
def stats(c):
    W,H=1000,500; d=Doc(W,H); card_base(d,c,W,H,"GITHUB STATS",f"synced {SYNC} · last 12 months")
    nums=[(str(TOTAL),"CONTRIBUTIONS"),(str(ACTIVE),"ACTIVE DAYS"),(f"{LONGEST}d","LONGEST STREAK"),(str(REPOS),"PUBLIC REPOS"),(str(BEST),"BEST DAY")]
    for i,(v,l) in enumerate(nums):
        x=32+i*188
        if i: d.add(f'<line x1="{x-16}" y1="90" x2="{x-16}" y2="150" stroke="{c["line"]}"/>')
        d.text(x,128,v,34,c["acc"] if i==0 else c["bone"],"Sora",300); d.text(x,150,l,10,c["dim"],"JBM",500,ls=1.8)
    d.text(32,200,"CONTRIBUTION HEATMAP",10,c["dim"],"JBM",500,ls=2.4)
    ramp=[c["panel"],c["dark"],c["adim"],c["deep"],c["acc"]]
    lx=W-32-5*16-70; d.text(lx,200,"less",10,c["faint"],"JBM",400)
    for k,col in enumerate(ramp): d.add(f'<rect x="{lx+36+k*16}" y="190" width="12" height="12" rx="2.5" fill="{col}"/>')
    d.text(W-32,200,"more",10,c["faint"],"JBM",400,"end")
    s=17.5; x0,y0=32,216
    def lvl(v): return 0 if v==0 else 1 if v<=2 else 2 if v<=5 else 3 if v<=8 else 4
    for i,v in enumerate(C): d.add(f'<rect x="{x0+(i//7)*s:.1f}" y="{y0+(i%7)*s:.1f}" width="{s-3.5:.1f}" height="{s-3.5:.1f}" rx="3" fill="{ramp[lvl(v)]}"/>')
    d.add(f'<line x1="32" y1="360" x2="{W-32}" y2="360" stroke="{c["line"]}"/>')
    d.text(32,392,"LANGUAGES BY BYTES",10,c["dim"],"JBM",500,ls=2.4)
    x=32; tw=W-64
    for k,((n,p),col) in enumerate(zip(LANGS,CAT)):
        w=tw*p/sum(q for _,q in LANGS); d.add(f'<rect x="{x:.1f}" y="408" width="{max(w-3,2):.1f}" height="10" rx="5" fill="{col}"/>'); x+=w
    x=32
    for (n,p),col in zip(LANGS,CAT):
        d.add(f'<circle cx="{x+5}" cy="{446}" r="4.5" fill="{col}"/>'); d.text(x+16,450,n,12,c["bone"],"JBM",500); d.text(x+16+len(n)*7.3+8,450,f"{p}%",12,c["dim"],"JBM",400); x+=len(n)*7.3+len(f"{p}%")*7.3+52
    return d.render()
def rhythm(c):
    rows=[("AGENTIC AI",["LangGraph.js","LangChain.js","A2A","RAG","Vector embeddings","Agent memory"]),
          ("ML & DATA",["Python","scikit-learn","Pandas","NumPy","CNNs","OCR","Streamlit"]),
          ("BACKEND",["Node.js","Express","FastAPI","OAuth 2.0 / OIDC","JWT","Keycloak","MongoDB"]),
          ("TOOLS",["Git","Jupyter","Power BI","Tableau","Matplotlib"])]
    W,H=1000,96+len(rows)*50+20; d=Doc(W,H); card_base(d,c,W,H,"TOOLKIT","what i build with")
    for i,(lab,items) in enumerate(rows):
        y=92+i*50
        d.add(f'<rect x="32" y="{y+2}" width="3" height="18" rx="1.5" fill="{c["acc"]}"/>'); d.text(46,y+16,lab,11,c["dim"],"JBM",500,ls=1.8)
        px=200
        for t in items: px=pill(d,c,px,y,t)
    return d.render()
def snake(c,src):
    v=f':root{{--cb:#0000;--cs:{c["bone"]};--ce:{c["panel"]};--c0:{c["panel"]};--c1:{c["dark"]};--c2:{c["adim"]};--c3:{c["deep"]};--c4:{c["acc"]}}}'
    return re.sub(r":root\{[^}]*\}",v,src,count=1)
def buildlog(c):
    import datetime as dtm
    lanes=["DATA","ML","AGENTIC","BACKEND"]; col={"DATA":CAT[1],"ML":CAT[0],"AGENTIC":c["acc"],"BACKEND":CAT[2]}
    LH=78; top=96; W,H=1000,top+len(lanes)*LH+46; d=Doc(W,H); card_base(d,c,W,H,"BUILD LOG",f"{len(REPOS2)} project repos · plotted by the day each one started")
    pass
    t0=START.replace(day=1); t1=(END.replace(day=28)+dtm.timedelta(days=8)).replace(day=1); gx,gw=150,W-150-40
    X=lambda s:gx+(dtm.date.fromisoformat(s)-t0).days/(t1-t0).days*gw
    for m in range(15):
        y_,mo=t0.year+(t0.month-1+m)//12,(t0.month-1+m)%12+1
        if dtm.date(y_,mo,1)>t1: break
        x=X(f"{y_}-{mo:02d}-01")
        d.add(f'<line x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{top+len(lanes)*LH}" stroke="{c["line"]}" stroke-dasharray="2 4"/>')
        if m%2==1: d.text(x,H-20,dtm.date(y_,mo,1).strftime("%b").upper(),10,c["dim"],"JBM",500,"middle",ls=1)
    nx=X(END.isoformat()); d.add(f'<line x1="{nx:.1f}" y1="{top-14}" x2="{nx:.1f}" y2="{top+len(lanes)*LH}" stroke="{c["acc"]}" stroke-opacity=".6"/>'); d.text(nx,top-20,"NOW",10,c["acc"],"JBM",700,"middle",ls=1.5)
    for i,l in enumerate(lanes):
        y=top+i*LH+LH/2
        d.add(f'<line x1="{gx}" y1="{y}" x2="{gx+gw}" y2="{y}" stroke="{c["line2"]}"/>')
        d.add(f'<circle cx="38" cy="{y}" r="5" fill="{col[l]}"/>'); d.text(52,y+4,l,11,c["bone"],"JBM",500,ls=1.6)
        items=sorted([r for r in REPOS2 if r[3]==l],key=lambda r:r[1])
        for k,(n,dt,sz,_) in enumerate(items):
            x=X(dt); same=[r for r in items if r[1]==dt]
            if len(same)>1: x+= (same.index((n,dt,sz,_))-.5)*14
            r=4+min(7,math.log10(sz+1)*1.6)
            up=k%2==0
            d.add(f'<circle cx="{x:.1f}" cy="{y}" r="{r:.1f}" fill="{col[l]}" stroke="{c["bg"]}" stroke-width="2"/>')
            ly=y-r-8 if up else y+r+16
            anc="end" if x>gx+gw-70 else "start" if x<gx+40 else "middle"
            ov={"SenseLink":("end",8),"Project-Hermes":("start",-8)}
            lx=x
            if n in ov: anc,dx=ov[n]; lx=x+dx
            d.text(lx,ly,n,11,c["body"],"JBM",400,anc)
    return d.render()


# ======================= README =======================
BT=chr(96)
def README(base="assets/"):
    A=lambda n:f"{base}{n}.svg"
    wins=[("win-1","Cassini-Vivant"),("win-2","ProjectKit"),("win-3",None),("win-4","Project-Hermes"),("win-5",None),("win-6",None)]
    def cell(n,repo):
        img=f'<img src="{A(n)}" width="100%" alt="{n}" />'
        return f'<td width="50%" valign="top">'+(f'<a href="https://github.com/Shanks07-404/{repo}">{img}</a>' if repo else img)+'</td>'
    rows="".join("<tr>\n"+cell(*wins[i])+"\n"+cell(*wins[i+1])+"\n</tr>\n" for i in range(0,6,2))
    return f'''<div align="center">

<img src="{A("hero")}" alt="Vrushank Tipnis — data → machine learning → agentic AI" width="100%" />

<br/>

<a href="https://www.linkedin.com/in/vrushanktipnis13/"><img src="{A("chip-linkedin")}" height="34" alt="linkedin" /></a>
<a href="mailto:vrushank.works@gmail.com"><img src="{A("chip-email")}" height="34" alt="email" /></a>

<img src="{A("divider")}" width="100%" alt="" />

</div>

### {BT}01{BT} &nbsp;ABOUT

CS student at **BITS Pilani, Dubai**. I started in data science, moved into machine learning, and now spend most of my time on **agentic AI**: agents that delegate to each other, act, and remember what happened last time.

I like understanding things from the inside. I wrote an autograd engine before trusting {BT}.backward(){BT}, and an OAuth server before trusting Keycloak. Away from the keyboard I solve Rubik's cubes, which is roughly the same habit.

Open to **AI/ML engineering internships**.

<div align="center"><img src="{A("toolkit")}" alt="Toolkit" width="100%" /></div>

<div align="center"><img src="{A("divider")}" width="100%" alt="" /></div>

### {BT}02{BT} &nbsp;EXPERIENCE

<sub>*three internships, each one a layer further up the stack.*</sub>

<div align="center"><img src="{A("experience")}" alt="Internships" width="100%" /></div>

### {BT}03{BT} &nbsp;CURRENTLY

<sub>*research that isn't finished yet, and a paper moving onto real hardware.*</sub>

<div align="center"><img src="{A("now")}" alt="Current work" width="100%" /></div>

<div align="center"><img src="{A("divider")}" width="100%" alt="" /></div>

### {BT}04{BT} &nbsp;WINS

<sub>*five podiums, four of them first. click a card for the code.*</sub>

<table>
{rows}</table>

<div align="center"><img src="{A("divider")}" width="100%" alt="" /></div>

### {BT}05{BT} &nbsp;STATS

<sub>*pulled from the GitHub API and redrawn every day by an Action in this repo.*</sub>

<div align="center">

<img src="{A("stats")}" alt="GitHub stats" width="100%" />

<img src="{A("buildlog")}" alt="Build log: every public repo by start date" width="100%" />

</div>

### {BT}06{BT} &nbsp;THE SNAKE

<sub>*the same year, eaten one square at a time.*</sub>

<div align="center"><img src="{A("snake")}" alt="Contribution snake" width="100%" /></div>

<div align="center">

<img src="{A("divider")}" width="100%" alt="" />

<sub>data → models → agents &nbsp;·&nbsp; sharjah, uae</sub>

</div>
'''

# ======================= MAIN =======================
def main():
    load()
    c=P("violet"); out="assets"; os.makedirs(out,exist_ok=True)
    snake_src=urllib.request.urlopen(f"https://raw.githubusercontent.com/{USER}/{USER}/output/github-contribution-grid-snake-dark.svg",timeout=30).read().decode()
    files={"hero":hero(c),"chip-linkedin":chip(c,"linkedin",""),"chip-email":chip(c,"email",""),"divider":divider(c),
           "experience":experience(c),"now":now(c),"stats":stats(c),"toolkit":rhythm(c),"buildlog":buildlog(c),"snake":snake(c,snake_src)}
    for i,w in enumerate(WINS2): files[f"win-{i+1}"]=win(c,i,w)
    files["win-6"]=win(c,5,None)
    import hashlib
    for k,v in files.items(): open(f"{out}/{k}.svg","w",encoding="utf-8").write(v)
    md=README("assets/")
    for k,v in files.items():
        hsh=hashlib.sha1(v.encode()).hexdigest()[:8]
        md=md.replace(f'assets/{k}.svg"',f'assets/{k}.svg?v={hsh}"')
    open("README.md","w",encoding="utf-8").write(md)
    print("built",len(files),"assets")
if __name__=="__main__": main()
