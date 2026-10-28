# Insurance Settlements, Without the Retyping
*FDE Training Project 1 · Nirmaya Multispeciality Hospital (fictional hospital, real problem)*

You are a **Forward Deployed Engineer (FDE)**: an engineer who goes to the client, finds the real problem, and
builds the smallest working fix *inside the client's existing systems*, without replacing them.

## 1. The client and the problem
Nirmaya hospital bills an insurance company for every insured patient. Each insurer replies with a **settlement**:
how much it paid, and why it paid less (if it did). Some cuts are **fair** (the policy allows them: room rent above the
limit, non-payable items like gloves, the patient's co-pay); others are **unfair** and worth challenging.

The settlements arrive by e-mail from **6 insurers, each in its own format**: PDF letters, a letter typed in the e-mail
body, tables, one e-mail covering several patients, often with no claim number and a misspelt name.
The billing system (HMS) only knows what was *billed*, so a clerk **retypes every settlement into HMS by hand**:

- **Slow:** about 3 days of typing every month.
- **Error-prone:** misspelt names lead to wrong matches, amounts get mistyped, fair/unfair is decided from memory.
- **Incomplete:** only ~40 of 300 claims ever get checked.

> **Example: Anjali Sharma (claim HSP-1011, Arogya).** Billed ₹3,11,600, paid ₹2,33,200, cut ₹78,400 for
> *"Investigation charges disallowed"*. The e-mail spells her *"aanjali sharma"* and has no claim number.
> Her policy covers tests, so the cut is **unfair**, but only if someone finds, matches and checks it.

## 2. Two branches: before and after
| Branch | What you see | Portals |
|---|---|---|
| **`main`** | The hospital **today**: everything by hand | Nirmaya HMS · Nirmaya Mail · Insurer Desk |
| **`fde-solution`** | The hospital **after the FDE**: the same HMS with one new tab, **Claim Reconciliation**, where AI reads the e-mails | Nirmaya HMS (+ new tab) · Nirmaya Mail · Insurer Desk |

The HMS on `fde-solution` is the same code as on `main`, plus the new tab and its logic. See it for yourself:
`git diff main fde-solution --stat -M`.

## 3. The portals
| Portal | Address | What it is |
|---|---|---|
| **Nirmaya HMS** | http://localhost:8061 | The hospital's billing system: patients (with itemised bills), claims register, claim pages |
| **Nirmaya Mail** | http://localhost:8025 | The hospital's e-mail (a separate service). Insurers send settlements to `billing@nirmaya-hospital.example` |
| **Insurer Desk** | http://localhost:8070 | Demo tool that plays the 6 insurers. Log in, review a claim's bill, send a settlement e-mail |

Insurer Desk logins (password `demo` for all): `suraksha` · `arogya` · `jeevan` · `kavach` · `swasthya` · `sanjeevani`.

| Insurer | How it e-mails settlements |
|---|---|
| Suraksha Health | PDF letter with a details box, one claim per e-mail |
| Arogya Plus TPA | PDF typed letter, no claim number, name often misspelt |
| Jeevan Raksha | Letter typed in the e-mail body, no attachment |
| Kavach General | PDF remittance note, one table row per patient, several claims per e-mail |
| Swasthya Bharat TPA | Table in the e-mail body, several claims per e-mail |
| Sanjeevani General | PDF statement with a small table per patient, several claims per e-mail |

## 4. Run it
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python demo/seed.py          # reset: 30 patients with claims and bills, 21 insurer e-mails in the mailbox
```
| Branch | Start | Stop |
|---|---|---|
| `main` | `python start_legacy.py` | Ctrl+C |
| `fde-solution` | `GEMINI_API_KEY=your-key python start_integration.py` | Ctrl+C |

Switching branches: stop the portals, `git switch <branch>`, then `pip install -r requirements.txt` and `python demo/seed.py` again.

## 5. Try it
**Before (branch `main`): one claim by hand.** Nirmaya Mail → open an Arogya e-mail and its PDF → find the patient in
HMS (misspelt, no claim number) → open the claim → type the amount paid, *work out* the deduction, type the reason, and
decide if it's fair. Now imagine 300 a month.

**After (branch `fde-solution`): the new tab.** HMS → *Claim Reconciliation* → **Import from billing mailbox** (about
2 minutes on a free Gemini key) → check the results → **Post to Claims Register**. The Paid column fills in and each
claim shows **AUTO-RECONCILED**.

**A live new claim (either branch).** HMS → *Patients* → *Register New Patient* (choose an insurer, enter the itemised
bill) → Insurer Desk: log in as that insurer, *Review bill*, pick a reason, send → it appears in Nirmaya Mail → handle
it by hand (`main`) or with *Import* (`fde-solution`).

## 6. How the solution works (branch `fde-solution`)
```
New e-mails ──► 1 FETCH ──► 2 READ (AI) ──► 3 MATCH ──► 4 DECIDE ──► staff check ──► POST into HMS
                 code        Gemini          code         code
```
1. **Fetch** (`claimtrail/connectors.py`): only e-mails not processed yet, from the mailbox API; claims from the HMS export. Read-only.
2. **Read** (`claimtrail/ai.py`): Gemini turns each e-mail, whatever its format, into the same fixed shape, one row per patient:

   | Field | Type | Anjali's value |
   |---|---|---|
   | `claim_no` | text or none | none |
   | `patient_name` | text | aanjali sharma |
   | `billed` · `paid` | number | 311600 · 233200 |
   | `reason` | text | Investigation charges disallowed |
   | `category` | ROOM_LIMIT · NOT_COVERED_ITEMS · PATIENT_SHARE · OTHER | OTHER |
3. **Match** (`claimtrail/rules.py`): by claim number, or the same billed amount + a similar name → HSP-1011.
4. **Decide** (`claimtrail/rules.py`): cut = billed − paid; room limit / non-covered items / co-pay = fair, anything else = unfair.

**AI reads, code decides.** AI only turns messy e-mails into clean rows; every rupee decision is a plain rule you can read.
If an AI call fails, that e-mail is simply retried on the next import, and claims already settled are never overwritten.

**Does it work?** `python integration/claimtrail/evaluate.py` compares the results with the known answers for the
30 sample claims: **30 / 30 correct, ₹1,99,800 of unfair cuts found, 0 false alarms**, in about 2 minutes instead of 3 days.

## 7. Folders
```
legacy_system/     [main]          Nirmaya HMS: backend/ (app.py, db.py) · frontend/ (pages) · database/ (hms.db)
integration/       [fde-solution]  the same HMS + the new tab: backend/reconcile.py, frontend/reconcile.html + .js
  claimtrail/                      the AI components: connectors, llm, ai, rules, pipeline, evaluate
mail_portal/       [both]          Nirmaya Mail: backend/ (SMTP server, mailbox API) · frontend/ · storage/maildir/
demo/              [both]          insurer_desk/ · insurers/ (the 6 insurers' formats and policies) · seed.py (reset)
data/              [fde-solution]  answer_key.csv: the known answers for the 30 sample claims (used by evaluate.py)
docs/                              ARCHITECTURE · TEACHING_PLAN · GLOSSARY · summary · CLAUDE (notes for Claude Code)
presentation/                      the slide deck: open presentation/index.html
start_legacy.py    [main]          starts Mail, the HMS and the Insurer Desk
start_integration.py [fde-solution] starts Mail, the HMS with the new tab and the Insurer Desk
```
New words? See [docs/GLOSSARY.md](docs/GLOSSARY.md). How the systems connect: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
