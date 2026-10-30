"""Nirmaya Mail: the hospital's e-mail server and webmail. A separate system from HMS.
  SMTP  localhost:2525  receives e-mail (insurers send settlement letters here) and stores it (store.py, Maildir)
  HTTP  localhost:8025  the webmail pages + a mailbox API that other systems use to fetch mail
                        (in real life: the Gmail API, Microsoft Graph, or IMAP)
Run: python mail_portal/backend/server.py   (or start everything with the start_*.py script of your branch)
"""
import os
from pathlib import Path

from aiosmtpd.controller import Controller
from flask import Flask, Response, jsonify, request

import store

# The only mailbox this mail server hosts.
MAILBOX = "billing@nirmaya-hospital.example"   # the only mailbox this server hosts


# Decides what the SMTP server does with incoming e-mail.
class Inbox:
    """SMTP handler: accept mail for the billing mailbox, store it, refuse everything else."""

    # Accepts an e-mail only if it is addressed to the billing mailbox; anything else is refused.
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if address.lower() != MAILBOX:
            return "550 No such mailbox here"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    # Saves an accepted e-mail into the mailbox.
    async def handle_DATA(self, server, session, envelope):
        store.deliver(envelope.content)
        print(f"[mail] new e-mail from {envelope.mail_from}")
        return "250 Message accepted for delivery"


# The webmail website and the mailbox API.
app = Flask(__name__, static_folder=str(Path(__file__).resolve().parents[1] / "frontend"), static_url_path="")


# Opens the webmail inbox page.
@app.get("/")
def webmail():
    return app.send_static_file("mail.html")


# Lists all e-mails (sender, subject, date, attachment names).
@app.get("/api/messages")
def messages():
    return jsonify(mailbox=MAILBOX, messages=store.list_messages())


# Returns one e-mail with its body; opening it marks it as read, unless ?peek=1.
@app.get("/api/messages/<key>")
def message(key):  # ?peek=1: read it without marking it as read (how other systems fetch mail)
    return jsonify(store.get(key, mark_read=not request.args.get("peek")))


# Returns one PDF attachment of an e-mail.
@app.get("/api/messages/<key>/attachments/<name>")
def attachment(key, name):
    data = store.attachment(key, name)
    if data is None:
        return jsonify(error="No such attachment"), 404
    return Response(data, mimetype="application/pdf", headers={"Content-Disposition": f"inline; filename={name}"})


# Starts the SMTP server (port 2525) and the web server (port 8025).
if __name__ == "__main__":
    smtp = Controller(Inbox(), hostname="127.0.0.1", port=int(os.getenv("SMTP_PORT", "2525")))
    smtp.start()
    print(f"[mail] SMTP listening on 127.0.0.1:{smtp.port} for {MAILBOX}")
    app.run(port=int(os.getenv("PORT", "8025")))
