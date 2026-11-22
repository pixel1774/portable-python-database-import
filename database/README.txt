PORTABLE USER DATABASE - WINDOWS x64
====================================

## WHAT THIS PROJECT DOES

- Creates and opens an SQLite database.
- Creates user accounts and checks whether usernames already exist.
- Verifies usernames and passwords.
- Changes passwords using current-password verification.
- Supports administrator-authorized password recovery.
- Deletes user accounts.
- Stores password hashes instead of plaintext passwords.
- Uses PBKDF2-HMAC-SHA256 for password hashing.
- Exposes a native C API through database_api.dll.
- Uses SQLite through sqlite3.dll.
- Provides a Python interface using ctypes.
- Allows the database folder to be copied into other Python projects.

## PROJECT STRUCTURE

    YOUR-PROJECT-DIRECTORY/
    |
    |-- YOUR-PYTHON-SCRIPT.py
    |
    |-- database/
        |
        |-- __init__.py
        |-- database.py
        |
        |-- assets/
            |
            |-- Bin64/
            |   |-- database_api.dll
            |   |-- sqlite3.dll
            |
            |-- data/
            |   |-- database.db
            |
            |-- settings/
                |-- admin_password.txt

### FILE DESCRIPTIONS

- your-python-script.py - Has full accsess to the database and can use its features.
- database.py - Python ctypes wrapper and administrator password file helper.
- __init__.py - Initializes the Python package.
- database_api.dll - Native database library exposing the custom C API.
- sqlite3.dll - SQLite shared library dependency.
- database.db - SQLite database containing user account records.
- admin_password.txt - Stores the administrator recovery code.
- Bin64/ - Contains the 64-bit native DLL dependencies.
- data/ - Stores database files.
- settings/ - Stores administrator settings and recovery information.

## REQUIREMENTS

- Windows 64-bit.
- Python 64-bit.
- The included native DLL files.

No additional compilation or native library installation is required.

## SECURITY

### Password Storage

Passwords are hashed using PBKDF2-HMAC-SHA256.

The native implementation uses:

- A fresh cryptographically random 16-byte salt per account.
- 600,000 PBKDF2 iterations.
- A 32-byte derived password hash.

Original passwords are never stored in the database.

Username comparison is case-insensitive.

### Administrator Recovery

Administrator password recovery uses a randomly generated token.

The Python helper:

- Generates a token using secrets.token_urlsafe(24).
- Creates the administrator password file only if it does not already exist.
- Does not overwrite an existing recovery code.
- Attempts to restrict file permissions on Windows.
- Validates codes using constant-time comparison with secrets.compare_digest().

The recovery code is checked before the password reset operation is performed.

### Security Considerations

This is a learning/demo account database, not a complete production authentication service.

For production use, also consider:

- Login rate limiting.
- Account lockout policies.
- Secure transport.
- Secure administrator secret management.
- Database backups.
- Protection against unauthorized access to database files.
- Independent security review.

## NATIVE DLL FILES

The application includes the following native libraries:

    database/assets/Bin64/database_api.dll
    database/assets/Bin64/sqlite3.dll

Both DLLs must remain together in the same directory.

The Python wrapper locates the DLL directory relative to database.py, so the application does not depend on the current working directory.

On Windows, os.add_dll_directory() registers the native DLL directory while the database connection is open.

SQLite is loaded before the custom database library.

IMPORTANT:

Do not rename either DLL. The filename sqlite3.dll must match the dependency name expected by database_api.dll.

## DATABASE AND SETTINGS LOCATIONS

The application stores its files in:

    database/assets/data/database.db
    database/assets/settings/admin_password.txt

The Python application creates the required data and settings directories if they do not already exist.

The database file is created or opened when AuthDatabase initializes.

The administrator password file is created using:

    ensure_admin_password_file()

Existing administrator codes are preserved.

## ADDING THE DATABASE TO ANOTHER PYTHON PROJECT

You can use this database in your own Python projects by copying the entire database/ folder into your project's root directory.

You do not need to copy the original main.py test runner or other project files.

### 1. Copy the Database Folder

For example, your project could look like this:

    MyPythonProject/
    |
    |-- main.py
    |
    |-- database/
        |
        |-- __init__.py
        |-- database.py
        |
        |-- assets/
            |
            |-- Bin64/
            |   |-- database_api.dll
            |   |-- sqlite3.dll
            |
            |-- data/
            |
            |-- settings/

Keep the entire database folder together, including its assets directory.

### 2. Import the Database

In your Python script, import the database classes:

    from database.database import (
        AuthDatabase,
        DatabaseError,
        ensure_admin_password_file,
    )

### 3. Configure the Paths

Build your paths relative to your own project directory:

    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent

    DB_PATH = (
        BASE_DIR
        / "database"
        / "assets"
        / "data"
        / "database.db"
    )

    ADMIN_FILE = (
        BASE_DIR
        / "database"
        / "assets"
        / "settings"
        / "admin_password.txt"
    )

### 4. Use the Database

