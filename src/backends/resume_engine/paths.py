from pathlib import Path

from db.paths import get_app_data_dir


def get_resumes_dir() -> Path:
    """Directory where generated resumes are written."""
    path = get_app_data_dir() / "resumes"
    path.mkdir(parents=True, exist_ok=True)
    return path
