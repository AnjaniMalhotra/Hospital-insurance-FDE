# Project Summary: Insurance Short-Payment Finder

*FDE Training Project 1 · Nirmaya Multispeciality Hospital (fictional) · ClaimTrail*

## Branches
| Branch | Shows | Folders |
|---|---|---|
| `main` | The hospital today: everything by hand, no AI | `legacy_system/` · `mail_portal/` · `demo/` |
| `fde-solution` | After the FDE: the same HMS + one new tab, AI reads the e-mails | `integration/` · `mail_portal/` · `demo/` |

`git diff main fde-solution --stat` shows the whole FDE change: one tab plus the AI components.

## The problem
**Reconciling insurance settlements is slow, manual and error-prone.**

Every insurer sends its settlement (what it paid, and why it paid less) by e-mail: **6 insurers, 6 formats**
(PDF letters, text in the e-mail body, tables, one e-mail covering several patients), often without a claim number
and with misspelt names. The billing system (**HMS**) only knows what was *billed*, so a clerk retypes every
settlement into HMS by hand and decides from memory whether each cut was fair.

- **Slow:** about 3 days of typing every month.
- **Error-prone:** wrong patient matches, mistyped amounts, inconsistent fair/unfair calls.
- **Incomplete:** only ~40 of 300 claims ever get checked, so wrong cuts go unnoticed.

**Example:** Anjali Sharma (HSP-1011, Arogya). Billed ₹3,11,600, paid ₹2,33,200, ₹78,400 cut for
"Investigation charges disallowed". The letter has no claim number and spells her "aanjali sharma". Her policy
covers tests, so the cut is **unfair**, but only if someone finds, matches and checks it.

## The solution: ClaimTrail inside the HMS
A new **Claim Reconciliation** tab in a copy of the hospital's HMS (same look, same database). Staff click
**Import**, check the results, and click **Post**. Behind the tab, ClaimTrail:

1. **Fetches** only the new insurer e-mails (mailbox API) and the claims (HMS export), read-only.
2. **Reads** each e-mail with AI (Gemini) into a fixed pydantic shape: one row per patient.
3. **Matches** each row to its claim: by claim number, or the same billed amount + a similar name.
4. **Decides** in plain code: cut = billed − paid; room / non-payable items / co-pay = fair, anything else = unfair.
5. **Posts** the results into HMS on request: Paid column filled, status AUTO-RECONCILED.

**Core principle: AI reads, code decides.** AI never decides money.

## Results (sample month: 30 claims, 21 e-mails, 6 insurers)
| Measure | Result |
|---|---|
| Claims correct | **30 / 30** (every insurer 5 / 5) |
| Unfair cuts caught | **5 / 5: ₹1,99,800** flagged for review |
| Time | about 2 minutes for the month, instead of ~3 days of typing |
| False alarms | **0** |
| Total cut found | ₹2,57,000 |

Checked with `python integration/claimtrail/evaluate.py` against a planted answer key.

## The systems
| System | URL | Folder | Role |
|---|---|---|---|
| Nirmaya HMS (original) | http://localhost:8061 | `legacy_system/` | The client's billing system, unchanged |
| Nirmaya Mail | http://localhost:8025 (SMTP :2525) | `mail_portal/` | The hospital's e-mail server + webmail |
| **Integrated HMS** | http://localhost:8062 | `integration/` | Same HMS + Claim Reconciliation tab (runs ClaimTrail) |
| Insurer Desk | http://localhost:8070 | `demo/insurer_desk/` | Demo only: plays the 6 insurers |

