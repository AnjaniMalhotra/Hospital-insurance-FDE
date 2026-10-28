# Insurance Short-Payment Finder · branch `main`: the hospital today (before AI)
*FDE Training Project 1: a beginner-friendly project with a real (small) architecture behind it.*

This branch is **the client as the FDE finds it**: Nirmaya hospital's billing system, its e-mail, and the insurers
sending settlements. Everything is done by hand. No AI, no FDE code.

| Branch | Shows | Folders |
|---|---|---|
| **`main`** (this one) | How the hospital works today, by hand | `legacy_system/` · `mail_portal/` · `demo/` |
| `fde-solution` | The same hospital after the FDE's work: one new tab, AI reads the e-mails | `integration/` · `mail_portal/` · `demo/` |

Compare them: `git diff main fde-solution --stat` (the HMS gets one new tab plus the AI components).

## What is a Forward Deployed Engineer (FDE)?
An engineer who **goes to the client, finds the real problem, and builds the smallest working fix inside the
client's existing setup, without replacing it.**

## The problem, in simple words
**Reconciling insurance settlements is slow, manual and error-prone.**

Nirmaya hospital bills insurance companies for every insured patient. Each insurer replies with a settlement:
how much it paid, and why it paid less (if it did). Those settlements arrive by e-mail from **6 insurers, each in
its own format**: PDF letters, a letter typed in the e-mail body, tables, one e-mail covering 3-4 patients, often
with no claim number and a misspelt name.

The billing system (HMS) only knows what was *billed*. So a clerk opens every e-mail, finds the patient, works out
the deduction and **retypes it into HMS by hand**, then decides from memory whether the cut was fair.
- **Slow:** about 3 days of typing every month.
- **Error-prone:** misspelt names lead to wrong matches, amounts get mistyped, fair/unfair is a judgement call.
- **Incomplete:** only ~40 of 300 claims ever get checked, so wrong cuts slip through unnoticed.

> **Example: Anjali Sharma.** Billed ₹3,11,600 · paid ₹2,33,200 · cut ₹78,400 · reason *"Investigation charges
> disallowed"*. Her letter has no claim number and spells her *"aanjali sharma"*. Her policy covers tests, so the
> cut is **unfair**, but only if someone finds, matches and checks it.

## The systems (each a separate service)
| System | URL | Folder |
|---|---|---|
| Nirmaya HMS: billing portal (SQLite database) | http://localhost:8061 | `legacy_system/` |
| Nirmaya Mail: e-mail server + webmail | http://localhost:8025 (SMTP :2525) | `mail_portal/` |
| Insurer Desk: plays the 6 insurers (demo tool) | http://localhost:8070 | `demo/` |

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python demo/seed.py     # fresh HMS database (30 claims with itemised bills) + 21 e-mails from 6 insurers
python start.py         # starts the three systems; Ctrl+C stops them
```
Then do one claim by hand: Nirmaya Mail → open an Arogya e-mail and its PDF → find the patient in HMS (misspelt,
no claim number) → open the claim → type paid, *calculate* the deduction, type the reason, decide if it's fair.

## The six insurers
| Insurer | How it e-mails settlements |
|---|---|
| Suraksha Health | PDF letter with a details box, one claim per e-mail |
| Arogya Plus TPA | PDF typed letter, no claim number, name misspelt (Anjali) |
| Jeevan Raksha | Letter typed in the e-mail body, no attachment, initial + surname |
| Kavach General | PDF remittance note, one table row per patient, several claims per e-mail |
| Swasthya Bharat TPA | HTML table in the e-mail body, several claims per e-mail |
| Sanjeevani General | PDF statement with a small table for each patient, several claims per e-mail |

## Folders
```
legacy_system/   Nirmaya HMS (:8061): backend/ (app.py, db.py) · frontend/ (pages) · database/ (hms.db)
mail_portal/     Nirmaya Mail, a separate service (:8025, SMTP :2525): backend/ · frontend/ · storage/maildir/
demo/            DEMO ONLY: insurer_desk/ · insurers/ (the 6 insurers' templates, PDFs, policy) · seed.py (reset)
docs/            ARCHITECTURE · TEACHING_PLAN · DEMO_PLAN · DISCOVERY_NOTE · GLOSSARY (course material, both branches)
presentation/    HTML slide deck (open presentation/index.html)
start.py         starts every system
```
Read next: [legacy_system/README.md](legacy_system/README.md) · [mail_portal/README.md](mail_portal/README.md) ·
[demo/README.md](demo/README.md) · [summary.md](summary.md)
