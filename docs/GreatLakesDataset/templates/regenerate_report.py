"""
Regenerate final_report_gpt.pdf with fixed table formatting (no column overflow).
Hydrotreater Unit 200 — 10 CMLs, 2 lines.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "final_report_gpt.pdf")

PAGE_W, PAGE_H = letter
MARGIN = 0.65 * inch
USABLE_W = PAGE_W - 2 * MARGIN  # ~7.2 inches

# ── Styles ─────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
NAVY = colors.HexColor("#1a3c6e")
BLUE = colors.HexColor("#2a5a8e")
LIGHT_BG = colors.HexColor("#f0f4f8")
RED = colors.red
ORANGE = colors.HexColor("#CC6600")

def _add(name, **kw):
    if name in styles.byName:
        return
    styles.add(ParagraphStyle(name, **kw))

_add("CoverTitle", parent=styles["Title"], fontSize=20, spaceAfter=4, alignment=TA_CENTER)
_add("CoverSub", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER, spaceAfter=3)
_add("CoverInfo", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER, spaceAfter=2)
_add("SectionHead", parent=styles["Heading1"], fontSize=13, spaceBefore=16, spaceAfter=6, textColor=NAVY)
_add("SubHead", parent=styles["Heading2"], fontSize=11, spaceBefore=10, spaceAfter=5, textColor=BLUE)
_add("Body", parent=styles["Normal"], fontSize=9.5, leading=13, alignment=TA_JUSTIFY)
_add("Small", parent=styles["Normal"], fontSize=8.5, leading=11)
_add("TC", parent=styles["Normal"], fontSize=7.5, leading=9.5)
_add("TCB", parent=styles["Normal"], fontSize=7.5, leading=9.5, fontName="Helvetica-Bold")
_add("TCCrit", parent=styles["Normal"], fontSize=7.5, leading=9.5, fontName="Helvetica-Bold", textColor=RED)
_add("TCAlert", parent=styles["Normal"], fontSize=7.5, leading=9.5, fontName="Helvetica-Bold", textColor=ORANGE)
_add("Footer", parent=styles["Normal"], fontSize=7.5, alignment=TA_CENTER, textColor=colors.grey)
_add("Note", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#555555"))

S = styles

def P(text, style="TC"):
    return Paragraph(str(text), S[style])

def PB(text):
    return P(text, "TCB")

def hr():
    return HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=6, spaceBefore=3)

def make_table(headers, rows, col_widths=None, hdr_color=NAVY):
    hdr = [PB(h) for h in headers]
    data = [hdr] + rows
    w = col_widths or [USABLE_W / len(headers)] * len(headers)
    t = Table(data, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), hdr_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t

# ── Data ───────────────────────────────────────────────────────────────────
LINE1 = {
    "id": "200-L-1102", "service": "H2 recycle", "nps": '6"', "spec": "CS Sch 80",
    "cmls": [
        {"id": "CML-200-L-1102-01", "loc": "At low point drain", "comp": "Straight pipe",
         "nom": "0.237", "tmin": "0.154", "prev": "0.181", "cur": "0.146", "cat": "CRITICAL",
         "r1": "0.146", "r2": "0.152", "r3": "0.156", "r4": "0.158",
         "date": "2026-02-17", "time": "09:15", "op": "JP",
         "cr_short": "5.00", "cr_long": "4.54", "rl": "0.0", "next": "2026-08-22",
         "disp": "Isolate and repair/replace section; perform immediate engineering assessment. API 579 FFS evaluation recommended."},
        {"id": "CML-200-L-1102-02", "loc": "At low point drain", "comp": "Tee",
         "nom": "0.432", "tmin": "0.281", "prev": "0.346", "cur": "0.325", "cat": "Acceptable",
         "r1": "0.325", "r2": "0.330", "r3": "0.334", "r4": "0.341",
         "date": "2026-02-17", "time": "11:15", "op": "SM",
         "cr_short": "3.00", "cr_long": "3.09", "rl": "14.2", "next": "2031-02-21",
         "disp": "Maintain routine interval; no additional actions."},
        {"id": "CML-200-L-1102-03", "loc": "Near PSV 1102A", "comp": "Flange",
         "nom": "0.337", "tmin": "0.219", "prev": "0.262", "cur": "0.248", "cat": "Acceptable",
         "r1": "0.264", "r2": "0.266", "r3": "0.267", "r4": "0.248",
         "date": "2026-02-17", "time": "13:15", "op": "JP",
         "cr_short": "2.00", "cr_long": "3.90", "rl": "7.4", "next": "2029-11-03",
         "disp": "Maintain routine interval; no additional actions."},
        {"id": "CML-200-L-1102-04", "loc": "N. rack @ Bay 3", "comp": "Straight pipe",
         "nom": "0.432", "tmin": "0.281", "prev": "0.361", "cur": "0.337", "cat": "Acceptable",
         "r1": "0.356", "r2": "0.337", "r3": "0.344", "r4": "0.344",
         "date": "2026-02-18", "time": "09:15", "op": "SM",
         "cr_short": "3.43", "cr_long": "3.54", "rl": "15.8", "next": "2031-02-21",
         "disp": "Maintain routine interval; no additional actions."},
        {"id": "CML-200-L-1102-05", "loc": "At low point drain", "comp": "Reducer",
         "nom": "0.432", "tmin": "0.281", "prev": "0.388", "cur": "0.366", "cat": "Acceptable",
         "r1": "0.366", "r2": "0.380", "r3": "0.375", "r4": "0.383",
         "date": "2026-02-18", "time": "11:15", "op": "JP",
         "cr_short": "3.14", "cr_long": "5.81", "rl": "14.6", "next": "2031-02-21",
         "disp": "Maintain routine interval; no additional actions."},
    ]
}

LINE2 = {
    "id": "200-L-1148", "service": "Sour water", "nps": '4"', "spec": "CS Sch 40",
    "cmls": [
        {"id": "CML-200-L-1148-01", "loc": "Downstream of exchanger E-201", "comp": "Flange",
         "nom": "0.337", "tmin": "0.219", "prev": "0.290", "cur": "0.268", "cat": "Acceptable",
         "r1": "0.268", "r2": "0.271", "r3": "0.272", "r4": "0.268",
         "date": "2026-02-18", "time": "13:15", "op": "SM",
         "cr_short": "3.14", "cr_long": "5.45", "rl": "9.0", "next": "2030-08-22",
         "disp": "Maintain routine interval; no additional actions."},
        {"id": "CML-200-L-1148-02", "loc": "Near PSV 1102A", "comp": "Elbow 90\u00b0",
         "nom": "0.237", "tmin": "0.154", "prev": "0.292", "cur": "0.172", "cat": "Monitor",
         "r1": "0.172", "r2": "0.176", "r3": "0.180", "r4": "0.182",
         "date": "2026-02-19", "time": "09:15", "op": "JP",
         "cr_short": "17.13", "cr_long": "16.34", "rl": "1.1", "next": "2026-09-09",
         "disp": "Investigate corrosion mechanism; consider process review and add targeted CMLs. Engineering review if trend continues."},
        {"id": "CML-200-L-1148-03", "loc": "N. rack @ Bay 3", "comp": "Tee",
         "nom": "0.237", "tmin": "0.154", "prev": "0.174", "cur": "0.155", "cat": "Alert",
         "r1": "0.156", "r2": "0.155", "r3": "0.164", "r4": "0.161",
         "date": "2026-02-19", "time": "11:15", "op": "SM",
         "cr_short": "2.71", "cr_long": "5.72", "rl": "0.2", "next": "2026-08-22",
         "disp": "Plan repair or increase monitoring at next outage; validate thickness with follow-up UT."},
        {"id": "CML-200-L-1148-04", "loc": "Near PSV 1102A", "comp": "Elbow 90\u00b0",
         "nom": "0.188", "tmin": "0.122", "prev": "0.141", "cur": "0.129", "cat": "Alert",
         "r1": "0.142", "r2": "0.140", "r3": "0.145", "r4": "0.129",
         "date": "2026-02-19", "time": "13:15", "op": "JP",
         "cr_short": "1.71", "cr_long": "3.45", "rl": "2.0", "next": "2027-02-21",
         "disp": "Plan repair or increase monitoring at next outage; validate thickness with follow-up UT."},
        {"id": "CML-200-L-1148-05", "loc": "Near PSV 1102A", "comp": "Flange",
         "nom": "0.337", "tmin": "0.219", "prev": "0.306", "cur": "0.299", "cat": "Acceptable",
         "r1": "0.302", "r2": "0.299", "r3": "0.313", "r4": "0.308",
         "date": "2026-02-20", "time": "09:15", "op": "SM",
         "cr_short": "1.00", "cr_long": "2.09", "rl": "38.3", "next": "2031-02-21",
         "disp": "Maintain routine interval; no additional actions."},
    ]
}

LINES = [LINE1, LINE2]
ALL_CMLS = LINE1["cmls"] + LINE2["cmls"]
GAUGE_SN = "38DL-19-004821"

def cat_style(cat):
    if cat == "CRITICAL": return "TCCrit"
    if cat == "Alert": return "TCAlert"
    return "TC"

# ── Build ──────────────────────────────────────────────────────────────────
story = []

# ═══════════ COVER PAGE ═══════════
story.append(Spacer(1, 1.2 * inch))
story.append(Paragraph("GREAT LAKES CHEMICAL PROCESSING (GLCP)", S["CoverTitle"]))
story.append(Spacer(1, 0.15 * inch))
story.append(hr())
story.append(Spacer(1, 0.15 * inch))
story.append(Paragraph("FINAL INSPECTION REPORT", S["CoverTitle"]))
story.append(Paragraph("Ultrasonic Thickness Survey", S["CoverSub"]))
story.append(Paragraph("Hydrotreater Unit 200 \u2014 Pipe Racks and Pipe Bridge", S["CoverSub"]))
story.append(Spacer(1, 0.35 * inch))

cover_rows = [
    ["Report Number:", "UT-26-0217-200"],
    ["Revision:", "0"],
    ["Report Date:", "2026-03-05"],
    ["", ""],
    ["Client:", "Great Lakes Chemical Processing (GLCP)"],
    ["Site:", "GLCP \u2014 North Plant, Mississauga, Ontario"],
    ["Job / Work Order:", "GLCP-UT-2026-0217"],
    ["", ""],
    ["Survey Dates:", "2026-02-17 to 2026-02-21"],
    ["Method / Code Basis:", "UT Thickness (ASME V Article 5)"],
    ["Scope:", "10 CMLs across 2 piping lines"],
    ["", ""],
    ["Prepared By:", "UMA AI Inspection Intelligence (Sample Dataset)"],
    ["Contractor:", "UMA NDT Services Ltd."],
    ["Client Contact:", "A. Chen, Inspection Supervisor"],
]
ct = Table(cover_rows, colWidths=[1.8 * inch, 4.2 * inch])
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]))
story.append(ct)
story.append(Spacer(1, 0.4 * inch))
story.append(hr())
story.append(Spacer(1, 0.15 * inch))
story.append(Paragraph(
    "<i>Confidentiality: This sample report is generated from a synthetic example dataset for "
    "demonstration of report automation capabilities. Values and identifiers are illustrative.</i>",
    ParagraphStyle("Conf", parent=S["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
story.append(PageBreak())

# ═══════════ A. REPORT FRONT MATTER ═══════════
story.append(Paragraph("A. Report Front Matter", S["SectionHead"]))
story.append(hr())

story.append(Paragraph("1) Executive Summary", S["SubHead"]))
story.append(Paragraph(
    "This report documents an ultrasonic thickness (UT) survey completed on selected piping circuits "
    "in Hydrotreater Unit 200. A total of 10 corrosion monitoring locations (CMLs) across 2 lines were "
    "inspected between 2026-02-17 and 2026-02-21. Thickness readings were compared against nominal "
    "wall thickness and minimum required thickness (t-min) values to support integrity trending and "
    "inspection planning in accordance with the referenced codes and GLCP procedure.", S["Body"]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Key outcomes: <b>1 CML was classified as CRITICAL</b> (measured below t-min) and required immediate "
    "notification and disposition. <b>2 CMLs were classified as Alert</b> (measured below 110% of t-min). "
    "<b>1 CML was classified as Monitor</b> due to elevated short-term corrosion rate (&gt; 10 mpy). "
    "All other CMLs were classified as Acceptable.", S["Body"]))
story.append(Spacer(1, 10))

story.append(Paragraph("2) Scope of Work", S["SubHead"]))
scope_items = [
    "<b>Unit / Area:</b> Hydrotreater Unit 200 (Pipe Racks and Pipe Bridge)",
    "<b>Lines / Circuits:</b> 200-L-1102, 200-L-1148",
    "<b>CML Count:</b> 10 (5 per line)",
    "<b>Survey Dates:</b> 2026-02-17 to 2026-02-21",
    "<b>Method:</b> UT Thickness (ASME V Article 5)",
    "<b>Data Requirements:</b> Minimum of 4 readings per CML at approximately 90\u00b0 intervals; "
    "minimum value recorded per GLCP-NDT-001 Rev 3.",
]
for item in scope_items:
    story.append(Paragraph(item, S["Body"]))
    story.append(Spacer(1, 2))
story.append(Spacer(1, 8))

story.append(Paragraph("3) Reference Documents", S["SubHead"]))
refs = [
    "API 570 \u2014 Piping Inspection Code, in-service inspection, rating, repair, and alteration.",
    "API 574 \u2014 Inspection Practices for Piping System Components.",
    "ASME B31.3 \u2014 Process Piping (t-min basis).",
    "ASME Boiler &amp; Pressure Vessel Code Section V, Article 5 \u2014 Ultrasonic Examination Methods.",
    "GLCP-NDT-001 Rev 3 \u2014 UT Thickness Survey Procedure (company requirement).",
    "API 579-1/ASME FFS-1 \u2014 Fitness-For-Service (when disposition requires evaluation).",
]
for r in refs:
    story.append(Paragraph(f"\u2022 {r}", S["Small"]))
    story.append(Spacer(1, 2))

story.append(PageBreak())

# ═══════════ B. PERSONNEL & QUALIFICATIONS ═══════════
story.append(Paragraph("B. Personnel &amp; Qualifications", S["SectionHead"]))
story.append(hr())
story.append(Paragraph("5\u20138) Personnel, Certification, and Safety", S["SubHead"]))

pers_h = ["Name", "Role", "Cert Level", "Cert No.", "Employer", "Safety\nOrientation"]
pers_w = [1.0*inch, 1.0*inch, 0.8*inch, 1.0*inch, 1.2*inch, 0.9*inch]
pers_r = [
    [P("Jordan Patel"), P("Lead UT Inspector"), P("UT Level II"), P("UT-LL2-18427"),
     P("UMA NDT Services Ltd."), P("Completed (GLCP Site)")],
    [P("Sofia Martinez"), P("UT Inspector"), P("UT Level II"), P("UT-LL2-19311"),
     P("UMA NDT Services Ltd."), P("Completed (GLCP Site)")],
    [P("Ethan Okafor"), P("Assistant"), P("Trainee (under supervision)"), P("UT-TR-0774"),
     P("UMA NDT Services Ltd."), P("Completed (GLCP Site)")],
]
story.append(make_table(pers_h, pers_r, pers_w))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Certification records and training evidence are included in Appendix H-5. Minimum qualification "
    "requirements (UT Level II with documented experience) were met for personnel performing "
    "measurements; trainees worked under direct supervision.", S["Body"]))

story.append(PageBreak())

# ═══════════ C. EQUIPMENT & CALIBRATION ═══════════
story.append(Paragraph("C. Equipment &amp; Calibration", S["SectionHead"]))
story.append(hr())
story.append(Paragraph("9\u201314) Equipment Identification, Certificates, and Settings", S["SubHead"]))

eq_h = ["Item", "Model / Description", "Serial / ID", "Calibration Certificate"]
eq_w = [0.9*inch, 1.5*inch, 1.2*inch, 2.6*inch]
eq_r = [
    [P("UT gauge"), P("Olympus 38DL PLUS"), P("38DL-19-004821"),
     P("CAL-38DL-2025-11-033 (valid to 2026-11-30)")],
    [P("Transducer"), P("Dual element 5 MHz, 0.375 in"), P("DE-5M-0375-2219"),
     P("Included in gauge kit cert")],
    [P("Cal block"), P("IIW Type 1 (steel)"), P("IIW-STEEL-1142"),
     P("BLK-1142-2025-10-018 (traceable to NIST)")],
]
story.append(make_table(eq_h, eq_r, eq_w))
story.append(Spacer(1, 10))

story.append(Paragraph("<b>Material velocity settings used:</b>", S["Body"]))
story.append(Spacer(1, 4))
vel_h = ["Material", "Velocity Setting (in/\u03bcs)"]
vel_w = [3.5*inch, 2.0*inch]
vel_r = [
    [P("Carbon steel (CS)"), P("0.2330")],
    [P("Stainless steel (SS 316)"), P("0.2280")],
]
story.append(make_table(vel_h, vel_r, vel_w))
story.append(Spacer(1, 10))

story.append(Paragraph("<b>Daily calibration verification record</b> (tolerance \u00b10.002 in):", S["Body"]))
story.append(Spacer(1, 4))
cal_h = ["Date", "Time", "Operator", "Block\nThk (in)", "Reading 1", "Reading 2", "Reading 3", "Within\nTolerance"]
cal_w = [0.75*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.7*inch]
cal_data = [
    ("2026-02-17", "07:30", "JP", "0.500", "0.500", "0.500", "0.499", "Yes"),
    ("2026-02-18", "07:30", "SM", "0.500", "0.500", "0.500", "0.499", "Yes"),
    ("2026-02-19", "07:30", "JP", "0.500", "0.499", "0.501", "0.501", "Yes"),
    ("2026-02-20", "07:30", "SM", "0.500", "0.501", "0.499", "0.501", "Yes"),
    ("2026-02-21", "07:30", "JP", "0.500", "0.501", "0.501", "0.500", "Yes"),
]
cal_r = [[P(c) for c in row] for row in cal_data]
story.append(make_table(cal_h, cal_r, cal_w))

story.append(PageBreak())

# ═══════════ D. INSPECTION RESULTS ═══════════
story.append(Paragraph("D. Inspection Results \u2014 Data Tables", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "15\u201322) UT thickness results are tabulated by line and CML. For each CML, a minimum of "
    "four (4) readings were collected at approximately 90\u00b0 intervals. The minimum reading is "
    "recorded as the controlling thickness for trending and acceptance.", S["Body"]))
story.append(Spacer(1, 8))

# Results table per line
res_h = ["CML", "Location", "Comp.", "Nom.\n(in)", "t-min\n(in)", "Prev\n2019", "Current\nMin (in)", "Category"]
res_w = [1.15*inch, 1.45*inch, 0.7*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.6*inch, 0.7*inch]

# Detail readings table
det_h = ["CML", "R1 (in)", "R2 (in)", "R3 (in)", "R4 (in)", "Date", "Time", "Op.", "Gauge S/N"]
det_w = [1.15*inch, 0.55*inch, 0.55*inch, 0.55*inch, 0.55*inch, 0.8*inch, 0.45*inch, 0.4*inch, 1.0*inch]

for line in LINES:
    story.append(Paragraph(
        f"<b>Line / Circuit: {line['id']}</b> \u2014 {line['service']} | NPS {line['nps']} | {line['spec']}",
        S["Body"]))
    story.append(Spacer(1, 4))

    rows = []
    for c in line["cmls"]:
        cs = cat_style(c["cat"])
        rows.append([
            P(c["id"]), P(c["loc"]), P(c["comp"]),
            P(c["nom"]), P(c["tmin"]), P(c["prev"]),
            P(c["cur"], cs), P(c["cat"], cs),
        ])
    story.append(make_table(res_h, rows, res_w))
    story.append(Spacer(1, 6))

    det_rows = []
    for c in line["cmls"]:
        det_rows.append([
            P(c["id"]), P(c["r1"]), P(c["r2"]), P(c["r3"]), P(c["r4"]),
            P(c["date"]), P(c["time"]), P(c["op"]), P(GAUGE_SN),
        ])
    story.append(make_table(det_h, det_rows, det_w))
    story.append(Spacer(1, 12))

story.append(PageBreak())

# ═══════════ E. TRENDING & CORROSION ANALYSIS ═══════════
story.append(Paragraph("E. Trending &amp; Corrosion Analysis", S["SectionHead"]))
story.append(hr())
story.append(Paragraph("23\u201327) Corrosion Rates, Remaining Life, and Next Inspection", S["SubHead"]))
story.append(Paragraph(
    "Corrosion rates were calculated using historical thickness data (2015 and 2019 surveys) and "
    "the current survey (2026). Rates are reported in mils per year (mpy), where 1 mil = 0.001 in.",
    S["Body"]))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Definitions (API 570 \u00a77.1 basis):</b>", S["Body"]))
defs = [
    "Short-term corrosion rate (mpy) = (T<sub>2019</sub> \u2212 T<sub>2026</sub>) \u00d7 1000 / \u0394t<sub>2019\u20132026</sub>",
    "Long-term corrosion rate (mpy) = (T<sub>2015</sub> \u2212 T<sub>2026</sub>) \u00d7 1000 / \u0394t<sub>2015\u20132026</sub>",
    "Remaining life (yr) = (T<sub>2026</sub> \u2212 t-min) / (CR<sub>used</sub> / 1000)",
]
for d in defs:
    story.append(Paragraph(f"\u2022 {d}", S["Small"]))
    story.append(Spacer(1, 1))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Recommended next inspection date (API 570 \u00a76): interval set to one-half of remaining life, "
    "bounded to a minimum of 6 months and maximum of 5 years.", S["Body"]))
story.append(Spacer(1, 6))

# Split the trending table into two sub-tables to avoid overflow
tr_h = ["Line", "CML", "t-min\n(in)", "Current\n(in)", "Prev\n2019", "CR Short\n(mpy)",
        "CR Long\n(mpy)", "Rem.\nLife (yr)", "Next\nInspection"]
tr_w = [0.7*inch, 1.1*inch, 0.45*inch, 0.5*inch, 0.45*inch, 0.6*inch, 0.55*inch, 0.55*inch, 0.7*inch]
tr_rows = []
for c in ALL_CMLS:
    cs = cat_style(c["cat"])
    tr_rows.append([
        P(c["id"].split("-")[1] + "-" + c["id"].split("-")[2]),  # line part
        P(c["id"]),
        P(c["tmin"]), P(c["cur"], cs), P(c["prev"]),
        P(c["cr_short"]), P(c["cr_long"]),
        P(c["rl"], cs), P(c["next"], cs),
    ])
# Actually use the line["id"] for the line column
tr_rows2 = []
for line in LINES:
    for c in line["cmls"]:
        cs = cat_style(c["cat"])
        tr_rows2.append([
            P(line["id"]), P(c["id"]),
            P(c["tmin"]), P(c["cur"], cs), P(c["prev"]),
            P(c["cr_short"]), P(c["cr_long"]),
            P(c["rl"], cs), P(c["next"], cs),
        ])
story.append(make_table(tr_h, tr_rows2, tr_w))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<i>Note: Long-term corrosion rates were computed using 2015 historical thickness values; "
    "raw historical inputs are retained in the dataset.</i>", S["Note"]))

story.append(PageBreak())

# ═══════════ F. FINDINGS & DISPOSITIONS ═══════════
story.append(Paragraph("F. Findings &amp; Dispositions", S["SectionHead"]))
story.append(hr())
story.append(Paragraph("28\u201334) Categorized Findings and Required Actions", S["SubHead"]))
story.append(Paragraph(
    "Findings are categorized per GLCP-NDT-001 Rev 3 criteria and code expectations. Supporting "
    "evidence (photos, notifications, and notes) is referenced in the Appendices.", S["Body"]))
story.append(Spacer(1, 6))

# Sort: CRITICAL first, then Alert, Monitor, Acceptable
cat_order = {"CRITICAL": 0, "Alert": 1, "Monitor": 2, "Acceptable": 3}
sorted_cmls = sorted(ALL_CMLS, key=lambda x: cat_order.get(x["cat"], 99))

fd_h = ["Category", "CML", "Line", "Current\nMin (in)", "t-min\n(in)", "Basis", "Disposition / Notes"]
fd_w = [0.65*inch, 1.05*inch, 0.7*inch, 0.55*inch, 0.45*inch, 0.7*inch, 2.1*inch]
fd_rows = []
for c_data in sorted_cmls:
    # find line
    ln = ""
    for line in LINES:
        if c_data in line["cmls"]:
            ln = line["id"]
            break
    cs = cat_style(c_data["cat"])
    basis_map = {
        "CRITICAL": "Below t-min",
        "Alert": "Below 110% t-min",
        "Monitor": "CR > 10 mpy",
        "Acceptable": "Meets criteria",
    }
    disp = c_data["disp"]
    if c_data["cat"] == "Acceptable":
        disp = "No action required beyond routine inspection interval."
    fd_rows.append([
        P(c_data["cat"], cs), P(c_data["id"]), P(ln),
        P(c_data["cur"], cs), P(c_data["tmin"]),
        P(basis_map.get(c_data["cat"], "")),
        P(disp),
    ])
story.append(make_table(fd_h, fd_rows, fd_w))

story.append(PageBreak())

# ═══════════ G. RECOMMENDATIONS ═══════════
story.append(Paragraph("G. Recommendations", S["SectionHead"]))
story.append(hr())
story.append(Paragraph("35\u201338) Recommended Actions and Intervals", S["SubHead"]))
story.append(Paragraph(
    "Recommendations are based on measured thickness, calculated corrosion rates, and observed field "
    "conditions. Engineering remains responsible for final determination of inspection intervals "
    "and dispositions.", S["Body"]))
story.append(Spacer(1, 6))

rec_h = ["Line", "CML", "Cat.", "CR Short\n(mpy)", "Rem. Life\n(yr)", "Rec.\nInterval", "Next\nDate",
         "Recommendation / Referral"]
rec_w = [0.6*inch, 0.95*inch, 0.55*inch, 0.5*inch, 0.5*inch, 0.45*inch, 0.6*inch, 2.05*inch]
rec_rows = []
for line in LINES:
    for c in line["cmls"]:
        cs = cat_style(c["cat"])
        # Determine interval
        try:
            rl = float(c["rl"])
            if rl <= 0:
                interval = "0.5 yr"
            else:
                iv = rl / 2.0
                if iv > 5: iv = 5.0
                if iv < 0.5: iv = 0.5
                interval = f"{iv:.1f} yr"
        except ValueError:
            interval = "TBD"
        rec_rows.append([
            P(line["id"]), P(c["id"]), P(c["cat"], cs),
            P(c["cr_short"]), P(c["rl"], cs),
            P(interval), P(c["next"], cs),
            P(c["disp"]),
        ])
story.append(make_table(rec_h, rec_rows, rec_w))

story.append(PageBreak())

# ═══════════ H. APPENDICES ═══════════
story.append(Paragraph("H. Appendices", S["SectionHead"]))
story.append(hr())
story.append(Paragraph("39\u201347) Supporting Records and Photo Log", S["SubHead"]))
story.append(Paragraph(
    "Appendices below provide supporting evidence and records referenced throughout the report. "
    "For this sample report, photographs and certificates are represented as placeholders.", S["Body"]))
story.append(Spacer(1, 6))

app_h = ["Appendix", "Description", "Status"]
app_w = [0.8*inch, 3.8*inch, 1.5*inch]
app_data = [
    ("H-1", "Raw UT data export (gauge CSV)", "Included (placeholder)"),
    ("H-2", "Photographs \u2014 CML location (each CML)", "Included (placeholder)"),
    ("H-3", "Photographs \u2014 gauge display (CRITICAL and Alert)", "Included (placeholder)"),
    ("H-4", "Isometric drawings with CML locations marked", "Included (placeholder)"),
    ("H-5", "Personnel certification records (UT)", "Included (placeholder)"),
    ("H-6", "Equipment calibration certificates (traceable to NIST)", "Included (placeholder)"),
    ("H-7", "Photographs \u2014 surface condition / anomalies", "Included (placeholder)"),
    ("H-8", "Photographs \u2014 inaccessible locations (if any)", "Included (placeholder)"),
    ("H-9", "Photographs \u2014 daily calibration setup", "Included (placeholder)"),
]
app_r = [[P(a), P(b), P(c)] for a, b, c in app_data]
story.append(make_table(app_h, app_r, app_w))
story.append(Spacer(1, 12))

story.append(Paragraph("<b>Photo log (sample):</b>", S["Body"]))
story.append(Spacer(1, 4))
ph_h = ["Photo ID", "CML", "Photo Type", "Description / Notes"]
ph_w = [0.65*inch, 1.1*inch, 0.85*inch, 3.6*inch]
ph_data = [
    ("P-001", "CML-200-L-1102-01", "CML Location", "Wide shot and close-up of At low point drain (tagging visible)."),
    ("P-002", "CML-200-L-1102-01", "Gauge Display", "Gauge screen showing min thickness 0.146 in."),
    ("P-003", "CML-200-L-1102-02", "CML Location", "Wide shot and close-up of At low point drain (tagging visible)."),
    ("P-004", "CML-200-L-1102-03", "CML Location", "Wide shot and close-up of Near PSV 1102A (tagging visible)."),
    ("P-005", "CML-200-L-1102-04", "CML Location", "Wide shot and close-up of N. rack @ Bay 3 (tagging visible)."),
    ("P-006", "CML-200-L-1102-05", "CML Location", "Wide shot and close-up of At low point drain (tagging visible)."),
    ("P-007", "CML-200-L-1148-01", "CML Location", "Wide shot and close-up of Downstream of exchanger E-201."),
    ("P-008", "CML-200-L-1148-02", "CML Location", "Wide shot and close-up of Near PSV 1102A (tagging visible)."),
    ("P-009", "CML-200-L-1148-03", "CML Location", "Wide shot and close-up of N. rack @ Bay 3 (tagging visible)."),
    ("P-010", "CML-200-L-1148-03", "Gauge Display", "Gauge screen showing min thickness 0.155 in."),
    ("P-011", "CML-200-L-1148-04", "CML Location", "Wide shot and close-up of Near PSV 1102A (tagging visible)."),
    ("P-012", "CML-200-L-1148-04", "Gauge Display", "Gauge screen showing min thickness 0.129 in."),
    ("P-013", "CML-200-L-1148-05", "CML Location", "Wide shot and close-up of Near PSV 1102A (tagging visible)."),
]
ph_r = [[P(a), P(b), P(c), P(d)] for a, b, c, d in ph_data]
story.append(make_table(ph_h, ph_r, ph_w))
story.append(Spacer(1, 12))

# Photo placeholders
story.append(Paragraph("<b>Sample photo placeholders (for illustration):</b>", S["Body"]))
story.append(Spacer(1, 6))

placeholders = [
    ("CML Location Photo", "[Insert field photo here]"),
    ("Gauge Display Photo", "[Insert gauge screen photo here]"),
    ("Calibration Setup Photo", "[Insert daily calibration photo here]"),
    ("Marked Isometric Excerpt", "[Insert marked-up isometric here]"),
]
for title, placeholder in placeholders:
    ph_box = Table(
        [[Paragraph(f"<b>Placeholder: {title}</b>", S["Body"])],
         [Paragraph(placeholder, ParagraphStyle("ph", parent=S["Normal"], fontSize=10,
                    alignment=TA_CENTER, textColor=colors.grey))]],
        colWidths=[4.0 * inch]
    )
    ph_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(ph_box)
    story.append(Spacer(1, 6))

# ── Footer / page numbers ─────────────────────────────────────────────────
HEADER_TEXT = ("Great Lakes Chemical Processing (GLCP)  |  Final Inspection Report\n"
               "Report: UT-26-0217-200 Rev 0\n"
               "Survey dates: 2026-02-17 to 2026-02-21  |  Procedure: GLCP-NDT-001 Rev 3")

def header_footer(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    y = PAGE_H - 0.4 * inch
    for line_text in HEADER_TEXT.split("\n"):
        canvas.drawString(MARGIN, y, line_text)
        y -= 9
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, y - 2, PAGE_W - MARGIN, y - 2)
    # Footer
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(PAGE_W / 2, 0.4 * inch, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=letter,
    topMargin=0.9 * inch,
    bottomMargin=0.7 * inch,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    title="UT-26-0217-200 Rev 0 — Hydrotreater Unit 200 UT Survey Final Report",
    author="UMA AI Inspection Intelligence",
    subject="Ultrasonic Thickness Survey — GLCP — Hydrotreater Unit 200",
)

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"Report generated: {OUTPUT_PATH}")
