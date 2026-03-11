"""
Generate a MINIMAL template PDF for UT inspection reports.
Section headers + brief 1-2 sentence descriptions of what each section should contain.
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
OUTPUT_PATH = os.path.join(BASE_DIR, "template_minimal.pdf")

PAGE_W, PAGE_H = letter
MARGIN = 0.65 * inch
USABLE_W = PAGE_W - 2 * MARGIN

# ── Styles ─────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
NAVY = colors.HexColor("#1a3c6e")
BLUE = colors.HexColor("#2a5a8e")
LIGHT_BG = colors.HexColor("#f0f4f8")
PLACEHOLDER_BG = colors.HexColor("#fff8e1")
PLACEHOLDER_BORDER = colors.HexColor("#e0c860")

def _add(name, **kw):
    if name in styles.byName:
        return
    styles.add(ParagraphStyle(name, **kw))

_add("CoverTitle", parent=styles["Title"], fontSize=20, spaceAfter=4, alignment=TA_CENTER)
_add("CoverSub", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER, spaceAfter=3)
_add("SectionHead", parent=styles["Heading1"], fontSize=13, spaceBefore=16, spaceAfter=6, textColor=NAVY)
_add("SubHead", parent=styles["Heading2"], fontSize=11, spaceBefore=10, spaceAfter=5, textColor=BLUE)
_add("Body", parent=styles["Normal"], fontSize=9.5, leading=13, alignment=TA_JUSTIFY)
_add("Desc", parent=styles["Normal"], fontSize=9.5, leading=13, textColor=colors.HexColor("#444444"),
     fontName="Helvetica-Oblique")
_add("Footer", parent=styles["Normal"], fontSize=7.5, alignment=TA_CENTER, textColor=colors.grey)

S = styles

def hr():
    return HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=6, spaceBefore=3)

def placeholder_box(text):
    """A styled box containing placeholder/description text."""
    t = Table(
        [[Paragraph(text, S["Desc"])]],
        colWidths=[USABLE_W - 0.4 * inch]
    )
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, PLACEHOLDER_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), PLACEHOLDER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t

# ── Build ──────────────────────────────────────────────────────────────────
story = []

# ═══════════ COVER PAGE ═══════════
story.append(Spacer(1, 1.0 * inch))
story.append(Paragraph("UT INSPECTION REPORT TEMPLATE", S["CoverTitle"]))
story.append(Spacer(1, 0.1 * inch))
story.append(hr())
story.append(Spacer(1, 0.1 * inch))
story.append(Paragraph("Minimal Version", S["CoverSub"]))
story.append(Paragraph("Ultrasonic Thickness Survey \u2014 Final Inspection Report", S["CoverSub"]))
story.append(Spacer(1, 0.35 * inch))

story.append(Paragraph(
    "This template defines the standard sections and structure for a UT thickness survey "
    "final inspection report. Each section contains a brief description of the content that "
    "should be populated from inspection data. For detailed field-level guidance, refer to "
    "the Detailed Version of this template.",
    S["Body"]))
story.append(Spacer(1, 0.3 * inch))

cover_fields = [
    "Report Number", "Revision", "Date", "Client", "Facility / Site",
    "Unit / Area", "Work Order", "Scope Summary", "Survey Dates",
    "Prepared By (Name, Certification, Date)",
    "Reviewed By (Name, Certification, Date)",
    "Approved By (Name, Certification, Date)",
]
story.append(Paragraph("<b>Cover page fields:</b>", S["Body"]))
story.append(Spacer(1, 4))
for f in cover_fields:
    story.append(Paragraph(f"\u2022 {f}", S["Body"]))
    story.append(Spacer(1, 1))

story.append(PageBreak())

# ═══════════ 1. EXECUTIVE SUMMARY ═══════════
story.append(Paragraph("1. Executive Summary", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Provide a high-level overview of the inspection: what was inspected, when, how many CMLs "
    "were surveyed, and the key outcomes. Summarize the count of findings by category "
    "(CRITICAL, Alert, Monitor, Acceptable, Inaccessible). Highlight the most significant "
    "findings that require immediate attention."
))
story.append(Spacer(1, 12))

# ═══════════ 2. SCOPE OF WORK ═══════════
story.append(Paragraph("2. Scope of Work", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Define what was inspected: list all piping lines/circuits with their line numbers, "
    "service type, pipe size (NPS), material, schedule, and CML count per line. Include the "
    "total CML count, survey date range, inspection method, and reference to the client's "
    "request for quotation or work order."
))
story.append(Spacer(1, 12))

# ═══════════ 3. REFERENCE DOCUMENTS ═══════════
story.append(Paragraph("3. Reference Documents", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "List all applicable codes, standards, and procedures referenced during the inspection. "
    "Typical references include API 570, API 574, ASME B31.3, ASME Section V Article 5, "
    "API 579-1/ASME FFS-1, ASNT SNT-TC-1A, and any client-specific NDE procedures."
))
story.append(Spacer(1, 12))

# ═══════════ 4. PERSONNEL & QUALIFICATIONS ═══════════
story.append(Paragraph("4. Personnel &amp; Qualifications", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "List all inspection personnel with their names, roles, certification levels "
    "(e.g., UT Level II, UT Level III), certification numbers, employer, and confirmation "
    "that site-specific safety orientation was completed. Certification records should be "
    "appended."
))
story.append(Spacer(1, 12))

# ═══════════ 5. EQUIPMENT & CALIBRATION ═══════════
story.append(Paragraph("5. Equipment &amp; Calibration", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Identify all UT equipment used: gauge model and serial number, transducer type and ID, "
    "calibration block ID, and material velocity settings. Include the daily calibration "
    "verification log showing pre-job and post-job readings against known block thicknesses "
    "with pass/fail status within the specified tolerance (typically \u00b10.002 in). "
    "Reference appended calibration certificates."
))
story.append(Spacer(1, 12))

story.append(PageBreak())

# ═══════════ 6. INSPECTION RESULTS ═══════════
story.append(Paragraph("6. Inspection Results \u2014 Data Tables", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Present thickness measurement data organized by piping line and CML. For each CML, "
    "include: CML ID, location description, component type, nominal wall thickness, minimum "
    "required thickness (t-min), previous survey thickness, current minimum thickness, and "
    "disposition category. Also include the individual quadrant readings (typically 4 readings "
    "at 90\u00b0 intervals), measurement date/time, operator initials, and gauge serial number."
))
story.append(Spacer(1, 12))

# ═══════════ 7. TRENDING & CORROSION ANALYSIS ═══════════
story.append(Paragraph("7. Trending &amp; Corrosion Analysis", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Calculate and present corrosion rates and remaining life for each CML. Include "
    "short-term corrosion rate (based on previous survey), long-term corrosion rate (based on "
    "baseline/install), remaining life in years, and recommended next inspection date. "
    "State the formulas used and the basis per API 570. Flag any anomalous conditions "
    "(e.g., readings exceeding nominal, suggesting scale deposits)."
))
story.append(Spacer(1, 12))

# ═══════════ 8. FINDINGS & DISPOSITIONS ═══════════
story.append(Paragraph("8. Findings &amp; Dispositions", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Categorize all CML findings using the standard disposition categories: "
    "CRITICAL (below t-min), Alert (below 110% of t-min), Monitor (corrosion rate exceeding "
    "threshold, typically >10 mpy), and Acceptable. For each non-acceptable finding, state "
    "the basis for the classification and the required disposition or action "
    "(e.g., FFS evaluation, repair, increased monitoring)."
))
story.append(Spacer(1, 12))

# ═══════════ 9. RECOMMENDATIONS ═══════════
story.append(Paragraph("9. Recommendations", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Provide recommended actions for each finding category: recommended re-inspection "
    "intervals (typically half of remaining life, bounded between 6 months and 5 years), "
    "referrals for engineering review or FFS evaluation, process review recommendations, "
    "and any additional CML locations to add for future surveys."
))
story.append(Spacer(1, 12))

story.append(PageBreak())

# ═══════════ 10. APPENDICES ═══════════
story.append(Paragraph("10. Appendices", S["SectionHead"]))
story.append(hr())
story.append(placeholder_box(
    "Include the following supporting records as appendices:"
))
story.append(Spacer(1, 6))

appendices = [
    ("A", "Raw Data (Gauge Data Exports)",
     "Raw thickness data exported from the UT gauge in CSV or native format."),
    ("B", "Photograph Log",
     "Photos of each CML location (wide shot + close-up), gauge display photos for "
     "CRITICAL and Alert readings, surface condition photos, and inaccessible location photos."),
    ("C", "Personnel Certification Records",
     "Copies of ASNT SNT-TC-1A or equivalent UT certification for all inspection personnel."),
    ("D", "Equipment Calibration Certificates",
     "NIST-traceable calibration certificates for the UT gauge, transducer, and calibration block."),
    ("E", "Isometric Drawings with CML Locations",
     "Marked-up isometric drawings showing the physical location of each CML on the piping."),
]
for letter_id, title, desc in appendices:
    story.append(Paragraph(f"<b>Appendix {letter_id}: {title}</b>", S["Body"]))
    story.append(Spacer(1, 2))
    story.append(Paragraph(desc, S["Desc"]))
    story.append(Spacer(1, 8))


# ── Footer / page numbers ─────────────────────────────────────────────────
HEADER_TEXT = "UT Inspection Report Template \u2014 Minimal Version"

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
    title="UT Inspection Report Template \u2014 Minimal Version",
    author="UMA AI",
    subject="Template for Ultrasonic Thickness Survey Final Inspection Reports",
)

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"Template generated: {OUTPUT_PATH}")
