"""
Filesystem paths for Darth Apply's local data.

Everything the app persists lives under a per-user application data
directory so that uninstalling the app can cleanly remove user data
if the user chooses to.
"""

import os
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Resolve the per-user application data directory.

    On Windows this is %APPDATA%\\DarthApply, e.g.:
        C:\\Users\\<user>\\AppData\\Roaming\\DarthApply

    On macOS/Linux (for future cross-platform support) we fall back to
    the XDG base directory convention: ~/.local/share/darthapply
    """
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if not base:
            raise RuntimeError("APPDATA environment variable is not set")
        path = Path(base) / "DarthApply"
    else:
        path = Path.home() / ".local" / "share" / "darthapply"

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    """Full path to the SQLite database file."""
    return get_app_data_dir() / "darthapply.db"