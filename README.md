# 🔐 TrustVault – Secure Document Sharing

## 📌 About the Project

TrustVault is a secure document-sharing web application built using Python and Flask. It allows registered users to upload, view, and download their documents while restricting access to documents owned by other users.

The project focuses on authentication, document access control, and secure file handling.

## ✨ Features

- User registration and login
- Password hashing for secure password storage
- CSRF protection for form submissions
- Secure document upload
- File extension validation
- Maximum upload size of 5 MB
- Private document storage
- User-specific document access
- Protected document downloads
- Session cookie security settings
- SQLite database integration

## 🛠️ Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **Database:** SQLite
- **Security:** Password hashing, CSRF protection, access control
- **Tools:** Visual Studio Code, Git, GitHub

## 📂 Supported File Types

TrustVault currently allows the following file extensions:

- PDF (`.pdf`)
- Text (`.txt`)
- PNG (`.png`)
- JPG/JPEG (`.jpg`, `.jpeg`)

Maximum upload size: **5 MB**

## ⚙️ How to Run the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Open the project folder

```bash
cd YOUR_PROJECT_FOLDER
```

### 3. Install dependencies

```bash
pip install flask
```

If your project contains a `requirements.txt` file, install the listed dependencies instead:

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

### 5. Open in your browser

Visit:

http://127.0.0.1:5000/

Register an account or log in to start using TrustVault.

## 🔒 Security Measures

- Passwords are stored using password hashing.
- CSRF tokens help protect supported forms against cross-site request forgery.
- Download requests verify that the document belongs to the logged-in user.
- Unsupported file extensions are rejected.
- Uploaded files are stored in a private upload directory.
- Session cookie settings help protect session information.

**Note:** File extension checks alone do not verify the actual contents of an uploaded file. Further content validation and production security testing may be needed.

## 🎯 Project Objective

The objective of TrustVault is to demonstrate how a web application can combine user authentication, document management, database operations, and access control to support secure document sharing.

## 👩‍💻 Author

Developed as a security-focused web development project using Python and Flask.

## Security Testing

The following security tests were performed on the local application:

| Test | Expected Result | Status |
|---|---|---|
| Unsupported file upload (`.exe`) | File rejected | PASS |
| File larger than 5 MB | Request rejected | PASS |
| Unauthorized document download | Access denied with 404 response | PASS |

### File Upload Restrictions
- Allowed file types: PDF, TXT, PNG, JPG, JPEG.
- Maximum request size: 5 MB.
- Passwords are hashed before being stored.
- Document downloads are restricted to the document owner.

*Note: These tests were performed locally. Passing these tests does not guarantee complete application security.*
