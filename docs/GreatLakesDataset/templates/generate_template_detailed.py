"""
Generate a DETAILED template PDF for UT inspection reports.
Section headers + field-level descriptions, expected data sources,
and completeness criteria for each section.
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
OUTPUT_PATH = os.path.join(BASE_DIR, "template_detailed.pdf")

PAGE_W, PAGE_H = letter
MARGIN = 0.65 * inch
USABLE_W = PAGE_W - 2 * MARGIN

# ── Styles ─────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
NAVY = colors.HexColor("#1a3c6e")
BLUE = colors.HexColor("#2a5a8e")
LIGHT_BG = colors.HexColor("#f0f4f8")
DESC_BG = colors.HexColor("#fff8e1")
DESC_BORDER = colors.HexColor("#e0c860")
CRITERIA_BG = colors.HexColor("#e8f5e9")
CRITERIA_BORDER = colors.HexColor("#66bb6a")
SOURCE_BG = colors.HexColor("#e3f2fd")
SOURCE_BORDER = colors.HexColor("#42a5f5")

def _add(name, **kw):
    if name in styles.byName:
        return
    styles.add(ParagraphStyle(name, **kw))

_add("CoverTitle", parent=styles["Title"], fontSize=20, spaceAfter=4, alignment=TA_CENTER)
_add("CoverSub", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER, spaceAfter=3)
_add("SectionHead", parent=styles["Heading1"], fontSize=13, spaceBefore=16, spaceAfter=6, textColor=NAVY)
_add("SubHead", parent=styles["Heading2"], fontSize=11, spaceBefore=10, spaceAfter=5, textColor=BLUE)
_add("FieldLabel", parent=styles["Heading3"], fontSize=10, spaceBefore=6, spaceAfter=3, textColor=BLUE)
_add("Body", parent=styles["Normal"], fontSize=9.5, leading=13, alignment=TA_JUSTIFY)
_add("Desc", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#444444"),
     fontName="Helvetica-Oblique")
_add("Small", parent=styles["Normal"], fontSize=8.5, leading=11)
_add("TC", parent=styles["Normal"], fontSize=7.5, leading=9.5)
_add("TCB", parent=styles["Normal"], fontSize=7.5, leading=9.5, fontName="Helvetica-Bold")
_add("Footer", parent=styles["Normal"], fontSize=7.5, alignment=TA_CENTER, textColor=colors.grey)
_add("BoxLabel", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold",
     textColor=colors.HexColor("#333333"))

S = styles

def P(text, style="TC"):
    return Paragraph(str(text), S[style])

def PB(text):
    return P(text, "TCB")

def hr():
    return HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=6, spaceBefore=3)

def desc_box(text):
    """Yellow box: what this section/field should contain."""
    t = Table(
        [[Paragraph("<b>Description:</b> " + text, S["Desc"])]],
        colWidths=[USABLE_W - 0.4 * inch]
    )
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, DESC_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), DESC_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t

def source_box(text):
    """Blue box: where to find the data."""
    t = Table(
        [[Paragraph("<b>Data Sources:</b> " + text, S["Desc"])]],
        colWidths=[USABLE_W - 0.4 * inch]
    )
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, SOURCE_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), SOURCE_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t

def criteria_box(text):
    """Green box: how to judge completeness."""
    t = Table(
        [[Paragraph("<b>Completeness Criteria:</b> " + text, S["Desc"])]],
        colWidths=[USABLE_W - 0.4 * inch]
    )
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, CRITERIA_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), CRITERIA_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t

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


# ── Build ──────────────────────────────────────────────────────────────────
story = []

# ═══════════ COVER PAGE ═══════════
story.append(Spacer(1, 0.8 * inch))
story.append(Paragraph("UT INSPECTION REPORT TEMPLATE", S["CoverTitle"]))
story.append(Spacer(1, 0.1 * inch))
story.append(hr())
story.append(Spacer(1, 0.1 * inch))
story.append(Paragraph("Detailed Version", S["CoverSub"]))
story.append(Paragraph("Ultrasonic Thickness Survey \u2014 Final Inspection Report", S["CoverSub"]))
story.append(Spacer(1, 0.25 * inch))

story.append(Paragraph(
    "This template defines the standard sections, fields, data sources, and completeness "
    "criteria for a UT thickness survey final inspection report. It is intended to guide "
    "automated report generation: each section describes what data to extract, where to find "
    "it, and how to determine if the section is complete.",
    S["Body"]))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("<b>Color-coded guidance boxes:</b>", S["Body"]))
story.append(Spacer(1, 4))
story.append(desc_box("Yellow boxes describe what content belongs in the section and the expected format."))
story.append(Spacer(1, 4))
story.append(source_box("Blue boxes indicate where to find the data in the uploaded source files."))
story.append(Spacer(1, 4))
story.append(criteria_box("Green boxes define how to judge whether the section is complete."))

story.append(PageBreak())

# ═══════════ COVER PAGE FIELDS ═══════════
story.append(Paragraph("Cover Page", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "The cover page establishes the report identity, client information, and approval chain. "
    "All fields must be populated. The approval table must include at minimum: Prepared By, "
    "Reviewed By, and Approved By roles."
))
story.append(Spacer(1, 6))

cover_fields = [
    ("Report Number", "Unique report identifier following the company numbering convention "
     "(e.g., PNDE-RPT-YYYYMMDD-NNN-R0 or UT-YY-MMDD-NNN)."),
    ("Revision", "Revision number. Initial issue is 0 or R0. Subsequent revisions increment."),
    ("Date", "Report issue date in YYYY-MM-DD format."),
    ("Client", "Full legal name of the client company."),
    ("Facility / Site", "Physical location of the inspected facility (plant name, city, province/state)."),
    ("Unit / Area", "Specific process unit or area inspected (e.g., Amine Treating Unit ATU-100)."),
    ("Work Order", "Client work order or purchase order number authorizing the inspection."),
    ("Scope Summary", "Brief one-line scope (e.g., '150 CMLs across 18 piping lines')."),
    ("Survey Dates", "Start and end dates of the field survey in YYYY-MM-DD format."),
    ("Method / Code Basis", "Inspection method and governing code (e.g., UT Thickness per ASME V Article 5)."),
    ("Prepared By", "Name and certification of the person who prepared the report, with date."),
    ("Reviewed By", "Name and certification of the technical reviewer, with date."),
    ("Approved By", "Name and certification of the approving authority (typically UT Level III or API 570 inspector), with date."),
]

cover_h = ["Field", "Description"]
cover_w = [1.5 * inch, USABLE_W - 1.5 * inch]
cover_r = [[P(f, "TCB"), P(d)] for f, d in cover_fields]
story.append(make_table(cover_h, cover_r, cover_w))
story.append(Spacer(1, 6))

story.append(source_box(
    "Work order documents, client RFQ, company report numbering log, personnel records, "
    "field mobilization records."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "All fields populated. Report number follows company convention. Dates are consistent "
    "(survey dates precede prepared date, which precedes reviewed date, which precedes "
    "approved date). Approval chain includes at minimum three roles."
))

story.append(PageBreak())

# ═══════════ 1. EXECUTIVE SUMMARY ═══════════
story.append(Paragraph("1. Executive Summary", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "A concise overview of the entire inspection in narrative form. This section should allow "
    "a reader to understand the key outcomes without reading the full report. It must cover: "
    "who performed the inspection, what was inspected, when, the total scope, and the "
    "summary of findings by disposition category."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Required content elements:</b>", S["Body"]))
story.append(Spacer(1, 4))
elements = [
    "Contractor name and type of inspection performed (e.g., ultrasonic thickness survey).",
    "Client name, facility, and specific unit inspected.",
    "Survey date range.",
    "Total CMLs in scope, total successfully inspected, and total inaccessible.",
    "Summary count table: CRITICAL, Alert, Monitor, Acceptable, Inaccessible.",
    "Description of the most significant finding(s) \u2014 include CML ID, location, measured "
    "thickness vs. t-min, and any immediate notifications made.",
    "General statement about overall piping condition and dominant corrosion mechanisms.",
    "Note any anomalous conditions (e.g., scale deposits causing readings above nominal).",
]
for e in elements:
    story.append(Paragraph(f"\u2022 {e}", S["Small"]))
    story.append(Spacer(1, 1))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Summary count table format:</b>", S["Body"]))
story.append(Spacer(1, 4))
sum_h = ["Category", "Count"]
sum_w = [3.0 * inch, 1.5 * inch]
sum_r = [
    [P("Total CMLs in Scope"), P("[from scope definition]")],
    [P("CMLs Inspected"), P("[total measured]")],
    [P("Inaccessible"), P("[count of inaccessible CMLs]")],
    [P("CRITICAL (below t-min)"), P("[count]")],
    [P("Alert (within 110% of t-min)"), P("[count]")],
    [P("Monitor (elevated corrosion rate)"), P("[count]")],
    [P("Acceptable"), P("[count]")],
]
story.append(make_table(sum_h, sum_r, sum_w))
story.append(Spacer(1, 6))

story.append(source_box(
    "Inspection results data tables (Section 6), findings summary (Section 8), "
    "scope of work definition, field notification records."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "All count categories sum to total CMLs in scope. Most significant finding is described "
    "with specific CML ID and thickness values. Survey dates match scope of work. "
    "Contractor and client names are consistent with cover page."
))

story.append(PageBreak())

# ═══════════ 2. SCOPE OF WORK ═══════════
story.append(Paragraph("2. Scope of Work", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Defines the boundaries of the inspection: exactly which piping lines were inspected, "
    "their physical and metallurgical characteristics, and the number of CMLs per line. "
    "This section establishes the basis for all subsequent data tables."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Piping line table format:</b>", S["Body"]))
story.append(Spacer(1, 4))
scope_h = ["Line Number", "Service", "Size (in)", "Material", "Schedule", "CML Count"]
scope_w = [1.1*inch, 1.1*inch, 0.7*inch, 1.0*inch, 0.7*inch, 0.7*inch]
scope_r = [
    [P("[Line ID, e.g., 4-RA-101]"), P("[e.g., Rich Amine]"), P("[NPS, e.g., 4]"),
     P("[e.g., A106 Gr.B]"), P("[e.g., 80]"), P("[e.g., 12]")],
    [P("[repeat for each line]"), P("..."), P("..."), P("..."), P("..."), P("...")],
    [P("TOTAL"), P(""), P(""), P(""), P(""), P("[sum of all CMLs]")],
]
story.append(make_table(scope_h, scope_r, scope_w))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Additional required fields:</b>", S["Body"]))
story.append(Spacer(1, 3))
scope_fields = [
    "Survey Dates: Start and end date of field work.",
    "Previous Survey: Date of last inspection (baseline data for trending).",
    "Reference to client RFQ or work order that defined the scope.",
    "Measurement protocol: Number of readings per CML (typically 4 at 90\u00b0 intervals).",
]
for f in scope_fields:
    story.append(Paragraph(f"\u2022 {f}", S["Small"]))
    story.append(Spacer(1, 1))
story.append(Spacer(1, 6))

story.append(source_box(
    "Client RFQ/work order, CML master list (CSV/Excel), piping specifications, "
    "line lists, P&amp;IDs. The master CML list typically contains line numbers, service, "
    "material, schedule, and NPS for each CML."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "Every piping line in the master CML list is represented. CML counts per line match "
    "the actual number of CMLs in the data tables (Section 6). Total CML count matches "
    "the executive summary. Material and schedule are populated for every line."
))

story.append(PageBreak())

# ═══════════ 3. REFERENCE DOCUMENTS ═══════════
story.append(Paragraph("3. Reference Documents", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "List all codes, standards, and procedures that govern the inspection methodology, "
    "acceptance criteria, personnel qualifications, and equipment requirements. Include "
    "edition/revision numbers and dates."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Typical references for UT piping inspections:</b>", S["Body"]))
story.append(Spacer(1, 4))
refs = [
    ("API 570", "Piping Inspection Code: In-Service Inspection, Rating, Repair, and "
     "Alteration of Piping Systems. Governs inspection intervals, corrosion rate calculations, "
     "and remaining life assessment."),
    ("API 574", "Inspection Practices for Piping System Components. Provides guidance on "
     "inspection techniques for specific piping components (elbows, tees, reducers, etc.)."),
    ("ASME B31.3", "Process Piping. Provides the basis for minimum required wall thickness "
     "(t-min) calculations."),
    ("ASME Section V, Article 5", "Ultrasonic Examination Methods for Materials. Governs "
     "the UT measurement technique."),
    ("API 579-1/ASME FFS-1", "Fitness-For-Service. Referenced when findings require "
     "engineering assessment of continued operability."),
    ("ASNT SNT-TC-1A", "Personnel Qualification and Certification in Nondestructive Testing. "
     "Governs inspector certification requirements."),
    ("Client NDE Procedure", "The client's site-specific NDE requirements document "
     "(e.g., GLCP-NDT-001 Rev 3). Defines acceptance criteria, reporting format, and "
     "data requirements specific to the facility."),
    ("Inspection Procedure", "The contractor's UT thickness measurement procedure "
     "(e.g., PNDE-PROC-UT-005). Defines the specific measurement technique and equipment setup."),
]
ref_h = ["Document", "Description / Relevance"]
ref_w = [1.5 * inch, USABLE_W - 1.5 * inch]
ref_r = [[P(doc, "TCB"), P(desc)] for doc, desc in refs]
story.append(make_table(ref_h, ref_r, ref_w))
story.append(Spacer(1, 6))

story.append(source_box(
    "Contractor quality manual, client NDE specification, work order/RFQ (often specifies "
    "required codes). If not explicitly provided, use the standard set of API/ASME references "
    "listed above."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "At minimum, API 570, ASME B31.3, ASME Section V Article 5, and ASNT SNT-TC-1A are "
    "listed. Client-specific procedure is referenced if provided. All entries include "
    "edition or revision number."
))

story.append(PageBreak())

# ═══════════ 4. PERSONNEL & QUALIFICATIONS ═══════════
story.append(Paragraph("4. Personnel &amp; Qualifications", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Document all personnel who performed or supervised thickness measurements. Each person's "
    "certification level must meet the minimum requirements specified by the client procedure "
    "and ASNT SNT-TC-1A. Trainees may only work under direct supervision of a certified "
    "Level II or III."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Personnel table format:</b>", S["Body"]))
story.append(Spacer(1, 4))
pers_h = ["Name", "Role", "Cert Level", "Cert No.", "Employer", "Safety\nOrientation"]
pers_w = [1.0*inch, 1.0*inch, 0.8*inch, 1.0*inch, 1.2*inch, 0.9*inch]
pers_r = [
    [P("[Full name]"), P("[e.g., Lead UT Inspector]"), P("[e.g., UT Level II]"),
     P("[e.g., UT-LL2-18427]"), P("[Company name]"), P("[Completed / N/A]")],
    [P("[Each person who took readings or supervised]"), P("..."), P("..."),
     P("..."), P("..."), P("...")],
]
story.append(make_table(pers_h, pers_r, pers_w))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Field descriptions:</b>", S["Body"]))
story.append(Spacer(1, 3))
pers_fields = [
    "<b>Name:</b> Full name as it appears on the certification record.",
    "<b>Role:</b> Lead UT Inspector, UT Inspector, Assistant, or Trainee.",
    "<b>Cert Level:</b> ASNT SNT-TC-1A or CGSB certification level (UT Level I, II, or III). "
    "Personnel taking unsupervised measurements must be Level II or higher.",
    "<b>Cert No.:</b> Certification number from the issuing body.",
    "<b>Employer:</b> Company name of the inspection contractor.",
    "<b>Safety Orientation:</b> Confirmation that site-specific safety orientation was "
    "completed prior to commencing work.",
]
for f in pers_fields:
    story.append(Paragraph(f"\u2022 {f}", S["Small"]))
    story.append(Spacer(1, 1))
story.append(Spacer(1, 6))

story.append(source_box(
    "Personnel certification records (appended in Appendix C), site safety orientation "
    "sign-in sheets, contractor HR records. Operator initials in the data tables "
    "(Section 6) must match personnel listed here."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "Every operator initial that appears in the inspection results data tables is traceable "
    "to a person listed here. All measurement personnel are certified at UT Level II or "
    "higher (or documented as supervised trainees). Safety orientation is confirmed for all."
))

story.append(PageBreak())

# ═══════════ 5. EQUIPMENT & CALIBRATION ═══════════
story.append(Paragraph("5. Equipment &amp; Calibration", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Document all UT measurement equipment, calibration status, material velocity settings, "
    "and daily verification records. Equipment must have current NIST-traceable calibration. "
    "Daily verification must be performed pre-job and post-job with results within tolerance."
))
story.append(Spacer(1, 6))

# Equipment identification
story.append(Paragraph("<b>Equipment identification table:</b>", S["Body"]))
story.append(Spacer(1, 4))
eq_h = ["Item", "Model / Description", "Serial / ID", "Calibration Certificate"]
eq_w = [0.9*inch, 1.5*inch, 1.2*inch, 2.6*inch]
eq_r = [
    [P("[UT gauge]"), P("[e.g., Olympus 38DL PLUS]"), P("[Serial number]"),
     P("[Cal cert number and expiry date]")],
    [P("[Transducer]"), P("[Type, frequency, element size]"), P("[ID number]"),
     P("[Included in gauge cert or separate]")],
    [P("[Cal block]"), P("[Type, e.g., IIW Type 1]"), P("[Serial number]"),
     P("[Cal cert number, NIST traceable]")],
]
story.append(make_table(eq_h, eq_r, eq_w))
story.append(Spacer(1, 8))

# Velocity settings
story.append(Paragraph("<b>Material velocity settings:</b>", S["Body"]))
story.append(Spacer(1, 4))
vel_h = ["Material", "Velocity Setting (in/\u03bcs)"]
vel_w = [3.5*inch, 2.0*inch]
vel_r = [
    [P("[e.g., Carbon steel (CS)]"), P("[e.g., 0.2330]")],
    [P("[e.g., Stainless steel (SS 316)]"), P("[e.g., 0.2280]")],
]
story.append(make_table(vel_h, vel_r, vel_w))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Velocity settings must match the material being measured. If multiple materials are "
    "present in the scope, each must have its velocity setting documented.",
    S["Small"]))
story.append(Spacer(1, 8))

# Daily cal verification
story.append(Paragraph("<b>Daily calibration verification log:</b>", S["Body"]))
story.append(Spacer(1, 4))
cal_h = ["Date", "Time", "Operator", "Block Thk\n(in)", "Reading 1", "Reading 2",
         "Reading 3", "Within\nTolerance"]
cal_w = [0.75*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.7*inch]
cal_r = [
    [P("[Each survey day]"), P("[Pre-job time]"), P("[Initials]"), P("[Known thickness]"),
     P("[Reading]"), P("[Reading]"), P("[Reading]"), P("[Yes/No]")],
    [P("[Same day]"), P("[Post-job time]"), P("[Initials]"), P("[Known thickness]"),
     P("[Reading]"), P("[Reading]"), P("[Reading]"), P("[Yes/No]")],
]
story.append(make_table(cal_h, cal_r, cal_w))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Standard tolerance is \u00b10.002 inches. If any post-job verification fails, all "
    "readings taken since the last passing verification must be re-taken.",
    S["Small"]))
story.append(Spacer(1, 6))

story.append(source_box(
    "Gauge calibration certificates (appended in Appendix D), daily calibration log sheets, "
    "gauge data exports (may contain calibration records), equipment inventory records."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "All equipment serial numbers match those referenced in the data tables (Section 6). "
    "Calibration certificates are current (not expired during survey period). Daily "
    "verification entries exist for every survey day. All verifications show 'pass' / "
    "'within tolerance'. Velocity settings match the materials in the scope."
))

story.append(PageBreak())

# ═══════════ 6. INSPECTION RESULTS ═══════════
story.append(Paragraph("6. Inspection Results \u2014 Data Tables", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "The core data section. Present all thickness measurement results organized by piping "
    "line and CML. Two table formats are used: a summary table showing the controlling "
    "(minimum) thickness per CML, and a detail table showing all individual quadrant readings."
))
story.append(Spacer(1, 6))

# Summary table
story.append(Paragraph("<b>Summary table format (one per piping line):</b>", S["Body"]))
story.append(Spacer(1, 4))
res_h = ["CML ID", "Location", "Comp.\nType", "Nom.\n(in)", "t-min\n(in)",
         "Prev.\nThk (in)", "Current\nMin (in)", "Category"]
res_w = [1.0*inch, 1.3*inch, 0.65*inch, 0.5*inch, 0.5*inch, 0.55*inch, 0.6*inch, 0.7*inch]
res_r = [
    [P("[CML identifier]"), P("[Physical location description]"), P("[Pipe/Elbow/Tee/etc.]"),
     P("[Nominal wall]"), P("[Min required]"), P("[Previous survey reading]"),
     P("[Min of current readings]"), P("[CRITICAL / Alert / Monitor / Acceptable]")],
]
story.append(make_table(res_h, res_r, res_w))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Field descriptions:</b>", S["Body"]))
story.append(Spacer(1, 3))
result_fields = [
    "<b>CML ID:</b> Unique identifier for the Condition Monitoring Location. Convention "
    "typically follows [NPS]-[Service code]-[Line #]-[Sequential #] (e.g., 4-RA-101-06).",
    "<b>Location:</b> Physical description of where the CML is on the piping (e.g., "
    "'90\u00b0 elbow near T-102 Regenerator', 'straight run at pipe rack Bay 3').",
    "<b>Component Type:</b> Type of piping component: Straight pipe, Elbow (90\u00b0 or 45\u00b0), "
    "Tee, Reducer, Weldolet, Flange, etc.",
    "<b>Nominal Wall (in):</b> The original nominal wall thickness per the pipe specification "
    "(NPS + Schedule determines this value per ASME standards).",
    "<b>t-min (in):</b> Minimum required thickness calculated per ASME B31.3 for the design "
    "conditions (pressure, temperature). Below this value, the pipe does not meet code.",
    "<b>Previous Thickness (in):</b> The minimum thickness reading from the most recent prior "
    "survey at this same CML. Used to calculate short-term corrosion rate.",
    "<b>Current Min (in):</b> The minimum of all quadrant readings taken at this CML during "
    "the current survey. This is the controlling thickness for disposition.",
    "<b>Category:</b> Disposition based on the current reading: "
    "CRITICAL = below t-min; "
    "Alert = below 110% of t-min but above t-min; "
    "Monitor = acceptable thickness but corrosion rate exceeds threshold (typically >10 mpy); "
    "Acceptable = meets all criteria.",
]
for f in result_fields:
    story.append(Paragraph(f"\u2022 {f}", S["Small"]))
    story.append(Spacer(1, 2))
story.append(Spacer(1, 6))

# Detail readings table
story.append(Paragraph("<b>Detail readings table format (one per piping line):</b>", S["Body"]))
story.append(Spacer(1, 4))
det_h = ["CML ID", "R1 (in)", "R2 (in)", "R3 (in)", "R4 (in)", "Date", "Time",
         "Op.", "Gauge S/N"]
det_w = [1.15*inch, 0.55*inch, 0.55*inch, 0.55*inch, 0.55*inch, 0.8*inch,
         0.45*inch, 0.4*inch, 1.0*inch]
det_r = [
    [P("[CML ID]"), P("[0\u00b0]"), P("[90\u00b0]"), P("[180\u00b0]"), P("[270\u00b0]"),
     P("[YYYY-MM-DD]"), P("[HH:MM]"), P("[Initials]"), P("[Gauge serial]")],
]
story.append(make_table(det_h, det_r, det_w))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "R1 through R4 represent thickness readings at approximately 90\u00b0 intervals around the "
    "pipe circumference (12 o'clock, 3 o'clock, 6 o'clock, 9 o'clock). The minimum reading "
    "is used as the controlling thickness in the summary table above.",
    S["Small"]))
story.append(Spacer(1, 6))

story.append(source_box(
    "Primary source: gauge data export (CSV or native gauge format). Secondary sources: "
    "master CML list (for nominal wall, t-min, and previous survey data), field data sheets. "
    "Match CML IDs between gauge export and master list. Operator initials and gauge serial "
    "number from gauge metadata or field log."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "Every CML in the scope of work has a corresponding row in the data tables. No blank "
    "thickness values (inaccessible CMLs should be explicitly noted with reason). Previous "
    "survey thickness is populated for all CMLs where historical data exists. Categories "
    "are correctly assigned based on the comparison of current min reading to t-min and "
    "110% of t-min. Operator initials trace back to Personnel section. Gauge serial number "
    "matches Equipment section."
))

story.append(PageBreak())

# ═══════════ 7. TRENDING & CORROSION ANALYSIS ═══════════
story.append(Paragraph("7. Trending &amp; Corrosion Analysis", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Calculate corrosion rates and remaining life for each CML using historical and current "
    "thickness data. These calculations drive the recommended inspection intervals and are "
    "the primary basis for integrity management decisions."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Formulas (per API 570 \u00a77.1):</b>", S["Body"]))
story.append(Spacer(1, 3))
formulas = [
    "<b>Short-term corrosion rate (mpy)</b> = (T<sub>previous</sub> \u2212 T<sub>current</sub>) "
    "\u00d7 1000 / \u0394t (years between surveys). Uses the two most recent surveys.",
    "<b>Long-term corrosion rate (mpy)</b> = (T<sub>original/baseline</sub> \u2212 T<sub>current</sub>) "
    "\u00d7 1000 / \u0394t (years since baseline). Uses the earliest available data.",
    "<b>Remaining life (years)</b> = (T<sub>current</sub> \u2212 t-min) / (corrosion rate used / 1000). "
    "Use the higher of short-term and long-term rates for conservatism, unless engineering "
    "justifies otherwise.",
    "<b>Next inspection date</b> = current date + (remaining life / 2), bounded to a minimum "
    "of 6 months and maximum of 5 years per API 570 \u00a76.",
]
for f in formulas:
    story.append(Paragraph(f"\u2022 {f}", S["Small"]))
    story.append(Spacer(1, 2))
story.append(Spacer(1, 6))

# Trending table
story.append(Paragraph("<b>Trending table format:</b>", S["Body"]))
story.append(Spacer(1, 4))
tr_h = ["Line", "CML", "t-min\n(in)", "Current\n(in)", "Prev.\n(in)",
        "CR Short\n(mpy)", "CR Long\n(mpy)", "Rem. Life\n(yr)", "Next\nInspection"]
tr_w = [0.7*inch, 1.1*inch, 0.45*inch, 0.5*inch, 0.5*inch, 0.6*inch,
        0.55*inch, 0.6*inch, 0.7*inch]
tr_r = [
    [P("[Line ID]"), P("[CML ID]"), P("[t-min]"), P("[Current min]"), P("[Previous]"),
     P("[Calculated]"), P("[Calculated]"), P("[Calculated]"), P("[Calculated date]")],
]
story.append(make_table(tr_h, tr_r, tr_w))
story.append(Spacer(1, 6))

story.append(Paragraph(
    "Flag anomalous conditions: if a current reading exceeds the nominal wall thickness, "
    "this may indicate internal scale deposits rather than metal loss. Note this explicitly "
    "and recommend internal inspection to verify.",
    S["Small"]))
story.append(Spacer(1, 6))

story.append(source_box(
    "Calculated from data in Section 6 (current readings) combined with historical survey "
    "data from the master CML list. Nominal wall and t-min from piping specifications. "
    "If multiple historical surveys exist, use the most recent for short-term rate and the "
    "earliest for long-term rate."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "Every CML with both current and previous readings has a calculated short-term corrosion "
    "rate. Remaining life is calculated for all CMLs. No negative corrosion rates without "
    "explanation (negative rate implies wall growth, which should be flagged as anomalous). "
    "Next inspection dates are within the 6-month to 5-year bounds. CMLs with remaining "
    "life less than or equal to zero are flagged as CRITICAL in Section 8."
))

story.append(PageBreak())

# ═══════════ 8. FINDINGS & DISPOSITIONS ═══════════
story.append(Paragraph("8. Findings &amp; Dispositions", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Categorize every CML into a disposition category and define the required action for "
    "each non-acceptable finding. This section is the primary action-driver for the client's "
    "integrity management program."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Disposition categories and criteria:</b>", S["Body"]))
story.append(Spacer(1, 4))
cat_h = ["Category", "Criteria", "Typical Disposition"]
cat_w = [1.0*inch, 2.2*inch, 3.0*inch]
cat_r = [
    [P("CRITICAL", "TCB"), P("Current thickness is below t-min."),
     P("Immediate notification to client. Isolate and repair/replace, or perform API 579 "
       "Fitness-for-Service evaluation to justify continued operation.")],
    [P("Alert", "TCB"), P("Current thickness is below 110% of t-min but above t-min."),
     P("Plan repair or increased monitoring at next outage. Validate with follow-up UT. "
       "Consider FFS evaluation if remaining life is short.")],
    [P("Monitor", "TCB"), P("Thickness is acceptable but short-term corrosion rate exceeds "
       "threshold (typically >10 mpy)."),
     P("Investigate corrosion mechanism. Consider process review, inhibitor evaluation, "
       "or adding targeted CMLs. Engineering review if trend continues.")],
    [P("Acceptable", "TCB"), P("Thickness and corrosion rate meet all criteria."),
     P("No action required beyond routine inspection interval.")],
]
story.append(make_table(cat_h, cat_r, cat_w))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Findings table format:</b>", S["Body"]))
story.append(Spacer(1, 4))
fd_h = ["Category", "CML", "Line", "Current\nMin (in)", "t-min\n(in)",
        "Basis", "Disposition / Notes"]
fd_w = [0.65*inch, 1.05*inch, 0.7*inch, 0.6*inch, 0.5*inch, 0.7*inch, 2.0*inch]
fd_r = [
    [P("[Category]"), P("[CML ID]"), P("[Line ID]"), P("[Reading]"), P("[t-min]"),
     P("[Why this category]"), P("[Required action]")],
]
story.append(make_table(fd_h, fd_r, fd_w))
story.append(Spacer(1, 6))

story.append(Paragraph(
    "Sort findings by severity: CRITICAL first, then Alert, Monitor, and Acceptable. "
    "For CRITICAL findings, include details of when and how the client was notified "
    "(notification form number, date, person notified).",
    S["Small"]))
story.append(Spacer(1, 6))

story.append(source_box(
    "Derived from Section 6 (current readings vs. t-min) and Section 7 (corrosion rates). "
    "Notification records for CRITICAL findings. Client procedure defines the specific "
    "thresholds for each category."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "Every CML in scope is assigned exactly one category. Categories are consistent with "
    "the data: every CML with current reading below t-min is CRITICAL, every CML below "
    "110% t-min is Alert, every CML with corrosion rate above threshold is Monitor. "
    "CRITICAL findings include notification details. Dispositions are specific and "
    "actionable (not vague)."
))

story.append(PageBreak())

# ═══════════ 9. RECOMMENDATIONS ═══════════
story.append(Paragraph("9. Recommendations", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Provide specific, actionable recommendations for each finding. Recommendations must "
    "include re-inspection intervals, referrals for engineering review or FFS evaluation, "
    "and any process or operational changes suggested by the inspection findings."
))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Recommendations table format:</b>", S["Body"]))
story.append(Spacer(1, 4))
rec_h = ["Line", "CML", "Cat.", "CR Short\n(mpy)", "Rem. Life\n(yr)",
         "Rec.\nInterval", "Next\nDate", "Recommendation"]
rec_w = [0.6*inch, 0.95*inch, 0.55*inch, 0.55*inch, 0.5*inch, 0.5*inch,
         0.6*inch, 1.95*inch]
rec_r = [
    [P("[Line ID]"), P("[CML ID]"), P("[Category]"), P("[Rate]"), P("[Years]"),
     P("[Interval]"), P("[Date]"), P("[Specific action]")],
]
story.append(make_table(rec_h, rec_r, rec_w))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Interval guidelines (per API 570 \u00a76):</b>", S["Body"]))
story.append(Spacer(1, 3))
intervals = [
    "CRITICAL: 6 months or immediate action (repair/replace/FFS).",
    "Alert: Half of remaining life, minimum 6 months.",
    "Monitor: Half of remaining life, bounded 6 months to 5 years.",
    "Acceptable: Half of remaining life, maximum 5 years.",
]
for i in intervals:
    story.append(Paragraph(f"\u2022 {i}", S["Small"]))
    story.append(Spacer(1, 1))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Additional recommendations to consider:</b>", S["Body"]))
story.append(Spacer(1, 3))
addl = [
    "Process engineering review for CMLs showing unexpected corrosion patterns "
    "(e.g., localized thinning at elbows suggesting flow-accelerated corrosion).",
    "Addition of new CMLs in areas adjacent to CRITICAL or Alert findings.",
    "Internal inspection during next turnaround for CMLs showing anomalous readings "
    "(readings above nominal suggesting scale deposits).",
    "Metallurgical evaluation if corrosion mechanism is unclear.",
]
for a in addl:
    story.append(Paragraph(f"\u2022 {a}", S["Small"]))
    story.append(Spacer(1, 1))
story.append(Spacer(1, 6))

story.append(source_box(
    "Derived from Section 7 (remaining life and corrosion rates) and Section 8 "
    "(findings and dispositions). Interval calculations are formulaic; additional "
    "recommendations require engineering judgment informed by the corrosion patterns "
    "observed in the data."
))
story.append(Spacer(1, 4))
story.append(criteria_box(
    "Every CML has a recommended interval and next inspection date. Intervals are "
    "consistent with API 570 guidelines and remaining life calculations. CRITICAL findings "
    "have immediate action recommendations. Recommendations are specific (not generic). "
    "Process review is recommended where corrosion patterns suggest a systemic issue."
))

story.append(PageBreak())

# ═══════════ 10. APPENDICES ═══════════
story.append(Paragraph("10. Appendices", S["SectionHead"]))
story.append(hr())

story.append(desc_box(
    "Appendices provide the supporting evidence and records that substantiate the report. "
    "Each appendix should be clearly labeled and cross-referenced from the main body."
))
story.append(Spacer(1, 6))

appendices = [
    ("A", "Raw Data (Gauge Data Exports)",
     "The unprocessed thickness data exported directly from the UT gauge in its native "
     "format (typically CSV or proprietary gauge format). This provides an auditable trail "
     "from raw measurement to reported value.",
     "Gauge CSV/data file as uploaded by the inspector. Match CML IDs in the raw data "
     "to the reported values in Section 6.",
     "Raw data file is included. CML count in raw data matches the number of CMLs reported. "
     "Timestamps in raw data fall within the survey date range."),

    ("B", "Photograph Log",
     "Photographs documenting each CML location, gauge readings for CRITICAL and Alert "
     "findings, surface conditions, and any inaccessible locations. Each photo should be "
     "labeled with: Photo ID, CML ID, photo type (CML Location / Gauge Display / Surface "
     "Condition / Inaccessible), and a brief description.",
     "Field photographs taken by inspection personnel. Photo file metadata for dates/times.",
     "At minimum, one CML location photo per CML. Gauge display photos for all CRITICAL "
     "and Alert findings. Photos of any anomalous surface conditions."),

    ("C", "Personnel Certification Records",
     "Copies of ASNT SNT-TC-1A, CGSB, or equivalent certifications for all UT inspection "
     "personnel listed in Section 4.",
     "Contractor HR/certification records.",
     "Certification record exists for every person listed in Section 4. Certifications are "
     "current (not expired during survey period)."),

    ("D", "Equipment Calibration Certificates",
     "NIST-traceable calibration certificates for the UT gauge, transducer, and calibration "
     "block listed in Section 5.",
     "Gauge manufacturer calibration records, third-party cal lab certificates.",
     "Certificate exists for every piece of equipment in Section 5. Calibrations are current. "
     "Certificates are NIST-traceable."),

    ("E", "Isometric Drawings with CML Locations",
     "Marked-up isometric drawings showing the physical location of each CML on the piping "
     "system. CML IDs on the drawings must match those in the data tables.",
     "Client-provided isometric drawings, marked up by inspection personnel in the field.",
     "Every CML in the scope has a marked location on an isometric drawing. CML IDs on "
     "drawings match the data tables."),
]

for letter_id, title, desc, sources, criteria in appendices:
    story.append(Paragraph(f"<b>Appendix {letter_id}: {title}</b>", S["Body"]))
    story.append(Spacer(1, 4))
    story.append(desc_box(desc))
    story.append(Spacer(1, 3))
    story.append(source_box(sources))
    story.append(Spacer(1, 3))
    story.append(criteria_box(criteria))
    story.append(Spacer(1, 10))


# ── Footer / page numbers ─────────────────────────────────────────────────
HEADER_TEXT = "UT Inspection Report Template \u2014 Detailed Version"

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawString(MARGIN, PAGE_H - 0.4 * inch, HEADER_TEXT)
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE_H - 0.5 * inch, PAGE_W - MARGIN, PAGE_H - 0.5 * inch)
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
    title="UT Inspection Report Template \u2014 Detailed Version",
    author="UMA AI",
    subject="Template for Ultrasonic Thickness Survey Final Inspection Reports",
)

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"Template generated: {OUTPUT_PATH}")
