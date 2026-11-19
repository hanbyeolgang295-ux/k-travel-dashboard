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
:root { --ink:#eef2ff; --muted:#9aa6c4; --gold:#f4c95d; --red:#ff5d73; --sky:#58c4ff; }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #233a7a 0%, transparent 60%),
                     radial-gradient(900px 500px at 110% 10%, #5b1f4f 0%, transparent 55%), #0b1023; }
html, body, .stApp, .stMarkdown, p, label, span, div { font-family:'Pretendard',sans-serif; }
.stApp, .stMarkdown, p, label, h1, h2, h3 { color: var(--ink) !important; }
section[data-testid="stSidebar"] { background: rgba(255,255,255,.04); border-right:1px solid rgba(255,255,255,.08); }
header[data-testid="stHeader"] { background: transparent; }
@keyframes rise { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:none} }
@keyframes fly { from{offset-distance:0%} to{offset-distance:100%} }
@keyframes dash { to{stroke-dashoffset:0} }
@keyframes stamp { 0%{opacity:0;transform:scale(2.4) rotate(-18deg)} 60%{opacity:1;transform:scale(.9) rotate(-12deg)} 100%{opacity:1;transform:scale(1) rotate(-12deg)} }
@keyframes gate { 0%,70%{opacity:1;visibility:visible} 100%{opacity:0;visibility:hidden} }
.intro { position:fixed; inset:0; z-index:9999; background:#0b1023; display:flex; align-items:center;
  justify-content:center; animation: gate 2.6s ease forwards; pointer-events:none; }
.intro .pp { width:260px; height:340px; border-radius:18px; background:linear-gradient(160deg,#16306b,#0d1c44);
  border:2px solid var(--gold); display:flex; flex-direction:column; align-items:center; justify-content:center;
  color:var(--gold); letter-spacing:4px; font-weight:800; box-shadow:0 20px 60px rgba(0,0,0,.5); position:relative; }
.intro .pp .emb { font-size:64px; }
.intro .st { position:absolute; bottom:40px; right:-30px; border:4px solid var(--red); color:var(--red);
  padding:8px 16px; border-radius:12px; font-weight:900; font-size:20px; letter-spacing:2px;
  animation: stamp .6s .9s cubic-bezier(.2,1.4,.4,1) both; background:rgba(11,16,35,.6); }
.hero { position:relative; border-radius:24px; padding:30px 36px; overflow:hidden; animation:rise .8s 2.4s both;
  background: linear-gradient(135deg, rgba(88,196,255,.16), rgba(255,93,115,.12));
  border:1px solid rgba(255,255,255,.12); backdrop-filter: blur(8px); }
.hero .kick { color:var(--gold); font-weight:800; letter-spacing:3px; font-size:.8rem; }
.hero h1 { margin:.3rem 0 .2rem; font-size:2.3rem; font-weight:900; letter-spacing:-1px; }
.hero p { color:var(--muted) !important; margin:0; }
.hero svg { position:absolute; right:20px; top:6px; opacity:.95; }
.plane { offset-path: path("M10 90 C 120 -10, 260 140, 380 30"); animation: fly 5s 2.6s ease-in-out infinite; font-size:26px; position:absolute; left:0; top:0; }
.route { stroke-dasharray:6 8; stroke-dashoffset:400; animation: dash 3s 2.6s ease forwards; }
.chip { display:inline-block; margin:.8rem .4rem 0 0; padding:5px 12px; border-radius:999px; font-size:.82rem;
  background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12); }
.glass { border-radius:20px; padding:6px 10px; background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.09); animation:rise .8s 2.6s both; }
.insight { border-radius:16px; padding:14px 18px; margin:12px 0; animation:rise .8s 2.7s both;
  background:linear-gradient(90deg, rgba(244,201,93,.16), rgba(244,201,93,.03)); border:1px solid rgba(244,201,93,.35); }
