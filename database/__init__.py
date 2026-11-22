from __future__ import annotations

import os
from pathlib import Path

from .database import AuthDatabase, DatabaseError, ensure_admin_password_file

DATA_DIR = Path(os.environ.get("AUTHPKG_DATA_DIR", Path.home() / ".authpkg"))
ADMIN_PASSWORD_FILE = ensure_admin_password_file(DATA_DIR / "adminpassword.txt")

__all__ = [
    "AuthDatabase",
    "DatabaseError",
    "DATA_DIR",
    "ADMIN_PASSWORD_FILE",
    "ensure_admin_password_file",
]