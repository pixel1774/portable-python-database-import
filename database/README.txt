# PORTABLE USER DATABASE - WINDOWS x64
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
- Can be used either from the downloaded source code or as an installed Python wheel package.

## REQUIREMENTS

- Windows 64-bit.
- Python 64-bit.
- The included native DLL files (provided with the source code or wheel).

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

## INSTALLATION AND USAGE

There are two ways to use this database in your Python projects.

- **Method 1:** Download the source code and copy the database folder into your project.
- **Method 2:** Install the prebuilt .whl package using pip.

Choose whichever method you prefer.

# METHOD 1 - USING THE DOWNLOADED SOURCE CODE

Use this method if you downloaded the source code instead of installing the wheel.

### 1. Copy the Database Folder

Copy the entire database/ folder into your Python project's root directory.

Your project should look like this:

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

You do not need to copy the original test scripts or other development files.

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

    DB_DIR = BASE_DIR / "database"
    ASSETS_DIR = DB_DIR / "assets"

    DATA_DIR = ASSETS_DIR / "data"
    SETTINGS_DIR = ASSETS_DIR / "settings"

    DB_PATH = DATA_DIR / "database.db"
    ADMIN_FILE = SETTINGS_DIR / "admin_password.txt"

    # Create the required directories
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

### 4. Use the Database

Example:

    from pathlib import Path

    from database.database import (
        AuthDatabase,
        ensure_admin_password_file,
    )

    BASE_DIR = Path(__file__).resolve().parent

    DB_DIR = BASE_DIR / "database"
    ASSETS_DIR = DB_DIR / "assets"

    DATA_DIR = ASSETS_DIR / "data"
    SETTINGS_DIR = ASSETS_DIR / "settings"

    DB_PATH = DATA_DIR / "database.db"
    ADMIN_FILE = SETTINGS_DIR / "admin_password.txt"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create or load the administrator recovery code
    admin_file = ensure_admin_password_file(ADMIN_FILE)

    admin_code = admin_file.read_text(
        encoding="utf-8"
    ).strip()

    # Open the database
    with AuthDatabase(DB_PATH) as db:

        # Register a user
        db.create_user("alice", "secure-password")

        # Verify login credentials
        if db.verify_user("alice", "secure-password"):
            print("Login successful!")
        else:
            print("Invalid username or password.")

        # Check whether a user exists
        print(db.user_exists("alice"))

### 5. Source Code Notes

- Keep database.py and __init__.py inside the database folder.
- Keep both DLLs inside assets/Bin64/.
- Do not rename either DLL.
- Use 64-bit Python.
- The wrapper automatically locates the DLLs relative to database.py.
- You can copy the database folder into multiple projects.

# METHOD 2 - USING THE INSTALLED .WHL PACKAGE

Use this method if you downloaded the prebuilt wheel package.

You do not need to copy the database folder or DLL files into your project. They are included in the installed package.

### 1. Install the Wheel

Open PowerShell or Command Prompt and navigate to your wheel file.

Install it using:

    python -m pip install portable_user_database-1.0.0-py3-none-win_amd64.whl

If you already have an older version installed and want to replace it, use:

    python -m pip install --force-reinstall portable_user_database-1.0.0-py3-none-win_amd64.whl

Make sure you use the actual filename of the wheel you downloaded.

IMPORTANT:

Install the package into the same Python environment that will run your project.

### 2. Import the Database

After installation, import it normally:

    from database.database import (
        AuthDatabase,
        DatabaseError,
        ensure_admin_password_file,
    )

You do not need to manually locate or load the DLL files.

The Python wrapper automatically locates the DLLs included in the installed package.

### 3. Configure Your Database Paths

When using the installed wheel, it is recommended to keep your database and administrator settings in your own project directory rather than inside the installed Python package.

Example project structure:

    MyPythonProject/
    |
    |-- main.py
    |
    |-- data/
    |
    |-- settings/

