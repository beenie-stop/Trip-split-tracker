import streamlit as st
from components.styles import inject_css
from utils import db
from utils.auth import require_login, sign_out


def setup_page(title, icon, need_trip=True):
    """Call at the top of every page. Returns the current trip (dict) or None."""
    st.set_page_config(page_title=f"{title} · TripSplit", page_icon=icon, layout="wide")
    inject_css()
    require_login()

    trips = db.my_trips()
    with st.sidebar:
        st.markdown("## 🌴 TripSplit")
        st.caption(f"Signed in as **{st.session_state.user['name']}**")
        if trips:
            ids = [t["id"] for t in trips]
            cur = st.session_state.get("trip_id")
            idx = ids.index(cur) if cur in ids else 0
            sel = st.selectbox("Current trip", ids, index=idx,
                               format_func=lambda i: next(t["name"] for t in trips if t["id"] == i))
            st.session_state.trip_id = sel
        st.divider()
        if st.button("Logout", use_container_width=True):
            sign_out()
            st.switch_page("app.py")

    trip = next((t for t in trips if t["id"] == st.session_state.get("trip_id")), None)
    if need_trip and not trip:
        st.info("Create or join a trip first.")
        st.page_link("pages/1_🏠_My_Trips.py", label="Go to My Trips", icon="🏠")
        st.stop()
    return trip
