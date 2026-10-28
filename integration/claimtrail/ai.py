"""AI part: the jobs plain code can't do well. No hand-written text rules anywhere.
  1. read_email: read one insurer e-mail (a letter, a table, a PDF, one patient or several) -> a list of settlements
  2. draft_appeal: write the appeal letter for an unfair cut
The answer to (1) comes back as pydantic objects (structured output): the schema below IS the instruction for the
shape of the answer, so the rest of the code gets clean numbers, not free text.
Calls go through llm.ask (Gemini, falling back to OpenAI).
"""
from typing import Literal

from pydantic import BaseModel, Field

from llm import ask

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


def read_email(text):
    """Text of one insurer e-mail (subject, body and the text of any PDF attachment) -> Email."""
    return ask("This e-mail was sent by an insurance company to a hospital's billing desk. It settles one or more "
               "of the hospital's insurance claims; the details may be in the body, in a table, or in the attached "
               "letter. Extract every claim it settles.\n\n" + text, Email)


def draft_appeal(c):
    """c = one result row (dict) with an unfair cut -> appeal letter text."""
    facts = (f"Claim {c['claim_id']} for {c['patient_name']}: billed Rs. {c['amount_claimed']:,.0f}, paid Rs. "
             f"{c['paid']:,.0f}, short by Rs. {c['cut']:,.0f}. Reason given: '{c['reason']}'.")
    return ask(f"Write a short, polite, firm appeal letter from the Billing Desk, Nirmaya Multispeciality Hospital, "
               f"Pune to {c['insurer']} asking them to pay the amount they cut. Under 150 words, plain text, "
               f"ready to send (no placeholders).\n\n" + facts)
