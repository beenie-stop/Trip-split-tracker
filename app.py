import streamlit as st
from components.styles import inject_css, hero
from utils.auth import sign_in, sign_up, try_restore, clear_cookie

st.set_page_config(page_title="TripSplit", page_icon="🌴", layout="centered")
inject_css()

if try_restore():
    st.switch_page("pages/1_🏠_My_Trips.py")

if st.session_state.get("_no_restore"):
    clear_cookie()  # user just logged out: forget this browser

hero("TripSplit", "Split trip expenses with friends — simple, fair and stress-free.", badge="🌴 Welcome")

tab_in, tab_up = st.tabs(["Login", "Sign up"])

with tab_in:
    with st.form("login"):
        ident = st.text_input("Username or email")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login", type="primary", use_container_width=True):
            try:
                sign_in(ident, pw)
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

with tab_up:
    with st.form("signup"):
        name = st.text_input("Your name")
        uname = st.text_input("Username", help="3-20 characters: letters, numbers, underscore")
        email2 = st.text_input("Email", key="su_email")
        pw2 = st.text_input("Password (min 6 characters)", type="password", key="su_pw")
        if st.form_submit_button("Create account", type="primary", use_container_width=True):
            if not name.strip() or not uname.strip() or not email2.strip() or len(pw2) < 6:
                st.error("Please fill all fields (password min 6 characters).")
            else:
                try:
                    if sign_up(name.strip(), uname, email2.strip(), pw2) == "ok":
                        st.rerun()
                    else:
                        st.success("Account created! Check your email to confirm, then log in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")