# CLAUDE.md: Insurance Short-Payment Finder (FDE training project 1) · branch `main`

## What this is
A beginner-friendly teaching project with a small but real architecture. Students act as Forward Deployed Engineers
for Nirmaya Multispeciality Hospital (fictional). Insurers pay less than billed and explain why in e-mails to the
hospital; staff retype every settlement into HMS by hand.

**Branches:** `main` (this) = the hospital before AI: `legacy_system/` (HMS) + `mail_portal/` + `demo/`.
`fde-solution` = the same project with `legacy_system/` upgraded into `integration/` (one new tab + the AI components).
Keep the two branches' shared code identical: make fixes to the HMS, mail portal or demo here, then merge `main`
into `fde-solution`.

## Rules for every change
1. `legacy_system/` and `mail_portal/` are the hospital as we found it. No AI or FDE code on this branch.
2. **Keep it simple for AI beginners.** No file over 120 lines; least code that works; pandas, flask, aiosmtpd, fpdf2;
   front ends are plain HTML/CSS/JS with no build step.
3. **Keep demo-only code in `demo/`** (insurer desk, insurer templates, seed) so teaching material stays clean.

## Commands
```bash
python demo/seed.py   # reset: fresh hms.db (30 claims + itemised bills) + 21 e-mails from 6 insurers
python start_legacy.py   # runs this branch's systems: Mail :8025 (SMTP :2525), HMS :8061, Insurer Desk :8070 (demo)
```
Port 8000 is taken by another app on this machine. After changing Python code, restart `start_legacy.py`.

## Layout
- `legacy_system/` (Nirmaya HMS, :8061): `backend/app.py` (`make_app()`: pages + `/api/patients`, `/api/claims`, settlement,
  `/export/claims.csv`, `/export/bill_items.csv`), `backend/db.py` (SQLite schema incl. `bill_items`), `frontend/` (plain old
  pages: index, login, patients, claims, claim, `hms.js`), `database/hms.db`.
- `mail_portal/` (Nirmaya Mail, separate service :8025 + SMTP :2525): `backend/server.py` (aiosmtpd SMTP + Flask webmail +
  `/api/messages`), `backend/store.py` (Maildir), `frontend/mail.html`, `storage/maildir/`.
- `demo/`: `seed.py` (reset), `insurers/` (`insurers.py` 6 insurers + desk logins + e-mail templates, `documents.py` +
  `statements.py` PDF styles, `policy.py` room limits / co-pay / what each reason cuts), `insurer_desk/`: not taught.
- Running example: **Anjali Sharma, HSP-1011, Arogya**, billed 3,11,600, paid 2,33,200, unfair cut 78,400.
- `start_legacy.py` (this branch) / `start_integration.py` (fde-solution): start the branch's three services.
- Docs: ONE student README at the root (identical on both branches: the project, not how it was built); everything
  else in `docs/` (ARCHITECTURE, TEACHING_PLAN, GLOSSARY, summary, this file) and `presentation/`. No other READMEs.
  Add new terms to `docs/GLOSSARY.md`.
