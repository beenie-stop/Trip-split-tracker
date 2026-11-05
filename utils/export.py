import io
import pandas as pd
from utils.calculations import compute_balances


def build_frames(members, expenses, settlements):
    names = {m["id"]: m["name"] for m in members}
    exp_rows = []
    for e in expenses:
        split = ", ".join(f"{names[s['member_id']]}: {float(s['share_amount']):.2f}" for s in e["expense_splits"])
        exp_rows.append({"Date": e["expense_date"], "Description": e["title"], "Category": e["category"],
                         "Paid By": names[e["paid_by"]], "Amount": float(e["amount"]), "Split": split})
    bal = compute_balances(members, expenses, settlements)
    bal_rows = [{"Member": names[k], "Net Balance": v} for k, v in bal.items()]
    set_rows = [{"Date": s["created_at"][:10], "From": names[s["from_member"]], "To": names[s["to_member"]],
                 "Amount": float(s["amount"]), "Method": s["method"], "Note": s.get("note") or ""}
                for s in settlements]
    return pd.DataFrame(exp_rows), pd.DataFrame(bal_rows), pd.DataFrame(set_rows)


def to_excel(frames: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    return buf.getvalue()
