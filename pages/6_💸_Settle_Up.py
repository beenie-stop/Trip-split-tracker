import streamlit as st
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.calculations import compute_balances, suggest_payments, money
from utils.realtime import live_watch

trip = setup_page("Settle Up", "💸")
trip_hero(trip, "Settle up with the fewest payments")
live_watch(trip["id"])
cur = trip["currency"]

members = db.get_members(trip["id"])
names = {m["id"]: m["name"] for m in members}
upi = {m["id"]: m.get("upi_id") for m in members}
expenses = db.get_expenses(trip["id"])
settlements = db.get_settlements(trip["id"])
pays = suggest_payments(compute_balances(members, expenses, settlements))

st.markdown("#### Payments to make")
if not pays:
    st.success("🎉 All settled! Head to Export to download your trip summary.")

for f, t, amt in pays:
    with st.container(border=True):
        st.markdown(f"**{names[f]}** pays **{names[t]}** &nbsp; <span class='pos'>{money(cur, amt)}</span>",
                    unsafe_allow_html=True)
        if upi.get(t):
            st.caption(f"{names[t]}'s UPI ID: `{upi[t]}`")
        a, b, c = st.columns([1, 2, 1])
        method = a.selectbox("Method", ["UPI", "Cash"], key=f"m_{f}_{t}")
        note = b.text_input("Note / UPI ref (optional)", key=f"n_{f}_{t}")
        c.write("")
        if c.button("Mark as paid", key=f"p_{f}_{t}", type="primary", use_container_width=True):
            db.add_settlement(trip["id"], f, t, amt, method, note)
            st.rerun()

st.markdown("#### Payment history")
if not settlements:
    st.caption("No payments recorded yet.")
for s in settlements:
    a, b = st.columns([5, 1])
    a.markdown(f"✅ **{names[s['from_member']]}** paid **{names[s['to_member']]}** "
               f"{money(cur, float(s['amount']))} via {s['method']} · {s['created_at'][:10]}"
               + (f" · _{s['note']}_" if s.get("note") else ""))
    if b.button("Undo", key=f"undo_{s['id']}"):
        db.delete_settlement(s["id"])
        st.rerun()
