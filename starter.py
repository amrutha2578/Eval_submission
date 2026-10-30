def transfer(conn, source_id, destination_id, amount):
    # BUG: writes are not protected as one atomic unit and bool passes as int.
    if not isinstance(amount, int) or amount <= 0:
        raise ValueError("invalid amount")
    source = conn.execute("SELECT balance FROM accounts WHERE id=?", (source_id,)).fetchone()
    destination = conn.execute("SELECT balance FROM accounts WHERE id=?", (destination_id,)).fetchone()
    if source is None or destination is None:
        raise KeyError("account not found")
    if source[0] < amount:
        raise ValueError("insufficient funds")
    conn.execute("UPDATE accounts SET balance=balance-? WHERE id=?", (amount, source_id))
    conn.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (amount, destination_id))
