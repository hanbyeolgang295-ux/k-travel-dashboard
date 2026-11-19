"""K-TRAVEL PASSPORT — 2026 방한 관광 대시보드 (12주차 배포 실습).
데이터: 실습용 가상 데이터(코드 안에서 생성) · 실제 통계 아님.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="K-TRAVEL PASSPORT", page_icon="🛂", layout="wide")

# ---------------- 데이터 (실습용 가상 데이터) ----------------
COUNTRIES = {
    "중국": (39.9, 116.4, 520, 1.9), "일본": (35.7, 139.7, 300, 1.4), "미국": (38.9, -77.0, 140, 2.3),
    "대만": (25.0, 121.5, 120, 1.3), "베트남": (21.0, 105.8, 70, 1.1), "필리핀": (14.6, 121.0, 55, 1.0),
    "태국": (13.8, 100.5, 50, 1.2), "홍콩": (22.3, 114.2, 45, 1.6),
}
FLAG = {"중국": "🇨🇳", "일본": "🇯🇵", "미국": "🇺🇸", "대만": "🇹🇼", "베트남": "🇻🇳", "필리핀": "🇵🇭", "태국": "🇹🇭", "홍콩": "🇭🇰"}


@st.cache_data
def make_data():
    rng = np.random.default_rng(2026)
    season = np.array([.78, .85, 1.0, 1.08, 1.12, .98, 1.05, 1.1, 1.0, 1.15, 1.06, .9])
    rows = []
    for c, (lat, lon, base, spend) in COUNTRIES.items():
        for m in range(1, 13):
            v = base * season[m - 1] * (1 + .015 * m) * rng.uniform(.93, 1.07)
            rows.append({"국가": c, "월": m, "lat": lat, "lon": lon,
                         "방문객(천 명)": round(v, 1),
                         "1인 지출(백만원)": round(spend * rng.uniform(.9, 1.1), 2),
                         "만족도(5점)": round(rng.uniform(3.9, 4.7), 2)})
    df = pd.DataFrame(rows)
    df["지출 합계(억원)"] = (df["방문객(천 명)"] * 1000 * df["1인 지출(백만원)"] / 100).round(0)
    return df


data = make_data()

# ---------------- 스타일 ----------------
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
:root { --ink:#f3f5ff; --muted:#8f9bc0; --gold:#ffd166; --pink:#ff4d8d; --cyan:#3ee0ff; }
#MainMenu, footer, header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"] { display:none !important; }
section[data-testid="stSidebar"], div[data-testid="collapsedControl"] { display:none !important; }
.block-container { padding-top:1.2rem !important; max-width:1280px; }
.stApp { background:#05060f; overflow-x:hidden; }
.stApp::before, .stApp::after { content:""; position:fixed; width:70vmax; height:70vmax; border-radius:50%;
  filter:blur(90px); opacity:.55; z-index:0; pointer-events:none; }
.stApp::before { background:radial-gradient(circle,#3b2bff 0%,transparent 60%); top:-30vmax; left:-20vmax; animation:blobA 18s ease-in-out infinite alternate; }
.stApp::after { background:radial-gradient(circle,#ff2d87 0%,transparent 60%); bottom:-35vmax; right:-25vmax; animation:blobB 22s ease-in-out infinite alternate; }
@keyframes blobA { to { transform:translate(30vw,20vh) scale(1.2); } }
@keyframes blobB { to { transform:translate(-25vw,-15vh) scale(1.15); } }
.block-container > div { position:relative; z-index:1; }
html, body, .stApp, p, label, span, div, button { font-family:'Pretendard',sans-serif !important; }
.stApp p, .stApp label, h1, h2, h3 { color:var(--ink) !important; }
@keyframes rise { from{opacity:0;transform:translateY(28px) scale(.98);filter:blur(6px)} to{opacity:1;transform:none;filter:none} }
@keyframes shine { to { background-position:200% center; } }
.sec { margin:34px 0 10px; display:flex; align-items:baseline; gap:12px; animation:rise .9s both; }
.sec .no { font-weight:900; font-size:.8rem; letter-spacing:3px; color:var(--cyan); }
.sec h2 { margin:0; font-size:1.6rem; font-weight:900; letter-spacing:-.5px;
  background:linear-gradient(90deg,#fff,#b9c4ff,#ff9cc4,#fff); background-size:200% auto;
  -webkit-background-clip:text; background-clip:text; color:transparent !important; animation:shine 6s linear infinite; }
.panel { border-radius:22px; padding:14px 18px 6px; background:rgba(255,255,255,.035);
  border:1px solid rgba(255,255,255,.08); backdrop-filter:blur(14px); animation:rise .9s both; }
div[data-testid="stPlotlyChart"] { border-radius:22px; background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.08);
  padding:6px; animation:rise 1s both; transition:transform .3s, border-color .3s; }
div[data-testid="stPlotlyChart"]:hover { transform:translateY(-3px); border-color:rgba(62,224,255,.45); }
div[data-testid="stElementContainer"]:has(> iframe) { animation:rise 1s both; }
.insight { border-radius:18px; padding:16px 22px; margin:14px 0; animation:rise 1s .3s both; font-size:1.05rem;
  background:linear-gradient(90deg, rgba(255,209,102,.18), rgba(255,77,141,.08)); border:1px solid rgba(255,209,102,.4);
  box-shadow:0 0 40px rgba(255,209,102,.12); }
button[data-baseweb="tab"] { background:transparent !important; }
button[data-baseweb="tab"] p { font-weight:800; font-size:1rem; }
div[data-baseweb="tab-highlight"] { background:linear-gradient(90deg,var(--cyan),var(--pink)) !important; height:3px !important; }
div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div { background:rgba(255,255,255,.05) !important; border-color:rgba(255,255,255,.12) !important; }
div[data-baseweb="select"] > div { background:rgba(255,255,255,.06) !important; color:#fff !important; }
span[data-baseweb="tag"] { background:linear-gradient(90deg,#3b2bff,#ff2d87) !important; }
.foot { text-align:center; color:var(--muted) !important; font-size:.8rem; margin:40px 0 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- 히어로: 캔버스 모션 그래픽 ----------------
import json as _json
pts = [{"n": c, "lat": v[0], "lon": v[1], "w": v[2]} for c, v in COUNTRIES.items()]
components.html("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
html,body{margin:0;background:transparent;overflow:hidden;font-family:'Pretendard',sans-serif;color:#f3f5ff}
#w{position:relative;height:440px;border-radius:28px;overflow:hidden;
 background:radial-gradient(120% 90% at 70% 40%,rgba(59,43,255,.35),transparent 60%),linear-gradient(160deg,#0a0c22,#120a24);
 border:1px solid rgba(255,255,255,.1)}
canvas{position:absolute;inset:0;width:100%;height:100%}
.t{position:absolute;left:44px;top:46px;max-width:520px;z-index:2}
.k{font-weight:900;letter-spacing:5px;font-size:12px;color:#3ee0ff;opacity:0;animation:in .8s .2s forwards}
h1{margin:10px 0 12px;font-size:54px;line-height:1.05;font-weight:900;letter-spacing:-2px;opacity:0;animation:in .9s .4s forwards;
 background:linear-gradient(90deg,#fff 0%,#b9c4ff 30%,#ff9cc4 60%,#fff 100%);background-size:200% auto;-webkit-background-clip:text;color:transparent;
 animation:in .9s .4s forwards, sh 5s linear infinite}
p{color:#a7b0d6;font-size:16px;margin:0;opacity:0;animation:in .9s .7s forwards}
.chips{margin-top:22px;display:flex;gap:8px;opacity:0;animation:in .9s 1s forwards}
.chip{padding:7px 14px;border-radius:999px;font-size:13px;font-weight:700;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14)}
.live{display:inline-block;width:8px;height:8px;border-radius:50%;background:#3ee0ff;margin-right:6px;box-shadow:0 0 0 0 #3ee0ff;animation:pl 1.6s infinite}
@keyframes in{from{opacity:0;transform:translateY(22px);filter:blur(8px)}to{opacity:1;transform:none;filter:none}}
@keyframes sh{to{background-position:200% center}}
@keyframes pl{70%{box-shadow:0 0 0 10px rgba(62,224,255,0)}100%{box-shadow:0 0 0 0 rgba(62,224,255,0)}}
</style>
<div id="w"><canvas id="c"></canvas>
<div class="t"><div class="k">K-TRAVEL PASSPORT · 2026</div>
<h1>2026 방한 관광<br>인사이트 대시보드</h1>
<p>8개국 · 12개월 방문객 · 지출 · 만족도를 한 화면에서 비교합니다</p>
<div class="chips"><span class="chip"><span class="live"></span>LIVE ROUTES</span><span class="chip">✈ 8 COUNTRIES</span><span class="chip">📅 12 MONTHS</span></div></div></div>
<script>
const P=__PTS__, SEOUL={lat:37.57,lon:126.98};
const cv=document.getElementById('c'),x=cv.getContext('2d');let W,H,D=devicePixelRatio||1;
function rs(){W=cv.clientWidth;H=cv.clientHeight;cv.width=W*D;cv.height=H*D;x.setTransform(D,0,0,D,0,0)}rs();addEventListener('resize',rs);
const pr=(la,lo)=>{if(lo<0)lo=178;return[W*0.46+(lo-95)/(85)*W*0.5, H*0.9-(la-8)/(40)*H*0.8]};
const stars=[...Array(160)].map(()=>({x:Math.random(),y:Math.random(),r:Math.random()*1.3+.2,p:Math.random()*6}));
const grid=[];for(let la=8;la<=50;la+=1.6)for(let lo=95;lo<=180;lo+=1.6)grid.push([la,lo]);
const cols=['#3ee0ff','#ff4d8d','#ffd166','#7ef0b8','#b49bff','#ff9f5a','#6f8bff','#ff8fc7'];
const planes=[];P.forEach((p,i)=>{const n=Math.max(1,Math.round(p.w/120));for(let k=0;k<n;k++)planes.push({i,t:Math.random(),s:.0025+Math.random()*.002})});
let T=0;
function arc(a,b,t){const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2-Math.hypot(b[0]-a[0],b[1]-a[1])*.35;
 const u=1-t;return[u*u*a[0]+2*u*t*mx+t*t*b[0],u*u*a[1]+2*u*t*my+t*t*b[1]]}
function f(){T+=1;x.clearRect(0,0,W,H);
 stars.forEach(s=>{x.globalAlpha=.25+.35*Math.sin(T*.02+s.p);x.fillStyle='#fff';x.beginPath();x.arc(s.x*W,s.y*H,s.r,0,7);x.fill()});
 x.globalAlpha=1;x.fillStyle='rgba(140,160,255,.13)';grid.forEach(g=>{const q=pr(g[0],g[1]);x.fillRect(q[0],q[1],1.4,1.4)});
 const S=pr(SEOUL.lat,SEOUL.lon), grow=Math.min(1,T/90);
 P.forEach((p,i)=>{const A=pr(p.lat,p.lon);x.strokeStyle=cols[i];x.globalAlpha=.28;x.lineWidth=1.2;x.setLineDash([3,5]);x.lineDashOffset=-T*.4;
  x.beginPath();for(let t=0;t<=grow;t+=.02){const q=arc(A,S,t);t?x.lineTo(q[0],q[1]):x.moveTo(q[0],q[1])}x.stroke();x.setLineDash([]);
  const r=4+p.w/80;x.globalAlpha=.9;x.fillStyle=cols[i];x.beginPath();x.arc(A[0],A[1],3,0,7);x.fill();
  x.globalAlpha=.35*(1-((T*.01+i*.13)%1));x.beginPath();x.arc(A[0],A[1],r*((T*.01+i*.13)%1)*2,0,7);x.strokeStyle=cols[i];x.lineWidth=1.5;x.stroke();
  x.globalAlpha=.85;x.fillStyle='#cfd6ff';x.font='600 11px Pretendard';x.fillText(p.n,A[0]+7,A[1]+4)});
 if(T>60)planes.forEach(pl=>{pl.t+=pl.s;if(pl.t>1)pl.t=0;const A=pr(P[pl.i].lat,P[pl.i].lon);
  for(let k=0;k<14;k++){const tt=pl.t-k*.012;if(tt<0)break;const q=arc(A,S,tt);x.globalAlpha=(1-k/14)*.9;x.fillStyle=cols[pl.i];
   x.beginPath();x.arc(q[0],q[1],2.6*(1-k/14)+.4,0,7);x.fill()}});
 for(let k=0;k<3;k++){const ph=((T*.012)+k/3)%1;x.globalAlpha=(1-ph)*.7;x.strokeStyle='#ffd166';x.lineWidth=2;x.beginPath();x.arc(S[0],S[1],6+ph*46,0,7);x.stroke()}
 x.globalAlpha=1;x.shadowColor='#ffd166';x.shadowBlur=24;x.fillStyle='#ffd166';x.beginPath();x.arc(S[0],S[1],6,0,7);x.fill();x.shadowBlur=0;
 x.font='900 13px Pretendard';x.fillStyle='#fff';x.fillText('SEOUL',S[0]+12,S[1]-10);
 requestAnimationFrame(f)}f();
</script>
""".replace("__PTS__", _json.dumps(pts, ensure_ascii=False)), height=450)

