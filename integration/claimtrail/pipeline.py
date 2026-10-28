"""ClaimTrail's pipeline: insurer e-mails + the HMS claims export -> every claim filled in -> integration/claimtrail/output/results.csv
Run: python integration/claimtrail/pipeline.py   (needs the systems running: python start_integration.py, and GEMINI_API_KEY).
The Claim Reconciliation tab (integration/backend/reconcile.py) calls run(). Incremental: pass the previous results and only the NEW e-mails; earlier results are kept.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

import ai
import connectors
import llm
import rules

OUT = Path(__file__).resolve().parent / "output"   # claimtrail/output: results, processed e-mails, copies
FILLED = ["letter_file", "name_on_letter", "matched_by", "paid", "cut", "reason", "category", "result"]


def read(email, log):
    """AI reads one e-mail -> its settlements, or None if the AI call failed (the e-mail is retried next run)."""
    try:
        return ai.read_email(email["text"]).settlements
    except Exception as e:
        log(f"  {email['file']}: AI could not read it ({type(e).__name__}: {str(e)[:80]}), will retry next run")


def draft(row, log):
    """AI drafts the appeal letter; if the AI call fails, the claim is kept without a draft."""
    try:
        return ai.draft_appeal(row)
    except Exception as e:
        log(f"  {row['claim_id']}: appeal not drafted ({type(e).__name__}), write it by hand or run again")
        return ""


def run(emails, out=OUT, log=print, previous=None):
    """emails = [{file, text}] (see connectors.fetch_emails). Returns (results, handled): `handled` = files of
    e-mails that are done (every claim in them filled in now or already settled). The rest are retried later."""
    if not llm.READY:
        raise RuntimeError(llm.NO_KEY)
    out.mkdir(parents=True, exist_ok=True)
    log(f"Reader: {llm.MODE}")
    claims = connectors.fetch_claims()                  # what the hospital billed (HMS export), with each status
    done = set() if previous is None else set(previous.claim_id[previous.letter_file.notna()])

    # 1. AI: read every e-mail (8 at a time) -> structured settlements (pydantic), one per patient in the e-mail
    with ThreadPoolExecutor(8) as pool:
        read_all = list(pool.map(lambda e: read(e, log), emails))

    # 2. RULES: find each settlement's claim, skip claims already settled, work out the cut, decide fair or unfair
    filled, handled, skipped = {}, set(), 0
    for email, settlements in zip(emails, read_all):
        name, ok = email["file"], settlements is not None
        for s in settlements or []:
            i, how = rules.find_claim(s, claims)
            if i is None:
                log(f"  {name}: no claim found for '{s.patient_name}' (will retry next run)")
                ok = False
                continue
            claim_id, status = claims.at[i, "claim_id"], claims.at[i, "status"]
            if status != "SUBMITTED" or claim_id in done:   # never redo or overwrite a settled claim
                log(f"  {name}: {claim_id} is already settled ({status}), skipped")
                skipped += 1
                continue
            cut = claims.at[i, "amount_claimed"] - s.paid
            filled[claim_id] = [name, s.patient_name, how, s.paid, cut, s.reason, s.category, rules.decide(cut, s.category)]
        if ok:
            handled.add(name)
    found = pd.DataFrame(list(filled.values()), index=list(filled.keys()), columns=FILLED)
    df = claims.merge(found, left_on="claim_id", right_index=True, how="left")
    df["new"] = df.claim_id.isin(found.index)

    # 3. AI: draft a letter only for the NEW unfair cuts
    todo = df[df.new & (df.result == "UNFAIR_CUT")].to_dict("records")
    with ThreadPoolExecutor(8) as pool:
        drafts = dict(zip([r["claim_id"] for r in todo], pool.map(lambda r: draft(r, log), todo)))
    df["appeal_letter"] = df.claim_id.map(drafts)

    # 4. Keep what earlier runs filled in
    if done:
        old = previous[previous.letter_file.notna()].set_index("claim_id")
        keep = df.claim_id.isin(old.index) & ~df.new
        cols = FILLED + ["appeal_letter"]
        df[cols] = df[cols].astype(object)
        df.loc[keep, cols] = old.loc[df.claim_id[keep], cols].to_numpy()
    df.loc[df.result.isna() & (df.status != "SUBMITTED"), "result"] = "IN_HMS"   # settled in HMS, not by this run
    df["result"] = df["result"].fillna("NO_LETTER")
    df["appeal_letter"] = df["appeal_letter"].fillna("")
    df.to_csv(out / "results.csv", index=False)

    # 5. Report in rupees
    unfair = df[df.result == "UNFAIR_CUT"]
    log(f"This run: {len(emails)} new e-mail(s), {len(found)} claim(s) filled in, {skipped} already settled, "
        f"{len(emails) - len(handled)} e-mail(s) to retry.")
    log(f"All claims so far: cut Rs. {pd.to_numeric(df.cut).where(lambda c: c > rules.TOLERANCE).sum():,.0f}. "
        f"Worth appealing: Rs. {pd.to_numeric(unfair.cut).sum():,.0f} across {len(unfair)} claims.")
    return df, handled


if __name__ == "__main__":
    run(connectors.fetch_emails(OUT / "inbox"))   # every e-mail in the billing mailbox, a full run
    print(f"Saved {OUT / 'results.csv'}")