Example:

    from pathlib import Path

    from database.database import (
        AuthDatabase,
        ensure_admin_password_file,
    )

    BASE_DIR = Path(__file__).resolve().parent

    DB_PATH = (
        BASE_DIR
        / "database"
        / "assets"
        / "data"
        / "database.db"
    )

    ADMIN_FILE = (
        BASE_DIR
        / "database"
        / "assets"
        / "settings"
        / "admin_password.txt"
    )

    # Create or load the administrator recovery code
    admin_file = ensure_admin_password_file(ADMIN_FILE)

    # Open the database
    with AuthDatabase(DB_PATH) as db:

        # Register a user
        db.create_user(
            "alice",
            "secure-password"
        )

        # Verify login credentials
        if db.verify_user("alice", "secure-password"):
            print("Login successful!")
        else:
            print("Invalid username or password.")

### 5. Portability Notes

The database folder can be reused in other Python projects without modifying the Python wrapper, provided that:

- You keep the folder structure intact.
- You keep both DLLs inside assets/Bin64/.
- You use a compatible 64-bit Windows Python installation.
- You do not rename the required DLL files.
- Your Python project can import the database package.

The wrapper automatically locates its native DLLs relative to database.py.

Database and settings paths should be built relative to your own project directory.

This allows you to add the database folder to multiple projects and use the same database API without rewriting the native DLL wrapper.

## PYTHON USAGE

Example using the original project structure:

    from pathlib import Path

    from database.database import (
        AuthDatabase,
        ensure_admin_password_file,
    )

    BASE_DIR = Path(__file__).resolve().parent

    DB_PATH = (
        BASE_DIR
        / "database"
        / "assets"
        / "data"
        / "database.db"
    )

    ADMIN_FILE = (
        BASE_DIR
        / "database"
        / "assets"
        / "settings"
        / "admin_password.txt"
    )

    admin_file = ensure_admin_password_file(ADMIN_FILE)

    admin_code = admin_file.read_text(
        encoding="utf-8"
    ).strip()

    with AuthDatabase(DB_PATH) as db:

        # Create user
        created = db.create_user(
            "alice",
            "a-long-password"
        )

        # Check whether user exists
        exists = db.user_exists("alice")

        # Verify login
        valid = db.verify_user(
            "alice",
            "a-long-password"
        )

        # Change password
        changed = db.change_password(
            "alice",
            "a-long-password",
            "new-password"
        )

        # Reset password using administrator code
        reset = db.reset_password_with_admin_code(
            "alice",
            admin_code,
            "recovered-password",
            admin_file,
        )

        # Delete user
        deleted = db.delete_user("alice")

## PYTHON API REFERENCE

### AuthDatabase(db_path, dll_dir=None)

Initializes the database connection.

- db_path - Path to the SQLite database file.
- dll_dir - Optional path to the native DLL directory.

When dll_dir is omitted, the wrapper automatically uses:

    database/assets/Bin64/

### create_user(username, password)

Creates a new user.

Returns:

- True - User successfully created.
- False - Username already exists.

### verify_user(username, password)

Verifies the supplied username and password.

Returns:

- True - Credentials are valid.
- False - Credentials are invalid.

### user_exists(username)

Checks whether a username exists.

Returns:

- True - User exists.
- False - User does not exist.

### change_password(username, current_password, new_password)

Changes an existing user's password.

Requires the current password.

Returns:

- True - Password successfully changed.
- False - User does not exist or current password is incorrect.

### reset_password_with_admin_code(username, admin_code, new_password, admin_password_file)

Resets a user's password using the administrator recovery code.

Returns:

- True - Password successfully reset.
- False - Invalid recovery code, missing user, or empty input.

### delete_user(username)

Deletes an existing user.

Returns:

- True - User successfully deleted.
- False - User does not exist.

### close()

Closes the database connection and releases the registered DLL directory handle.

### Context Manager

AuthDatabase supports Python's context manager protocol.

Example:

    with AuthDatabase(DB_PATH) as db:
        db.create_user("alice", "password")

The database connection is automatically closed when the block exits.

## TESTING

The project includes a standalone test script:

    main.py

Run it from the project root:

    python main.py

The test script uses the actual native DLL implementation through the Python wrapper.

It does not use mocked database functions or require pytest.

### FEATURES TESTED

1. Administrator password file creation.
2. Database initialization.
3. User creation.
4. User existence checks.
5. Correct password verification.
6. Incorrect password rejection.
7. Password changes.
8. Verification of new passwords.
9. Rejection of old passwords.
10. Administrator code validation.
11. Rejection of incorrect administrator codes.
12. Administrator password reset.
13. Verification of administrator-reset passwords.
14. Rejection of unauthorized password resets.
15. Password preservation after failed resets.
16. User deletion.
17. Verification that deleted users no longer exist.
18. Rejection of login attempts for deleted users.
19. Database connection cleanup.

### CURRENT TEST RESULTS

    Passed: 19
    Failed: 0
    Total:  19

    ALL TESTS PASSED!

These results confirm that all 19 tests passed with the current native DLL implementation.

## IMPORTANT NOTES

- Use 64-bit Python with 64-bit DLLs.
- Keep database_api.dll and sqlite3.dll together inside assets/Bin64/.
- Do not rename native DLLs.
- Keep the DLL directory registered while native libraries are in use.
- Always close database connections when finished.
- Do not commit real user databases or administrator recovery codes to public repositories.
- Keep administrator recovery codes private.
- Back up important database files regularly.

====================================
END OF README
====================================