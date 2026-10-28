# Teaching Plan: about 5 hours, for AI beginners

Teams of 3 to 4 play the FDEs. The mentor plays the hospital finance head.
The big idea: **AI reads the messy e-mails into a fixed shape (pydantic); plain code does the money.**

| # | Time | Module | Students do | Files |
|---|---|---|---|---|
| 1 | 0:00–0:40 | **What is an FDE + discovery** | Interview the "client". Write a 1-page discovery note. No code. | `docs/DISCOVERY_NOTE.md` |
| 2 | 0:40–1:10 | **Feel the manual work** | In Nirmaya Mail (:8025) and the old HMS (:8061), reconcile 2 claims by hand. Time yourselves. Then read `docs/ARCHITECTURE.md`: which systems, which protocols? | `legacy_system/` |
| 3 | 1:10–2:00 | **Rules part (no AI)** | Read `rules.py`: find the claim, the cut, fair or unfair. Change `TOLERANCE` or the `FAIR` list and see what moves. | `integration/claimtrail/rules.py` |
| – | 2:00–2:15 | Break | | |
| 4 | 2:15–3:00 | **Six insurers, six formats** | In Nirmaya Mail, open one e-mail per insurer. On paper, try to write one rule that reads all six. Why does it break? | `legacy_system/` (mail) |
| 5 | 3:00–3:45 | **AI with structured output** | Set `GEMINI_API_KEY`. Read the `Settlement` / `Email` pydantic schemas and the prompt in `read_email`. Run: one e-mail → a list of settlements. Discuss: what if AI misreads a number? (matching on the bill catches it) | `integration/claimtrail/ai.py`, `llm.py` |
| 6 | 3:45–4:20 | **Prove it + the integration** | In the integrated HMS (:8062): Import, check, Post. Then `python integration/claimtrail/evaluate.py`. | `integration/` |
| 7 | 4:20–5:00 | **Demo to the "client"** | Each team shows: the problem, the fix, the ₹ number. | `docs/DEMO_PLAN.md` |

## Module 1: what the mentor reveals only if asked
| Good question | Mentor's answer |
|---|---|
| "How do you find out what was paid?" | "Each insurer sends a letter (PDF). We type it into HMS by hand." |
| "Can I see some letters?" | Show one from each insurer. Students should notice 6 different formats, some with several patients. |
| "Do they always show the claim number?" | "Arogya doesn't. And they misspell names." |
| "Are all cuts wrong?" | "No. Room above the policy limit, items not covered, co-pay: those are fair." |
| "How long does it take?" | "About 3 days a month. We only check the big ones." |

## Break-it exercises (pick 2)
1. Send "Tariff as per agreement" from the Insurer Desk. Which category does the AI give it? Should it be FAIR?
2. Remove `"PATIENT_SHARE"` from `FAIR`. How many false alarms appear?
3. Misspell a name more badly in `demo/insurers/documents.py`. Does matching still work? When should it fail?

## Exit ticket (1 line each)
1. What did the client think the problem was? What was it really?
2. One thing you left to code, one thing you gave to AI, and why.
3. Your success number, in rupees.
