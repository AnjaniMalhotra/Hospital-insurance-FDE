"""The insurers' policy terms (the insurer's side, not the hospital's): room-rent limits, co-pay, and how much each
reason for a cut takes off a claim's itemised bill. Used by the Insurer Desk (to suggest the deduction while the
insurer reviews the bill) and by seed.py (so last month's planted cuts match real lines of each bill).
"""
# Reasons for a cut that the policy allows (fair).
FAIR = ["Room rent above policy limit", "Non-payable items (gloves, masks)", "Co-pay 10% as per policy"]
# Reasons for a cut that is worth challenging (unfair).
UNFAIR = ["Investigation charges disallowed", "Excess charges", "Treatment not medically justified",
          "Documents not submitted", "Implant cost not payable"]
# The most room rent each insurer pays per day, in rupees.
ROOM_LIMIT = {"Suraksha Health": 5000, "Kavach General": 4000, "Jeevan Raksha": 6000,  # Rs. per day
              "Swasthya Bharat TPA": 4500, "Arogya Plus TPA": 5000, "Sanjeevani General": 4000}
# The patient's own share of the bill: 10%.
CO_PAY = 0.10
HEAD = {  # reason -> the bill head it cuts
    "Room rent above policy limit": "Room rent",
    "Non-payable items (gloves, masks)": "Consumables (gloves, masks, syringes)",
    "Investigation charges disallowed": "Investigations (lab, imaging)",
    "Excess charges": "Doctor & surgeon fees",
    "Treatment not medically justified": "OT & procedure charges",
    "Documents not submitted": "Medicines & pharmacy",
    "Implant cost not payable": "Implants",
}


# Rupees a reason takes off a bill. Example: 'Investigation charges disallowed' on a bill with Rs. 78,400 of tests -> 78400.
def deduction(reason, bill, insurer):
    """Rupees that `reason` takes off the bill ([{head, qty, rate, amount}]), rounded to Rs. 100."""
    line = [b for b in bill if b["head"] == HEAD.get(reason)]
    if reason == "Room rent above policy limit":   # only the part of the daily rate above the limit
        cut = sum(b["qty"] * max(0, b["rate"] - ROOM_LIMIT[insurer]) for b in line)
    elif reason == "Co-pay 10% as per policy":     # the patient's share of the whole bill
        cut = CO_PAY * sum(b["amount"] for b in bill)
    elif reason == "Excess charges":               # fees above the insurer's tariff: about 30% of them
        cut = 0.3 * sum(b["amount"] for b in line)
    else:                                          # the whole line is disallowed
        cut = sum(b["amount"] for b in line)
    return int(round(cut, -2))
