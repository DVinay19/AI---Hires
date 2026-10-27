
from io import BytesIO
from xml.sax.saxutils import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)

GREEN = colors.HexColor("#17695B")
DARK = colors.HexColor("#202A2A")
MUTED = colors.HexColor("#62716F")
LIGHT_GREEN = colors.HexColor("#EAF4F0")
LINE = colors.HexColor("#DCE6E2")


def clean_text(value):
    """Convert user-supplied content into safe, printable text."""
    if value is None:
        return ""
    return str(value).strip()


def paragraph_text(value):
    """Escape text before inserting intentional ReportLab line breaks."""
    return escape(clean_text(value)).replace("\n", "<br/>")


def make_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ResumeName",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        textColor=DARK,
        alignment=TA_CENTER,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="ContactLine",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=10,
        wordWrap="CJK",
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=GREEN,
        alignment=TA_LEFT,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="ResumeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK,
        spaceAfter=3,
        splitLongWords=True,
        wordWrap="CJK",
    ))

    styles.add(ParagraphStyle(
        name="ResumeBullet",
        parent=styles["ResumeBody"],
        leftIndent=12,
        firstLineIndent=-8,
        bulletIndent=0,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=26,
        textColor=GREEN,
        alignment=TA_CENTER,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="SmallNote",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=MUTED,
        spaceBefore=4,
    ))

    return styles


def footer(canvas, document):
    """Add a discreet footer and page number to every page."""
    canvas.saveState()
    width, _ = A4

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(
        document.leftMargin,
        13 * mm,
        width - document.rightMargin,
        13 * mm,
    )

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(document.leftMargin, 8.5 * mm, "AI Hires")
    canvas.drawRightString(
        width - document.rightMargin,
        8.5 * mm,
        f"Page {document.page}",
    )
    canvas.restoreState()


def make_document(buffer, title):
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=17 * mm,
        bottomMargin=19 * mm,
        title=title,
        author="AI Hires",
        subject="Resume and career analysis",
    )


def add_section(story, heading, content, styles):
    content = clean_text(content)
    if not content:
        return

    story.append(Paragraph(escape(heading.upper()), styles["SectionHeading"]))
    story.append(HRFlowable(
        width="100%",
        thickness=0.6,
        color=LINE,
        spaceAfter=6,
    ))

    # Each non-empty line becomes its own readable paragraph or bullet.
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    for line in lines:
        if line.startswith(("-", "*", "•")):
            line = re.sub(r"^[-*•]\s*", "", line)
            story.append(Paragraph(
                "• " + paragraph_text(line),
                styles["ResumeBullet"],
            ))
        else:
            story.append(Paragraph(
                paragraph_text(line),
                styles["ResumeBody"],
            ))


def resume_pdf(data):
    """Build a clean, single-column, ATS-friendly resume PDF."""
    data = data or {}
    buffer = BytesIO()
    document = make_document(buffer, "Resume")

    styles = make_styles()
    story = []

    name = clean_text(data.get("name")) or "Resume"
    story.append(Paragraph(escape(name), styles["ResumeName"]))

    contact_fields = [
        clean_text(data.get("email")),
        clean_text(data.get("phone")),
        clean_text(data.get("location")),
        clean_text(data.get("linkedin")),
        clean_text(data.get("github")),
    ]
    contact = "  |  ".join(value for value in contact_fields if value)

    if contact:
        story.append(Paragraph(escape(contact), styles["ContactLine"]))

    story.append(HRFlowable(
        width="100%",
        thickness=1.5,
        color=GREEN,
        spaceBefore=2,
        spaceAfter=8,
    ))

    sections = [
        ("Professional Summary", data.get("summary", "")),
        ("Skills", data.get("skills", "")),
        ("Experience", data.get("experience", "")),
        ("Projects", data.get("projects", "")),
        ("Education", data.get("education", "")),
        ("Certifications", data.get("certifications", "")),
    ]

    for heading, content in sections:
        add_section(story, heading, content, styles)

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


def analysis_pdf(result):
    """Build a readable resume analysis report."""
    result = result or {}
    buffer = BytesIO()
    document = make_document(buffer, "AI Hires Resume Analysis")
    styles = make_styles()
    story = [
        Paragraph("AI Hires", styles["ReportTitle"]),
        Paragraph(
            "Resume Analysis &amp; Job Match Report",
            styles["ReportSubtitle"],
        ),
    ]

    add_section(
        story,
        "Target Role",
        result.get("job_title", "Not specified"),
        styles,
    )

    metrics = [
        ("Overall match estimate", result.get("overall", 0)),
        ("Skill coverage", result.get("skill_score", 0)),
        ("Text similarity", result.get("similarity", 0)),
        ("Section completeness", result.get("section_score", 0)),
    ]

    story.append(Paragraph("MATCH OVERVIEW", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=7))

    for label, value in metrics:
        story.append(Paragraph(
            f"<b>{escape(label)}:</b> {escape(str(value))}%",
            styles["ResumeBody"],
        ))

    for heading, key in [
        ("Matched Skills", "matched"),
        ("Missing or Undetected Skills", "missing"),
        ("Additional Skills", "additional"),
        ("Recommendations", "suggestions"),
    ]:
        values = result.get(key, [])
        if isinstance(values, (list, tuple)):
            content = "\n".join(f"• {item}" for item in values) or "None listed."
        else:
            content = clean_text(values) or "None listed."
        add_section(story, heading, content, styles)

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Important:</b> These scores are heuristic estimates, "
        "not official ATS scores or guarantees of hiring outcomes. "
        "Review all recommendations before using them.",
        styles["SmallNote"],
    ))

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
