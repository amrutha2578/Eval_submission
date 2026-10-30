import candidate
import sqlite3
import pytest

def setup_db():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE accounts(id TEXT PRIMARY KEY, balance INTEGER NOT NULL)")
    c.executemany("INSERT INTO accounts VALUES (?, ?)", [("a", 100), ("b", 20)])
    c.commit()
    return c

def balances(c):
    return dict(c.execute("SELECT id,balance FROM accounts").fetchall())

def test_successful_transfer():
    c = setup_db()
    candidate.transfer(c, "a", "b", 30)
    assert balances(c) == {"a": 70, "b": 50}

@pytest.mark.parametrize("amount", [0, -1, True, 1.5, "10"])
def test_invalid_amount_no_change(amount):
    c = setup_db()
    with pytest.raises(ValueError):
        candidate.transfer(c, "a", "b", amount)
    assert balances(c) == {"a": 100, "b": 20}

def test_insufficient_funds_no_change():
    c = setup_db()
    with pytest.raises(ValueError):
        candidate.transfer(c, "a", "b", 101)
    assert balances(c) == {"a": 100, "b": 20}

def test_missing_account_no_change():
    c = setup_db()
    with pytest.raises(KeyError):
        candidate.transfer(c, "a", "missing", 10)
    assert balances(c) == {"a": 100, "b": 20}

def test_same_account_rejected():
    c = setup_db()
    with pytest.raises(ValueError):
        candidate.transfer(c, "a", "a", 10)
    assert balances(c) == {"a": 100, "b": 20}

def test_does_not_commit_callers_transaction():
    c = setup_db()
    c.execute("UPDATE accounts SET balance=90 WHERE id='a'")
    candidate.transfer(c, "a", "b", 10)
    c.rollback()
    assert balances(c) == {"a": 100, "b": 20}
