# Glossary

Every term in this project, in plain language, with where you see it.

## The role
| Term | Meaning | Where |
|---|---|---|
| **FDE (Forward Deployed Engineer)** | An engineer who goes to the client, finds the real problem, and builds the smallest fix inside the setup they already have. | The role students play |
| **Client** | The organisation we help: Nirmaya hospital (fictional). | The mentor plays it |
| **Discovery** | Asking questions and looking at real files *before* writing code. | Module 1 in `docs/TEACHING_PLAN.md` |
| **Legacy system** | The client's existing software. We read from it but never change it. | `legacy_system/` (Nirmaya HMS) |
| **POC (Proof of Concept)** | A small working version that proves the idea before investing more. | presented in the slides |
| **Integration** | Putting the solution inside the client's routine: here, a new tab in their HMS. | `integration/` |

## Hospital and insurance
| Term | Meaning | Example |
|---|---|---|
| **Claim** | A bill the hospital sends to an insurer for a patient's treatment. | HSP-1011, ₹3,11,600 |
| **Insurer** | The insurance company that pays the claim. | Suraksha, Arogya, Kavach |
| **TPA (Third Party Administrator)** | A company that handles claims on an insurer's behalf. For us it works like an insurer: it sends the settlement. | Arogya Plus **TPA** |
| **UHID** | The hospital's unique ID for each patient (Unique Health ID). | NMH260110 |
| **Cashless claim** | The patient doesn't pay the hospital up front: the hospital bills the insurer directly. | Every insured patient here |
| **Self-pay** | A patient with no insurance, who pays the hospital themselves. So there is no claim. | Choose "Self-pay" when registering a patient |
| **Remittance note** | The insurer's note saying how much it is paying and for which patients. | Kavach's PDF |
| **NEFT** | An Indian bank-to-bank money transfer. Letters say the money will arrive "by NEFT". | Insurer letters |
| **Settlement letter** | The insurer's letter: what it paid for a claim, and why it cut anything. | E-mail attachments in Nirmaya Mail |
| **Cut (deduction)** | Billed minus paid. | ₹78,400 |
| **Fair cut** | A cut the policy allows: room above the policy limit, items never covered (gloves, masks), co-pay. No action. | "Room rent above policy limit" |
| **Unfair cut** | A cut the policy doesn't support. Worth an appeal. | "Investigation charges disallowed" |
| **Co-pay** | A share of the bill the patient pays, as written in the policy. | "Co-pay 10% as per policy" |
| **Appeal letter** | The hospital's request to the insurer to pay the amount it cut. | Drafted by ClaimTrail |
| **HMS** | Hospital Management System: the hospital's billing software. | Nirmaya HMS v4.2 |
| **Rs. / ₹ / lakh** | Indian rupee. 1 lakh = 1,00,000. | ₹1,99,800 |

## The POC
| Term | Meaning | Where |
|---|---|---|
| **Matching** | Finding which claim a letter is about: by claim number, or by billed amount + a similar name. | `rules.find_claim` |
| **Tolerance** | Cuts up to ₹100 count as rounding, not real cuts. | `rules.TOLERANCE` |
| **Result** | Paid in full, Fair cut, Unfair cut, or No letter read. | ClaimTrail table |
| **Answer key** | The true result for each test claim. Used only to test the POC. | `data/answer_key.csv` |
| **False alarm** | An appeal for a cut that was actually fair. | `evaluate.py` |

## AI and tech
| Term | Meaning | Where |
|---|---|---|
| **AI / LLM** | A model that reads and writes text (Gemini, GPT). Here it reads letters and drafts appeals. | `integration/claimtrail/ai.py` |
| **Gemini / OpenAI** | Our main AI model and its backup. | `integration/claimtrail/llm.py` |
| **AI agent (Pydantic AI)** | An AI model + instructions + the shape its answer must have. Our reader agent returns an `Email` object. | `agent("reader")` in `ai.py` |
| **Prompt** | The plain-English instruction we give the AI. | `system_prompt` in `ai.py` |
| **Schema / pydantic** | The fixed shape the AI's answer must follow, written as a Python class with pydantic. | `Settlement`, `Email` in `ai.py` |
| **Structured output** | Asking the AI to answer in a schema, so code gets clean numbers instead of free text. | `Agent(..., output_type=Email)` |
| **API key** | A secret password that lets our code use an AI service. | `GEMINI_API_KEY` |
| **PDF** | The file format most insurers' letters come in (others write in the e-mail body). | `data/letters/` |
| **Itemised bill** | The bill split into heads (room rent, investigations, implants, ...). Sent to the insurer with the claim; the insurer cuts lines from it. | HMS claim page, `bill_items` table |
| **Room-rent limit** | The most per day a policy pays for the room. Above it, the excess is a fair cut. | `demo/insurers/policy.py` |
| **Batch e-mail** | One insurer e-mail that settles several patients' claims at once. | Kavach, Swasthya, Sanjeevani |
| **CSV** | A simple table file that Excel and HMS can open. | "Download for HMS" |
| **Flask** | A small Python web framework. Runs HMS, Nirmaya Mail's webmail and ClaimTrail. | `*/server.py`, `legacy_system/backend/app.py` |
| **SQLite / database** | A database in a single file. HMS keeps patients, claims and settlements in it. | `database/hms.db` |
| **SMTP** | The protocol mail servers use to send and receive e-mail. Insurers send letters to ours on port 2525. | `mail_portal/backend/server.py` |
| **Maildir** | A standard way mail servers store e-mail: one file per message. | `mail_portal/storage/maildir/` |
| **Mailbox API** | A web API to list e-mails and download attachments (like the Gmail API or Microsoft Graph). | `/api/messages` on :8025 |
| **Export** | A read-only copy of data a system lets others take (HMS's claims CSV). | `/export/claims.csv` on :8061 |
| **JSON** | A simple text format for data that programs send to each other. | Every `/api/...` answer |
| **API link (GET / POST)** | A web address a program calls. GET asks for data; POST sends data to be saved. | `@app.get(...)`, `@app.post(...)` |
| **.env file** | A private file with your secret keys. It is never committed to git; the start script reads it for you. | `.env` in the project folder |
| **Seed (reseed)** | Reset the demo to a known starting state: fixed patients, claims and e-mails. | `python demo/seed.py` |
| **Connector** | The code that reads from the client's systems, read-only. | `integration/claimtrail/connectors.py` |
| **Service** | A program running on its own port that others call over HTTP. Each branch runs three. | `start_legacy.py` · `start_integration.py` |
