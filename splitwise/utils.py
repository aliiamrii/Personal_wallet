def calculate_balances(expenses, members):
    total_paid = {member.id: 0 for member in members}

    for exp in expenses:
        total_paid[exp.paid_by.id] += float(exp.amount)

    total_expense = sum(total_paid.values())
    per_person = total_expense / len(members)

    balances = {member.id: round(total_paid[member.id] - per_person, 2) for member in members}
    debtors = [{'user_id': uid, 'amount': -amount} for uid, amount in balances.items() if amount < 0]
    creditors = [{'user_id': uid, 'amount': amount} for uid, amount in balances.items() if amount > 0]

    transactions = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, creditor = debtors[i], creditors[j]
        amount = min(debtor['amount'], creditor['amount'])

        transactions.append({
            'from': debtor['user_id'],
            'to': creditor['user_id'],
            'amount': round(amount, 2)
        })

        debtor['amount'] -= amount
        creditor['amount'] -= amount

        if debtor['amount'] == 0:
            i += 1
        if creditor['amount'] == 0:
            j += 1

    return round(per_person, 2), transactions