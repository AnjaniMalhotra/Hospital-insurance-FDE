"""Rules part: plain code for everything with a clear answer. No AI in this file.
Same input -> same answer, every time, and the finance team can read every rule.
"""
from difflib import SequenceMatcher

TOLERANCE = 100  # a cut of up to Rs. 100 is rounding, not a real cut
FAIR = {"ROOM_LIMIT", "NOT_COVERED_ITEMS", "PATIENT_SHARE"}  # cuts the policy allows: no appeal


def similar(a, b):
    """0..1: how alike two names are. 'aanjali sharma' vs 'Anjali Sharma' -> high; 'R. Kumar' style initials count."""
    x, y = a.lower().replace(".", "").split(), b.lower().replace(".", "").split()
    if x and y and x[-1] == y[-1] and x[0][0] == y[0][0]:
        return 1.0
    return SequenceMatcher(None, " ".join(sorted(x)), " ".join(sorted(y))).ratio()


def find_claim(letter, claims):
    """Which HMS claim is this letter about? Returns (row index, how) or (None, '').
    1st: the claim number, if the letter prints one. 2nd: same billed amount + a similar patient name."""
    if letter.claim_no:
        hit = claims.index[claims.claim_id.str.endswith(letter.claim_no)]
        if len(hit):
            return hit[0], "claim number"
    pool = claims[claims.amount_claimed == letter.billed]
    scores = {i: similar(pool.at[i, "patient_name"], letter.patient_name) for i in pool.index}
    best = max(scores, key=scores.get, default=None)
    return (best, "name + amount") if best is not None and scores[best] >= 0.8 else (None, "")


def decide(cut, category):
    """Paid in full, a fair cut (policy allows it), or an unfair cut (worth an appeal)."""
    if cut <= TOLERANCE:
        return "PAID_FULL"
    return "FAIR_CUT" if category in FAIR else "UNFAIR_CUT"
