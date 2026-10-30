# Atomic account transfer

## Domain gap
Models often perform debit and credit as separate writes, allowing partial transfers when the destination update fails.

## Task
Implement transfer(conn, source_id, destination_id, amount). The SQLite connection has accounts(id TEXT PRIMARY KEY, balance INTEGER NOT NULL). Require amount to be a positive integer (bool invalid), distinct accounts, and both accounts to exist. Debit and credit must be atomic. Raise ValueError for invalid amount/same account, KeyError for missing account, and ValueError for insufficient funds. On any failure, balances must remain unchanged. Do not commit unrelated caller work; use a SAVEPOINT.

## Buggy starter code
```python
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
```

## Required response format
Return exactly one JSON object, with no Markdown fences:
{
  "diagnosis": "A concise explanation of the root cause and relevant edge cases.",
  "fixed_code": "The complete corrected Python module as a JSON string."
}

The fixed module must preserve the required public function/class names and signatures. Do not omit imports. Do not change the contract. Your code will be executed against tests, including edge cases. Explain why the fix addresses the bug, but prioritize executable correctness.
