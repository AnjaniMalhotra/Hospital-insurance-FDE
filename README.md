# Insurance Short-Payment Finder · branch `fde-solution`: the hospital after the FDE (with AI)
*FDE Training Project 1: a beginner-friendly, working solution with a real (small) architecture behind it.*

This branch is **the same hospital after the FDE's work**: the HMS (`integration/`) is the original code plus one
new tab, **Claim Reconciliation**, and the AI components behind it (`integration/claimtrail/`). Mail and the
insurers are unchanged.

| Branch | Shows | Folders |
|---|---|---|
| `main` | How the hospital works today, by hand | `legacy_system/` · `mail_portal/` · `demo/` |
| **`fde-solution`** (this one) | The same hospital: one new tab, AI reads the e-mails | `integration/` · `mail_portal/` · `demo/` |

See the whole FDE change: `git diff main fde-solution --stat` (git shows `legacy_system/` → `integration/` as a rename,
so only the new tab and the AI files stand out).

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

## The FDE solution: ClaimTrail
ClaimTrail **fetches** the new e-mails from the billing mailbox and the claims from the HMS export (read-only),
**reads** each e-mail into structured rows (AI + pydantic), **finds the claim**, works out the **cut**, decides **fair or unfair** (plain rules)
and drafts the **appeal letters** (AI). It runs as a new **Claim Reconciliation** tab inside the hospital's
HMS (`integration/`); the idea and the POC story are presented in the slides (`presentation/`).

| Job | Done by | Why |
|---|---|---|
| Read an e-mail, whatever its format, into pydantic objects | **AI** (Gemini, OpenAI as backup) | 6 insurers, 6 formats, several patients per e-mail. No hand-written text rules. |
| Billed − paid, fair or unfair, which claim it is | **Plain code** (`integration/claimtrail/rules.py`) | Clear rules with one right answer |
| Draft the appeal letter | **AI** | A person checks and sends every letter |

## The systems (each a separate service, same addresses as `main`)
| System | URL | Folder |
|---|---|---|
| **Nirmaya HMS + Claim Reconciliation tab** (runs ClaimTrail) | http://localhost:8061 | `integration/` |
| Nirmaya Mail: e-mail server + webmail | http://localhost:8025 (SMTP :2525) | `mail_portal/` |
| Insurer Desk: plays the 6 insurers (demo tool) | http://localhost:8070 | `demo/` |

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python demo/seed.py                    # fresh HMS database + 21 e-mails + data/answer_key.csv
GEMINI_API_KEY=... python start.py     # starts the three systems; Ctrl+C stops them
```
Then open http://localhost:8061 → *Claim Reconciliation* → *Import from billing mailbox* → *Post to Claims Register*.
Score it: `python integration/claimtrail/evaluate.py`. Command line run: `python integration/claimtrail/pipeline.py`.
ClaimTrail needs AI (`OPENAI_API_KEY` is an optional backup); there is no offline mode. Default model
`gemini-3.1-flash-lite`, paced to 12 calls a minute for the free tier (`GEMINI_RPM`; 0 = no pacing on a paid key),
so the first full import of 21 e-mails takes about 2 minutes. Later imports only read new e-mails.
Sample-month score with Gemini: **30 of 30 claims correct, ₹1,99,800 of ₹1,99,800 unfair cuts caught, 0 false alarms.**

## The sample month (answer key)
30 claims, 5 per insurer, in 21 e-mails. Every claim has an itemised bill in HMS, and every planted cut comes
from a real line of it. Planted: 20 paid in full, 5 fair cuts (₹57,200), **5 unfair cuts (₹1,99,800 worth appealing)**,
₹2,57,000 cut in all. `python integration/claimtrail/evaluate.py` scores ClaimTrail against this
(per insurer, ₹ caught, false alarms) once `GEMINI_API_KEY` is set.

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
integration/     Nirmaya HMS after the FDE (:8061): backend/ (app.py +2 lines, db.py, reconcile.py NEW) ·
                 frontend/ (same pages + reconcile.html/.js NEW) · database/ (hms.db) ·
                 claimtrail/ NEW: the AI components (connectors, llm, ai, rules, pipeline, evaluate, output/)
mail_portal/     Nirmaya Mail, a separate service (:8025, SMTP :2525): backend/ · frontend/ · storage/maildir/
demo/            DEMO ONLY: insurer_desk/ · insurers/ (the 6 insurers' templates, PDFs, policy) · seed.py (reset)
data/            answer_key.csv: the true result of each sample claim, written by seed.py, used only by evaluate.py
docs/            ARCHITECTURE · TEACHING_PLAN · DEMO_PLAN · DISCOVERY_NOTE · GLOSSARY (course material, both branches)
presentation/    HTML slide deck (open presentation/index.html)
start.py         starts every system
```
Read next: [integration/README.md](integration/README.md) · [mail_portal/README.md](mail_portal/README.md) ·
[demo/README.md](demo/README.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [summary.md](summary.md)
