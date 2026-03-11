"""
Generate sample Final Inspection Report PDF for Great Lakes Chemical Processing
Amine Treating Unit (ATU-100) UT Thickness Survey — November 2024
Report Number: PNDE-RPT-20241025-031-R0
"""

import csv
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "PNDE-RPT-20241025-031-R0.pdf")

# ── Load CSV data ──────────────────────────────────────────────────────────
def load_csv(filename):
    path = os.path.join(BASE_DIR, "data", filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

master = load_csv("master_cml_list.csv")

# ── Styles ─────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("CoverTitle", parent=styles["Title"], fontSize=22, spaceAfter=6, alignment=TA_CENTER))
styles.add(ParagraphStyle("CoverSub", parent=styles["Normal"], fontSize=14, alignment=TA_CENTER, spaceAfter=4))
styles.add(ParagraphStyle("CoverInfo", parent=styles["Normal"], fontSize=11, alignment=TA_CENTER, spaceAfter=2))
styles.add(ParagraphStyle("SectionHead", parent=styles["Heading1"], fontSize=14, spaceBefore=18, spaceAfter=8,
                           textColor=colors.HexColor("#1a3c6e")))
styles.add(ParagraphStyle("SubHead", parent=styles["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=6,
                           textColor=colors.HexColor("#2a5a8e")))
styles.add(ParagraphStyle("BodyJ", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("SmallBody", parent=styles["Normal"], fontSize=9, leading=12))
styles.add(ParagraphStyle("TableCell", parent=styles["Normal"], fontSize=7.5, leading=9))
styles.add(ParagraphStyle("TableCellBold", parent=styles["Normal"], fontSize=7.5, leading=9, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))
styles.add(ParagraphStyle("CriticalCell", parent=styles["Normal"], fontSize=7.5, leading=9,
                           fontName="Helvetica-Bold", textColor=colors.red))
styles.add(ParagraphStyle("AlertCell", parent=styles["Normal"], fontSize=7.5, leading=9,
                           fontName="Helvetica-Bold", textColor=colors.HexColor("#CC6600")))

S = styles  # alias

def hr():
    return HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3c6e"), spaceAfter=8, spaceBefore=4)

def make_table(headers, rows, col_widths=None, header_color=colors.HexColor("#1a3c6e")):
    hdr = [Paragraph(f"<b>{h}</b>", S["TableCell"]) for h in headers]
    data = [hdr] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

# ── Derive calculations ───────────────────────────────────────────────────
lines_data = {}
for r in master:
    ln = r["line_number"]
    if ln not in lines_data:
        lines_data[ln] = {"service": r["service"], "size": r["pipe_size_in"],
                          "material": r["material"], "cmls": []}
    lines_data[ln]["cmls"].append(r)

critical = [r for r in master if r["status"] == "CRITICAL"]
alert = [r for r in master if r["status"] == "Alert"]
monitor = [r for r in master if r["status"] == "Monitor"]
acceptable = [r for r in master if r["status"] == "Acceptable"]
inaccessible = [r for r in master if r["status"] == "Inaccessible"]

def remaining_life(reading_2024, tmin, rate_mpy):
    try:
        t = float(reading_2024)
        tm = float(tmin)
        cr = float(rate_mpy)
        if cr <= 0:
            return "N/A"
        rl = (t - tm) / (cr / 1000.0)
        return f"{rl:.1f}"
    except (ValueError, ZeroDivisionError, TypeError):
        return "N/A"

def next_inspection(rl_str):
    try:
        rl = float(rl_str)
        if rl <= 0:
            return "Immediate"
        interval = rl / 2.0
        if interval > 10:
            interval = 10
        if interval < 0.5:
            interval = 0.5
        next_date = datetime(2024, 11, 7) + timedelta(days=int(interval * 365.25))
        return next_date.strftime("%b %Y")
    except (ValueError, TypeError):
        return "TBD"

# ── Build document ─────────────────────────────────────────────────────────
story = []

# ═══════════ COVER PAGE ═══════════
story.append(Spacer(1, 1.5 * inch))
story.append(Paragraph("PRECISION NDE SERVICES INC.", S["CoverTitle"]))
story.append(Spacer(1, 0.3 * inch))
story.append(hr())
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("FINAL INSPECTION REPORT", S["CoverTitle"]))
story.append(Paragraph("Ultrasonic Thickness Survey", S["CoverSub"]))
story.append(Spacer(1, 0.4 * inch))

cover_info = [
    ["Report Number:", "PNDE-RPT-20241025-031-R0"],
    ["Revision:", "0 (Original Issue)"],
    ["Date:", "November 14, 2024"],
    ["", ""],
    ["Client:", "Great Lakes Chemical Processing (GLCP)"],
    ["Location:", "Hamilton Plant, Ontario"],
    ["Unit:", "Amine Treating Unit (ATU-100)"],
    ["Work Order:", "WO-20241025-031"],
    ["", ""],
    ["Scope:", "150 Condition Monitoring Locations (CMLs)"],
    ["", "18 piping lines"],
    ["Survey Dates:", "November 4–7, 2024"],
]
ct = Table(cover_info, colWidths=[2.2 * inch, 4.0 * inch])
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 11),
    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(ct)

story.append(Spacer(1, 0.6 * inch))
story.append(hr())
story.append(Spacer(1, 0.3 * inch))

approval_data = [
    [Paragraph("<b>Role</b>", S["TableCell"]), Paragraph("<b>Name</b>", S["TableCell"]),
     Paragraph("<b>Signature</b>", S["TableCell"]), Paragraph("<b>Date</b>", S["TableCell"])],
    ["Prepared By:", "Marcus Chen, UT Level II", "_________________", "Nov 12, 2024"],
    ["Reviewed By:", "Sarah Thompson, UT Level II", "_________________", "Nov 13, 2024"],
    ["Approved By:", "David Park, UT Level III", "_________________", "Nov 14, 2024"],
]
at = Table(approval_data, colWidths=[1.4 * inch, 2.2 * inch, 1.6 * inch, 1.2 * inch])
at.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(at)

story.append(Spacer(1, 0.5 * inch))
story.append(Paragraph("CONFIDENTIAL — For authorized use by Great Lakes Chemical Processing only.",
                        ParagraphStyle("Conf", parent=S["Normal"], fontSize=9, alignment=TA_CENTER,
                                       textColor=colors.red, fontName="Helvetica-Bold")))

story.append(PageBreak())

# ═══════════ TABLE OF CONTENTS ═══════════
story.append(Paragraph("TABLE OF CONTENTS", S["SectionHead"]))
story.append(hr())
toc_items = [
    ("1.0", "Executive Summary", "3"),
    ("2.0", "Scope of Work", "4"),
    ("3.0", "Reference Documents", "5"),
    ("4.0", "Personnel & Qualifications", "6"),
    ("5.0", "Equipment & Calibration", "7"),
    ("6.0", "Inspection Results — Data Tables", "9"),
    ("7.0", "Trending & Corrosion Analysis", "16"),
    ("8.0", "Findings & Dispositions", "18"),
    ("9.0", "Recommendations", "21"),
    ("Appendix A", "Raw Data (Gauge Data Exports)", "23"),
    ("Appendix B", "Photograph Log", "24"),
    ("Appendix C", "Personnel Certification Records", "26"),
    ("Appendix D", "Equipment Calibration Certificates", "27"),
    ("Appendix E", "Isometric Drawings with CML Locations", "28"),
]
for num, title, pg in toc_items:
    story.append(Paragraph(f"<b>{num}</b>&nbsp;&nbsp;&nbsp;&nbsp;{title}"
                           f"{'.' * max(1, 70 - len(num) - len(title))}{pg}", S["SmallBody"]))
    story.append(Spacer(1, 3))

story.append(PageBreak())

# ═══════════ 1.0 EXECUTIVE SUMMARY ═══════════
story.append(Paragraph("1.0 EXECUTIVE SUMMARY", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "Precision NDE Services Inc. (PNDE) performed an ultrasonic thickness (UT) survey of the "
    "Amine Treating Unit (ATU-100) piping at the Great Lakes Chemical Processing (GLCP) Hamilton "
    "Plant, Ontario, from November 4 through November 7, 2024. The survey encompassed 150 "
    "Condition Monitoring Locations (CMLs) distributed across 18 piping lines in sour gas, "
    "treated gas, lean amine, rich amine, regenerator overhead, reflux, steam, and cooling water "
    "services.", S["BodyJ"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    f"Of the 150 CMLs in scope, 148 were successfully inspected and 2 were documented as "
    f"inaccessible. The survey identified <b>{len(critical)} CRITICAL findings</b> (readings below "
    f"minimum required thickness), <b>{len(alert)} Alert findings</b> (readings approaching t-min), "
    f"and <b>{len(monitor)} Monitor conditions</b> (elevated corrosion rates exceeding 10 mpy). "
    f"The remaining {len(acceptable)} CMLs were classified as Acceptable.", S["BodyJ"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "The most significant finding was at CML 4-RA-101-06 (4\" Rich Amine line, 90° elbow near "
    "T-102 Regenerator) where a measured thickness of 0.142\" was recorded — below the minimum "
    "required thickness of 0.150\". GLCP Inspection Coordinator Jennifer Walsh was immediately "
    "notified on-site, and a Fitness-for-Service (FFS) evaluation per API 579 has been initiated. "
    "A second CRITICAL finding at CML 6-RA-103-11 (6\" Rich Amine Header weldolet) measured "
    "0.168\" against a t-min of 0.180\", indicating a localized thin area.", S["BodyJ"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Rich amine and regenerator overhead services exhibited the highest corrosion rates, consistent "
    "with the expected degradation mechanisms for amine treating systems (acid gas loading, amine "
    "degradation products). The cooling water line 3-CW-101 exhibited an anomalous condition where "
    "three CMLs returned readings exceeding the nominal wall thickness, suggesting internal scale "
    "deposits rather than metal loss. Internal inspection during the next turnaround is recommended.", S["BodyJ"]))
story.append(Spacer(1, 8))

# Summary stats table
summary_data = [
    ["Total CMLs in Scope", "150"],
    ["CMLs Inspected", "148"],
    ["Inaccessible", "2"],
    ["CRITICAL (below t-min)", str(len(critical))],
    ["Alert (within 110% of t-min)", str(len(alert))],
    ["Monitor (rate > 10 mpy)", str(len(monitor))],
    ["Acceptable", str(len(acceptable))],
]
summary_rows = [[Paragraph(r[0], S["TableCell"]), Paragraph(f"<b>{r[1]}</b>", S["TableCell"])]
                 for r in summary_data]
story.append(make_table(["Category", "Count"], summary_rows, col_widths=[4.0 * inch, 1.5 * inch]))

story.append(PageBreak())

# ═══════════ 2.0 SCOPE OF WORK ═══════════
story.append(Paragraph("2.0 SCOPE OF WORK", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "The scope of work was defined by Client Request for Quotation GLCP-RFQ-2024-089, dated "
    "September 15, 2024. The survey covered the following:", S["BodyJ"]))
story.append(Spacer(1, 6))

scope_headers = ["Line Number", "Service", "Size (in)", "Material", "Schedule", "CML Count"]
scope_rows = []
for ln in sorted(lines_data.keys()):
    d = lines_data[ln]
    cmls = d["cmls"]
    sched = cmls[0]["schedule"]
    scope_rows.append([
        Paragraph(ln, S["TableCell"]),
        Paragraph(d["service"], S["TableCell"]),
        Paragraph(d["size"], S["TableCell"]),
        Paragraph(d["material"], S["TableCell"]),
        Paragraph(str(sched), S["TableCell"]),
        Paragraph(str(len(cmls)), S["TableCell"]),
    ])
scope_rows.append([
    Paragraph("<b>TOTAL</b>", S["TableCellBold"]), "", "", "", "",
    Paragraph(f"<b>{len(master)}</b>", S["TableCellBold"]),
])
story.append(make_table(scope_headers, scope_rows,
                         col_widths=[1.1*inch, 1.3*inch, 0.6*inch, 1.0*inch, 0.7*inch, 0.8*inch]))
story.append(Spacer(1, 10))
story.append(Paragraph("<b>Survey Dates:</b> November 4–7, 2024 (4 working days)", S["BodyJ"]))
story.append(Paragraph("<b>Previous Survey:</b> October 15–17, 2019 (baseline data for trending)", S["BodyJ"]))

story.append(PageBreak())

# ═══════════ 3.0 REFERENCE DOCUMENTS ═══════════
story.append(Paragraph("3.0 REFERENCE DOCUMENTS", S["SectionHead"]))
story.append(hr())

ref_docs = [
    ["API 570", "Piping Inspection Code: In-Service Inspection, Rating, Repair, and Alteration of "
     "Piping Systems, 4th Edition, February 2016"],
    ["API 574", "Inspection Practices for Piping System Components, 4th Edition, November 2016"],
    ["ASME B31.3", "Process Piping, 2022 Edition"],
    ["ASME Section V", "Nondestructive Examination, Article 5 — Ultrasonic Examination Methods for "
     "Materials, 2023 Edition"],
    ["API 579-1/ASME FFS-1", "Fitness-For-Service, 3rd Edition, June 2016"],
    ["ASNT SNT-TC-1A", "Personnel Qualification and Certification in Nondestructive Testing, 2020 Edition"],
    ["GLCP-NDT-001 Rev 3", "Great Lakes Chemical Processing — Nondestructive Testing Requirements "
     "for Piping Systems, Revision 3, January 2023"],
    ["GLCP-RFQ-2024-089", "Request for Quotation — ATU-100 Piping UT Survey, September 15, 2024"],
    ["PNDE-PROC-UT-005 Rev 7", "Precision NDE Services — Ultrasonic Thickness Measurement Procedure, "
     "Revision 7, March 2024"],
    ["PNDE-JSA-20241025-031", "Job Safety Analysis — ATU-100 UT Survey, October 25, 2024"],
]
for code, desc in ref_docs:
    story.append(Paragraph(f"<b>{code}</b> — {desc}", S["SmallBody"]))
    story.append(Spacer(1, 4))

story.append(PageBreak())

# ═══════════ 4.0 PERSONNEL & QUALIFICATIONS ═══════════
story.append(Paragraph("4.0 PERSONNEL & QUALIFICATIONS", S["SectionHead"]))
story.append(hr())

story.append(Paragraph("4.1 Inspection Personnel", S["SubHead"]))
pers_headers = ["Name", "Role", "Cert Level", "Cert Number", "Expiry", "Gauge Assigned"]
pers_rows = [
    [Paragraph("Marcus Chen", S["TableCell"]), Paragraph("Lead Inspector", S["TableCell"]),
     Paragraph("UT Level II", S["TableCell"]), Paragraph("PNDE-UT2-0847", S["TableCell"]),
     Paragraph("Mar 15, 2026", S["TableCell"]), Paragraph("38DL Plus S/N 2847193", S["TableCell"])],
    [Paragraph("Sarah Thompson", S["TableCell"]), Paragraph("Inspector", S["TableCell"]),
     Paragraph("UT Level II", S["TableCell"]), Paragraph("PNDE-UT2-1203", S["TableCell"]),
     Paragraph("Aug 22, 2025", S["TableCell"]), Paragraph("38DL Plus S/N 2901456", S["TableCell"])],
    [Paragraph("David Park", S["TableCell"]), Paragraph("Project Manager / Approver", S["TableCell"]),
     Paragraph("UT Level III", S["TableCell"]), Paragraph("PNDE-UT3-0215", S["TableCell"]),
     Paragraph("Jan 10, 2027", S["TableCell"]), Paragraph("N/A (office review)", S["TableCell"])],
]
story.append(make_table(pers_headers, pers_rows,
                         col_widths=[1.1*inch, 1.2*inch, 0.8*inch, 1.1*inch, 0.9*inch, 1.4*inch]))
story.append(Spacer(1, 10))

story.append(Paragraph("4.2 Qualification Confirmation", S["SubHead"]))
story.append(Paragraph(
    "All field inspectors hold a minimum UT Level II certification in accordance with ASNT SNT-TC-1A "
    "and employer written practice, as required by GLCP-NDT-001 §3.2. Both Marcus Chen and Sarah "
    "Thompson meet the minimum experience requirements of 1,680 hours of UT inspection experience. "
    "Certification records are appended in Appendix C.", S["BodyJ"]))
story.append(Spacer(1, 8))

story.append(Paragraph("4.3 Site Safety Orientation", S["SubHead"]))
story.append(Paragraph(
    "All personnel completed the GLCP Hamilton Plant site-specific safety orientation on November 1, "
    "2024, conducted by Mike Sullivan (GLCP Safety Coordinator). Daily tailgate safety meetings were "
    "conducted each morning prior to commencing work, in accordance with GLCP-NDT-001 §3.3 and "
    "Job Safety Analysis PNDE-JSA-20241025-031. H₂S personal monitors were issued and tested daily. "
    "No safety incidents occurred during the survey period.", S["BodyJ"]))

story.append(PageBreak())

# ═══════════ 5.0 EQUIPMENT & CALIBRATION ═══════════
story.append(Paragraph("5.0 EQUIPMENT & CALIBRATION", S["SectionHead"]))
story.append(hr())

story.append(Paragraph("5.1 Ultrasonic Thickness Gauges", S["SubHead"]))
equip_headers = ["Item", "Description", "Serial Number", "Cal Cert No.", "Cal Due Date"]
equip_rows = [
    [Paragraph("UT Gauge 1", S["TableCell"]), Paragraph("Olympus 38DL Plus", S["TableCell"]),
     Paragraph("2847193", S["TableCell"]), Paragraph("PNDE-CAL-2024-0847", S["TableCell"]),
     Paragraph("May 15, 2025", S["TableCell"])],
    [Paragraph("UT Gauge 2", S["TableCell"]), Paragraph("Olympus 38DL Plus", S["TableCell"]),
     Paragraph("2901456", S["TableCell"]), Paragraph("PNDE-CAL-2024-1203", S["TableCell"]),
     Paragraph("Jul 22, 2025", S["TableCell"])],
]
story.append(make_table(equip_headers, equip_rows,
                         col_widths=[0.9*inch, 1.3*inch, 1.0*inch, 1.5*inch, 1.0*inch]))
story.append(Spacer(1, 10))

story.append(Paragraph("5.2 Transducers", S["SubHead"]))
trans_headers = ["Transducer", "Type", "Frequency", "Diameter", "Serial Number"]
trans_rows = [
    [Paragraph("Probe 1", S["TableCell"]), Paragraph("D790-SM, Dual Element", S["TableCell"]),
     Paragraph("5 MHz", S["TableCell"]), Paragraph("0.375\"", S["TableCell"]),
     Paragraph("D790-2847-A", S["TableCell"])],
    [Paragraph("Probe 2", S["TableCell"]), Paragraph("D790-SM, Dual Element", S["TableCell"]),
     Paragraph("5 MHz", S["TableCell"]), Paragraph("0.375\"", S["TableCell"]),
     Paragraph("D790-2901-A", S["TableCell"])],
]
story.append(make_table(trans_headers, trans_rows,
                         col_widths=[0.9*inch, 1.5*inch, 0.9*inch, 0.8*inch, 1.1*inch]))
story.append(Spacer(1, 10))

story.append(Paragraph("5.3 Calibration Block", S["SubHead"]))
story.append(Paragraph(
    "<b>Calibration Standard:</b> PNDE-CS-001, 4-step carbon steel block (0.100\", 0.200\", "
    "0.400\", 0.800\"), NIST-traceable. Certificate Number: PNDE-CAL-BLK-2024-001, "
    "expiry June 30, 2025. Calibration certificate is appended in Appendix D.", S["BodyJ"]))
story.append(Spacer(1, 10))

story.append(Paragraph("5.4 Material Velocity Settings", S["SubHead"]))
vel_headers = ["Material", "Velocity (in/μs)", "Lines"]
vel_rows = [
    [Paragraph("A106 Gr.B (Carbon Steel)", S["TableCell"]),
     Paragraph("0.2330", S["TableCell"]),
     Paragraph("All lines except 3-RF-101, 2-RF-102", S["TableCell"])],
    [Paragraph("316 Stainless Steel", S["TableCell"]),
     Paragraph("0.2260", S["TableCell"]),
     Paragraph("3-RF-101, 2-RF-102 (Reflux)", S["TableCell"])],
]
story.append(make_table(vel_headers, vel_rows, col_widths=[2.0*inch, 1.2*inch, 3.0*inch]))
story.append(Spacer(1, 10))

story.append(Paragraph("5.5 Daily Calibration Verification Records", S["SubHead"]))
story.append(Paragraph(
    "Daily calibration checks were performed each morning prior to commencing inspections and at "
    "the end of each shift, in accordance with GLCP-NDT-001 §4.3. All readings were within the "
    "required ±0.002\" tolerance. Calibration verification photographs are included in Appendix B.", S["BodyJ"]))
story.append(Spacer(1, 6))

cal_headers = ["Date", "Inspector", "Gauge S/N", "AM Check (0.200\" step)", "PM Check (0.200\" step)", "Status"]
cal_rows = []
for day, date_str in enumerate(["Nov 4, 2024", "Nov 5, 2024", "Nov 6, 2024", "Nov 7, 2024"]):
    for name, sn, am, pm in [
        ("M. Chen", "2847193", "0.200\"", "0.201\""),
        ("S. Thompson", "2901456", "0.201\"", "0.200\""),
    ]:
        # Vary slightly per day
        cal_rows.append([
            Paragraph(date_str, S["TableCell"]),
            Paragraph(name, S["TableCell"]),
            Paragraph(sn, S["TableCell"]),
            Paragraph(am, S["TableCell"]),
            Paragraph(pm, S["TableCell"]),
            Paragraph("PASS", S["TableCell"]),
        ])
story.append(make_table(cal_headers, cal_rows,
                         col_widths=[0.9*inch, 0.9*inch, 0.8*inch, 1.2*inch, 1.2*inch, 0.6*inch]))

story.append(PageBreak())

# ═══════════ 6.0 INSPECTION RESULTS — DATA TABLES ═══════════
story.append(Paragraph("6.0 INSPECTION RESULTS — DATA TABLES", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "The following tables present the thickness measurement results organized by piping line and "
    "CML location. Each CML was measured using a minimum of 4 readings at 90° intervals around "
    "the pipe circumference, per GLCP-NDT-001 §5.3. The minimum reading from the four-point scan "
    "is reported as the measured thickness. Historical data from the October 2019 survey is included "
    "for trending comparison.", S["BodyJ"]))
story.append(Spacer(1, 8))

data_headers = ["CML ID", "Component", "Location", "Nom.\n(in)", "t-min\n(in)",
                "2019\n(in)", "2024\n(in)", "Rate\n(mpy)", "Status"]

for ln in sorted(lines_data.keys()):
    d = lines_data[ln]
    story.append(Paragraph(f"6.{list(sorted(lines_data.keys())).index(ln)+1}  Line {ln} — "
                           f"{d['service']} ({d['size']}\" {d['cmls'][0]['material']}, "
                           f"Sch {d['cmls'][0]['schedule']})", S["SubHead"]))
    rows = []
    for c in d["cmls"]:
        status = c["status"]
        if status == "CRITICAL":
            style = S["CriticalCell"]
        elif status == "Alert":
            style = S["AlertCell"]
        else:
            style = S["TableCell"]

        r2024 = c["reading_2024_in"] if c["reading_2024_in"] else "—"
        rate = c["corrosion_rate_mpy"] if c["corrosion_rate_mpy"] else "—"

        rows.append([
            Paragraph(c["cml_id"], S["TableCell"]),
            Paragraph(c["component"], S["TableCell"]),
            Paragraph(c["location"], S["TableCell"]),
            Paragraph(c["nominal_wall_in"], S["TableCell"]),
            Paragraph(c["tmin_in"], S["TableCell"]),
            Paragraph(c["reading_2019_in"], S["TableCell"]),
            Paragraph(r2024, style),
            Paragraph(rate, style),
            Paragraph(status, style),
        ])
    story.append(make_table(data_headers, rows,
                             col_widths=[0.75*inch, 0.7*inch, 1.6*inch, 0.45*inch, 0.45*inch,
                                         0.45*inch, 0.45*inch, 0.45*inch, 0.75*inch]))
    story.append(Spacer(1, 8))

story.append(PageBreak())

# ═══════════ 7.0 TRENDING & CORROSION ANALYSIS ═══════════
story.append(Paragraph("7.0 TRENDING & CORROSION ANALYSIS", S["SectionHead"]))
story.append(hr())

story.append(Paragraph("7.1 Trending Comparison with Historical Data", S["SubHead"]))
story.append(Paragraph(
    "Thickness readings from the current 2024 survey were compared against the baseline 2019 survey "
    "data to establish corrosion trends across all inspected CMLs. The interval between surveys is "
    "approximately 5.05 years (October 2019 to November 2024).", S["BodyJ"]))
story.append(Spacer(1, 8))

story.append(Paragraph("7.2 Corrosion Rate Summary by Line", S["SubHead"]))
rate_headers = ["Line", "Service", "Min Rate\n(mpy)", "Max Rate\n(mpy)", "Avg Rate\n(mpy)", "Concern Level"]
rate_rows = []
for ln in sorted(lines_data.keys()):
    d = lines_data[ln]
    rates = []
    for c in d["cmls"]:
        try:
            r = float(c["corrosion_rate_mpy"])
            rates.append(r)
        except (ValueError, TypeError):
            pass
    if rates:
        avg = sum(rates) / len(rates)
        mn = min(rates)
        mx = max(rates)
        concern = "Low" if avg < 5 else ("Medium" if avg < 10 else "High")
        st = S["CriticalCell"] if concern == "High" else (S["AlertCell"] if concern == "Medium" else S["TableCell"])
        rate_rows.append([
            Paragraph(ln, S["TableCell"]),
            Paragraph(d["service"], S["TableCell"]),
            Paragraph(f"{mn:.1f}", S["TableCell"]),
            Paragraph(f"{mx:.1f}", S["TableCell"]),
            Paragraph(f"{avg:.1f}", st),
            Paragraph(concern, st),
        ])
story.append(make_table(rate_headers, rate_rows,
                         col_widths=[0.9*inch, 1.3*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch]))
story.append(Spacer(1, 10))

story.append(Paragraph("7.3 Remaining Life and Next Inspection Date", S["SubHead"]))
story.append(Paragraph(
    "Remaining life is calculated per API 570 §7.1 as: <b>RL = (t_actual − t_min) / corrosion_rate</b>. "
    "The next recommended inspection date is set at half the calculated remaining life (half-life "
    "method), capped at a maximum of 10 years, per API 570 §6.", S["BodyJ"]))
story.append(Spacer(1, 6))

# Show remaining life for critical/alert/monitor CMLs
rl_headers = ["CML ID", "Line", "2024 (in)", "t-min (in)", "Rate (mpy)", "Remaining Life (yr)", "Next Inspection"]
rl_rows = []
for c in sorted(critical + alert + monitor, key=lambda x: x["cml_id"]):
    rl = remaining_life(c["reading_2024_in"], c["tmin_in"], c["corrosion_rate_mpy"])
    ni = next_inspection(rl)
    status = c["status"]
    st = S["CriticalCell"] if status == "CRITICAL" else (S["AlertCell"] if status == "Alert" else S["TableCell"])
    rl_rows.append([
        Paragraph(c["cml_id"], st),
        Paragraph(c["line_number"], S["TableCell"]),
        Paragraph(c["reading_2024_in"] or "—", S["TableCell"]),
        Paragraph(c["tmin_in"], S["TableCell"]),
        Paragraph(c["corrosion_rate_mpy"] or "—", S["TableCell"]),
        Paragraph(rl, st),
        Paragraph(ni, st),
    ])
story.append(make_table(rl_headers, rl_rows,
                         col_widths=[0.85*inch, 0.7*inch, 0.65*inch, 0.65*inch, 0.65*inch, 1.0*inch, 0.95*inch]))

story.append(PageBreak())

# ═══════════ 8.0 FINDINGS & DISPOSITIONS ═══════════
story.append(Paragraph("8.0 FINDINGS & DISPOSITIONS", S["SectionHead"]))
story.append(hr())

story.append(Paragraph(
    "All findings are categorized per GLCP-NDT-001 §6.2 as follows:", S["BodyJ"]))
story.append(Spacer(1, 4))
cat_data = [
    ["CRITICAL", "Measured thickness below t-min", "Immediate notification; engineering review; FFS evaluation"],
    ["Alert", "Measured thickness below 110% of t-min", "1-year re-inspection interval; engineering notification"],
    ["Monitor", "Corrosion rate exceeding 10 mpy", "Increased monitoring frequency; process review"],
    ["Acceptable", "Readings above thresholds, rates < 10 mpy", "Standard re-inspection per API 570 §6"],
]
cat_rows = [[Paragraph(r[0], S["TableCellBold"]), Paragraph(r[1], S["TableCell"]),
             Paragraph(r[2], S["TableCell"])] for r in cat_data]
story.append(make_table(["Category", "Criteria", "Required Action"], cat_rows,
                         col_widths=[1.0*inch, 2.5*inch, 3.0*inch]))
story.append(Spacer(1, 12))

# 8.1 CRITICAL
story.append(Paragraph("8.1 CRITICAL Findings — Readings Below t-min", S["SubHead"]))
story.append(Paragraph(
    "Per GLCP-NDT-001 §6.3, all CRITICAL findings were reported to GLCP Inspection Coordinator "
    "Jennifer Walsh immediately upon discovery. The following CMLs recorded measured thickness "
    "values below the minimum required thickness:", S["BodyJ"]))
story.append(Spacer(1, 6))

crit_headers = ["CML ID", "Line", "Component", "2024\n(in)", "t-min\n(in)", "Rate\n(mpy)", "Disposition"]
crit_rows = []
for c in sorted(critical, key=lambda x: x["cml_id"]):
    note = c.get("note", "")
    if "localized" in note.lower():
        disp = "FFS evaluation per API 579"
    elif float(c.get("corrosion_rate_mpy", "0") or "0") > 20:
        disp = "Replace at next turnaround; FFS evaluation"
    else:
        disp = "FFS evaluation per API 579; repair or replace as determined"
    crit_rows.append([
        Paragraph(c["cml_id"], S["CriticalCell"]),
        Paragraph(c["line_number"], S["TableCell"]),
        Paragraph(c["component"], S["TableCell"]),
        Paragraph(c["reading_2024_in"], S["CriticalCell"]),
        Paragraph(c["tmin_in"], S["TableCell"]),
        Paragraph(c["corrosion_rate_mpy"], S["CriticalCell"]),
        Paragraph(disp, S["TableCell"]),
    ])
story.append(make_table(crit_headers, crit_rows,
                         col_widths=[0.8*inch, 0.7*inch, 0.7*inch, 0.5*inch, 0.5*inch, 0.5*inch, 2.4*inch]))
story.append(Spacer(1, 8))

# Notification documentation for CRITICAL findings
story.append(Paragraph("<b>Notification Documentation:</b>", S["BodyJ"]))
story.append(Paragraph(
    "• <b>4-RA-101-06:</b> Reported to Jennifer Walsh (GLCP) on November 5, 2024 at 11:45 AM on-site. "
    "Reading confirmed by triple re-measurement. FFS evaluation initiated same day. "
    "Gauge display and surface condition photographs: IMG_0151, IMG_0202.", S["SmallBody"]))
story.append(Paragraph(
    "• <b>6-RA-103-11:</b> Reported to Jennifer Walsh (GLCP) on November 6, 2024 at 10:30 AM. "
    "Localized thin area mapped with circumferential readings. "
    "Gauge display and surface condition photographs: IMG_0163, IMG_0203.", S["SmallBody"]))
story.append(Paragraph(
    "• <b>2-RV-102-02, 2-RV-102-04:</b> Reported to Jennifer Walsh on November 6, 2024 at 2:00 PM. "
    "Multiple CMLs on this line below t-min. Line-wide replacement recommended. "
    "Photographs: IMG_0172, IMG_0173, IMG_0204, IMG_0205.", S["SmallBody"]))
story.append(Paragraph(
    "• <b>2-RF-102-03, 2-RF-102-04, 2-RF-102-05:</b> Reported to Jennifer Walsh on November 7, 2024 "
    "at 10:00 AM. 316SS reflux line showing general wall loss pattern. "
    "Photographs: IMG_0176, IMG_0177, IMG_0178, IMG_0206, IMG_0207, IMG_0208.", S["SmallBody"]))
story.append(Spacer(1, 12))

# 8.2 Alert
story.append(Paragraph("8.2 Alert Findings — Below 110% of t-min", S["SubHead"]))
alert_headers = ["CML ID", "Line", "Component", "2024 (in)", "110% t-min (in)", "t-min (in)", "Disposition"]
alert_rows = []
for c in sorted(alert, key=lambda x: x["cml_id"]):
    tmin = float(c["tmin_in"])
    alert_rows.append([
        Paragraph(c["cml_id"], S["AlertCell"]),
        Paragraph(c["line_number"], S["TableCell"]),
        Paragraph(c["component"], S["TableCell"]),
        Paragraph(c["reading_2024_in"], S["AlertCell"]),
        Paragraph(f"{tmin * 1.1:.3f}", S["TableCell"]),
        Paragraph(c["tmin_in"], S["TableCell"]),
        Paragraph("1-year re-inspection interval", S["TableCell"]),
    ])
story.append(make_table(alert_headers, alert_rows,
                         col_widths=[0.8*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch, 1.8*inch]))
story.append(Spacer(1, 12))

# 8.3 Monitor
story.append(Paragraph("8.3 Monitor Findings — Corrosion Rates Exceeding 10 mpy", S["SubHead"]))
mon_headers = ["CML ID", "Line", "Component", "2024 (in)", "Rate (mpy)", "Disposition"]
mon_rows = []
for c in sorted(monitor, key=lambda x: float(x.get("corrosion_rate_mpy", "0") or "0"), reverse=True):
    mon_rows.append([
        Paragraph(c["cml_id"], S["TableCell"]),
        Paragraph(c["line_number"], S["TableCell"]),
        Paragraph(c["component"], S["TableCell"]),
        Paragraph(c["reading_2024_in"], S["TableCell"]),
        Paragraph(c["corrosion_rate_mpy"], S["TableCell"]),
        Paragraph("2-year re-inspection; process review", S["TableCell"]),
    ])
story.append(make_table(mon_headers, mon_rows,
                         col_widths=[0.8*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.7*inch, 2.3*inch]))
story.append(Spacer(1, 12))

# 8.4 Inaccessible CMLs
story.append(Paragraph("8.4 Inaccessible CMLs", S["SubHead"]))
inac_headers = ["CML ID", "Line", "Component", "Reason", "Documentation"]
inac_rows = []
for c in inaccessible:
    note = c.get("note", "")
    reason = note.replace("INACCESSIBLE: ", "") if note else "See notes"
    inac_rows.append([
        Paragraph(c["cml_id"], S["TableCell"]),
        Paragraph(c["line_number"], S["TableCell"]),
        Paragraph(c["component"], S["TableCell"]),
        Paragraph(reason, S["TableCell"]),
        Paragraph("Photo + field note", S["TableCell"]),
    ])
story.append(make_table(inac_headers, inac_rows,
                         col_widths=[0.9*inch, 0.8*inch, 0.8*inch, 2.5*inch, 1.0*inch]))
story.append(Spacer(1, 12))

# 8.5 Anomalies
story.append(Paragraph("8.5 Anomalies", S["SubHead"]))
story.append(Paragraph(
    "<b>Scale Buildup — Line 3-CW-101 (Amine Cooler Cooling Water):</b> CMLs 3-CW-101-01, "
    "3-CW-101-02, and 3-CW-101-04 returned ultrasonic thickness readings exceeding the nominal "
    "wall thickness (readings of 0.228\", 0.231\", and 0.225\" versus 0.216\" nominal). This is "
    "indicative of internal scale or mineral deposits on the pipe inner surface, which increases "
    "the apparent wall thickness measured by the UT gauge. Gauge calibration was verified and "
    "confirmed accurate. Internal visual inspection is recommended during the next turnaround to "
    "assess scale extent and determine if cleaning is required.", S["BodyJ"]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Accelerated Corrosion — CML 3-RV-101-04:</b> This CML on the Regenerator Overhead line "
    "exhibited a corrosion rate of approximately 12 mpy, significantly higher than the expected "
    "5 mpy for this service. This may indicate process upset conditions (e.g., acid gas carryover, "
    "amine degradation). Process engineering review is recommended.", S["BodyJ"]))

story.append(PageBreak())

# ═══════════ 9.0 RECOMMENDATIONS ═══════════
story.append(Paragraph("9.0 RECOMMENDATIONS", S["SectionHead"]))
story.append(hr())

story.append(Paragraph("9.1 Immediate Actions (Within 30 Days)", S["SubHead"]))
recs_imm = [
    "Complete Fitness-for-Service (FFS) evaluation per API 579-1 for CML 4-RA-101-06 "
    "(4\" Rich Amine elbow, 0.142\" vs 0.150\" t-min). Engineering assessment to determine "
    "suitability for continued service, or requirement for repair/replacement.",
    "Complete FFS evaluation for CML 6-RA-103-11 (6\" Rich Amine Header weldolet, 0.168\" "
    "vs 0.180\" t-min). Map extent of localized thinning with supplemental grid scanning.",
    "Evaluate 2\" Regen Overhead line 2-RV-102 for potential near-term replacement. Three CMLs "
    "are below or near t-min (0.087\", 0.098\", 0.119\" vs 0.110\" t-min).",
    "Evaluate 2\" Reflux line 2-RF-102 for replacement. Three CMLs below t-min in 316SS service "
    "(0.066\", 0.079\", 0.079\" vs 0.085\" t-min).",
]
for i, rec in enumerate(recs_imm, 1):
    story.append(Paragraph(f"<b>{i}.</b> {rec}", S["BodyJ"]))
    story.append(Spacer(1, 4))

story.append(Spacer(1, 8))
story.append(Paragraph("9.2 Re-Inspection Intervals", S["SubHead"]))
ri_headers = ["Priority", "Lines / CMLs", "Interval", "Basis"]
ri_rows = [
    [Paragraph("1 — Immediate", S["CriticalCell"]),
     Paragraph("4-RA-101-06, 6-RA-103-11, 2-RV-102-02, 2-RV-102-04, "
               "2-RF-102-03, 2-RF-102-04, 2-RF-102-05", S["TableCell"]),
     Paragraph("FFS / Repair", S["CriticalCell"]),
     Paragraph("Below t-min", S["TableCell"])],
    [Paragraph("2 — 1 Year", S["AlertCell"]),
     Paragraph("4-RA-102-09, 2-RV-102-05, 2-RF-102-02", S["TableCell"]),
     Paragraph("Nov 2025", S["AlertCell"]),
     Paragraph("Within 110% of t-min", S["TableCell"])],
    [Paragraph("3 — 2 Years", S["TableCell"]),
     Paragraph("All Monitor CMLs (23 locations) — Rich Amine, Regen OH lines", S["TableCell"]),
     Paragraph("Nov 2026", S["TableCell"]),
     Paragraph("Corrosion rate > 10 mpy", S["TableCell"])],
    [Paragraph("4 — 5 Years", S["TableCell"]),
     Paragraph("All remaining Acceptable CMLs", S["TableCell"]),
     Paragraph("Nov 2029", S["TableCell"]),
     Paragraph("API 570 §6 half-life method", S["TableCell"])],
]
story.append(make_table(ri_headers, ri_rows,
                         col_widths=[1.0*inch, 2.5*inch, 0.9*inch, 1.5*inch]))
story.append(Spacer(1, 12))

story.append(Paragraph("9.3 Engineering Review Referrals", S["SubHead"]))
story.append(Paragraph(
    "The following items are referred to GLCP Process and Mechanical Engineering for review:", S["BodyJ"]))
story.append(Spacer(1, 4))
eng_refs = [
    "FFS evaluation per API 579-1, Part 4 (General Metal Loss) for CMLs 4-RA-101-06 and "
    "6-RA-103-11. Part 5 (Local Metal Loss) assessment is recommended for 6-RA-103-11 given "
    "the localized nature of the thinning.",
    "Metallurgical review of 2\" Reflux line 2-RF-102 (316SS). The general wall loss pattern "
    "across multiple CMLs may indicate a material selection concern or chemical incompatibility.",
    "Corrosion rate assessment for Rich Amine service. Rates of 12–35 mpy on Rich Amine lines "
    "suggest potential for amine degradation products (Heat Stable Salts) or acid gas loading "
    "beyond design parameters.",
]
for i, ref in enumerate(eng_refs, 1):
    story.append(Paragraph(f"<b>{i}.</b> {ref}", S["BodyJ"]))
    story.append(Spacer(1, 4))

story.append(Spacer(1, 8))
story.append(Paragraph("9.4 Process Review Recommendations", S["SubHead"]))
proc_recs = [
    "Review amine solution quality (HSS content, amine concentration, pH) for potential "
    "correlation with accelerated corrosion rates observed in Rich Amine and Regenerator "
    "Overhead services.",
    "Investigate whether any process upsets occurred between the 2019 and 2024 survey periods "
    "that could explain the elevated corrosion at CML 3-RV-101-04 (12 mpy vs expected 5 mpy).",
    "Schedule internal inspection of cooling water line 3-CW-101 during next turnaround to "
    "assess the extent of scale deposits and determine if chemical cleaning is warranted.",
    "Consider installation of corrosion coupons or on-line corrosion monitoring probes on Rich "
    "Amine lines (4-RA-101, 4-RA-102, 6-RA-103) to provide real-time corrosion data between "
    "UT surveys.",
]
for i, rec in enumerate(proc_recs, 1):
    story.append(Paragraph(f"<b>{i}.</b> {rec}", S["BodyJ"]))
    story.append(Spacer(1, 4))

story.append(PageBreak())

# ═══════════ APPENDIX A — RAW DATA ═══════════
story.append(Paragraph("APPENDIX A — RAW DATA (GAUGE DATA EXPORTS)", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "Raw gauge data was exported from both Olympus 38DL Plus units (S/N 2847193 and S/N 2901456) "
    "at the end of each survey day. Daily export files are archived as:", S["BodyJ"]))
story.append(Spacer(1, 6))

raw_files = [
    ["field_data_20241104.csv", "40 readings", "Nov 4, 2024", "6-SG-101, 6-SG-102, 4-LA-101, 4-LA-102"],
    ["field_data_20241105.csv", "40 readings", "Nov 5, 2024", "6-LA-103, 4-RA-101, 4-RA-102"],
    ["field_data_20241106.csv", "41 readings", "Nov 6, 2024", "4-RA-102, 6-RA-103, 3-RV-101, 2-RV-102"],
    ["field_data_20241107.csv", "29 readings", "Nov 7, 2024", "3-RF-101, 2-RF-102, 2-ST-101, 3-CW-101, 3-CW-102"],
]
raw_rows = [[Paragraph(c, S["TableCell"]) for c in row] for row in raw_files]
story.append(make_table(["Filename", "Records", "Date", "Lines Covered"], raw_rows,
                         col_widths=[1.6*inch, 0.9*inch, 1.0*inch, 3.0*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "A combined and reconciled data file (field_data_combined.csv) containing all 150 CML records "
    "with matched historical data is maintained by PNDE. Original gauge data files are retained per "
    "PNDE document control procedures for a minimum of 10 years.", S["BodyJ"]))

story.append(PageBreak())

# ═══════════ APPENDIX B — PHOTOGRAPH LOG ═══════════
story.append(Paragraph("APPENDIX B — PHOTOGRAPH LOG", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "A total of 226 photographs were taken during the survey, organized by the following categories "
    "per GLCP-NDT-001 §7.2:", S["BodyJ"]))
story.append(Spacer(1, 6))

photo_summary = [
    ["CML Location", "148", "Every inspected CML — tag and surrounding area"],
    ["Gauge Display", "53", "CRITICAL, Alert, and Monitor readings — gauge screen showing value"],
    ["Surface Condition", "7", "Pipe surface at CRITICAL findings — visual assessment"],
    ["Calibration Check", "8", "Daily AM calibration verification setup (2 inspectors × 4 days)"],
    ["Inaccessible Documentation", "2", "Access obstruction — 6-LA-103-08 and 2-ST-101-03"],
    ["Anomaly", "3", "Scale deposit evidence at 3-CW-101-01, -02, -04"],
    ["General Site", "5", "Unit overview and work area orientation"],
]
photo_rows = [[Paragraph(c, S["TableCell"]) for c in row] for row in photo_summary]
story.append(make_table(["Photo Type", "Count", "Description"], photo_rows,
                         col_widths=[1.5*inch, 0.6*inch, 4.2*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "All photographs are cross-referenced by CML ID in the photo manifest (photo_manifest.csv). "
    "High-resolution originals are archived in PNDE project files. Representative photographs for "
    "CRITICAL findings are referenced in Section 8.1 of this report.", S["BodyJ"]))

# Sample photo reference table for critical/alert
story.append(Spacer(1, 8))
story.append(Paragraph("Key Photographs — CRITICAL and Alert Findings:", S["SubHead"]))
key_photos = [
    ["4-RA-101-06", "CRITICAL", "IMG_0053, IMG_0151, IMG_0202", "CML location, gauge display, surface condition"],
    ["6-RA-103-11", "CRITICAL", "IMG_0081, IMG_0163, IMG_0203", "CML location, gauge display, surface condition"],
    ["2-RV-102-02", "CRITICAL", "IMG_0094, IMG_0172, IMG_0204", "CML location, gauge display, surface condition"],
    ["2-RV-102-04", "CRITICAL", "IMG_0096, IMG_0173, IMG_0205", "CML location, gauge display, surface condition"],
    ["2-RF-102-03", "CRITICAL", "IMG_0110, IMG_0176, IMG_0206", "CML location, gauge display, surface condition"],
    ["2-RF-102-04", "CRITICAL", "IMG_0111, IMG_0177, IMG_0207", "CML location, gauge display, surface condition"],
    ["2-RF-102-05", "CRITICAL", "IMG_0112, IMG_0178, IMG_0208", "CML location, gauge display, surface condition"],
    ["4-RA-102-09", "Alert", "IMG_0068, IMG_0157", "CML location, gauge display"],
    ["2-RV-102-05", "Alert", "IMG_0097, IMG_0174", "CML location, gauge display"],
    ["2-RF-102-02", "Alert", "IMG_0109, IMG_0175", "CML location, gauge display"],
]
kp_rows = [[Paragraph(c, S["TableCell"]) for c in row] for row in key_photos]
story.append(make_table(["CML ID", "Status", "Photo IDs", "Photo Types"], kp_rows,
                         col_widths=[0.9*inch, 0.7*inch, 1.8*inch, 2.8*inch]))

story.append(PageBreak())

# ═══════════ APPENDIX C — PERSONNEL CERTS ═══════════
story.append(Paragraph("APPENDIX C — PERSONNEL CERTIFICATION RECORDS", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "The following personnel certification records are maintained on file and are available upon "
    "request. Copies of current certifications were provided to GLCP prior to mobilization, in "
    "accordance with GLCP-NDT-001 §3.1.", S["BodyJ"]))
story.append(Spacer(1, 8))

cert_headers = ["Inspector", "Cert Number", "Method/Level", "Issue Date", "Expiry Date",
                "Certifying Body", "Document"]
cert_rows = [
    [Paragraph("Marcus Chen", S["TableCell"]),
     Paragraph("PNDE-UT2-0847", S["TableCell"]),
     Paragraph("UT Level II", S["TableCell"]),
     Paragraph("Mar 15, 2021", S["TableCell"]),
     Paragraph("Mar 15, 2026", S["TableCell"]),
     Paragraph("PNDE per ASNT SNT-TC-1A", S["TableCell"]),
     Paragraph("PersonnelCert_Marcus_Chen.pdf", S["TableCell"])],
    [Paragraph("Sarah Thompson", S["TableCell"]),
     Paragraph("PNDE-UT2-1203", S["TableCell"]),
     Paragraph("UT Level II", S["TableCell"]),
     Paragraph("Aug 22, 2020", S["TableCell"]),
     Paragraph("Aug 22, 2025", S["TableCell"]),
     Paragraph("PNDE per ASNT SNT-TC-1A", S["TableCell"]),
     Paragraph("PersonnelCert_Sarah_Thompson.pdf", S["TableCell"])],
    [Paragraph("David Park", S["TableCell"]),
     Paragraph("PNDE-UT3-0215", S["TableCell"]),
     Paragraph("UT Level III", S["TableCell"]),
     Paragraph("Jan 10, 2022", S["TableCell"]),
     Paragraph("Jan 10, 2027", S["TableCell"]),
     Paragraph("PNDE per ASNT SNT-TC-1A", S["TableCell"]),
     Paragraph("On file at PNDE", S["TableCell"])],
]
story.append(make_table(cert_headers, cert_rows,
                         col_widths=[0.9*inch, 1.0*inch, 0.7*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.1*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "<i>Note: Full certification packages including training records, examination results, and "
    "eye examination records are maintained at PNDE head office per ASNT SNT-TC-1A requirements.</i>",
    S["SmallBody"]))

story.append(PageBreak())

# ═══════════ APPENDIX D — EQUIPMENT CAL CERTS ═══════════
story.append(Paragraph("APPENDIX D — EQUIPMENT CALIBRATION CERTIFICATES", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "The following calibration certificates are maintained on file. All calibrations are performed "
    "by PNDE's calibration laboratory, which maintains NIST traceability in accordance with "
    "GLCP-NDT-001 §4.2.", S["BodyJ"]))
story.append(Spacer(1, 8))

calcert_headers = ["Equipment", "Serial No.", "Cal Cert No.", "Cal Date", "Due Date",
                   "Traceable To", "Document"]
calcert_rows = [
    [Paragraph("Olympus 38DL Plus", S["TableCell"]),
     Paragraph("2847193", S["TableCell"]),
     Paragraph("PNDE-CAL-2024-0847", S["TableCell"]),
     Paragraph("May 15, 2024", S["TableCell"]),
     Paragraph("May 15, 2025", S["TableCell"]),
     Paragraph("NIST", S["TableCell"]),
     Paragraph("CalCert_38DL-2847193.pdf", S["TableCell"])],
    [Paragraph("Olympus 38DL Plus", S["TableCell"]),
     Paragraph("2901456", S["TableCell"]),
     Paragraph("PNDE-CAL-2024-1203", S["TableCell"]),
     Paragraph("Jul 22, 2024", S["TableCell"]),
     Paragraph("Jul 22, 2025", S["TableCell"]),
     Paragraph("NIST", S["TableCell"]),
     Paragraph("CalCert_38DL-2901456.pdf", S["TableCell"])],
    [Paragraph("Cal Block (4-step CS)", S["TableCell"]),
     Paragraph("PNDE-CS-001", S["TableCell"]),
     Paragraph("PNDE-CAL-BLK-2024-001", S["TableCell"]),
     Paragraph("Jun 30, 2024", S["TableCell"]),
     Paragraph("Jun 30, 2025", S["TableCell"]),
     Paragraph("NIST", S["TableCell"]),
     Paragraph("CalCert_PNDE-CS-001.pdf", S["TableCell"])],
]
story.append(make_table(calcert_headers, calcert_rows,
                         col_widths=[1.1*inch, 0.7*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.6*inch, 1.3*inch]))

story.append(PageBreak())

# ═══════════ APPENDIX E — ISOMETRIC DRAWINGS ═══════════
story.append(Paragraph("APPENDIX E — ISOMETRIC DRAWINGS WITH CML LOCATIONS", S["SectionHead"]))
story.append(hr())
story.append(Paragraph(
    "Isometric drawings showing CML locations are provided for the piping lines with CRITICAL "
    "findings. CML markers are indicated on the drawings with their identification numbers. "
    "CRITICAL and Alert CMLs are highlighted.", S["BodyJ"]))
story.append(Spacer(1, 8))

iso_headers = ["Drawing No.", "Line", "Service", "CMLs Shown", "CRITICAL CMLs"]
iso_rows = [
    [Paragraph("ISO_4-RA-101", S["TableCell"]),
     Paragraph("4-RA-101", S["TableCell"]),
     Paragraph("Rich Amine", S["TableCell"]),
     Paragraph("12", S["TableCell"]),
     Paragraph("4-RA-101-06", S["CriticalCell"])],
    [Paragraph("ISO_6-RA-103", S["TableCell"]),
     Paragraph("6-RA-103", S["TableCell"]),
     Paragraph("Rich Amine Header", S["TableCell"]),
     Paragraph("14", S["TableCell"]),
     Paragraph("6-RA-103-11", S["CriticalCell"])],
]
story.append(make_table(iso_headers, iso_rows,
                         col_widths=[1.2*inch, 0.8*inch, 1.2*inch, 0.8*inch, 1.2*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "<i>Note: Full-size isometric drawings (ISO_4-RA-101.svg, ISO_6-RA-103.svg) are provided as "
    "separate electronic files. Isometric drawings for all remaining lines are available from GLCP "
    "and can be marked up upon request.</i>", S["SmallBody"]))

story.append(Spacer(1, 1.0 * inch))
story.append(hr())
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph("— END OF REPORT —", ParagraphStyle("End", parent=S["Normal"],
                        fontSize=12, alignment=TA_CENTER, fontName="Helvetica-Bold",
                        textColor=colors.HexColor("#1a3c6e"))))
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("PNDE-RPT-20241025-031-R0 | Revision 0 | November 14, 2024",
                        S["Footer"]))
story.append(Paragraph("Precision NDE Services Inc. | Confidential",
                        S["Footer"]))

# ── Build PDF ──────────────────────────────────────────────────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(4.25 * inch, 0.5 * inch,
                              f"PNDE-RPT-20241025-031-R0  |  Page {doc.page}")
    canvas.drawRightString(7.5 * inch, 0.5 * inch, "CONFIDENTIAL")
    canvas.drawString(1.0 * inch, 0.5 * inch, "Precision NDE Services Inc.")
    canvas.restoreState()

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=letter,
    topMargin=0.75 * inch,
    bottomMargin=0.85 * inch,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    title="PNDE-RPT-20241025-031-R0 — ATU-100 UT Survey Final Report",
    author="Precision NDE Services Inc.",
    subject="Ultrasonic Thickness Survey — Great Lakes Chemical Processing — ATU-100",
)

doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"Report generated: {OUTPUT_PATH}")
