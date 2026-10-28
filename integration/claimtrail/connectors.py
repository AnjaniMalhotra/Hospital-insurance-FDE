"""How ClaimTrail connects to the hospital's systems. READ-ONLY: it never changes HMS or the mailbox
(writing results into HMS happens only in integration/backend/reconcile.py, when staff press Post).
  1. HMS export (CSV over HTTP)    -> what the hospital billed: one row per claim
  2. Mailbox API (JSON over HTTP)  -> the insurers' e-mails: body text and PDF attachments
In real life: (1) an HMS report export or a read-only database view; (2) the Gmail API, Microsoft Graph or IMAP.
"""
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

import pandas as pd
from pypdf import PdfReader

HMS_URL = os.getenv("HMS_URL", "http://localhost:8062")
MAIL_URL = os.getenv("MAIL_URL", "http://localhost:8026")


def fetch_claims():
    """All claims from the HMS export: claim_id, patient_name, insurer, admission_date, amount_claimed, status."""
    return pd.read_csv(f"{HMS_URL}/export/claims.csv")


def list_messages():
    """The e-mails in the billing mailbox (sender, subject, date, attachment names), newest first."""
    with urlopen(f"{MAIL_URL}/api/messages") as res:
        return json.load(res)["messages"]


def pdf_text(path):
    """The text inside a PDF (plain code, no AI: the AI then makes sense of it)."""
    return "\n".join(page.extract_text() for page in PdfReader(path).pages)


def get(url):
    with urlopen(url) as res:
        return res.read()


def fetch_emails(folder, skip=()):
    """Every e-mail NOT in `skip` (ids already processed), as {id, file, text}:
    text = what the AI reads (subject + body + the text of each PDF attachment);
    file = a copy saved in `folder` for people to open (the PDF, or the e-mail body as .html if there is no PDF).
    (Real-world equivalent: an IMAP search for new mail, or Gmail history.)"""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    emails = []
    for m in list_messages():
        if m["id"] in skip:
            continue
        api = f"{MAIL_URL}/api/messages/{quote(m['id'])}"
        msg = json.loads(get(api + "?peek=1"))         # peek: don't mark it as read for the billing staff
        text, file = f"From: {msg['from']}\nSubject: {msg['subject']}\nDate: {msg['date']}\n\n{msg['body']}", None
        for name in msg["attachments"]:
            if name.lower().endswith(".pdf"):
                (folder / name).write_bytes(get(f"{api}/attachments/{quote(name)}"))
                text += f"\n\n--- Attached PDF: {name} ---\n{pdf_text(folder / name)}"
                file = file or name
        if file is None:                                # the settlement is in the e-mail body itself
            file = f"email_{re.sub(r'[^A-Za-z0-9]', '', m['id'])[:20]}.html"
            (folder / file).write_text(msg["html"] or f"<pre>{html.escape(msg['body'])}</pre>")
        emails.append({"id": m["id"], "file": file, "text": text})
    return emails