div[data-testid="stPlotlyChart"] { animation: rise .8s 2.6s both; }
button[data-baseweb="tab"] p { font-weight:700; }
</style>
<div class="intro"><div class="pp"><div class="emb">🛂</div><div>PASSPORT</div><div style="font-size:12px;margin-top:8px;opacity:.8">REPUBLIC OF KOREA · 2026</div><div class="st">WELCOME ✈ KOREA</div></div></div>
""", unsafe_allow_html=True)

# ---------------- 사이드바 ----------------
st.sidebar.markdown("### 🛂 입국 심사대")
countries = st.sidebar.multiselect("국가", list(COUNTRIES), default=list(COUNTRIES))
months = st.sidebar.slider("월 범위", 1, 12, (1, 12))
metric = st.sidebar.radio("지표", ["방문객(천 명)", "지출 합계(억원)", "만족도(5점)"])
st.sidebar.caption("데이터: 실습용 가상 데이터 · 실제 관광 통계 아님")

view = data[data["국가"].isin(countries) & data["월"].between(*months)]
if view.empty:
    st.warning("국가를 하나 이상 선택하세요.")
    st.stop()

agg = "mean" if metric == "만족도(5점)" else "sum"
by_c = view.groupby("국가", as_index=False).agg(값=(metric, agg), lat=("lat", "first"), lon=("lon", "first"))
by_c = by_c.sort_values("값", ascending=False)
top = by_c.iloc[0]

# ---------------- 히어로 ----------------
st.markdown(f"""
<div class="hero">
  <div class="kick">K-TRAVEL PASSPORT · 2026</div>
  <h1>올해 한국을 가장 많이 찾은 나라는?</h1>
  <p>국가·월별 방한 관광객, 지출, 만족도를 한 장의 여권처럼 펼쳐 봅니다.</p>
  <span class="chip">📅 {months[0]}~{months[1]}월</span><span class="chip">🌏 {len(countries)}개국</span>
  <span class="chip">📌 {metric}</span>
  <svg width="400" height="130" viewBox="0 0 400 130"><path class="route" d="M10 90 C 120 -10, 260 140, 380 30"
   fill="none" stroke="#f4c95d" stroke-width="2.5"/><circle cx="10" cy="90" r="5" fill="#58c4ff"/>
   <circle cx="380" cy="30" r="6" fill="#ff5d73"/><text x="352" y="20" fill="#fff" font-size="12" font-weight="700">SEOUL</text></svg>
  <div class="plane">✈️</div>
</div>""", unsafe_allow_html=True)

# ---------------- KPI (카운트업) ----------------
visitors = view["방문객(천 명)"].sum()
spend = view["지출 합계(억원)"].sum()
sat = view["만족도(5점)"].mean()
kpi = [("🧳", "총 방문객", visitors, 1, "천 명"), ("💳", "관광 지출", spend, 0, "억원"),
       ("⭐", "평균 만족도", sat, 2, "/ 5"), (FLAG[top["국가"]], f"1위 · {top['국가']}", top["값"], 1 if agg == "sum" else 2, "")]
cards = "".join(f"""<div class="k" style="animation-delay:{2.6 + i*.12}s"><div class="i">{a}</div><div class="l">{b}</div>
<div class="v"><span data-to="{c}" data-d="{d}">0</span> <small>{e}</small></div></div>""" for i, (a, b, c, d, e) in enumerate(kpi))
components.html(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>body{{margin:0;font-family:'Pretendard',sans-serif;background:transparent}}
.r{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} @media(max-width:700px){{.r{{grid-template-columns:1fr 1fr}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
.k{{border-radius:18px;padding:14px 18px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);
 color:#eef2ff;animation:rise .6s both;transition:.2s}} .k:hover{{transform:translateY(-4px);border-color:#f4c95d}}
.i{{font-size:1.5rem}} .l{{color:#9aa6c4;font-size:.85rem;margin-top:2px}} .v{{font-size:1.8rem;font-weight:900}}
.v small{{font-size:.85rem;color:#9aa6c4;font-weight:600}}</style>
<div class="r">{cards}</div>
<script>setTimeout(()=>document.querySelectorAll('[data-to]').forEach(el=>{{const to=+el.dataset.to,d=+el.dataset.d,t0=performance.now();
const f=n=>{{const p=Math.min((n-t0)/1200,1),e=1-Math.pow(1-p,3);el.textContent=(to*e).toLocaleString('ko-KR',{{minimumFractionDigits:d,maximumFractionDigits:d}});if(p<1)requestAnimationFrame(f)}};requestAnimationFrame(f)}}),2500)</script>
""", height=125)

share = by_c["값"].iloc[0] / by_c["값"].sum() * 100 if agg == "sum" else None
msg = (f"🏆 <b>{FLAG[top['국가']]} {top['국가']}</b>이(가) {metric} 1위입니다"
       + (f" — 선택한 국가 전체의 <b>{share:.1f}%</b>를 차지합니다." if share else f" (평균 {top['값']:.2f}점)."))
st.markdown(f"<div class='insight'>{msg}</div>", unsafe_allow_html=True)

# ---------------- 차트 ----------------
PAL = ["#58c4ff", "#ff5d73", "#f4c95d", "#7ee0b5", "#b08cff", "#ff9f5a", "#5f8bff", "#ff8fc7"]
CMAP = {c: PAL[i] for i, c in enumerate(COUNTRIES)}
BASE = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", color="#eef2ff"), margin=dict(l=10, r=10, t=50, b=10))

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
    fig.update_geos(bgcolor="rgba(0,0,0,0)", landcolor="#1b2547", oceancolor="#0b1023", showocean=True,
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

st.caption("데이터: 실습용 가상 데이터(코드 안에서 생성) · 실제 관광 통계가 아니며, 이 자료로 원인을 단정하지 않습니다.")
