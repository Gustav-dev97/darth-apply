"""
Universal ATS-friendly DOCX resume builder driven by style models.
"""

from datetime import date
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from .models import get_style

MONTHS_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
ALIGN_MAP = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER}

def _format_date(d: date | None) -> str:
    return f"{MONTHS_PT[d.month - 1]}/{d.year}" if d else ""

def _format_range(start: date, end: date | None, is_current: bool, sep: str) -> str:
    if is_current: return f"{_format_date(start)}{sep}Atual"
    return f"{_format_date(start)}{sep}{_format_date(end)}"

def _set_default_style(doc: Document, font: str, size: float) -> None:
    style = doc.styles["Normal"]
    style.font.name = font
    style.font.size = Pt(size)

def _set_margins(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin, section.bottom_margin = Inches(0.6), Inches(0.6)
        section.left_margin, section.right_margin = Inches(0.75), Inches(0.75)

def _add_bottom_border(paragraph) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    pPr.append(pBdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)

def _add_header(doc: Document, profile, style: dict) -> None:
    p = doc.add_paragraph()
    p.alignment = ALIGN_MAP[style["name_align"]]
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(profile.full_name.upper())
    run.bold, run.font.size, run.font.name = True, Pt(style["name_size"]), style["font"]
    if style["name_has_line"]: _add_bottom_border(p)

    contact_parts = [c for c in [profile.city, profile.state, profile.phone, profile.email] if c]
    if contact_parts:
        p_c = doc.add_paragraph()
        p_c.alignment = ALIGN_MAP[style["contact_align"]]
        p_c.paragraph_format.space_after = Pt(2)
        r = p_c.add_run(" • ".join(contact_parts))
        r.font.size, r.font.name = Pt(style["contact_size"]), style["font"]

    if profile.links:
        p_l = doc.add_paragraph()
        p_l.alignment = ALIGN_MAP[style["contact_align"]]
        p_l.paragraph_format.space_after = Pt(6)
        r = p_l.add_run(" | ".join(f"{l.name}: {l.url}" for l in profile.links))
        r.font.size, r.font.name = Pt(style["contact_size"]), style["font"]
        r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

def _add_section_header(doc: Document, title: str, style: dict) -> None:
    p = doc.add_paragraph()
    p.alignment = ALIGN_MAP[style["section_align"]]
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title.upper())
    run.bold, run.font.size, run.font.name = True, Pt(style["section_size"]), style["font"]
    if style["section_has_line"]: _add_bottom_border(p)

def _add_bullet(doc: Document, text: str, style: dict) -> None:
    cleaned = text.lstrip("•-*").strip()
    if not cleaned: return
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.space_after = Pt(3)
    r_bullet = p.add_run(f"{style['bullet_char']} ")
    r_bullet.bold, r_bullet.font.name = True, style["font"]
    r_text = p.add_run(cleaned)
    r_text.font.name, r_text.font.size = style["font"], Pt(style["body_size"])

def _add_title_line(doc: Document, bold_part: str, muted_part: str, style: dict) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    r1 = p.add_run(bold_part)
    r1.bold, r1.font.name = True, style["font"]
    r1.font.size = Pt(style["body_size"] + 0.5)
    if muted_part:
        r2 = p.add_run(f"{style['title_separator']}{muted_part}")
        r2.font.size, r2.font.name = Pt(style["meta_size"]), style["font"]

def build_resume(profile, model_id: str = "classico") -> Document:
    style = get_style(model_id)
    doc = Document()
    _set_margins(doc)
    _set_default_style(doc, style["font"], style["body_size"])

    _add_header(doc, profile, style)

    if profile.headline:
        _add_section_header(doc, "Objetivo Profissional", style)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.add_run(profile.headline).bold = True

    if profile.summary:
        _add_section_header(doc, "Resumo de Qualificações", style)
        for line in profile.summary.split("\n"):
            if line.strip(): _add_bullet(doc, line.strip(), style)

    if profile.educations:
        _add_section_header(doc, "Formação Acadêmica", style)
        for edu in profile.educations:
            d_range = _format_range(edu.start_date, edu.end_date, edu.is_current, style["date_separator"])
            title = f"{edu.degree} em {edu.field_of_study}" if edu.field_of_study else edu.degree
            _add_title_line(doc, title, f"{edu.institution} – {d_range}", style)

    if profile.experiences:
        _add_section_header(doc, "Experiência Profissional", style)
        for exp in profile.experiences:
            d_range = _format_range(exp.start_date, exp.end_date, exp.is_current, style["date_separator"])
            _add_title_line(doc, f"{exp.role} | {exp.company}", d_range, style)
            if exp.location:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                p.add_run(exp.location).italic = True
            if exp.description:
                for line in exp.description.split("\n"):
                    if line.strip(): _add_bullet(doc, line.strip(), style)

    if profile.projects:
        _add_section_header(doc, "Projetos Principais", style)
        for proj in profile.projects:
            d_str = _format_range(proj.start_date, proj.end_date, False, style["date_separator"]) if proj.start_date else ""
            title = proj.name + (f" | {proj.link}" if proj.link else "")
            _add_title_line(doc, title, d_str, style)
            if proj.description:
                for line in proj.description.split("\n"):
                    if line.strip(): _add_bullet(doc, line.strip(), style)

    if profile.courses:
        _add_section_header(doc, "Cursos Complementares", style)
        for course in profile.courses:
            d_str = _format_date(course.completion_date)
            title = course.name + (f" | {course.institution}" if course.institution else "")
            _add_title_line(doc, title, d_str, style)

    if profile.skills:
        _add_section_header(doc, "Habilidades", style)
        grouped = {}
        for skill in profile.skills:
            grouped.setdefault(skill.category or "Geral", []).append(skill.name)
        for cat in sorted(grouped.keys()):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            r1 = p.add_run(f"{cat}: ")
            r1.bold, r1.font.name = True, style["font"]
            r2 = p.add_run(", ".join(sorted(grouped[cat])))
            r2.font.name = style["font"]

    return doc