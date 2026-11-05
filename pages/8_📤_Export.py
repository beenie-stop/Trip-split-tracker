import streamlit as st
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.export import build_frames, to_excel

trip = setup_page("Export", "📤")
trip_hero(trip, "Export & end trip")

members = db.get_members(trip["id"])
expenses = db.get_expenses(trip["id"])
settlements = db.get_settlements(trip["id"])
exp_df, bal_df, set_df = build_frames(members, expenses, settlements)

st.markdown("#### Preview")
st.dataframe(exp_df, use_container_width=True, hide_index=True)

safe = trip["name"].replace(" ", "_")
a, b = st.columns(2)
a.download_button("⬇️ Download CSV (expenses)", exp_df.to_csv(index=False).encode("utf-8"),
                  file_name=f"{safe}_expenses.csv", mime="text/csv", use_container_width=True)
b.download_button("⬇️ Download Excel (all sheets)",
                  to_excel({"Expenses": exp_df, "Balances": bal_df, "Settlements": set_df}),
                  file_name=f"{safe}_summary.xlsx",
                  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                  use_container_width=True)

st.divider()
st.markdown("#### Trip status")
if trip["status"] == "completed":
    st.success("This trip is marked as completed.")
    if st.button("Reopen trip"):
        db.set_trip_status(trip["id"], "active")
        st.rerun()
else:
    st.caption("Once everyone is settled and you've exported, mark the trip as completed.")
    if st.button("✅ Mark trip as completed", type="primary"):
        db.set_trip_status(trip["id"], "completed")
        st.rerun()
