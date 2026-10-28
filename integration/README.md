# Integration: the same hospital HMS + one new tab

What the FDE builds, on the **`fde-solution`** branch: Nirmaya HMS (`main`'s `legacy_system/`, renamed to
`integration/`) with **one new tab, Claim Reconciliation**, in the same old look, at the same address.
Everything else in the HMS is the original code, so the branch diff shows **only the new feature**.

## Open it
`GEMINI_API_KEY=... python start.py`, then **http://localhost:8061** → Staff Login → **Claim Reconciliation** (marked NEW).

## Folder structure (same as `main`'s legacy_system/)
```
main: legacy_system/                fde-solution: integration/
├── backend/                        ├── backend/
│   ├── app.py                      │   ├── app.py            + 2 lines: register the new tab
│   └── db.py                       │   ├── db.py             identical
│                                   │   └── reconcile.py      NEW: the tab's API (runs ClaimTrail, posts results)
├── frontend/                       ├── frontend/
│   ├── index · login · patients    │   ├── index · login · patients   identical
│   ├── claims.html · claim.html    │   ├── claims.html · claim.html   + a help line · + the reconciliation result
│   └── hms.js · style.css          │   ├── hms.js · style.css         + menu link · + a few status colours
│                                   │   └── reconcile.html · .js       NEW: the Claim Reconciliation tab
└── database/hms.db                 ├── database/hms.db
                                    └── claimtrail/           NEW: the AI components
                                        ├── connectors.py     read-only: HMS export + mailbox API (new e-mails only)
                                        ├── llm.py · ai.py    Gemini (OpenAI backup) reads each e-mail into pydantic rows
                                        ├── rules.py          find the claim, work out the cut, fair or unfair
                                        ├── pipeline.py       wires it together · evaluate.py  scores it
                                        └── output/           results.csv · processed.json · inbox/ (copies)
```
See every difference yourself:
```bash
git diff main fde-solution --stat                            # the whole FDE change
git diff main fde-solution -M -- legacy_system integration   # the HMS: one tab + its logic files
```

## The new tab, step by step
1. **Import from billing mailbox:** `reconcile.py` runs ClaimTrail, which fetches only the e-mails it hasn't processed yet
   (plus any it couldn't finish before) and the claims from the HMS export.
2. **Read & match:** Gemini reads each e-mail into `Settlement` rows; rules match each to its claim and decide fair or unfair.
3. **Check:** summary (claims filled in, total deduction, appealable amount) + the results table, with a link to the
   original PDF / e-mail.
4. **Post to Claims Register:** `reconcile.py` writes paid, deduction, reason and result into every claim still SUBMITTED
   and marks it **AUTO-RECONCILED**. Claims already settled (by a clerk, or posted earlier) are skipped, never overwritten.

Reset everything with `python demo/seed.py`. Fixes to the base HMS go on `main` first, then merge `main` into
`fde-solution`.