## Folder structure
```
legacy_system/        the hospital's HMS, as we found it (service :8061)
  backend/            app.py (Flask pages, API, CSV exports) · db.py (SQLite: patients, claims, bill_items, settlements)
  frontend/           old-style pages: index, login, patients, claims, claim, hms.js, style.css
  database/           hms.db
mail_portal/          the hospital's e-mail, a separate service (:8025, SMTP :2525)
  backend/            server.py (SMTP + webmail + mailbox API) · store.py (Maildir)
  frontend/           mail.html · mail.css
  storage/            maildir/ (one file per e-mail)
integration/          what the FDE builds: mirrors the base project, so a diff shows only the new feature
  backend/ frontend/  a full copy of the HMS (same layout as legacy_system/) + the new tab:
  database/           backend/reconcile.py, frontend/reconcile.html + .js (new), 2 lines in app.py, menu link;
                      database/hms.db links to the hospital's database
  claimtrail/         connectors.py (read-only fetch) · llm.py (Gemini → OpenAI) · ai.py (pydantic schemas,
                      prompt) · rules.py (match + decide) · pipeline.py (wires it) · evaluate.py (scores it)
                      output/ (results.csv · processed.json · inbox/)
demo/                 demo only, not taught
  insurer_desk/       insurer logins, itemised bill review, sends e-mails by real SMTP
  insurers/           insurers.py (6 insurers, templates) · documents.py + statements.py (PDFs) · policy.py
  seed.py             resets all demo data (30 claims, 21 e-mails, answer key)
data/                 answer_key.csv (testing only) · letters/
docs/                 ARCHITECTURE · TEACHING_PLAN · DEMO_PLAN · DISCOVERY_NOTE · GLOSSARY
presentation/         12-slide HTML deck (open presentation/index.html)
start.py              starts all 4 systems
```

## How the pipeline connects
```
HMS (:8061/:8062) ── claims + itemised bills ──► Insurer Desk (:8070) ── e-mail, SMTP ──► Nirmaya Mail (:8025)
                                                                                              │
Integrated HMS (:8062) ─ Import ─► ClaimTrail:  FETCH (connectors) ◄── mailbox API ───────────┘
                                                READ  (ai + llm, pydantic)
                                                MATCH + DECIDE (rules)
                                                SAVE  (pipeline → results.csv)
                       ─ Post ───► hms.db: Paid filled, AUTO-RECONCILED (settled claims never overwritten)
```

## Tech stack
| Layer | Tools |
|---|---|
| Language | Python 3.14 |
| Web servers | Flask |
| Database | SQLite |
| E-mail | aiosmtpd (SMTP server), smtplib (sending), Maildir |
| Data | pandas |
| PDFs | fpdf2 (create), pypdf (read text) |
| AI | Gemini `gemini-3.1-flash-lite` via google-genai, OpenAI as backup |
| Structured output | pydantic |
| Front ends | plain HTML, CSS, JavaScript (no build step) |

## Design rules
- **Never change the client's systems.** All new work lives in `integration/`.
- **Read-only by default.** HMS is written only when staff press Post, and never over a settled claim.
- **AI only for the messy part** (reading e-mails). Money and fair/unfair decisions are plain, readable rules.
- **Incremental.** Only new e-mails are read; failed ones are retried next time.
- **Prove it in rupees** against known answers.
- **Simple for beginners.** No file over 120 lines, no frameworks beyond the list above.

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python demo/seed.py                  # reset the demo data
GEMINI_API_KEY=... python start.py            # start all 4 systems
```
Open http://localhost:8062 → **Claim Reconciliation** → **Import from billing mailbox** (about 2 minutes on a free
Gemini key) → **Post to Claims Register**. Then score it: `python integration/claimtrail/evaluate.py`.

Free-tier notes: calls are paced to 12 a minute (`GEMINI_RPM`, set 0 on a paid key); change model with `GEMINI_MODEL`.

## Further reading
[README.md](README.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/DEMO_PLAN.md](docs/DEMO_PLAN.md) ·
[docs/TEACHING_PLAN.md](docs/TEACHING_PLAN.md) · [docs/GLOSSARY.md](docs/GLOSSARY.md) · [integration/README.md](integration/README.md)
