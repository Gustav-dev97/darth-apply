"""
Convert a DOCX to PDF via LibreOffice headless.

LibreOffice is NOT required for DOCX generation. If it's installed, we
produce a PDF alongside the DOCX. If it's not, we return None and the
caller decides what to do (warn the user, offer only DOCX, etc).
"""

import shutil
import subprocess
from pathlib import Path


LIBREOFFICE_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_libreoffice() -> str | None:
    for path in LIBREOFFICE_CANDIDATES:
        if Path(path).exists():
            return path
    return shutil.which("soffice") or shutil.which("libreoffice")


def convert_docx_to_pdf(docx_path: Path, out_dir: Path) -> Path | None:
    """
    Convert DOCX to PDF using LibreOffice headless.

    Returns the PDF path on success, or None if LibreOffice is unavailable
    or the conversion fails.
    """
    soffice = find_libreoffice()
    if not soffice:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(out_dir),
                str(docx_path),
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

    pdf_path = out_dir / (docx_path.stem + ".pdf")
    return pdf_path if pdf_path.exists() else None
