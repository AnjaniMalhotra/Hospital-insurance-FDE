"""The insurers' side (outside the hospital): 6 companies, each e-mailing its settlements in its own way.
Used by seed.py (last month's e-mails) and the demo Insurer Desk (new e-mails, sent by real SMTP).
Each write function takes the claims for ONE e-mail and returns (subject, body text, body HTML or None, PDF files).
"""
import random
from email.message import EmailMessage
from email.utils import format_datetime

import documents
import statements
from documents import inr

MAILBOX = "billing@nirmaya-hospital.example"


def cover(company):
    return f"Dear Sir/Madam,\n\nPlease find attached the settlement details for your hospital.\n\nRegards,\n{company}"


def pdf(prefix, data):
    return [(f"{prefix}_{random.randint(10000, 99999)}.pdf", data)]


def suraksha(cs):
    c = cs[0]
    return (f"Claim settlement - {c.claim_id.replace('-', '')}", cover("Suraksha Health Claims"), None,
            pdf("suraksha_letter", documents.suraksha(c)))


def arogya(cs):
    return "Settlement advice", cover("Arogya Plus TPA"), None, pdf("arogya_letter", documents.arogya(cs[0]))


def kavach(cs):
    return "Remittance note", cover("Kavach Remittances"), None, pdf("kavach_remittance", statements.kavach(cs))


def sanjeevani(cs):
    return (f"Settlement statement ({len(cs)} claims)", cover("Sanjeevani Hospital Claims Cell"), None,
            pdf("sanjeevani_statement", statements.sanjeevani(cs)))


def jeevan(cs):  # no attachment: the letter IS the e-mail. Patient as initial + surname, no hospital claim number.
    c = cs[0]
    first, last = c.patient_name.split()
    text = (f"Dear Billing Team,\n\nGreetings from Jeevan Raksha Insurance.\n\nThis is to inform you that the "
            f"hospitalisation claim of {first[0]}. {last} (admitted {c.admission_date}), our ref JR/CL/{c.claim_id[4:]}77, "
            f"has been processed.\n\n  Amount claimed by hospital : INR {inr(c.amount_claimed)}.00\n"
            f"  Amount settled             : INR {inr(c.paid)}.00\n"
            f"  Remarks                    : {c.reason or 'Settled in full'}\n\nPayment will reach your account by "
            "NEFT within 3 working days.\n\nWarm regards,\nSettlements Desk\nJeevan Raksha Insurance Co.")
    return f"Claim processed - ref JR/CL/{c.claim_id[4:]}77", text, None, []


def swasthya(cs):  # no attachment: one e-mail, a table in the body with one row per patient
    head = ["Sr", "Patient", "Bill No", "Bill Amt", "Approved", "Short-paid reason"]
    rows = [[n, c.patient_name.upper(), c.claim_id.replace("-", "/"), inr(c.amount_claimed), inr(c.paid),
             c.reason or "-"] for n, c in enumerate(cs, 1)]
    text = "Dear Team,\n\nSettlement summary for this week:\n\n" + "\n".join(
        " | ".join(str(v) for v in r) for r in [head] + rows) + "\n\nRegards,\nSwasthya Bharat TPA - Provider Cell"
    cells = lambda r, tag: "".join(f'<{tag} style="border:1px solid #999;padding:4px 8px">{v}</{tag}>' for v in r)
    html = (f'<p>Dear Team,</p><p>Settlement summary for this week:</p><table style="border-collapse:collapse;'
            f'font:13px Arial"><tr style="background:#FDE68A">{cells(head, "th")}</tr>'
            + "".join(f"<tr>{cells(r, 'td')}</tr>" for r in rows) + "</table><p>Regards,<br>Swasthya Bharat TPA - Provider Cell</p>")
    return f"Weekly settlement summary - {len(cs)} claims", text, html, []


INSURERS = {  # name -> desk login, e-mail sender, max claims in one e-mail, template, what the hospital receives
    "Suraksha Health": dict(login="suraksha", sender="Suraksha Health Claims <claims@suraksha-health.example>",
                            batch=1, write=suraksha, format="PDF letter with a details box, one claim per e-mail"),
    "Kavach General": dict(login="kavach", sender="Kavach Remittances <remittance@kavach-general.example>",
                           batch=4, write=kavach, format="PDF remittance note: one table row per patient, several claims"),
    "Jeevan Raksha": dict(login="jeevan", sender="Jeevan Raksha Settlements <settlements@jeevanraksha.example>",
                          batch=1, write=jeevan, format="Letter typed in the e-mail body, no attachment, no claim number"),
    "Swasthya Bharat TPA": dict(login="swasthya", sender="Swasthya Bharat TPA <provider.cell@swasthyabharat.example>",
                                batch=4, write=swasthya, format="Table in the e-mail body, one row per patient, several claims"),
    "Arogya Plus TPA": dict(login="arogya", sender="Arogya Plus TPA <noreply@arogyaplus-tpa.example>",
                            batch=1, write=arogya, format="PDF typed letter, no claim number, name often misspelt"),
    "Sanjeevani General": dict(login="sanjeevani", sender="Sanjeevani Claims Cell <hospital.desk@sanjeevani-gic.example>",
                               batch=4, write=sanjeevani, format="PDF statement: a small table for each patient, several claims"),
}


def settlement_email(cs, when):
    """cs = the claims for one e-mail (same insurer), each with: claim_id, patient_name, insurer, admission_date,
    amount_claimed, paid, reason, paid_on. Returns (the e-mail message, [(PDF file name, PDF bytes)])."""
    t = INSURERS[cs[0].insurer]
    subject, text, html, files = t["write"](cs)
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Date"], msg["Subject"] = t["sender"], MAILBOX, format_datetime(when), subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")
    for name, data in files:
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=name)
    return msg, files
