import html
import streamlit as st

CSS = """
<style>
.stApp{background:#ffffff}
[data-testid="stSidebar"]{background:#f0fdf4;border-right:1px solid #dcfce7}
h1,h2,h3,h4{color:#14532d}
#MainMenu, footer{visibility:hidden}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border-radius:10px;font-weight:600}
.hero{background-size:cover;background-position:center;border-radius:20px;padding:44px 32px;margin-bottom:22px;color:#fff;box-shadow:0 6px 20px rgba(22,163,74,.25)}
.hero h1{color:#fff!important;margin:6px 0 4px 0;font-size:2.1rem}
.hero p{margin:0;opacity:.95;font-size:1.02rem}
.hero .badge{display:inline-block;background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.5);padding:3px 12px;border-radius:999px;font-size:.82rem;font-weight:600}
.card{background:#fff;border:1px solid #dcfce7;border-radius:16px;padding:14px 18px;box-shadow:0 2px 8px rgba(22,163,74,.08);margin-bottom:10px}
.card .amt{float:right;font-weight:700;color:#16a34a}
.tripcard{border:1px solid #dcfce7;border-radius:16px;overflow:hidden;box-shadow:0 2px 8px rgba(22,163,74,.08);margin-bottom:8px;background:#fff}
.tripcard .img{height:120px;background-size:cover;background-position:center}
.tripcard .body{padding:10px 14px}
.tripcard .body b{color:#14532d}
.pos{color:#16a34a;font-weight:700}
.neg{color:#dc2626;font-weight:700}
.muted{color:#6b7280;font-size:.85rem}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def _bg(image_url, dark=0.5):
    if image_url:
        u = html.escape(image_url, quote=True)
        return f"linear-gradient(rgba(5,46,22,{dark}),rgba(5,46,22,{dark})),url('{u}')"
    return "linear-gradient(135deg,#15803d,#4ade80)"


def hero(title, subtitle="", image_url=None, badge=""):
    b = f'<span class="badge">{html.escape(badge)}</span>' if badge else ""
    st.markdown(
        f'<div class="hero" style="background-image:{_bg(image_url)}">{b}'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def trip_hero(trip, heading):
    status = "✅ Completed" if trip.get("status") == "completed" else "🟢 Active"
    hero(trip["name"], heading, trip.get("cover_url"), badge=f"{status}  ·  Code {trip['code']}")


def trip_card(trip):
    u = _bg(trip.get("cover_url"), 0.25)
    st.markdown(
        f'<div class="tripcard"><div class="img" style="background-image:{u}"></div>'
        f'<div class="body"><b>{html.escape(trip["name"])}</b><br>'
        f'<span class="muted">Code {trip["code"]} · {trip["currency"]} · {trip["status"]}</span></div></div>',
        unsafe_allow_html=True,
    )