# ---------------- 필터 (인라인) ----------------
st.markdown("<div class='sec'><span class='no'>01</span><h2>입국 심사대 · 조건 고르기</h2></div>", unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns([5, 3, 4])
countries = fc1.multiselect("국가", list(COUNTRIES), default=list(COUNTRIES))
months = fc2.slider("월 범위", 1, 12, (1, 12))
metric = fc3.radio("지표", ["방문객(천 명)", "지출 합계(억원)", "만족도(5점)"], horizontal=True)

view = data[data["국가"].isin(countries) & data["월"].between(*months)]
if view.empty:
    st.warning("국가를 하나 이상 선택하세요.")
    st.stop()

agg = "mean" if metric == "만족도(5점)" else "sum"
by_c = view.groupby("국가", as_index=False).agg(값=(metric, agg), lat=("lat", "first"), lon=("lon", "first"))
by_c = by_c.sort_values("값", ascending=False)
top = by_c.iloc[0]

st.markdown("<div class='sec'><span class='no'>02</span><h2>한눈에 보는 숫자</h2></div>", unsafe_allow_html=True)

# ---------------- KPI (카운트업) ----------------
visitors = view["방문객(천 명)"].sum()
spend = view["지출 합계(억원)"].sum()
sat = view["만족도(5점)"].mean()
kpi = [("🧳", "총 방문객", visitors, 1, "천 명"), ("💳", "관광 지출", spend, 0, "억원"),
       ("⭐", "평균 만족도", sat, 2, "/ 5"), (FLAG[top["국가"]], f"1위 · {top['국가']}", top["값"], 1 if agg == "sum" else 2, "")]
cards = "".join(f"""<div class="k" style="animation-delay:{.15 + i*.15}s"><div class="i">{a}</div><div class="l">{b}</div>
<div class="v"><span data-to="{c}" data-d="{d}">0</span> <small>{e}</small></div></div>""" for i, (a, b, c, d, e) in enumerate(kpi))
components.html(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>body{{margin:0;font-family:'Pretendard',sans-serif;background:transparent}}
.r{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} @media(max-width:700px){{.r{{grid-template-columns:1fr 1fr}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
.k{{position:relative;overflow:hidden;border-radius:22px;padding:18px 20px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.1);
 color:#f3f5ff;animation:rise .7s both;transition:.3s}} .k:hover{{transform:translateY(-6px) scale(1.02);border-color:#3ee0ff;box-shadow:0 18px 40px rgba(62,224,255,.18)}}
.k::after{{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.12) 50%,transparent 70%);transform:translateX(-100%);animation:sw 3.5s 1.2s infinite}}
@keyframes sw{{to{{transform:translateX(100%)}}}}
.k:nth-child(1){{border-top:3px solid #3ee0ff}} .k:nth-child(2){{border-top:3px solid #ff4d8d}} .k:nth-child(3){{border-top:3px solid #ffd166}} .k:nth-child(4){{border-top:3px solid #b49bff}}
.i{{font-size:1.5rem}} .l{{color:#9aa6c4;font-size:.85rem;margin-top:2px}} .v{{font-size:2.1rem;font-weight:900;letter-spacing:-1px}}
.v small{{font-size:.85rem;color:#9aa6c4;font-weight:600}}</style>
<div class="r">{cards}</div>
<script>setTimeout(()=>document.querySelectorAll('[data-to]').forEach(el=>{{const to=+el.dataset.to,d=+el.dataset.d,t0=performance.now();
const f=n=>{{const p=Math.min((n-t0)/1200,1),e=1-Math.pow(1-p,3);el.textContent=(to*e).toLocaleString('ko-KR',{{minimumFractionDigits:d,maximumFractionDigits:d}});if(p<1)requestAnimationFrame(f)}};requestAnimationFrame(f)}}),500)</script>
""", height=135)

share = by_c["값"].iloc[0] / by_c["값"].sum() * 100 if agg == "sum" else None
mon = view.groupby("월")["방문객(천 명)"].sum()
peak_m, low_m = int(mon.idxmax()), int(mon.idxmin())
sat_c = view.groupby("국가")["만족도(5점)"].mean()
spc = view.groupby("국가")["1인 지출(백만원)"].mean()
ins = [("🏆", "1위 국가", f"{FLAG[top['국가']]} {top['국가']}", (f"선택 국가 중 {share:.1f}% 차지" if share else f"평균 {top['값']:.2f}점"), "#3ee0ff"),
       ("📈", "성수기", f"{peak_m}월", f"비수기 {low_m}월보다 {mon.max()/mon.min():.1f}배 많음", "#ff4d8d"),
       ("💎", "큰손 국가", f"{FLAG[spc.idxmax()]} {spc.idxmax()}", f"1인 평균 {spc.max():.2f}백만원 지출", "#ffd166"),
       ("😊", "만족도 1위", f"{FLAG[sat_c.idxmax()]} {sat_c.idxmax()}", f"평균 {sat_c.max():.2f} / 5점", "#b49bff")]
html = "".join(f"<div class='ic' style='--c:{c};animation-delay:{.1+i*.12}s'><div class='ih'>{e} {t}</div><div class='iv'>{v}</div><div class='is'>{d}</div></div>" for i,(e,t,v,d,c) in enumerate(ins))
st.markdown("""<style>.ig{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:6px 0 4px}
@media(max-width:800px){.ig{grid-template-columns:1fr 1fr}}
.ic{border-radius:20px;padding:18px 20px;background:linear-gradient(160deg,color-mix(in srgb,var(--c) 22%,transparent),rgba(255,255,255,.03));
border:1px solid color-mix(in srgb,var(--c) 55%,transparent);box-shadow:0 0 30px color-mix(in srgb,var(--c) 18%,transparent);animation:rise .8s both}
.ih{font-size:.85rem;font-weight:800;color:var(--c)}.iv{font-size:1.7rem;font-weight:900;margin:6px 0 2px;color:#fff}.is{font-size:.85rem;color:#c3cbe8}</style>""", unsafe_allow_html=True)
st.markdown("<div class='sec'><span class='no'>INSIGHT</span><h2>데이터가 말해주는 4가지</h2></div>", unsafe_allow_html=True)
st.markdown(f"<div class='ig'>{html}</div>", unsafe_allow_html=True)

# ---------------- 차트 ----------------
PAL = ["#3ee0ff", "#ff4d8d", "#ffd166", "#7ef0b8", "#b49bff", "#ff9f5a", "#6f8bff", "#ff8fc7"]
CMAP = {c: PAL[i] for i, c in enumerate(COUNTRIES)}
BASE = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", color="#eef2ff"), margin=dict(l=10, r=10, t=50, b=10))

st.markdown("<div class='sec'><span class='no'>03</span><h2>항로 · 흐름 · 기록</h2></div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🌏 세계 지도 재생", "📈 월별 흐름", "🗂️ 입국 기록"])

with t1:
    mv = view.copy()
    fig = px.scatter_geo(mv, lat="lat", lon="lon", size="방문객(천 명)", color="국가", hover_name="국가",
                         animation_frame="월", color_discrete_map=CMAP, size_max=55, projection="natural earth",
                         hover_data={"lat": False, "lon": False, "방문객(천 명)": ":.1f", "만족도(5점)": ":.2f"},
                         title="▶ 재생을 누르면 월별로 관광객 버블이 커졌다 작아져요")
    fig.add_trace(go.Scattergeo(lat=[37.57], lon=[126.98], mode="markers+text", text=["SEOUL"],
                                textposition="top center", marker=dict(size=12, color="#f4c95d", symbol="star"),
                                showlegend=False, hoverinfo="skip"))
    fig.update_geos(bgcolor="rgba(0,0,0,0)", landcolor="#161a3a", oceancolor="rgba(0,0,0,0)", showocean=True,
                    countrycolor="#2c3a6b", coastlinecolor="#2c3a6b", lataxis_range=[-5, 60], lonaxis_range=[60, 160])
    fig.update_layout(**BASE, height=520, legend=dict(orientation="h", y=-.05))
    st.plotly_chart(fig, width="stretch")

with t2:
    a, b = st.columns([3, 2])
    with a:
        line = view.groupby(["월", "국가"], as_index=False)[metric].agg(agg)
        f2 = px.line(line, x="월", y=metric, color="국가", markers=True, color_discrete_map=CMAP,
                     title=f"월별 {metric}")
        f2.update_traces(line=dict(width=3), marker=dict(size=7))
        f2.update_layout(**BASE, hovermode="x unified", legend=dict(orientation="h", y=1.02, yanchor="bottom", x=1, xanchor="right", title=None))
        f2.update_xaxes(dtick=1, gridcolor="rgba(255,255,255,.06)")
        f2.update_yaxes(gridcolor="rgba(255,255,255,.06)", rangemode="tozero")
        st.plotly_chart(f2, width="stretch")
    with b:
        rank = by_c.sort_values("값")
        rank["라벨"] = rank["국가"].map(lambda c: f"{FLAG[c]} {c}")
        f3 = px.bar(rank, x="값", y="라벨", orientation="h", color="국가", color_discrete_map=CMAP,
                    text="값", title=f"국가 순위 · {metric}")
        f3.update_traces(texttemplate="%{text:,.1f}", textposition="outside", marker_cornerradius=8, showlegend=False)
        f3.update_layout(**BASE, yaxis_title=None, xaxis_title=None)
        f3.update_xaxes(showgrid=False, showticklabels=False)
        st.plotly_chart(f3, width="stretch")

with t3:
    st.dataframe(view.drop(columns=["lat", "lon"]), hide_index=True, width="stretch",
                 column_config={"만족도(5점)": st.column_config.ProgressColumn("만족도(5점)", min_value=0, max_value=5, format="%.2f")})
    st.download_button("⬇️ 입국 기록 CSV 저장", view.to_csv(index=False).encode("utf-8-sig"), "k_travel.csv", "text/csv")

st.markdown("<div class='foot'>데이터: 실습용 가상 데이터(코드 안에서 생성) · 실제 관광 통계 아님 · 산업데이터시각화 12주차 배포 실습</div>", unsafe_allow_html=True)
