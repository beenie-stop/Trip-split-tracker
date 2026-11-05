import streamlit as st
from components.sidebar import setup_page
from components.styles import trip_hero
from utils import db
from utils.realtime import live_watch

trip = setup_page("Members", "👥")
trip_hero(trip, "Members & trip settings")
live_watch(trip["id"])

members = db.get_members(trip["id"])

c1, c2 = st.columns([2, 1])
with c2:
    st.markdown("##### Share this code")
    st.code(trip["code"], language=None)
    st.caption("Friends with an account can join from **My Trips → Join with code**.")

with c1:
    st.markdown("##### Add a friend")
    with st.form("add_member", clear_on_submit=True):
        a, b = st.columns(2)
        name = a.text_input("Name")
        upi = b.text_input("UPI ID (optional)", placeholder="name@bank")
        if st.form_submit_button("Add member", type="primary"):
            if name.strip():
                db.add_member(trip["id"], name.strip(), upi.strip())
                st.rerun()
            else:
                st.error("Enter a name.")

st.markdown("##### Everyone on this trip")
for m in members:
    with st.container(border=True):
        a, b, c, d = st.columns([2, 2, 1, 1])
        new_name = a.text_input("Name", m["name"], key=f"n_{m['id']}", label_visibility="collapsed")
        new_upi = b.text_input("UPI", m.get("upi_id") or "", key=f"u_{m['id']}",
                               placeholder="UPI ID (optional)", label_visibility="collapsed")
        if c.button("Save", key=f"s_{m['id']}", use_container_width=True):
            db.update_member(m["id"], new_name.strip() or m["name"], new_upi.strip())
            st.rerun()
        if d.button("Remove", key=f"r_{m['id']}", use_container_width=True):
            try:
                db.delete_member(m["id"])
                st.rerun()
            except Exception:
                st.error("Can't remove someone who has expenses or settlements.")
        st.caption("✅ Has an account" if m.get("user_id") else "👤 Added manually")

st.divider()
st.markdown("##### Trip cover photo")
cover = st.file_uploader("Upload a new cover", type=["jpg", "jpeg", "png", "webp"], key="cover_up")
url = st.text_input("…or paste an image URL")
if st.button("Update cover photo"):
    try:
        new = db.upload_cover(cover) if cover else (url.strip() or None)
        db.set_cover(trip["id"], new)
        st.rerun()
    except Exception as e:
        st.error(f"Could not update: {e}")
