# demo/: tools for running the demo (NOT teaching material)

Nothing here is part of the hospital or of ClaimTrail. Don't teach it; just use it.

## Insurer Desk: http://localhost:8070
Plays the 6 insurance companies. Each has its own **login** (password `demo` for all) and its own **preset template**:

| Login | Company | What the hospital receives |
|---|---|---|
| `suraksha` | Suraksha Health | PDF letter with a details box, one claim per e-mail |
| `arogya` | Arogya Plus TPA | PDF typed letter, no claim number, name misspelt |
| `jeevan` | Jeevan Raksha | Letter in the e-mail body, no attachment |
| `kavach` | Kavach General | PDF remittance note, one row per patient (up to 4 claims per e-mail) |
| `swasthya` | Swasthya Bharat TPA | HTML table in the e-mail body (up to 4 claims per e-mail) |
| `sanjeevani` | Sanjeevani General | PDF statement, a small table per patient (up to 4 claims per e-mail) |

Each insurer has policy terms (`demo/insurers/policy.py`): a room-rent limit per day (₹4,000 to ₹6,000) and 10% co-pay.

Show a **new** claim going all the way through:
1. **Nirmaya HMS** (http://localhost:8061) → Patients → *Register New Patient*
   (choose an insurer, enter the itemised bill: room days x rate, investigations, implants, ...) → a new claim,
   e.g. HSP-1031, status SUBMITTED. Tip: a room rate above the insurer's limit gives a fair room-rent cut.
2. **Insurer Desk** → log in as that insurer → *Review bill* shows HSP-1031's itemised bill with your policy checks
   (room rent above your limit, non-payable consumables) → choose *Pay in full* or a reason: the deduction is worked
   out from the bill and the line it cuts is highlighted (you can change the amount) → tick up to 4 claims for batch
   insurers → *Send settlement e-mail*.
   The e-mail is built in that insurer's template and sent by **real SMTP** to the hospital's mail server.
3. **Nirmaya Mail** (http://localhost:8025) → the e-mail appears at the top, unread.
4. **Nirmaya HMS** (http://localhost:8061) → *Claim Reconciliation* → *Import from billing mailbox* → only the new e-mail is read (AI), matched and decided → *Post*.

Tip: register 3 patients with **Swasthya** and settle them in one e-mail to show one e-mail → three claims.

## Reset between classes
```bash
python demo/seed.py     # fresh HMS database + the 21 original e-mails + data/answer_key.csv; removes demo patients
```
This also clears `integration/claimtrail/output/`, so ClaimTrail forgets which e-mails it has processed.

## Files
```
demo/
├── insurer_desk/   app.py (logins, reads HMS claims + bills, sends e-mail by smtplib) · static/ (index.html, desk.js)
├── insurers/       insurers.py   the 6 insurers: desk logins, senders, e-mail templates
│                   documents.py  one-claim PDF letters (Suraksha, Arogya) + letterhead helpers
│                   statements.py multi-patient PDFs (Kavach, Sanjeevani)
│                   policy.py     room-rent limits, co-pay, what each reason cuts from a bill
└── seed.py         resets HMS, the mailbox, data/answer_key.csv and integration/claimtrail/output
```
