# CLAUDE.md: Insurance Short-Payment Finder (FDE training project 1) · branch `fde-solution`

## What this is
A beginner-friendly teaching project with a small but real architecture. Students act as Forward Deployed Engineers
for Nirmaya Multispeciality Hospital (fictional). Insurers pay less than billed and explain why in e-mails; staff
used to retype every settlement into HMS by hand. The FDE adds **ClaimTrail** as one new tab in HMS: it fetches insurer
e-mails (mailbox API) and claims (HMS export); AI reads each e-mail into pydantic objects; code matches and decides
fair/unfair; staff check and post. Architecture: `docs/ARCHITECTURE.md`.

**Branches:** `main` = the hospital before AI (`legacy_system/` + `mail_portal/` + `demo/`). `fde-solution` (this) =
`legacy_system/` renamed to `integration/` + the tab + `integration/claimtrail/`. Shared fixes (HMS base code, mail
portal, demo, docs, presentation) go on `main` first, then merge `main` into `fde-solution`.

## Rules for every change
1. **Change the hospital's HMS as little as possible.** `integration/` = `main`'s `legacy_system/` + the new tab; keep
   every other file identical to `main` so the branch diff shows only the feature. `mail_portal/` is never changed.
2. **ClaimTrail is read-only** on the hospital: it only reads `/export/claims.csv` and the mailbox API
   (`integration/claimtrail/connectors.py`). Writing back happens only in `integration/backend/reconcile.py`.
3. **Rules in code, AI only for the mess.** Money and fair/unfair decisions: `integration/claimtrail/rules.py`.
   AI (`integration/claimtrail/ai.py`, pydantic structured output): reading e-mails (incl. the reason's category), drafting appeals.
   No hand-written text rules / regex readers and no offline mode.
4. **Keep it simple for AI beginners.** No file over 120 lines; least code that works; pandas, flask, aiosmtpd,
   google-genai, openai only; front ends are plain HTML/CSS/JS with no build step.
5. **Keep demo-only code in `demo/`** (and seed/plumbing scripts) so teaching material stays clean.
6. Report in rupees; prove it on known answers: `python integration/claimtrail/evaluate.py`.
7. **Incremental:** ClaimTrail fetches only unprocessed e-mails (`integration/claimtrail/output/processed.json`), retries unreadable ones,
   skips claims not SUBMITTED, keeps earlier results; Post never overwrites a settled claim.

## Commands
```bash
python demo/seed.py            # reset: fresh hms.db (30 claims) + 21 e-mails + data/answer_key.csv + clears claimtrail/output
GEMINI_API_KEY=... python start_integration.py   # HMS with the tab :8062 + shared Mail :8025 (SMTP 2525) + Desk :8070
                                   # PORTS at the top; main's HMS is on 8061; Mail + Desk are reused if already running
python integration/claimtrail/pipeline.py   # CLI run (systems must be running) -> integration/claimtrail/output/results.csv
python integration/claimtrail/evaluate.py   # score vs data/answer_key.csv
```
`GEMINI_API_KEY` is required (`OPENAI_API_KEY` optional backup); without a key ClaimTrail refuses to run.
Default `GEMINI_MODEL=gemini-3.1-flash-lite`, `GEMINI_RPM=12` (free-tier pacing; 0 = off). Calls time out after 60 s.
Port 8000 is taken by another app on this machine. After changing Python code, restart `start_integration.py`.

## Layout
- `integration/` (Nirmaya HMS with the tab, :8061) = `main`'s `legacy_system/` plus: `backend/reconcile.py` (NEW Flask
  blueprint: `/api/reconcile`, `/api/reconcile/post`, `/letters/<f>`), 2 marked lines in `backend/app.py`,
  `frontend/reconcile.html` + `reconcile.js` (NEW), a menu link in `hms.js`, small additions in `claims.html`,
  `claim.html`, `style.css`. `backend/db.py` is identical to `main`.
- `integration/claimtrail/` (NEW, the AI components): `connectors.py` (HMS export + mailbox API, read-only), `llm.py`,
  `ai.py`, `rules.py`, `pipeline.py`, `evaluate.py`; `output/`: results.csv, processed.json, inbox/.
- `mail_portal/` (Nirmaya Mail, separate service :8025 + SMTP :2525): `backend/server.py`, `backend/store.py`,
  `frontend/mail.html`, `storage/maildir/`. Identical to `main`.
- `demo/`: `seed.py` (reset; this branch also writes `data/answer_key.csv`), `insurers/`, `insurer_desk/`: not taught.
- `data/answer_key.csv`: true result per sample claim, for `evaluate.py` only. Committed on this branch (added with
  `git add -f`, since `data/` is ignored); the seed rewrites it identically, so it never changes.
- Running example: **Anjali Sharma, HSP-1011, Arogya**, billed 3,11,600, paid 2,33,200, unfair cut 78,400.
- `start_integration.py` (this branch) / `start_legacy.py` (main): start the branch's three services.
- Docs: ONE student README at the root (identical on both branches: the project, not how it was built); everything
  else in `docs/` (ARCHITECTURE, TEACHING_PLAN, GLOSSARY, summary, this file) and `presentation/`. No other READMEs.
  Add new terms to `docs/GLOSSARY.md`.
