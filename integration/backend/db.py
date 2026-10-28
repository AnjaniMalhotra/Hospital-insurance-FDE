"""Nirmaya HMS database (SQLite file hms.db): patients, insurance claims with their itemised bills, and settlements
typed in by staff.
One database, used by the original HMS and (later) the integrated HMS, just like one hospital database.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "database" / "hms.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
  uhid TEXT PRIMARY KEY, name TEXT NOT NULL, age INTEGER, phone TEXT, dept TEXT, doctor TEXT,
  diagnosis TEXT, admitted TEXT, discharged TEXT, insurer TEXT, policy TEXT);
CREATE TABLE IF NOT EXISTS claims (
  claim_id TEXT PRIMARY KEY, uhid TEXT NOT NULL REFERENCES patients(uhid), insurer TEXT NOT NULL,
  billed INTEGER NOT NULL, submitted TEXT, status TEXT NOT NULL DEFAULT 'SUBMITTED');
CREATE TABLE IF NOT EXISTS bill_items (
  claim_id TEXT NOT NULL REFERENCES claims(claim_id), head TEXT NOT NULL, qty INTEGER, rate INTEGER, amount INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS settlements (
  claim_id TEXT PRIMARY KEY REFERENCES claims(claim_id), paid INTEGER, deduction INTEGER, reason TEXT,
  entered_by TEXT, entered_at TEXT, result TEXT, letter TEXT, appeal TEXT);
"""

# The standard heads of a hospital bill (the claim's itemised bill uses these)
HEADS = ["Room rent", "Doctor & surgeon fees", "Investigations (lab, imaging)", "Medicines & pharmacy",
         "Consumables (gloves, masks, syringes)", "Implants", "OT & procedure charges"]

# One row per claim, with its patient and (if any) its settlement
CLAIMS = """SELECT c.claim_id, c.uhid, p.name AS patient_name, c.insurer, p.admitted AS admission_date,
  c.billed AS amount_claimed, c.status, c.submitted, s.paid, s.deduction, s.reason, s.entered_by, s.entered_at,
  s.result, s.letter, s.appeal
  FROM claims c JOIN patients p USING (uhid) LEFT JOIN settlements s USING (claim_id)"""


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def rows(sql, *args):
    with connect() as con:
        return [dict(r) for r in con.execute(sql, args)]


def run(sql, *args):
    with connect() as con:
        con.execute(sql, args)


def next_id(table, column, prefix, start):
    """Next free id, e.g. HSP-1031 or NMH260130."""
    n = rows(f"SELECT COUNT(*) AS n FROM {table}")[0]["n"]
    return f"{prefix}{start + n}"


def save_settlement(claim_id, paid, deduction, reason, entered_by, at, result=None, letter=None, appeal=None):
    """Insert or replace the settlement of one claim, and update the claim's status."""
    run("INSERT OR REPLACE INTO settlements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        claim_id, paid, deduction, reason, entered_by, at, result, letter, appeal)
    run("UPDATE claims SET status = 'SETTLEMENT ENTERED' WHERE claim_id = ?", claim_id)


def add_bill(claim_id, items):
    """Save a claim's itemised bill: items = [{head, qty, rate, amount}]. Returns the total."""
    for i in items:
        run("INSERT INTO bill_items VALUES (?, ?, ?, ?, ?)", claim_id, i["head"], i.get("qty") or 1,
            i.get("rate") or i["amount"], int(i["amount"]))
    return sum(int(i["amount"]) for i in items)
