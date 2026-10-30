"""Proves ClaimTrail works: compares integration/claimtrail/output/results.csv with the planted answers (data/answer_key.csv).
Run: python integration/claimtrail/evaluate.py   (after an import in the Claim Reconciliation tab, or pipeline.py)
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # the project folder


# Compares ClaimTrail's results with the known answers and prints how many are right.
def main():
    got = pd.read_csv(ROOT / "integration" / "claimtrail" / "output" / "results.csv")
    key = pd.read_csv(ROOT / "data" / "answer_key.csv")
    df = key.merge(got[["claim_id", "insurer", "result"]], on="claim_id", suffixes=("_true", "_got"))
    df["correct"] = df.result_true == df.result_got

    print(pd.crosstab(df.result_true, df.result_got), "\n")
    print(f"Correct: {df.correct.sum()} of {len(df)} claims")
    print("By insurer:", ", ".join(f"{i} {g.correct.sum()}/{len(g)}" for i, g in df.groupby("insurer")))

    unfair = df[df.result_true == "UNFAIR_CUT"]
    caught = unfair[unfair.result_got == "UNFAIR_CUT"]
    false_alarms = df[(df.result_got == "UNFAIR_CUT") & (df.result_true != "UNFAIR_CUT")]
    print(f"Unfair cuts caught: {len(caught)} of {len(unfair)} "
          f"(Rs. {key.set_index('claim_id').cut[caught.claim_id].sum():,.0f} of Rs. {unfair.cut.sum():,.0f})")
    print(f"False alarms (appeals for a fair cut): {len(false_alarms)}")


# Runs the check when this file is started directly.
if __name__ == "__main__":
    main()
