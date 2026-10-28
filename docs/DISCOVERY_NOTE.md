# Discovery Note: Nirmaya Hospital, Insurance Short-Payments
*Example answer. Students write their own after interviewing the mentor. One page max.*

**Client:** Finance Head, Nirmaya Multispeciality Hospital, Pune (fictional) **FDE team:** ____

## 1. What the client said
"Insurers pay us less than we bill. We don't know which claims, or why. My team has no time to check."

## 2. How it works today
- HMS (the billing software) records each claim and what we **billed**. It has no idea what was **paid**.
- Each insurer sends a **settlement letter (PDF) per claim** by e-mail, in its own style.
- A clerk opens each letter, finds the patient, and **types** paid / deduction / reason into HMS.
- About 3 days a month. Only the biggest claims get checked.

## 3. What is really going wrong
1. The answer (paid and why) is only inside the letters, and **reading them by hand doesn't scale**.
2. Every insurer writes differently: one shows the claim number, one doesn't and misspells names, one just
   changed its layout.
3. Nobody can tell a **fair** cut (allowed by the policy) from an **unfair** one worth appealing.

## 4. Constraints
- We **cannot change HMS**. We read its Excel export and the letters only.
- A person must check every appeal letter before it is sent.

## 5. What we will build (smallest useful thing)
A standalone tool: upload the letters → it fills in every claim (paid, cut, reason) → marks fair or unfair
→ drafts the appeal letters → exports a file to update HMS.
Rules do the maths and the fair/unfair decision. AI only reads the letters (and drafts appeals).

## 6. How we will prove it
30 test claims with known answers (20 paid in full, 5 fair cuts, 5 unfair cuts).
Target: catch every unfair cut, 0 false alarms.

## 7. Success number we will report
"Found ₹X cut by insurers; ₹Y of it is worth appealing. Checking time: from about 3 days to a few minutes."
