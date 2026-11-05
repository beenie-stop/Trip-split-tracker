import streamlit as st
from utils import db
from utils.auth import sync_cookie


def live_watch(trip_id, seconds=4):
    """Checks the database every few seconds; reloads the page only when something changed.
    Also keeps the 'stay logged in' cookie fresh."""

    @st.fragment(run_every=seconds)
    def _watch():
        sig = db.trip_signature(trip_id)
        sync_cookie()
        key = f"_sig_{trip_id}"
        old = st.session_state.get(key)
        st.session_state[key] = sig
        if old is not None and old != sig:
            st.rerun()

    _watch()