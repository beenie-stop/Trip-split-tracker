import uuid
import streamlit as st
from datetime import datetime, timezone
from utils.supabase_client import get_client


def sb():
    return get_client()


def uid():
    return st.session_state.user["id"]


# ---------- trips ----------
def my_trips():
    rows = sb().table("members").select("trip_id, trips(*)").eq("user_id", uid()).execute().data
    trips = [r["trips"] for r in rows if r.get("trips")]
    return sorted(trips, key=lambda t: t["created_at"], reverse=True)


def create_trip(name, currency, cover_url):
    return sb().rpc("create_trip", {"p_name": name, "p_currency": currency, "p_cover": cover_url}).execute().data


def join_trip(code):
    return sb().rpc("join_trip", {"p_code": code}).execute().data


def upload_cover(file):
    ext = file.name.rsplit(".", 1)[-1].lower()
    path = f"{uid()}/{uuid.uuid4().hex}.{ext}"
    sb().storage.from_("trip-covers").upload(path, file.getvalue(), {"content-type": file.type})
    return sb().storage.from_("trip-covers").get_public_url(path)


def set_cover(trip_id, url):
    sb().table("trips").update({"cover_url": url}).eq("id", trip_id).execute()


def set_trip_status(trip_id, status):
    sb().table("trips").update({"status": status}).eq("id", trip_id).execute()


# ---------- members ----------
def get_members(trip_id):
    return sb().table("members").select("*").eq("trip_id", trip_id).order("created_at").execute().data


def add_member(trip_id, name, upi_id=None):
    sb().table("members").insert({"trip_id": trip_id, "name": name, "upi_id": upi_id or None}).execute()


def update_member(member_id, name, upi_id):
    sb().table("members").update({"name": name, "upi_id": upi_id or None}).eq("id", member_id).execute()


def delete_member(member_id):
    sb().table("members").delete().eq("id", member_id).execute()


# ---------- expenses ----------
def add_expense(trip_id, title, amount, category, paid_by, date, splits):
    e = sb().table("expenses").insert({
        "trip_id": trip_id, "title": title, "amount": amount, "category": category,
        "paid_by": paid_by, "expense_date": str(date),
    }).execute().data[0]
    rows = [{"trip_id": trip_id, "expense_id": e["id"], "member_id": m, "share_amount": a}
            for m, a in splits.items() if a > 0]
    sb().table("expense_splits").insert(rows).execute()


def get_expenses(trip_id):
    return (sb().table("expenses").select("*, expense_splits(*)").eq("trip_id", trip_id)
            .order("expense_date", desc=True).order("created_at", desc=True).execute().data)


def update_expense(expense_id, title, category, paid_by, date):
    sb().table("expenses").update({
        "title": title, "category": category, "paid_by": paid_by, "expense_date": str(date),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", expense_id).execute()


def delete_expense(expense_id):
    sb().table("expenses").delete().eq("id", expense_id).execute()


# ---------- settlements ----------
def get_settlements(trip_id):
    return sb().table("settlements").select("*").eq("trip_id", trip_id).order("created_at", desc=True).execute().data


def add_settlement(trip_id, from_member, to_member, amount, method, note=None):
    sb().table("settlements").insert({
        "trip_id": trip_id, "from_member": from_member, "to_member": to_member,
        "amount": amount, "method": method, "note": note or None, "status": "paid",
    }).execute()


def delete_settlement(settlement_id):
    sb().table("settlements").delete().eq("id", settlement_id).execute()


# ---------- realtime signature ----------
def trip_signature(trip_id):
    c = sb()
    parts = [
        c.table("expenses").select("id,updated_at").eq("trip_id", trip_id).execute().data,
        c.table("settlements").select("id,status").eq("trip_id", trip_id).execute().data,
        c.table("members").select("id,name,upi_id").eq("trip_id", trip_id).execute().data,
        c.table("trips").select("status,cover_url").eq("id", trip_id).execute().data,
    ]
    return str(parts)
