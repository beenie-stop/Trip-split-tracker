def compute_splits(total, split_type, participants, values=None):
    """Returns (dict member_id -> amount, error_message)."""
    total = round(float(total), 2)
    values = values or {}
    if not participants:
        return None, "Select at least one person to split between."

    if split_type == "Custom amount":
        amounts = {p: round(float(values.get(p, 0)), 2) for p in participants}
        if abs(sum(amounts.values()) - total) > 0.01:
            return None, f"Custom amounts add up to {sum(amounts.values()):.2f}, but the total is {total:.2f}."
        return amounts, None

    if split_type == "Equal":
        weights = {p: 1.0 for p in participants}
    elif split_type == "Percentage":
        weights = {p: float(values.get(p, 0)) for p in participants}
        if abs(sum(weights.values()) - 100) > 0.01:
            return None, f"Percentages add up to {sum(weights.values()):.2f}%, they must total 100%."
    else:  # Shares
        weights = {p: float(values.get(p, 0)) for p in participants}
        if sum(weights.values()) <= 0:
            return None, "Total shares must be greater than 0."

    wsum = sum(weights.values())
    amounts = {p: round(total * w / wsum, 2) for p, w in weights.items()}
    diff = round(total - sum(amounts.values()), 2)  # fix rounding pennies
    if diff:
        biggest = max(amounts, key=amounts.get)
        amounts[biggest] = round(amounts[biggest] + diff, 2)
    return amounts, None
