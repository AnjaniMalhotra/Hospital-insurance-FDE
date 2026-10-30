"""Nirmaya HMS: the hospital's billing system. A plain web app (pages + JSON API) on a SQLite database.
Run: python legacy_system/backend/app.py   ->  http://localhost:8061   (or start everything with the start_*.py script of your branch)

API (what the pages use):            GET  /api/patients        POST /api/patients
                                     GET  /api/claims          GET  /api/claims/<id>
                                     POST /api/claims/<id>/settlement   (staff type it in)
Export (what other systems may read): GET  /export/claims.csv   (read-only, like an HMS "Export to Excel")
                                      GET  /export/bill_items.csv   (each claim's itemised bill, sent with the claim)
"""
import csv
import io
import os
from datetime import date, datetime
from pathlib import Path

from flask import Flask, Response, jsonify, request

import db

# Which doctor sees which department. Example: 'Cardiology' -> 'Dr. R. Menon'.
DOCTORS = {"Cardiology": "Dr. R. Menon", "Orthopaedics": "Dr. S. Kulkarni", "General Surgery": "Dr. A. Deshpande",
           "General Medicine": "Dr. P. Joshi", "Ophthalmology": "Dr. N. Bhatt"}


# Turns a list of rows into a downloadable CSV file. Example: claim rows -> claims_export.csv.
def csv_file(rows, cols, name):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={name}"})


# Builds the HMS web app: all its pages and API links are defined inside this function.
def make_app(static_folder):
    """The HMS backend. The integrated HMS reuses it with its own pages (static_folder)."""
    app = Flask(__name__, static_folder=str(static_folder), static_url_path="")

    # Opens the HMS home page.
    @app.get("/")
    def home():
        return app.send_static_file("index.html")

    # Returns every patient (with their claim number, if they have one) as JSON.
    @app.get("/api/patients")
    def patients():
        return jsonify(db.rows("SELECT p.*, c.claim_id FROM patients p LEFT JOIN claims c USING (uhid) ORDER BY p.uhid"))

    # Registers a new patient; an insured patient also gets a claim with the itemised bill.
    @app.post("/api/patients")
    def add_patient():
        p = request.get_json(force=True)
        # A patient must have a name.
        if not (p.get("name") or "").strip():
            return jsonify(error="Patient name is required."), 400
        # Gives the patient the next free hospital ID. Example: NMH260130.
        uhid = db.next_id("patients", "uhid", "NMH", 260100)
        db.run("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", uhid, p["name"].strip(), p.get("age") or None,
               p.get("phone"), p.get("dept"), DOCTORS.get(p.get("dept")), p.get("diagnosis"), p.get("admitted"),
               p.get("discharged"), p.get("insurer"), p.get("policy"))
        # Self-pay patients get no claim; insured patients get one below.
        claim_id = None
        if p.get("insurer") and p["insurer"] != "Self-pay":  # insured patients get a cashless claim
            claim_id = db.next_id("claims", "claim_id", "HSP-", 1001)
            items = [i for i in p.get("bill") or [] if int(i.get("amount") or 0) > 0]
            db.run("INSERT INTO claims (claim_id, uhid, insurer, billed, submitted) VALUES (?, ?, ?, ?, ?)",
                   claim_id, uhid, p["insurer"], sum(int(i["amount"]) for i in items), date.today().isoformat())
            db.add_bill(claim_id, items)  # billed = the total of the itemised bill
        return jsonify(uhid=uhid, claim_id=claim_id)

    # Returns every claim with its patient and settlement details.
    @app.get("/api/claims")
    def claims():
        return jsonify(db.rows(db.CLAIMS + " ORDER BY c.claim_id"))

    # Returns one claim with its patient and bill. Example: /api/claims/HSP-1011.
    @app.get("/api/claims/<claim_id>")
    def claim(claim_id):
        found = db.rows(db.CLAIMS + " WHERE c.claim_id = ?", claim_id)
        if not found:
            return jsonify(error="Claim not found"), 404
        return jsonify(claim=found[0], patient=db.rows("SELECT * FROM patients WHERE uhid = ?", found[0]["uhid"])[0],
                       bill=db.rows("SELECT head, qty, rate, amount FROM bill_items WHERE claim_id = ?", claim_id))

    # Saves what the insurer paid, typed in by staff. Example: paid 233200, deduction 78400.
    @app.post("/api/claims/<claim_id>/settlement")
    def settle(claim_id):
        s = request.get_json(force=True)
        db.save_settlement(claim_id, s.get("paid"), s.get("deduction"), s.get("reason"), s.get("entered_by", "BILLING02"),
                           datetime.now().isoformat(timespec="minutes"))
        return jsonify(ok=True)

    # Read-only CSV of all claims, so other systems can read them (like 'Export to Excel').
    @app.get("/export/claims.csv")
    def export():
        cols = ["claim_id", "patient_name", "insurer", "admission_date", "amount_claimed", "status"]
        return csv_file(db.rows(db.CLAIMS + " ORDER BY c.claim_id"), cols, "claims_export.csv")

    # Read-only CSV with every claim's itemised bill lines.
    @app.get("/export/bill_items.csv")
    def export_bills():
        rows = db.rows("SELECT * FROM bill_items ORDER BY claim_id, rowid")
        return csv_file(rows, ["claim_id", "head", "qty", "rate", "amount"], "bill_items_export.csv")

    return app


# Starts the HMS on port 8061 when this file is run directly.
if __name__ == "__main__":
    make_app(Path(__file__).resolve().parents[1] / "frontend").run(port=int(os.getenv("PORT", "8061")))
