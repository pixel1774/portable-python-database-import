from __future__ import annotations

import ctypes
import os
from pathlib import Path
import secrets
import subprocess


class DatabaseError(RuntimeError):
    """Raised when the native SQLite/auth layer encounters an error."""


def ensure_admin_password_file(admin_password_file: str | Path) -> Path:
    """Create a random admin reset code file once with restricted permissions."""
    file_path = Path(admin_password_file)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        code = secrets.token_urlsafe(24)
        fd = os.open(
            str(file_path),
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        try:
            os.write(fd, f"{code}\n".encode("utf-8"))
        finally:
            os.close(fd)

        if os.name == "nt":
            user = os.environ.get("USERNAME")
            if user:
                subprocess.run(
                    ["icacls", str(file_path), "/inheritance:r", "/grant:r", f"{user}:F"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

    return file_path



class AuthDatabase:
    def __init__(self, db_path: str | Path, dll_dir: str | Path | None = None) -> None:
        self.db_path = Path(db_path)
        self._dll_dir_handle = None
        self._sqlite = None
        self._lib = None
        self._handle = None

        here = Path(__file__).resolve().parent

        native_dir = (
            Path(dll_dir).resolve()
            if dll_dir
            else here / "assets" / "Bin64"
        )

        if not native_dir.is_dir():
            raise DatabaseError(f"DLL directory not found: {native_dir}")

        sqlite_dll = native_dir / "sqlite3.dll"
        db_dll = native_dir / "database_api.dll"

        if not sqlite_dll.is_file():
            raise DatabaseError(f"SQLite DLL not found: {sqlite_dll}")

        if not db_dll.is_file():
            raise DatabaseError(f"Database DLL not found: {db_dll}")

        try:
            if os.name == "nt":
                self._dll_dir_handle = os.add_dll_directory(str(native_dir))

            # Load SQLite first
            self._sqlite = ctypes.CDLL(str(sqlite_dll))

            # Load your database library second
            self._lib = ctypes.CDLL(str(db_dll))

        except OSError as exc:
            if self._dll_dir_handle is not None:
                self._dll_dir_handle.close()
                self._dll_dir_handle = None

            raise DatabaseError(
                f"Failed to load native libraries from {native_dir}.\n"
                f"Windows loader error: {exc}"
            ) from exc

        self._configure_signatures()

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        handle = ctypes.c_void_p()
        rc = self._lib.DB_Open(
            str(self.db_path).encode("utf-8"),
            ctypes.byref(handle)
        )

        if rc != 0 or not handle.value:
            raise DatabaseError(self._last_error())

        self._handle = handle

    def _configure_signatures(self) -> None:
        self._lib.DB_Open.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_void_p)
        ]
        self._lib.DB_Open.restype = ctypes.c_int

        self._lib.DB_Close.argtypes = [ctypes.c_void_p]
        self._lib.DB_Close.restype = None

        self._lib.DB_CreateUser.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p
        ]
        self._lib.DB_CreateUser.restype = ctypes.c_int

        self._lib.DB_VerifyUser.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p
        ]
        self._lib.DB_VerifyUser.restype = ctypes.c_int

        self._lib.DB_UserExists.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p
        ]
        self._lib.DB_UserExists.restype = ctypes.c_int

        self._lib.DB_DeleteUser.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p
        ]
        self._lib.DB_DeleteUser.restype = ctypes.c_int

        self._lib.DB_ChangePassword.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        self._lib.DB_ChangePassword.restype = ctypes.c_int

        self._lib.DB_GetLastError.argtypes = []
        self._lib.DB_GetLastError.restype = ctypes.c_char_p

    def _last_error(self) -> str:
        err = self._lib.DB_GetLastError()
        return err.decode("utf-8", errors="replace") if err else "Unknown database error."

    def _call_bool(self, fn, *args) -> bool:
        if not self._handle:
            raise DatabaseError("Database connection is closed.")

        rc = fn(self._handle, *args)

        if rc == 1:
            return True
        if rc == 0:
            return False

        raise DatabaseError(self._last_error())

    def create_user(self, username: str, password: str) -> bool:
        return self._call_bool(
            self._lib.DB_CreateUser,
            username.encode("utf-8"),
            password.encode("utf-8"),
        )

    def verify_user(self, username: str, password: str) -> bool:
        return self._call_bool(
            self._lib.DB_VerifyUser,
            username.encode("utf-8"),
            password.encode("utf-8"),
        )

    def user_exists(self, username: str) -> bool:
        return self._call_bool(
            self._lib.DB_UserExists,
            username.encode("utf-8")
        )

    def delete_user(self, username: str) -> bool:
        return self._call_bool(
            self._lib.DB_DeleteUser,
            username.encode("utf-8")
        )

    def change_password(
        self,
        username: str,
        current_password: str,
        new_password: str
    ) -> bool:
        return self._call_bool(
            self._lib.DB_ChangePassword,
            username.encode("utf-8"),
            current_password.encode("utf-8"),
            new_password.encode("utf-8"),
            0,
        )

    def _validate_admin_code(
        self,
        provided_code: str,
        admin_password_file: str | Path
    ) -> bool:
        file_path = Path(admin_password_file)

        if not file_path.exists():
            raise DatabaseError(f"Admin password file not found: {file_path}")

        expected_code = file_path.read_text(encoding="utf-8").strip()

        if not expected_code or not provided_code:
            return False

        return secrets.compare_digest(provided_code.strip(), expected_code)

    def reset_password_with_admin_code(
        self,
        username: str,
        admin_code: str,
        new_password: str,
        admin_password_file: str | Path,
    ) -> bool:
        if not self._handle:
            raise DatabaseError("Database connection is closed.")

        if not self._validate_admin_code(admin_code, admin_password_file):
            return False

        if not username or not new_password:
            return False

        if not self.user_exists(username):
            return False

        return self._call_bool(
            self._lib.DB_ChangePassword,
            username.encode("utf-8"),
            b"",
            new_password.encode("utf-8"),
            1,
        )

    def close(self) -> None:
        if self._handle:
            self._lib.DB_Close(self._handle)
            self._handle = None

        if self._dll_dir_handle is not None:
            self._dll_dir_handle.close()
            self._dll_dir_handle = None

    def __enter__(self) -> AuthDatabase:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
