"""Sets up "last month" at Nirmaya: the HMS database's 30 demo patients + claims with itemised bills, and the
settlements 6 insurers e-mailed to the billing mailbox (letters, tables, PDFs, several patients per e-mail).
Run: python demo/seed.py      (also resets the demo: run it before each class; patients staff added are kept)
"""
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "legacy_system" / "backend"), str(ROOT / "mail_portal" / "backend"),
                str(ROOT / "demo" / "insurers")]
import db  # noqa: E402  (the HMS database)
import insurers  # noqa: E402
import policy  # noqa: E402  (the insurers' policy terms: what each reason cuts)
import store  # noqa: E402  (the mail server's mailbox)

random.seed(7)
IST = timezone(timedelta(hours=5, minutes=30))
NAMES = ["Ramesh Kumar", "Sunita Rao", "Anil Verma", "Priya Nair", "Mohammed Irfan", "Kavita Joshi",
         "Suresh Patel", "Meena Iyer", "Rajesh Gupta", "Fatima Shaikh", "Anjali Sharma", "Vikram Singh",
         "Lakshmi Reddy", "Arjun Mehta", "Pooja Desai", "Harish Rao", "Neha Kapoor", "Deepak Yadav",
         "Sanjay Mishra", "Geeta Pillai", "Rahul Chauhan", "Shalini Menon", "Manoj Tiwari", "Rekha Das",
         "Imran Khan", "Swati Kulkarni", "Ashok Jain", "Divya Krishnan", "Nitin Saxena", "Farah Ali"]
CASES = [("Cardiology", "Dr. R. Menon", "Coronary angioplasty with stent"),
         ("Orthopaedics", "Dr. S. Kulkarni", "Knee replacement"),
         ("General Surgery", "Dr. A. Deshpande", "Appendix removal (laparoscopic)"),
         ("General Medicine", "Dr. P. Joshi", "Dengue fever"), ("Ophthalmology", "Dr. N. Bhatt", "Cataract surgery")]
ANJALI = 10  # our running example: Arogya claim HSP-1011, billed 3,11,600, paid 2,33,200
ANJALI_BILL = [("Room rent", 5, 5000), ("Doctor & surgeon fees", 1, 60000), ("Investigations (lab, imaging)", 1, 78400),
               ("Medicines & pharmacy", 1, 42200), ("Consumables (gloves, masks, syringes)", 1, 18000),
               ("Implants", 1, 58000), ("OT & procedure charges", 1, 30000)]   # total 3,11,600
IMPLANTS = {"Cardiology": (45000, 90000), "Orthopaedics": (60000, 120000), "Ophthalmology": (8000, 25000)}


def make_bill(dept, insurer, room_above_limit):
    """A realistic itemised bill: (head, qty, rate) rows. Room rent is above the insurer's limit only when asked."""
    r = lambda lo, hi: random.randrange(lo, hi, 100)
    limit = policy.ROOM_LIMIT[insurer]
    rate = limit + random.choice([1500, 2500, 3500]) if room_above_limit else random.choice(range(2500, limit + 1, 500))
    rows = [("Room rent", random.randint(2, 7), rate), ("Doctor & surgeon fees", 1, r(15000, 80000)),
            ("Investigations (lab, imaging)", 1, r(8000, 60000)), ("Medicines & pharmacy", 1, r(10000, 70000)),
            ("Consumables (gloves, masks, syringes)", 1, r(3000, 20000))]
    if dept in IMPLANTS:
        rows.append(("Implants", 1, r(*IMPLANTS[dept])))
    if dept != "General Medicine":
        rows.append(("OT & procedure charges", 1, r(20000, 90000)))
    return rows


def clear_demo_records():
    """Remove the demo's own patients and claims (NMH260100.., HSP-1001..). Patients staff added keep their records."""
    uhids, claim_ids = [f"NMH{260100 + i}" for i in range(len(NAMES))], [f"HSP-{1001 + i}" for i in range(len(NAMES))]
    for table, column, ids in [("settlements", "claim_id", claim_ids), ("bill_items", "claim_id", claim_ids),
                               ("claims", "claim_id", claim_ids), ("patients", "uhid", uhids)]:
        db.run(f"DELETE FROM {table} WHERE {column} IN ({', '.join('?' * len(ids))})", *ids)


def main():
    clear_demo_records()
    store.clear()
    insurers.SENT.unlink(missing_ok=True)
    results = ["FAIR_CUT"] * 5 + ["UNFAIR_CUT"] * 5 + ["PAID_FULL"] * 20
    random.shuffle(results)
    swap = results.index("UNFAIR_CUT")
    results[swap], results[ANJALI] = results[ANJALI], results[swap]

    claims = []
    for i, (name, result) in enumerate(zip(NAMES, results)):
        insurer = list(insurers.INSURERS)[i % 6]
        dept, doctor, diagnosis = CASES[0] if i == ANJALI else random.choice(CASES)
        reason = policy.FAIR[i % 3] if result == "FAIR_CUT" else ""
        rows = ANJALI_BILL if i == ANJALI else make_bill(dept, insurer, reason == policy.FAIR[0])
        bill = [{"head": h, "qty": q, "rate": rate, "amount": q * rate} for h, q, rate in rows]
        if result == "UNFAIR_CUT":   # an unfair reason that really applies to this bill
            reason = "Investigation charges disallowed" if i == ANJALI else random.choice(
                [x for x in policy.UNFAIR if policy.deduction(x, bill, insurer)])
        billed = sum(b["amount"] for b in bill)
        paid = billed - (policy.deduction(reason, bill, insurer) if reason else 0)
        admitted, uhid, claim_id = date(2026, 9, 1 + i % 28), f"NMH{260100 + i}", f"HSP-{1001 + i}"

        # 1) The hospital's own records, in the HMS database
        db.run("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", uhid, name, random.randint(24, 80),
               f"98{random.randint(10**7, 10**8 - 1)}", dept, doctor, diagnosis, admitted.isoformat(),
               (admitted + timedelta(days=random.randint(1, 7))).isoformat(), insurer, f"POL/{random.randint(10**7, 10**8 - 1)}")
        db.run("INSERT INTO claims (claim_id, uhid, insurer, billed, submitted) VALUES (?, ?, ?, ?, ?)",
               claim_id, uhid, insurer, billed, (admitted + timedelta(days=8)).isoformat())
        db.add_bill(claim_id, bill)
        claims.append(SimpleNamespace(claim_id=claim_id, patient_name=name, insurer=insurer, amount_claimed=billed,
                                      admission_date=admitted.isoformat(), paid=paid, reason=reason))

    # 2) The insurers' settlement e-mails, already sitting in the billing mailbox. Insurers that batch send 3 claims
    #    per e-mail (here: 3 + 2), the others one e-mail per claim.
    emails = 0
    for insurer, t in insurers.INSURERS.items():
        mine, size = [c for c in claims if c.insurer == insurer], 1 if t["batch"] == 1 else 3
        for k in range(0, len(mine), size):
            group = mine[k:k + size]
            when = datetime(2026, 10, 5 + int(group[0].claim_id[4:]) % 20, random.randint(9, 18), random.randint(0, 59),
                            tzinfo=IST)
            for c in group:
                c.paid_on = when.date().isoformat()
            msg, _ = insurers.settlement_email(group, when)
            store.deliver(msg.as_bytes())
            insurers.record_sent(group)
            emails += 1
    print(f"Seeded: {len(NAMES)} demo patients + claims in {db.DB.name}, {emails} e-mails from {len(insurers.INSURERS)} "
          "insurers in the billing mailbox.")


if __name__ == "__main__":
    main()
