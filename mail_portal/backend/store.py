"""Nirmaya Mail's message store: a Maildir folder, the standard on-disk format real mail servers use.
Every e-mail is one file holding the full message: headers, body text and the PDF attachment.
"""
import mailbox
from email import message_from_bytes, policy
from email.utils import parsedate_to_datetime
from pathlib import Path

MAILDIR = Path(__file__).resolve().parents[1] / "storage" / "maildir"


def _box():
    MAILDIR.parent.mkdir(exist_ok=True)  # storage/ is not in git: create it on first use
    return mailbox.Maildir(MAILDIR, create=True)


def _parse(box, key):
    return message_from_bytes(box.get_bytes(key), policy=policy.default)


def deliver(raw):
    """Store one raw e-mail (bytes). Called by the SMTP server for every message it accepts."""
    return _box().add(mailbox.MaildirMessage(raw))


def list_messages():
    """Newest first: id, from, subject, date, unread, attachment names."""
    box, out = _box(), []
    for key in box.keys():
        msg = _parse(box, key)
        out.append({"id": key, "from": str(msg["From"]), "subject": str(msg["Subject"]),
                    "date": parsedate_to_datetime(msg["Date"]).strftime("%Y-%m-%d %H:%M"),
                    "unread": "S" not in box.get_message(key).get_flags(),
                    "attachments": [p.get_filename() for p in msg.iter_attachments()]})
    return sorted(out, key=lambda m: m["date"], reverse=True)


def get(key, mark_read=True):
    """One message with its body (plain text, and HTML if the sender wrote one). Opening it marks it as read (Seen), like any mail client."""
    box = _box()
    msg = _parse(box, key)
    if mark_read:
        flagged = box.get_message(key)
        flagged.set_subdir("cur")
        flagged.add_flag("S")
        box[key] = flagged
    body, html = msg.get_body(preferencelist=("plain",)), msg.get_body(preferencelist=("html",))
    return {"id": key, "from": str(msg["From"]), "to": str(msg["To"]), "subject": str(msg["Subject"]),
            "date": parsedate_to_datetime(msg["Date"]).strftime("%Y-%m-%d %H:%M"),
            "body": body.get_content() if body else "", "html": html.get_content() if html else None, "attachments": [p.get_filename() for p in msg.iter_attachments()]}


def attachment(key, name):
    """The bytes of one attachment (e.g. the PDF letter), or None."""
    for part in _parse(_box(), key).iter_attachments():
        if part.get_filename() == name:
            return part.get_content()
    return None


def clear():
    box = _box()
    for key in list(box.keys()):
        box.remove(key)
