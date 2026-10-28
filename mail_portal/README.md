# Mail Portal: Nirmaya Mail (the hospital's e-mail)

The hospital's e-mail system, a **separate service** from HMS (in real life: Microsoft 365, Google Workspace,
Zimbra). Insurers e-mail their settlements here. We **never change it**. (On `fde-solution`, ClaimTrail reads it through the mailbox API.)

| Service | Address |
|---|---|
| Webmail + mailbox API | http://localhost:8025 |
| SMTP (receives e-mail) | localhost:2525, only for `billing@nirmaya-hospital.example` |

## Folders
```
mail_portal/
├── backend/     server.py  SMTP server (aiosmtpd) + Flask webmail + mailbox API
│                store.py   saves and reads e-mails in the Maildir
├── frontend/    mail.html · mail.css   the webmail page staff use
└── storage/     maildir/   one file per e-mail, the standard mail-server format (filled by demo/seed.py)
```
Run on its own: `python mail_portal/backend/server.py` (or everything: `python start.py`).

## The mailbox API (how other systems fetch mail; real life: Gmail API, Microsoft Graph, IMAP)
| Endpoint | Returns |
|---|---|
| `GET /api/messages` | every e-mail: id, from, subject, date, unread, attachment names |
| `GET /api/messages/<id>` (`?peek=1` = don't mark as read) | one e-mail: plain body, HTML body, attachments |
| `GET /api/messages/<id>/attachments/<name>` | the PDF |
