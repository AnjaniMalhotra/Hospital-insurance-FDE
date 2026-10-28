"""DEMO TOOL (not part of what we teach). It plays the 6 insurers for BOTH hospital systems (pick one on the desk).
Log in, review a claim's itemised bill, choose the outcome (deduction suggested from your policy), and the settlement
is e-mailed over real SMTP in that insurer's own template (see demo/insurers/insurers.py).
Run: python demo/insurer_desk/app.py   ->  http://localhost:8070   (or start everything with the start_*.py script of your branch)
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

HOSPITALS = dict(h.split("=") for h in os.getenv(   # the hospital systems this desk settles claims for
    "HOSPITALS", "Nirmaya HMS :8061 (before)=http://localhost:8061,Nirmaya HMS :8062 (after)=http://localhost:8062").split(","))
SMTP_HOST, SMTP_PORT = "127.0.0.1", int(os.getenv("SMTP_PORT", "2525"))   # the shared hospital mail server
MAIL_WEB = os.getenv("MAIL_WEB", "http://localhost:8025")
LOGINS, PASSWORD = {t["login"]: name for name, t in insurers.INSURERS.items()}, "demo"   # every login: password demo
IST = timezone(timedelta(hours=5, minutes=30))
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "demo-only-insurer-desk"


def picked():  # the hospital system chosen on the desk (a real insurer receives claims through its own portal)
    return session.get("hospital") if session.get("hospital") in HOSPITALS else next(iter(HOSPITALS))


def export(name):  # claims.csv (the claims sent to us) or bill_items.csv (their itemised bills) from that HMS
    return pd.read_csv(f"{HOSPITALS[picked()]}/export/{name}")


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


@app.post("/api/hospital")
def hospital():  # switch which hospital system's claims the desk shows
    session["hospital"] = request.get_json(force=True).get("name")
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
        df, items = export("claims.csv"), export("bill_items.csv")
    except OSError:
        return jsonify(error=f"Can't reach {picked()}: start it, or pick the other hospital above.",
                       hospitals=list(HOSPITALS), hospital=picked()), 503
    mine = df[df.insurer == me].fillna("").iloc[::-1].to_dict("records")   # only OUR claims, newest first
    for c in mine:
        c["bill"] = items[items.claim_id == c["claim_id"]].drop(columns="claim_id").to_dict("records")
        c["suggest"] = {r: policy.deduction(r, c["bill"], me) for r in policy.FAIR + policy.UNFAIR}
    t = insurers.INSURERS[me]
    return jsonify(insurer=me, format=t["format"], batch=t["batch"], fair=policy.FAIR, unfair=policy.UNFAIR,
                   hospitals=list(HOSPITALS), hospital=picked(), room_limit=policy.ROOM_LIMIT[me], co_pay=policy.CO_PAY,
                   head=policy.HEAD, claims=mine)


@app.post("/api/send")
def send():  # items = [{claim_id, paid, reason}] -> ONE e-mail in this insurer's template
    me, items = session.get("insurer"), request.get_json(force=True).get("items") or []
    if not me:
        return jsonify(error="Please log in"), 401
    if not 1 <= len(items) <= insurers.INSURERS[me]["batch"]:
        return jsonify(error=f"{me} sends 1 to {insurers.INSURERS[me]['batch']} claim(s) per e-mail"), 400
    df, now = export("claims.csv").set_index("claim_id"), datetime.now(IST)
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
    return jsonify(subject=msg["Subject"], sender=msg["From"], to=msg["To"], claims=len(group), mail=MAIL_WEB,
                   attachments=[f for f, _ in files])


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "8070")))