Configure your paths:

    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent

    DATA_DIR = BASE_DIR / "data"
    SETTINGS_DIR = BASE_DIR / "settings"

    DB_PATH = DATA_DIR / "database.db"
    ADMIN_FILE = SETTINGS_DIR / "admin_password.txt"

    # Create directories if they do not exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

### 4. Use the Installed Package

Example:

    from pathlib import Path

    from database.database import (
        AuthDatabase,
        ensure_admin_password_file,
    )

    BASE_DIR = Path(__file__).resolve().parent

    DATA_DIR = BASE_DIR / "data"
    SETTINGS_DIR = BASE_DIR / "settings"

    DB_PATH = DATA_DIR / "database.db"
    ADMIN_FILE = SETTINGS_DIR / "admin_password.txt"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create or load the administrator recovery code
    admin_file = ensure_admin_password_file(ADMIN_FILE)

    admin_code = admin_file.read_text(
        encoding="utf-8"
    ).strip()

    # Open the database
    with AuthDatabase(DB_PATH) as db:

        # Register a user
        db.create_user("alice", "secure-password")

        # Verify login
        if db.verify_user("alice", "secure-password"):
            print("Login successful!")
        else:
            print("Invalid username or password.")

### 5. Installed Package Notes

- You do not need to copy the database folder into your project.
- You do not need to manually copy either DLL.
- The DLLs are included in the wheel.
- The wrapper automatically locates the native DLL directory.
- Your database and administrator settings can be stored wherever you choose.
- Use 64-bit Windows Python.

# PYTHON API REFERENCE

### AuthDatabase(db_path, dll_dir=None)

Initializes the database connection.

- db_path - Path to the SQLite database file.
- dll_dir - Optional path to the native DLL directory.

When dll_dir is omitted, the wrapper automatically locates the native DLL directory relative to database.py.

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

# NATIVE DLL FILES

The application uses the following native libraries:

    database/assets/Bin64/database_api.dll
    database/assets/Bin64/sqlite3.dll

When using the source code, these files must remain together inside assets/Bin64/.

When using the wheel, both DLLs are included in the installed Python package.

The wrapper uses os.add_dll_directory() on Windows to register the native DLL directory while the database connection is open.

SQLite is loaded before the custom database library.

IMPORTANT:

Do not rename either DLL. The filename sqlite3.dll must match the dependency name expected by database_api.dll.

# DATABASE AND SETTINGS LOCATIONS

The database and administrator recovery file are created at the locations specified by your Python script.

For source code usage, the recommended locations are:

    database/assets/data/database.db
    database/assets/settings/admin_password.txt

For installed wheel usage, the recommended locations are:

    data/database.db
    settings/admin_password.txt

Your script should create the required parent directories before creating the administrator password file.

The database file is created or opened when AuthDatabase initializes.

The administrator password file is created using:

    ensure_admin_password_file()

Existing administrator codes are preserved and are not overwritten.

# TESTING

The project includes standalone test scripts for checking the database features.

If you downloaded the source code and have the original test runner, run:

    python main.py

If you installed the wheel, you can create and run the separate test script:

    python test_database.py

The tests use the actual native DLL implementation through the Python wrapper.

They do not use mocked database functions or require pytest.

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

### VERIFIED TEST RESULTS

    Passed: 19
    Failed: 0
    Total:  19

    ALL TESTS PASSED!

The installed wheel package has successfully passed all 19 feature tests.

# IMPORTANT NOTES

- Use 64-bit Python with the included 64-bit DLLs.
- Keep database_api.dll and sqlite3.dll together inside assets/Bin64/ when using source code.
- Do not rename native DLLs.
- When using the wheel, the DLLs are already included.
- Always close database connections when finished.
- Keep administrator recovery codes private.
- Do not commit real user databases or administrator recovery codes to public repositories.
- Back up important database files regularly.

====================================
END OF README
====================================