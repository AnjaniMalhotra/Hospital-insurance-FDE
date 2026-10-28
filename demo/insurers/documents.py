"""The insurers' PDF settlement letters (one claim each), in each insurer's house style. Returns the PDF as bytes.
Suraksha: a letter with a details box. Arogya: a typed letter, no claim number, name misspelt.
Also the shared letterhead/table helpers that statements.py (multi-claim PDFs) builds on."""
from fpdf import FPDF
from fpdf.fonts import FontFace

TO = ["The Medical Superintendent", "Nirmaya Multispeciality Hospital", "Survey No. 42, Baner Road, Pune 411045"]


def split_name(name):
    """'Anjali Sharma' -> ('Anjali', 'Sharma'); the surname is the last word, and a one-word name has none."""
    first, _, last = name.strip().rpartition(" ")
    return (first, last) if first else (last, "")


def inr(x):
    """311600 -> '3,11,600' (Indian digit grouping)."""
    s = str(int(x))
    head, tail = s[:-3], s[-3:]
    groups = [head[max(i - 2, 0):i] for i in range(len(head), 0, -2)][::-1]
    return ",".join(groups + [tail]) if head else tail


def letterhead(name, colour, address, ref, date):
    """Coloured band, logo mark, company name and address, then reference/date and the hospital's address."""
    pdf = FPDF()
    pdf.set_margins(15, 12, 15)
    pdf.add_page()
    pdf.set_auto_page_break(False)
    pdf.set_fill_color(*colour)
    pdf.rect(0, 0, 210, 5, "F")                                         # colour band
    pdf.ellipse(176, 11, 18, 18, "F")                                   # logo mark: a circle with the initial
    pdf.set_xy(176, 15.5)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(255)
    pdf.cell(18, 9, name[0], align="C")
    pdf.set_xy(15, 12)
    pdf.set_text_color(*colour)
    pdf.cell(0, 8, name.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(95)
    pdf.multi_cell(0, 4, "\n".join(address), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*colour)
    pdf.line(15, 36, 195, 36)
    pdf.set_xy(15, 42)
    pdf.set_text_color(20)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(120, 5, f"Ref: {ref}")
    pdf.cell(0, 5, f"Date: {date}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.multi_cell(0, 5, "\n".join(TO), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    return pdf


def para(pdf, text, bold=False, gap=3):
    pdf.set_font("Helvetica", "B" if bold else "", 10)
    pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(gap)


def table(pdf, rows, widths, shade):
    """A bordered table; the first row is the heading."""
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(255, 255, 255)
    with pdf.table(col_widths=widths, headings_style=FontFace(emphasis="BOLD", fill_color=shade)) as t:
        for row in rows:
            cells = t.row()
            for value in row:
                cells.cell(str(value))
    pdf.ln(4)


def finish(pdf, company, team, colour):
    """Sign-off and footer, then the PDF as bytes."""
    para(pdf, f"\nFor {company}", gap=8)
    para(pdf, f"Authorised Signatory\n{team}", bold=True)
    pdf.set_draw_color(*colour)
    pdf.line(15, 278, 195, 278)
    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", "I", 7)
    pdf.cell(0, 4, "This is a computer-generated letter and does not require a physical signature.", align="C")
    return bytes(pdf.output())


def suraksha(c):
    blue = (0, 82, 147)
    first, last = split_name(c.patient_name)
    pdf = letterhead("Suraksha Health Insurance Ltd.", blue, ["Tower B, Andheri East, Mumbai 400069",
                     "IRDAI Reg. No. 129 | Toll free: 1800 200 1234 | claims@suraksha-health.example"],
                     f"SHI/CS/2026/{c.claim_id[4:]}-{int(c.paid) % 9000 + 1000}", c.paid_on)
    para(pdf, f"Sub: Settlement of cashless claim - Claim No. {c.claim_id.replace('-', '')}", bold=True)
    para(pdf, "Dear Sir/Madam,\nWe have processed the above claim as per the terms and conditions of the policy. "
              "The settlement details are given below:")
    table(pdf, [["Particulars", "Details"], ["Claim No", c.claim_id.replace("-", "")],
                ["Patient", f"{last} {first}".strip().upper()], ["Amount claimed", f"{c.amount_claimed:.2f}"],
                ["Amount approved", f"{c.paid:.2f}"], ["Deduction", f"{c.amount_claimed - c.paid:.2f}"],
                ["Reason", c.reason or "-"]], (50, 130), (220, 232, 245))
    para(pdf, "The approved amount has been credited to your registered bank account by NEFT.")
    return finish(pdf, "Suraksha Health Insurance Ltd.", "Claims Settlement Department", blue)


def arogya(c):
    green = (0, 128, 96)
    name = c.patient_name.lower().replace("a", "aa", 1)  # typed by hand, with a typo
    pdf = letterhead("Arogya Plus TPA Services Pvt. Ltd.", green, ["Third Party Administrator | IRDAI Licence No. 018",
                     "B-14, Sector 18, Noida 201301 | Provider desk: 0120 455 7000"], f"APT/SA/{c.paid_on[5:7]}/{c.paid}", c.paid_on)
    para(pdf, "Sub: Settlement Advice", bold=True)
    para(pdf, f"Dear Sir/Madam,\nWe have processed the claim of {name} (admitted on {c.admission_date}). Bill amount Rs. "
              f"{inr(c.amount_claimed)}/- ; approved Rs. {inr(c.paid)}/-. Disallowance: {c.reason or 'NIL'}.")
    para(pdf, "The amount will be remitted to your registered bank account within 7 working days. "
              "For any clarification please contact our provider desk, quoting the reference above.")
    return finish(pdf, "Arogya Plus TPA Services Pvt. Ltd.", "Claims Team", green)
