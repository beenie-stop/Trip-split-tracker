import streamlit as st
from datetime import date
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.calculations import money
from utils.constants import CATEGORIES
from utils.realtime import live_watch

trip = setup_page("Expenses", "📋")
trip_hero(trip, "All expenses")
live_watch(trip["id"])
cur = trip["currency"]

members = db.get_members(trip["id"])
names = {m["id"]: m["name"] for m in members}
ids = list(names)
expenses = db.get_expenses(trip["id"])

if not expenses:
    st.info("No expenses yet. Add one from the **Add Expense** page.")
    st.stop()

f1, f2, f3 = st.columns(3)
q = f1.text_input("Search", placeholder="dinner…")
cats = f2.multiselect("Category", CATEGORIES)
payers = f3.multiselect("Paid by", ids, format_func=names.get)

shown = [x for x in expenses
         if (not q or q.lower() in x["title"].lower())
         and (not cats or x["category"] in cats)
         and (not payers or x["paid_by"] in payers)]

m1, m2 = st.columns(2)
m1.metric("Total spent", money(cur, sum(float(x["amount"]) for x in shown)))
m2.metric("Expenses", len(shown))

for x in shown:
    label = f"{x['expense_date']}  ·  {x['title']}  —  {money(cur, float(x['amount']))}"
    with st.expander(label):
        st.markdown(f"Paid by **{names[x['paid_by']]}** · {x['category']}")
        for s in x["expense_splits"]:
            st.write(f"• {names[s['member_id']]}: {money(cur, float(s['share_amount']))}")

        with st.form(f"edit_{x['id']}"):
            st.caption("Edit details (to change amount or split, delete and re-add the expense)")
            a, b = st.columns(2)
            t = a.text_input("Description", x["title"])
            cat = b.selectbox("Category", CATEGORIES,
                              index=CATEGORIES.index(x["category"]) if x["category"] in CATEGORIES else len(CATEGORIES) - 1)
            c, d = st.columns(2)
            dt = c.date_input("Date", date.fromisoformat(x["expense_date"]))
            pb = d.selectbox("Paid by", ids, index=ids.index(x["paid_by"]), format_func=names.get)
            if st.form_submit_button("Save changes"):
                db.update_expense(x["id"], t.strip() or x["title"], cat, pb, dt)
                st.rerun()
        if st.button("🗑️ Delete expense", key=f"del_{x['id']}"):
            db.delete_expense(x["id"])
            st.rerun()
