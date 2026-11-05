import streamlit as st
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.calculations import compute_balances, suggest_payments, money
from utils.realtime import live_watch

trip = setup_page("Balances", "⚖️")
trip_hero(trip, "Who owes whom")
live_watch(trip["id"])
cur = trip["currency"]

members = db.get_members(trip["id"])
names = {m["id"]: m["name"] for m in members}
expenses = db.get_expenses(trip["id"])
settlements = db.get_settlements(trip["id"])
bal = compute_balances(members, expenses, settlements)

total = sum(float(e["amount"]) for e in expenses)
m1, m2, m3 = st.columns(3)
m1.metric("Total spent", money(cur, total))
m2.metric("People", len(members))
m3.metric("Per person (avg)", money(cur, total / len(members) if members else 0))

st.markdown("#### Net balance")
cols = st.columns(min(len(members), 4) or 1)
for i, m in enumerate(members):
    v = bal[m["id"]]
    cls, txt = ("pos", "gets back") if v > 0.009 else (("neg", "owes") if v < -0.009 else ("muted", "settled"))
    with cols[i % len(cols)]:
        st.markdown(
            f'<div class="card"><b>{m["name"]}</b><br><span class="{cls}">{money(cur, abs(v))}</span>'
            f'<br><span class="muted">{txt}</span></div>', unsafe_allow_html=True)

st.markdown("#### Who pays whom")
pays = suggest_payments(bal)
if not pays:
    st.success("🎉 Everyone is settled up!")
for f, t, amt in pays:
    st.markdown(f'<div class="card"><b>{names[f]}</b> → <b>{names[t]}</b>'
                f'<span class="amt">{money(cur, amt)}</span></div>', unsafe_allow_html=True)
if pays:
    st.page_link("pages/6_💸_Settle_Up.py", label="Go to Settle Up", icon="💸")
