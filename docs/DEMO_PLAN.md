# Demo Plan: the legacy way → the integrated HMS

Two git branches, same addresses: HMS **http://localhost:8061** · Nirmaya Mail **http://localhost:8025** ·
Insurer Desk (demo tool) **http://localhost:8070**.
- Act 1 on **`main`**: `git switch main && python demo/seed.py && python start.py`
- Act 2 on **`fde-solution`**: stop it (Ctrl+C), then `git switch fde-solution && python demo/seed.py && GEMINI_API_KEY=... python start.py`
 The idea, the architecture and the POC story are in the slides
(`presentation/`); the live demo shows only the hospital's systems: before and after.

## Act 1: the manual way, in the old HMS (about 8 min)
1. **Home → Login.** "This is the billing system the staff use every day."
2. **Insurance Claims.** "30 claims. Look at the Paid column: empty. HMS only knows what we billed."
3. **Open Anjali's claim (HSP-1011).** "Here is her itemised bill: ₹3,11,600. The insurer gets the same bill."
4. **Staff Webmail (Nirmaya Mail).** "Six insurers e-mail their settlements here, each in its own format: PDF letters,
   a letter in the e-mail body, a table with three patients. HMS has no idea e-mail exists."
5. **Ask a volunteer to do one claim by hand.** Open an Arogya e-mail and its PDF, find the patient (misspelt, no claim
   number), open that claim, type paid, *calculate* the deduction, type the reason, decide if it's fair.
6. **Ask the room:** "That took a few minutes. How long for 300 a month? Who decides fair or unfair?"

## Act 2: the integrated HMS (about 10 min)
1. **http://localhost:8061 → Claim Reconciliation** (marked NEW). "Same HMS, same address, one new tab."
2. **Import from billing mailbox.** Gemini reads every new e-mail into structured rows: 21 e-mails, 30 claims
   (about 2 minutes on a free key, so start it, then explain the slide on the pipeline while it runs).
3. **The summary row:** claims filled in, total deduction, appealable amount.
4. **Show: Unfair cut → Anjali (HSP-1011).** "Her letter says *aanjali sharma* with no claim number. Matched on the
   billed amount and a similar name. ₹78,400 cut for investigations: not allowed by the policy, so it's unfair."
   Click **PDF** to show the original letter.
5. **Post to Claims Register** → open the register: *Paid* is filled in, status **AUTO-RECONCILED**. Open HSP-1011:
   the result and the drafted appeal letter are on the claim page.

## Act 3: a live new claim (optional, about 5 min)
Register a patient in the integrated HMS with an itemised bill → Insurer Desk: log in as that insurer, review the
bill, choose a reason, send → it appears in Nirmaya Mail → **Import from billing mailbox** reads only that one new
e-mail → Post. See `demo/README.md`.

## Key line to close on
**"AI is the reader, not the decider."** Code does the maths and the fair/unfair rule; AI reads e-mails that all
look different.
