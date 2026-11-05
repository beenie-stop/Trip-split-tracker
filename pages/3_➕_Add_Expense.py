import streamlit as st
from datetime import date
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.constants import CATEGORIES, SPLIT_TYPES
from utils.splits import compute_splits

trip = setup_page("Add Expense", "➕")
trip_hero(trip, "Add a new expense")
cur = trip["currency"]

members = db.get_members(trip["id"])
if len(members) < 2:
    st.warning("Add at least one friend in the Members page first.")
    st.stop()

names = {m["id"]: m["name"] for m in members}
ids = list(names)
me = next((m["id"] for m in members if m.get("user_id") == st.session_state.user["id"]), ids[0])

v = st.session_state.setdefault("form_v", 0)
if st.session_state.get("flash"):
    st.success(st.session_state.pop("flash"))

a, b = st.columns([2, 1])
title = a.text_input("Description *", key=f"title_{v}", placeholder="Dinner at the beach shack")
amount = b.number_input(f"Amount ({cur}) *", min_value=0.0, step=10.0, format="%.2f", key=f"amt_{v}")

c, d, e = st.columns(3)
category = c.selectbox("Category", CATEGORIES, key=f"cat_{v}")
when = d.date_input("Date", value=date.today(), key=f"date_{v}")
paid_by = e.selectbox("Paid by", ids, index=ids.index(me), format_func=names.get, key=f"pb_{v}")

participants = st.multiselect("Split between", ids, default=ids, format_func=names.get, key=f"part_{v}")
split_type = st.radio("How to split?", SPLIT_TYPES, horizontal=True, key=f"st_{v}")

values = {}
if split_type != "Equal" and participants:
    st.caption({
        "Custom amount": f"Enter how much each person owes ({cur}).",
        "Percentage": "Enter each person's percentage (must total 100).",
        "Shares": "Enter shares, e.g. 2 for someone who had double.",
    }[split_type])
    cols = st.columns(min(len(participants), 3))
    default = {"Custom amount": 0.0, "Percentage": round(100 / len(participants), 2), "Shares": 1.0}[split_type]
    for i, p in enumerate(participants):
        with cols[i % len(cols)]:
            values[p] = st.number_input(names[p], min_value=0.0, value=default, step=1.0,
                                        key=f"val_{split_type}_{p}_{v}")
    total_in = sum(values.values())
    if split_type == "Custom amount":
        st.caption(f"Entered {total_in:,.2f} of {amount:,.2f}  ·  Remaining {amount - total_in:,.2f}")
    elif split_type == "Percentage":
        st.caption(f"Total: {total_in:.2f}%")

if st.button("Save expense", type="primary", use_container_width=True):
    if not title.strip():
        st.error("Please add a description.")
    elif amount <= 0:
        st.error("Amount must be greater than 0.")
    else:
        splits, err = compute_splits(amount, split_type, participants, values)
        if err:
            st.error(err)
        else:
            try:
                db.add_expense(trip["id"], title.strip(), round(amount, 2), category, paid_by, when, splits)
                st.session_state.form_v = v + 1
                st.session_state.flash = f"Saved “{title.strip()}” ✅"
                st.rerun()
            except Exception as ex:
                st.error(f"Could not save: {ex}")
