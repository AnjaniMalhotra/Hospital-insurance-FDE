# Architecture: how the systems really connect

Three small systems, each its own process, talking over real protocols, just like at a real hospital.
Start them with `python start_legacy.py` on `main` or `python start_integration.py` on `fde-solution` (reset the data
first with `python demo/seed.py`). Two git branches:
**`main`** = the hospital today (HMS is `legacy_system/`); **`fde-solution`** = after the FDE (HMS is `integration/`:
the same HMS + one new tab + ClaimTrail). The two HMS versions have their own ports (main: 8061, fde-solution: 8062)
and share one Mail (8025, SMTP 2525) and one Insurer Desk (8070), so both can run side by side (see README).

```
   OUTSIDE THE HOSPITAL                    THE HOSPITAL
 ┌──────────────────────┐   SMTP :2525   ┌───────────────────────────────┐
 │ Insurers             │ ─────────────► │ Nirmaya Mail      :8025       │◄── mailbox API (HTTP/JSON) ──┐
 │ (demo: Insurer Desk  │    e-mails     │ mail_portal/  SMTP → Maildir  │                               │
 │  :8070)              │                │ webmail pages for staff       │                               │
 └──────────▲───────────┘                └───────────────────────────────┘                               │
            │ claims + itemised bills    ┌──────────────────────────────────────────────────────────┐    │
            └─────────────────────────── │ Nirmaya HMS       :8061      web pages + JSON API + hms.db │    │
                                         │  main:          legacy_system/   everything by hand       │    │
                                         │  fde-solution:  integration/  =  the same HMS             │    │
                                         │                   + "Claim Reconciliation" tab            │    │
                                         │                   + claimtrail/ (AI reads, rules decide) ─┼────┘
                                         └──────────────────────────────────────────────────────────┘
```

## The systems
| System | Folder | What it is | Talks to |
|---|---|---|---|
| **Nirmaya HMS** (`main`) | `legacy_system/` | The hospital's billing system: pages + JSON API on a **SQLite database** (`hms.db`: patients, claims, bill_items, settlements) | nobody (it's old) |
| **Nirmaya Mail** | `mail_portal/` | The hospital's e-mail: an **SMTP server** storing each e-mail in a **Maildir**, webmail pages, and a **mailbox API** | receives mail from insurers |
| **Integrated HMS** (`fde-solution`) | `integration/` | The same HMS code + one new tab: Claim Reconciliation (`backend/reconcile.py`), same port :8061 | its own database |
| **ClaimTrail** (inside it) | `integration/claimtrail/` | Fetches claims + e-mails, AI reads, rules match and decide, AI drafts appeals | HMS export, mailbox API (**read-only**) |
| **Insurer Desk** | `demo/insurer_desk/` | **Demo only.** Plays the insurers | HMS export, SMTP |

## The data flow, step by step (Anjali's claim)
1. **HMS:** staff register Anjali → a row in `patients` and a claim `HSP-1011` in `claims` (status SUBMITTED).
2. **Insurer → Mail:** Arogya e-mails a settlement letter (PDF attached) to `billing@nirmaya-hospital.example` over
   **SMTP**. The mail server stores the full e-mail as one file in its Maildir.
3. **Today (manual):** a clerk opens webmail, reads the PDF, types paid / deduction / reason into HMS.
4. **ClaimTrail, step 1 (connectors.py), run by the Integrated HMS's server:**
   `GET :8061/export/claims.csv` → what was billed · `GET :8025/api/messages`, `.../<id>?peek=1` (body) +
   `.../attachments/<pdf>` → each new e-mail as text.
5. **ClaimTrail, steps 2–5 (pipeline.py):** AI reads each e-mail into pydantic `Settlement` rows, one per patient
   (`ai.py`) → find the claim, work out the cut, fair or
   unfair (rules, `rules.py`) → draft appeals (AI) → `integration/claimtrail/output/results.csv`.
6. **The tab:** staff click *Import from billing mailbox* (the HMS server runs steps 4–5), check the results in the
   old HMS style, and on *Post* the server writes them into `hms.db` → the claim becomes AUTO-RECONCILED.

## Incremental, like a real integration
- ClaimTrail keeps a log of e-mails it has finished (`integration/claimtrail/output/processed.json`) and only fetches the others
  (real world: an IMAP search for unseen mail, or the Gmail API's history id).
- An e-mail it can't finish (AI call failed, or a patient not found in HMS) stays unprocessed and is **retried next run**.
- A claim already settled in HMS (typed by a clerk, or posted earlier) is **skipped**, never overwritten.
- Results build up across runs (`integration/claimtrail/output/results.csv`); each run marks its own rows as *new*.
- *Post* writes only claims still SUBMITTED. ClaimTrail never marks e-mails as read: staff still see them.

## How each piece maps to the real world
| In this project | In a real hospital |
|---|---|
| SQLite `hms.db` | The HMS vendor's database (Oracle, SQL Server, MySQL…) |
| `/export/claims.csv` | The HMS "Export to Excel" report, or a read-only database view |
| Our SMTP server on :2525 | The hospital's mail server (Microsoft 365, Google Workspace, Zimbra) |
| Maildir folder | The mail server's message store |
| Mailbox API `/api/messages` | Gmail API, Microsoft Graph, or IMAP |
| `connectors.py` | The integration layer: credentials, retries, read-only access |
| Integrated HMS module | A vendor plug-in, or a small app on the hospital's intranet that writes back via the HMS API / import |
| Insurer Desk | Real insurers' claim systems (we can't run those, so the demo fakes them) |

## Why it is built this way (the FDE rules)
- **Read-only by default:** ClaimTrail only *reads* the HMS export and the mailbox. Writing back happens only when
  staff press *Post*, through the HMS's own server (`integration/backend/reconcile.py`), and never over a settled claim.
- **Rules in code, AI for the mess:** only `ai.py` talks to an AI model; every money decision is in `rules.py`.
- **Separate systems, clear contracts:** each system can be swapped (a real mail server, a real HMS) by changing
  one URL in `connectors.py` (`HMS_URL`, `MAIL_URL`).

## What to teach, and what not
| Teach | Folder |
|---|---|
| The client's world and its manual work | `legacy_system/` (HMS) + `mail_portal/` (Mail) |
| ClaimTrail: connectors, AI reading, rules, evaluation | `integration/claimtrail/` |
| The Claim Reconciliation tab inside HMS | `integration/` |
| **Don't teach** (plumbing for the demo) | `demo/` (Insurer Desk), `start_*.py`, `demo/seed.py`, `demo/insurers/` |
