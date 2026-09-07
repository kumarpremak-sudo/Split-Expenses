"""
Greedy debt minimization algorithm.

Calculates the minimum number of transactions needed to settle
all debts within a group, using exact cent arithmetic (Splitwise pattern).
Eliminates floating point precision errors and guarantees zero residual drift.
"""
import json


def calculate_settlements(members, expenses):
    """
    Calculate net balances and minimize settlement transactions.

    Args:
        members: list of Member model instances
        expenses: list of Expense model instances

    Returns:
        dict with:
            - 'balances': per-member breakdown (paid, owed, net)
            - 'settlements': list of {from_id, from_name, to_id, to_name, amount}
            - 'total_spent': total group expenditure
            - 'max_abs_net': maximum absolute net balance (for UI bar scaling)
    """
    valid_member_ids = {m.id for m in members}
    member_map = {m.id: m.name for m in members}

    # Track paid and owed in integer cents to eliminate floating-point drift
    paid_cents = {m.id: 0 for m in members}
    owed_cents = {m.id: 0 for m in members}

    total_spent_cents = 0

    for expense in expenses:
        # Validate payer belongs to current group
        payer_id = expense.paid_by_id
        if payer_id not in valid_member_ids:
            continue

        exp_cents = int(round(expense.amount * 100))
        if exp_cents <= 0:
            continue

        # Parse split_ids safely
        try:
            split_ids = json.loads(expense.split_among) if expense.split_among else []
        except (json.JSONDecodeError, TypeError):
            split_ids = []

        # Keep only active group members
        valid_split_ids = [mid for mid in split_ids if mid in valid_member_ids]

        # Default split to all group members if empty or invalid
        if not valid_split_ids:
            valid_split_ids = list(valid_member_ids)

        if not valid_split_ids:
            continue

        total_spent_cents += exp_cents
        paid_cents[payer_id] += exp_cents

        # Exact integer split with cent-remainder allocation
        num_split = len(valid_split_ids)
        base_share = exp_cents // num_split
        remainder = exp_cents % num_split

        for idx, mid in enumerate(valid_split_ids):
            # Distribute remainder 1-cent to first 'remainder' members
            extra = 1 if idx < remainder else 0
            owed_cents[mid] += (base_share + extra)

    member_balances = []
    max_abs_net_cents = 0

    for m in members:
        p_cents = paid_cents[m.id]
        o_cents = owed_cents[m.id]
        net_c = p_cents - o_cents
        abs_net = abs(net_c)
        if abs_net > max_abs_net_cents:
            max_abs_net_cents = abs_net

        member_balances.append({
            'id': m.id,
            'name': member_map[m.id],
            'paid': round(p_cents / 100.0, 2),
            'owed': round(o_cents / 100.0, 2),
            'net': round(net_c / 100.0, 2),
            'net_cents': net_c,
        })

    settlements = _minimize_transactions_cents(member_balances)

    # Clean up internal integer fields
    for b in member_balances:
        b.pop('net_cents', None)

    return {
        'balances': member_balances,
        'settlements': settlements,
        'total_spent': round(total_spent_cents / 100.0, 2),
        'max_abs_net': round(max_abs_net_cents / 100.0, 2),
    }


def _minimize_transactions_cents(member_balances):
    """
    Greedy algorithm operating on exact integer cents.

    Guarantees:
    - Sum of creditor cents ALWAYS equals sum of debtor cents.
    - Zero residual cents or float rounding drift.
    - Produces at most N-1 transactions for N members.
    """
    creditors = []
    debtors = []

    for member in member_balances:
        net_c = member['net_cents']
        if net_c > 0:
            creditors.append({'id': member['id'], 'name': member['name'], 'cents': net_c})
        elif net_c < 0:
            debtors.append({'id': member['id'], 'name': member['name'], 'cents': abs(net_c)})

    # Sort descending by amount for optimal greedy matching
    creditors.sort(key=lambda x: x['cents'], reverse=True)
    debtors.sort(key=lambda x: x['cents'], reverse=True)

    settlements = []

    while creditors and debtors:
        creditor = creditors[0]
        debtor = debtors[0]

        transfer_cents = min(creditor['cents'], debtor['cents'])

        if transfer_cents > 0:
            settlements.append({
                'from_id': debtor['id'],
                'from_name': debtor['name'],
                'to_id': creditor['id'],
                'to_name': creditor['name'],
                'amount': round(transfer_cents / 100.0, 2),
            })

        creditor['cents'] -= transfer_cents
        debtor['cents'] -= transfer_cents

        if creditor['cents'] == 0:
            creditors.pop(0)
        if debtor['cents'] == 0:
            debtors.pop(0)

    return settlements
