# 🔐 TrustVault – Secure Document Sharing

## About the Project

TrustVault is a Python and Flask web application that allows registered users to upload and download their own documents. Server-side ownership checks prevent users from downloading documents belonging to other accounts.

The project demonstrates authentication, document access control, CSRF protection, and basic security testing.

## Features

- User registration and login
- Password hashing
- CSRF token validation for supported form submissions
- Private document uploads
- Server-side document ownership checks
- Protected document downloads
- File extension restrictions
- Maximum upload size of 5 MB
- SQLite database integration
- Audit logging for document uploads and downloads

## Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **Database:** SQLite
- **Testing:** pytest
- **Tools:** Visual Studio Code, Git, GitHub
- **Deployment:** Render

## Supported File Types

- PDF (`.pdf`)
- Text (`.txt`)
- PNG (`.png`)
- JPG/JPEG (`.jpg`, `.jpeg`)

Maximum upload size: **5 MB**

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/suppi2006/TrustVault.git
cd TrustVault
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
```

### 4. Configure the application

Set a strong secret key using an environment variable before running the application. Do not commit real secrets to GitHub.

Windows PowerShell example:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
```

For production, configure environment variables and secure cookie settings in the deployment environment.

### 5. Start the application

```bash
python app.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

## Automated Tests

Run the automated tests with:

```bash
python -m pytest test_app.py -v
```

The current local test suite contains six tests covering:

- Login page availability
- Dashboard authentication requirement
- Password hash storage
- Invalid CSRF token rejection
- Incorrect password rejection
- Prevention of cross-user document downloads

**Latest recorded local result:** 6 tests passed.

Additional manual checks were performed for unsupported file uploads and files larger than the 5 MB limit.

## Security Measures

- Passwords are stored as hashes.
- CSRF tokens are validated on supported form submissions.
- Download queries check both the document ID and the authenticated user's ID.
- Unsupported file extensions are rejected.
- Uploaded files use generated storage names.
- Upload and download events are recorded in audit logs.
- Session cookie settings include HTTP-only and SameSite protections.

## Known Limitations

- Role-based access and configurable document-sharing permissions are not implemented.
- File extensions are checked, but actual file contents are not fully validated.
- Malware scanning, rate limiting, and account lockout are not implemented.
- Audit events are recorded, but a user-facing audit log viewer is not implemented.
- The current SQLite database and local upload storage may not persist across deployment restarts or redeployments on an ephemeral hosting filesystem.
- Production security and deployment configuration require further review.

These limitations mean the project is a learning and demonstration application, not a fully production-hardened document storage service.

## Project Objective

TrustVault demonstrates how authentication, database operations, file handling, and server-side access control can be combined to protect users' private documents.

## Author

Developed as a security-focused web development project using Python and Flask.