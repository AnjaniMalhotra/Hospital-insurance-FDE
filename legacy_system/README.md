# Legacy System: Nirmaya HMS (the hospital's billing portal)

The hospital's billing system as the FDE finds it. It runs as its own service on **http://localhost:8061**.
On this branch everything in it is done by hand. On the `fde-solution` branch it becomes `integration/`: the same HMS
+ one new tab. The hospital's e-mail is a separate service: see [`../mail_portal/`](../mail_portal/README.md).

> Nirmaya Multispeciality Hospital, its insurers and all data are fictional, made for training.

## Folders
```
legacy_system/
├── backend/     app.py   Flask: the pages + JSON API + read-only exports
│                db.py    SQLite schema and helpers: patients, claims, bill_items, settlements
├── frontend/    index.html · login.html · patients.html · claims.html · claim.html · hms.js · style.css
└── database/    hms.db   the database file (created by demo/seed.py)
```
Run on its own: `python legacy_system/backend/app.py` (or everything: `python start.py`).

## The pages
| Page | What staff do there | What's wrong with it |
|---|---|---|
| `index.html` · `login.html` | Hospital website, staff login, link to webmail | Nothing (the front door) |
| `patients.html` | Search patients, **register a new patient** with an itemised bill; insured patients get a claim | Fine for its job |
| `claims.html` | All claims sent to insurers | The **Paid** column stays empty until someone types it in |
| `claim.html` | See the itemised bill; type in amount paid, deduction and reason | No maths (*"calculate yourself"*), no fair/unfair check |

## The API
| Endpoint | Used by |
|---|---|
| `GET/POST /api/patients` · `GET /api/claims` · `GET /api/claims/<id>` · `POST /api/claims/<id>/settlement` | the pages |
| `GET /export/claims.csv` · `GET /export/bill_items.csv` (read-only, like "Export to Excel") | Insurer Desk (and ClaimTrail on `fde-solution`) |

## One claim by hand (the pain)
Open webmail → open an Arogya e-mail ("Settlement advice", no patient named) → open the PDF → read "aanjali sharma",
no claim number → find her in HMS → open her claim → type ₹2,33,200 → work out ₹78,400 → type the reason →
decide alone whether it's fair. Then repeat for every e-mail.
