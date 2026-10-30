def transfer(conn, source_id, destination_id, amount):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        raise ValueError("invalid amount")
    if source_id == destination_id:
        raise ValueError("accounts must differ")
    conn.execute("SAVEPOINT transfer_sp")
    try:
        rows = conn.execute(
            "SELECT id, balance FROM accounts WHERE id IN (?, ?)",
            (source_id, destination_id)
        ).fetchall()
        balances = {row[0]: row[1] for row in rows}
        if source_id not in balances or destination_id not in balances:
            raise KeyError("account not found")
        if balances[source_id] < amount:
            raise ValueError("insufficient funds")
        conn.execute("UPDATE accounts SET balance=balance-? WHERE id=?", (amount, source_id))
        conn.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (amount, destination_id))
        conn.execute("RELEASE SAVEPOINT transfer_sp")
    except Exception:
        conn.execute("ROLLBACK TO SAVEPOINT transfer_sp")
        conn.execute("RELEASE SAVEPOINT transfer_sp")
        raise
