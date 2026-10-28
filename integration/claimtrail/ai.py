"""AI part: the jobs plain code can't do well. No hand-written text rules anywhere.
  1. read_email: the READER agent reads one insurer e-mail (a letter, a table, a PDF, one patient or several)
     -> an Email object holding a list of settlements
  2. draft_appeal: the WRITER agent writes the appeal letter for an unfair cut
Both are Pydantic AI agents on llm.model() (Gemini, falling back to OpenAI). The reader's output_type is the Email
model below, as the model's native JSON output, so its answer is a validated pydantic object: the schema IS the
instruction for the shape of the answer.
"""
from functools import cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput

import llm

Category = Literal["ROOM_LIMIT", "NOT_COVERED_ITEMS", "PATIENT_SHARE", "OTHER"]


class Settlement(BaseModel):
    """One patient's claim inside the e-mail."""
    claim_no: str | None = Field(description="The HOSPITAL's claim / bill number, digits only (HSP-1011, HSP1011, "
                                             "NMH/HSP-1011, HSP/1011 -> '1011'). null if not shown. Not the insurer's ref.")
    patient_name: str = Field(description="The patient's name exactly as written, typos and initials included")
    billed: float = Field(description="Amount the hospital claimed / billed, in rupees, as a plain number")
    paid: float = Field(description="Amount the insurer approved / settled / paid, in rupees, as a plain number")
    reason: str = Field(description="The insurer's reason for paying less, word for word. '' if paid in full")
    category: Category = Field(description="ROOM_LIMIT: room rent above the policy limit. NOT_COVERED_ITEMS: only "
                                           "non-medical consumables the policy never covers (gloves, masks, syringes). "
                                           "PATIENT_SHARE: co-pay the patient owes. OTHER: every other reason, e.g. "
                                           "investigations/tests, implants, treatment, fees or documents disallowed; "
                                           "also OTHER if nothing was cut.")


class Email(BaseModel):
    insurer: str = Field(description="The insurance company or TPA that sent it")
    settlements: list[Settlement] = Field(description="One item per patient/claim in the e-mail and its attachments")


@cache  # build each agent once, the first time it's needed (so importing works without a key)
def agent(job):
    if job == "reader":
        return Agent(llm.model(), output_type=NativeOutput(Email), model_settings=llm.SETTINGS, system_prompt=(
            "You read e-mails an insurance company sent to a hospital's billing desk. Each settles one or more of "
            "the hospital's insurance claims; the details may be in the body, in a table, or in the attached letter. "
            "Extract every claim it settles."))
    return Agent(llm.model(), model_settings=llm.SETTINGS, system_prompt=(
        "You write short, polite, firm appeal letters from the Billing Desk, Nirmaya Multispeciality Hospital, Pune, "
        "asking an insurer to pay the amount it cut. Under 150 words, plain text, ready to send (no placeholders)."))


def read_email(text):
    """Text of one insurer e-mail (subject, body and the text of any PDF attachment) -> Email."""
    return llm.run(agent("reader"), text).output


def draft_appeal(c):
    """c = one result row (dict) with an unfair cut -> appeal letter text."""
    return llm.run(agent("writer"), f"To {c['insurer']}. Claim {c['claim_id']} for {c['patient_name']}: billed Rs. "
                                    f"{c['amount_claimed']:,.0f}, paid Rs. {c['paid']:,.0f}, short by Rs. {c['cut']:,.0f}. "
                                    f"Reason given: '{c['reason']}'.").output
