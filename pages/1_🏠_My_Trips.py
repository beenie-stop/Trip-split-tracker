import streamlit as st
from components.sidebar import setup_page
from components.styles import hero, trip_card
from utils import db
from utils.constants import CURRENCIES

setup_page("My Trips", "🏠", need_trip=False)
hero("My Trips", "Create a new trip or join your friends with a code.", badge="🏠 Home")

t_create, t_join = st.tabs(["➕ Create trip", "🔑 Join with code"])

with t_create:
    with st.form("create_trip"):
        name = st.text_input("Trip name", placeholder="Goa 2026")
        cur = st.selectbox("Currency", CURRENCIES)
        cover_file = st.file_uploader("Cover photo (optional)", type=["jpg", "jpeg", "png", "webp"])
        cover_url = st.text_input("…or paste an image URL (optional)")
        if st.form_submit_button("Create trip", type="primary"):
            if not name.strip():
                st.error("Give your trip a name.")
            else:
                try:
                    url = cover_url.strip() or None
                    if cover_file:
                        url = db.upload_cover(cover_file)
                    st.session_state.trip_id = db.create_trip(name.strip(), cur, url)
                    st.success("Trip created! Add your friends in the Members page.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not create trip: {e}")

with t_join:
    with st.form("join_trip"):
        code = st.text_input("Trip code", placeholder="A1B2C3")
        if st.form_submit_button("Join trip", type="primary"):
            try:
                st.session_state.trip_id = db.join_trip(code)
                st.success("Joined!")
                st.rerun()
            except Exception as e:
                st.error("Invalid trip code." if "Invalid" in str(e) else f"Could not join: {e}")

st.subheader("Your trips")
trips = db.my_trips()
if not trips:
    st.info("No trips yet. Create one above!")
cols = st.columns(3)
for i, t in enumerate(trips):
    with cols[i % 3]:
        trip_card(t)
        if st.button("Open", key=f"open_{t['id']}", use_container_width=True):
            st.session_state.trip_id = t["id"]
            st.switch_page("pages/4_📋_Expenses.py")
