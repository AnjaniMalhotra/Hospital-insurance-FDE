# Handoff: where this project stands (written 2026-10-30)

For the next Claude session (or person). Read this first, then `docs/CLAUDE.md` (the rules) and `README.md` (the project).

## What this is
A teaching project, "FDE training project 1". Students play a Forward Deployed Engineer for a fictional hospital
(Nirmaya). Insurers e-mail settlements that pay less than billed; staff retype them into the HMS by hand.
The solution (ClaimTrail) reads the e-mails with AI and decides fair vs unfair cuts with plain rules.
The user is **teaching with this**: notebook first, then the code. So everything must stay simple and readable.

## Two branches (both pushed to GitHub, `AnjaniMalhotra/Hospital-insurance-FDE`)
| Branch | What it is | Start it |
|---|---|---|
| `main` | The hospital today, no AI. `legacy_system/` (HMS) + `mail_portal/` + `demo/` | `python start_legacy.py` |
| `fde-solution` | Same plus a *Claim Reconciliation* tab. `integration/` replaces `legacy_system/`, plus `integration/claimtrail/` (the AI), `data/`, `notebooks/` | `python start_integration.py` |

- Ports: Mail 8025 (SMTP 2525), HMS 8061, Insurer Desk 8070 (demo tool that plays the 6 insurers, password `demo`).
- One venv covers both branches: `.venv` (built with `uv`, Python 3.11) from `fde-solution`'s `requirements.txt`.
- Reset the demo with `python demo/seed.py` (30 patients, 21 settlement e-mails). Run it after switching branches.
- Shared code (`mail_portal/`, `demo/insurers/`, `demo/insurer_desk/`, the HMS files, glossary) is **identical on both branches** on purpose.
  Fix shared code on `main`, then merge into `fde-solution`. `integration/backend/{app,db}.py` are renamed copies of `legacy_system/backend/`.

## Keys and `.env`
- `.env` in the project root (git-ignored, never commit) holds `GEMINI_API_KEY` and `OPENAI_API_KEY`. Both were tested and work.
- `start_integration.py` loads `.env` itself (a small `load_env()`); real environment variables win. `main` needs no keys.
- Models: Gemini `gemini-3-flash-preview`, then `gemini-3.5-flash-lite`, then OpenAI `gpt-5.4-mini` (Pydantic AI `FallbackModel`).

## What was done in this session
- Read both branches fully; added `.env`; built `.venv`; ran the notebook end to end.
- `notebooks/pdf_to_structured_data.ipynb`: now self-contained (ships `notebooks/arogya_letter.pdf`, no imports from the project), outputs saved.
  Uses `gemini-3.1-flash-lite` (differs from the app's models; fine, but worth knowing).
- **Windows bug fixed:** opening an e-mail in Nirmaya Mail returned 500 because Maildir puts `:` in file names (Windows forbids it).
  Fix is in `mail_portal/backend/store.py` (`mailbox.Maildir.colon = "!"`), done by the collaborator and kept.
- One-line plain-English comments added above every Python function, route and code block, on both branches (script-generated, so identical text).
- Glossary: TPA spelled out (Third Party Administrator) plus UHID, cashless claim, self-pay, remittance note, NEFT, JSON, GET/POST, `.env`, seed.
- Cleanup: `__pycache__` removed; stray `integration/` folder removed from `main`; nothing stray on `fde-solution`.

## Known gotchas
- The ClaimTrail import calls the AI on every unprocessed e-mail at once (21 of them): expect 2 to 5 minutes. It looks stuck but isn't.
- VS Code's built-in Simple Browser did not pass clicks through; use a normal browser at `http://127.0.0.1:<port>`.
- `localhost` can resolve to IPv6 first on Windows (slow fallback); the servers listen on IPv4 only.
- Port 8000 is taken by another app on the user's machine.
- Git on Windows prints LF/CRLF warnings; harmless.

## Open items (not done yet)
1. **`seed.py` plan, waiting on the user's answers:** leave only ~3 claims pending so imports finish fast. Proposed: Anjali (`HSP-1011`) + 2 others,
   the other 27 pre-settled in the HMS, only the 3 pending claims' e-mails delivered, an optional `--all` flag for the full 30-claim demo,
   and `evaluate.py` scoring only the claims the run read. `fde-solution` only. Nothing built yet.
2. **Merging `main` into `fde-solution` conflicts in `README.md`:** `fde-solution` links the slides at `hospital-insurance.netlify.app`,
   `main` at `anjanimalhotra.github.io/Hospital-insurance-FDE`. The user must pick one; the README should be identical on both branches.
3. **120-line rule:** `docs/CLAUDE.md` says no file over 120 lines; the new comments pushed some files over (e.g. `demo/insurers/insurers.py`, maybe `ai.py`, `llm.py`).
4. The README and `docs/CLAUDE.md` still show `GEMINI_API_KEY=... python start_integration.py`; it now just reads `.env`.
5. The slides still say "Insurer / TPA" without spelling out TPA.
6. Never ran the full import plus `evaluate.py` on the final code (README claims 30/30 correct, ₹1,99,800 of unfair cuts, 0 false alarms).

## Working style the user wants
Simple words everywhere (comments, docs). Ask before anything destructive or outward-facing; the user explicitly allowed pushing once things worked.
Commit messages end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
