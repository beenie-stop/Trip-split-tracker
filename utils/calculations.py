def money(cur, x):
    return f"{cur}{x:,.2f}"


def compute_balances(members, expenses, settlements):
    """balance > 0: gets money back, balance < 0: owes money."""
    bal = {m["id"]: 0.0 for m in members}
    for e in expenses:
        bal[e["paid_by"]] += float(e["amount"])
        for s in e["expense_splits"]:
            bal[s["member_id"]] -= float(s["share_amount"])
    for s in settlements:
        if s.get("status", "paid") == "paid":
            bal[s["from_member"]] += float(s["amount"])
            bal[s["to_member"]] -= float(s["amount"])
    return {k: round(v, 2) for k, v in bal.items()}


def suggest_payments(bal):
    """Greedy: biggest debtor pays biggest creditor. Returns [(from, to, amount)]."""
    creditors = sorted([[m, a] for m, a in bal.items() if a > 0.009], key=lambda x: -x[1])
    debtors = sorted([[m, -a] for m, a in bal.items() if a < -0.009], key=lambda x: -x[1])
    out, i, j = [], 0, 0
    while i < len(debtors) and j < len(creditors):
        pay = round(min(debtors[i][1], creditors[j][1]), 2)
        if pay > 0:
            out.append((debtors[i][0], creditors[j][0], pay))
        debtors[i][1] = round(debtors[i][1] - pay, 2)
        creditors[j][1] = round(creditors[j][1] - pay, 2)
        if debtors[i][1] <= 0.01:
            i += 1
        if creditors[j][1] <= 0.01:
            j += 1
    return out
