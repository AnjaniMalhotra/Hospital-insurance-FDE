"""DEMO TOOL (not part of what we teach). It plays the 6 insurance companies.
Log in as an insurer, review the itemised bill of each claim the hospital submitted to you, choose the outcome
(the deduction for the chosen reason is suggested from the bill and your policy terms), and the insurer e-mails
its settlement to the hospital's billing mailbox over real SMTP, in that insurer's own preset template
(PDF letter, table in the e-mail body, one e-mail for several patients, ...: see demo/insurers/insurers.py).
Run: python demo/insurer_desk/app.py   ->  http://localhost:8070   (or start everything with: python start.py)
"""
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
from flask import Flask, jsonify, request, session

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo" / "insurers"))
import insurers  # noqa: E402  (how each insurer writes and e-mails its settlements)
import policy  # noqa: E402  (each insurer's policy terms: room limit, co-pay, what each reason cuts)

HMS_URL = os.getenv("HMS_URL", "http://localhost:8061")
SMTP_HOST, SMTP_PORT = "127.0.0.1", int(os.getenv("SMTP_PORT", "2525"))
PASSWORD = "demo"                                   # every demo login uses this password
LOGINS = {t["login"]: name for name, t in insurers.INSURERS.items()}
IST = timezone(timedelta(hours=5, minutes=30))
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "demo-only-insurer-desk"


def submitted_claims():
    """The claims hospitals have sent us. (A real insurer receives these through its own claim portal.)"""
    return pd.read_csv(f"{HMS_URL}/export/claims.csv")


def bills():
    """Each claim's itemised bill (the hospital sends it with the claim): claim_id, head, qty, rate, amount."""
    return pd.read_csv(f"{HMS_URL}/export/bill_items.csv")


@app.get("/")
def home():
    return app.send_static_file("index.html")


@app.get("/api/logins")
def logins():  # shown on the login page so the presenter can pick a company
    return jsonify([{"login": t["login"], "insurer": n, "format": t["format"], "batch": t["batch"]}
                    for n, t in insurers.INSURERS.items()])


@app.post("/api/login")
def login():
    b = request.get_json(force=True)
    if b.get("login") not in LOGINS or b.get("password") != PASSWORD:
        return jsonify(error="Wrong username or password"), 401
    session["insurer"] = LOGINS[b["login"]]
    return jsonify(ok=True)


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/claims")
def claims():
    me = session.get("insurer")
    if not me:
        return jsonify(error="Please log in"), 401
    try:
        df, items = submitted_claims(), bills()
    except OSError:
        return jsonify(error=f"Can't reach the hospital's HMS at {HMS_URL}. Start everything with: python start.py"), 503
    mine = df[df.insurer == me].fillna("").iloc[::-1].to_dict("records")   # only OUR claims, newest first
    for c in mine:
        c["bill"] = items[items.claim_id == c["claim_id"]].drop(columns="claim_id").to_dict("records")
        c["suggest"] = {r: policy.deduction(r, c["bill"], me) for r in policy.FAIR + policy.UNFAIR}
    t = insurers.INSURERS[me]
    return jsonify(insurer=me, format=t["format"], batch=t["batch"], fair=policy.FAIR, unfair=policy.UNFAIR,
                   room_limit=policy.ROOM_LIMIT[me], co_pay=policy.CO_PAY, head=policy.HEAD, claims=mine)


@app.post("/api/send")
def send():
    """items = [{claim_id, paid, reason}] -> ONE e-mail in this insurer's template."""
    me, items = session.get("insurer"), request.get_json(force=True).get("items") or []
    if not me:
        return jsonify(error="Please log in"), 401
    if not 1 <= len(items) <= insurers.INSURERS[me]["batch"]:
        return jsonify(error=f"{me} sends 1 to {insurers.INSURERS[me]['batch']} claim(s) per e-mail"), 400
    df, now = submitted_claims().set_index("claim_id"), datetime.now(IST)
    group = []
    for it in items:
        if it.get("claim_id") not in df.index or df.at[it["claim_id"], "insurer"] != me:
            return jsonify(error=f"Unknown claim {it.get('claim_id')}"), 404
        c = df.loc[it["claim_id"]]
        billed = int(c.amount_claimed)
        paid = max(0, min(billed, int(float(it.get("paid") or billed))))
        group.append(SimpleNamespace(claim_id=it["claim_id"], patient_name=c.patient_name, insurer=me, paid=paid,
                                     admission_date=c.admission_date, amount_claimed=billed, paid_on=now.date().isoformat(),
                                     reason=(it.get("reason") or "") if paid < billed else ""))
    msg, files = insurers.settlement_email(group, now)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:  # real e-mail, to the hospital's mail server
            smtp.send_message(msg)
    except OSError as e:
        return jsonify(error=f"Can't reach the hospital's mail server ({e})"), 503
    return jsonify(subject=msg["Subject"], sender=msg["From"], to=msg["To"], claims=len(group),
                   attachments=[f for f, _ in files])


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "8070")))
