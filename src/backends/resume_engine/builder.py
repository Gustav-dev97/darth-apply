"""
Build an ATS-friendly DOCX resume from the profile.

Design rules followed (per current ATS parsing best practices):
- Single column, no tables
- No images or graphics in the body
- Standard fonts (Calibri)
- Section headers in ALL CAPS, bold, with a thin bottom border
- Bullets as literal "•" characters
- Contact info in the body, not in a Word header
- Supports projects (for users without formal experience)
- Supports courses (rendered without descriptions; descriptions are
  stored only for AI-based job matching)
"""

from datetime import date

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Calibri"
BODY_SIZE = Pt(11)
NAME_SIZE = Pt(22)
SECTION_SIZE = Pt(12)
META_SIZE = Pt(10)

MONTHS_PT = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]


def _set_default_style(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = BODY_SIZE


def _set_margins(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)


def _format_date(d: date | None) -> str:
    if d is None:
        return ""
    return f"{MONTHS_PT[d.month - 1]}/{d.year}"


def _format_range(start: date, end: date | None, is_current: bool) -> str:
    if is_current:
        return f"{_format_date(start)} – Atual"
    return f"{_format_date(start)} – {_format_date(end)}"


def _add_header(doc: Document, name: str, contact_parts: list[str], links: list[str]) -> None:
    # Name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(name.upper())
    run.bold = True
    run.font.size = NAME_SIZE
    run.font.name = FONT

    # Contact info (separated by bullet)
    if contact_parts:
        p_contact = doc.add_paragraph()
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_contact.paragraph_format.space_after = Pt(2)
        r = p_contact.add_run(" • ".join(contact_parts))
        r.font.size = Pt(10.5)
        r.font.name = FONT

    # Links (separated by pipe)
    if links:
        p_links = doc.add_paragraph()
        p_links.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_links.paragraph_format.space_after = Pt(6)
        r = p_links.add_run(" | ".join(links))
        r.font.size = Pt(10)
        r.font.name = FONT
        r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


def _add_section_header(doc: Document, title: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title.upper())
    run.bold = True
    run.font.size = SECTION_SIZE
    run.font.name = FONT

    # Bottom border line
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    pPr.append(pBdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")  # Thickness
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)


def _add_bullet(doc: Document, text: str) -> None:
    # Remove qualquer prefixo de bullet que já venha no texto (evita "• • texto")
    cleaned = text.lstrip("•-*").strip()
    if not cleaned:
        return
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.space_after = Pt(3)
    p.add_run("• ").bold = True
    p.add_run(cleaned)


def _add_title_line(doc: Document, bold_part: str, muted_part: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    r1 = p.add_run(bold_part)
    r1.bold = True
    r1.font.name = FONT
    if muted_part:
        r2 = p.add_run(f"  |  {muted_part}")
        r2.font.size = META_SIZE
        r2.font.name = FONT


def build_resume(profile) -> Document:
    doc = Document()
    _set_margins(doc)
    _set_default_style(doc)

    # 1. Header
    contact_parts = [c for c in [profile.city, profile.state, profile.phone, profile.email] if c]
    links_parts = [f"{l.name}: {l.url}" for l in profile.links] if profile.links else []
    _add_header(doc, profile.full_name, contact_parts, links_parts)

    # 2. Objective
    if profile.headline:
        _add_section_header(doc, "Objetivo Profissional")
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.add_run(profile.headline).bold = True

    # 3. Summary
    if profile.summary:
        _add_section_header(doc, "Resumo de Qualificações")
        for line in profile.summary.split("\n"):
            if line.strip():
                _add_bullet(doc, line.strip())

    # 4. Education
    if profile.educations:
        _add_section_header(doc, "Formação Acadêmica")
        for edu in profile.educations:
            date_range = _format_range(edu.start_date, edu.end_date, edu.is_current)
            title = f"{edu.degree} em {edu.field_of_study}" if edu.field_of_study else edu.degree
            _add_title_line(doc, title, f"{edu.institution} – {date_range}")

    # 5. Experience (Only if exists)
    if profile.experiences:
        _add_section_header(doc, "Experiência Profissional")
        for exp in profile.experiences:
            date_range = _format_range(exp.start_date, exp.end_date, exp.is_current)
            _add_title_line(doc, f"{exp.role} | {exp.company}", date_range)
            if exp.location:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                r = p.add_run(exp.location)
                r.italic = True
                r.font.size = Pt(9.5)
            if exp.description:
                for line in exp.description.split("\n"):
                    if line.strip():
                        _add_bullet(doc, line.strip())

    # 6. Projects (Fallback for no experience / personal projects)
    if profile.projects:
        _add_section_header(doc, "Projetos Principais")
        for proj in profile.projects:
            date_str = _format_range(proj.start_date, proj.end_date, False) if proj.start_date else ""
            title = proj.name
            if proj.link:
                title += f" | {proj.link}"
            _add_title_line(doc, title, date_str)
            if proj.description:
                for line in proj.description.split("\n"):
                    if line.strip():
                        _add_bullet(doc, line.strip())

    # 6.5 Courses (Complementary Education)
    # Only name, institution and completion date are rendered. The course
    # description is intentionally omitted here — it is stored in the DB
    # for AI-based job matching, not for the visible resume.
    if profile.courses:
        _add_section_header(doc, "Cursos Complementares")
        for course in profile.courses:
            date_str = _format_date(course.completion_date) if course.completion_date else ""
            title = course.name
            if course.institution:
                title += f" | {course.institution}"
            _add_title_line(doc, title, date_str)

    # 7. Skills
    if profile.skills:
        _add_section_header(doc, "Habilidades")
        grouped: dict[str, list[str]] = {}
        for skill in profile.skills:
            cat = skill.category or "Geral"
            grouped.setdefault(cat, []).append(skill.name)

        for cat in sorted(grouped.keys()):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(f"{cat}: ")
            run.bold = True
            run.font.name = FONT
            p.add_run(", ".join(sorted(grouped[cat])))

    return doc