import streamlit as st
from supabase import create_client


def get_client():
    """One Supabase client per browser session (so each user keeps their own login)."""
    if "sb" not in st.session_state:
        st.session_state.sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return st.session_state.sb
