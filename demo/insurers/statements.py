"""Multi-claim PDFs: one settlement document that covers several patients at once (built on documents.py).
Kavach: a remittance note, one table row per patient. Sanjeevani: a statement with a small table for each patient."""
from documents import finish, inr, letterhead, para, split_name, table


# Kavach's short patient name. Example: 'Anjali Sharma' -> 'Anjali S.'.
def member(name):
    """Kavach's way of writing a member: first name + surname initial ("Anjali S."), or the name if it is one word."""
    first, last = split_name(name)
    return f"{first} {last[0]}." if last else first


# Kavach's PDF remittance note: one table row per patient.
def kavach(cs):
    maroon = (150, 30, 45)
    pdf = letterhead("Kavach General Insurance Co. Ltd.", maroon, ["MG Road, Bengaluru 560001",
                     "IRDAI Reg. No. 162 | remittance@kavach-general.example"], f"KGI-RN-{cs[0].claim_id[4:]}-{len(cs)}",
                     cs[0].paid_on)
    para(pdf, "REMITTANCE NOTE", bold=True)
    para(pdf, f"Provider ID: PRV-20417. Payment details for the {len(cs)} claims below. Amounts in INR.")
    rows = [[member(c.patient_name), f"NMH/{c.claim_id}", inr(c.amount_claimed),
             inr(c.amount_claimed - c.paid), inr(c.paid), c.reason or "Nil"] for c in cs]
    table(pdf, [["Member", "Hosp. Ref", "Gross", "Disallowed", "Net Paid", "Remarks"]] + rows,
          (28, 30, 22, 22, 22, 56), (240, 225, 228))
    return finish(pdf, "Kavach General Insurance Co. Ltd.", "Provider Payments", maroon)


# Sanjeevani's PDF statement: a small table for each patient.
def sanjeevani(cs):
    purple = (88, 44, 131)
    pdf = letterhead("Sanjeevani General Insurance Ltd.", purple, ["Salt Lake Sector V, Kolkata 700091",
                     "IRDAI Reg. No. 177 | hospital.desk@sanjeevani-gic.example"], f"SGI/STMT/{cs[0].paid_on}", cs[0].paid_on)
    para(pdf, "CLAIM SETTLEMENT STATEMENT", bold=True)
    for n, c in enumerate(cs, 1):
        para(pdf, f"{n}. Insured: {c.patient_name.title()}   |   Hospital bill ref: {c.claim_id}", bold=True, gap=1)
        table(pdf, [["Claimed", "Admissible", "Non-admissible", "Remarks"],
                    [f"Rs. {inr(c.amount_claimed)}", f"Rs. {inr(c.paid)}", f"Rs. {inr(c.amount_claimed - c.paid)}",
                     c.reason or "Fully admissible"]], (35, 35, 35, 75), (232, 224, 242))
    para(pdf, "Admissible amounts are released by NEFT to the account registered with us.")
    return finish(pdf, "Sanjeevani General Insurance Ltd.", "Hospital Claims Cell", purple)
