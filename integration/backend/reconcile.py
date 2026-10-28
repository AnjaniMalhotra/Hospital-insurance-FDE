"""NEW in the integrated HMS: the Claim Reconciliation tab's API. Everything else in this HMS is the original code.
It runs ClaimTrail (integration/claimtrail/: fetch new e-mails, AI reads them, rules decide), then writes the
results into the HMS database when staff press Post.

  POST /api/reconcile        fetch only NEW e-mails from the billing mailbox, read + match them (ClaimTrail pipeline)
  POST /api/reconcile/post   write the results into claims still SUBMITTED (status AUTO-RECONCILED);
                             claims already settled (by hand or earlier) are never overwritten
  GET  /letters/<file>       the original e-mail / PDF a result was read from
Incremental: claimtrail/output/processed.json remembers which e-mails are done; results.csv keeps every result.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Blueprint, jsonify, send_from_directory

import db  # the HMS database helpers (unchanged)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "claimtrail"))
os.environ.setdefault("HMS_URL", f"http://localhost:{os.getenv('PORT', '8061')}")  # ClaimTrail reads THIS HMS's export
import connectors  # noqa: E402  (ClaimTrail: read-only links to the HMS export and the mailbox API)
import pipeline  # noqa: E402  (ClaimTrail: AI reads, rules decide)

INBOX, PROCESSED, RESULTS = pipeline.OUT / "inbox", pipeline.OUT / "processed.json", pipeline.OUT / "results.csv"
RESULT = {"PAID_FULL": "Paid in full", "FAIR_CUT": "Fair cut", "UNFAIR_CUT": "Unfair cut"}
reconcile_api = Blueprint("reconcile", __name__)


def as_rows(df):
    """Results as a list of dicts (empty cells become null)."""
    return df.astype(object).where(df.notna(), None).to_dict("records")


@reconcile_api.post("/api/reconcile")
def reconcile():
    done = json.loads(PROCESSED.read_text()) if PROCESSED.exists() else {}   # e-mail id -> {file, at}
    previous = pd.read_csv(RESULTS) if RESULTS.exists() else None
    log = []
    try:
        emails = connectors.fetch_emails(INBOX, skip=done)                    # only e-mails not processed yet
        df, handled = pipeline.run(emails, log=log.append, previous=previous)
    except OSError as e:  # the mail server is not running
        return jsonify(error=f"Can't reach the billing mailbox ({e}). Start everything with: python start.py"), 503
    except Exception as e:  # e.g. no AI key: show a readable error instead of a crash page
        return jsonify(error=str(e) if isinstance(e, RuntimeError) else f"{type(e).__name__}: {e}"), 500
    already, now = len(done), datetime.now().isoformat(timespec="minutes")
    done.update({e["id"]: {"file": e["file"], "at": now} for e in emails if e["file"] in handled})
    PROCESSED.write_text(json.dumps(done, indent=1))
    return jsonify(log=log, letters=len(emails), already=already, filled=int(df.new.sum()),
                   pending=len(emails) - len(handled), rows=as_rows(df))


@reconcile_api.get("/letters/<path:name>")
def letter(name):
    return send_from_directory(INBOX, name)


@reconcile_api.post("/api/reconcile/post")
def post_results():
    if not RESULTS.exists():
        return jsonify(error="Nothing to post yet: import from the billing mailbox first."), 400
    now, posted, skipped = datetime.now().isoformat(timespec="minutes"), 0, 0
    current = {c["claim_id"]: c["status"] for c in db.rows("SELECT claim_id, status FROM claims")}
    for r in as_rows(pd.read_csv(RESULTS)):
        if not r.get("letter_file"):  # no letter read for this claim
            continue
        if current.get(r["claim_id"]) != "SUBMITTED":  # already settled: never overwrite
            skipped += 1
            continue
        db.save_settlement(r["claim_id"], r["paid"], r["cut"], r.get("reason") or "", "ClaimTrail", now,
                           RESULT.get(r["result"]), r["letter_file"], r.get("appeal_letter") or "")
        db.run("UPDATE claims SET status = 'AUTO-RECONCILED' WHERE claim_id = ?", r["claim_id"])  # filled by the tab
        posted += 1
    return jsonify(posted=posted, skipped=skipped)
