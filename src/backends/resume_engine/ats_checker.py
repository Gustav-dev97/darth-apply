"""
ATS-friendliness checker.

Extracts text and structural metadata from the generated DOCX (and PDF, when
available) to verify that a downstream parser would see the essential content.
Includes structural checks (no tables, safe fonts, no images).
"""

import re
from pathlib import Path


def extract_text_docx(path: Path) -> str:
    from docx import Document
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text_pdf(path: Path) -> str:
    import fitz  # pymupdf
    doc = fitz.open(str(path))
    text = "".join(page.get_text() for page in doc)
    doc.close()
    return text


def check_resume_docx(path: Path, profile) -> dict:
    """Deep ATS checks on the DOCX structure."""
    from docx import Document

    doc = Document(str(path))
    checks = []

    def add(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    # 1. Tabelas (ATS odeia tabelas)
    add("Sem tabelas ocultas", len(doc.tables) == 0, f"{len(doc.tables)} tabelas encontradas")

    # 2. Imagens (ATS não lê imagens, e elas confundem o parser)
    inline_shapes = doc.inline_shapes
    add("Sem imagens no corpo", len(inline_shapes) == 0, f"{len(inline_shapes)} imagens encontradas")

    # 3. Fontes padrão (Calibri, Arial, Times New Roman são seguras)
    fonts = set()
    for p in doc.paragraphs:
        for r in p.runs:
            if r.font.name:
                fonts.add(r.font.name)
    safe_fonts = {"Calibri", "Arial", "Times New Roman", "Verdana", None}
    unknown_fonts = fonts - safe_fonts
    add("Fontes ATS-friendly", len(unknown_fonts) == 0, f"Incompatíveis: {', '.join(unknown_fonts) if unknown_fonts else 'Nenhuma'}")

    # 4. Contato no topo (não em cabeçalho/rodapé do Word)
    has_contact_top = False
    for p in doc.paragraphs[:5]:  # Checa apenas os 5 primeiros parágrafos
        if profile.email.lower() in p.text.lower():
            has_contact_top = True
    add("Contato no topo do texto", has_contact_top)

    # 5. Seções padrão
    text = "\n".join(p.text for p in doc.paragraphs).lower()
    required_sections = ["objetivo profissional", "resumo", "formação acadêmica", "habilidades"]
    found_sections = sum(1 for s in required_sections if s in text)
    add("Seções padrão detectadas", found_sections >= 2, f"{found_sections}/{len(required_sections)} encontradas")

    passed = all(c["passed"] for c in checks)
    return {"passed": passed, "checks": checks}


def check_resume_pdf(path: Path, profile) -> dict:
    """ATS checks on the extracted PDF text (less structural, more content-based)."""
    import fitz

    doc = fitz.open(str(path))
    text = "".join(page.get_text() for page in doc)
    doc.close()

    checks = []

    def add(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    text_lower = text.lower()

    # 1. Nome e Email visíveis
    add("Nome completo visível", profile.full_name.lower() in text_lower)
    add("Email visível", profile.email.lower() in text_lower)

    # 2. Comprimento do texto (prova que não é uma imagem vazia)
    add("Texto extraível do PDF", len(text) > 200, f"{len(text)} caracteres extraídos")

    # 3. Seções sobreviveram à conversão
    sections = ["objetivo profissional", "resumo", "formação acadêmica", "habilidades"]
    found = sum(1 for s in sections if s in text_lower)
    add("Seções legíveis no PDF", found >= 2, f"{found}/{len(sections)} encontradas")

    passed = all(c["passed"] for c in checks)
    return {"passed": passed, "checks": checks}