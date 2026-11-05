import pandas as pd
import plotly.express as px
import streamlit as st
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.realtime import live_watch

GREENS = ["#14532d", "#166534", "#16a34a", "#22c55e", "#4ade80", "#86efac", "#bbf7d0", "#65a30d", "#a3e635"]

trip = setup_page("Charts", "📊")
trip_hero(trip, "Spending insights")
live_watch(trip["id"])
cur = trip["currency"]

members = db.get_members(trip["id"])
names = {m["id"]: m["name"] for m in members}
expenses = db.get_expenses(trip["id"])
if not expenses:
    st.info("Add some expenses to see charts.")
    st.stop()

df = pd.DataFrame([{"date": e["expense_date"], "category": e["category"],
                    "amount": float(e["amount"]), "paid_by": names[e["paid_by"]]} for e in expenses])

a, b = st.columns(2)
with a:
    fig = px.pie(df, names="category", values="amount", hole=0.5, title="By category",
                 color_discrete_sequence=GREENS)
    st.plotly_chart(fig, use_container_width=True)
with b:
    daily = df.groupby("date", as_index=False)["amount"].sum()
    fig = px.bar(daily, x="date", y="amount", title=f"Spending per day ({cur})", color_discrete_sequence=["#16a34a"])
    st.plotly_chart(fig, use_container_width=True)

paid = df.groupby("paid_by")["amount"].sum()
share = {}
for e in expenses:
    for s in e["expense_splits"]:
        share[names[s["member_id"]]] = share.get(names[s["member_id"]], 0) + float(s["share_amount"])
pp = pd.DataFrame({"person": list(names.values())})
pp["Paid"] = pp["person"].map(paid).fillna(0)
pp["Share (owed)"] = pp["person"].map(share).fillna(0)
fig = px.bar(pp.melt("person", var_name="type", value_name="amount"), x="person", y="amount",
             color="type", barmode="group", title="Paid vs fair share",
             color_discrete_map={"Paid": "#16a34a", "Share (owed)": "#bbf7d0"})
st.plotly_chart(fig, use_container_width=True)
