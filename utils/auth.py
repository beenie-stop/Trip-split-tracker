import re
from urllib.parse import quote, unquote
import streamlit as st
import streamlit.components.v1 as components
from utils.supabase_client import get_client

COOKIE = "tripsplit_rt"
COOKIE_DAYS = 365


def _user_dict(u):
    meta = u.user_metadata or {}
    return {"id": u.id, "email": u.email, "name": meta.get("name") or (u.email or "user").split("@")[0]}


# ---------- "stay logged in" cookie ----------
def _write_cookie(value, days):
    v = quote(value, safe="")
    components.html(
        f"""<script>
        const d = new Date(); d.setTime(d.getTime() + ({days}) * 86400000);
        window.parent.document.cookie = "{COOKIE}={v}; expires=" + d.toUTCString() + "; path=/; SameSite=Lax";
        </script>""",
        height=0,
    )


def clear_cookie():
    _write_cookie("", -1)


def sync_cookie(force=False):
    """Keep the browser cookie in step with the latest Supabase refresh token."""
    try:
        s = get_client().auth.get_session()
    except Exception:
        return
    if not s:
        return
    if force or st.session_state.get("_cookie_rt") != s.refresh_token:
        _write_cookie(s.refresh_token, COOKIE_DAYS)
        st.session_state["_cookie_rt"] = s.refresh_token


def try_restore():
    """If the browser has a saved login, sign the user back in silently."""
    if st.session_state.get("user"):
        return True
    if st.session_state.get("_no_restore"):
        return False
    rt = st.context.cookies.get(COOKIE)
    if not rt:
        return False
    try:
        res = get_client().auth.refresh_session(unquote(rt))
        st.session_state.user = _user_dict(res.user)
        return True
    except Exception:
        return False


# ---------- sign up / in / out ----------
def sign_up(name, username, email, password):
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
        raise ValueError("Username must be 3-20 characters: letters, numbers or underscore.")
    if not get_client().rpc("username_available", {"p_username": username}).execute().data:
        raise ValueError("That username is already taken.")
    res = get_client().auth.sign_up(
        {"email": email, "password": password, "options": {"data": {"name": name, "username": username}}}
    )
    if res.session:
        st.session_state.pop("_no_restore", None)
        st.session_state.user = _user_dict(res.user)
        return "ok"
    return "confirm"


def sign_in(identifier, password):
    identifier = identifier.strip()
    if "@" not in identifier:
        email = get_client().rpc("email_for_username", {"p_username": identifier.lower()}).execute().data
        if not email:
            raise ValueError("No account found with that username.")
    else:
        email = identifier
    res = get_client().auth.sign_in_with_password({"email": email, "password": password})
    st.session_state.pop("_no_restore", None)
    st.session_state.user = _user_dict(res.user)


def sign_out():
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    st.session_state.clear()
    st.session_state["_no_restore"] = True  # login page will clear the cookie


def require_login():
    if not st.session_state.get("user") and not try_restore():
        st.switch_page("app.py")
        st.stop()
    sync_cookie()