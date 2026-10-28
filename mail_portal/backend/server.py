"""Nirmaya Mail: the hospital's e-mail server and webmail. A separate system from HMS.
  SMTP  localhost:2525  receives e-mail (insurers send settlement letters here) and stores it (store.py, Maildir)
  HTTP  localhost:8025  the webmail pages + a mailbox API that other systems use to fetch mail
                        (in real life: the Gmail API, Microsoft Graph, or IMAP)
Run: python mail_portal/backend/server.py   (or start everything with: python start.py)
"""
import os
from pathlib import Path

from aiosmtpd.controller import Controller
from flask import Flask, Response, jsonify, request

import store

MAILBOX = "billing@nirmaya-hospital.example"   # the only mailbox this server hosts


class Inbox:
    """SMTP handler: accept mail for the billing mailbox, store it, refuse everything else."""

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if address.lower() != MAILBOX:
            return "550 No such mailbox here"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        store.deliver(envelope.content)
        print(f"[mail] new e-mail from {envelope.mail_from}")
        return "250 Message accepted for delivery"


app = Flask(__name__, static_folder=str(Path(__file__).resolve().parents[1] / "frontend"), static_url_path="")


@app.get("/")
def webmail():
    return app.send_static_file("mail.html")


@app.get("/api/messages")
def messages():
    return jsonify(mailbox=MAILBOX, messages=store.list_messages())


@app.get("/api/messages/<key>")
def message(key):  # ?peek=1: read it without marking it as read (how other systems fetch mail)
    return jsonify(store.get(key, mark_read=not request.args.get("peek")))


@app.get("/api/messages/<key>/attachments/<name>")
def attachment(key, name):
    data = store.attachment(key, name)
    if data is None:
        return jsonify(error="No such attachment"), 404
    return Response(data, mimetype="application/pdf", headers={"Content-Disposition": f"inline; filename={name}"})


if __name__ == "__main__":
    smtp = Controller(Inbox(), hostname="127.0.0.1", port=int(os.getenv("SMTP_PORT", "2525")))
    smtp.start()
    print(f"[mail] SMTP listening on 127.0.0.1:{smtp.port} for {MAILBOX}")
    app.run(port=int(os.getenv("PORT", "8025")))
